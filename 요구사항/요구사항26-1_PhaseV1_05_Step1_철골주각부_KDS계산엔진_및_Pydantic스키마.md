# 요구사항 26-1: Phase V1-5 Step 1 철골 주각부 KDS 계산 엔진 & Pydantic 스키마 명세서

## 1. 개요 및 SSOT 계층 매핑

본 문서는 **철골 주각부 (`steel_baseplate`)**의 **Step 1 (KDS 계산 엔진 & Pydantic v2 스키마)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_baseplate` (카탈로그 No. 24, Tier 1 플래그십)
* **담당 소스 파일**:
  - 엔진 구현: [`src/engine/steel/baseplate.py`](../src/engine/steel/baseplate.py)
  - API 라우트: [`src/api/routes/steel.py`](../src/api/routes/steel.py)
  - 단위 테스트: [`tests/engine/test_steel_baseplate.py`](../tests/engine/test_steel_baseplate.py)
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` C루틴 (`steel__CHK_USBP_*.c`, `solver_baseplate_*`, `DPLUS_STEEL.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 Baseplate 편 (KDS 14 31 25 한계상태설계법, 콘크리트 지압 및 대·소편심 해석, AISC Design Guide 1 캔틸레버 휨 모델)
  3. `[3순위 학회 예제집]`: 한국강구조학회 『KDS 41 31 00 : 2019에 따른 강구조설계 예제집』
     - `제13장 예제 13.6.7`: 주각부 설계 - 축력이 지배하는 고정단 H형강 기둥 주각부 ($H\text{-}428\times 407\times 20\times 35$, SM355 강재, 콘크리트 $f_{ck}=24\text{ MPa}$, 플레이트 $700\times 700\times 55\text{ mm}$, 페데스탈 $800\times 800\text{ mm}$, 지압강도 $\phi_c P_p = 7,430\text{ kN}$, $m=147\text{ mm}, n=187\text{ mm}, \lambda n'=104\text{ mm}$, 지배암 $l=187\text{ mm}$, 소요두께 $t_{req}=53.1\text{ mm}$, 8-M24 앵커)
     - `제11장 예제 11.12`: 중심축하중을 받는 각형강관 기둥의 베이스플레이트 설계 ($300\times 300\times 12$ 각관, $450\times 450\times 24\text{ mm}$ 플레이트)
     - `제6장 예제 6.1, 6.2`: 대편심 모멘트 지배 주각부 (인장측 앵커볼트 인장력 $T_u$ 발생, 콘크리트 브레이크아웃 및 강재 파단 검토)
  4. `[4순위 국가건설기준]`:
     - `KDS 14 31 25`: 강구조 연결 및 접합설계기준 (4.5 주각부 설계)
     - `KDS 14 20 54`: 콘크리트용 앵커 설계기준 (선설치 및 후설치 앵커볼트 인장·전단 강도)
     - `AISC Design Guide 1`: Base Plate and Anchor Rod Design (2nd Edition)

---

## 2. Pydantic v2 데이터 입출력 스키마 상세 정의

`src/engine/steel/baseplate.py` 및 `src/api/routes/steel.py`에 적용될 엄밀한 공학 데이터 구조입니다:

### 2.1. 기둥 단면 및 앵커볼트 입력 스키마
```python
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class BaseplateColumnType(str, Enum):
    H_SHAPE = "H"           # H형강 기둥 (Rolled / Built-up)
    BOX_SHAPE = "BOX"       # 각형강관 기둥 (Rectangular Hollow Section)
    PIPE_SHAPE = "PIPE"     # 원형강관 기둥 (Circular Hollow Section)

class AnchorInstallType(str, Enum):
    CAST_IN_HEADED = "CAST_IN_HEADED"  # 선설치 헤드볼트 (kc = 12.5)
    POST_INSTALLED = "POST_INSTALLED"  # 후설치 앵커 (kc = 10.0)

class BaseplateAnchorInput(BaseModel):
    install_type: AnchorInstallType = AnchorInstallType.CAST_IN_HEADED
    bolt_grade: str = Field("SS400", description="앵커 강종 (SS400, SM355, 4.6, 8.8 등)")
    diameter: float = Field(24.0, gt=0, description="앵커볼트 공칭직경 da (mm)")
    num_anchors: int = Field(4, ge=2, description="총 앵커볼트 개수")
    num_tension_anchors: int = Field(2, ge=1, description="인장측 앵커볼트 개수")
    hef: float = Field(300.0, gt=0, description="유효 매립깊이 (mm)")
    edge_distance: float = Field(150.0, gt=0, description="콘크리트 연단거리 c_a1 (mm)")
    spacing: float = Field(150.0, gt=0, description="앵커볼트 간격 s_a (mm)")
    futa: float = Field(400.0, gt=0, description="앵커볼트 최소인장강도 (MPa)")
    fy_anchor: float = Field(240.0, gt=0, description="앵커볼트 항복강도 (MPa)")
```

### 2.2. 주각부 베이스플레이트 전체 입력 스키마 (`BasePlateInput`)
```python
class BasePlateInput(BaseModel):
    name: str = Field("1F-BP1", description="주각부 식별 부재명")
    
    # 기둥 정보
    col_type: BaseplateColumnType = BaseplateColumnType.H_SHAPE
    col_d: float = Field(400.0, gt=0, description="기둥 전체 높이 dc (mm)")
    col_bf: float = Field(400.0, gt=0, description="기둥 플랜지 폭 bfc (mm)")
    col_tf: float = Field(20.0, gt=0, description="기둥 플랜지 두께 tfc (mm)")
    col_tw: float = Field(13.0, gt=0, description="기둥 웨브 두께 twc (mm)")
    col_fy: float = Field(355.0, gt=0, description="기둥 강재 항복강도 (MPa)")
    
    # 베이스플레이트 정보
    B: float = Field(600.0, gt=0, description="플레이트 폭 (mm, 플랜지 직각 방향)")
    N: float = Field(600.0, gt=0, description="플레이트 길이 (mm, 플랜지 평행 방향)")
    tp: float = Field(35.0, gt=0, description="플레이트 두께 (mm)")
    plate_fy: float = Field(355.0, gt=0, description="플레이트 강재 항복강도 (MPa)")
    plate_fu: float = Field(490.0, gt=0, description="플레이트 강재 인장강도 (MPa)")
    
    # 콘크리트 기초 (페데스탈)
    fck: float = Field(27.0, gt=0, description="콘크리트 설계기준압축강도 (MPa)")
    pedestal_B: float = Field(800.0, gt=0, description="페데스탈 폭 B2 (mm)")
    pedestal_N: float = Field(800.0, gt=0, description="페데스탈 길이 N2 (mm)")
    grout_thickness: float = Field(30.0, ge=0, description="무수축 모르타르 그라우트 두께 (mm)")
    
    # 앵커볼트
    anchor: BaseplateAnchorInput = Field(default_factory=BaseplateAnchorInput)
    anchor_edge_dist_plate: float = Field(60.0, gt=0, description="플레이트 연단~앵커 중심 거리 (mm)")
    
    # 리브 스티프너 (선택 옵션)
    use_rib: bool = Field(False, description="리브 스티프너 사용 여부")
    rib_thickness: float = Field(12.0, ge=0, description="리브 두께 (mm)")
    rib_height: float = Field(150.0, ge=0, description="리브 높이 (mm)")
    
    # 설계 계수하중
    Pu: float = Field(600.0, description="계수 축압축력 (kN, 압축 +)")
    Mu: float = Field(150.0, description="계수 휨모멘트 (kN·m)")
    Vu: float = Field(80.0, ge=0, description="계수 전단력 (kN)")
```

### 2.3. 계산 결과 및 DCR 스키마 (`BasePlateResult`)
```python
class BasePlateResult(BaseModel):
    # 콘크리트 지압
    A1: float = Field(..., description="베이스플레이트 면적 (mm²)")
    A2: float = Field(..., description="페데스탈 유효면적 (mm²)")
    geo_factor: float = Field(..., description="콘크리트 지압 형상 증대계수 sqrt(A2/A1) <= 2.0")
    fp_max_allow: float = Field(..., description="콘크리트 허용 설계지압응력 (MPa)")
    phi_Pp: float = Field(..., description="콘크리트 설계지압강도 (kN)")
    fp_actual: float = Field(..., description="실제 최대 지압응력 (MPa)")
    dcr_bearing: float = Field(..., description="콘크리트 지압 DCR")
    
    # 편심 및 응력 분포
    eccentricity: float = Field(..., description="하중 편심거리 e = Mu/Pu (mm)")
    critical_e: float = Field(..., description="임계 편심거리 ecrit (mm)")
    eccentricity_case: str = Field(..., description="소편심 / 중편심 / 대편심 판정")
    Yc: float = Field(..., description="콘크리트 압축대 길이 (mm)")
    
    # 플레이트 휨 두께
    cantilever_m: float = Field(..., description="플랜지 평행 캔틸레버 길이 m (mm)")
    cantilever_n: float = Field(..., description="플랜지 직각 캔틸레버 길이 n (mm)")
    cantilever_n_prime: float = Field(..., description="웨브-플랜지 사이 캔틸레버 n' (mm)")
    cantilever_l: float = Field(..., description="지배 캔틸레버 길이 l (mm)")
    req_plate_tp: float = Field(..., description="소요 플레이트 두께 tp,req (mm)")
    dcr_plate: float = Field(..., description="플레이트 휨 DCR (tp,req / tp)^2")
    
    # 앵커볼트 한계상태
    Tu_anchor_total: float = Field(..., description="총 소요 앵커 인장력 (kN)")
    Tu_per_anchor: float = Field(..., description="개별 앵커 소요 인장력 (kN)")
    phi_Nsa: float = Field(..., description="앵커 강재 설계인장강도 (kN)")
    phi_Ncb: float = Field(..., description="콘크리트 브레이크아웃 설계강도 (kN)")
    phi_Nn: float = Field(..., description="앵커 지배 인장강도 min(phi_Nsa, phi_Ncb) (kN)")
    dcr_anchor_tension: float = Field(..., description="앵커 인장 DCR")
    
    # 전단 및 복합응력
    phi_Vsa: float = Field(..., description="앵커 강재 설계전단강도 (kN)")
    phi_Vcp: float = Field(..., description="콘크리트 프라이아웃 설계강도 (kN)")
    phi_Vn: float = Field(..., description="앵커 지배 전단강도 min(phi_Vsa, phi_Vcp) (kN)")
    dcr_anchor_shear: float = Field(..., description="앵커 전단 DCR")
    dcr_anchor_combined: float = Field(..., description="앵커 인장-전단 상호작용 DCR (Tu/phiN)^1.67 + (Vu/phiV)^1.67")
    
    # 종합
    governing_dcr: float = Field(..., description="최대 지배 DCR")
    is_safe: bool = Field(..., description="구조 안전성 종합 판정 (True/False)")
    messages: List[str] = Field(default_factory=list, description="설계 경고 및 안내 메시지")
```

---

## 3. KDS 14 31 25 / KDS 14 20 54 핵심 수식 및 알고리즘 정식화

### 3.1. 콘크리트 기초 지압강도 ($P_p$ 및 $\phi_c P_p$)
* **콘크리트 지압면적**:
  $$A_1 = B \times N, \quad A_2 = B_2 \times N_2$$
* **지압 증대계수**:
  $$\text{geo\_factor} = \min\left(2.0, \sqrt{\frac{A_2}{A_1}}\right) \ge 1.0$$
* **설계지압응력 및 강도**:
  $$f_{p,\max} = \phi_c \cdot (0.85 f_{ck}) \cdot \text{geo\_factor} \le \phi_c \cdot (1.7 f_{ck}) \quad (\phi_c = 0.65)$$
  $$\phi_c P_p = f_{p,\max} \cdot A_1$$

### 3.2. 하중 편심거리 및 3대 응력 분포 판정
하중 편심거리 $e = \frac{M_u}{P_u}$ (단, $P_u \le 0$인 순수인장의 경우 앵커 인장 모드로 직행):
1. **Case A [소편심: 전단면 압축] ($e \le \frac{N}{6}$)**:
   - 압축응력이 베이스플레이트 전단면에 걸쳐 사다리꼴 또는 삼각형으로 분포하며 앵커볼트에 인장력이 작용하지 않음.
   - 최대 지압응력: $f_p = \frac{P_u}{A_1}\left(1 + \frac{6e}{N}\right)$
   - $T_u = 0\text{ kN}$, $Y_c = N$
2. **Case B [중편심: 부분 압축] ($\frac{N}{6} < e \le e_{crit}$)**:
   - 임계 편심거리: $e_{crit} = \frac{N}{2} - \frac{P_u}{2 q_{\max}}$ (여기서 $q_{\max} = f_{p,\max} \cdot B$)
   - 지압 합력점과 기둥 중심 편심 평형을 만족하는 압축대 길이: $Y_c = 3\left(\frac{N}{2} - e\right)$
   - 최대 지압응력: $f_p = \frac{2 P_u}{3 B (N/2 - e)} \le f_{p,\max}$
   - $T_u = 0\text{ kN}$
3. **Case C [대편심: 앵커 인장 작용] ($e > e_{crit}$)**:
   - 모멘트가 커서 인장측 앵커볼트가 들리며 인장력 $T_u$가 발생함.
   - 압축단에서 인장측 앵커볼트 중심까지의 유효깊이: $d' = N - d_{edge}$
   - 지압응력 $f_p = f_{p,\max}$ 극한 상태 가정 하 힘과 모멘트의 정적 평형 2차 방정식:
     $$Y_c^2 - 2 d' Y_c + \frac{2 \left[ P_u (d' - N/2) + M_u \right]}{f_{p,\max} B} = 0$$
     $$Y_c = d' - \sqrt{d'^2 - \frac{2 \left[ P_u (d' - N/2) + M_u \right]}{f_{p,\max} B}}$$
   - 총 콘크리트 압축력: $C = f_{p,\max} \cdot B \cdot Y_c$ (또는 $0.5 \cdot f_{p,\max} \cdot B \cdot Y_c$)
   - 앵커 소요인장력: $T_u = C - P_u$

### 3.3. 캔틸레버 굽힘암 및 소요 플레이트 두께 ($t_{req}$)
* **H형강 기둥 캔틸레버 돌출길이 (AISC DG-1 / KDS 14 31 25)**:
  $$m = \frac{N - 0.95 d}{2}, \quad n = \frac{B - 0.80 b_f}{2}$$
* **각형강관(BOX) 기둥 캔틸레버 돌출길이**:
  $$m = \frac{N - 0.95 d}{2}, \quad n = \frac{B - 0.95 b}{2}$$
* **웨브와 플랜지 사이 내측 휨 캔틸레버 $n'$**:
  $$n' = \frac{1}{4}\sqrt{d \cdot b_f}$$
  $$X = \frac{4 d b_f}{(d + b_f)^2} \frac{P_u}{\phi_c P_p} \le 1.0, \quad \lambda = \frac{2\sqrt{X}}{1 + \sqrt{1 - X}} \le 1.0$$
* **지배 굽힘암 $l$**:
  $$l = \max(m, n, \lambda n')$$
* **소요 베이스플레이트 두께 $t_{req}$**:
  - 소편심/중편심 시: $t_{req} = l \sqrt{\frac{2 P_u}{0.90 F_y B N}}$ 또는 $t_{req} = l \sqrt{\frac{2 f_{p,actual}}{0.90 F_y}}$
  - 대편심 시: $t_{req} = l \sqrt{\frac{2 f_{p,\max}}{0.90 F_y}}$

### 3.4. 앵커볼트 강도 검토 (KDS 14 20 54)
* **강재 인장강도**: $\phi N_{sa} = 0.75 \cdot n_{ta} \cdot A_{se} \cdot f_{uta}$
* **콘크리트 브레이크아웃 강도**: $\phi N_{cb} = 0.70 \cdot \frac{A_{Nc}}{A_{Nc0}} \cdot \psi_{ed,N} \cdot N_b$
  ($N_b = k_c \sqrt{f_{ck}} h_{ef}^{1.5}$, 선설치 $k_c = 12.5$, 후설치 $k_c = 10.0$)
* **강재 전단강도**: $\phi V_{sa} = 0.65 \cdot 0.60 \cdot n_{total} \cdot A_{se} \cdot f_{uta}$
* **콘크리트 프라이아웃 강도**: $\phi V_{cp} = 0.70 \cdot k_{cp} \cdot N_{cb}$ ($h_{ef} \ge 65\text{ mm} \implies k_{cp} = 2.0$)
* **인장-전단 상호작용**: $\left(\frac{T_u}{\phi N_n}\right)^{1.67} + \left(\frac{V_u}{\phi V_n}\right)^{1.67} \le 1.0$

---

## 4. 강구조설계 예제집 3자 삼각 대조 검증 기준

| 검증 항목 | 강구조설계 예제집 13.6.7 정답치 | AltDP_3rd 허용 오차 한계 | 비고 |
|---|---|---|---|
| 기둥 단면 / 강종 | $H\text{-}428\times 407\times 20\times 35$ / SM355 | 일치 | $F_y = 335\text{ MPa}$ ($t > 40\text{mm}$) |
| 베이스플레이트 / 페데스탈 | $700\times 700\text{ mm}$ / $800\times 800\text{ mm}$ | 일치 | $f_{ck} = 24\text{ MPa}$ |
| 지압형상계수 $\sqrt{A_2/A_1}$ | $\sqrt{640,000 / 490,000} = 1.143$ | $\le 0.05\%$ | |
| 콘크리트 설계지압강도 $\phi_c P_p$ | $7,430\text{ kN}$ | $\le 0.10\%$ | $0.65 \times 0.85 \times 24 \times 490 \times 1.143$ |
| 캔틸레버 길이 $m$ | $147\text{ mm}$ | $\le 0.10\%$ | $(700 - 0.95 \times 428)/2$ |
| 캔틸레버 길이 $n$ | $187\text{ mm}$ | $\le 0.10\%$ | $(700 - 0.80 \times 407)/2$ |
| 캔틸레버 길이 $\lambda n'$ | $104\text{ mm}$ | $\le 0.10\%$ | $\lambda = 1.0$ |
| 지배 굽힘암 $l$ | $187\text{ mm}$ | $\le 0.10\%$ | $\max(147, 187, 104)$ |
| 소요 두께 $t_{req}$ | $53.1\text{ mm}$ | $\le 0.10\%$ | $187 \sqrt{\frac{2 \times 5,950 \times 10^3}{0.9 \times 335 \times 700 \times 700}}$ |
| 편심거리 $e$ | $8.29\text{ mm}$ | $\le 0.10\%$ | $49.3 \times 10^3 / 5,950 = 8.29\text{ mm}$ |
| 편심 판정 | 소편심 (인장력 없음, $T_u=0$) | 일치 | $e < 133\text{ mm}$ |
| 앵커볼트 배치 | 8-M24 ($A_{d,\min} = 3,200\text{ mm}^2$) | 일치 | $0.005 A_g$ 최소규정 |

---

## 5. Pytest TDD 단위 테스트 계획 (`tests/engine/test_steel_baseplate.py`)

1. `test_kds_example_13_6_7_concentric_baseplate()`:
   - 강구조설계 예제집 13.6.7 완벽 대조 ($H\text{-}428\times 407$, $700\times 700$, $P_u=5830, M_u=49.3$)
   - 지압강도 $\phi_c P_p = 7,430\text{ kN} \pm 0.10\%$, 소요두께 $t_{req} = 53.1\text{ mm} \pm 0.10\%$ 검증.
2. `test_rectangular_box_column_baseplate_example_11_12()`:
   - 각형강관 기둥 ($300\times 300\times 12$) 주각부 지압 및 휨 두께 $24\text{ mm}$ 검증.
3. `test_large_eccentricity_anchor_tension_breakout()`:
   - 대편심 모멘트 지배 상태 2차방정식 $Y_c$ 해법 및 앵커볼트 인장력 $T_u$, 콘파칭 강도 $\phi N_{cb}$ 검증.
4. `test_anchor_shear_and_pryout_interaction()`:
   - 전단력 $V_u$ 재하 시 앵커 전단 $\phi V_{sa}$, 프라이아웃 $\phi V_{cp}$ 및 $(T_u/\phi N)^{1.67} + (V_u/\phi V)^{1.67} \le 1.0$ 복합응력 검증.
5. `test_baseplate_pydantic_api_endpoint()`:
   - FastAPI `/api/steel/baseplate/check` 엔드포인트 요청 및 JSON 응답 무결성 검증.

---

## 6. 완료 정의 (DoD) 및 체크리스트

- [ ] **Pydantic v2 모델**: `BasePlateInput`, `BasePlateResult`, `BaseplateAnchorInput` 구현.
- [ ] **수치 계산 엔진**: 지압, 3가지 편심 분류, 캔틸레버 두께, 앵커 인장/전단 수식 100% 구현.
- [ ] **예제집 삼각대조**: 예제 13.6.7 오차 $\le 0.10\%$ 입증.
- [ ] **Pytest 100% 통과**: `pytest tests/engine/test_steel_baseplate.py` PASS.
- [ ] **API 라우트 연동**: `src/api/routes/steel.py`에 주각부 검토/설계 엔드포인트 등록.
