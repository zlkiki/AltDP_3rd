# 요구사항 22-7: Phase V1-01 Step 7 RC 보 최소 철근량(휨·전단·비틀림) 전수 검토, 전단력 0 강도생략 및 최소배근 의무검토 명세서

---

## 1. 개요 및 배경

본 문서는 **RC 보 (`rc_beam`)** 수직 관통 완료 후 실무 검토 과정에서 식별된 **(1) 최소 철근량 검토 누락(최소 휨철근, 최소 전단철근, 최소 비틀림철근) 전면 해결**, **(2) 계수전단력 0 ($V_u \le 0$)일 때 전단강도 상세 검토의 동적 생략 및 1줄 요약화**, 그리고 **(3) 하중이 0($M_u=0, V_u=0, T_u=0$)이 되어 강도 검토가 생략되더라도 구조 안전을 위한 최소 배근량 검토는 절대 생략 불가(Mandatory Minimum Reinforcement Check)** 원칙을 확립하기 위한 정밀 공학 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 계산 엔진: $A_{s,\min}$, $A_{v,\min}$, $(A_v + 2A_t)_{\min}$, $A_{l,\min}$ 산출 및 DCR 평가)
  - `src/web/static/js/report/rc_beam_report.js` (A4 순백색 계산서: 제 3장 휨최소철근 단면적 KaTeX, 제 5장 $V_u=0$ 강도생략 + 최소전단철근 KaTeX 상시출력, 최소비틀림철근 KaTeX 전개)
  - `src/web/static/js/components/form_rc_beam.js` (입력폼: 최소철근량 부족 시 직관적 실시간 경고 연동)
  - `tests/engine/test_rc_beam.py` (엔진 단위 테스트: 최소 배근량 검토 및 0하중 처리 무결성 검증)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 20 / 22 기준 공식 수치 해석, KaTeX 8단계 수식 유도, 0.10% 오차 무결성
* **연동 SSOT**:
  - **KDS 14 20 20 : 2022** (콘크리트구조 휨 및 압축 설계기준 제4.2.2절 휨부재의 최소 철근량)
  - **KDS 14 20 22 : 2022** (콘크리트구조 전단 및 비틀림 설계기준 제4.3.3절 최소 전단철근량, 제4.3.4절 최대 간격, 제4.5.4절 최소 비틀림철근량 및 간격)
  - **콘크리트학회 콘크리트구조기준 예제집(2020)** (제4장 휨부재 최소철근, 제6장 전단 최소철근, 제7장 비틀림 최소철근)
  - **원본앱 Ground Truth** (`original_src/Midas Design+/DgnLanguage/Korean/CVLDgnReportKR.ini`, `DgnEngine.ini`: 최소전단철근 보강, 요구 횡방향/종방향 비틀림 철근량 계산)
  - [`docs/10`](../docs/10_agent_development_protocols.md), [`docs/14`](../docs/14_structural_calculation_report_specification.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md), [`docs/07 PART 4`](../docs/07_web_application_ui_ux_specification.md)

---

## 2. 현황 분석 및 3대 결함 원인

### 2.1. [결함 1] 최소 철근량 검토의 전면 누락 및 불완전 구현
1. **휨 최소철근량 ($A_{s,\min}$)**:
   - 현재 `rc_beam` 계산서는 제 3장에서 $\phi M_n \ge 1.2 M_{cr}$ 및 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$만 표기하고 있습니다.
   - KDS 14 20 20 제4.2.2절 식 (4.2-1), (4.2-2)에 규정된 **최소 휨철근 단면적 $A_{s,\min} = \max\left(\frac{0.25\sqrt{f_{ck}}}{f_y} b_w d, \, \frac{1.4}{f_y} b_w d\right)$ ($mm^2$) 산출식 및 실제 배치 철근량 $A_{s,prov}$와의 직접 비교 검토($A_{s,prov} \ge A_{s,\min}$)**가 누락되어 있습니다.
2. **최소 전단철근량 ($A_{v,\min}$)**:
   - `beam.py` 내부에서 $A_{v,\min}$ 수치만 계산할 뿐, `rc_beam_report.js` 계산서 제 5장 전단 검토 어디에도 $A_{v,\min}$의 산출 근거식이나 실제 스터럽 면적 $A_{v,prov}$와의 비교($A_{v,prov} \ge A_{v,\min}$) 검토가 표기되지 않고 있습니다.
3. **최소 비틀림철근량 ($(A_v + 2A_t)_{\min}$, $A_{l,\min}$)**:
   - KDS 14 20 22 제4.5.4절 식 (4.5-6) 최소 횡방향 폐쇄스터럽 $(A_v + 2A_t)_{\min}$ 검토가 누락되었습니다.
   - `beam.py`에서 식 (4.5-7) $A_{l,\min}$을 계산하고도 $A_{l,req} = \max(A_{l,\text{calc}}, A_{l,\min})$으로 처리하지 않고 방치하여, 비틀림 소요 종방향 철근량이 과소평가되는 심각한 공학적 결함이 존재합니다.

### 2.2. [결함 2] 전단력 0 ($V_u = 0$)일 때 전단강도 검토 미생략
- 선행 `요구사항 22-5-3`에서 휨모멘트 $M_u \le 0$일 때와 비틀림 $T_u \le 0$ (또는 $T_u \le \phi T_{th}$)일 때는 상세 강도 전개식을 생략하고 1줄 요약 안내 박스를 표출하도록 개선되었습니다.
- 그러나 **계수전단력 $V_u \le 0$일 때는 이와 같은 동적 생략 로직이 누락**되어, 작용 전단력이 없음에도 불필요하게 긴 콘크리트 및 전단철근 강도식($V_c, V_s, \phi V_n$)이 그대로 출력되어 계산서의 간결성을 해치고 있습니다.

### 2.3. [결함 3] 하중이 0일 때 최소 배근량 검토가 누락/연쇄 생략될 위험
- 하중이 0이 되어 강도 검토($M_u \le \phi M_n$, $V_u \le \phi V_n$, $\tau_{comb} \le \tau_{allow}$)가 1줄 요약으로 생략되더라도, **철근콘크리트 구조물의 연성 확보 및 취성파괴 방지를 위한 법정 최소 배근 규정(최소 휨철근량, 최소 전단철근량, 스터럽 최대 간격)은 절대로 생략될 수 없습니다**.
- 현재 상태에서는 하중이 0일 때 최소 배근 검토까지 부재하거나 함께 묻혀버리는 문제가 있으므로 이를 엄격히 분리하여 독립 검토해야 합니다.

---

## 3. 세부 엔지니어링 개편 사양 명세

### 3.1. 최소 휨철근량 ($A_{s,\min}$) 3-Station 정밀 검토 체계 확립 (KDS 14 20 20 제4.2.2절)

#### (1) KDS 기준 수식 및 판정 조건
* **기본 산정식** (식 4.2-1, 4.2-2):
  $$A_{s,\min} = \max\left(\frac{0.25 \sqrt{f_{ck}}}{f_y} b_w d, \, \frac{1.4}{f_y} b_w d\right)$$
  - T형 보 플랜지가 압축을 받는 경우 ($M_u > 0$): 복부 폭 $b_w$ 적용
  - T형 보 플랜지가 인장을 받는 경우 ($M_u < 0$): $2 b_w$ 또는 플랜지 폭 $b$ 적용
* **예외 규정** (4.2.2(3)):
  - $A_{s,prov} \ge \frac{4}{3} A_{s,req}$ 만족 시 $A_{s,\min}$ 조건을 적용하지 않고 만족(O.K) 판정.
  - 또는 $\phi M_n \ge 1.2 M_{cr}$ 만족 시 만족(O.K) 판정.
* **내력비 (DCR) 산정**:
  $$\text{DCR}_{As,\min} = \frac{A_{s,\min}}{A_{s,prov}}$$

#### (2) 3-Station 위치별 적용 규격
* **단부-I (End-I)**: 상부 인장철근 $A_{s,top,I}$ 대비 $A_{s,\min,I}$ 검토 ($\text{DCR} = A_{s,\min,I} / A_{s,top,I}$)
* **중앙부-M (Center-M)**: 하부 인장철근 $A_{s,bot,M}$ 대비 $A_{s,\min,M}$ 검토 ($\text{DCR} = A_{s,\min,M} / A_{s,bot,M}$)
* **단부-J (End-J)**: 상부 인장철근 $A_{s,top,J}$ 대비 $A_{s,\min,J}$ 검토 ($\text{DCR} = A_{s,\min,J} / A_{s,top,J}$)

#### (3) 계산서 제 3장 KaTeX 수식 전개 표준
```latex
\begin{aligned}
A_{s,\min} &= \max\left(\frac{0.25\sqrt{f_{ck}}}{f_y} b_w d, \, \frac{1.4}{f_y} b_w d\right) \\
&= \max\left(\frac{0.25 \times \sqrt{27.0}}{400} \times 400 \times 540.0, \, \frac{1.4}{400} \times 400 \times 540.0\right) \\
&= \max(701.5, \, 756.0) = \mathbf{756.0\text{ mm}^2} \le A_{s,prov} (2026.8\text{ mm}^2) \\
\text{DCR}_{As,\min} &= \frac{756.0}{2026.8} = \mathbf{0.373} \le 1.000 \quad \rightarrow \quad \text{O.K}
\end{aligned}
```
> [!IMPORTANT]
> **휨모멘트가 0 ($M_u = 0$)이어도 제 3장의 $A_{s,\min}$ 수식 전개 및 $\phi M_n \ge 1.2 M_{cr}$ 검토는 무조건 출력(생략 불가)**됩니다.

---

### 3.2. 전단력 0 ($V_u \le 0$)일 때 전단강도 검토 동적 생략 및 1줄 요약

* **생략 조건**: $V_u \le 0.0\text{ kN}$
* **제 5장 5.2절 전단강도 상세 수식 대체**:
  - $V_u > 0$일 때: $V_c, V_s, \phi V_n, \text{DCR} = V_u / \phi V_n$ 상세 KaTeX 전개.
  - $V_u \le 0$일 때: 상세 강도 전개식을 생략하고 아래 1줄 요약 안내 박스를 표출:
  ```html
  <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
      <strong>5.2 전단강도 검토:</strong> 작용 계수전단력 없음 ($V_u = 0.0\text{ kN}$) — 전단강도 상세 검토 생략
  </div>
  ```

---

### 3.3. 최소 전단철근량 ($A_{v,\min}$) 및 최대 배근간격 ($s_{\max}$) 검토 의무화 (KDS 14 20 22 제4.3.3, 4.3.4절)

#### (1) KDS 기준 수식 및 법정 배치 의무
* **법정 배치 의무** (KDS 14 20 22 제4.3.3(1)):
  - $V_u > 0.5 \phi V_c$인 경우 전단철근 배치가 필수적이며,
  - **보의 전체 높이가 $h > 250\text{ mm}$인 일반 구조용 보는 전단력이 0이거나 $V_u \le 0.5 \phi V_c$이더라도 취성파괴를 방지하기 위해 최소 전단철근($A_{v,\min}$)을 반드시 배치**해야 합니다.
* **최소 전단철근량 산정** (식 4.3-1):
  $$A_{v,\min} = \max\left(0.0625 \sqrt{f_{ck}} \frac{b_w s}{f_{yt}}, \, 0.35 \frac{b_w s}{f_{yt}}\right)$$
  - 실제 제공 전단철근 단면적: $A_{v,prov} = n_{\text{legs}} \times A_{v1}$ (예: 2-D10 $\rightarrow 2 \times 71.33 = 142.7\text{ mm}^2$)
  - $\text{DCR}_{Av,\min} = \frac{A_{v,\min}}{A_{v,prov}} \le 1.000$
* **전단철근 최대 허용간격 $s_{\max}$** (KDS 14 20 22 제4.3.4절):
  $$s_{\max} = \begin{cases} \min\left(\frac{d}{2}, \, 600\text{ mm}\right) & \left(V_s \le \frac{1}{3}\sqrt{f_{ck}} b_w d\right) \\ \min\left(\frac{d}{4}, \, 300\text{ mm}\right) & \left(V_s > \frac{1}{3}\sqrt{f_{ck}} b_w d\right) \end{cases}$$
  ($V_u = 0$일 때는 $V_s = 0$이므로 항상 $s_{\max} = \min(d/2, 600\text{ mm})$ 적용)
  - $\text{DCR}_{s} = \frac{s}{s_{\max}} \le 1.000$

#### (2) 계산서 제 5장 5.3절 최소 전단철근 및 간격 독립 블록 신설 (상시 출력)
```latex
\begin{aligned}
A_{v,\min} &= \max\left(0.0625 \sqrt{f_{ck}} \frac{b_w s}{f_{yt}}, \, 0.35 \frac{b_w s}{f_{yt}}\right) \\
&= \max\left(0.0625 \times \sqrt{27.0} \times \frac{400 \times 150}{400}, \, 0.35 \times \frac{400 \times 150}{400}\right) \\
&= \max(48.7, \, 52.5) = \mathbf{52.5\text{ mm}^2} \le A_{v,prov} (142.7\text{ mm}^2) \quad (\text{DCR} = 0.368) \quad \rightarrow \quad \text{O.K} \\
s_{\max} &= \min\left(\frac{d}{2}, \, 600\right) = \min(270.0, \, 600.0) = \mathbf{270.0\text{ mm}} \ge s (150\text{ mm}) \quad (\text{DCR} = 0.556) \quad \rightarrow \quad \text{O.K}
\end{aligned}
```
> [!IMPORTANT]
> **$V_u = 0$으로 5.2절 전단강도 상세 검토가 생략되더라도, 위 5.3절 최소 전단철근량 및 최대 간격 검토는 상시 필수 출력(생략 절대 불가)**됩니다.

---

### 3.4. 최소 비틀림철근량 ($(A_v + 2A_t)_{\min}$, $A_{l,\min}$) 검토 체계 확립 (KDS 14 20 22 제4.5.4절)

#### (1) 비틀림 설계 필요 시 ($T_u > \phi T_{th}$) 최소 배근 검토
1. **최소 횡방향 폐쇄스터럽 철근량** (식 4.5-6):
   $$(A_v + 2A_t)_{\min} = \max\left(0.0625 \sqrt{f_{ck}} \frac{b_w s}{f_{yt}}, \, 0.35 \frac{b_w s}{f_{yt}}\right)$$
   - 전단과 비틀림에 필요한 총 횡방향 스터럽 소요량:
     $$(A_v + 2A_t)_{req} = \max\left(A_{v,req} + 2 A_{t,req}, \, (A_v + 2A_t)_{\min}\right)$$
   - 실제 스터럽 면적 대비 판정: $A_{v,prov} \ge (A_v + 2A_t)_{req}$
2. **최소 종방향 비틀림철근량** (식 4.5-7):
   $$A_{l,\min} = \frac{0.42 \sqrt{f_{ck}} A_{cp}}{f_y} - \left(\frac{A_t}{s}\right) p_h \left(\frac{f_{yt}}{f_y}\right)$$
   (단, 식 4.5-7 계산 시 $A_t / s$는 $0.175 b_w / f_{yt}$ 이상이어야 함)
   - 최종 소요 종방향 철근량:
     $$A_{l,req} = \max(A_{l,\text{calc}}, \, A_{l,\min})$$
   - 실제 측면철근 면적 대비 판정: $A_{l,prov} \ge A_{l,req}$ ($\text{DCR} = A_{l,req} / A_{l,prov}$)
3. **비틀림 철근 간격 제한**:
   - 횡방향 스터럽 간격: $s \le \min(p_h / 8, \, 300\text{ mm})$
   - 종방향 철근 간격: $s_l \le 300\text{ mm}$, 모서리마다 적어도 1개 배치, 직경 $d_b \ge \max(0.1 s, 10\text{ mm})$

#### (2) 비틀림 무시 가능 시 ($T_u \le \phi T_{th}$ 또는 $T_u \le 0$)
- $T_u \le \phi T_{th}$ 문턱 비틀림 판정을 명시하고, 비틀림 전용 추가 배근은 불필요함을 안내.
- 단, 부재 전체의 횡방향 최소 배근은 전단 최소철근($A_{v,\min}$) 규정을 따름을 명확히 명시.

---

## 4. 소스 코드 수정 계획 (Source Modification Plan)

### 4.1. 백엔드 계산 엔진 (`src/engine/rc/beam.py`)
1. **`FlexureResult` 스키마 확장**:
   - `As_min: float = 0.0` (최소 휨철근 소요 단면적, mm2)
   - `dcr_As_min: float = 0.0` ($A_{s,\min} / A_{s,prov}$)
   - `is_min_rebar_ok: bool = True` ($A_{s,prov} \ge A_{s,\min}$ 또는 $\phi M_n \ge 1.2 M_{cr}$ 만족)
2. **`calculate_rc_beam_flexure` 함수 로직 개편**:
   - KDS 식 (4.2-1), (4.2-2)에 의한 $A_{s,\min}$ 계산식 추가:
     `As_min = max(0.25 * math.sqrt(fck) * b_eff_calc * d / fy, 1.4 * b_eff_calc * d / fy)`
   - $M_u \le 0$인 경우에도 $A_{s,\min}$ 및 `is_min_flexure_ok`를 정밀 평가하도록 보완.
3. **`ShearResult` 스키마 확장**:
   - `dcr_Av_min: float = 0.0` ($A_{v,\min} / A_{v,prov}$)
   - `dcr_spacing: float = 0.0` ($s / s_{\max}$)
   - `is_min_shear_ok: bool = True` ($A_{v,prov} \ge A_{v,\min}$ 만족 여부)
4. **`calculate_rc_beam_shear` 함수 로직 개편**:
   - $V_u \le 0$일 때 `is_zero_shear = True` 설정
   - $V_u = 0$이더라도 $A_{v,\min}$ 및 $s_{\max}$ 검토를 독립 수행하고 `dcr_Av_min`, `dcr_spacing` 정상 산출.
5. **`TorsionResult` 스키마 및 `calculate_rc_beam_torsion` 함수 개편**:
   - `Al_min: float = 0.0`, `Av_2At_min: float = 0.0`, `s_max_torsion: float = 0.0` 필드 추가
   - $A_{l,req} = \max(A_{l,\text{calc}}, A_{l,\min})$ 수식 적용으로 소요량 누락 버그 완치.

### 4.2. 프론트엔드 A4 구조계산서 (`src/web/static/js/report/rc_beam_report.js`)
1. **제 3장 단면 연성 및 최소철근량 검토**:
   - 3.1 총괄 요약표에 **소요 $A_{s,\min}$ vs 배근 $A_{s,prov}$ 및 DCR 컬럼 신설**.
   - 3.2~3.4 상세 KaTeX 블록에 **$A_{s,\min} = \max\left(\frac{0.25\sqrt{f_{ck}}}{f_y} b_w d, \, \frac{1.4}{f_y} b_w d\right)$ 수치대입 및 판정식 추가**.
   - $M_u = 0$ 시에도 3장은 상시 100% 온전하게 출력.
2. **제 5장 전단 및 비틀림 강도 검토**:
   - 5.1 총괄 요약표에 **$A_{v,\min}$ vs $A_{v,prov}$, 스터럽 간격 $s$ vs $s_{\max}$, DCR 컬럼 신설**.
   - 5.2 전단강도 상세 검토: **$V_u \le 0$일 때 1줄 요약 박스로 동적 생략** 처리.
   - 5.3 **최소 전단철근량 및 최대 간격 검토 신설 (상시 KaTeX 출력, $V_u = 0$이어도 무조건 출력)**.
   - 5.4 비틀림 검토: $T_u > \phi T_{th}$ 시 $(A_v + 2A_t)_{\min}$ 및 $A_{l,\min}$ KaTeX 전개, $T_u \le \phi T_{th}$ 시 1줄 요약 처리.
3. **제 7장 종합 안전성 판정표**:
   - 최소 휨철근량 DCR, 최소 전단철근량 DCR, 스터럽 최대 간격 DCR, 최소 비틀림철근량 DCR을 종합 판정표에 전수 반영.

---

## 5. 단계별 마이크로 실행 계획

본 요구사항은 독립된 2개의 작업 단위로 분할하여 실행합니다:

| 세부 Step | 권장 모델 | 주요 작업 내용 | 필수 검증 기준 (DoD) |
|:---:|:---:|---|---|
| **22-7-1** | 🧠 **High** | • `beam.py` 엔진 확장 ($A_{s,\min}$, $A_{v,\min}$, $A_{l,\min}$, 간격 한계 DCR 산출 및 버그 치유)<br>• `test_rc_beam.py` 단위 테스트 확장 (최소 배근량 및 0하중 전단/휨/비틀림 검증) | `pytest tests/engine/test_rc_beam.py` PASS<br>KDS 수식 오차 $\le 0.10\%$ |
| **22-7-2** | ⚙️ **Medium** | • `rc_beam_report.js` 계산서 개편 (제 3장 $A_{s,\min}$ KaTeX 신설, 제 5장 $V_u=0$ 1줄생략 + 최소전단철근 상시출력, 비틀림 최소배근 KaTeX)<br>• 브라우저 4-Pane 통합 육안 검증 및 콘솔 무오류 확인 | 브라우저 DOM 렌더링 정상<br>콘솔 에러 0건<br>`pytest` 전체 회귀 PASS |

---

## 6. 완료 검증 기준 (Definition of Done)

- [ ] **최소 휨철근 검토**: $A_{s,\min} = \max\left(\frac{0.25\sqrt{f_{ck}}}{f_y} b_w d, \, \frac{1.4}{f_y} b_w d\right)$ 수식 전개식 및 $A_{s,prov} \ge A_{s,\min}$ 검토가 계산서 제 3장에 정상 출력될 것.
- [ ] **전단력 0 생략**: $V_u \le 0$일 때 제 5장 전단강도 상세 수식($V_c, V_s, \phi V_n$)이 생략되고 1줄 요약 박스로 간결히 표출될 것.
- [ ] **최소 전단철근 상시 검토**: $V_u \le 0$으로 전단강도 검토가 생략되더라도, 최소 전단철근량($A_{v,prov} \ge A_{v,\min}$) 및 최대 배근간격($s \le s_{\max}$) KaTeX 검토는 제 5장에 반드시 출력될 것.
- [ ] **최소 비틀림철근 검토**: $T_u > \phi T_{th}$ 시 $(A_v + 2A_t)_{\min}$ 및 $A_{l,\min}$ 산출식이 계산서에 출력되고, $A_{l,req} = \max(A_{l,\text{calc}}, A_{l,\min})$이 엔진에 정확히 반영될 것.
- [ ] **0하중 최소배근 의무화**: $M_u = 0$, $V_u = 0$, $T_u = 0$이더라도 최소 휨배근, 최소 전단배근, 스터럽 간격 검토는 절대 누락되지 않고 정상 판정될 것.
- [ ] **테스트 무결성**: `pytest` 전체 회귀 테스트(기존 391개 + 신규 테스트)가 100% 통과할 것.
- [ ] **외부 기억 동기화**: `PROJECT_PROGRESS.md`에 `Phase 22-7` 항목이 등록되고 최신 상태가 동기화될 것.
