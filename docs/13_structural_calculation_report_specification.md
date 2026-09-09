# KDS 구조계산서 및 검토보고서 종합 명세서 (13_structural_calculation_report_specification.md)

본 문서는 원본앱 바이너리(`original_src/`), 언어 및 리포트 리소스(`DgnLanguage/Korean/GENDgnReportKR.ini`, `CVLDgnReportKR.ini`, `DgnReportBase.ini`, `DLG_DPLUS_DGN.ini`) 및 **AltDP_3rd RC 보(`rc_beam`)·RC 기둥(`rc_column`) 플래그십 모듈**에서 검증·정립된 **요약 보고서(Summary Report)**, **상세 보고서(Detail Report)**, **사용자 입력 정보 보고서(Input Data Report)**, **보고서 생성 옵션**, **A4 순백색 KaTeX 수식 전개 체계** 및 **Tracer AST 리포트 파이프라인**을 총체적으로 집대성한 전 부재 공통 기술 명세서(Report SSOT)입니다.

---

## 1. 구조계산서 3대 보고서 유형 체계

AltDP_3rd는 실무 엔지니어링 및 인허가 목적에 따라 **3가지 전용 보고서 모드**를 지원합니다.

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
│ • 종합 안전성(DCR) 검토표     │ • 3-Station 전수 검토 분기      │                               │
└───────────────────────────────┴─────────────────────────────────┴───────────────────────────────┘
```

---

## 2. 보고서 구성 옵션 및 공통 표기 규약 (`IDD_DGN_REPORT_OPT_*`)

### 2.1. 사용자 입력 정보 포함 옵션 (`IDC_DGN_REPORT_CHECK_INP`)
* **`[체크 ON]` (기본값)**:
  - 계산서 상단에 **[사용자 입력 데이터 상세 (Input Data Specification)]** 섹션을 자동으로 포함하여 재료 물성치, 단면 치수, 배근 간격, 하중 조건 및 검토 옵션을 완벽히 수록.
* **`[체크 OFF]`**:
  - 사용자 입력 섹션을 생략하고 **[검토 결과 요약]** 및 **[KDS 상세 수식 계산]** 위주로 출력하여 문서 페이지 수를 압축.

### 2.2. 보고서 출력 범위 및 시각화 옵션 (`IDD_DGN_REPORT_OPT_DATA_DLG`)
* **시각화 항목 포함 (`IDC_DGN_CHK_VISITEM`, `IDC_DGN_CHK_PRNITEM`)**:
  - 2D 배근 단면도(SVG, $260 \times 300\text{ px}$ 정밀 렌더링), 철근 배치 상세도, P-M 상관 곡선 차트, 지반 접지압 분포도 삽입.
* **결과 테이블 출력 (`IDC_DGN_CHK_RESTABLE`)**:
  - 최악 위험 단면(Governing Station/LCB)만 출력할지, 전체 3-Station(End-I, Mid-M, End-J) 내력비 테이블을 모두 출력할지 제어.
* **단면 강도 테이블 (`IDC_DGN_CHK_BARCLUSTR`)**:
  - 1단~3단 철근 열별 단면적($A_s$), 중심거리, 유효깊이($d, d_t$) 산정 근거 표 포함.

### 2.3. 단위계 및 수치 포맷팅 표준 규격
* **KDS 표준 SI 단위계 고정**:
  - 응력 및 강도 ($\text{MPa}$): 소수점 1~2자리 (`24.0 MPa`, `400.0 MPa`)
  - 힘 및 하중 ($\text{kN}$): 소수점 2자리 (`150.25 kN`)
  - 휨모멘트 ($\text{kN}\cdot\text{m}$): 소수점 2자리 (`210.50 kN·m`)
  - 치수 및 유효깊이 ($\text{mm}$): 소수점 0~1자리 (`400 mm`, `540.5 mm`)
  - 변위 및 처짐 ($\text{mm}$): 소수점 1자리 (`10.4 mm`)
  - 균열폭 ($\text{mm}$): 소수점 2자리 (`0.18 mm`)
  - 철근비 ($\rho$): 소수점 5자리 (`0.00942`)
  - **DCR (내력비, 안전율 비)**: 소수점 3자리 볼드 표기 (`0.622`)

### 2.4. 3-Station (End-I, Center-M, End-J) 다중 위험단면 표기 규약
RC 보, 기둥, 거더 등 선형 구조부재는 단일 단면만 검토하는 오류를 방지하고, 3대 위험 위치를 독립적으로 평가하여 계산서에 분기 표기합니다:
* **End-I (좌측 단부)**: 부모멘트($M_u^-$), 최대 전단력($V_u$), 비틀림모멘트($T_u$) 지배 검토.
* **Center-M (중앙부)**: 정모멘트($M_u^+$), Branson 처짐($\Delta$), 균열폭($w$) 지배 검토.
* **End-J (우측 단부)**: 부모멘트($M_u^-$), 최대 전단력($V_u$), 비틀림모멘트($T_u$) 지배 검토.
* **계산서 출력 방식**: 종합 요약표에서는 3-Station 중 최대 DCR을 갖는 Governing Station을 최우선 하이라이트하고, 상세 보고서에서는 각 Station별 검토 수식을 탭/섹션별로 완전 전개.

### 2.5. 0 하중(Zero Load) 시 '최소배근 강제 판정' 표기 규약
설계 부재력이 $0$ ($M_u = 0, V_u = 0, T_u = 0$)으로 입력되더라도 단순 계산 생략(DCR=0.000 PASS)을 금지하고 다음 최소 규준식을 계산서에 필수로 출력합니다:
1. **휨 최소철근량 판정식**:
   $$\rho_{\min} = \max\left(\frac{0.25\sqrt{f_{ck}}}{f_y}, \frac{1.4}{f_y}\right) \le \rho_{prov} \quad \text{또는} \quad \phi M_n \ge 1.2 M_{cr}$$
2. **최소 전단철근량 및 최대 간격 판정식**:
   $$A_{v,\min} = 0.0625\sqrt{f_{ck}}\frac{b_w s}{f_{yt}} \ge 0.35\frac{b_w s}{f_{yt}}, \quad s \le s_{\max} = \min(d/2, 600\text{ mm})$$
3. **최소 비틀림철근 판정식**:
   $$A_{l,\min} = \frac{0.42\sqrt{f_{ck}} A_{cp}}{f_y} - \left(\frac{A_t}{s}\right) p_h \left(\frac{f_{yt}}{f_y}\right)$$

### 2.6. 다단배근(1~3단) 및 T형/복합 단면 기하 표기 규약
* **유효깊이 $d$ vs $d_t$ 분리 표기**:
  - 인장철근 전체 도심까지의 유효깊이: $d = h - y_{cg}$ (휨강도 $M_n$ 및 전단강도 $V_c$ 산정에 사용)
  - 최외단 인장철근 도심까지의 깊이: $d_t = h - \text{cover} - d_{stirrup} - d_b/2$ (최외단 인장변형률 $\epsilon_t$ 및 강도감소계수 $\phi$ 산정에 사용)
* **T형/L형 보 플랜지 거동 판정식**:
  - 유효 플랜지 폭 $b_e$, 플랜지 두께 $h_f$, 복부 폭 $b_w$ 명시.
  - $a \le h_f$: 직사각형 보 거동으로 간주하여 플랜지 폭 $b_e$ 적용.
  - $a > h_f$: 플랜지 돌출부 압축력 $C_{cf} = 0.85 f_{ck} (b_e - b_w) h_f$를 분리하는 T형 보 엄밀식 전개.

---

## 3. 요약 보고서 (Summary Report) 공통 표준 서식

1~2페이지 이내의 압축 A4 레이아웃으로 핵심 안전성을 한눈에 증명하는 전 부재 공통 서식입니다:

```markdown
# [부재명: {MEMBER_NAME}] KDS 구조계산서 (요약 보고서)

## 1. 일반 설계 조건 및 사용 재료 (General Information & Materials)
- 프로젝트명: {PROJECT_NAME} | 부재 분류: {CATEGORY} › {MEMBER_TYPE} | 검토일자: {DATE}
- 적용 기준: KDS 국가건설기준 (KDS 14 20 00 / KDS 14 31 00 등) | 단위계: SI Unit (kN, mm, MPa)
- 주요 재료: 주재료 강도 ({fck} 또는 {Fy}), 보조재료 강도 ({fy} 또는 {Fu}), 탄성계수 ({E})

## 2. 단면 제원 및 상세 (2D SVG 벡터 그래픽 포함)
- 단면 치수: {SECTION_LABEL} (폭, 높이, 두께 또는 형강 호칭)
- 주요 상세: 주근/플랜지 배근 제원, 횡보강/웨브 제원, 피복두께 / 지지조건
- [260x300 px 부재별 정밀 2D 단면 및 상세도 SVG 벡터 그래픽 임베드]

## 3. 한계상태별 안전성 검토 결과 종합표 (DCR Summary)
| 검토 단면 (Station/Part) | 검토 한계상태 (Limit State) | 계수 소요력 (Demand) | 설계 내력 (Capacity) | DCR | 판정 |
|---|---|---|---|---|---|
| **위험 단면 1 (Governing)** | 주강도 검토 (휨 / 압축 / 인장) | {Demand_1} | {Capacity_1} | **{DCR_1}** | **PASS** 🟢 |
| **위험 단면 1 (Governing)** | 전단 / 비틀림 / 좌굴 검토 | {Demand_2} | {Capacity_2} | **{DCR_2}** | **PASS** 🟢 |
| **사용성 단면 (Service)** | 단기 / 장기 처짐 검토 | {Defl_actual} | {Defl_allow} | **{DCR_3}** | **PASS** 🟢 |
| **사용성 단면 (Service)** | 균열폭 / 순간격 / 응력 검토 | {Crack_actual} | {Crack_allow} | **{DCR_4}** | **PASS** 🟢 |

- **최대 지배 DCR**: **{MAX_DCR}** ({GOVERNING_FAILURE_MODE} 파괴 모드 지배)
- **종합 안전성 판정**: **{FINAL_STATUS} (ALL PASS)** 🟢
```
*(※ RC 보 전용 실제 요약 보고서 출력 예시는 [`docs/15_rc_beam_specification.md`](15_rc_beam_common_requirements_report.md) 참조)*

---

## 4. 상세 보고서 (Detail Report) KDS 공통 7대 챕터 체계

관공서 및 구조심의 제출을 위한 정밀 공학 계산서는 부재 유형에 무관하게 **일관된 KDS 공통 7대 챕터 구조**를 엄격히 준수하여 전개됩니다:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ KDS 상세 구조계산서 전 부재 공통 7대 챕터 아키텍처 (7-Chapter Standard)                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • 제 1장. 부재 형상 및 비주얼 단면 배치도 (Geometry & 2D Vector Layout)                         │
│ • 제 2장. 사용 재료 및 설계 기준 계수 (Materials & Design Code Parameters)                       │
│ • 제 3장. 배근율 / 단면제한 / 연성 한계 검토 (Reinforcement Limits & Slenderness/Ductility)      │
│ • 제 4장. 주 강도 상세 산정 (Primary Capacity: Flexure, Compression, Axial-Moment P-M)         │
│ • 제 5장. 부 강도 상세 산정 (Secondary Capacity: Shear, Torsion, Buckling, Connections)         │
│ • 제 6장. 사용성 한계상태 검토 (Serviceability: Deflection, Crack Width, Vibration, Spacing)   │
│ • 제 7장. 종합 안전성 검토 판정표 (Executive DCR Summary Table & Governing Assessment)          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1. 7대 챕터별 수식 전개 표준 규칙 (Calculation Step Structure)
각 장의 세부 수식 단계는 수식 이스케이프 오류와 오버플로우를 차단하기 위해 다음 **4단계 정형 서식**으로 구성됩니다:
1. **설계 규준식 명시**: KDS 기준 조항 번호와 표준 기호 수식 제시 (예: $V_c = \frac{1}{6}\lambda\sqrt{f_{ck}} b_w d$).
2. **실제 변수값 대입식**: 단위 환산 계수를 포함한 실제 수치 대입 과정 노출 (등호(=) 기준 `aligned` 줄바꿈 적용).
3. **최종 계산 결과 및 단위**: 공학 단위($\text{kN, kN}\cdot\text{m, MPa, mm}$)와 소수점 정밀도 포맷팅 적용.
4. **허용치 비교 및 DCR 판정**: $\text{DCR} = \frac{\text{Demand}}{\text{Capacity}}$ 산출 및 $\text{PASS} \ / \ \text{FAIL}$ 뱃지 표기.

*(※ RC 보 1F-B1에 대한 7대장 전 항목의 구체적 KaTeX 전개식 전문은 [`docs/15_rc_beam_specification.md`](15_rc_beam_common_requirements_report.md)에 상세 수록되어 있습니다.)*

---

## 5. 백엔드-프론트엔드 리포트 아키텍처 및 Tracer AST 파이프라인

### 5.1. CalculationTracer AST 구조 (`src/core/tracer.py`)
수식 이스케이프 버그와 HTML 하드코딩을 원천 방지하기 위해, 백엔드 엔진은 구조화된 **AST(Abstract Syntax Tree)**를 생성하고, 프론트엔드가 이를 KaTeX DOM으로 변환합니다:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CalculationTracer AST Pipeline Architecture                                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Engine Layer (`src/engine/`)                                                        │
│    └── CalculationTracer 인스턴스에 단계별 스텝 기록:                                   │
│        tracer.add_step(                                                                │
│            id="phi_Mn", title="설계휨강도 산정",                                       │
│            formula=r"\phi M_n = \phi A_s f_y (d - a/2)",                              │
│            substitute=r"0.85 \times 2026.8 \times 400 \times (536 - 99.35/2) \times 10^{-6}",│
│            result=335.48, unit="kN·m", rule_ref="KDS 14 20 20 (4.1)"                 │
│        )                                                                               │
│                                                                                        │
│ 2. API Serialization Layer (`src/api/`)                                                │
│    └── Pydantic 모델을 통해 JSON Tree 직렬화 전송                                     │
│                                                                                        │
│ 3. Frontend KaTeX Viewer Layer (`src/web/static/js/report/`)                           │
│    ├── `redcr/BeamReportGenerator.js`  : 부재별 특화 DOM 조립                           │
│    ├── `report_common_renderer.js`     : KaTeX 렌더링 및 A4 페이지네이션               │
│    └── `result_renderer.js`            : 실시간 DCR 게이지 및 뱃지 바인딩              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2. 순백색 고정 배경 및 CSS Paged Media 인쇄 규격
화면 브라우저 출력과 관공서 제출용 A4 인쇄물의 1:1 완벽 일치를 보장합니다:
* **순백색 배경 고정**: 테마(다크모드)와 무관하게 계산서 캔버스는 `#ffffff` 배경 및 `#1e293b` 본문 텍스트 강제 적용.
* **CSS Paged Media `@media print` 표준**:
  ```css
  @page {
      size: A4 portrait;
      margin: 15mm 12mm 15mm 12mm;
  }
  .a4-page-break {
      page-break-before: always;
      break-before: page;
  }
  table.chk-table thead {
      display: table-header-group; /* 페이지 넘김 시 테이블 헤더 자동 반복 */
  }
  table.chk-table tr {
      page-break-inside: avoid;    /* 테이블 행 중간 잘림 방지 */
  }
  ```
* **DCR 상태별 표준 컬러 팔레트**:
  - `PASS` ($\text{DCR} \le 1.000$): 딥 그린 (`#1a7a4a`, 배경 `#eafaf1`)
  - `WARN` ($0.950 < \text{DCR} \le 1.000$): 오렌지 앰버 (`#b45309`, 배경 `#fef3c7`)
  - `FAIL` ($\text{DCR} > 1.000$): 크림슨 레드 (`#b00020`, 배경 `#fde8e8`)

---

## 6. 전 부재 도메인별 계산서 필수 수식 인벤토리 (61종 공통 SSOT)

| 부재 도메인 | 핵심 검토 항목 | 주요 KDS 수식 및 검토 파라미터 |
|---|---|---|
| **RC 보** | 3-Station 휨, 전단, 비틀림, 처짐, 균열, 순간격 | $a, c, \epsilon_t, \phi M_n, V_c, V_s, V_{n,\max}, T_{th}, T_{cr}, A_l, A_t/s, I_e, \Delta_{tot}, s_{\max}$ |
| **RC 기둥** | P-M 상관도 곡선, 세장비 좌굴, 횡구속철근 | $P_n, \phi P_{n,\max}, M_{nx}, M_{ny}, e_{\min}, kL/r, \delta_{ns}, \delta_s, s_{tie}, \rho_s$ |
| **RC 전단벽** | 면내전단, 단부 경계요소(SBE), 전도모멘트 | $V_c, V_s, V_{n,\max}, \rho_v, \rho_n, c \ge \frac{l_w}{600(\delta_u/h_w)}, SBE, \phi M_n$ |
| **RC 슬래브** | 직접설계법(DDM), 최소두께, 펀칭전단 | $h_{\min}, M_o = \frac{1}{8} q_u l_2 l_n^2, v_c = \min(0.33\sqrt{f_{ck}}, 0.17(1+2/\beta_c)\sqrt{f_{ck}}, 0.083(\alpha_s d/b_o + 2)\sqrt{f_{ck}})$ |
| **RC 기초/옹벽** | 편심 접지압, 2방향 전단, 전도/활동 안전율 | $q_{\max} = \frac{P}{A}(1 \pm \frac{6e}{B}) \le q_a, V_c(\text{punching}), FS_{over} \ge 2.0, FS_{slide} \ge 1.5$ |
| **Steel 보/기둥** | 폭두께비, 횡지지 좌굴, 휨-압축 P-M | $\lambda \le \lambda_p \le \lambda_r, L_b \le L_p \le L_r, F_{cr}, \frac{P_u}{\phi P_n} + \frac{8}{9}(\frac{M_{ux}}{\phi M_{nx}} + \frac{M_{uy}}{\phi M_{ny}}) \le 1.0$ |
| **접합부/주각부** | 고장력볼트 전단/지압, 필릿용접, 베이스플레이트 | $R_n(\text{shear/bearing}), R_n(\text{block shear}), F_w = 0.60 F_{EXX}, t_p = l \sqrt{\frac{2 P_u}{0.9 F_y B N}}$ |

---

## 7. 결론 및 리포트 엔진 개발 가이드라인

1. **단일 진실 공급원(SSOT) 원칙**:
   - 본 문서에 정의된 수식 체계와 기호, 챕터 구성은 백엔드 Jinja2 템플릿(`src/report/templates/`), 익스포터(`excel_exporter.py`, `pdf_exporter.py`), 프론트엔드 자바스크립트 렌더러(`BeamReportGenerator.js`, `ColumnCheckReportGenerator.js`) 전역에서 100% 동일하게 유지됩니다.
2. **플랫폼 정렬 및 신규 부재 확장**:
   - 향후 개발되는 벽체, 슬래브, 기초, 철골 부재는 RC 보와 RC 기둥에서 검증된 **"7대장 챕터 구조"**, **"3-Station 또는 다중 위치 평가"**, **"0 하중 시 최소배근 방어"**, **"Tracer AST KaTeX 렌더링"** 규칙을 공통 표준으로 그대로 상속하여 구현합니다.
