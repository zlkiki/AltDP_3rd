# 요구사항 24-1: Phase V1-3 Step 1 RC 전단벽 KDS 계산 엔진 & 경계요소 Pydantic 스키마 명세서

## 1. 개요 및 SSOT 계층 매핑

본 문서는 **RC 전단벽 (`rc_shear_wall`)**의 **Step 1 (KDS 계산 엔진 & Pydantic 스키마)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `rc_shear_wall` (카탈로그 No. 4, Tier 1 플래그십)
* **담당 소스 파일**: `src/engine/rc/wall.py`, `tests/engine/test_rc_wall.py`
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` C루틴 심볼 (`solver_wall__*CURBUPModeDlg*.c`, `DPLUS_RCS.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 RC Wall 장 (전단벽 면내 휨/전단 설계, 변위기반 특수경계요소 산정)
  3. `[3순위 학회 예제집]`: 콘크리트구조학회(2020) 기준 예제집
     - `예제 9.1`: 일반 철근콘크리트 전단벽 휨 및 전단설계 (상세식 $V_c$ 산정 및 배근비 검토)
     - `예제 9.2`: 특수철근콘크리트 구조벽체의 휨-전단 및 경계요소(SBE) 설계
  4. `[4순위 국가건설기준]`:
     - `KDS 14 20 72`: 콘크리트 벽체 설계기준 (일반벽체, 배근 최소기준)
     - `KDS 14 20 22`: 콘크리트구조 전단 및 비틀림 설계기준 (4.8 벽체 전단강도)
     - `KDS 14 20 20`: 콘크리트구조 휨 및 압축 설계기준 (면내 P-M 상관해석)
     - `KDS 14 20 80`: 콘크리트 내진설계기준 (4.6 구조벽체 및 특수구조벽체 경계요소)

---

## 2. Pydantic v2 데이터 입출력 스키마 상세 정의

`src/engine/rc/wall.py`에 아래의 엄밀한 공학 데이터 구조를 구현합니다:

### 2.1. 단면 및 재료 스키마 (`RCWallSection`)
```python
class WallSeismicCategory(str, Enum):
    ORDINARY = "ORDINARY"        # 보통 전단벽
    SPECIAL = "SPECIAL"          # 특수 전단벽 (내진 특별기준 KDS 14 20 80)

class RCWallSection(BaseModel):
    tw: float = Field(..., gt=0, description="전단벽 두께 (mm)")
    lw: float = Field(..., gt=0, description="전단벽 길이 (mm)")
    hw: float = Field(..., gt=0, description="벽체 층고 (mm)")
    total_hw: Optional[float] = Field(None, gt=0, description="건물 전체 벽체 높이 Hw (mm, 미입력 시 hw 사용)")
    cover: float = Field(40.0, gt=0, description="외곽 순피복 두께 (mm)")
    fck: float = Field(..., gt=0, description="콘크리트 설계기준압축강도 (MPa)")
    fy_v: float = Field(..., gt=0, description="수직 주철근 설계기준항복강도 (MPa)")
    fy_h: float = Field(..., gt=0, description="수평 전단철근 설계기준항복강도 (MPa)")
    fy_be: float = Field(..., gt=0, description="경계요소 철근 설계기준항복강도 (MPa)")
    lambda_factor: float = Field(1.0, ge=0.75, le=1.0, description="경량 콘크리트 계수 (보통 콘크리트: 1.0)")
    seismic_category: WallSeismicCategory = WallSeismicCategory.SPECIAL
```

### 2.2. 철근 배근 스키마 (`RCWallRebar`)
```python
class RCWallRebar(BaseModel):
    curtain_layers: int = Field(2, ge=1, le=2, description="배근 단수 (1: 단배근, 2: 복배근)")
    
    # 수직 철근
    vert_bar: str = Field("D13", description="수직 철근 규격")
    vert_spacing: float = Field(200.0, gt=0, description="수직 철근 배근 간격 (mm)")
    
    # 수평 철근
    horiz_bar: str = Field("D13", description="수평 전단철근 규격")
    horiz_spacing: float = Field(200.0, gt=0, description="수평 전단철근 배근 간격 (mm)")
    
    # 단부 집중 보강근
    end_bar: str = Field("D22", description="단부 집중 주철근 규격")
    end_bar_count: int = Field(4, ge=0, description="양단부 편측 집중 주철근 개수")
    
    # 경계요소 구속 철근 (SBE 횡보강근)
    tie_bar: str = Field("D10", description="경계요소 띠철근 규격")
    tie_spacing: float = Field(100.0, gt=0, description="경계요소 띠철근 수직 간격 (mm)")
    tie_legs_x: int = Field(2, ge=2, description="경계요소 두께방향 띠철근/크로스타이 다리수")
    tie_legs_y: int = Field(2, ge=2, description="경계요소 길이방향 띠철근 다리수")
```

### 2.3. 계수 하중 및 내진 변위 스키마 (`RCWallLoads`)
```python
class RCWallLoads(BaseModel):
    Pu: float = Field(..., description="계수 축하중 (kN, 압축 +)")
    Mu: float = Field(..., description="면내 계수 휨모멘트 (kN·m)")
    Vu: float = Field(..., description="면내 계수 전단력 (kN)")
    Nu: Optional[float] = Field(None, description="전단 산정용 계수 축력 (kN, 미입력 시 Pu 사용)")
    Mu_shear: Optional[float] = Field(None, description="전단 산정용 계수 휨모멘트 (kN·m, 미입력 시 Mu 사용)")
    delta_u: float = Field(30.0, ge=0.0, description="내진 해석에 의한 최상층 설계변위 (mm)")
```

### 2.4. 특수경계요소(SBE) 및 계산 결과 스키마 (`RCWallResult`)
```python
class SBECheckResult(BaseModel):
    is_required: bool = Field(..., description="특수경계요소 필요 여부")
    method: str = Field(..., description="판정 근거: 'DISPLACEMENT_BASED' 또는 'STRESS_BASED'")
    neutral_axis_c: float = Field(..., description="중립축 깊이 c (mm)")
    c_limit: float = Field(..., description="한계 중립축 깊이 c_limit = lw / (600 * (delta_u / Hw)) (mm)")
    stress_top: float = Field(..., description="극외단 압축응력 sigma_max (MPa)")
    stress_limit: float = Field(..., description="압축응력 한계 0.2*fck (MPa)")
    sbe_length_req: float = Field(..., description="경계요소 소요 구속길이 lc (mm)")
    sbe_width_req: float = Field(..., description="경계요소 소요 두께 bc (mm)")
    ash_req: float = Field(..., description="소요 횡보강근 단면적 Ash (mm²)")
    ash_provided: float = Field(..., description="배근된 횡보강근 단면적 Ash (mm²)")
    s_max: float = Field(..., description="횡보강근 최대 수직간격 (mm)")
    status: str = Field(..., description="판정 ('OK' 또는 'NG')")

class RCWallResult(BaseModel):
    # 단면 제원 및 배근비
    rho_v: float = Field(..., description="수직철근비 (최소 0.0025)")
    rho_h: float = Field(..., description="수평철근비 (최소 0.0025)")
    d_eff: float = Field(..., description="유효깊이 d = 0.8 * lw (mm)")
    
    # 전단강도 검토
    Vc: float = Field(..., description="콘크리트 전단강도 (kN)")
    Vs: float = Field(..., description="전단철근 부담 전단강도 (kN)")
    Vn_max: float = Field(..., description="전단강도 상한 5/6 * sqrt(fck) * tw * d (kN)")
    phi_Vn: float = Field(..., description="설계 전단강도 phi * Vn (kN, phi = 0.75)")
    dcr_shear: float = Field(..., description="전단 DCR = Vu / phi_Vn")
    shear_status: str = Field(..., description="전단 판정 ('OK' 또는 'NG')")
    
    # 면내 휨-축력 강도 검토
    phi_Mn: float = Field(..., description="축력 Pu 작용 하 면내 설계 휨강도 (kN·m)")
    dcr_flexure: float = Field(..., description="휨 DCR = Mu / phi_Mn")
    flexure_status: str = Field(..., description="휨 판정 ('OK' 또는 'NG')")
    
    # 특수경계요소(SBE) 검토
    sbe: SBECheckResult = Field(..., description="특수경계요소 상세 검토 결과")
    
    # 종합 판정
    governing_dcr: float = Field(..., description="지배 DCR = max(dcr_shear, dcr_flexure)")
    overall_status: str = Field(..., description="종합 판정 ('OK' 또는 'NG')")
```

---

## 3. 핵심 수치해석 및 KDS 공학 알고리즘

### 3.1. 전단강도 $V_c$ 산정 (KDS 14 20 22 4.8)
1. **유효깊이 $d$**:
   $$d = 0.8 l_w$$
2. **콘크리트 전단강도 $V_c$ (상세식)**:
   $$V_{c1} = 0.28 \lambda \sqrt{f_{ck}} t_w d + \frac{N_u d}{4 l_w}$$
   $$V_{c2} = \left[ 0.05 \lambda \sqrt{f_{ck}} + \frac{l_w (0.1 \lambda \sqrt{f_{ck}} + 0.2 \frac{N_u}{l_w t_w})}{\frac{M_u}{V_u} - \frac{l_w}{2}} \right] t_w d$$
   $$V_c = \min(V_{c1}, V_{c2}) \ge 0$$
   *(단, $\frac{M_u}{V_u} - \frac{l_w}{2} \le 0$인 경우 $V_{c2}$는 적용하지 않음)*
3. **간이식 옵션**:
   - $\frac{M_u}{V_u} \ge \frac{l_w}{2}$인 경우: $V_c = \frac{1}{6} \lambda \sqrt{f_{ck}} t_w d$
4. **전단철근 강도 $V_s$**:
   $$V_s = \frac{A_v f_{yt} d}{s_h}$$
5. **공칭전단강도 상한**:
   $$V_n \le \frac{5}{6} \sqrt{f_{ck}} t_w d$$
6. **설계 전단강도**:
   $$\phi V_n = \phi (V_c + V_s) \quad (\phi = 0.75)$$

### 3.2. 면내 휨-축력 강도 검토 (P-M 수치적분)
1. 벽체 단면을 층별(Fiber)로 분할하여 중립축 깊이 $c$에 따른 변형률 적분.
2. 콘크리트 등가직사각형 응력블록 ($\alpha_1 = 0.85, \beta_1$) 및 철근 항복응력 계산.
3. 주어진 계수축력 $P_u$에 대해 평형 조건을 만족하는 중립축 깊이 $c$를 이분법/뉴턴랩슨으로 결정.
4. 해당 $c$에서의 공칭 휨모멘트 $M_n$ 산정 후 강도감소계수 $\phi = 0.65 \sim 0.85$ 적용하여 $\phi M_n$ 도출.

### 3.3. 특수경계요소(SBE) 필요성 및 상세 설계 (KDS 14 20 80 4.6)
1. **변위기반 판정**:
   $$c \ge \frac{l_w}{600 \left(\frac{\delta_u}{h_w}\right)}$$
   - 위 조건 만족 시 특수경계요소 설치 필수.
2. **응력기반 판정**:
   - 탄성 해석에 의한 극외단 압축응력 $\sigma_{max} = \frac{P_u}{A_g} + \frac{M_u y}{I_g} \ge 0.2 f_{ck}$ 시 경계요소 필요.
3. **경계요소 구속 길이 $l_c$**:
   $$l_c \ge \max\left(c - 0.1 l_w, \; \frac{c}{2}\right)$$
4. **경계요소 횡보강근 소요량 $A_{sh}$**:
   $$\frac{A_{sh}}{s h_c} \ge \max\left[ 0.09 \frac{f_{ck}}{f_{yt}}, \; 0.3 \left(\frac{A_g}{A_{ch}} - 1\right) \frac{f_{ck}}{f_{yt}} \right]$$
5. **최대 수직 간격 $s_{max}$**:
   $$s_{max} \le \min\left(\frac{t_w}{3}, \; 6 d_b, \; 150\text{ mm}\right)$$

---

## 4. TDD 단위 테스트 계획 (`tests/engine/test_rc_wall.py`)

1. **테스트 케이스 1 [콘크리트학회 예제집 9.1 일반 전단벽 휨/전단]**:
   - 벽체 제원: $t_w = 300\text{ mm}, l_w = 4000\text{ mm}, h_w = 3500\text{ mm}$
   - $f_{ck} = 24\text{ MPa}, f_y = 400\text{ MPa}$
   - 배근: 복배근 D13@200 ($A_v = 254\text{ mm}^2$)
   - $P_u = 1200\text{ kN}, V_u = 800\text{ kN}, M_u = 2400\text{ kN}\cdot\text{m}$
   - 검증 기준: $V_c, V_s, \phi V_n$ 오차 $\le 0.10\%$.
2. **테스트 케이스 2 [콘크리트학회 예제집 9.2 특수경계요소(SBE) 검토]**:
   - 지진하중에 의한 설계변위 $\delta_u = 35\text{ mm}, H_w = 35000\text{ mm}$
   - 변위기반 한계 중립축 깊이 $c_{limit}$ 및 필요 여부 정확 일치.
   - 경계요소 소요길이 $l_c$ 및 $A_{sh}$ 오차 $\le 0.10\%$.
3. **테스트 케이스 3 [최소 철근비 및 전단강도 상한 검토]**:
   - 최소 배근비 $\rho_{min} = 0.0025$ 검증 및 $V_n \le \frac{5}{6}\sqrt{f_{ck}}t_w d$ 상한 클리핑 검증.

---

## 5. 완료 정의 (Definition of Done)

- [ ] `src/engine/rc/wall.py`에 Pydantic v2 스키마 및 수치해석 함수 구현 완료.
- [ ] `tests/engine/test_rc_wall.py` 작성 및 `pytest` 100% 통과 (Exit Code 0).
- [ ] 학회 예제집 대비 계산 오차 $\le 0.10\%$ 달성.
- [ ] Dummy/Mock 코드 0건 확인.
