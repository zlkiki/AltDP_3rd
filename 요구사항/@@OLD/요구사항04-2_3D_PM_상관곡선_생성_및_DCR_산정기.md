# 요구사항 04-2: 3D P-M 상관곡선 생성 및 DCR 산정기 (PM Diagram Solver)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* `src/engine/solver/fiber_section.py` 파이버 적분기를 기반으로, 중립축 위치 $c$와 경사각 $\theta \in [0, 2\pi]$를 스윕하여 3차원 공칭 P-M-M 상관곡면 및 KDS 14 20 20 강도감소계수 $\phi(\epsilon_t)$가 적용된 설계 P-M-M 상관곡면을 생성하는 엔진을 구현합니다.
* 다중 설계 축력/휨모멘트 하중점 $(P_u, M_{ux}, M_{uy})$에 대해 설계 상관곡면과의 최단 벡터 교점 탐색을 수행하여 정확한 3차원 DCR(Demand-Capacity Ratio)을 산정합니다.

### 1.2. 참조 Ground Truth 자산
* **디컴파일 소스**: [`decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c)
* **KDS 기준서**: KDS 14 20 10 (설계원칙 - $\phi$ 산정), KDS 14 20 20 (휨 및 압축 - $\phi P_{n,max}$)
* **대상 소스**: [`src/engine/solver/pm_diagram.py`](file:///f:/PyProject/AltDP_3rd/src/engine/solver/pm_diagram.py)

---

## 2. 상세 구현 명세

### 2.1. 2D & 3D P-M 상관곡선 생성 알고리즘
* **중립축 스윕 (c-sweep)**:
  - 무한대(순수압축 $P_0$)부터 최소 깊이(순수인장 $P_t$)까지 대수적/지수적 간격으로 $c$를 스윕.
  - 최외단 인장철근 변형률 $\epsilon_t$ 산정 $\implies$ KDS 14 20 10에 따른 $\phi(\epsilon_t)$ 자동 결정.
* **설계 강도 산정 ($\phi P_n, \phi M_{nx}, \phi M_{ny}$)**:
  - 축압축 강도 상한 적용: $\phi P_n \le \phi P_{n,max} = 0.80 \phi P_0$ (띠철근) 또는 $0.85 \phi P_0$ (나선철근).
* **3D 상관곡면 생성 ($\theta$-sweep)**:
  - $\theta = 0^\circ, 15^\circ, 30^\circ, \dots, 360^\circ$ 각도별 2D 슬라이스 곡선 생성 $\implies$ 3차원 메시 표면 구성.

### 2.2. DCR 산정 및 파이버 기반 안전성 판정
* **동일 편심비/각도 기반 광선 투사법 (Radial Ray Search)**:
  - 하중점 $(P_u, M_{ux}, M_{uy})$의 작용각 $\theta = \arctan2(M_{uy}, M_{ux})$ 계산.
  - 해당 각도의 2D P-M 설계 곡선에서 주어진 $P_u$에 대한 허용 휨모멘트 $\phi M_{n,\theta}$ 보간.
  - $\text{DCR} = \frac{\sqrt{M_{ux}^2 + M_{uy}^2}}{\phi M_{n,\theta}}$ 산출.
* **3차원 방사형 벡터 DCR (3D Vector DCR)**:
  - 원점 $(0, 0, 0)$과 하중점 $(P_u, M_{ux}, M_{uy})$을 잇는 광선과 3D P-M 표면의 교점 산출.

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/engine/solver/pm_diagram.py`](file:///f:/PyProject/AltDP_3rd/src/engine/solver/pm_diagram.py) | [NEW] | 2D/3D P-M 상관곡선 생성기, $\phi$ 보간 및 3차원 DCR 솔버 |
| [`tests/engine/test_pm_diagram.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_pm_diagram.py) | [NEW] | 2D/3D P-M 곡선 생성, 주요 점($P_0, P_{max}, P_b, P_t$) 검증 및 DCR 정확도 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] 2D 주요 주축($X, Y$) P-M 곡선 점 30~50개 고속 샘플링 (< 20ms)
- [x] $\epsilon_t$에 따른 압축지배($\phi=0.65$/$0.70$), 전이영역, 인장지배($\phi=0.85$) $\phi$ 보간 무결성
- [x] $\phi P_{n,max}$ 평탄화 상한선(Cap) 정상 적용 확인
- [x] 3D $\theta$-sweep 기반 상관곡면 및 Bresler 근사식 대비 오차 1.0% 미만 수렴 확인
- [x] 임의 하중점 $(P_u, M_{ux}, M_{uy})$에 대한 DCR 산출 및 안전/위험 판정 무결성 검증
- [x] `pytest tests/engine/test_pm_diagram.py` 100% 통과 (수행시간 < 0.5초)
