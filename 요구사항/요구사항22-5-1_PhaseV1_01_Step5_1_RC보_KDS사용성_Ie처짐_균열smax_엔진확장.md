# 요구사항 22-5-1: Phase V1-01 Step 5-1 RC 보 KDS 사용성(처짐 Ie & 균열 s_max) 엔진 확장 및 0하중 대응 명세서

---

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 설계 엔진의 **(1) KDS 14 20 30 제4.2절에 따른 지점 조건 및 배근 유형 연동 Branson 유효단면2차모멘트($I_e$) 가중평균 수치 정식화**, **(2) KDS 14 20 30 제4.2.3절 휨철근 최대 간격 제한($s \le s_{\max}$) 검토 함수 신설**, **(3) 계수하중 0($T_u=0, M_u=0, V_u=0$) 입력 시 엔진 응답 플래그 및 Pydantic 입출력 스키마 확장**을 완수하기 위한 계산 엔진 전용 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 사용성 해석 엔진: Branson $I_e$ 가중평균, 균열방지 $s_{\max}$, 0하중 플래그, 입출력 모델)
  - `tests/engine/test_rc_beam_serviceability.py` (사용성 신규 전용 단위 테스트 스위트)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 30 비선형 사용성 수치해석 및 엄밀한 오차 $\le 0.10\%$ 검증
* **1순위/4순위 설계기준 SSOT**:
  - **KDS 14 20 30 : 2021** (콘크리트구조 사용성 설계기준)
    * 4.2.1 유효단면2차모멘트 $I_e$ 및 지점조건 가중평균 식 (4.2-1) ~ (4.2-3)
    * 4.2.2 시간의존계수 $\xi$ 및 장기처짐 배수 $\lambda_\Delta = \frac{\xi}{1 + 50\rho'}$ 식 (4.2-2)
    * 4.2.3 균열방지 휨철근 간격 제한 식 (4.2-4): $s \le s_{\max} = 375(k_{cr}/f_s) - 2.5c_c \le 300(k_{cr}/f_s)$
  - **콘크리트구조 학회기준 예제집 (2020)**:
    * 예제 3.1: 단순/연속보 처짐 및 Branson $I_e$ 가중평균 산정
    * 예제 3.2: 균열제어를 위한 철근 배근 간격 $s_{\max}$ 검토

---

## 2. 현행 기준 수치 알고리즘 상세 명세

### 2.1. 지점 조건 및 배근 유형 연동 Branson 유효단면2차모멘트($I_e$) 가중평균
1. **단면별 유효단면2차모멘트 ($I_e$) 산정 (KDS 14 20 30 4.2.1)**:
   $$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} \le I_g$$
   - 작용 모멘트 $M_a \le M_{cr}$ 인 경우: $I_e = I_g$
   - 균열단면2차모멘트 $I_{cr}$: 중립축 깊이 $k \cdot d$ 산정 후 콘크리트 압축대 및 철근 환산단면 모멘트 계산
2. **지점 조건별 대표 유효단면2차모멘트 $I_{e,avg}$ 가중평균 (KDS 14 20 30 4.2.1(4))**:
   - **단순 지지 (SIMPLE / 0)**:
     $$I_{e,avg} = I_{e,m} \quad (\text{중앙부 단면})$$
   - **양단 연속 (CONTINUOUS / BOTH_ENDS_CONTINUOUS / 1)**:
     $$I_{e,avg} = 0.50 I_{e,m} + 0.25(I_{e,1} + I_{e,2}) \quad (\text{또는 원본앱 옵션 } 0.70 I_{e,m} + 0.15(I_{e,1} + I_{e,2}))$$
   - **1단 연속 (ONE_END_CONTINUOUS / 2)**:
     $$I_{e,avg} = 0.85 I_{e,m} + 0.15 I_{e,cont}$$
   - **캔틸레버 (CANTILEVER / 3)**:
     $$I_{e,avg} = I_{e,fixed} \quad (\text{고정단 지지부 단면})$$
3. **배근 유형(`arrange_type`)과의 연동**:
   - `ONE_SECTION`: $I_{e,1} = I_{e,2} = I_{e,m}$ (전단면 동일 적용)
   - `SYMMETRIC_ENDS`: $I_{e,1} = I_{e,2} = I_{e,end}$ (단부 대칭 적용)
   - `THREE_STATIONS`: $I_{e,1} = I_{e,end\_i}$, $I_{e,m} = I_{e,mid}$, $I_{e,2} = I_{e,end\_j}$ 독립 적용
4. **장기처짐 배수 ($\lambda_\Delta$) 정밀 산출**:
   $$\lambda_\Delta = \frac{\xi}{1 + 50\rho'}$$
   - 지속하중 재하기간 계수 $\xi$: 5년 이상 2.0, 12개월 1.4, 6개월 1.2, 3개월 1.0 (기본값: 2.0)
   - 압축철근비 $\rho' = \frac{A_s'}{b \cdot d}$ (정모멘트 구간: 상부철근, 부모멘트 구간: 하부철근)

---

### 2.2. KDS 14 20 30 제4.2.3절 균열방지 휨철근 간격 제한 ($s \le s_{\max}$)
1. **규준 식 (4.2-4)**:
   $$s \le s_{\max} = 375 \left(\frac{k_{cr}}{f_s}\right) - 2.5 c_c \le 300 \left(\frac{k_{cr}}{f_s}\right)$$
   - 환경 조건 계수 $k_{cr}$:
     * 건조 환경 (Dry Environment): $k_{cr} = 280$
     * 기타 환경 (Other Environment / Wet): $k_{cr} = 210$
   - **철근 실 응력 $f_s$ 직접 산출 (탄성 균열 단면해석 기반)**:
     - 단순 약산($2/3 f_y$)에 의존하지 않고, 사용하중 휨모멘트 $M_s$ (또는 사용모멘트 $M_a$) 하에서의 실제 인장철근 응력을 직접 계산:
       $$kd = \frac{-B_{kd} + \sqrt{B_{kd}^2 - 4 A_{kd} C_{kd}}}{2 A_{kd}}, \quad jd = d - \frac{kd}{3}$$
       $$f_s = \frac{M_s \times 10^6}{A_s \cdot jd} \quad \left(\text{또는 } f_s = n \frac{M_s \times 10^6 \cdot (d - kd)}{I_{cr}}\right)$$
     - 응력 제한: $0 < f_s \le f_y$ (단, $M_s \le 0$이거나 미입력 시 약산식 $f_s = \frac{2}{3} f_y$를 폴백으로 연동)
   - 순피복두께 $c_c$:
     * 최외단 인장철근 표면에서 콘크리트 외측까지의 최단 피복두께 ($c_c = \text{cover} - d_b/2$ 또는 순피복값)

2. **3-Station 각 단면별 인장철근 분리 검토 (Station-by-Station Tension Check)**:
   - **단부-I (End-I)**:
     * 부모멘트 작용 $\rightarrow$ **상부 인장철근**($A_{s,\text{top}}$) 대상
     * 상부 유효깊이 $d_{\text{top}}$, 상부 피복 $c_{c,\text{top}}$, 상부 사용모멘트 $M_{s,I}$에 따른 $f_{s,I}$ 직접 산출
     * 상부 실제 철근간격 $s_{I,\text{top}}$ vs $s_{\max,I}$ 대조 및 $\text{DCR} = s_{I,\text{top}} / s_{\max,I}$
   - **중앙부-M (Center-M)**:
     * 정모멘트 작용 $\rightarrow$ **하부 인장철근**($A_{s,\text{bot}}$) 대상
     * 하부 유효깊이 $d_{\text{bot}}$, 하부 피복 $c_{c,\text{bot}}$, 중앙부 사용모멘트 $M_{s,M}$에 따른 $f_{s,M}$ 직접 산출
     * 하부 실제 철근간격 $s_{M,\text{bot}}$ vs $s_{\max,M}$ 대조 및 $\text{DCR} = s_{M,\text{bot}} / s_{\max,M}$
   - **단부-J (End-J)**:
     * 부모멘트 작용 $\rightarrow$ **상부 인장철근**($A_{s,\text{top}}$) 대상
     * 상부 유효깊이 $d_{\text{top}}$, 상부 피복 $c_{c,\text{top}}$, 상부 사용모멘트 $M_{s,J}$에 따른 $f_{s,J}$ 직접 산출
     * 상부 실제 철근간격 $s_{J,\text{top}}$ vs $s_{\max,J}$ 대조 및 $\text{DCR} = s_{J,\text{top}} / s_{\max,J}$
   - **배근 유형 연동**:
     * `ONE_SECTION`: 중앙부-M 대표 검토
     * `SYMMETRIC_ENDS`: 단부-I(상부인장) & 중앙부-M(하부인장) 2개 단면 검토
     * `THREE_STATIONS`: End-I, Center-M, End-J 3개 위치 독립 전수 검토

---

### 2.3. 계수하중 0($T_u=0, M_u=0, V_u=0$) 대응 및 입출력 모델 확장
1. **0하중 플래그 지원**:
   - `is_zero_torsion`: $T_u \le 0.0$ 또는 $T_u \le \phi T_{th}$
   - `is_zero_flexure`: $M_u \le 0.0$
   - `is_zero_shear`: $V_u \le 0.0$
2. **Pydantic 모델 스키마 확장 (`src/engine/rc/beam.py`)**:
   ```python
   class StationCrackSpacingCheck(BaseModel):
       station: str             # "end_i", "center_m", "end_j"
       rebar_pos: str           # "TOP" (단부 부모멘트) 또는 "BOTTOM" (중앙부 정모멘트)
       s_actual: float          # 실제 중심 또는 순간격 (mm)
       s_max: float             # 규준 최대 허용간격 (mm)
       cc: float                # 순피복두께 (mm)
       k_cr: float              # 환경계수 (280 또는 210)
       fs: float                # 직접 산출된 철근 사용응력 (MPa)
       dcr: float               # s_actual / s_max
       is_ok: bool              # 만족 여부

   class DeflectionResult(BaseModel):
       # 기존 필드 유지
       Ie_avg: float            # 신규: 지점조건 가중평균 유효단면2차모멘트 (mm^4)
       Ie_mid: float            # 중앙부 Ie
       Ie_end_i: float          # 단부 I Ie
       Ie_end_j: float          # 단부 J Ie
       support_condition: str   # SIMPLE, CONTINUOUS, ONE_END_CONTINUOUS, CANTILEVER
       lambda_delta: float      # 장기처짐 계수
       # 3-Station 각 단면별 인장철근 균열방지 간격 검토 결과
       crack_spacing_checks: Dict[str, StationCrackSpacingCheck] = Field(default_factory=dict)
   ```

---

## 3. 단위 테스트 계획 (`tests/engine/test_rc_beam_serviceability.py`)

1. **테스트 1: 콘크리트학회 예제집 3.1 벤치마크 (처짐 $I_e$ 가중평균)**
   - 단순보 및 양단연속보 조건에 대해 $M_a > M_{cr}$ 시 $I_e$ 및 $I_{e,avg}$ 오차 $\le 0.10\%$ 검증.
2. **테스트 2: 콘크리트학회 예제집 3.2 벤치마크 (균열 간격 $s_{\max}$)**
   - 건조환경($k_{cr}=280$) 및 기타환경($k_{cr}=210$)에 따른 $s_{\max}$ 산출 및 DCR 검증.
3. **테스트 3: 0하중 플래그 및 모델 반환 무결성 검증**
   - $T_u=0, M_u=0$ 입력 시 오류 없이 플래그 정상 반환 및 360+ 기존 회귀 테스트 무결성 확인.

---

## 4. 완료 검증 기준 (Definition of Done)

- [ ] KDS 14 20 30 제4.2절 지점조건 4종 및 배근유형 3종에 대한 Branson $I_e$ 가중평균 함수가 `beam.py`에 구현될 것.
- [ ] KDS 14 20 30 제4.2.3절 균열방지 철근간격 제한($s \le s_{\max}$) 검토 시, 단순 약산($2/3 f_y$)을 배제하고 탄성 균열해석을 통해 $f_s$를 단면별로 직접 산출할 것.
- [ ] 3-Station(End-I, Center-M, End-J) 각각의 인장철근(단부: 상부인장, 중앙부: 하부인장)에 대해 $s_{\max}$ 및 DCR을 분리 검토하여 `StationCrackSpacingCheck` 딕셔너리로 반환할 것.
- [ ] 0하중($T_u=0, M_u=0, V_u=0$) 대응 응답 플래그가 정상 추가될 것.
- [ ] 신규 `tests/engine/test_rc_beam_serviceability.py` 테스트가 100% PASS하고, 기존 회귀 테스트가 무결하게 통과할 것 (오차 $\le 0.10\%$).
