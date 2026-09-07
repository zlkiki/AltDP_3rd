# 요구사항 25-1: Phase V1-4 Step 1 철골 보/기둥 KDS 계산 엔진 & Pydantic 스키마 명세서

## 1. 개요 및 SSOT 계층 매핑

본 문서는 **철골 보/기둥 (`steel_beam_column`)**의 **Step 1 (KDS 계산 엔진 & Pydantic v2 스키마)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_beam_column` (카탈로그 No. 22, Tier 1 플래그십)
* **담당 소스 파일**:
  - 엔진 구현: [`src/engine/steel/beam.py`](file:///f:/PyProject/AltDP_3rd/src/engine/steel/beam.py), [`src/engine/steel/column.py`](file:///f:/PyProject/AltDP_3rd/src/engine/steel/column.py), [`src/engine/steel/compactness.py`](file:///f:/PyProject/AltDP_3rd/src/engine/steel/compactness.py)
  - API 라우트: [`src/api/routes/steel.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/steel.py)
  - 테스트: [`tests/engine/test_steel_beam.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_steel_beam.py), [`tests/engine/test_steel_column.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_steel_column.py)
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` C루틴 (`steel__CHK_USMC_*.c`, `DPLUS_STEEL.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 Steel Beam-Column 장 (AISC 360 / KDS 14 31 10 한계상태설계법, LTB 횡좌굴강도, 유효단면계수, 보-기둥 P-M 상관식)
  3. `[3순위 학회 예제집]`: 한국강구조학회 『KDS 41 31 00 : 2019에 따른 강구조설계 예제집』
     - `제5장 예제 5.1`: H형강 축압축재의 휨좌굴강도 산정 ($H\text{-}300\times 300\times 10\times 15$, $KL/r$, $F_{cr}$, $\phi_c P_n$)
     - `제6장 예제 6.1, 6.2`: H형강 강축휨 부재 횡지지구속 및 비지지 LTB 좌굴강도 ($H\text{-}400\times 200\times 8\times 13$, $L_b$ vs $L_p, L_r$, $\phi_b M_n$)
     - `제7장 예제 7.1`: H형강 보의 웨브 전단강도 산정 ($C_v$, $\phi_v V_n$)
     - `제8장 예제 8.1, 8.2`: 축압축력과 이축모멘트를 동시에 받는 H형강 보-기둥 조합력 P-M 검토 (식 4.5-1, 식 4.5-2)
  4. `[4순위 국가건설기준]`:
     - `KDS 14 31 10`: 강구조부재 설계기준 (4.1 인장, 4.2 휨, 4.3 압축, 4.4 전단, 4.5 조합력 및 비틀림)

---

## 2. Pydantic v2 데이터 입출력 스키마 상세 정의

`src/engine/steel/` 및 `src/api/routes/steel.py`에 적용될 엄밀한 공학 데이터 구조입니다:

### 2.1. 단면 및 형강 분류 스키마 (`SteelSection`)
```python
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SteelSectionType(str, Enum):
    H_SHAPE = "H"           # H형강 (Rolled / Built-up)
    BOX_SHAPE = "BOX"       # 각형강관 (Rectangular Hollow Section)
    PIPE_SHAPE = "PIPE"     # 원형강관 (Circular Hollow Section)
    CHANNEL = "CHANNEL"     # ㄷ형강 (C-Channel)

class SteelSection(BaseModel):
    section_type: SteelSectionType = SteelSectionType.H_SHAPE
    designation: str = Field("H-400x200x8x13", description="KS 표준 호칭 규격")
    
    # 치수 (mm)
    H: float = Field(..., gt=0, description="단면 전체 높이 (Depth, mm)")
    B: float = Field(..., gt=0, description="플랜지 폭 (Flange Width, mm)")
    tw: float = Field(..., gt=0, description="웨브 두께 (Web Thickness, mm)")
    tf: float = Field(..., gt=0, description="플랜지 두께 (Flange Thickness, mm)")
    r: float = Field(16.0, ge=0, description="필릿 반경 (Fillet Radius, mm)")
    
    # 강재 재료 성질
    material_name: str = Field("SM355", description="강종 명칭 (SS275, SM355, SM460 등)")
    Fy: float = Field(355.0, gt=0, description="설계기준항복강도 (MPa)")
    Fu: float = Field(490.0, gt=0, description="설계인장강도 (MPa)")
    E: float = Field(205000.0, gt=0, description="강재 탄성계수 (MPa)")
    G: float = Field(79000.0, gt=0, description="강재 전단탄성계수 (MPa)")
    
    # 기하특성치 (자동 계산 또는 SDB 연동)
    A: float = Field(..., gt=0, description="단면적 (mm²)")
    Ix: float = Field(..., gt=0, description="강축 단면2차모멘트 (mm⁴)")
    Iy: float = Field(..., gt=0, description="약축 단면2차모멘트 (mm⁴)")
    Zx: float = Field(..., gt=0, description="강축 소성단면계수 (mm³)")
    Zy: float = Field(..., gt=0, description="약축 소성단면계수 (mm³)")
    Sx: float = Field(..., gt=0, description="강축 탄성단면계수 (mm³)")
    Sy: float = Field(..., gt=0, description="약축 탄성단면계수 (mm³)")
    rx: float = Field(..., gt=0, description="강축 회전반경 (mm)")
    ry: float = Field(..., gt=0, description="약축 회전반경 (mm)")
    J: float = Field(..., gt=0, description="비틀림상수 (Torsional Constant, mm⁴)")
    Cw: float = Field(..., ge=0, description="휨비틀림상수 (Warping Constant, mm⁶)")
```

### 2.2. 부재 기하 및 지지조건 스키마 (`SteelMemberGeometry`)
```python
class SteelMemberGeometry(BaseModel):
    L: float = Field(..., gt=0, description="부재 전장 길이 (mm)")
    
    # 좌굴 길이 및 유효좌굴길이계수
    Lx: float = Field(..., gt=0, description="강축 비지지 좌굴길이 (mm)")
    Ly: float = Field(..., gt=0, description="약축 비지지 좌굴길이 (mm)")
    Kx: float = Field(1.0, gt=0, description="강축 유효좌굴길이계수")
    Ky: float = Field(1.0, gt=0, description="약축 유효좌굴길이계수")
    
    # 횡지지 및 LTB 조건
    Lb: float = Field(..., gt=0, description="횡비지지길이 (Lateral Unbraced Length, mm)")
    Cb: float = Field(1.0, ge=1.0, le=3.0, description="모멘트 구배계수 (기본 1.0)")
    
    # 2차 모멘트 확대계수 산정용 파라미터
    Cmx: float = Field(1.0, ge=0.4, le=1.0, description="강축 등가모멘트계수")
    Cmy: float = Field(1.0, ge=0.4, le=1.0, description="약축 등가모멘트계수")
    B1_x: float = Field(1.0, ge=1.0, description="강축 비횡변위 모멘트확대계수")
    B1_y: float = Field(1.0, ge=1.0, description="약축 비횡변위 모멘트확대계수")
```

### 2.3. 계수 설계하중 스키마 (`SteelLoads`)
```python
class SteelLoads(BaseModel):
    Pu: float = Field(0.0, description="계수 축력 (kN, 압축 +, 인장 -)")
    Mux: float = Field(0.0, ge=0.0, description="강축 계수 휨모멘트 (kN·m)")
    Muy: float = Field(0.0, ge=0.0, description="약축 계수 휨모멘트 (kN·m)")
    Vux: float = Field(0.0, ge=0.0, description="강축 계수 전단력 (kN)")
    Vuy: float = Field(0.0, ge=0.0, description="약축 계수 전단력 (kN)")
    
    # 쿼터 모멘트 (Cb 자동 계산용, 옵션)
    Mmax: Optional[float] = Field(None, description="비지지 구간 최대 모멘트 |Mmax| (kN·m)")
    MA: Optional[float] = Field(None, description="1/4 지점 모멘트 |MA| (kN·m)")
    MB: Optional[float] = Field(None, description="중앙(1/2) 지점 모멘트 |MB| (kN·m)")
    MC: Optional[float] = Field(None, description="3/4 지점 모멘트 |MC| (kN·m)")
```

### 2.4. 계산 결과 종합 스키마 (`SteelBeamColumnResult`)
```python
class CompactnessClass(str, Enum):
    COMPACT = "COMPACT"             # 조밀 단면
    NON_COMPACT = "NON_COMPACT"     # 비조밀 단면
    SLENDER = "SLENDER"             # 세장판 단면

class SteelElementCompactness(BaseModel):
    lambda_val: float = Field(..., description="실제 판폭두께비")
    lambda_p: float = Field(..., description="조밀 한계 판폭두께비")
    lambda_r: float = Field(..., description="비조밀 한계 판폭두께비")
    classification: CompactnessClass = Field(..., description="판폭두께비 판정")

class SteelBeamColumnResult(BaseModel):
    # 1. 단면 조밀성
    flange_compactness: SteelElementCompactness
    web_compactness: SteelElementCompactness
    overall_classification: CompactnessClass
    Q: float = Field(1.0, le=1.0, description="세장판 단면 감소계수 Q")
    
    # 2. 휨강도 및 LTB (X축)
    Mp_x: float = Field(..., description="소성 휨강도 (kN·m)")
    Lp: float = Field(..., description="소성 한계 비지지길이 (mm)")
    Lr: float = Field(..., description="비탄성 LTB 한계 비지지길이 (mm)")
    Mn_x: float = Field(..., description="공칭 강축 휨강도 (kN·m)")
    phi_b: float = Field(0.90, description="휨강도 저감계수")
    phi_Mn_x: float = Field(..., description="설계 강축 휨강도 (kN·m)")
    dcr_flexure_x: float = Field(..., description="강축 휨 DCR = Mux / phi_Mn_x")
    
    # 3. 휨강도 (Y축)
    Mp_y: float = Field(..., description="약축 소성 휨강도 (kN·m)")
    Mn_y: float = Field(..., description="공칭 약축 휨강도 (kN·m)")
    phi_Mn_y: float = Field(..., description="설계 약축 휨강도 (kN·m)")
    dcr_flexure_y: float = Field(..., description="약축 휨 DCR = Muy / phi_Mn_y")
    
    # 4. 압축/인장강도
    slenderness_x: float = Field(..., description="강축 세장비 Kx*Lx / rx")
    slenderness_y: float = Field(..., description="약축 세장비 Ky*Ly / ry")
    max_slenderness: float = Field(..., description="최대 세장비 max(KL/r)")
    is_slenderness_ok: bool = Field(..., description="세장비 제한 KL/r <= 200 적합 여부")
    Fe: float = Field(..., description="Euler 탄성좌굴응력 (MPa)")
    Fcr: float = Field(..., description="임계좌굴응력 (MPa)")
    Pn: float = Field(..., description="공칭 압축강도 (kN)")
    phi_c: float = Field(0.90, description="압축강도 저감계수")
    phi_Pn: float = Field(..., description="설계 압축강도 (kN)")
    dcr_axial: float = Field(..., description="축력 DCR = Pu / phi_Pn")
    
    # 5. 전단강도
    Cv: float = Field(..., description="웨브 전단좌굴계수")
    Vn: float = Field(..., description="공칭 전단강도 (kN)")
    phi_v: float = Field(0.90, description="전단강도 저감계수")
    phi_Vn: float = Field(..., description="설계 전단강도 (kN)")
    dcr_shear: float = Field(..., description="전단 DCR = Vu / phi_Vn")
    
    # 6. P-M 축휨 상호작용
    pm_formula: str = Field(..., description="적용 수식 ('Eq 4.5-1 (Pu/phiPn >= 0.2)' 또는 'Eq 4.5-2 (Pu/phiPn < 0.2)')")
    dcr_pm: float = Field(..., description="종합 P-M 상호작용 DCR")
    
    # 7. 종합 판정
    max_dcr: float = Field(..., description="지배 최대 DCR = max(dcr_pm, dcr_shear)")
    status: str = Field(..., description="'OK' 또는 'NG'")
```

---

## 3. KDS 14 31 10 정밀 수치 연산 알고리즘

### 3.1. 단면 조밀성(Compactness) 판정 (표 4.1-1, 표 4.1-2)
* **플랜지 (I형강/H형강 휨재의 균일압축 플랜지)**:
  $$\lambda = \frac{B}{2 t_f}, \quad \lambda_p = 0.38 \sqrt{\frac{E}{F_y}}, \quad \lambda_r = 1.0 \sqrt{\frac{E}{F_y}}$$
* **웨브 (I형강/H형강 휨재의 휨 웨브)**:
  $$\lambda = \frac{H - 2(t_f + r)}{t_w}, \quad \lambda_p = 3.76 \sqrt{\frac{E}{F_y}}, \quad \lambda_r = 5.70 \sqrt{\frac{E}{F_y}}$$
* **축압축재 판폭두께비 한계값**:
  - 플랜지: $\lambda_r = 0.56 \sqrt{E/F_y}$
  - 웨브: $\lambda_r = 1.49 \sqrt{E/F_y}$
* **판정 기준**:
  - $\lambda \le \lambda_p \implies \text{COMPACT (조밀)}$
  - $\lambda_p < \lambda \le \lambda_r \implies \text{NON\_COMPACT (비조밀)}$
  - $\lambda > \lambda_r \implies \text{SLENDER (세장판, 단면감소계수 } Q < 1.0 \text{ 산정)}$

### 3.2. 휨강도 및 횡비틀림좌굴(LTB, KDS 14 31 10 4.2)
1. **소성모멘트**: $M_p = F_y Z_x$
2. **횡지지 한계길이 $L_p$**:
   $$L_p = 1.76 r_y \sqrt{\frac{E}{F_y}}$$
3. **비탄성 LTB 한계길이 $L_r$**:
   $$L_r = 1.95 r_{ts} \frac{E}{0.7 F_y} \sqrt{\frac{J c}{S_x h_0} + \sqrt{\left(\frac{J c}{S_x h_0}\right)^2 + 6.76 \left(\frac{0.7 F_y}{E}\right)^2}}$$
   - 여기서 $h_0 = H - t_f$, $c = 1.0$ (2축 대칭 I형강), $r_{ts}^2 = \frac{\sqrt{I_y C_w}}{S_x}$
4. **공칭 휨강도 $M_{nx}$**:
   - **구간 1 ($L_b \le L_p$)**: $M_{nx} = M_p$
   - **구간 2 ($L_p < L_b \le L_r$)**:
     $$M_{nx} = C_b \left[ M_p - (M_p - 0.7 F_y S_x)\left(\frac{L_b - L_p}{L_r - L_p}\right) \right] \le M_p$$
   - **구간 3 ($L_b > L_r$)**:
     $$F_{cr} = \frac{C_b \pi^2 E}{\left(\frac{L_b}{r_{ts}}\right)^2} \sqrt{1 + 0.078 \frac{J c}{S_x h_0}\left(\frac{L_b}{r_{ts}}\right)^2}, \quad M_{nx} = F_{cr} S_x \le M_p$$
5. **설계 휨강도**: $\phi_b M_{nx} = 0.90 M_{nx}$

### 3.3. 압축좌굴강도(KDS 14 31 10 4.3)
1. **유효세장비**: $\frac{KL}{r} = \max\left(\frac{K_x L_x}{r_x}, \frac{K_y L_y}{r_y}\right) \le 200$
2. **오일러 탄성좌굴응력**:
   $$F_e = \frac{\pi^2 E}{\left(\frac{KL}{r}\right)^2}$$
3. **임계좌굴응력 $F_{cr}$**:
   - $\frac{KL}{r} \le 4.71 \sqrt{\frac{E}{F_y}} \left(\frac{F_y}{F_e} \le 2.25\right) \implies F_{cr} = \left[0.658^{\frac{F_y}{F_e}}\right] F_y$ (비탄성 좌굴)
   - $\frac{KL}{r} > 4.71 \sqrt{\frac{E}{F_y}} \left(\frac{F_y}{F_e} > 2.25\right) \implies F_{cr} = 0.877 F_e$ (탄성 좌굴)
4. **설계 압축강도**:
   $$\phi_c P_n = 0.90 F_{cr} A_g \quad (\text{세장판 시 } A_g \rightarrow A_e)$$

### 3.4. 웨브 전단강도(KDS 14 31 10 4.4)
1. **웨브 폭두께비**: $h/t_w = (H - 2(t_f + r)) / t_w$
2. **전단좌굴계수 $C_v$**:
   - $h/t_w \le 2.24 \sqrt{E/F_y} \implies C_v = 1.0, \quad \phi_v = 1.00$
   - $2.24 \sqrt{E/F_y} < h/t_w \le 1.10 \sqrt{k_v E/F_y} \implies C_v = 1.0, \quad \phi_v = 0.90$
   - $1.10 \sqrt{k_v E/F_y} < h/t_w \le 1.37 \sqrt{k_v E/F_y} \implies C_v = \frac{1.10\sqrt{k_v E/F_y}}{h/t_w}, \quad \phi_v = 0.90$
   - $h/t_w > 1.37 \sqrt{k_v E/F_y} \implies C_v = \frac{1.51 k_v E}{(h/t_w)^2 F_y}, \quad \phi_v = 0.90$
3. **설계 전단강도**: $\phi_v V_n = \phi_v \cdot 0.6 F_y (H \cdot t_w) \cdot C_v$

### 3.5. 조합력 상호작용 검토(KDS 14 31 10 4.5)
1. **축력비 산정**: $\frac{P_u}{\phi_c P_n}$
2. **식 4.5-1 (고축력 분기: $\frac{P_u}{\phi_c P_n} \ge 0.2$)**:
   $$\text{DCR}_{pm} = \frac{P_u}{\phi_c P_n} + \frac{8}{9}\left(\frac{B_1 M_{ux}}{\phi_b M_{nx}} + \frac{B_1 M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$$
3. **식 4.5-2 (저축력 분기: $\frac{P_u}{\phi_c P_n} < 0.2$)**:
   $$\text{DCR}_{pm} = \frac{P_u}{2 \phi_c P_n} + \left(\frac{B_1 M_{ux}}{\phi_b M_{nx}} + \frac{B_1 M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$$

---

## 4. 강구조설계예제집 3자 삼각대조 벤치마크 검증 명세

`pytest tests/engine/test_steel_beam.py` 및 `test_steel_column.py`에서 아래의 공인 벤치마크 예제를 전수 검증합니다:

| 예제 번호 | 검토 항목 | 단면 규격 및 제원 | 하중 및 지지조건 | 예제집 정답 기준 | 허용 오차 |
|---|---|---|---|---|:---:|
| **예제 5.1** | 압축재 좌굴강도 | $H\text{-}300\times 300\times 10\times 15$<br>(SM355, $A=119.8\,\text{cm}^2$) | $L=4.0\,\text{m}, K_x=K_y=1.0$ | $KL/r = 53.27$<br>$F_e = 712.1\,\text{MPa}$<br>$F_{cr} = 288.1\,\text{MPa}$<br>$\phi_c P_n = 3,106\,\text{kN}$ | $\le 0.10\%$ |
| **예제 6.1** | 휨재 소성 및 LTB | $H\text{-}400\times 200\times 8\times 13$<br>(SM355, $Z_x=1286\,\text{cm}^3$) | 1. $L_b = 1.5\,\text{m} \le L_p$<br>2. $L_b = 3.5\,\text{m} (L_p < L_b < L_r)$<br>$C_b = 1.0$ | 1. $M_p = 456.5\,\text{kN}\cdot\text{m}$<br>$\phi_b M_n = 410.9\,\text{kN}\cdot\text{m}$<br>2. $\phi_b M_n = 352.4\,\text{kN}\cdot\text{m}$ | $\le 0.10\%$ |
| **예제 7.1** | 웨브 전단강도 | $H\text{-}400\times 200\times 8\times 13$<br>(SM355, $h/t_w=43.0$) | 비보강 웨브, $k_v = 5.34$ | $C_v = 1.00$<br>$\phi_v V_n = 681.6\,\text{kN}$ | $\le 0.10\%$ |
| **예제 8.1** | 보-기둥 P-M 조합력 | $H\text{-}350\times 350\times 12\times 19$<br>(SM355, $L=4.0\,\text{m}$) | $P_u = 1,800\,\text{kN}$<br>$M_{ux} = 150\,\text{kN}\cdot\text{m}$<br>$M_{uy} = 30\,\text{kN}\cdot\text{m}$ | $P_u/\phi_c P_n = 0.38 \ge 0.2$<br>식 4.5-1 적용<br>$\text{DCR}_{pm} = 0.742 \le 1.0$ (OK) | $\le 0.10\%$ |

---

## 5. TDD 구현 및 수용 기준 (Acceptance Criteria)

- [ ] `src/engine/steel/beam.py` 및 `column.py`의 dataclass 구조를 Pydantic v2 스키마와 100% 호환되도록 정비.
- [ ] `src/api/routes/steel.py`의 `/beam/design` 및 `/column/design` 엔드포인트에서 신규 스키마 연동 완료.
- [ ] 강구조설계예제집 5.1, 6.1, 7.1, 8.1 대비 수치 오차 $\le 0.10\%$ 달성.
- [ ] `pytest tests/engine/test_steel_beam.py` 및 `test_steel_column.py` 100% PASS (Exit Code 0).
- [ ] `docs/16`에 따른 4대 물리적 증거(원본 발췌, 3자 오차표, pytest 터미널 로그, git diff) 확보 및 커밋/푸시.
