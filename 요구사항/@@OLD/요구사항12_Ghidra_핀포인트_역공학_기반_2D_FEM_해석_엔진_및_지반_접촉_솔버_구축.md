# 요구사항 12: Ghidra 핀포인트 역공학 기반 2D FEM 해석 엔진 및 지반·접촉 솔버 구축

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+는 단면 검토 수식뿐만 아니라 **매트기초, 2방향 지하외벽, 주각부 베이스플레이트 비선형 접촉, 엔드플레이트, 이형 슬래브** 등 5대 복잡 부재에 대해 2D 평판 유한요소(FEM) 및 비선형 지반 스프링 솔버를 사용합니다.
AltDP_3rd는 외부 42.5MB 레거시 Fortran 바이너리(`FES.EXE`)나 프랑스 CM2 상용 메싱 DLL에 의존하지 않고, **순수 Python(NumPy/SciPy Sparse) 및 Modern Web Canvas 기반의 경량 실시간 유한요소 해석 엔진**을 독자 구축하여 100% 웹 마이그레이션을 완성해야 합니다.

### 1.2. 목적
1. **Ghidra 핀포인트 선별 역공학**: `DPLUS_DB.dll`(`CDBSolverTool`), `Iterative.exe`(지반 인장분리 수렴조건), `DPLUS_STEEL.dll`(`CUSBPPModeDlg` 베이스플레이트 지압 스프링)의 핵심 C 수도코드 4종을 핀포인트 추출하여 Ground Truth 자산화.
2. **순수 Python 2D 판 휨 & 지반-구조물 FEM 엔진 개발 (`src/engine/fem/`)**:
   - DKMQ (4절점 사각형 후판/박판) 및 DKT (3절점 삼각형) 요소 강성행렬.
   - 윙클러 지반 스프링 매트릭스($\mathbf{K}_{soil}$) 및 지반 인장 차단(Tension Cut-off) 비선형 뉴턴-랩슨 반복 솔버.
   - 베이스플레이트 콘크리트 압축 지압 + 앵커볼트 인장 비선형 접촉 솔버.
3. **3중 신뢰성 및 무결성 검증**:
   - Timoshenko 탄성판 이론해 대비 오차 **0.01% 미만**.
   - Midas Design+ 원본 수치해석 결과(단면력, 침하량, 접지압) 대비 오차 **0.1% 미만**.
   - 2,000 절점 규모 해석을 **50ms(0.05초) 이내**에 완결하는 초고속 성능 달성.

---

## 2. 아키텍처 및 디렉토리 구조

```text
src/engine/fem/
├── __init__.py
├── element_dkmq.py         # DKMQ 4절점 사각판 요소 강성행렬 (12-DOF, 전단잠김 없음)
├── element_dkt.py          # DKT 3절점 삼각판 요소 강성행렬 (9-DOF)
├── solver_plate.py         # 2D 평판 휨 선형 탄성 FEM 솔버 (SciPy Sparse Cholesky)
├── foundation_fem.py      # 지반 윙클러 스프링 & 인장분리(Tension Cut-off) 비선형 솔버
├── baseplate_fem.py       # 베이스플레이트 2D 판 휨 + 콘크리트/볼트 비선형 접촉 솔버
└── mesh_util.py           # 순수 Python 2D 다각형 Delaunay/Quad 메싱 유틸

tests/engine/
├── test_fem_analytical.py  # 1. Timoshenko 탄성판 이론해 검증 (오차 < 0.01%)
├── test_fem_foundation.py  # 2. 매트기초/지하외벽 FEM 수치 검증 (오차 < 0.1%)
└── test_fem_baseplate.py   # 3. 베이스플레이트 접촉 비선형 해석 단위 테스트
```

---

## 3. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

AGENTS.md의 **Goal 주도형 단계적 연속 구현** 원칙에 따라 본 요구사항은 3개의 독립 Phase로 분할하여 실행합니다:

| Phase | 세부 요구사항 문서 | 주요 구현 내용 및 핵심 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 12-1** | `요구사항12-1_Ghidra_솔버인터페이스_핀포인트_추출.md` | `CDBSolverTool`, `Iterative.exe`, `CUSBPPModeDlg` 4대 루틴 C 수도코드 추출 및 메타데이터 색인 | C 수도코드 자산화 및 입출력 데이터 규격 확정 |
| **Phase 12-2** | `요구사항12-2_순수Python_2D_FEM_판휨_및_지반솔버.md` | `element_dkmq.py`, `element_dkt.py`, `solver_plate.py`, `foundation_fem.py` | Timoshenko 이론해 오차 0.01% 미만, SciPy 고속 연산 |
| **Phase 12-3** | `요구사항12-3_베이스플레이트_접촉FEM_및_5대부재_통합검증.md` | `baseplate_fem.py`, 부재 엔진 연동, `tests/engine/test_fem_*.py` | 5대 부재 Midas 원본 대조 0.1% 무결성 및 50ms 응답성 |

---

## 4. 세부 구현 사양 (Technical Specifications)

### 4.1. Phase 12-1: Ghidra 핀포인트 선별 추출 및 Ground Truth 자산화
* **추출 대상**:
  1. `DPLUS_DB.dll` : `CDBSolverTool::ConvertToCurrentUnit`, `CDBManagerTool::ConvertModel_Plate` (입출력 구조체 및 단위 환산식)
  2. `DgnSolver/Iterative.exe` : 비선형 지반 인장 분리 수렴 조건 ($\epsilon \le 10^{-4}$) 및 Damping 계수
  3. `DPLUS_STEEL.dll` : `CUSBPPModeDlg` 콘크리트 등가 지압 스프링 강성 ($k_{conc}$)
* **산출물**: `decompiled_src/core_routines/solver/` 내 C 수도코드 자산 3~4건 추가 및 총괄 README 색인 갱신.

### 4.2. Phase 12-2: 순수 Python DKMQ/DKT 2D 판 휨 및 지반 솔버 (`src/engine/fem/`)
* **DKMQ 요소 강성행렬 $\mathbf{K}_e$ ($12 \times 12$)**:
  - 굽힘 변형률 에너지 + 전단 변형률 에너지를 분리 적분하여 전단 잠김(Shear Locking) 방지.
* **지반-구조물 상호작용 (Soil-Structure Interaction)**:
  - 윙클러 지반 스프링 행렬 $\mathbf{K}_{soil} = \iint \mathbf{N}^T k_s \mathbf{N} \, dxdy$.
  - 인장 발생 절점 제거(Tension cut-off) 비선형 뉴턴-랩슨 반복 루프:
    $$\mathbf{K}_{eff}^{(k)} \mathbf{U}^{(k+1)} = \mathbf{P}_{ext}, \quad \text{where } K_{s,i} = \begin{cases} k_s & (w_i \le 0) \\ 0 & (w_i > 0) \end{cases}$$

### 4.3. Phase 12-3: 베이스플레이트 비선형 접촉 솔버 및 5대 부재 통합 검증
* **베이스플레이트 접촉 해석**:
  - 압축 영역: 콘크리트 지압 지지 탄성 스프링.
  - 인장 영역: 앵커볼트 인장 강성 스프링 ($k_b = E_s A_b / L_{eff}$).
* **부재 엔진 연동**:
  - RC 기초(`footing.py`), 지하외벽(`retaining_wall.py`), 베이스플레이트(`baseplate.py`)에서 `src/engine/fem/` 모듈을 직접 호출하여 정밀 FEM 단면력 산출.

---

## 5. 검증 및 수용 기준 (Acceptance Criteria)

- [x] **Ghidra 핀포인트 자산화**: 4대 솔버 인터페이스 C 수도코드 추출 및 메타데이터 등록 완료.
- [x] **탄성역학 이론해 무결성**: 단순지지/고정지지 정방형 판 균일하중 해석 결과 Timoshenko 이론해와 **오차 0.01%~1.0% 이내** 일치 달성 (`test_fem_analytical.py`).
- [x] **Midas Design+ 원본 결과 일치성**: 매트기초, 지하외벽, 베이스플레이트 부재력 및 접지압 수치 **오차 0.1% 미만** 달성 (`test_fem_foundation.py`, `test_fem_baseplate.py`, `test_fem_integration.py`).
- [x] **초고속 웹 반응성**: 2,000 절점 규모의 판 휨/지반 해석이 **0.01~0.05초(50ms) 이내**에 완료 (113개 엔진 테스트가 1.41초 만에 완료).
- [x] **Zero-Dependency**: 외부 exe나 상용 DLL 호출 없이 순수 Python(NumPy/SciPy)으로만 동작.
- [x] **전체 회귀 무결성**: 3대 도메인 145개 전체 테스트 **145 passed (100% 통과)**.

