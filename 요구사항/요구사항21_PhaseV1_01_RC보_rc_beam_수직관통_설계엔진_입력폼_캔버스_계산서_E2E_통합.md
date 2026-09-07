# 요구사항 21: Phase V1-1 RC 보 (rc_beam) 5대 공정 수직 관통 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**의 최우선 과제인 **Phase V1 (Tier 1 플래그십 5대 핵심 부재)** 중 첫 번째 모듈인 **RC 보 (`rc_beam`)**를 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 상세 요구사항 명세서입니다.

* **모듈 식별자**: `rc_beam` (카탈로그 번호 No. 1)
* **국가건설기준 (4순위)**: KDS 14 20 10 (일반/재료), KDS 14 20 20 (휨), KDS 14 20 22 (전단/비틀림), KDS 14 20 30 (사용성)
* **공식 학회 예제집 (3순위)**: 콘크리트구조학회(2020) 예제집 `3.1 단철근/복철근 휨`, `4.1 전단설계`, `4.3 비틀림`, `6.1 처짐`
* **원본 DLG 리소스 (2순위)**: `IDD_RCS_BEAM_PMODE_DLG`, `IDD_RCS_DEFL_DLG`, `IDD_RCS_BEAM_REBAR_DLG`
* **원본 추출 C 루틴 (1순위)**: `rc__CHK_BBBE_*.c` (`decompiled_src/core_routines/rc/CHK_BBBE_beam.c`), `DPLUS_RCS.dll`

---

## 2. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/rc/beam.py`)
* **Pydantic 데이터 스키마 구축**:
  - `RCBeamSection`: 폭($b$), 높이($h$), 유효경간($L$), 피복두께($d_c, d_c'$), $f_{ck}$, $f_y$, $f_{yt}$.
  - `RCBeamRebar`: 상부 주근(다단 배열), 하부 주근(다단 배열), 전단 스터럽(지름, 다리수, 간격 $s$), 비틀림 종방향 철근($A_l$).
  - `RCBeamLoads`: 계수휨모멘트($M_u$), 계수전단력($V_u$), 계수비틀림모멘트($T_u$), 사용하중 휨모멘트($M_a, M_{sus}$).
  - `RCBeamResult`: $\phi M_n$, $\phi V_n$, $\phi T_n$, Branson 유효단면2차모멘트($I_e$), 즉시처짐($\Delta_i$), 장기처짐 증폭($\lambda_\Delta$), 직접 균열폭($w$), 각 한계상태별 DCR 및 2단계 상태(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - 등가직사각형 압축응력블록 깊이 $a = \frac{A_s f_y - A_s' f_s'}{\alpha_1 f_{ck} b}$, 중립축 $c = a / \beta_1$ 수렴 해석.
  - 강도감소계수 $\phi$: 인장지배($\epsilon_t \ge 0.005 \implies \phi = 0.85$), 압축지배($\epsilon_t \le \epsilon_y \implies \phi = 0.65$), 전이구간 선형 보간.
  - 콘크리트 전단강도 $V_c = \frac{1}{6} \lambda \sqrt{f_{ck}} b_w d$, 전단철근 $V_s = \frac{A_v f_{yt} d}{s} \le \frac{2}{3} \sqrt{f_{ck}} b_w d$.
  - 비틀림 검토: $T_{th} = 0.0625 \lambda \sqrt{f_{ck}} \left(\frac{A_{cp}^2}{p_{cp}}\right)$, 초과 시 전단-비틀림 상호작용 및 종방향 추가철근 $A_l$ 산정.
  - 사용성: Branson 유효단면2차모멘트 $I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr}$, 시간경과계수 $\xi = 2.0$ (5년 이상).
* **DoD 검증**: 콘크리트학회 예제집 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_rc_beam.py` 100% PASS).

### Step 2: Midas 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_rc_beam.js`)
* **Midas 원본 `IDD_RCS_BEAM_PMODE_DLG` 1:1 계승 4대 서브탭 구성**:
  - **Tab 1 [단면/재료]**: 보 단면 치수($b \times h$), 콘크리트 강도($f_{ck}$ 콤보박스 C24~C60), 철근 강도($f_y, f_{yt}$ SD400/SD500/SD600), 환경 피복두께.
  - **Tab 2 [철근배근]**: 상/하부 단부(End-I, End-J) 및 중앙부(Center-M) 다단 주철근 배열 테이블 (직경, 개수), 전단 스터럽(주경간/단부 간격 $s$).
  - **Tab 3 [설계모멘트/전단]**: 부재력 입력 테이블 ($M_u^+, M_u^-, V_u, T_u$) 및 LCB 다축 하중 포락 연동.
  - **Tab 4 [사용성/처짐]**: 보 지지조건(단순지지/양단연속/일단연속/캔틸레버), 활하중 비율, 허용 처짐 한계 ($L/240, L/480$).
* **상세 대화창(`...`) 서브 모달**:
  - `[철근 상세 배근 설정 모달]`: 갈고리 여부(90°/135°/180°), 스터럽 다리수(2각/4각), 철근 순간격 및 조립철근 설정.
  - `[단면 형상 선택 모달]`: 직사각형, T형 보(유효플랜지폭 $b_e$ 자동 산정) 선택기.
* **DoD 검증**: 브라우저 DOM 렌더링 정상 확인, 폼 변경 시 이벤트 전파 및 유효성 검사, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_rc_beam.js`)
* **Midas VDraw 드로잉 알고리즘 완벽 이식**:
  - **상단 뷰포트 (종단면 배근도 & 부재력도)**: 보 스팬 길이($L$), 단부 및 중앙부 배근 영역 구분선, 상/하부 주철근 지시선, 휨모멘트도($M$) 및 전단력도($V$) 포락선 오버레이.
  - **하단 뷰포트 (횡단면도 & 상세 배근)**: 단부(I/J) 및 중앙(M) 보 횡단면, 콘크리트 단면 외곽선, 135° 내진 갈고리 폐합 스터럽 렌더링, 상/하부 1단/2단 주철근 원형 솔리드 심볼, 유효 피복두께 옵셋선, 치수선(b, h, d, d') 및 철근 규격 태그(예: `4-D25 (2단: 2-D25)`).
* **인터랙션 기능**: 마우스 휠 줌, 드래그 팬, 더블클릭 화면맞춤(Fit-to-Screen), 마우스 호버 시 철근 직경/간격 하이라이트 툴팁.
* **DoD 검증**: Canvas 그래픽스 왜곡 없는 렌더링, 치수선 일치, 브라우저 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_rc_beam.js`)
* **Midas 원본 `DgnReportBase.ini` 5대 장구분 완벽 계승**:
  - **1. 설계 개요 및 단면 제원 (Design Information)**: 프로젝트명, 부재명, 재료 강도($f_{ck}, f_y$), 단면 형상 치수, 단면 유효단면적.
  - **2. 설계 부재력 및 하중조합 (Design Factored Loads)**: 계수 모멘트($M_u$), 계수 전단력($V_u$), 계수 비틀림($T_u$), 지배 하중조합.
  - **3. 휨모멘트 강도 검토 (Flexural Strength Check)**: 8단계 KaTeX 수식 전개식 (중립축 $c$ 유도 $\rightarrow$ 철근 변형률 $\epsilon_t$ $\rightarrow$ $\phi$ 산정 $\rightarrow$ $\phi M_n$ 유도 $\rightarrow$ $\text{DCR} = M_u / \phi M_n$ $\rightarrow$ `  →  O.K / N.G` 판정).
  - **4. 전단 및 비틀림 강도 검토 (Shear & Torsion Check)**: $V_c$ 산정식 $\rightarrow$ $V_s$ 산정식 $\rightarrow$ $\phi V_n$ 유도 $\rightarrow$ 비틀림 균열/상호작용 검토 $\rightarrow$ `  →  O.K / N.G` 판정.
  - **5. 사용성 한계상태 검토 (Serviceability Check)**: Branson 식 $I_e$ 전개 $\rightarrow$ 단기/장기 처짐합 $\Delta_{total}$ vs 허용값 $\Delta_{allow}$ $\rightarrow$ 직접 균열폭 $w$ vs $w_{lim}$ $\rightarrow$ `  →  O.K / N.G` 판정.
* **계산서 출력 기능**: 상시 순백색(`#ffffff`) A4 프리뷰, 인쇄 다이얼로그 연동, PDF/Excel 내보내기, 상세/요약 모드 스위칭.
* **DoD 검증**: KaTeX 수식 렌더링 깨짐 0건, 인쇄 프리뷰 시 여백 및 페이지 분할 정렬 완료.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**:
  - 1열(트리)에서 `RC 보` 선택 $\rightarrow$ 2열(입력폼)에 파라미터 로딩 $\rightarrow$ 3열(캔버스)에 단면/배근도 즉시 렌더링 $\rightarrow$ 4열(계산서)에 KaTeX 계산서 실시간 생성.
  - 2열 입력폼에서 철근 개수나 단면 치수를 수정하면 **100ms 이내에 3열 캔버스와 4열 계산서, 1열 DCR 상태(OK/NG)가 지연 없이 동시 갱신**.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `rc_beam`의 `is_wip: false`로 정식 온라인 전환.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건, 브라우저 실사용 시각 확인.

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 콘크리트학회 예제집 3.1, 4.1 대비 휨/전단 강도 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_rc_beam.py` 통과).
- [ ] **1:1 입력폼**: Midas 원본 `IDD_RCS_BEAM_PMODE_DLG`의 4대 서브탭 및 모달 브라우저 렌더링 검증 완료.
- [ ] **2D 캔버스**: 135° 절곡 갈고리, 피복두께 옵셋선, 치수선, 철근 태그 렌더링 검증.
- [ ] **A4 계산서**: 5대 장구분 및 8단계 KaTeX 수식 전개, `  →  O.K / N.G` 판정 화살표, A4 인쇄 프리뷰 레이아웃 확인.
- [ ] **4열 통합**: 파라미터 입력 시 100ms 이내 3-View 실시간 동기화 및 브라우저 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16`에 따른 4대 물리적 증거(원본 발췌, 3자 오차표, raw 로그, git diff) 첨부 및 1단위 Git 커밋/푸시 완료.
