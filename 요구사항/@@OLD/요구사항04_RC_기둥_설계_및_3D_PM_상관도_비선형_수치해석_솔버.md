# 요구사항 04: RC 기둥 설계 및 3D P-M 상관도 비선형 수치해석 솔버

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
철근콘크리트(RC) 기둥(Column)은 축압축력과 일축/이축 휨모멘트를 동시에 지지하는 핵심 압축부재입니다. Midas Design+의 가장 강력하고 복잡한 수치해석 핵심 루틴인 `CRCSCodeCheck::CHK_BCCO`와 `mfsolver.exe`의 파이버 단면 수치적분(Fiber Section Integration) 엔진은 중립축 위치와 회전각을 수치적으로 탐색하여 P-M 상관곡선을 생성합니다.

### 1.2. 목적
1. `decompiled_src/core_routines/solver/`의 `solver__CHK_BCCO_*.c`, `solver__CHK_BCGR_*.c` 소스코드를 리버스 엔지니어링하여, 순수 Python 기반의 **파이버 단면 3차원 P-M 상관도 비선형 수치해석 솔버(`src/engine/solver/pm_diagram.py`, `fiber_section.py`)** 구현.
2. 직사각형, 원형, 다각형 기둥 단면에 대한 KDS 14 20 20 장주효과(모멘트 확대계수법) 및 이축휨(Bresler 식, PCA Load Contour 법) 설계 엔진(`src/engine/rc/column.py`) 구축.
3. 3차원 공칭/설계 P-M 상관곡선 및 다중 하중조합 작용점을 시각화하는 대화형 차트(`src/web/static/js/pm_chart.js`) 구현.

---

## 2. KDS 국가건설기준 및 비선형 수치해석 공식

### 2.1. 파이버 단면 수치적분법 (Fiber Section Numerical Integration)
* **단면 이산화**: 콘크리트 단면을 $N \times M$ 격자 파이버($\Delta A_c$), 철근을 각 위치별 이산 파이버($A_{si}$)로 분할.
* **단면 변형률 분포 (Bernoulli 평면유지 가정)**:
  $$\epsilon(x, y) = \epsilon_0 + \kappa_x y - \kappa_y x = \epsilon_{cu} \left(1 - \frac{y \cos\theta + x \sin\theta}{c}\right)$$
  - $c$: 중립축 깊이, $\theta$: 중립축 경사각
* **단면 내력 적분 (Axial Force & Moments)**:
  $$P(c, \theta) = \sum_{i} \sigma_{c}(\epsilon_{ci}) \Delta A_{ci} + \sum_{j} \sigma_{s}(\epsilon_{sj}) A_{sj}$$
  $$M_x(c, \theta) = \sum_{i} \sigma_{c}(\epsilon_{ci}) y_i \Delta A_{ci} + \sum_{j} \sigma_{s}(\epsilon_{sj}) y_j A_{sj}$$
  $$M_y(c, \theta) = \sum_{i} \sigma_{c}(\epsilon_{ci}) x_i \Delta A_{ci} + \sum_{j} \sigma_{s}(\epsilon_{sj}) x_j A_{sj}$$

### 2.2. KDS P-M 한계상태 및 강도저감계수 $\phi$ (KDS 14 20 10 / 20)
* **순수 압축 강도 ($P_0$) 및 최대 축압축강도 상한 ($\phi P_{n,max}$)**:
  $$P_0 = \alpha_1 f_{ck}(A_g - A_{st}) + f_y A_{st}$$
  $$\phi P_{n,max} = \begin{cases} 0.80 \phi P_0 & (\text{띠철근 기둥, } \phi = 0.65) \\ 0.85 \phi P_0 & (\text{나선철근 기둥, } \phi = 0.70) \end{cases}$$
* **인장/압축 제어 전이영역 강도저감계수 $\phi(\epsilon_t)$**:
  최외단 인장철근 변형률 $\epsilon_t$에 따라 $\phi$ 자동 선형 보간.
* **순수 인장 강도 ($P_t$)**: $P_t = f_y A_{st}, \quad \phi P_t = 0.85 f_y A_{st}$

### 2.3. 장주효과 및 이축 휨 (Slenderness & Biaxial Bending)
* **모멘트 확대계수법 ($\delta_{ns}, \delta_s$)**:
  $$M_c = \delta_{ns} M_{2ns} + \delta_s M_{2s}, \quad \delta_{ns} = \frac{C_m}{1 - P_u / (0.75 P_c)} \ge 1.0$$
  - 오일러 좌굴하중: $P_c = \frac{\pi^2 EI}{(k L_u)^2}, \quad EI = \frac{0.2 E_c I_g + E_s I_{se}}{1 + \beta_{dns}}$
* **이축휨 설계식 (Bresler / PCA)**:
  $$\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_0}, \quad \left(\frac{M_{ux}}{\phi M_{nx}}\right)^\alpha + \left(\frac{M_{uy}}{\phi M_{ny}}\right)^\alpha \le 1.0$$

---

## 3. C 수도코드 Ground Truth 매핑

| 기능 도메인 | 참조 디컴파일 C 소스 자산 | 대상 C++ 클래스 및 핵심 함수 |
|---|---|---|
| **기둥 P-M 해석 & 모멘트 확대** | [`decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c) | `CRCSCodeCheck::CHK_BCCO()` |
| **P-M 곡선 점 샘플링** | [`decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c) | `CRCSCodeCheck::CalcPMDiagramPoints()` |
| **기둥 그룹 다중단면 일괄검토** | [`decompiled_src/core_routines/solver/CHK_BCGR_column_group.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCGR_column_group.c) | `CRCSCodeCheck::CHK_BCGR()` |
| **파이버 단면 비선형 적분** | [`decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c) | `FiberSectionIntegrator::SolveForces()` |

---

## 4. Python & Web 신규 구현 아키텍처

```text
src/
├── engine/
│   ├── solver/
│   │   ├── __init__.py
│   │   ├── fiber_section.py   # 파이버 메쉬 생성 및 단면 변형률/응력 적분기
│   │   └── pm_diagram.py      # 3D P-M-M 상관곡선 생성 및 DCR 판정기
│   └── rc/
│       └── column.py          # RC 기둥 종합 설계 (장주효과, 이축휨, 띠철근)
├── api/
│   ├── schemas/rc_column.py   # Pydantic 입력/출력 모델
│   └── routes/rc_column.py    # FastAPI 엔드포인트 (/api/v1/rc/column/pm-curve, /check)
└── web/static/js/
    └── pm_chart.js            # Canvas / Chart.js 대화형 3D/2D P-M 차트
```

### 4.1. 클래스 및 핵심 메서드 사양
* **[`src/engine/solver/fiber_section.py`](file:///f:/PyProject/AltDP_3rd/src/engine/solver/fiber_section.py)**:
  - `class Fiber`: `x, y, area, material_type`
  - `class FiberSection`: 단면 메쉬 생성(`discretize(nx=30, ny=30)`), 중립축 위치 $c, \theta$에 대한 $(P, M_x, M_y)$ 반환.
* **[`src/engine/solver/pm_diagram.py`](file:///f:/PyProject/AltDP_3rd/src/engine/solver/pm_diagram.py)**:
  - `class PMDiagramSolver`: $\theta \in [0, 2\pi]$ 및 $c$ 스윕을 통해 $(P_n, M_n)$ 및 $(\phi P_n, \phi M_n)$ 곡면 포인트 생성.
  - `calc_dcr(Pu, Mux, Muy) -> float`: P-M 표면과 하중 벡터의 교점 탐색을 통한 정확한 DCR 산출.
* **[`src/engine/rc/column.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rc/column.py)**:
  - `class RCColumn`: 단면, 주철근, 띠철근/나선철근, 비지지길이 $L_u$, 유효좌굴계수 $k$.
  - `evaluate_column(loads: List[SectionForces]) -> RCColumnDesignResult`

---

## 5. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 04-1** | `요구사항04-1_파이버_단면_비선형_수치적분_엔진.md` | `src/engine/solver/fiber_section.py`, `tests/engine/test_fiber_section.py` | 단면 응력적분 및 $P_0, P_t, P_b$ 일치성 |
| **Phase 04-2** | `요구사항04-2_3D_PM_상관곡선_생성_및_DCR_산정기.md` | `src/engine/solver/pm_diagram.py`, `tests/engine/test_pm_diagram.py` | 3D P-M 곡선 생성 및 DCR 오차 < 0.1% |
| **Phase 04-3** | `요구사항04-3_RC기둥_장주_이축휨설계_및_PM차트UI.md` | `src/engine/rc/column.py`, `src/web/static/js/pm_chart.js`, `tests/api/test_rc_column_api.py` | 모멘트 확대계수, Bresler 검증, Web 차트 렌더링 |

---

## 6. 검증 및 수용 기준 (Acceptance Criteria)

- [x] **P-M 상관곡선 수치 일치성**: `decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c` 원본 값 및 MIDAS Design+ 결과 대비 상관곡선 오차 0.1% 미만.
- [x] **단면 수렴성 및 속도**: 파이버 100개 기준 단일 P-M 상관곡선(100개 포인트) 생성 시간 50ms 이내 완료.
- [x] **KDS 장주/이축휨 검증**: 세장비 $k L_u / r > 22$ 구간 모멘트 확대 및 Bresler 식 DCR 계산 무결성 100%.
- [x] **초고속 단위 테스트 통과**: `pytest tests/engine/test_fiber_section.py test_pm_diagram.py test_rc_column.py tests/api/test_rc_column_api.py` (100% 통과).
