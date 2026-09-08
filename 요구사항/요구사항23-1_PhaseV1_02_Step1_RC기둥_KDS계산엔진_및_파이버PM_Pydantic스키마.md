# 요구사항 23-1: Phase V1-2 Step 1 RC 기둥 KDS 계산 엔진 & 파이버 P-M 스키마 명세서

## 1. 개요 및 SSOT 계층 매핑

본 문서는 **RC 기둥 (`rc_column`)**의 **Step 1 (KDS 계산 엔진 & Pydantic 스키마)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `rc_column` (카탈로그 No. 2, Tier 1 플래그십)
* **담당 소스 파일**: `src/engine/rc/column.py`, `tests/engine/test_rc_column.py`
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` C루틴 심볼 (`solver__CHK_BCCO_*.c`, `CDBSolverTool`, `DPLUS_RCS.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 RC Column 장 (P-M 수치적분, Bresler 간이/엄밀식, 모멘트확대계수법)
  3. `[3순위 학회 예제집]`: 콘크리트구조학회(2020) 기준 예제집
     - `예제 5.1`: 4변 대칭 단주 P-M 상관곡선 작성 및 축력-휨 강도 검토
     - `예제 5.2`: 원형 띠철근/나선철근 기둥 축하중 및 P-M 곡선 검토
     - `예제 5.3`: 세장한 압축부재(장주) 횡구속/비구속 골조 모멘트 확대계수 $\delta_{ns}, \delta_s$ 산정
     - `예제 5.4`: 기둥 이축휨(Biaxial Bending) 및 Bresler 상호작용 검토
  4. `[4순위 국가건설기준]`: KDS 14 20 10 (일반/재료), KDS 14 20 20 (휨 및 압축), KDS 14 20 22 (전단)

---

## 2. Pydantic v2 데이터 입출력 스키마 상세 정의

`src/engine/rc/column.py`에 아래의 엄밀한 공학 데이터 구조를 구현합니다:

### 2.1. 단면 및 재료 스키마 (`RCColumnSection`)
```python
class ColumnShape(str, Enum):
    RECTANGULAR = "RECTANGULAR"  # 사각 기둥
    CIRCULAR = "CIRCULAR"        # 원형 기둥

class HoopType(str, Enum):
    TIED = "TIED"                # 띠철근 (phi = 0.65)
    SPIRAL = "SPIRAL"            # 나선철근 (phi = 0.70)

class RCColumnSection(BaseModel):
    shape: ColumnShape = ColumnShape.RECTANGULAR
    b: float = Field(..., gt=0, description="기둥 단면 폭 (mm, 사각)")
    h: float = Field(..., gt=0, description="기둥 단면 높이 (mm, 사각)")
    diameter: Optional[float] = Field(None, gt=0, description="원형 기둥 지름 (mm)")
    length: float = Field(..., gt=0, description="기둥 비지지 길이 Lu (mm)")
    cover: float = Field(40.0, gt=0, description="외곽 순피복 두께 (mm)")
    hoop_type: HoopType = HoopType.TIED
    fck: float = Field(..., gt=0, description="콘크리트 설계기준압축강도 (MPa)")
    fy: float = Field(..., gt=0, description="주철근 설계기준항복강도 (MPa)")
    fys: float = Field(..., gt=0, description="띠철근/나선철근 설계기준항복강도 (MPa)")
```

### 2.2. 철근 배근 스키마 (`RCColumnRebar`)
```python
class RebarLayer(BaseModel):
    depth_ratio: float = Field(..., ge=0.0, le=1.0, description="단면 상단 기준 상대 깊이 d_i / h")
    area: float = Field(..., gt=0, description="해당 층 총 철근 단면적 (mm²)")
    count: int = Field(..., gt=0, description="철근 개수")
    bar_dia: str = Field(..., description="철근 규격 (예: 'D25')")

class RCColumnRebar(BaseModel):
    pattern: str = Field("SYMMETRIC_4SIDE", description="배근 형태: 'SYMMETRIC_4SIDE', '2SIDE_X', '2SIDE_Y', 'CIRCULAR'")
    corner_bar: str = Field("D25", description="코너 주철근 규격")
    corner_count: int = Field(4, description="코너 주철근 수")
    side_x_bar: Optional[str] = Field("D22", description="X변 중간 주철근 규격")
    side_x_count: int = Field(0, ge=0, description="X변 편측 중간 철근 개수")
    side_y_bar: Optional[str] = Field("D22", description="Y변 중간 주철근 규격")
    side_y_count: int = Field(0, ge=0, description="Y변 편측 중간 철근 개수")
    hoop_bar: str = Field("D10", description="띠철근 규격")
    hoop_spacing: float = Field(300.0, gt=0, description="띠철근 배근 간격 (mm)")
    hoop_legs_x: int = Field(2, ge=2, description="X방향 띠철근 다리수")
    hoop_legs_y: int = Field(2, ge=2, description="Y방향 띠철근 다리수")
```

### 2.3. 설계 부재력 및 세장비 스키마 (`RCColumnLoads`)
```python
class ColumnEndCondition(str, Enum):
    BRACED = "BRACED"        # 횡구속 (Non-sway)
    UNBRACED = "UNBRACED"    # 횡비구속 (Sway)

class RCColumnLoads(BaseModel):
    Pu: float = Field(..., description="계수 축하중 (kN, 압축 +)")
    Mux_top: float = Field(0.0, description="상단 계수 휨모멘트 X축 (kN·m)")
    Mux_bot: float = Field(0.0, description="하단 계수 휨모멘트 X축 (kN·m)")
    Muy_top: float = Field(0.0, description="상단 계수 휨모멘트 Y축 (kN·m)")
    Muy_bot: float = Field(0.0, description="하단 계수 휨모멘트 Y축 (kN·m)")
    Vux: float = Field(0.0, description="계수 전단력 X방향 (kN)")
    Vuy: float = Field(0.0, description="계수 전단력 Y방향 (kN)")
    kx: float = Field(1.0, gt=0, description="X축 유효좌굴길이계수")
    ky: float = Field(1.0, gt=0, description="Y축 유효좌굴길이계수")
    end_condition: ColumnEndCondition = ColumnEndCondition.BRACED
    beta_dns: float = Field(0.0, ge=0.0, le=1.0, description="지속하중에 대한 최대 계수 축하중 비")
```

### 2.4. 계산 결과 스키마 (`RCColumnResult`)
```python
class PMPoint(BaseModel):
    P: float = Field(..., description="축강도 (kN)")
    M: float = Field(..., description="휨강도 (kN·m)")
    phi_P: float = Field(..., description="설계 축강도 (kN)")
    phi_M: float = Field(..., description="설계 휨강도 (kN·m)")
    c: float = Field(..., description="중립축 깊이 (mm)")
    epsilon_t: float = Field(..., description="최외단 인장철근 변형률")
    phi: float = Field(..., description="강도감소계수")

class RCColumnResult(BaseModel):
    Ag: float = Field(..., description="전체 단면적 (mm²)")
    Ast: float = Field(..., description="총 주철근 단면적 (mm²)")
    rho_g: float = Field(..., description="주철근비 (Ast/Ag, 0.01~0.08)")
    P0: float = Field(..., description="순수 압축 강도 (kN)")
    phi_Pn_max: float = Field(..., description="최대 설계 축강도 (kN)")
    P_tens: float = Field(..., description="순수 인장 강도 (kN)")
    phi_P_tens: float = Field(..., description="설계 순수 인장 강도 (kN)")
    # 세장비 및 모멘트 확대
    slenderness_x: float = Field(..., description="X축 세장비 k_x * Lu / r_x")
    slenderness_y: float = Field(..., description="Y축 세장비 k_y * Lu / r_y")
    slenderness_limit_x: float = Field(..., description="X축 세장비 한계")
    slenderness_limit_y: float = Field(..., description="Y축 세장비 한계")
    is_slender_x: bool = Field(..., description="X축 장주 여부")
    is_slender_y: bool = Field(..., description="Y축 장주 여부")
    delta_ns_x: float = Field(1.0, description="X축 비횡구속 모멘트확대계수")
    delta_ns_y: float = Field(1.0, description="Y축 비횡구속 모멘트확대계수")
    Mc_x: float = Field(..., description="확대 계수모멘트 X축 (kN·m)")
    Mc_y: float = Field(..., description="확대 계수모멘트 Y축 (kN·m)")
    # P-M 상관 곡선
    pm_curve_x: List[PMPoint] = Field(..., description="X축 200 파이버 P-M 상관곡선 데이터포인트")
    pm_curve_y: List[PMPoint] = Field(..., description="Y축 200 파이버 P-M 상관곡선 데이터포인트")
    # 이축휨 검토
    dcr_pm_x: float = Field(..., description="X축 P-M 강도비 (DCR)")
    dcr_pm_y: float = Field(..., description="Y축 P-M 강도비 (DCR)")
    bresler_ratio: float = Field(..., description="Bresler 상호작용비 (1/Pn <= 1/Pnx + 1/Pny - 1/P0)")
    # 전단 검토
    Vc_x: float = Field(..., description="X방향 콘크리트 부담 전단강도 (kN, 축력 보정)")
    Vs_x: float = Field(..., description="X방향 전단철근 부담 전단강도 (kN)")
    phi_Vn_x: float = Field(..., description="X방향 설계 전단강도 (kN)")
    dcr_shear_x: float = Field(..., description="X방향 전단 DCR")
    Vc_y: float = Field(..., description="Y방향 콘크리트 부담 전단강도 (kN, 축력 보정)")
    Vs_y: float = Field(..., description="Y방향 전단철근 부담 전단강도 (kN)")
    phi_Vn_y: float = Field(..., description="Y방향 설계 전단강도 (kN)")
    dcr_shear_y: float = Field(..., description="Y방향 전단 DCR")
    governing_dcr: float = Field(..., description="최대 지배 DCR")
    is_ok: bool = Field(..., description="전체 구조 안전성 판정 (DCR <= 1.000)")
```

---

## 3. KDS 핵심 수치 연산 알고리즘 상세 명세

### 3.1. 순수 압축강도 및 최대 설계축강도 (KDS 14 20 20 제4.1.2조)
$$P_0 = 0.85 f_{ck} (A_g - A_{st}) + f_y A_{st}$$
- 띠철근 기둥: $\phi = 0.65$, $\phi P_{n,max} = 0.80 \phi P_0$
- 나선철근 기둥: $\phi = 0.70$, $\phi P_{n,max} = 0.85 \phi P_0$

### 3.2. 200 파이버 단면 수치적분 P-M 상관곡면 생성
1. 단면을 높이 방향 $N=200$개 슬라이스 파이버로 이산화 ($y_i, A_{c,i}$).
2. 중립축 깊이 $c$를 무한대($P_0$)부터 0($P_{tens}$)까지 100~200 단계로 변화:
   - 각 파이버의 변형률 $\epsilon_i = 0.0033 \left(\frac{c - y_i}{c}\right)$
   - 콘크리트 압축 응력블록: $\alpha_1 = 0.85$, $\beta_1 = \max(0.65, 0.85 - 0.007(f_{ck} - 28))$
   - 각 철근 레이어의 응력 $f_{s,j} = E_s \epsilon_{s,j}$ (항복한계 $-f_y \le f_{s,j} \le f_y$)
   - 단면 내력 합력 산정:
     $$P_n = \int \sigma_c dA_c + \sum A_{s,j} f_{s,j}$$
     $$M_n = \int \sigma_c (y_{mid} - y) dA_c + \sum A_{s,j} f_{s,j} (y_{mid} - d_j)$$
3. 인장지배/압축지배 강도감소계수 $\phi$ 동적 산정:
   $$\phi = \begin{cases} 0.65 & (\epsilon_t \le \epsilon_y) \\ 0.65 + 0.20 \frac{\epsilon_t - \epsilon_y}{0.005 - \epsilon_y} & (\epsilon_y < \epsilon_t < 0.005) \\ 0.85 & (\epsilon_t \ge 0.005) \end{cases}$$

### 3.3. 세장비 및 모멘트 확대계수법 (KDS 14 20 20 제4.3절)
1. 단면 2차반경: $r_x = \sqrt{I_x / A_g} \approx 0.30 h$, $r_y \approx 0.30 b$ (원형 $r = 0.25 D$).
2. 횡구속 골조 세장비 한계:
   $$\left(\frac{k l_u}{r}\right)_{limit} = 34 - 12 \left(\frac{M_1}{M_2}\right) \le 40$$
   세장비 $k l_u / r \le$ 한계치이면 단주로 판정 ($\delta_{ns} = 1.0$). 초과 시 장주로 판정:
3. 부재 강성 $E I$:
   $$E I = \frac{0.4 E_c I_g}{1 + \beta_{dns}} \quad \text{또는} \quad E I = \frac{0.2 E_c I_g + E_s I_{se}}{1 + \beta_{dns}}$$
4. 오일러 좌굴하중: $P_c = \frac{\pi^2 E I}{(k l_u)^2}$
5. 모멘트 확대계수:
   $$C_m = 0.6 + 0.4 \left(\frac{M_1}{M_2}\right) \ge 0.4$$
   $$\delta_{ns} = \frac{C_m}{1 - P_u / (0.75 P_c)} \ge 1.0$$
   $$M_c = \delta_{ns} M_{2,min}, \quad M_{2,min} = P_u (15 + 0.03 h) \text{ mm}$$

### 3.4. 이축휨 검토 (Bresler 상호작용 역수식)
$$\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_0}$$
- 판정 조건: $P_u \le \phi P_n \iff \frac{P_u}{\phi P_n} \le 1.000$

### 3.5. 축하중을 받는 기둥의 전단강도 (KDS 14 20 22 제4.3.2조)
$$V_c = \frac{1}{6} \left(1 + \frac{P_u}{14 A_g}\right) \lambda \sqrt{f_{ck}} b_w d$$
$$V_s = \frac{A_v f_{ys} d}{s}$$
$$\phi V_n = \phi (V_c + V_s), \quad \phi = 0.75$$

---

## 4. 단위 테스트 및 0.10% 오차 검증 데이터셋 (`tests/engine/test_rc_column.py`)
*(원문 검증 우선(Source-Verification First) 프로토콜에 따라 kcsc2md `source/예제집/콘크리트구조 학회기준 예제집(2020)_OCR.pdf` 원본 렌더링 실측 검증 완료)*

* **테스트 케이스 1 (학회 예제집 5.1 사각형 단주 기둥 설계, 원본 PDF 116~119p 실측 검증)**:
  - $b=500\text{ mm}, h=500\text{ mm}$, 피복두께 $40\text{ mm}$.
  - $f_{ck}=27\text{ MPa}, f_y=400\text{ MPa}$.
  - 배근: **8-D22** ($d_b=22.2\text{ mm}, A_b=387.1\text{ mm}^2, A_{st}=3,097\text{ mm}^2$, 4면 대칭 배치), 띠철근 D10.
  - 계수 하중: $P_u=1,250\text{ kN}, M_u=375\text{ kN}\cdot\text{m}$ (작용 편심 $e=300\text{ mm}$).
  - 원문 공인 정답:
    * 중립축 $c = 192.6\text{ mm}$
    * 공칭 강도: $P_n = 1,590\text{ kN}, M_n = 477\text{ kN}\cdot\text{m}$
    * 최외단 인장철근 변형률: $\epsilon_{s3} = 0.00423$ (변화구간 단면)
    * 강도감소계수: $\phi = 0.799$
    * 설계 강도: $\phi P_n = 1,270\text{ kN} > P_u (=1,250\text{ kN})$, $\phi M_n = 381\text{ kN}\cdot\text{m} > M_u (=375\text{ kN}\cdot\text{m})$
  - 오차 검증: AltDP_3rd 200 파이버 P-M 상관곡선 상의 강도와 원문 정답 오차 $\le 0.10\%$.

* **테스트 케이스 2 (학회 예제집 5.3 2축하중을 받는 정사각형 기둥 설계, 원본 PDF 125p 실측 검증)**:
  - 단면 및 재료: $f_{ck}=35\text{ MPa}, f_y=400\text{ MPa}$.
  - 계수 하중: $P_u=5,300\text{ kN}, M_{ux}=404\text{ kN}\cdot\text{m}, M_{uy}=168\text{ kN}\cdot\text{m}$.
  - 압축지배 소요 공칭강도: $P_n = 8,153.8\text{ kN}, M_{nx} = 621.5\text{ kN}\cdot\text{m}, M_{ny} = 258.5\text{ kN}\cdot\text{m}$ ($\phi=0.65$).
  - Bresler 역수식 상호작용비 및 2축 휨 DCR 정밀 검증 ($\le 0.10\%$).

* **테스트 케이스 3 (학회 예제집 5.4 횡구속 골조에서 기둥의 장주효과, 원본 PDF 130p 실측 검증)**:
  - 단면: $600 \times 600\text{ mm}$, 순 층간 높이 $l_u = 6,500\text{ mm}$, $k=1.0$ (횡구속 골조).
  - 재료: $f_{ck}=40\text{ MPa}, f_y=400\text{ MPa}$.
  - 세장비 한계 $k l_u / r$ 판정 (단주/장주 분기), 오일러 좌굴하중 $P_c$, 모멘트확대계수 $\delta_{ns}$, 확대계수모멘트 $M_c$ 검증 ($\le 0.10\%$).

* **테스트 케이스 4 (원형 나선철근 기둥 및 축력 보정 전단강도)**:
  - 원형 기둥 $D=600\text{ mm}$, 나선철근 $\phi=0.70$, $P_{n,max} = 0.85 \phi P_0$ 대조.
  - 전단강도 $V_c$ (축력 보정 효과 $1 + P_u/(14 A_g)$) 및 전단철근 $V_s$ 정밀 검증.

---

## 5. 완료 정의 (DoD: Definition of Done)

- [ ] `src/engine/rc/column.py` 내 모든 스키마 및 알고리즘 구현 완료
- [ ] `pytest tests/engine/test_rc_column.py` 100% 통과 (Exit Code 0)
- [ ] 원문 검증 우선 프로토콜에 따른 학회 예제집 5.1/5.3/5.4 실측 원본 정답 대비 계산 오차율 $\le 0.10\%$ 달성
- [ ] 더미 코드(Mock/Hardcoded) 0건 확인
