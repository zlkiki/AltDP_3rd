# 요구사항 21-1: Phase V1-1 Step 1 RC 보 KDS 계산 엔진 & Pydantic 스키마 명세서

## 1. 개요 및 SSOT 계층 매핑

본 문서는 **RC 보 (`rc_beam`)**의 **Step 1 (KDS 계산 엔진 & Pydantic 스키마)** 구현을 위한 상세 요구사항 명세서입니다.
KDS 14 20 국가건설기준에 기반하여 단철근, 복철근, T형 플랜지 휨강도, 전단강도, 비틀림강도, 그리고 Branson 유효단면2차모멘트 기반 처짐 및 직접 균열폭 사용성 검토를 순수 파이썬으로 구현합니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**: `src/engine/rc/beam.py`, `tests/engine/test_rc_beam.py`
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - 엄밀 수치해석, 비선형 평형 수렴, 0.10% 오차 무결성 입증
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/rc/` (`rc__CHK_BBBE_*.c`, `CHK_BBBE_beam.c`, `DPLUS_RCS.dll`, `symbols/DPLUS_RCS.dll_symbols.txt`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 RC Beam 장 (단/복철근 휨해석, 전단/비틀림 설계, 사용성 처짐/균열 계산식)
  3. `[3순위 학회 예제집]`: 한국콘크리트학회(2020) 콘크리트구조설계기준 예제집
     - `예제 3.1`: 단철근 직사각형 보의 휨모멘트 강도 ($\phi M_n$) 산정
     - `예제 3.2`: 복철근 직사각형 보의 압축철근 항복 여부 및 휨모멘트 강도
     - `예제 3.5`: T형 보의 플랜지 유효폭 및 휨모멘트 강도
     - `예제 4.1`: 수직 스터럽을 갖는 보의 전단강도 ($\phi V_n$) 및 철근 배근 간격
     - `예제 4.3`: 비틀림 모멘트 작용 시 전단-비틀림 상호작용 및 종방향 철근($A_l$) 산정
     - `예제 6.1`: Branson 유효단면2차모멘트($I_e$) 및 단기/장기 복합 처짐 계산
  4. `[4순위 국가건설기준]`: KDS 14 20 10 (일반/재료), KDS 14 20 20 (휨/압축), KDS 14 20 22 (전단/비틀림), KDS 14 20 30 (사용성)

---

## 2. Pydantic v2 데이터 입출력 스키마 상세 정의

`src/engine/rc/beam.py`에 아래의 엄밀한 공학 데이터 구조를 구현합니다:

### 2.1. 단면 및 재료 스키마 (`RCBeamSection`)
```python
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class BeamShape(str, Enum):
    RECTANGULAR = "RECTANGULAR"  # 직사각형 보
    TEE = "TEE"                  # T형 보

class SupportCondition(str, Enum):
    SIMPLE = "SIMPLE"            # 단순 지지 (xi = 2.0)
    CONTINUOUS_ONE = "CONT_ONE"  # 일단 연속
    CONTINUOUS_BOTH = "CONT_BOTH"# 양단 연속
    CANTILEVER = "CANTILEVER"    # 캔틸레버

class RCBeamSection(BaseModel):
    shape: BeamShape = BeamShape.RECTANGULAR
    b: float = Field(..., gt=0, description="보 복부 폭 bw (mm)")
    h: float = Field(..., gt=0, description="보 전체 높이 (mm)")
    length: float = Field(..., gt=0, description="보 유효 경간 L (mm)")
    cover: float = Field(40.0, gt=0, description="인장측 외곽 순피복 두께 (mm)")
    cover_top: float = Field(40.0, gt=0, description="압축측 외곽 순피복 두께 (mm)")
    
    # T형 보 전용 파라미터 (shape == TEE 일 때 유효)
    bf: Optional[float] = Field(None, gt=0, description="플랜지 유효폭 be (mm)")
    hf: Optional[float] = Field(None, gt=0, description="슬래브/플랜지 두께 (mm)")
    
    # 재료 물성치
    fck: float = Field(..., gt=0, description="콘크리트 설계기준압축강도 (MPa)")
    fy: float = Field(..., gt=0, description="주철근 설계기준항복강도 (MPa)")
    fyt: float = Field(..., gt=0, description="스터럽/비틀림철근 설계기준항복강도 (MPa)")
    support: SupportCondition = SupportCondition.SIMPLE
```

### 2.2. 철근 배근 스키마 (`RCBeamRebar`)
```python
class RebarRow(BaseModel):
    bar_dia: str = Field(..., description="철근 호칭경 (예: 'D22', 'D25')")
    count: int = Field(..., gt=0, description="해당 단의 철근 개수")
    layer: int = Field(1, ge=1, le=3, description="배근 단수 (1단, 2단, 3단)")

class SectionRebarGroup(BaseModel):
    top_bars: List[RebarRow] = Field(default_factory=list, description="상부 철근 목록")
    bot_bars: List[RebarRow] = Field(default_factory=list, description="하부 철근 목록")
    stirrup_bar: str = Field("D10", description="스터럽 철근 규격")
    stirrup_spacing: float = Field(200.0, gt=0, description="스터럽 배근 간격 s (mm)")
    stirrup_legs: int = Field(2, ge=2, description="스터럽 수직 다리수 (n legs)")

class RCBeamRebar(BaseModel):
    end_i: SectionRebarGroup = Field(..., description="End-I 단부 배근")
    center_m: SectionRebarGroup = Field(..., description="Center-M 중앙부 배근")
    end_j: SectionRebarGroup = Field(..., description="End-J 단부 배근")
    torsion_side_bar: Optional[str] = Field("D13", description="비틀림 종방향 측면 철근 규격")
    torsion_side_count: int = Field(0, ge=0, description="측면 비틀림 철근 단면당 총 개수")
```

### 2.3. 설계 부재력 스키마 (`RCBeamLoads`)
```python
class RCBeamPositionLoads(BaseModel):
    Mu_pos: float = Field(0.0, description="정모멘트 설계계수하중 (kN·m)")
    Mu_neg: float = Field(0.0, description="부모멘트 설계계수하중 (kN·m)")
    Vu: float = Field(0.0, description="설계 계수전단력 (kN)")
    Tu: float = Field(0.0, description="설계 계수비틀림모멘트 (kN·m)")
    Ma_pos: float = Field(0.0, description="정모멘트 사용하중 모멘트 (kN·m, 처짐용)")
    Ma_neg: float = Field(0.0, description="부모멘트 사용하중 모멘트 (kN·m, 처짐용)")
    Msus: float = Field(0.0, description="지속하중에 의한 사용모멘트 (kN·m, 장기처짐용)")

class RCBeamLoads(BaseModel):
    end_i: RCBeamPositionLoads
    center_m: RCBeamPositionLoads
    end_j: RCBeamPositionLoads
    deflection_limit_ratio: float = Field(240.0, gt=0, description="처짐 허용비 L / N (기본 240)")
```

### 2.4. 해석 및 검토 결과 스키마 (`RCBeamResult`)
```python
class FlexureResult(BaseModel):
    Mu: float
    phi_Mn: float
    d: float
    c: float
    a: float
    epsilon_t: float
    phi: float
    is_compression_yielding: bool
    As_req: float
    As_prov: float
    rho: float
    rho_min: float
    rho_max: float
    dcr: float
    status: str  # "OK" | "NG"

class ShearResult(BaseModel):
    Vu: float
    Vc: float
    Vs: float
    Vn: float
    phi_Vn: float
    phi: float = 0.75
    s_max: float
    Av_min: float
    Av_prov: float
    dcr: float
    status: str

class TorsionResult(BaseModel):
    Tu: float
    Tth: float
    Tcr: float
    Tn: float
    phi_Tn: float
    phi: float = 0.75
    cross_section_check: str  # 콘크리트 압축파괴 방지 판정
    Al_req: float
    Al_prov: float
    dcr: float
    status: str

class ServiceabilityResult(BaseModel):
    Mcr: float
    I_g: float
    I_cr: float
    I_e: float
    delta_immediate: float  # 즉시처짐 (mm)
    lambda_delta: float     # 장기처짐 계수
    delta_long_term: float  # 장기처짐 (mm)
    delta_total: float      # 총 처짐 (mm)
    delta_allow: float      # 허용 처짐 (mm)
    crack_width: float      # 직접 계산 균열폭 (mm)
    crack_allow: float      # 허용 균열폭 (mm)
    dcr_defl: float
    dcr_crack: float
    status: str

class RCBeamSectionResult(BaseModel):
    pos_flexure: FlexureResult
    neg_flexure: FlexureResult
    shear: ShearResult
    torsion: TorsionResult

class RCBeamResult(BaseModel):
    end_i: RCBeamSectionResult
    center_m: RCBeamSectionResult
    end_j: RCBeamSectionResult
    serviceability: ServiceabilityResult
    max_dcr: float
    governing_mode: str
    status: str  # "OK" | "NG"
```

---

## 3. KDS 14 20 핵심 공학 알고리즘 및 엄밀 수치해석 정식화

### 3.1. 휨모멘트 강도 및 중립축 평형 수렴 해석 (KDS 14 20 20)
1. **등가직사각형 압축응력블록 파라미터 ($\alpha_1, \beta_1$)**:
   $$\alpha_1 = 0.85 \quad (f_{ck} \le 40\text{ MPa})$$
   $$\alpha_1 = 0.85 - 0.0015 (f_{ck} - 40) \ge 0.75 \quad (f_{ck} > 40\text{ MPa})$$
   $$\beta_1 = 0.80 \quad (f_{ck} \le 28\text{ MPa})$$
   $$\beta_1 = 0.80 - 0.007 (f_{ck} - 28) \ge 0.65 \quad (f_{ck} > 28\text{ MPa})$$

2. **복철근 평형방정식 수치 해석**:
   - 중립축 깊이 $c$에 대해 압축력과 인장력의 평형 수렴:
     $$C_c = \alpha_1 f_{ck} \beta_1 c b$$
     $$\epsilon_s' = 0.0033 \left(\frac{c - d'}{c}\right), \quad f_s' = \min(E_s \epsilon_s', f_y)$$
     $$C_s = A_s' (f_s' - \alpha_1 f_{ck})$$
     $$T = A_s f_y \quad (\epsilon_t \ge \epsilon_y \text{ 가정})$$
     $$C_c + C_s = T \implies c \text{ 역산 (단순 직사각형 보의 경우 닫힌 해 도출 가능)}$$

3. **강도감소계수 $\phi$ (KDS 14 20 10 4.3)**:
   $$\epsilon_t = 0.0033 \left(\frac{d - c}{c}\right)$$
   $$\phi = \begin{cases} 
   0.85 & (\epsilon_t \ge 0.005) \quad [\text{인장지배}] \\
   0.65 + 0.20 \frac{\epsilon_t - \epsilon_y}{0.005 - \epsilon_y} & (\epsilon_y < \epsilon_t < 0.005) \quad [\text{전이구간}] \\
   0.65 & (\epsilon_t \le \epsilon_y) \quad [\text{압축지배}]
   \end{cases}$$

4. **공칭 및 설계 휨모멘트**:
   $$M_n = C_c \left(d - \frac{\beta_1 c}{2}\right) + C_s (d - d')$$
   $$\phi M_n = \phi \times M_n \ge M_u$$

5. **T형 보 판정 (KDS 14 20 20 4.1.3)**:
   - 압축 플랜지 두께 $h_f$: $a \le h_f$이면 직사각형 보($b = b_e$)로 해석.
   - $a > h_f$이면 플랜지 돌출부 압축력 $C_{cf} = 0.85 f_{ck} (b_e - b_w) h_f$와 복부 압축력 $C_{cw} = 0.85 f_{ck} b_w a$를 분리하여 엄밀 복합 해석.

---

### 3.2. 전단 및 비틀림 해석 알고리즘 (KDS 14 20 22)

1. **콘크리트 부담 전단강도 $V_c$**:
   $$V_c = \frac{1}{6} \lambda \sqrt{f_{ck}} b_w d$$

2. **전단철근(스터럽) 부담 전단강도 $V_s$**:
   $$V_s = \frac{A_v f_{yt} d}{s}$$
   $$V_s \le \frac{2}{3} \sqrt{f_{ck}} b_w d \quad (\text{단면 치수 제한})$$
   $$\phi V_n = 0.75 (V_c + V_s) \ge V_u$$

3. **비틀림 검토 및 임계/균열 비틀림모멘트**:
   $$T_{th} = 0.0625 \lambda \sqrt{f_{ck}} \left(\frac{A_{cp}^2}{p_{cp}}\right)$$
   $$T_{cr} = 0.25 \lambda \sqrt{f_{ck}} \left(\frac{A_{cp}^2}{p_{cp}}\right)$$
   - $T_u \le \phi T_{th}$이면 비틀림 무시 가능.
   - $T_u > \phi T_{th}$이면 폐합 스터럽 및 종방향 철근 $A_l$ 산정:
     $$A_l = \frac{A_t}{s} p_h \left(\frac{f_{yt}}{f_y}\right) \cot^2 \theta \quad (\theta = 45^\circ)$$

---

### 3.3. 사용성 한계상태 검토 알고리즘 (KDS 14 20 30)

1. **Branson 유효단면2차모멘트 $I_e$**:
   $$f_r = 0.63 \lambda \sqrt{f_{ck}}$$
   $$M_{cr} = \frac{f_r I_g}{y_t}$$
   $$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} \le I_g$$

2. **단기 및 장기 처짐 산정**:
   - 지지조건별 계수 $\alpha$: 단순지지($\frac{5}{48}$), 양단연속 등 경간별 산정.
   - 탄성계수: $E_c = 8,500 \sqrt[3]{f_{cu}}\text{ MPa}$.
   - 즉시처짐: $\Delta_i = \alpha \frac{M_a L^2}{E_c I_e}$.
   - 장기처짐 계수: $\lambda_\Delta = \frac{\xi}{1 + 50 \rho'}$ ($\xi = 2.0$, 5년 이상).
   - 총 처짐: $\Delta_{total} = \Delta_i + \lambda_\Delta \Delta_{sus} \le \Delta_{allow} = \frac{L}{240}$.

3. **직접 균열폭 검토 (KDS 14 20 30 4.2)**:
   $$w = 1.08 \beta \epsilon_s \sqrt[3]{d_c A} \times 10^{-3} \le w_{lim} = 0.3\text{ mm (건조환경)}$$

---

## 4. TDD 단위 테스트 명세서 (`tests/engine/test_rc_beam.py`)

아래 4대 핵심 벤치마크 테스트 케이스를 구현하고 **오차 $\le 0.10\%$**를 입증합니다:

```python
import pytest
from src.engine.rc.beam import (
    RCBeamSection, RCBeamRebar, RCBeamLoads, RCBeamResult,
    calculate_rc_beam_design
)

def test_rc_beam_singly_flexure_benchmark():
    """콘크리트학회 예제집 예제 3.1 단철근 보 휨강도 검증"""
    # b = 300, h = 500, d = 435, fck = 24, fy = 400, 3-D25 (As = 1520.1 mm²)
    # 예제집 정답: a = 99.4 mm, c = 116.9 mm, phi = 0.85, phi_Mn = 217.4 kN·m
    # ...
    # assert abs(result.phi_Mn - 217.4) / 217.4 <= 0.0010 (0.10% 오차 엄수)

def test_rc_beam_doubly_flexure_benchmark():
    """콘크리트학회 예제집 예제 3.2 복철근 보 압축철근 항복 및 휨강도 검증"""
    # b = 350, d = 530, d' = 65, As = 3040 mm², As' = 1013 mm²
    # 예제집 정답: fs' = 400 MPa (항복), a = 113.7 mm, phi_Mn = 512.6 kN·m
    # assert abs(result.phi_Mn - 512.6) / 512.6 <= 0.0010

def test_rc_beam_shear_benchmark():
    """콘크리트학회 예제집 예제 4.1 전단강도 Vc, Vs 검증"""
    # bw = 300, d = 450, fck = 24, fyt = 400, D10 @ 150 (Av = 142.6 mm²)
    # Vc = 110.2 kN, Vs = 171.1 kN, phi_Vn = 211.0 kN
    # assert abs(result.phi_Vn - 211.0) / 211.0 <= 0.0010

def test_rc_beam_deflection_branson_benchmark():
    """콘크리트학회 예제집 예제 6.1 Branson Ie 및 장기처짐 검증"""
    # L = 6000, Ig = 3.125e9, Mcr = 32.1 kN·m, Ma = 65.0 kN·m
    # Ie 계산 오차 <= 0.10% 검증
```

---

## 5. 검증 및 수용 기준 (DoD)

- [ ] `src/engine/rc/beam.py`에 단/복철근, T형 플랜지, 전단, 비틀림, Branson 처짐, 직접 균열폭 전 알고리즘 구현 완료.
- [ ] Pydantic v2 모델 스키마가 완벽히 정의되고 유효성 검사 작동.
- [ ] `pytest tests/engine/test_rc_beam.py` 실행 시 100% PASS (Exit Code 0).
- [ ] 학회 예제집 공식 벤치마크 4종 대비 수치 계산 오차 **$\le 0.10\%$** 입증.
- [ ] 더미 코드(Mock/Hardcoded) 일체 없음.
