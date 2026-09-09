# 요구사항 22-4-1: Phase V1-01 Step 4 RC 보 철근비 기준 KDS 현행화, 타 프로젝트(redcr) 잔재 청산 및 자체 검증 결과 기록 명세서

## 1. 개요 및 배경

본 문서는 **RC 보 (`rc_beam`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 공학 구조계산서)** 구현 완료 후 발견된 후속 보완 과제인 **(1) 구버전 철근비 기준 완전 배제 및 현행 KDS 14 20 20: 2022 단일 규격화**, **(2) 철근 강도별($f_y$) 최소 허용 순인장변형률 $\epsilon_{t,\min}$ 정밀 산정**, **(3) 타 프로젝트 고유명사(`redcr`) 전면 청산 및 표준 네이밍 대체**, 그리고 **(4) 자체 검증 결과 기록**을 위한 통합 정밀 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 계산 엔진: 최소철근량 $\phi M_n \ge 1.2 M_{cr}$ 및 강도별 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$ 정밀 검토식)
  - `src/web/static/js/report/rc_beam_report.js` (신규 표준 파일명: 구 `redcr_rc_beam.js`에서 리네이밍 및 KDS 현행화 3단계 KaTeX 전개 개편)
  - `src/web/static/js/report/report_common_renderer.js` (신규 표준 파일명: 구 `redcr_common_renderer.js`에서 리네이밍)
  - `src/web/static/js/core/report_engine.js` (A4 계산서 통합 디스패처: `rc_beam_report.js` 및 표준 함수 연동)
  - `src/web/templates/index.html` (프론트엔드 엔트리포인트: `<script>` 태그 표준화)
  - `tests/ui/test_phase22_4_rc_beam_report.py` (자체 검증 테스트 스위트: 표준 명칭 및 KDS 신규 수식 갱신)
  - `tests/engine/test_rc_beam.py` (엔진 단위 테스트: $f_y$ 강도별 최소변형률 및 최소철근량 검증)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 20: 2022 기준 공식 수치 해석 및 KaTeX LaTeX 3단계 수식 조립
* **1순위/4순위 설계기준 SSOT**:
  - **KDS 14 20 20 : 2022** (콘크리트구조 휨 및 압축 설계기준)
    * 4.2.2 휨부재의 최소 철근량: $\phi M_n \ge 1.2 M_{cr}$ (단, $A_s \ge \frac{4}{3} A_{s,req}$ 만족 시 적용 예외)
    * 4.1.2 휨부재의 최대 철근량 및 연성 한계: 최외단 인장철근 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$ (철근 강도별 분기) 및 중립축 깊이비 한계 $c/d_t \le (c/d_t)_{\lim}$

---

## 2. 현행 기준(KDS 14 20 20 : 2022) 대조 및 정밀 설계 명세

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

## 3. 타 프로젝트 고유명사(`redcr`) 전면 청산 및 표준 네이밍 대체 명세

### 3.1. 문제 배경 및 청산 원칙
* **배경**: `redcr`은 이전 타 프로젝트(RED-CR)의 레거시 고유명사이며, 본 프로젝트 `AltDP_3rd`의 표준 네이밍 규약에 어긋납니다.
* **원칙**: 이번 22-4-1 작업에서 `redcr` 관련 파일명, 클래스명, 전역 함수명, CSS 클래스명, HTML 태그 및 테스트 함수명을 일괄 청산하고 AltDP_3rd 표준 명칭으로 1:1 전면 대체합니다.

### 3.2. 1:1 대체 및 리네이밍 인벤토리 매핑

| 구분 | 레거시 타 프로젝트 명칭 (`redcr`) | AltDP_3rd 신규 표준 명칭 | 비고 |
|:---|:---|:---|:---|
| **A4 렌더러 파일** | `src/web/static/js/report/redcr_rc_beam.js` | `src/web/static/js/report/rc_beam_report.js` | 파일 리네이밍 및 KDS 현행화 |
| **공통 렌더러 파일** | `src/web/static/js/report/redcr_common_renderer.js` | `src/web/static/js/report/report_common_renderer.js` | 파일 리네이밍 |
| **렌더러 클래스명** | `class RedcrRcBeamReport` | `class RCBeamReportGenerator` | 표준 리포트 제너레이터 클래스명 |
| **전역 등록 함수** | `window.renderRedcrRCBeamReport` | `window.renderRCBeamReport` | 표준 전역 함수 |
| **CSS 컨테이너 클래스** | `.redcr-report`, `.redcr-report-container` | `.altdp-report`, `.altdp-report-container` | `report.css` 및 렌더러 동기화 |
| **HTML 스크립트 로드** | `<script src="/static/js/report/redcr_rc_beam.js">` | `<script src="/static/js/report/rc_beam_report.js">` | `index.html` 태그 변경 |
| **디스패처 호출부** | `report_engine.js` 내 `redcr_rc_beam` 분기 | `report_engine.js` 내 `rc_beam_report` 분기 | 동적/정적 로더 표준화 |
| **단위 테스트 스위트** | `test_redcr_rc_beam_js_serving` 등 4개 함수 | `test_rc_beam_report_js_serving` 등 표준화 | `tests/ui/test_phase22_4_rc_beam_report.py` |

*(참고: `src/web/static/js/report/redcr/` 하위 모듈 폴더는 향후 부재별 순차 마이그레이션 시 자체 모듈로 단계적 흡수/폐기)*

---

## 4. 요구사항 22-4 자체 TEST 통과 현황 공식 기록

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

## 5. 작업 분할 및 구현 지침 (Execution Steps)

1. **Step 1: 계산 엔진 보강 (`src/engine/rc/beam.py`)**:
   - 구버전 `rho_min`, `rho_max` 관련 산정 및 의존 로직 완전 배제.
   - 철근 강도별 최소 순인장변형률 산정식 구현:
     $$\epsilon_{t,\min} = 0.0040 \quad (f_y \le 400), \quad \epsilon_{t,\min} = 2.0 \times \frac{f_y}{E_s} \quad (f_y > 400)$$
   - 한계 중립축 깊이비 $(c/d_t)_{\lim} = \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_{t,\min}}$ 산정 로직 구현.
   - 균열모멘트 $M_{cr} = \frac{f_r I_g}{y_t}$ 및 $\phi M_n \ge 1.2 M_{cr}$ (단, $A_s \ge \frac{4}{3} A_{s,req}$ 적용 예외) 판정 로직 구현.
   - `FlexureResult` Pydantic 스키마에 `Mcr`, `phi_Mn_min`, `epsilon_t_min`, `c_dt_limit`, `is_min_flexure_ok`, `is_ductility_ok` 필드 반영.
2. **Step 2: `redcr` 파일 리네이밍 및 타 프로젝트 명칭 완전 청산**:
   - `src/web/static/js/report/redcr_rc_beam.js` $\rightarrow$ `src/web/static/js/report/rc_beam_report.js` 리네이밍.
   - `src/web/static/js/report/redcr_common_renderer.js` $\rightarrow$ `src/web/static/js/report/report_common_renderer.js` 리네이밍.
   - 클래스명 `RCBeamReportGenerator`, 전역 함수 `window.renderRCBeamReport`, CSS 클래스 `altdp-report` 전면 교체.
   - `src/web/templates/index.html` 및 `src/web/static/js/core/report_engine.js` 내 참조 식별자 및 파일 경로 1:1 동기화.
3. **Step 3: A4 계산서 렌더러 KDS 현행화 (`src/web/static/js/report/rc_beam_report.js`)**:
   - 제 1장 단면 제원부의 철근비 상하한 박스를 **[철근량 상하한 및 연성 한계 검토 - KDS 14 20 20]**로 개편.
   - 구버전 철근비 $\rho_{\min}, \rho_{\max}$ 수식 및 참고 병기 완전 삭제.
   - $\phi M_n \ge 1.2 M_{cr}$ (최소철근량) 및 $\epsilon_t \ge \epsilon_{t,\min}$ (강도별 연성한계) 3단계 완전 전개 수식 렌더링.
4. **Step 4: 테스트 스위트 확장 및 전체 회귀 검증**:
   - `tests/engine/test_rc_beam.py`에 $f_y = 400, 500, 600\text{ MPa}$ 강도별 $\epsilon_{t,\min}$ 및 $\phi M_n \ge 1.2 M_{cr}$ 검증 단위 테스트 추가.
   - `tests/ui/test_phase22_4_rc_beam_report.py`의 `redcr` 명칭 전면 교체 및 신규 KDS 14 20 20 KaTeX 수식 전개 검증 추가.
   - `pytest` 100% 무결점 통과 확인.

---

## 6. 검증 및 수용 기준 (DoD)

- [ ] `src/engine/rc/beam.py`에서 $\phi M_n \ge 1.2 M_{cr}$ (또는 $A_s \ge \frac{4}{3} A_{s,req}$) 판정이 정상 수행될 것.
- [ ] `src/engine/rc/beam.py`에서 철근 강도별($f_y \le 400$ 시 $0.004$, $f_y > 400$ 시 $2.0 \epsilon_y$) $\epsilon_{t,\min}$ 판정 및 한계 중립축 깊이비가 정확히 산정될 것.
- [ ] 구버전 철근비 $\rho_{\min}, \rho_{\max}$ 산출 및 병기가 계산서와 엔진에서 완전히 배제될 것.
- [ ] 타 프로젝트 명칭인 `redcr`이 파일명(`rc_beam_report.js`, `report_common_renderer.js`), 클래스명, 전역 함수명, HTML 태그, 테스트 함수명에서 완전히 청산 및 대체될 것.
- [ ] A4 계산서 제 1장에 현행 KDS 기준 $\phi M_n \ge 1.2 M_{cr}$ 및 $\epsilon_t \ge \epsilon_{t,\min}$ 3단계 완전 전개 수식이 깔끔하게 렌더링될 것.
- [ ] `tests/ui/test_phase22_4_rc_beam_report.py` 및 `tests/engine/test_rc_beam.py` 단위 테스트가 100% 통과할 것.
- [ ] `pytest` 전체 349+ 회귀 테스트가 에러 0건으로 100% 무결점 통과할 것.
