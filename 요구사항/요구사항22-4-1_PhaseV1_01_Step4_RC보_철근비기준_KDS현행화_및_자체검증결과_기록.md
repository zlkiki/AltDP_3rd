# 요구사항 22-4-1: Phase V1-01 Step 4 RC 보 철근비 KDS 현행화, 3-Station 개별 계산근거 출력, 원본앱 1:1 배근유형 옵션 구현 및 redcr 잔재 청산 명세서

## 1. 개요 및 배경

본 문서는 **RC 보 (`rc_beam`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 공학 구조계산서)** 구현 완료 후 발견된 후속 보완 과제인 **(1) 구버전 철근비 기준 완전 배제 및 현행 KDS 14 20 20: 2022 단일 규격화**, **(2) 철근 강도별($f_y$) 최소 허용 순인장변형률 $\epsilon_{t,\min}$ 정밀 산정**, **(3) 단부 I, 중앙 M, 단부 J 3개 위치별 정/부모멘트 분리 및 개별 KaTeX 계산근거 출력**, **(4) 원본앱 1:1 대조 배근 유형(1개 단면/2개 단면/3개 단면 설계) 옵션 지원**, **(5) 타 프로젝트 고유명사(`redcr`) 전면 청산 및 표준 네이밍 대체**, 그리고 **(6) 자체 검증 결과 기록**을 위한 통합 정밀 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 계산 엔진: 최소철근량 $\phi M_n \ge 1.2 M_{cr}$, 강도별 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$, 3-Station 정/부모멘트 분리 해석, `BeamArrangeType` 지원)
  - `src/web/static/js/components/form_rc_beam.js` (입력폼: Tab 2 배근 탭 상단에 원본앱 1:1 배근 유형-1/2/3 라디오 옵션 추가 및 동기화)
  - `src/web/static/js/report/rc_beam_report.js` (신규 표준 파일명: 구 `redcr_rc_beam.js`에서 리네이밍 및 3-Station 개별 KaTeX 계산근거 출력 전면 개편)
  - `src/web/static/js/report/report_common_renderer.js` (신규 표준 파일명: 구 `redcr_common_renderer.js`에서 리네이밍)
  - `src/web/static/js/core/report_engine.js` (A4 계산서 통합 디스패처: `rc_beam_report.js` 및 표준 함수 연동)
  - `src/web/templates/index.html` (프론트엔드 엔트리포인트: `<script>` 태그 표준화)
  - `tests/ui/test_phase22_4_rc_beam_report.py` (자체 검증 테스트 스위트: 표준 명칭 및 3-Station KaTeX 수식 검증)
  - `tests/engine/test_rc_beam.py` (엔진 단위 테스트: $f_y$ 강도별 변형률, $M_{cr}$, 3-Station 위치별 정/부모멘트 휨강도 검증)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 20: 2022 기준 공식 수치 해석, 3-Station 역학 분리 및 KaTeX LaTeX 조립
* **1순위/4순위 설계기준 SSOT**:
  - **KDS 14 20 20 : 2022** (콘크리트구조 휨 및 압축 설계기준)
    * 4.2.2 휨부재의 최소 철근량: $\phi M_n \ge 1.2 M_{cr}$ (단, $A_s \ge \frac{4}{3} A_{s,req}$ 만족 시 적용 예외)
    * 4.1.2 휨부재의 최대 철근량 및 연성 한계: 최외단 인장철근 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$ (철근 강도별 분기) 및 중립축 깊이비 한계 $c/d_t \le (c/d_t)_{\lim}$
  - **원본앱 리소스 Ground Truth**:
    * `original_src/Midas Design+/Language/Korean/DLG_DPLUS_RCS.ini` (`IDD_RCS_BEAM_PMODE_DLG`)

---

## 2. 현행 기준(KDS 14 20 20 : 2022) 대조 및 3-Station 정밀 계산근거 명세

### 2.1. 최소 철근량 검토 KDS 현행화 (구버전 철근비 완전 배제)

#### (1) 설계 원칙: 구버전 철근비 $\rho_{\min}$ 폐기 및 현행 KDS 단일화
* **구버전 철근비 ($\rho_{\min} = \max(0.25\sqrt{f_{ck}}/f_y, 1.4/f_y)$) 완전 제거**:
  - 구버전 콘크리트구조설계기준(KCI 2012 이전)의 단철근 근사식인 $\rho_{\min}$은 현행 기준에서 휨부재 최소 철근량 판정식으로 사용되지 않습니다.
  - **구버전 철근비 수치나 참고 병기는 일체 유지하지 않고 완전히 배제**하며, 현행 KDS 14 20 20 단일 기준으로 일원화합니다.
* **현행 KDS 14 20 20 : 2022 4.2.2 기준 규정**:
  - 인장철근이 요구되는 휨부재의 모든 단면에서 설계휨강도 $\phi M_n$은 균열모멘트 $M_{cr}$의 **1.2배 이상**이어야 합니다.
  $$\phi M_n \ge 1.2 M_{cr}$$
  - **균열모멘트 $M_{cr}$ 산정**:
    $$M_{cr} = \frac{f_r I_g}{y_t}, \quad f_r = 0.63 \lambda \sqrt{f_{ck}}$$
    (보통골재 콘크리트 $\lambda = 1.0$, 비균열 전단면 2차 모멘트 $I_g = \frac{b h^3}{12}$, 중립축까지 거리 $y_t = \frac{h}{2}$)
  - **예외 규정**: 단면의 모든 위치에서 해석에 의해 필요한 소요 철근량보다 1/3 이상 인장철근이 더 배치되는 경우($A_s \ge \frac{4}{3} A_{s,req}$), 위 $1.2 M_{cr}$ 조건을 적용하지 않고 만족(O.K)으로 판정합니다.

#### (2) 계산서(KaTeX) 3단계 전개 규격 (구버전 병기 없음)
```latex
% 1. 기준식
\phi M_n \ge 1.2 M_{cr} \quad \left(\text{단, } A_s \ge \frac{4}{3} A_{s,req} \text{ 만족 시 적용 예외}\right)

% 2. 수치 대입식
f_r = 0.63 \times 1.0 \times \sqrt{27.0} = 3.27\text{ MPa}, \quad I_g = \frac{400 \times 600^3}{12} = 7.20 \times 10^9\text{ mm}^4
M_{cr} = \frac{f_r I_g}{y_t} = \frac{3.27 \times 7.20\times 10^9}{300} \times 10^{-6} = 78.5\text{ kN}\cdot\text{m}
1.2 M_{cr} = 1.2 \times 78.5 = \mathbf{94.2\text{ kN}\cdot\text{m}}

% 3. 판정식
\phi M_n (347.2\text{ kN}\cdot\text{m}) \ge 1.2 M_{cr} (94.2\text{ kN}\cdot\text{m}) \quad \longrightarrow \quad [\mathbf{최소철근량 만족 O.K}]
```

---

### 2.2. 최대 철근량 및 연성 한계 검토 KDS 현행화 (철근 강도별 정밀 분기)

#### (1) 설계 원칙: 구버전 $\rho_{\max}$ 완전 폐기 및 최외단 순인장변형률 $\epsilon_t$ 기준화
* **구버전 최대철근비 ($\rho_{\max} = 0.85\beta_1 \frac{f_{ck}}{f_y} \frac{\epsilon_{cu}}{\epsilon_{cu}+0.004}$) 완전 제거**:
  - 현행 KDS 기준 본문에서 $\rho_{\max}$ 수식은 공식 삭제되었으며, 복철근 보나 T형 보에서 왜곡을 유발하므로 **일체 유지/병기하지 않고 완전히 제거**합니다.
* **현행 KDS 14 20 20 : 2022 4.1.2(3) / 4.1.2.3 철근 강도별 최소 허용 순인장변형률 $\epsilon_{t,\min}$**:
  - 휨부재의 연성 파괴를 보장하기 위해 공칭강도 상태에서 최외단 인장철근의 순인장변형률 $\epsilon_t$는 철근의 기준항복강도 $f_y$에 따라 아래 한계 이상이어야 합니다:
    * **$f_y \le 400\text{ MPa}$ 인 경우**:
      $$\epsilon_{t,\min} = \mathbf{0.0040}$$
    * **$f_y > 400\text{ MPa}$ 인 경우**:
      $$\epsilon_{t,\min} = \mathbf{2.0 \, \epsilon_y} = 2.0 \times \frac{f_y}{E_s} \quad (E_s = 200,000\text{ MPa})$$
  - **철근 강도 규격별 $\epsilon_{t,\min}$ 정량값 표**:
    | 철근 강도 규격 | 항복강도 $f_y$ | 항복변형률 $\epsilon_y = f_y / E_s$ | 최소 허용 순인장변형률 $\epsilon_{t,\min}$ | 한계 중립축 깊이비 $(c/d_t)_{\lim}$ ($f_{ck} \le 40\text{ MPa}$) |
    |:---:|:---:|:---:|:---:|:---:|
    | **SD400** | $400\text{ MPa}$ | $0.00200$ | **$0.0040$** | **$0.452$** |
    | **SD500** | $500\text{ MPa}$ | $0.00250$ | **$0.0050$** ($2.0 \epsilon_y$) | **$0.398$** |
    | **SD600** | $600\text{ MPa}$ | $0.00300$ | **$0.0060$** ($2.0 \epsilon_y$) | **$0.355$** |

* **중립축 깊이비 한계 ($(c/d_t)_{\lim}$)**:
  - 변형률 적합조건에 따른 중립축 깊이비 한계:
    $$\frac{c}{d_t} \le \left(\frac{c}{d_t}\right)_{\lim} = \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_{t,\min}}$$
  - 콘크리트 극한압축변형률 $\epsilon_{cu}$:
    * $f_{ck} \le 40\text{ MPa}$: $\epsilon_{cu} = 0.0033$
    * $f_{ck} > 40\text{ MPa}$: $\epsilon_{cu} = \max\left(0.0028, 0.0033 - 0.0001 \times \frac{f_{ck} - 40}{10}\right)$
* **인장지배단면 한계와의 연계 (KDS 14 20 20 4.1.2(1))**:
  - **최소 허용변형률 한계 ($\epsilon_t \ge \epsilon_{t,\min}$)**: 휨부재 연성 파괴 보장을 위한 필수 최소 한계 (미달 시 취성 파괴 우려로 **NG** 판정).
  - **인장지배단면 한계 ($\epsilon_t \ge \epsilon_{t,\text{tension}}$)**: 강도감소계수 $\phi = 0.85$ 적용 기준.
    * $f_y \le 400\text{ MPa}$: $\epsilon_{t,\text{tension}} = 0.0050$
    * $f_y > 400\text{ MPa}$: $\epsilon_{t,\text{tension}} = 2.5 \, \epsilon_y$ (SD500: $0.00625$, SD600: $0.00750$)
    * $\epsilon_{t,\min} \le \epsilon_t < \epsilon_{t,\text{tension}}$ 구간은 변화구간단면으로 $\phi$ 계수가 $0.65 \sim 0.85$로 보간 적용됨.

#### (2) 계산서(KaTeX) 3단계 전개 규격 (구버전 병기 없음)
```latex
% 1. 기준식
\epsilon_t \ge \epsilon_{t,\min} = \begin{cases} 0.0040 & (f_y \le 400\text{ MPa}) \\ 2.0\,\epsilon_y & (f_y > 400\text{ MPa}) \end{cases} \quad \left(\text{또는 } \frac{c}{d_t} \le \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_{t,\min}}\right)

% 2. 수치 대입식 (SD400: fy = 400 MPa, fck = 27 MPa 시)
\epsilon_{t,\min} = 0.0040, \quad \left(\frac{c}{d_t}\right)_{\lim} = \frac{0.0033}{0.0033 + 0.0040} = 0.452
c = \frac{a}{\beta_1} = \frac{60.2}{0.80} = 75.3\text{ mm}, \quad \frac{c}{d_t} = \frac{75.3}{535.0} = 0.141 \le 0.452
\epsilon_t = \epsilon_{cu} \left(\frac{d_t - c}{c}\right) = 0.0033 \left(\frac{535.0 - 75.3}{75.3}\right) = \mathbf{0.0201}

% 3. 판정식
\epsilon_t (0.0201) \ge \epsilon_{t,\min} (0.0040) \quad \left(\frac{c}{d_t} = 0.141 \le 0.452\right) \quad \longrightarrow \quad [\mathbf{연성파괴 유도 O.K}]
```

---

### 2.3. 3-Station 위치별(I/M/J) 휨/전단 역학 분리 및 개별 계산근거 출력 규격

#### (1) 문제점 및 현황 분석
* **기존 계산서의 한계**:
  - 기존 `redcr_rc_beam.js`는 제 2장에 End-I, Center-M, End-J 3개 위치의 부재력을 표로 보여주면서도, **제 3장(휨모멘트 강도 검토)과 제 4장(전단 검토)에서는 중앙부 1개 단면(Center-M)의 KaTeX 수식만 단일 출력**하여 단부(End-I, End-J)의 부모멘트 검토 계산근거가 누락되어 있었습니다.
* **RC 보의 위치별 역학 거동 차이**:
  1. **단부 I (End-I)**:
     - 지배 하중: **부모멘트 ($M_u^-$)** (지점 상부 인장) 및 **최대 전단력 ($V_u$)**
     - 인장철근: **상부 철근 ($A_s = A_{s,\text{top}}$)** / 압축철근: **하부 철근 ($A_s' = A_{s,\text{bot}}$)**
     - T형 보 플랜지 거동: 상부 인장 시 슬래브 콘크리트에 균열이 발생하므로 플랜지 압축효과가 배제되어 **복부 폭 $b_w$ 직사각형 보로 거동**함.
  2. **중앙부 (Center-M)**:
     - 지배 하중: **정모멘트 ($M_u^+$)** (경간 하부 인장) 및 **사용성 처짐/균열**
     - 인장철근: **하부 철근 ($A_s = A_{s,\text{bot}}$)** / 압축철근: **상부 철근 ($A_s' = A_{s,\text{top}}$)**
     - T형 보 플랜지 거동: 상부 플랜지가 압축을 받으므로 **유효폭 $b_e$를 갖는 T형 보로 거동**함 ($a \le h_f$ 시 직사각형 거동, $a > h_f$ 시 T형 보 휨강도 공식 적용).
  3. **단부 J (End-J)**:
     - 지배 하중: **부모멘트 ($M_u^-$)** (지점 상부 인장) 및 **최대 전단력 ($V_u$)**
     - 인장철근: **상부 철근 ($A_s = A_{s,\text{top}}$)** / 압축철근: **하부 철근 ($A_s' = A_{s,\text{bot}}$)**
     - 거동 특성: End-I와 대칭 또는 독립 하중/배근 조건 검토.

#### (2) 계산서(A4 리포트) 3-Station 개별 계산근거 출력 구조
계산서 **제 3장**과 **제 4장**을 아래와 같이 3-Station 위치별로 완전히 개별 전개합니다:

```
[제 3장. 휨모멘트 강도 검토 (Flexural Strength Check)]
  │
  ├─ 3.1 3-Station 위치별 휨설계 강도 총괄 요약표
  │     (End-I 부모멘트, Center-M 정모멘트, End-J 부모멘트 대비 Mu, phi_Mn, DCR, 판정)
  │
  ├─ 3.2 단부-I (End-I) 부모멘트 (Mu-) 검토 [상부 인장 배근]
  │     - Step 1: 등가 응력블록 a 및 중립축 c 산정 (상부 As_top = 2026.8 mm2 인장)
  │     - Step 2: 최외단 순인장변형률 et 및 강도감소계수 phi 산정 (KDS 14 20 20)
  │     - Step 3: 공칭휨강도 Mn 및 설계휨강도 phi_Mn 산정
  │     - Step 4: 소요 휨강도 대비 안전성 판정 (Mu- / phi_Mn <= 1.0)
  │
  ├─ 3.3 중앙부 (Center-M) 정모멘트 (Mu+) 검토 [하부 인장 배근 / T형 유효폭]
  │     - Step 1: 플랜지 압축 T형 거동 검토 및 응력블록 a, c 산정 (하부 As_bot 인장)
  │     - Step 2: 순인장변형률 et 및 강도감소계수 phi 산정
  │     - Step 3: 정모멘트 설계휨강도 phi_Mn 산정
  │     - Step 4: 소요 휨강도 대비 안전성 판정 (Mu+ / phi_Mn <= 1.0)
  │
  └─ 3.4 단부-J (End-J) 부모멘트 (Mu-) 검토 [상부 인장 배근]
        - (배근 유형-2 대칭 시: "단부-I과 대칭 동일 단면" 요약 표기)
        - (배근 유형-3 비대칭 시: End-I과 동일한 KaTeX 4단계 완전 전개 출력)
```

---

## 3. 원본앱 1:1 대조 배근 유형(단면 설계 옵션) 명세

### 3.1. 원본앱 리소스 대조 (`DLG_DPLUS_RCS.ini`)
원본앱 `IDD_RCS_BEAM_PMODE_DLG`의 배근 유형 프레임(`IDC_GURBE_FRAME_ARRANGE`)에는 3종의 라디오 옵션이 존재합니다:
```ini
IDC_GURBE_FRAME_ARRANGE      = "배근 유형"
IDC_GURBE_RADIO_ARRANGETYPE1 = "배근 유형-1 ( 전단면 )"
IDC_GURBE_RADIO_ARRANGETYPE2 = "배근 유형-2 ( 양단부와 중앙부 )"
IDC_GURBE_RADIO_ARRANGETYPE3 = "배근 유형-3 ( 각단부와 중앙부 )"
```

### 3.2. 3대 배근 유형별 동작 및 연동 명세

| 배근 유형 | 명칭 및 설명 | 입력폼 UI (`form_rc_beam.js`) 동작 | 계산 엔진 및 계산서 (`rc_beam_report.js`) |
|:---|:---|:---|:---|
| **유형-1** (`ONE_SECTION`) | **전단면 (1개 단면 일괄 설계)** | • 1개 단면(중앙부/전단면) 배근 테이블만 활성화 입력.<br>• 입력 시 End-I, Center-M, End-J에 동일 배근 자동 일괄 복사. | • 전단면 단일 배근 기준으로 최대 부재력(최대 정/부모멘트, 최대 전단력) 검토.<br>• 계산서에 단일 기준 단면 KaTeX 계산근거 집중 전개. |
| **유형-2** (`SYMMETRIC_ENDS`) | **양단부와 중앙부 (2개 단면 대칭 설계)** | • 실무 표준 기본값(Default).<br>• End-I 입력 시 End-J에 동일 배근이 실시간 양방향 자동 동기화.<br>• End-J 셀은 읽기 전용(또는 '단부-I 연동' 뱃지 표시). | • 단부(End-I=J 대칭 부모멘트) + 중앙부(Center-M 정모멘트) 2대 대표 위치 KaTeX 계산근거 출력.<br>• 단부-J는 단부-I 대칭 요약 표기. |
| **유형-3** (`THREE_STATIONS`) | **각단부와 중앙부 (3개 단면 독립 설계)** | • End-I, Center-M, End-J 세 단면 배근 테이블의 모든 셀이 독립적으로 활성화.<br>• 각 단부의 비대칭 배근 및 독립 스터럽 간격 입력 지원. | • End-I (부모멘트), Center-M (정모멘트), End-J (부모멘트) 3개 위치 모두 개별 KaTeX 계산근거 100% 완전 전개 출력. |

### 3.3. 데이터 모델 스키마 확장 (`src/engine/rc/beam.py`)
```python
class BeamArrangeType(str, Enum):
    """RC Beam Reinforcement Detailing Scope Option."""
    ONE_SECTION = "ONE_SECTION"          # 배근 유형-1: 전단면 (1개 단면)
    SYMMETRIC_ENDS = "SYMMETRIC_ENDS"    # 배근 유형-2: 양단부와 중앙부 (2개 단면 대칭)
    THREE_STATIONS = "THREE_STATIONS"    # 배근 유형-3: 각단부와 중앙부 (3개 단면 독립)

class RCBeamRebar(BaseModel):
    arrange_type: BeamArrangeType = BeamArrangeType.SYMMETRIC_ENDS
    end_i: SectionRebarGroup
    center_m: SectionRebarGroup
    end_j: SectionRebarGroup
    # ...
```

---

## 4. 타 프로젝트 고유명사(`redcr`) 전면 청산 및 표준 네이밍 대체 명세

### 4.1. 문제 배경 및 청산 원칙
* **배경**: `redcr`은 이전 타 프로젝트(RED-CR)의 레거시 고유명사이며, 본 프로젝트 `AltDP_3rd`의 표준 네이밍 규약에 어긋납니다.
* **원칙**: 이번 22-4-1 작업에서 `redcr` 관련 파일명, 클래스명, 전역 함수명, CSS 클래스명, HTML 태그 및 테스트 함수명을 일괄 청산하고 AltDP_3rd 표준 명칭으로 1:1 전면 대체합니다.

### 4.2. 1:1 대체 및 리네이밍 인벤토리 매핑

| 구분 | 레거시 타 프로젝트 명칭 (`redcr`) | AltDP_3rd 신규 표준 명칭 | 비고 |
|:---|:---|:---|:---|
| **A4 렌더러 파일** | `src/web/static/js/report/redcr_rc_beam.js` | `src/web/static/js/report/rc_beam_report.js` | 파일 리네이밍 및 3-Station KaTeX 개편 |
| **공통 렌더러 파일** | `src/web/static/js/report/redcr_common_renderer.js` | `src/web/static/js/report/report_common_renderer.js` | 파일 리네이밍 |
| **렌더러 클래스명** | `class RedcrRcBeamReport` | `class RCBeamReportGenerator` | 표준 리포트 제너레이터 클래스명 |
| **전역 등록 함수** | `window.renderRedcrRCBeamReport` | `window.renderRCBeamReport` | 표준 전역 함수 |
| **CSS 컨테이너 클래스** | `.redcr-report`, `.redcr-report-container` | `.altdp-report`, `.altdp-report-container` | `report.css` 및 렌더러 동기화 |
| **HTML 스크립트 로드** | `<script src="/static/js/report/redcr_rc_beam.js">` | `<script src="/static/js/report/rc_beam_report.js">` | `index.html` 태그 변경 |
| **디스패처 호출부** | `report_engine.js` 내 `redcr_rc_beam` 분기 | `report_engine.js` 내 `rc_beam_report` 분기 | 동적/정적 로더 표준화 |
| **단위 테스트 스위트** | `test_redcr_rc_beam_js_serving` 등 4개 함수 | `test_rc_beam_report_js_serving` 등 표준화 | `tests/ui/test_phase22_4_rc_beam_report.py` |

*(참고: `src/web/static/js/report/redcr/` 하위 모듈 폴더는 향후 부재별 순차 마이그레이션 시 자체 모듈로 단계적 흡수/폐기)*

---

## 5. 요구사항 22-4 자체 TEST 통과 현황 공식 기록

* **전용 테스트 파일**: `tests/ui/test_phase22_4_rc_beam_report.py`
* **테스트 실행 명령**: `pytest tests/ui/test_phase22_4_rc_beam_report.py`
* **실측 결과**: **`7 passed in 1.36s (100% 통과)`**
* **전체 회귀 테스트**: **`pytest` 349 passed (100% 무결점 통과)**

### 7대 세부 단위 테스트 검증 내역 (표준화 반영)
1. `test_rc_beam_report_js_serving`: `rc_beam_report.js` 서빙 및 5대 장구분, 8단계 핵심 KaTeX 수식 검증 (`PASS`)
2. `test_index_html_contains_rc_beam_report`: `index.html` 표준 스크립트 로드 태그 검증 (`PASS`)
3. `test_report_engine_delegates_to_rc_beam_report`: `report_engine.js` 디스패처 분기 연동 검증 (`PASS`)
4. `test_rc_beam_report_formula_substitution_steps`: 기준식 $\rightarrow$ 대입식 $\rightarrow$ 결과값 3단계 완전 전개 검증 (`PASS`)
5. `test_report_excel_button_disabled`: Excel 버튼 disabled 및 안내 툴팁 검증 (`PASS`)
6. `test_report_table_layout_and_column_widths`: fixed table layout 및 colgroup 열너비 균형 검증 (`PASS`)
7. `test_report_zoom_fit_width_on_init`: 초기 로드 시 74% 폭맞춤(fitToWidth) 기본보기 검증 (`PASS`)

---

## 6. 작업 분할 및 구현 지침 (Execution Steps)

1. **Step 1: 계산 엔진 보강 (`src/engine/rc/beam.py`)**:
   - `BeamArrangeType` Enum (`ONE_SECTION`, `SYMMETRIC_ENDS`, `THREE_STATIONS`) 추가.
   - 구버전 `rho_min`, `rho_max` 관련 산정 및 의존 로직 완전 배제.
   - 철근 강도별 최소 순인장변형률 산정식 구현:
     $$\epsilon_{t,\min} = 0.0040 \quad (f_y \le 400), \quad \epsilon_{t,\min} = 2.0 \times \frac{f_y}{E_s} \quad (f_y > 400)$$
   - 한계 중립축 깊이비 $(c/d_t)_{\lim} = \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_{t,\min}}$ 산정 로직 구현.
   - 균열모멘트 $M_{cr} = \frac{f_r I_g}{y_t}$ 및 $\phi M_n \ge 1.2 M_{cr}$ (단, $A_s \ge \frac{4}{3} A_{s,req}$ 적용 예외) 판정 로직 구현.
   - `FlexureResult` Pydantic 스키마에 `Mcr`, `phi_Mn_min`, `epsilon_t_min`, `c_dt_limit`, `is_min_flexure_ok`, `is_ductility_ok` 필드 반영.
   - 3-Station 정/부모멘트 및 전단/비틀림 해석 결과 데이터 구조 정비.

2. **Step 2: 배근 유형 옵션 폼 반영 (`src/web/static/js/components/form_rc_beam.js`)**:
   - Tab 2 배근 탭 상단에 원본앱 `IDC_GURBE_FRAME_ARRANGE` 1:1 라디오 버튼 그룹 배치:
     * `배근 유형-1 (전단면)`: 단일 단면 일괄 적용
     * `배근 유형-2 (양단부와 중앙부)`: End-I / Center-M 중심, End-J 자동 동기화 (기본값)
     * `배근 유형-3 (각단부와 중앙부)`: 3개 위치 독립 배근 테이블 활성화
   - 라디오 선택에 따라 배근 테이블 셀 활성화/비활성화 및 동기화 이벤트 핸들링.

3. **Step 3: `redcr` 파일 리네이밍 및 타 프로젝트 명칭 완전 청산**:
   - `src/web/static/js/report/redcr_rc_beam.js` $\rightarrow$ `src/web/static/js/report/rc_beam_report.js` 리네이밍.
   - `src/web/static/js/report/redcr_common_renderer.js` $\rightarrow$ `src/web/static/js/report/report_common_renderer.js` 리네이밍.
   - 클래스명 `RCBeamReportGenerator`, 전역 함수 `window.renderRCBeamReport`, CSS 클래스 `altdp-report` 전면 교체.
   - `src/web/templates/index.html` 및 `src/web/static/js/core/report_engine.js` 내 참조 식별자 및 파일 경로 1:1 동기화.

4. **Step 4: A4 계산서 3-Station 개별 KaTeX 계산근거 렌더링 (`src/web/static/js/report/rc_beam_report.js`)**:
   - 제 1장: 구버전 철근비 수식 완전 삭제 및 $\phi M_n \ge 1.2 M_{cr}$, $\epsilon_t \ge \epsilon_{t,\min}$ KDS 현행화 3단계 전개.
   - 제 3장 휨모멘트 강도 검토:
     * 3-Station 종합 휨강도 요약표 렌더링.
     * **단부-I (End-I)**: 부모멘트($M_u^-$) 상부 인장 휨강도 KaTeX 4단계 완전 전개.
     * **중앙부 (Center-M)**: 정모멘트($M_u^+$) 하부 인장/T형 플랜지 압축 휨강도 KaTeX 4단계 완전 전개.
     * **단부-J (End-J)**: 부모멘트($M_u^-$) 상부 인장 휨강도 개별 KaTeX 수식 전개 (유형-2 시 대칭 요약, 유형-3 시 독립 전개).
   - 제 4장 전단/비틀림 강도 검토: 3-Station 전단 요약표 및 지배 단부 KaTeX 3단계 전개.

5. **Step 5: 테스트 스위트 확장 및 전체 회귀 검증**:
   - `tests/engine/test_rc_beam.py`에 $f_y = 400, 500, 600\text{ MPa}$ 강도별 $\epsilon_{t,\min}$, $\phi M_n \ge 1.2 M_{cr}$ 및 3-Station 정/부모멘트 검증 단위 테스트 추가.
   - `tests/ui/test_phase22_4_rc_beam_report.py`에 `rc_beam_report.js` 표준 서빙, 3-Station KaTeX 수식 전개 검증 추가.
   - `pytest` 100% 무결점 통과 확인.

---

## 7. 검증 및 수용 기준 (DoD)

- [ ] `src/engine/rc/beam.py`에서 $\phi M_n \ge 1.2 M_{cr}$ (또는 $A_s \ge \frac{4}{3} A_{s,req}$) 판정이 정상 수행될 것.
- [ ] `src/engine/rc/beam.py`에서 철근 강도별($f_y \le 400$ 시 $0.004$, $f_y > 400$ 시 $2.0 \epsilon_y$) $\epsilon_{t,\min}$ 판정 및 한계 중립축 깊이비가 정확히 산정될 것.
- [ ] 구버전 철근비 $\rho_{\min}, \rho_{\max}$ 산출 및 병기가 계산서와 엔진에서 완전히 배제될 것.
- [ ] 원본앱 `IDD_RCS_BEAM_PMODE_DLG` 1:1 대조 배근 유형(유형-1 전단면, 유형-2 양단부/중앙부, 유형-3 각단부/중앙부) 라디오 옵션이 정상 동작할 것.
- [ ] A4 계산서 제 3장에서 단부 I(부모멘트), 중앙부 M(정모멘트), 단부 J(부모멘트)의 계산근거가 각각 개별적으로 명확히 분리 출력될 것.
- [ ] 타 프로젝트 명칭인 `redcr`이 파일명(`rc_beam_report.js`, `report_common_renderer.js`), 클래스명, 전역 함수명, HTML 태그, 테스트 함수명에서 완전히 청산 및 대체될 것.
- [ ] `tests/ui/test_phase22_4_rc_beam_report.py` 및 `tests/engine/test_rc_beam.py` 단위 테스트가 100% 통과할 것.
- [ ] `pytest` 전체 349+ 회귀 테스트가 에러 0건으로 100% 무결점 통과할 것.
