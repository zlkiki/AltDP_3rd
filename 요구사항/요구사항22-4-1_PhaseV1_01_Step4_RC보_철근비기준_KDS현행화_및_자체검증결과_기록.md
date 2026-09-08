# 요구사항 22-4-1: Phase V1-01 Step 4 RC 보 철근비 기준 KDS 현행화 및 22-4 자체 검증 결과 기록 명세서

## 1. 개요 및 배경

본 문서는 **RC 보 (`rc_beam`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 공학 구조계산서)** 구현 완료 후 발견된 후속 보완 및 기준 정합성 강화를 위한 버그픽스/개선 상세 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 계산 엔진: 최소철근량 $\phi M_n \ge 1.2 M_{cr}$ 및 순인장변형률 $\epsilon_t \ge 0.004$ 정밀 검토식 추가)
  - `src/web/static/js/report/redcr_rc_beam.js` (A4 계산서 렌더러: 제 1장 철근비 및 연성 한계 검토 3단계 전개 현행화)
  - `tests/ui/test_phase22_4_rc_beam_report.py` (자체 검증 테스트 스위트 갱신)
  - `요구사항/요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md` (DoD 완료 및 자체 TEST 결과 동기화)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 20: 2022 기준 공식 수치 해석 및 KaTeX LaTeX 3단계 수식 조립
* **1순위/4순위 설계기준 SSOT**:
  - **KDS 14 20 20 : 2022** (콘크리트구조 휨 및 압축 설계기준)
    * 4.2.2 휨부재의 최소 철근량: $\phi M_n \ge 1.2 M_{cr}$ (단, $A_s \ge \frac{4}{3} A_{s,req}$ 만족 시 적용 예외)
    * 4.1.2 휨부재의 최대 철근량 및 연성 한계: 최외단 인장철근 순인장변형률 $\epsilon_t \ge 0.004$ 및 중립축 깊이비 한계 $c/d \le \frac{\epsilon_{cu}}{\epsilon_{cu}+0.004} = 0.452$

---

## 2. 현행 기준(KDS 14 20 20 : 2022) 대조 및 정밀 변경 명세

### 2.1. 최소 철근량 검토 KDS 현행화

#### (1) 구버전 vs 현행 기준 비교
* **구버전 (기존 코드)**:
  $$\rho_{\min} = \max\left(\frac{0.25 \sqrt{f_{ck}}}{f_y}, \frac{1.4}{f_y}\right)$$
  - 이는 구 콘크리트구조설계기준(KCI 2012 이전) 및 구 KDS(2018 이전)의 ACI 318 계열 수식입니다.
* **현행 KDS 14 20 20 : 2022 기준**:
  - 해석에 의해 인장철근 배근이 요구되는 휨부재의 모든 단면에서 설계휨강도 $\phi M_n$은 균열모멘트 $M_{cr}$의 **1.2배 이상**이어야 합니다.
  $$\phi M_n \ge 1.2 M_{cr}$$
  - 균열모멘트 산정:
    $$M_{cr} = \frac{f_r I_g}{y_t}, \quad f_r = 0.63 \lambda \sqrt{f_{ck}}$$
  - 예외 규정: 단면의 모든 위치에서 해석에 의해 필요한 소요 철근량보다 1/3 이상 인장철근이 더 배치되는 경우($A_s \ge \frac{4}{3} A_{s,req}$)에는 이 최소철근량 규정을 적용하지 않을 수 있습니다.

#### (2) 계산서(KaTeX) 3단계 전개 규격
```latex
% 1. 기준식
\phi M_n \ge 1.2 M_{cr} \quad \left(\text{또는 } A_s \ge \frac{4}{3} A_{s,req}\right)

% 2. 수치 대입식
M_{cr} = \frac{f_r I_g}{y_t} = \frac{0.63 \times 1.0 \times \sqrt{27.0} \times 7.20\times 10^9}{300} \times 10^{-6} = 78.5\text{ kN}\cdot\text{m}
1.2 M_{cr} = 1.2 \times 78.5 = 94.2\text{ kN}\cdot\text{m}

% 3. 판정식 (구기준 rho_min 참고 병기)
\phi M_n (347.2\text{ kN}\cdot\text{m}) \ge 1.2 M_{cr} (94.2\text{ kN}\cdot\text{m}) \quad [\mathbf{O.K}]
\left(\text{참고: } \rho = 0.0095 \ge \rho_{\min} = 0.0035 \quad [\mathbf{O.K}]\right)
```

---

### 2.2. 최대 철근량 및 연성 파괴 한계 검토 KDS 현행화

#### (1) 구버전 vs 현행 기준 비교
* **구버전 (기존 코드)**:
  $$\rho_{\max} = 0.85 \beta_1 \frac{f_{ck}}{f_y} \left(\frac{\epsilon_{cu}}{\epsilon_{cu} + 0.004}\right)$$
  - 이는 과거 KCI 2007 해설서 등에서 단철근 직사각형 보에 한해 $\epsilon_t = 0.004$를 철근비로 환산했던 근사식이며, 현행 기준 본문에서는 "최대 철근비 $\rho_{max}$" 수식이 완전 삭제되었습니다.
  - 복철근 보나 T형 보의 경우 압축철근($A_s'$)이나 플랜지 압축효과가 반영되지 않아 오차가 발생합니다.
* **현행 KDS 14 20 20 : 2022 기준**:
  - 휨부재의 취성 파괴를 방지하고 충분한 연성을 확보하기 위하여 **최외단 인장철근의 순인장변형률 $\epsilon_t$**로 직접 규정합니다.
  $$\epsilon_t \ge 0.004 \quad (\text{인장지배단면 한계: } \epsilon_t \ge 0.005)$$
  - 중립축 깊이비 한계 ($f_{ck} \le 40\text{ MPa}$ 시 $\epsilon_{cu} = 0.0033$):
  $$\frac{c}{d} \le \frac{\epsilon_{cu}}{\epsilon_{cu} + 0.004} = \frac{0.0033}{0.0033 + 0.004} = 0.452$$

#### (2) 계산서(KaTeX) 3단계 전개 규격
```latex
% 1. 기준식
\epsilon_t \ge 0.004 \quad \left(\text{또는 } \frac{c}{d} \le \frac{\epsilon_{cu}}{\epsilon_{cu} + 0.004} = 0.452\right)

% 2. 수치 대입식
c = \frac{a}{\beta_1} = \frac{60.2}{0.80} = 75.3\text{ mm}, \quad \frac{c}{d} = \frac{75.3}{535.0} = 0.141 \le 0.452
\epsilon_t = \epsilon_{cu} \left(\frac{d - c}{c}\right) = 0.0033 \left(\frac{535.0 - 75.3}{75.3}\right) = \mathbf{0.0201}

% 3. 판정식 (단철근 환산 rho_max 참고 병기)
\epsilon_t (0.0201) \ge 0.004 \quad \longrightarrow \quad [\mathbf{연성파괴 유도 O.K}]
\left(\text{참고: } \rho = 0.0095 \le \rho_{\max} = 0.0206 \quad [\mathbf{O.K}]\right)
```

---

## 3. 요구사항 22-4 자체 TEST 통과 현황 공식 기록

* **전용 테스트 파일**: `tests/ui/test_phase22_4_rc_beam_report.py`
* **테스트 실행 명령**: `pytest tests/ui/test_phase22_4_rc_beam_report.py`
* **실측 결과**: **`7 passed in 1.36s (100% 통과)`**
* **전체 회귀 테스트**: **`pytest` 349 passed (100% 무결점 통과)**

### 7대 세부 단위 테스트 검증 내역
1. `test_redcr_rc_beam_js_serving`: `redcr_rc_beam.js` 서빙 및 5대 장구분, 8단계 핵심 KaTeX 수식 검증 (`PASS`)
2. `test_index_html_contains_redcr_rc_beam`: `index.html` 스크립트 로드 태그 검증 (`PASS`)
3. `test_report_engine_delegates_to_redcr_rc_beam`: `report_engine.js` 디스패처 분기 연동 검증 (`PASS`)
4. `test_redcr_rc_beam_formula_substitution_steps`: 기준식 $\rightarrow$ 대입식 $\rightarrow$ 결과값 3단계 완전 전개 검증 (`PASS`)
5. `test_report_excel_button_disabled`: Excel 버튼 disabled 및 안내 툴팁 검증 (`PASS`)
6. `test_report_table_layout_and_column_widths`: fixed table layout 및 colgroup 열너비 균형 검증 (`PASS`)
7. `test_report_zoom_fit_width_on_init`: 초기 로드 시 74% 폭맞춤(fitToWidth) 기본보기 검증 (`PASS`)

---

## 4. 작업 분할 및 구현 지침 (Execution Steps)

1. **Step 1: 계산 엔진 보강 (`src/engine/rc/beam.py`)**:
   - `calculate_rc_beam_flexure`에 $M_{cr}$ 계산 및 $\phi M_n \ge 1.2 M_{cr}$ 검토 판정식 추가.
   - $A_s \ge \frac{4}{3} A_{s,req}$ 판정식 추가.
   - `FlexureResult` 데이터클래스에 `Mcr`, `phi_Mn_min`, `is_min_flexure_ok` 필드 추가.
2. **Step 2: A4 계산서 렌더러 현행화 (`src/web/static/js/report/redcr_rc_beam.js`)**:
   - 제 1장 단면 제원부의 철근비 상하한 박스를 **[철근량 상하한 및 연성 한계 검토 - KDS 14 20 20]**로 개편.
   - $\phi M_n \ge 1.2 M_{cr}$ (최소철근량) 및 $\epsilon_t \ge 0.004$ (최대철근/연성한계) 3단계 전개 적용.
   - 구 기준 $\rho_{\min}, \rho_{\max}$ 수치는 실무용 참고치로 병기.
3. **Step 3: 테스트 스위트 확장 및 검증**:
   - `tests/engine/test_rc_beam.py`에 $\phi M_n \ge 1.2 M_{cr}$ 검증 케이스 추가.
   - `tests/ui/test_phase22_4_rc_beam_report.py`에 신규 KDS 14 20 20 KaTeX 수식 전개 검증 추가.
   - `pytest` 100% 통과 확인.

---

## 5. 검증 및 수용 기준 (DoD)

- [ ] `src/engine/rc/beam.py`에서 $\phi M_n \ge 1.2 M_{cr}$ 및 $\epsilon_t \ge 0.004$ 판정 정상 수행.
- [ ] `redcr_rc_beam.js`에서 제 1장에 현행 KDS 기준 수식 $\phi M_n \ge 1.2 M_{cr}$ 및 $\epsilon_t \ge 0.004$ 3단계 완전 전개 렌더링.
- [ ] 구 기준 $\rho_{\min}, \rho_{\max}$ 수치가 실무 참고치로 적절히 병기 표시됨.
- [ ] `tests/ui/test_phase22_4_rc_beam_report.py` 및 `tests/engine/test_rc_beam.py` 100% 통과.
- [ ] `pytest` 전체 349+ 회귀 테스트 무결점 통과.
