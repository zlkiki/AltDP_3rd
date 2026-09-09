# 요구사항 22-7-2: Phase V1-01 Step 7-2 RC 보 A4 계산서 전단 0 생략 및 최소전단·비틀림 KaTeX 블록 신설 명세서

---

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 순백색 A4 구조계산서 렌더러(`src/web/static/js/report/rc_beam_report.js`)의 **(1) 제 3장 단면 연성 및 최소철근량 검토에서 현행 KDS 14 20 20 : 2022 신 기준($\phi M_n \ge 1.2 M_{cr}$) 유지 및 $M_u=0$ 시 상시 표출 보장**, **(2) 제 5장 전단 검토에서 계수전단력 0 ($V_u \le 0$)일 때 전단강도 상세 수식의 1줄 요약 동적 생략**, **(3) 제 5장 5.3절 최소 전단철근량($A_{v,prov} \ge A_{v,\min}$) 및 최대 배근간격($s \le s_{\max}$) 독립 KaTeX 검토 블록 신설 (상시 표출, $V_u \le 0$이어도 생략 불가)**, **(4) 제 5장 5.4절 비틀림 검토에서 최소 횡방향 폐쇄스터럽($(A_v + 2A_t)_{\min}$) 및 최소 종방향 철근량($A_{l,\min}$) KaTeX 전개**, 그리고 **(5) 제 7장 종합 안전성 판정표에 최소 전단철근 및 간격 DCR 반영**을 완수하기 위한 계산서 전용 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/rc_beam_report.js` (RC보 전용 순백색 A4 계산서 생성기)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KaTeX 8단계 수식 유도, `aligned` 환경 포맷팅, 인쇄 A4 레이아웃 무결성
* **연동 SSOT**:
  - **KDS 14 20 20 : 2022** (제4.2.2절 $\phi M_n \ge 1.2 M_{cr}$)
  - **KDS 14 20 22 : 2022** (제4.3.3절 $A_{v,\min}$, 제4.3.4절 $s_{\max}$, 제4.5.4절 $(A_v + 2A_t)_{\min}$, $A_{l,\min}$)
  - [`docs/14`](../docs/14_structural_calculation_report_specification.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md)

---

## 2. 세부 UI 및 KaTeX 렌더링 개편 사양

### 2.1. 제 3장: 현행 KDS 신 기준 휨 최소철근 상시 표출 확립
* **검토식 유지**:
  $$\phi M_n \ge 1.2 M_{cr} \quad \left(\text{단, } \phi M_n \ge \frac{4}{3} M_u \text{ 만족 시 적용 예외}\right)$$
  - 3-Station 각각(End-I 상부, Center-M 하부, End-J 상부)에 대한 8단계 수식 전개 유지.
* **0하중 처리**:
  - $M_u \le 0$이더라도 제 3장의 $\phi M_n \ge 1.2 M_{cr}$ 및 순인장변형률 $\epsilon_t \ge \epsilon_{t,\min}$ 검토는 **절대로 생략되지 않고 100% 정상 출력**.

---

### 2.2. 제 5장: 계수전단력 0 ($V_u \le 0$)일 때 전단강도 동적 생략 (5.2절)
* **조건**: `endIShear.VuDemand <= 0 && centerMShear.VuDemand <= 0 && endJShear.VuDemand <= 0` (또는 지배 단부 $V_u \le 0$)
* **렌더링 분기**:
  - $V_u > 0$일 때: 기존 $V_c, V_s, \phi V_n, \text{DCR} = V_u / \phi V_n$ 상세 KaTeX 전개.
  - $V_u \le 0$일 때: 상세 수식을 생략하고 1줄 안내 박스 표출:
  ```html
  <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
      <strong>5.2 전단강도 검토:</strong> 작용 계수전단력 없음 ($V_u = 0.0\text{ kN}$) — 전단강도 상세 검토 생략
  </div>
  ```

---

### 2.3. 제 5장: 5.3절 최소 전단철근량 및 최대 간격 독립 KaTeX 블록 신설 (상시 표출)
> [!IMPORTANT]
> **5.2절 전단강도 상세 검토가 생략되더라도, 본 5.3절 최소 전단철근 및 간격 검토는 상시 필수 출력**됩니다.

* **5.1 총괄표 확장**:
  - 기존 표에 소요 $A_{v,\min}$, 배근 $A_{v,prov}$, 최대간격 $s_{\max}$, 배근간격 $s$, 최소전단 DCR 컬럼 추가.
* **5.3절 독립 KaTeX 블록 구성**:
  ```latex
  \begin{aligned}
  A_{v,\min} &= \max\left(0.0625 \sqrt{f_{ck}} \frac{b_w s}{f_{yt}}, \, 0.35 \frac{b_w s}{f_{yt}}\right) \\
  &= \max\left(0.0625 \times \sqrt{27.0} \times \frac{400 \times 150}{400}, \, 0.35 \times \frac{400 \times 150}{400}\right) = \mathbf{52.5\text{ mm}^2} \le A_{v,prov} (142.7\text{ mm}^2) \\
  \text{DCR}_{Av,\min} &= \frac{A_{v,\min}}{A_{v,prov}} = \frac{52.5}{142.7} = \mathbf{0.368} \le 1.000 \quad \rightarrow \quad \text{O.K} \\
  s_{\max} &= \min\left(\frac{d}{2}, \, 600.0\right) = \min(270.0, \, 600.0) = \mathbf{270.0\text{ mm}} \ge s (150\text{ mm}) \\
  \text{DCR}_{spacing} &= \frac{s}{s_{\max}} = \frac{150.0}{270.0} = \mathbf{0.556} \le 1.000 \quad \rightarrow \quad \text{O.K}
  \end{aligned}
  ```

---

### 2.4. 제 5장: 5.4절 최소 비틀림철근량 KaTeX 전개
* **$T_u > \phi T_{th}$ 시**:
  1. **최소 횡방향 폐쇄스터럽**:
     $$(A_v + 2A_t)_{\min} = \max\left(0.0625\sqrt{f_{ck}}\frac{b_w s}{f_{yt}}, \, 0.35\frac{b_w s}{f_{yt}}\right) \le A_{v,prov}$$
  2. **최소 종방향 비틀림 철근량**:
     $$A_{l,\min} = \frac{0.42\sqrt{f_{ck}} A_{cp}}{f_y} - \left(\frac{A_t}{s}\right) p_h \frac{f_{yt}}{f_y} \quad \left(\frac{A_t}{s} \ge \frac{0.175 b_w}{f_{yt}}\right)$$
     $$A_{l,req} = \max(A_{l,\text{calc}}, \, A_{l,\min}) \le A_{l,prov}$$
  3. **간격 한계**:
     $$s \le \min\left(\frac{p_h}{8}, \, 300\text{ mm}\right), \quad s_l \le 300\text{ mm}$$
* **$T_u \le \phi T_{th}$ (또는 $T_u \le 0$) 시**:
  - 기존과 동일하게 1줄 요약 안내 박스 유지 (부재 횡방향 최소 배근은 5.3절 전단 최소철근 배근으로 갈음됨을 명시).

---

### 2.5. 제 7장: 종합 안전성 판정표 갱신
* 종합 판정 테이블에 다음 행들을 누락 없이 반영:
  - 최소 전단철근량 ($A_{v,prov} \ge A_{v,\min}$)
  - 전단철근 최대 배근간격 ($s \le s_{\max}$)
  - 최소 비틀림 종방향 철근량 ($A_{l,prov} \ge A_{l,req}$) (비틀림 작용 시)

---

## 3. 완료 검증 기준 (Definition of Done)

- [ ] 순백색 A4 계산서 제 3장에 현행 KDS 신 기준($\phi M_n \ge 1.2 M_{cr}$)이 상시 출력될 것.
- [ ] $V_u \le 0$ 입력 시 제 5장 전단강도 상세 수식이 1줄 요약 박스로 동적 생략될 것.
- [ ] $V_u \le 0$이어도 제 5장 5.3절 최소 전단철근량($A_{v,\min}$) 및 최대 간격($s_{\max}$) KaTeX 블록이 반드시 출력될 것.
- [ ] $T_u > \phi T_{th}$ 시 $(A_v + 2A_t)_{\min}$ 및 $A_{l,\min}$ KaTeX 전개가 정상 렌더링될 것.
- [ ] 제 7장 종합 판정표에 최소 전단철근 및 간격 DCR이 정상 표기될 것.
- [ ] 브라우저 콘솔 에러 0건 및 KaTeX 오버플로우 0건 유지.
