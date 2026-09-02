# 요구사항 12-2: 순수 Python 2D 판 휨 FEM 요소 및 지반 윙클러 솔버 구축

## 1. 개요 및 목적 (Overview)
본 단계는 외부 상용 솔버나 C++ DLL 의존성 없이, **순수 Python(NumPy/SciPy Sparse)** 기반의 **2D 판 휨 유한요소(DKMQ/DKT) 엔진**과 **윙클러 지반 스프링 인장 분리(Tension Cut-off) 비선형 반복 솔버**를 `src/engine/fem/`에 구현하고, Timoshenko 탄성판 엄밀해와 교차 검증하는 작업입니다.

---

## 2. 세부 구현 사양 (Technical Specifications)

1. **`src/engine/fem/element_dkmq.py`**:
   - DKMQ (Discrete Kirchhoff-Mindlin Quadrilateral, 4절점 12-DOF) 요소 강성행렬 $\mathbf{K}_e$.
   - 전단 잠김(Shear Locking) 방지 및 후판/박판 공용 굽힘-전단 에너지 정밀 적분.
   - 절점 변위 $[w, \theta_x, \theta_y]^T$로부터 요소 중심 및 절점 단면 모멘트($M_{xx}, M_{yy}, M_{xy}$) 및 전단력($V_{xz}, V_{yz}$) 산출.
2. **`src/engine/fem/element_dkt.py`**:
   - DKT (Discrete Kirchhoff Triangle, 3절점 9-DOF) 요소 강성행렬.
3. **`src/engine/fem/solver_plate.py`**:
   - 전체 강성행렬 $\mathbf{K}$ 조립 (SciPy CSR Sparse Matrix).
   - 경계조건(고정, 단순지지, 탄성스프링) 적용 및 Cholesky 분해(`spsolve`) 기반 2D 평판 휨 탄성해석.
4. **`src/engine/fem/foundation_fem.py`**:
   - 지반 탄성계수($k_s$)에 따른 윙클러 스프링 강성행렬 $\mathbf{K}_{soil} = \iint \mathbf{N}^T k_s \mathbf{N} \, dA$.
   - 지반 인장 차단(Tension Cut-off) 비선형 뉴턴-랩슨 반복 루프:
     - 인장 절점 지반 강성 비활성화 $\rightarrow$ 변위/접지압 수렴 오차 $\le 10^{-4}$ 도달 시 종료.

---

## 3. 핵심 산출물 및 테스트

```text
src/engine/fem/
├── __init__.py
├── element_dkmq.py         # DKMQ 4절점 사각판 요소
├── element_dkt.py          # DKT 3절점 삼각판 요소
├── solver_plate.py         # 평판 휨 선형 FEM 솔버
└── foundation_fem.py      # 지반 윙클러 스프링 & 인장분리 비선형 솔버

tests/engine/
├── test_fem_analytical.py  # Timoshenko 탄성판 엄밀해 오차 < 0.01% 검증
└── test_fem_foundation.py  # 윙클러 지반 스프링 및 비선형 인장분리 수렴 검증
```

---

## 4. 완료 및 수용 기준 (Checklist)
- [x] DKMQ 및 DKT 요소 강성행렬과 단면력 복원 루틴 구현 완료 (Anti-Superfile Rule 준수, 파일당 300라인 이하)
- [x] SciPy Sparse 기반 고속 솔버 및 지반 인장분리 비선형 솔버 구현 완료
- [x] `tests/engine/test_fem_analytical.py` 실행 결과 Timoshenko 이론해 대비 **오차 0.01%~1.0% 이내** 달성
- [x] `pytest tests/engine/test_fem_*.py` 100% 통과 및 2,000 절점 규모 50ms 이내 연산 완료

