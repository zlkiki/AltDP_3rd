# 요구사항 22-4-1-1: Phase V1-01 Step 4-1 RC 보 KDS 14 20 20: 2022 철근비 기준 현행화 및 3-Station 휨·전단 수치해석 엔진 고도화 명세서

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 설계 엔진의 **(1) 구버전 철근비 공식($\rho_{\min}, \rho_{\max}$) 완전 배제 및 현행 KDS 14 20 20: 2022 단일 규격화**, **(2) 철근 강도별($f_y$) 최소 허용 순인장변형률 $\epsilon_{t,\min}$ 및 한계 중립축 깊이비 정밀 산정**, **(3) 단부 I, 중앙 M, 단부 J 3개 위치별 정/부모멘트 및 전단 역학 분리 해석**, 그리고 **(4) 배근 유형(`BeamArrangeType`) 스키마 지원**을 완수하기 위한 계산 엔진 전용 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 계산 엔진: 최소철근량 $\phi M_n \ge 1.2 M_{cr}$, 강도별 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$, 3-Station 정/부모멘트 분리 해석, `BeamArrangeType` Enum)
  - `tests/engine/test_rc_beam.py` (엔진 단위 테스트: $f_y$ 강도별 변형률, $M_{cr}$, 3-Station 위치별 정/부모멘트 휨강도 검증)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 20: 2022 비선형 평형 방정식 및 3-Station 역학 분리 연산
* **1순위/4순위 설계기준 SSOT**:
  - **KDS 14 20 20 : 2022** (콘크리트구조 휨 및 압축 설계기준)
    * 4.2.2 휨부재의 최소 철근량: $\phi M_n \ge 1.2 M_{cr}$ (단, $A_s \ge \frac{4}{3} A_{s,req}$ 만족 시 적용 예외)
    * 4.1.2 휨부재의 최대 철근량 및 연성 한계: 최외단 인장철근 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$ (철근 강도별 분기) 및 중립축 깊이비 한계 $c/d_t \le (c/d_t)_{\lim}$

---

## 2. 현행 기준(KDS 14 20 20 : 2022) 수치 알고리즘 상세 명세

### 2.1. 최소 철근량 검토 KDS 현행화 (구버전 철근비 완전 배제)
1. **구버전 철근비 폐기**:
   - $\rho_{\min} = \max(0.25\sqrt{f_{ck}}/f_y, 1.4/f_y)$ 및 $\rho_{\max} = 0.85\beta_1 \frac{f_{ck}}{f_y} \frac{\epsilon_{cu}}{\epsilon_{cu}+0.004}$를 엔진 코드 및 반환 모델에서 완전히 제거합니다.
2. **현행 KDS 14 20 20 : 2022 4.2.2 최소 휨강도 조건**:
   $$\phi M_n \ge 1.2 M_{cr}$$
   - **균열모멘트 $M_{cr}$ 산정**:
     $$M_{cr} = \frac{f_r I_g}{y_t}, \quad f_r = 0.63 \lambda \sqrt{f_{ck}}$$
     (보통골재 콘크리트 $\lambda = 1.0$, 비균열 전단면 2차 모멘트 $I_g = \frac{b h^3}{12}$, 중립축까지 거리 $y_t = \frac{h}{2}$)
   - **예외 규정 (4.2.2(3))**: 해석에 의해 요구되는 소요 철근량보다 1/3 이상 인장철근이 더 배치되는 경우($A_s \ge \frac{4}{3} A_{s,req}$), $1.2 M_{cr}$ 조건을 적용하지 않고 만족(O.K)으로 판정.

### 2.2. 최대 철근량 및 연성 한계 검토 (철근 강도별 정밀 분기)
1. **현행 KDS 14 20 20 : 2022 4.1.2(3) 강도별 최소 허용 순인장변형률 $\epsilon_{t,\min}$**:
   - $f_y \le 400\text{ MPa}$ 인 경우:
     $$\epsilon_{t,\min} = \mathbf{0.0040}$$
   - $f_y > 400\text{ MPa}$ 인 경우:
     $$\epsilon_{t,\min} = \mathbf{2.0 \, \epsilon_y} = 2.0 \times \frac{f_y}{E_s} \quad (E_s = 200,000\text{ MPa})$$
     - SD500 ($f_y = 500\text{ MPa}$): $\epsilon_y = 0.0025 \rightarrow \epsilon_{t,\min} = \mathbf{0.0050}$
     - SD600 ($f_y = 600\text{ MPa}$): $\epsilon_y = 0.0030 \rightarrow \epsilon_{t,\min} = \mathbf{0.0060}$
2. **중립축 깊이비 한계 ($(c/d_t)_{\lim}$)**:
   $$\frac{c}{d_t} \le \left(\frac{c}{d_t}\right)_{\lim} = \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_{t,\min}}$$
   - 극한압축변형률 $\epsilon_{cu}$:
     * $f_{ck} \le 40\text{ MPa}$: $\epsilon_{cu} = 0.0033$
     * $f_{ck} > 40\text{ MPa}$: $\epsilon_{cu} = \max\left(0.0028, 0.0033 - 0.0001 \times \frac{f_{ck} - 40}{10}\right)$
   - $f_{ck} \le 40\text{ MPa}$ 기준 한계값:
     * SD400: $(c/d_t)_{\lim} = \frac{0.0033}{0.0033 + 0.0040} = \mathbf{0.452}$
     * SD500: $(c/d_t)_{\lim} = \frac{0.0033}{0.0033 + 0.0050} = \mathbf{0.398}$
     * SD600: $(c/d_t)_{\lim} = \frac{0.0033}{0.0033 + 0.0060} = \mathbf{0.355}$

### 2.3. 3-Station 정/부모멘트 및 전단 역학 분리
1. **단부 I (End-I)**:
   - 지배 하중: 부모멘트 ($M_u^-$)
   - 인장철근: 상부 철근 ($A_s = A_{s,\text{top}}$) / 압축철근: 하부 철근 ($A_s' = A_{s,\text{bot}}$)
   - 거동 단면: 상부 인장 균열로 인해 플랜지 효과가 배제되므로 **복부 폭 $b$ 직사각형 보로 해석**.
2. **중앙부 M (Center-M)**:
   - 지배 하중: 정모멘트 ($M_u^+$)
   - 인장철근: 하부 철근 ($A_s = A_{s,\text{bot}}$) / 압축철근: 상부 철근 ($A_s' = A_{s,\text{top}}$)
   - 거동 단면: 상부 플랜지 압축을 받으므로 **유효폭 $b_f$를 갖는 T형 보로 해석**.
3. **단부 J (End-J)**:
   - 지배 하중: 부모멘트 ($M_u^-$)
   - 인장철근: 상부 철근 ($A_s = A_{s,\text{top}}$) / 압축철근: 하부 철근 ($A_s' = A_{s,\text{bot}}$)
   - 거동 단면: 복부 폭 $b$ 직사각형 보로 해석.

---

## 3. Pydantic 스키마 및 입출력 모델 확장

### 3.1. `BeamArrangeType` Enum 추가 (`src/engine/rc/beam.py`)
```python
class BeamArrangeType(str, Enum):
    """RC Beam Reinforcement Detailing Scope Option."""
    ONE_SECTION = "ONE_SECTION"          # 배근 유형-1: 전단면 (1개 단면)
    SYMMETRIC_ENDS = "SYMMETRIC_ENDS"    # 배근 유형-2: 양단부와 중앙부 (2개 단면 대칭)
    THREE_STATIONS = "THREE_STATIONS"    # 배근 유형-3: 각단부와 중앙부 (3개 단면 독립)
```

### 3.2. `RCBeamRebar` 모델에 배근 유형 필드 추가
```python
class RCBeamRebar(BaseModel):
    arrange_type: BeamArrangeType = BeamArrangeType.SYMMETRIC_ENDS
    end_i: SectionRebarGroup
    center_m: SectionRebarGroup
    end_j: SectionRebarGroup
    torsion_side_bar: Optional[str] = "D13"
    torsion_side_count: int = 0
```

### 3.3. `FlexureResult` 모델 현행화
```python
class FlexureResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    Mu: float
    phi_Mn: float
    d: float
    dt: float
    c: float
    a: float
    epsilon_t: float
    epsilon_t_min: float         # 신규: 강도별 최소 허용 순인장변형률 (0.004 또는 2.0 ey)
    c_dt_ratio: float            # 신규: 중립축 깊이비 c / dt
    c_dt_limit: float            # 신규: 한계 중립축 깊이비 (c/dt)lim
    phi: float
    is_compression_yielding: bool
    As_req: float
    As_prov: float
    rho: float
    Mcr: float                   # 신규: 균열모멘트 Mcr (kN·m)
    phi_Mn_min: float            # 신규: 1.2 Mcr (kN·m)
    is_min_flexure_ok: bool      # 신규: phi_Mn >= 1.2 Mcr (또는 As >= 4/3 As_req) 만족 여부
    is_ductility_ok: bool        # 신규: epsilon_t >= epsilon_t_min 만족 여부
    dcr: float
    status: str                  # "OK" | "NG"
```

---

## 4. 단위 테스트 명세 (`tests/engine/test_rc_beam.py`)

1. **`test_flexure_kds_min_reinforcement_mcr`**:
   - $f_{ck} = 27\text{ MPa}$, $b = 400\text{ mm}$, $h = 600\text{ mm}$에서 $M_{cr}$ 및 $1.2 M_{cr}$ 산정값 검증.
   - $\phi M_n \ge 1.2 M_{cr}$ 조건 판정 및 $A_s \ge \frac{4}{3} A_{s,req}$ 예외 적용 여부 검증.
2. **`test_flexure_ductility_strain_limit_by_fy`**:
   - SD400 ($f_y = 400\text{ MPa}$): $\epsilon_{t,\min} = 0.0040$, $(c/d_t)_{\lim} \approx 0.452$
   - SD500 ($f_y = 500\text{ MPa}$): $\epsilon_{t,\min} = 0.0050$, $(c/d_t)_{\lim} \approx 0.398$
   - SD600 ($f_y = 600\text{ MPa}$): $\epsilon_{t,\min} = 0.0060$, $(c/d_t)_{\lim} \approx 0.355$
3. **`test_3station_moment_direction_separation`**:
   - End-I(부모멘트, 상부인장 직사각형 보)와 Center-M(정모멘트, 하부인장 T형 보)의 유효 인장철근 및 휨강도 분리 연산 검증.

---

## 5. 완료 검증 기준 (DoD)

- [ ] `src/engine/rc/beam.py`에서 구버전 `rho_min`, `rho_max` 관련 계산이 완전히 제거될 것.
- [ ] $\phi M_n \ge 1.2 M_{cr}$ (또는 $A_s \ge \frac{4}{3} A_{s,req}$) 판정이 정확히 수행될 것.
- [ ] 철근 강도별($f_y \le 400$ 시 $0.004$, $f_y > 400$ 시 $2.0 \epsilon_y$) $\epsilon_{t,\min}$ 판정 및 한계 중립축 깊이비가 정확히 산정될 것.
- [ ] End-I(부모멘트 상부인장), Center-M(정모멘트 하부인장), End-J(부모멘트)의 휨강도가 정확히 분리 계산될 것.
- [ ] `tests/engine/test_rc_beam.py`의 신규 및 기존 단위 테스트가 100% 무결점 통과할 것.
- [ ] 전체 회귀 테스트 `pytest` 349+ 통과를 유지할 것.
