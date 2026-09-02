# KDS 구조계산서 및 검토보고서 종합 명세서 (14_structural_calculation_report_specification.md)

본 문서는 Midas Design+ 원본 바이너리(`original_src/`), 언어 및 리포트 리소스(`DgnLanguage/Korean/GENDgnReportKR.ini`, `CVLDgnReportKR.ini`, `DgnReportBase.ini`, `DLG_DPLUS_DGN.ini`) 및 AltDP 웹 리포트 엔진에서 추출된 **요약 보고서(Summary Report)**, **상세 보고서(Detail Report)**, **사용자 입력 정보 보고서(Input Data Report)**, **보고서 생성 옵션** 및 **부재별 KDS 표준 수식 체계**를 총체적으로 집대성한 기술 명세서(Report SSOT)입니다.

---

## 1. 구조계산서 3대 보고서 유형 체계

원본 Midas Design+ 및 AltDP_3rd는 엔지니어링 목적에 따라 **3가지 전용 보고서 모드**를 지원합니다.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ KDS 구조계산서 3대 보고서 체계 (Structural Report Modes)                                         │
├───────────────────────────────┬─────────────────────────────────┬───────────────────────────────┤
│ 1. 요약 보고서 (Summary)       │ 2. 상세 보고서 (Detail)         │ 3. 입력 데이터 보고서 (Input) │
├───────────────────────────────┼─────────────────────────────────┼───────────────────────────────┤
│ • 1~2페이지 압축 A4 레이아웃  │ • 인허가 및 심의 제출용 정밀식  │ • 사용자 원시 입력 제원 리스트│
│ • 핵심 설계조건 & 재료 요약   │ • KDS 조항별 Step-by-Step 유도  │ • 단면/재료/배근/하중 파라미터│
│ • 2D SVG 단면 배근도          │ • 모든 중간 변수(a, c, εt, φ)   │ • 설계 옵션 및 하중조합 케이스│
│ • 최악 하중 케이스(Governing) │ • 2D 단면도 + P-M 상관도 곡선   │ • 계산서 본문 앞/뒤 첨부 가능 │
│ • 종합 안전성(DCR) 검토표     │ • 전체 하중조합별 전수 검토표   │                               │
└───────────────────────────────┴─────────────────────────────────┴───────────────────────────────┘
```

---

## 2. 보고서 구성 옵션 상세 명세 (`IDD_DGN_REPORT_OPT_*` 역공학)

`DLG_DPLUS_DGN.ini`의 `IDD_DGN_REPORT_OPT_DLG`에서 역공학 분석된 보고서 제어 옵션입니다:

### 2.1. 사용자 입력 정보 포함 옵션 (`IDC_DGN_REPORT_CHECK_INP`)
* **`[체크 ON]` (기본값)**:
  - 계산서 상단에 **[1. 사용자 입력 데이터 상세 (Input Data Specification)]** 섹션을 자동으로 포함하여 설계자가 입력한 재료 물성치, 단면 치수, 배근 간격, 하중 조건 및 검토 옵션을 완벽히 수록.
* **`[체크 OFF]`**:
  - 사용자 입력 섹션을 생략하고 **[검토 결과 요약]** 및 **[KDS 상세 수식 계산]** 위주로 출력하여 문서 페이지 수를 최소화.

### 2.2. 보고서 출력 범위 및 시각화 옵션 (`IDD_DGN_REPORT_OPT_DATA_DLG`)
* **시각화 항목 포함 (`IDC_DGN_CHK_VISITEM`, `IDC_DGN_CHK_PRNITEM`)**:
  - 2D 배근 단면도(SVG), 철근 배치 상세도, P-M 상관 곡선 차트, 지반 접지압 분포도 삽입 여부.
* **결과 테이블 출력 (`IDC_DGN_CHK_RESTABLE`)**:
  - 최악 하중 조합(Governing LCB)만 출력할지, 전체 하중 조합 케이스별 내력비 테이블을 모두 출력할지 선택.
* **단면 강도 테이블 (`IDC_DGN_CHK_BARCLUSTR`)**:
  - 철근 열별 단면적, 중심거리, 유효깊이 산정 근거 표 포함.

### 2.3. 단위계 및 수치 포맷팅 옵션 (`IDD_DGN_REPORT_OPT_PAGE_DLG`, `NUMB_DLG`)
* **단위계 제어 (`IDC_DGN_CHK_CODE_UNIT`, `IDC_DGN_CHK_UNIT_USER`)**:
  - `설계 기준 단위계 고정 (Code Unit)`: KDS 표준 SI 단위계($\text{mm, MPa, kN, kN}\cdot\text{m}$)로 고정 출력.
  - `사용자 단위계 연동 (User Unit)`: 화면에서 선택한 단위계(MKS: $\text{tonf, cm, kgf/cm}^2$ 또는 US: $\text{kip, in, ksi}$)로 실시간 환산 출력.
* **수치 유효숫자 및 소수점 자리수 규격**:
  - 응력 ($\text{MPa}$): 소수점 2자리 (`24.00 MPa`)
  - 힘 ($\text{kN}$): 소수점 2자리 (`150.25 kN`)
  - 모멘트 ($\text{kN}\cdot\text{m}$): 소수점 2자리 (`210.50 kN·m`)
  - 변위/처짐 ($\text{mm}$): 소수점 1자리 (`12.4 mm`)
  - 균열폭 ($\text{mm}$): 소수점 2자리 (`0.18 mm`)
  - DCR (안전율 비): 소수점 3자리 (`0.807`)

---

## 3. 요약 보고서 (Summary Report) 표준 목차 및 서식

1~2페이지 이내로 핵심 안전성을 증명하는 간결한 양식입니다.

```markdown
# [부재명: 1F-B1] 구조계산서 (요약 보고서)

## 1. 일반 설계 조건 및 재료 특성 (General Information)
- 프로젝트명: AltDP_3rd Engineering Project | 검토일자: 2026-09-02 | 검토자: 구조설계팀
- 적용 설계 기준: KDS 14 20 00 (콘크리트구조설계기준) | 단위계: SI Unit (kN, mm, MPa)
- 재료 특성: 콘크리트 $f_{ck} = 24.0 \text{ MPa}$, 주철근 $f_y = 400.0 \text{ MPa}$, 전단철근 $f_{ys} = 400.0 \text{ MPa}$

## 2. 단면 형상 및 주요 배근 제원 (Section & Reinforcement)
- 단면 크기: 폭 $b = 400 \text{ mm}$, 높이 $h = 600 \text{ mm}$, 유효깊이 $d = 540 \text{ mm}$, 피복두께 $d_c = 40 \text{ mm}$
- 상부근: 4-D25 ($A_s = 2,027 \text{ mm}^2$) | 하부근: 4-D25 ($A_s = 2,027 \text{ mm}^2$)
- 전단철근: HD10 @ 150 (2-Legs, $A_v = 142.6 \text{ mm}^2$)
- [2D 배근 단면도 SVG 벡터 그래픽 삽입]

## 3. 소요 부재력 및 위험 하중조합 (Governing Design Forces)
- 위험 하중조합 (LCB): 1.2D + 1.6L
- 계수 부재력: $M_u = 210.00 \text{ kN}\cdot\text{m}$, $V_u = 150.00 \text{ kN}$, $P_u = 0.00 \text{ kN}$

## 4. 종합 안전성 검토 결과 요약표 (Executive Summary)
| 검토 항목 | KDS 설계 기준식 | 소요 부재력 (Demand) | 설계 내력 (Capacity) | 안전율 (DCR) | 최종 판정 |
|---|---|---|---|---|---|
| **휨 강도 (정모멘트)** | KDS 14 20 20 (4.1) | $M_u = 210.00 \text{ kN}\cdot\text{m}$ | $\phi M_n = 260.27 \text{ kN}\cdot\text{m}$ | **0.807** | **OK** 🟢 |
| **전단 강도** | KDS 14 20 22 (4.1) | $V_u = 150.00 \text{ kN}$ | $\phi V_n = 229.35 \text{ kN}$ | **0.654** | **OK** 🟢 |
| **단기/장기 처짐** | KDS 14 20 30 (4.2) | $\Delta_{max} = 12.4 \text{ mm}$ | $\Delta_{allow} = 20.0 \text{ mm}$ | **0.620** | **OK** 🟢 |
| **직접 균열폭** | KDS 14 20 30 (4.1) | $w = 0.18 \text{ mm}$ | $w_{allow} = 0.30 \text{ mm}$ | **0.600** | **OK** 🟢 |
```

---

## 4. 상세 보고서 (Detail Report) 표준 목차 및 KDS Step-by-Step 수식 체계

인허가 관공서 및 구조심의 제출용 정밀 공학 계산서입니다.

```markdown
# [부재명: 1F-B1] 구조계산서 (상세 보고서)

## 1. 일반 설계 조건 (General Design Criteria)
- 부재 명칭: 1F-B1 (1층 메인 거더)
- 적용 기준: KDS 14 20 00 : 2022 콘크리트구조 설계기준
- 환경 조건: 건조 환경 (Dry Environment, 허용 균열폭 $w_{all} = 0.3\text{ mm}$)
- 내진 설계 범주: 중간 모멘트 골조 (IMF)

## 2. 사용자 입력 데이터 상세 (Input Data Specification)
*(※ 보고서 옵션에서 `입력 정보 포함` 선택 시 자동 수록)*
- 부재 길이 (경간): $L = 6,000 \text{ mm}$, 순경간 $L_n = 5,600 \text{ mm}$
- 단면 제원: $b = 400 \text{ mm}, h = 600 \text{ mm}, d_{ct} = 60 \text{ mm}, d_{cb} = 60 \text{ mm}$
- 재료 물성: $f_{ck} = 24 \text{ MPa}, f_y = 400 \text{ MPa}, f_{ys} = 400 \text{ MPa}, E_c = 25,050 \text{ MPa}, E_s = 200,000 \text{ MPa}$
- 철근 배근: 상부 1단 3-D25 + 2단 1-D25, 하부 4-D25, 스터럽 HD10 @ 150
- 설계 하중: 고정하중 $D = 35 \text{ kN/m}$, 활하중 $L = 20 \text{ kN/m}$

## 3. 단면 특성 및 강도계수 산정 (Section Properties)
- 비균열 전단면적: $A_g = b \cdot h = 400 \times 600 = 240,000 \text{ mm}^2$
- 비균열 단면2차모멘트: $I_g = \frac{b h^3}{12} = \frac{400 \times 600^3}{12} = 7.200 \times 10^9 \text{ mm}^4$
- 파괴계수: $f_r = 0.63 \lambda \sqrt{f_{ck}} = 0.63 \times 1.0 \times \sqrt{24} = 3.086 \text{ MPa}$
- 균열휨모멘트: $M_{cr} = \frac{f_r I_g}{y_t} = \frac{3.086 \times 7.200 \times 10^9}{300} \times 10^{-6} = 74.07 \text{ kN}\cdot\text{m}$

## 4. 정밀 구조 안전성 검토 (Step-by-Step Code Verification)

### 4.1. 휨모멘트 강도 검토 (KDS 14 20 20)
1. **등가 직사각형 응력블록 깊이 ($a$)**:
   $$\beta_1 = 0.85 - 0.007(f_{ck} - 28) = 0.85 \quad (f_{ck} \le 28\text{ MPa})$$
   $$a = \frac{A_s f_y}{0.85 f_{ck} b} = \frac{2,026.8 \times 400}{0.85 \times 24 \times 400} = 99.35 \text{ mm}$$
2. **중립축 깊이 ($c$) 및 순인장변형률 ($\epsilon_t$)**:
   $$c = \frac{a}{\beta_1} = \frac{99.35}{0.85} = 116.89 \text{ mm}$$
   $$\epsilon_t = 0.003 \cdot \frac{d - c}{c} = 0.003 \cdot \frac{540 - 116.89}{116.89} = 0.01086 > 0.005 \quad (\text{인장지배단면})$$
3. **강도감소계수 ($\phi$) 및 설계휨강도 ($\phi M_n$)**:
   $$\phi = 0.85 \quad (\epsilon_t \ge 0.005)$$
   $$M_n = A_s f_y \left(d - \frac{a}{2}\right) = 2,026.8 \times 400 \times \left(540 - \frac{99.35}{2}\right) \times 10^{-6} = 397.51 \text{ kN}\cdot\text{m}$$
   $$\phi M_n = 0.85 \times 397.51 = 337.88 \text{ kN}\cdot\text{m} \ge M_u = 210.00 \text{ kN}\cdot\text{m}$$
   $$\text{DCR} = \frac{210.00}{337.88} = \mathbf{0.622} \le 1.0 \quad \longrightarrow \quad \mathbf{OK}$$

### 4.2. 전단 강도 검토 (KDS 14 20 22)
1. **콘크리트 분담 전단강도 ($V_c$)**:
   $$V_c = \frac{1}{6} \lambda \sqrt{f_{ck}} b_w d = \frac{1}{6} \times 1.0 \times \sqrt{24} \times 400 \times 540 \times 10^{-3} = 176.36 \text{ kN}$$
2. **전단철근 분담 전단강도 ($V_s$)**:
   $$V_s = \frac{A_v f_{ys} d}{s} = \frac{142.6 \times 400 \times 540}{150} \times 10^{-3} = 205.34 \text{ kN}$$
3. **최대 전단강도 한계 검토 ($V_{n,\max}$)**:
   $$V_{s,\max} = \frac{2}{3} \sqrt{f_{ck}} b_w d = 705.45 \text{ kN} \ge V_s = 205.34 \text{ kN} \quad (\mathbf{OK})$$
4. **설계 전단강도 ($\phi V_n$)**:
   $$\phi V_n = 0.75 \times (176.36 + 205.34) = 286.28 \text{ kN} \ge V_u = 150.00 \text{ kN}$$
   $$\text{DCR} = \frac{150.00}{286.28} = \mathbf{0.524} \le 1.0 \quad \longrightarrow \quad \mathbf{OK}$$

### 4.3. 사용성 한계상태 검토 (KDS 14 20 30)
1. **Branson 유효단면2차모멘트 ($I_e$)**:
   $$I_{cr} = 3.120 \times 10^9 \text{ mm}^4, \quad M_a = 145.0 \text{ kN}\cdot\text{m} > M_{cr} = 74.07 \text{ kN}\cdot\text{m}$$
   $$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} = 3.664 \times 10^9 \text{ mm}^4 \le I_g$$
2. **단기 즉시처짐 및 장기 처짐 ($\Delta_{total}$)**:
   $$\Delta_i = 4.8 \text{ mm}, \quad \xi = 2.0 \text{ (5년 이상)}, \quad \rho' = 0.0094$$
   $$\lambda_{\Delta} = \frac{\xi}{1 + 50 \rho'} = 1.361, \quad \Delta_{long} = \Delta_{sus} \times 1.361 = 5.2 \text{ mm}$$
   $$\Delta_{total} = \Delta_i + \Delta_{long} = 10.0 \text{ mm} \le \Delta_{all} = \frac{L}{250} = 24.0 \text{ mm} \quad (\mathbf{OK})$$
3. **직접 균열폭 검토 ($w$)**:
   $$f_s = 0.6 f_y = 240 \text{ MPa}, \quad d_c = 40 \text{ mm}, \quad s = 105 \text{ mm}$$
   $$w = 1.08 \cdot \beta \cdot \frac{f_s}{E_s} \cdot \sqrt[3]{d_c s} = 0.16 \text{ mm} \le w_{all} = 0.30 \text{ mm} \quad (\mathbf{OK})$$

## 5. 종합 검토 판정표 (Final Summary)
| 검토 부위 | 항목 | 소요력 (Demand) | 설계내력 (Capacity) | DCR | 판정 |
|---|---|---|---|---|---|
| 중앙부 | 정모멘트 휨 | $210.00 \text{ kN}\cdot\text{m}$ | $337.88 \text{ kN}\cdot\text{m}$ | **0.622** | **PASS** 🟢 |
| 좌측 단부 | 부모멘트 휨 | $185.00 \text{ kN}\cdot\text{m}$ | $337.88 \text{ kN}\cdot\text{m}$ | **0.548** | **PASS** 🟢 |
| 좌측 단부 | 전단력 | $150.00 \text{ kN}$ | $286.28 \text{ kN}$ | **0.524** | **PASS** 🟢 |
| 중앙부 | 총 처짐 | $10.0 \text{ mm}$ | $24.0 \text{ mm}$ | **0.417** | **PASS** 🟢 |
| 중앙부 | 균열폭 | $0.16 \text{ mm}$ | $0.30 \text{ mm}$ | **0.533** | **PASS** 🟢 |
```

---

## 5. 부재 도메인별 검토보고서 필수 수식 인벤토리

| 부재 유형 | 핵심 검토 항목 | 주요 KDS 수식 및 검토 변수 |
|---|---|---|
| **RC 보** | 휨, 전단, 비틀림, 처짐, 균열 | $a, c, \epsilon_t, \phi M_n, V_c, V_s, V_{n,\max}, T_{th}, T_{cr}, I_e, \Delta, w$ |
| **RC 기둥** | P-M 상관도, 세장비, 횡구속 | $P_n, \phi P_{n,\max}, M_n, e_{\min}, kL/r, \delta_{ns}, \delta_s, s_{tie}, \rho_s$ |
| **RC 전단벽** | 면내전단, 철근비, 경계요소 | $V_c, V_s, V_{n,\max}, \rho_v, \rho_n, c \ge \frac{l_w}{600(\delta_u/h_w)}, SBE$ |
| **RC 슬래브** | 휨, 처짐, 펀칭전단(2방향) | $h_{\min}, M_u(\text{DDM}), v_c = \min(0.33\sqrt{f_{ck}}, 0.17(1+2/\beta_c)\sqrt{f_{ck}}, 0.083(\alpha_s d/b_o + 2)\sqrt{f_{ck}})$ |
| **RC 기초/옹벽** | 지반지지력, 펀칭, 전도/활동 | $q_{\max} = \frac{P}{A}(1 \pm \frac{6e}{B}) \le q_a, V_c(\text{punching}), FS_{over} \ge 2.0, FS_{slide} \ge 1.5$ |
| **Steel 보/기둥** | 판폭두께비, 좌굴, P-M | $\lambda \le \lambda_p \le \lambda_r, L_b \le L_p \le L_r, F_{cr}, \frac{P_u}{\phi P_n} + \frac{8}{9}(\frac{M_{ux}}{\phi M_{nx}} + \frac{M_{uy}}{\phi M_{ny}}) \le 1.0$ |
| **접합부/주각부** | 볼트, 용접, 베이스플레이트 | $R_n(\text{shear/bearing}), R_n(\text{block shear}), F_w = 0.6 F_{EXX}, t_p = l \sqrt{\frac{2 P_u}{0.9 F_y B N}}$ |

---

## 6. 결론 및 웹 리포트 생성기 (`ReportGenerator`) 연동 규약
1. **SSOT 준수**: 본 문서에 정의된 수식과 포맷팅 규칙은 `src/report/generator.py`, `src/report/excel_exporter.py`, `src/report/pdf_exporter.py` 및 프론트엔드 `redcr_common_renderer.js`에서 100% 동일하게 구현됩니다.
2. **무결한 인쇄성**: 순백색 고정 배경 및 CSS Paged Media `@media print` 스타일을 통해 화면에서 보는 결과와 A4 실제 인쇄물이 1:1로 일치함을 보장합니다.
