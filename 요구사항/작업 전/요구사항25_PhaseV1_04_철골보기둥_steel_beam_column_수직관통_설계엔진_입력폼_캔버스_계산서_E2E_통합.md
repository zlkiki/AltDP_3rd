# 요구사항 25: Phase V1-4 철골 보/기둥 (steel_beam_column) 5대 공정 수직 관통 마스터 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](../docs/12_full_feature_porting_master_plan.md)**의 Phase V1(Tier 1 플래그십 5대 핵심 부재) 중 네 번째 모듈인 **철골 보/기둥 (`steel_beam_column`)**을 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 마스터 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_beam_column` (카탈로그 번호 No. 22, Tier 1 플래그십)
* **담당 핵심 파일**:
  - 엔진 & 스키마: [`src/engine/steel/beam.py`](../src/engine/steel/beam.py), [`src/engine/steel/column.py`](../src/engine/steel/column.py), [`src/engine/steel/compactness.py`](../src/engine/steel/compactness.py), [`src/api/routes/steel.py`](../src/api/routes/steel.py)
  - 입력폼 컴포넌트: `src/web/static/js/components/form_steel_beam_column.js`, `src/web/static/js/components/member_manager.js`
  - 그래픽 뷰포트: `src/web/static/js/visual/vector_steel_beam_column.js`, `src/web/static/js/visual/vector/vector_steel.js`
  - 구조계산서 렌더러: `src/web/static/js/report/redcr/SteelReportGenerator.js`, `src/web/static/js/report/redcr_steel_beam_column.js`
  - 통합 및 디스패처: `src/web/static/js/core/dispatcher.js`, `src/web/static/js/catalog.js`
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` C루틴 심볼 (`steel__CHK_USMC_*.c`, `DPLUS_STEEL.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 Steel Beam-Column 편 (`IDD_STL_BEAMCOLUMN_INPUT_DLG`, `IDD_STL_BEAMCOL_*`)
  3. `[3순위 학회 예제집]`: 한국강구조학회·한국건축구조기술사회 『KDS 41 31 00 : 2019에 따른 강구조설계 예제집』 (오류 시 Patch-First 선 치유 원칙)
     - 제5장 압축재: `예제 5.1`, `예제 5.2` (H형강 휨좌굴강도, 유효좌굴길이 및 세장비 산정)
     - 제6장 휨재: `예제 6.1`, `예제 6.2` (H형강 강축휨, 횡지지 $L_b \le L_p$ 및 비지지 횡비틀림좌굴 LTB 강도)
     - 제7장 전단재: `예제 7.1` (웨브 전단좌굴계수 $C_v$ 및 공칭전단강도 $V_n$)
     - 제8장 조합력: `예제 8.1`, `예제 8.2` (축력과 이축휨을 받는 H형강 보-기둥 P-M 상관비 H1-1a / H1-1b)
  4. `[4순위 국가건설기준]`: (오류 시 Patch-First 선 치유 원칙)
     - `KDS 14 31 10`: 강구조부재 설계기준 (한계상태설계법 - 4.1 인장재, 4.2 휨재, 4.3 압축재, 4.4 전단재, 4.5 조합력과 비틀림 부재)

---

## 2. docs/07 제21절 기반 UI/UX 선행 검토 체크리스트

[`docs/07_web_application_ui_ux_specification.md 제21절`](../docs/07_web_application_ui_ux_specification.md)의 6대 필수 검토 항목을 충실히 반영하여 프론트엔드 연동 사양을 사전 확립합니다:

1. **[사이드바 & 카테고리 정합성]**:
   - 8대 카테고리 Pills 탭 중 `[Steel 강구조]` 그룹에 속하며, 영문 키 `steel_beam_column`, 한글 명칭 "철골 보/기둥".
   - 3단계 WorkTree(`Steel 강구조 > 골조부재 > 철골 보/기둥`) 및 즐겨찾기(⭐) 지원.
2. **[Pane 1 부재 매니저 요약 테이블]**:
   - 핵심 요약 컬럼: 부재 ID, 형강 호칭 규격(예: `H-400x200x8x13`), 부재 길이($L$), 횡지지길이($L_b$), 지배 계수축력($P_u$), 강축휨($M_{ux}$), 종합 P-M DCR, 판정 배지(`OK`/`NG`).
3. **[Pane 2 모듈 주도형 서브탭 & 원본 1:1 서브 모달]**:
   - 원본 `IDD_STL_BEAMCOLUMN_INPUT_DLG` 기반 모듈 주도형 서브탭 정의 (단면/재료, 부재길이/지지, 설계계수, 설계부재력). 통일된 공학 테마와 UX 공유.
   - 패널 폭 리사이즈 드래그 시 컨트롤 찌그러짐 방지: **패널 최소너비 `min-width: 320px`, 컨트롤 최소너비 `110px`, `auto-fit/minmax` 반응형 래핑 및 `overflow-x: auto` 방어**.
   - 서브 대화창(`...`) 모달 3종: `[KS 표준 형강 DB 모달]`, `[모멘트구배계수 Cb 계산기 모달]`, `[하중조합 포락 모달]`.
   - 3버튼 통합 액션 파이프라인 (`[💾 적용] [⚡ 검토] [✨ 자동설계]`) - 적용은 메모리/캔버스만, 검토 시에만 백엔드 KDS 계산서 갱신.
   - 다크/라이트 테마 무결성 (`var(--bg-...)`, `var(--text-...)`, `var(--border)`) 및 components.css 엔지니어링 폼 표준 준수.
4. **[Pane 3 동적 가변 1~3단 세로 적층형 그래픽 뷰포트]**:
   - `GraphicViewport.setStationCount(2)` 기반 동적 세로 다중 카드 스택.
   - **[1단 뷰포트: 원본앱 참조 타이틀 `H형강 상세 단면도`]**: H/Box 형강 상세 단면도, 필릿 라운딩($r$), 치수선($H, B, t_w, t_f$), 도심축($x-x, y-y$), 단면 특성치, 판폭두께비(조밀/비조밀/세장) 색상 코딩.
   - **[2단 뷰포트: 원본앱 참조 타이틀 `부재 입면 및 모멘트 구배도`]**: 부재 전장 입면도, 횡지지($L_b$) 구간도, 모멘트 다이어그램($M_x, M_y$) 및 횡비틀림 좌굴 모드 형상 오버레이.
   - 잔존 임시 모듈 완전 배제 및 독립 줌/팬/Fit 및 호버 툴팁.
5. **[Pane 4 순백색 A4 8단계 KaTeX 구조계산서 (`report_engine.js` 단일화)]**:
   - 상시 순백색(`#ffffff`) 고정 A4 용지 레이아웃 (`report_engine.js`로 단일화, 구형 렌더러 완전 제거).
   - 사용자 입력부의 [⚡ 검토], [✨ 자동설계] 클릭 시 정식 KaTeX 계산서가 즉시 출력되도록 파이프라인 단일화.
   - 상세/요약 라디오 분기 및 `[☑ 사용자 입력 데이터 상세 포함]` 토글.
   - 5대 장구분 및 8단계 KaTeX 판폭두께비, LTB 휨강도, 압축좌굴, P-M 상호작용 수식 전개.
   - 원본 고유 `  →  O.K / N.G` 판정 화살표.
   - [🖨️ 인쇄] 및 [📊 Excel 내보내기] 연동 (불필요한 PDF 버튼 전면 제거).
6. **[인터랙티브 반응성 및 성능]**:
   - 폼 입력 시 캔버스 즉시 동기화, `[⚡ 검토]` 클릭 시 100ms 이내 순백색 A4 계산서 및 DCR 안전율 갱신.

---

## 3. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase V1-4 철골 보/기둥 (steel_beam_column) 5대 마이크로 공정 파이프라인                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Step 1: KDS 계산엔진]  ──► [Step 2: 1:1 서브탭폼] ──► [Step 3: 2D 캔버스] ──► [Step 4: A4 계산서] ──► [Step 5: E2E 통합] │
│ (Pydantic / 0.1% TDD)       (4대 서브탭 & 모달)       (세로적층 2단 뷰포트)     (순백색 A4 8단계 KaTeX)   (100ms 동기화/WIP해제)│
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/steel/beam.py`, `column.py`, `src/api/routes/steel.py`)
* **Pydantic v2 데이터 스키마 구축**:
  - `SteelSection`: 단면 타입(H형강, 각형강관, 원형강관 등), 호칭규격(KS D 3502 DB 연동), 치수($H, B, t_w, t_f, r$), 단면 기하특성치($A, I_x, I_y, Z_x, Z_y, S_x, S_y, r_x, r_y, J, C_w$).
  - `SteelMemberGeometry`: 부재 길이($L$), 강축/약축 유효좌굴길이계수($K_x, K_y, K_z$), 횡비지지길이($L_b$).
  - `SteelDesignCoefficients`: 모멘트 구배계수($C_b$), 모멘트 확대계수($B_1, B_2, C_m$).
  - `SteelLoads`: 계수축력($P_u$, 인장/압축), 강축/약축 계수모멘트($M_{ux}, M_{uy}$), 계수전단력($V_{ux}, V_{uy}$).
  - `SteelBeamColumnResult`: 판폭두께비 조밀/비조밀/세장 판정($\lambda, \lambda_p, \lambda_r$), 휨강도($\phi_b M_{nx}, \phi_b M_{ny}$, LTB 좌굴강도), 압축강도($\phi_c P_n$, Euler $F_e$, 임계응력 $F_{cr}$), 인장강도($\phi_t P_n$), 전단강도($\phi_v V_n$), P-M 축휨 상호작용 DCR(H1-1a / H1-1b) 및 종합 판정(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - **판폭두께비(KDS 14 31 10 표 4.1-1, 4.1-2)**:
    * H형강 플랜지: $\lambda = \frac{B}{2 t_f}$, $\lambda_p = 0.38 \sqrt{E/F_y}$, $\lambda_r = 1.0 \sqrt{E/F_y}$ (휨재)
    * H형강 웨브(휨): $\lambda = \frac{h}{t_w}$, $\lambda_p = 3.76 \sqrt{E/F_y}$, $\lambda_r = 5.70 \sqrt{E/F_y}$
    * 축압축재: 플랜지 $\lambda_r = 0.56 \sqrt{E/F_y}$, 웨브 $\lambda_r = 1.49 \sqrt{E/F_y}$
  - **휨강도 및 횡비틀림좌굴(LTB, KDS 14 31 10 4.2)**:
    * 소성모멘트: $M_p = F_y Z_x$
    * 한계 비지지길이: $L_p = 1.76 r_y \sqrt{E/F_y}$
    * 비탄성 LTB 한계: $L_r = 1.95 r_{ts} \frac{E}{0.7 F_y} \sqrt{\frac{J c}{S_x h_0} + \sqrt{\left(\frac{J c}{S_x h_0}\right)^2 + 6.76\left(\frac{0.7 F_y}{E}\right)^2}}$
    * 공칭휨강도 $M_n$:
      - $L_b \le L_p \implies M_n = M_p$
      - $L_p < L_b \le L_r \implies M_n = C_b \left[ M_p - (M_p - 0.7 F_y S_x)\left(\frac{L_b - L_p}{L_r - L_p}\right) \right] \le M_p$
      - $L_b > L_r \implies M_n = F_{cr} S_x \le M_p$
  - **압축좌굴강도(KDS 14 31 10 4.3)**:
    * 세장비 $\frac{KL}{r} = \max\left(\frac{K_x L_x}{r_x}, \frac{K_y L_y}{r_y}\right) \le 200$
    * 오일러 탄성좌굴응력: $F_e = \frac{\pi^2 E}{(KL/r)^2}$
    * 임계좌굴응력:
      - $\frac{KL}{r} \le 4.71 \sqrt{\frac{E}{F_y}} \left(\frac{F_y}{F_e} \le 2.25\right) \implies F_{cr} = \left[0.658^{\frac{F_y}{F_e}}\right] F_y$
      - $\frac{KL}{r} > 4.71 \sqrt{\frac{E}{F_y}} \left(\frac{F_y}{F_e} > 2.25\right) \implies F_{cr} = 0.877 F_e$
    * 설계압축강도: $\phi_c P_n = 0.90 F_{cr} A_g$ (세장판단면 시 유효단면적 $A_e$ 적용)
  - **전단강도(KDS 14 31 10 4.4)**:
    * $V_n = 0.6 F_y A_w C_v$, $\phi_v = 0.90$ (또는 $1.00$)
  - **조합력 상호작용식(KDS 14 31 10 식 4.5-1, 4.5-2)**:
    * $\frac{P_u}{\phi_c P_n} \ge 0.2 \implies \frac{P_u}{\phi_c P_n} + \frac{8}{9}\left(\frac{M_{ux}}{\phi_b M_{nx}} + \frac{M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$
    * $\frac{P_u}{\phi_c P_n} < 0.2 \implies \frac{P_u}{2 \phi_c P_n} + \left(\frac{M_{ux}}{\phi_b M_{nx}} + \frac{M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$
* **DoD 검증**: 강구조설계예제집 5.1(압축), 6.1(휨/LTB), 7.1(전단), 8.1(보-기둥 P-M) 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_beam.py`, `test_steel_column.py` 100% PASS).

### Step 2: 원본앱 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_steel_beam_column.js`)
* **원본앱 `IDD_STL_BEAMCOLUMN_INPUT_DLG` 1:1 계승 4대 서브탭 구성**:
  - **Tab 1 [단면/재료]**: 강종 콤보(`SS275`, `SM355`, `SM460` 등), 단면 형태(H형강, 각형강관, 원형강관), 단면 치수 입력 필드 및 `[단면 DB...]` 버튼.
  - **Tab 2 [부재길이/지지]**: 부재 전장($L$), 강축/약축 좌굴길이계수($K_x, K_y$), 횡비지지길이($L_b$), 단부 회전구속조건.
  - **Tab 3 [설계계수]**: 모멘트 구배계수($C_b$, 직접입력 또는 쿼터 모멘트 자동계산), 2차 모멘트 확대계수($B_1, B_2$), 모멘트 등가계수($C_{mx}, C_{my}$).
  - **Tab 4 [설계부재력]**: 지배 하중조합 및 부재력($P_u, M_{ux}, M_{uy}, V_{ux}, V_{uy}$), 다중 하중 케이스 포락 그리드.
* **원본앱 3대 액션 버튼 툴바**:
  - `[💾 적용]`: 메모리 저장 및 캔버스 단면도 치수만 동기화 (**계산서는 실시간 갱신 차단**).
  - `[⚡ 검토]`: 선행 적용 후 KDS 백엔드 검토 실행 및 순백색 A4 계산서/DCR 갱신.
  - `[✨ 자동설계]`: 현재 하중 조건에 적합한 최적 최소중량 KS H형강 경제단면 자동 탐색 및 주입.
* **상세 대화창(`...`) 서브 모달 3종**:
  - `[KS 표준 형강 DB 모달]`: H형강, 각형강관 규격 검색, 필터링 및 단면성질 1클릭 바인딩.
  - `[모멘트구배계수 Cb 계산기 모달]`: 보의 단부 모멘트비 및 횡하중 재하 형태별 $C_b$ 대화형 산출기.
  - `[하중조합 포락 모달]`: 풍하중/지진하중 등 다축 조합력 그리드 관리.
* **UI/UX 무결성**: 서브탭 래핑(`.sub-tab-bar` `flex-wrap: wrap;`), 테마 변수(`var(--bg-...)`), components.css 엔지니어링 폼 표준 준수.
* **DoD 검증**: 브라우저 DOM 렌더링 정상, 폼 변경 시 이벤트 전파 및 유효성 검사, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_steel_beam_column.js`)
* **원본앱 VDraw 강재 그래픽스 알고리즘 이식 (세로 적층형 2단 뷰포트)**:
  - **상단 뷰포트 (부재 입면 및 좌굴 거동도)**:
    * 부재 전장($L$) 입면 및 핀/고정 지지조건 기호.
    * 횡지지점($L_b$) 및 가새 위치 삼각형 기호 마킹.
    * 모멘트 다이어그램($M_{ux}, M_{uy}$) 및 횡비틀림 좌굴 모드 곡선 오버레이.
  - **하단 뷰포트 (H/Box 형강 정밀 단면도)**:
    * 플랜지/웨브 정밀 외곽선 및 필릿 곡률($r$) 렌더링.
    * 치수선($H, B, t_w, t_f$), 도심축($x-x, y-y$) 일점쇄선.
    * 단면 기하특성치($A, I_x, I_y, Z_x, Z_y$) 오버레이 배지.
    * 국부좌굴(플랜지/웨브) 조밀/비조밀/세장 판정 상태별 색상 강조.
* **인터랙션 기능**: 마우스 휠 줌/팬, Fit, 단면 요소 호버 시 치수 및 국부좌굴 여유도 툴팁.
* **DoD 검증**: Canvas 그래픽스 정확 렌더링, 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_steel_beam_column.js`)
* **원본앱 5대 장구분 계승**:
  - **1. 설계 개요 및 형강 단면 제원**: 강종, 기준강도($F_y, F_u$), 표준 단면 호칭, 단면 기하계수($A, I, Z, S, r, J, C_w$).
  - **2. 단면 조밀성 판정 (Width-to-Thickness Ratio)**: 플랜지/웨브 폭두께비 KaTeX 산정 $\rightarrow$ 조밀/비조밀/세장 판정 $\rightarrow$ `  →  O.K`.
  - **3. 휨강도 검토 (Flexural Strength)**: $M_p = F_y Z_x \rightarrow L_b$ vs $L_p, L_r \rightarrow \text{LTB 좌굴강도 } M_n \rightarrow \phi_b M_n$ $\rightarrow$ $\text{DCR} \le 1.000$ $\rightarrow$ `  →  O.K / N.G`.
  - **4. 압축/인장강도 검토 (Axial Strength)**: 세장비 $KL/r \le 200 \rightarrow \text{Euler } F_e \rightarrow \text{임계좌굴응력 } F_{cr} \rightarrow \phi_c P_n$ $\rightarrow$ $\text{DCR} \le 1.000$ $\rightarrow$ `  →  O.K / N.G`.
  - **5. 조합력 상호작용 검토 (P-M Interaction)**: H1-1a / H1-1b KaTeX 수식 전개 $\rightarrow$ $\text{DCR} \le 1.000$ $\rightarrow$ `  →  O.K / N.G`.
* **DoD 검증**: A4 인쇄 프리뷰 레이아웃, KaTeX 수식 무결성 확인.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**: 폼 입력 시 단면도 그래픽 즉시 동기화, `[⚡ 검토]` 클릭 시 100ms 이내 계산서 및 P-M DCR 안전율 갱신.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `steel_beam_column`의 `is_wip: false`로 정식 온라인 전환.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건.

---

## 4. 세부 하위 구현계획서 구조 (Sub-Specifications)

본 마스터 요구사항 25는 5대 정밀 공정에 따라 아래 5개의 독립 세부 구현계획서로 분할되어 체계적으로 실행됩니다:

1. **[`요구사항25-1_PhaseV1_04_Step1_철골보기둥_KDS계산엔진_및_Pydantic스키마.md`](요구사항25-1_PhaseV1_04_Step1_철골보기둥_KDS계산엔진_및_Pydantic스키마.md)**
   - KDS 14 31 10 조밀성·LTB·좌굴·전단·P-M 순수 파이썬 정밀 수식
   - Pydantic v2 데이터 입출력 스키마 체계
   - 강구조설계예제집 5.1/6.1/7.1/8.1 3자 삼각대조 및 Pytest TDD
2. **[`요구사항25-2_PhaseV1_04_Step2_철골보기둥_원본앱_1대1_서브탭_입력폼_및_모달.md`](요구사항25-2_PhaseV1_04_Step2_철골보기둥_원본앱_1대1_서브탭_입력폼_및_모달.md)**
   - Pane 1 다중 부재 매니저 요약 테이블 그리드
   - Pane 2 원본앱 `IDD_STL_BEAMCOLUMN_INPUT_DLG` 1:1 계승 4대 서브탭 폼
   - 형강 DB 모달, Cb 계산기 모달, 하중조합 모달 연동
3. **[`요구사항25-3_PhaseV1_04_Step3_철골보기둥_2D_VDraw_캔버스_단면도_및_부재력도_인터랙션.md`](요구사항25-3_PhaseV1_04_Step3_철골보기둥_2D_VDraw_캔버스_단면도_및_부재력도_인터랙션.md)**
   - Pane 3 세로 적층형 2단 그래픽 뷰포트
   - 상단: 부재 입면, 지지/횡구속, 모멘트도, LTB 좌굴형상
   - 하단: H/Box 형강 정밀 단면, 필릿 곡률, 치수선, 조밀성 하이라이트
4. **[`요구사항25-4_PhaseV1_04_Step4_철골보기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md`](요구사항25-4_PhaseV1_04_Step4_철골보기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md)**
   - Pane 4 상시 순백색(`#ffffff`) A4 고정 구조계산서
   - 원본 5대 장구분 및 8단계 KaTeX 수식 유도 (LTB, 오일러, P-M 상호작용)
   - 상세/요약 분기, 인쇄/PDF/Excel 익스포트
5. **[`요구사항25-5_PhaseV1_04_Step5_철골보기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md`](요구사항25-5_PhaseV1_04_Step5_철골보기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md)**
   - 4-Pane 워크스페이스 100ms 실시간 동시 동기화 검증
   - `catalog.js` 및 메타데이터 WIP 해제 (`is_wip: false`)
   - E2E 전수 통합 테스트 및 콘솔 에러 0건 검증

---

## 5. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 강구조설계예제집(2019) 5.1(압축), 6.1(휨/LTB), 7.1(전단), 8.1(보-기둥 P-M) 대비 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_*.py` 100% PASS).
- [ ] **1:1 입력폼**: 원본앱 `IDD_STL_BEAMCOLUMN_INPUT_DLG` 4대 서브탭, 3대 액션 버튼(`[💾적용] [⚡검토] [✨자동설계]`), 서브탭 래핑 및 테마 무결성 브라우저 렌더링 확인.
- [ ] **2D 캔버스**: 세로 적층 2단 뷰포트(부재 입면/모멘트도 + 형강 상세 단면/치수선) 렌더링 확인.
- [ ] **A4 계산서**: 5대 장구분 8단계 KaTeX 판폭두께비, LTB, 압축좌굴, P-M 상호작용 수식 출력 확인.
- [ ] **4열 통합**: 폼 입력 시 캔버스 동기화, [⚡ 검토] 시 100ms 이내 계산서 갱신 및 브라우저 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16` 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
