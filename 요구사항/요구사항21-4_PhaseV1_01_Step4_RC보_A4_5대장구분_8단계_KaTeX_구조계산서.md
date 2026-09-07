# 요구사항 21-4: Phase V1-1 Step 4 RC 보 A4 5대 장구분 8단계 KaTeX 구조계산서 명세서

## 1. 개요 및 계산서 SSOT 매핑

본 문서는 **RC 보 (`rc_beam`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 공학 구조계산서)** 구현을 위한 상세 요구사항 명세서입니다.
원본앱 계산서의 대단원 체계와 수치 전개 형식을 완벽히 계승하며, 웹 환경에서 수식의 깨짐 없이 순백색(`#ffffff`) A4 용지 인쇄 프리뷰로 실무 납품 가능한 고품질 구조계산서를 자동 생성합니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/redcr_rc_beam.js` (신규 보 계산서 렌더러 모듈)
  - `src/web/static/js/report_view.js` (보 계산서 디스패처 등록)
  - `src/report/generator.py` (A4 인쇄용 HTML/PDF 템플릿 엔진)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - 수백 줄의 KaTeX LaTeX 수식 조립, 분기별 수치 대입 정밀성, A4 인쇄 레이아웃 정합성 검증
* **1순위/2순위 계산서 SSOT**:
  - `original_src/Midas Design+/Dbase/DgnReportBase.ini`
  - 원본 계산서 5대 대단원 장구분 및 Step-by-Step 수식 전개 방식 완벽 계승

---

## 2. A4 구조계산서 레이아웃 및 5대 장구분 구성

모든 계산서는 인쇄 시 표준 A4 용지 규격(순백색 `#ffffff` 배경, 20mm 표준 여백)에 최적화되며 아래 5개 대단원으로 구성됩니다:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [RC BEAM STRUCTURAL CALCULATION REPORT - KDS 14 20 00]                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)                  │
│ 2. 설계 부재력 및 하중조합 (Design Factored Loads & Combinations)                       │
│ 3. 휨모멘트 강도 검토 (Flexural Strength Check - Positive & Negative Bending)           │
│ 4. 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)                           │
│ 5. 사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width)              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 8단계 KaTeX 수식 전개식 상세 명세

### 3.1. 제1장: 설계 기본 정보 및 단면 제원 (Design Information)
* **프로젝트 및 부재 메타데이터 표**:
  - 프로젝트명, 부재 번호(`BEAM-01`), 검토 일시, 설계 기준(`KDS 14 20 00 : 2022`).
* **재료 물성치 및 기하 파라미터**:
  - $f_{ck} = 27.0\text{ MPa}$, $f_y = 400.0\text{ MPa}$, $f_{yt} = 400.0\text{ MPa}$, $E_c = 8,500 \sqrt[3]{f_{cu}} = 26,066\text{ MPa}$.
  - 복부 폭 $b_w = 400\text{ mm}$, 전체 높이 $h = 600\text{ mm}$, 순피복두께 $c_v = 40\text{ mm}$, 유효높이 $d = 535\text{ mm}$.
  - T형 보의 경우 플랜지 유효폭 $b_e = 1,200\text{ mm}$, 플랜지 두께 $h_f = 150\text{ mm}$.
* **철근비 상하한 한계 검토 (KaTeX 수식)**:
  $$\rho_{min} = \max\left(\frac{0.25 \sqrt{f_{ck}}}{f_y}, \frac{1.4}{f_y}\right) = \max(0.0032, 0.0035) = 0.0035$$
  $$\rho_{max} = 0.85 \beta_1 \frac{f_{ck}}{f_y} \left(\frac{\epsilon_{cu}}{\epsilon_{cu} + 0.004}\right) = 0.0206$$
  $$\rho = \frac{A_s}{b_w d} = \frac{2,026.8}{400 \times 535} = 0.0095 \quad \longrightarrow \quad \rho_{min} \le \rho \le \rho_{max} \quad [\mathbf{O.K}]$$

### 3.2. 제2장: 설계 부재력 및 하중조합 (Design Loads)
* **단부 및 중앙부 설계 계수하중 요약 표**:
  - End-I: $M_u^- = 320.0\text{ kN}\cdot\text{m}, V_u = 240.0\text{ kN}, T_u = 25.0\text{ kN}\cdot\text{m}$.
  - Center-M: $M_u^+ = 280.0\text{ kN}\cdot\text{m}, V_u = 60.0\text{ kN}, T_u = 10.0\text{ kN}\cdot\text{m}$.
  - End-J: $M_u^- = 310.0\text{ kN}\cdot\text{m}, V_u = 230.0\text{ kN}, T_u = 25.0\text{ kN}\cdot\text{m}$.

### 3.3. 제3장: 휨모멘트 강도 검토 (Flexural Strength Check - 8단계 전개)
1. **압축응력블록 깊이 $a$ 및 중립축 $c$ 유도**:
   $$a = \frac{A_s f_y - A_s' f_s'}{\alpha_1 f_{ck} b_w} = \frac{2,026.8 \times 400 - 642.4 \times 400}{0.85 \times 27 \times 400} = 60.2\text{ mm}$$
   $$c = \frac{a}{\beta_1} = \frac{60.2}{0.80} = 75.3\text{ mm}$$
2. **최외단 인장철근 변형률 $\epsilon_t$ 산정**:
   $$\epsilon_t = \epsilon_{cu} \left(\frac{d - c}{c}\right) = 0.0033 \left(\frac{535 - 75.3}{75.3}\right) = 0.0201$$
3. **강도감소계수 $\phi$ 판정**:
   $$\epsilon_t = 0.0201 \ge 0.005 \quad \longrightarrow \quad \text{인장지배단면, } \phi = 0.85$$
4. **설계 휨모멘트 강도 $\phi M_n$ 유도**:
   $$M_n = A_s f_y \left(d - \frac{a}{2}\right) + A_s' f_s' \left(\frac{a}{2} - d'\right) = 408.5\text{ kN}\cdot\text{m}$$
   $$\phi M_n = 0.85 \times 408.5 = 347.2\text{ kN}\cdot\text{m}$$
5. **DCR 및 최종 판정**:
   $$\text{DCR} = \frac{M_u}{\phi M_n} = \frac{280.0}{347.2} = 0.806 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### 3.4. 제4장: 전단 및 비틀림 강도 검토 (Shear & Torsion Check)
1. **콘크리트 전단강도 $V_c$**:
   $$V_c = \frac{1}{6} \lambda \sqrt{f_{ck}} b_w d = \frac{1}{6} \times 1.0 \times \sqrt{27} \times 400 \times 535 \times 10^{-3} = 185.3\text{ kN}$$
2. **전단철근 부담강도 $V_s$**:
   $$V_s = \frac{A_v f_{yt} d}{s} = \frac{142.6 \times 400 \times 535}{150} \times 10^{-3} = 203.4\text{ kN}$$
3. **설계 전단강도 $\phi V_n$ 및 DCR**:
   $$\phi V_n = 0.75 (V_c + V_s) = 0.75 \times (185.3 + 203.4) = 291.5\text{ kN}$$
   $$\text{DCR}_V = \frac{V_u}{\phi V_n} = \frac{240.0}{291.5} = 0.823 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$
4. **비틀림 임계 검토 및 상호작용**:
   $$T_{th} = 0.0625 \lambda \sqrt{f_{ck}} \left(\frac{A_{cp}^2}{p_{cp}}\right) = 14.2\text{ kN}\cdot\text{m}$$
   $$T_u = 25.0\text{ kN}\cdot\text{m} > \phi T_{th} = 0.75 \times 14.2 = 10.7\text{ kN}\cdot\text{m} \quad (\text{비틀림 설계 필요})$$
   $$\sqrt{\left(\frac{V_u}{b_w d}\right)^2 + \left(\frac{T_u p_h}{1.7 A_{oh}^2}\right)^2} \le \phi \left(\frac{V_c}{b_w d} + \frac{2}{3} \sqrt{f_{ck}}\right) \quad \longrightarrow \quad \mathbf{O.K}$$
   $$A_l = \frac{A_t}{s} p_h \left(\frac{f_{yt}}{f_y}\right) = 542.8\text{ mm}^2 \le A_{l,prov} = 642.4\text{ mm}^2 \quad \longrightarrow \quad \mathbf{O.K}$$

### 3.5. 제5장: 사용성 한계상태 검토 (Serviceability Check)
1. **Branson 유효단면2차모멘트 $I_e$**:
   $$M_{cr} = \frac{f_r I_g}{y_t} = \frac{3.27 \times 7.2 \times 10^9}{300} \times 10^{-6} = 78.5\text{ kN}\cdot\text{m}$$
   $$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} = 3.85 \times 10^9\text{ mm}^4$$
2. **처짐 검토**:
   $$\Delta_i = 6.2\text{ mm}, \quad \lambda_\Delta = \frac{2.0}{1 + 50(0.003)} = 1.74, \quad \Delta_{long} = 1.74 \times 3.8 = 6.6\text{ mm}$$
   $$\Delta_{total} = \Delta_i + \Delta_{long} = 12.8\text{ mm} \le \Delta_{allow} = \frac{L}{240} = 25.0\text{ mm} \quad \longrightarrow \quad \mathbf{O.K}$$
3. **직접 균열폭 검토**:
   $$w = 1.08 \beta \epsilon_s \sqrt[3]{d_c A} \times 10^{-3} = 0.22\text{ mm} \le w_{lim} = 0.30\text{ mm} \quad \longrightarrow \quad \mathbf{O.K}$$

---

## 4. 검증 및 수용 기준 (DoD)

- [ ] `src/web/static/js/report/redcr_rc_beam.js` 구현 완료.
- [ ] 5대 장구분 및 8단계 KaTeX 수식 전개식 렌더링 검증.
- [ ] 모든 검토 항목의 `  →  O.K / N.G` 상태 표시 정상 출력.
- [ ] 순백색(`#ffffff`) A4 용지 인쇄 프리뷰 레이아웃 및 페이지 분할 정합성 확인.
- [ ] KaTeX 수식 문법 에러 및 콘솔 에러 0건.
