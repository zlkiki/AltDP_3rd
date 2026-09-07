# 요구사항 24: Phase V1-3 RC 전단벽 (rc_shear_wall) 5대 공정 수직 관통 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**의 Phase V1(Tier 1 플래그십 5대 핵심 부재) 중 세 번째 모듈인 **RC 전단벽 (`rc_shear_wall`)**을 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 상세 요구사항 명세서입니다.

* **모듈 식별자**: `rc_shear_wall` (카탈로그 번호 No. 4)
* **국가건설기준 (4순위)**: KDS 14 20 10 (재료), KDS 14 20 20 (축력/휨), KDS 14 20 40 (내진설계 및 구조벽체)
* **공식 학회 예제집 (3순위)**: 콘크리트구조학회(2020) 예제집 `9.1 일반 전단벽 휨/전단설계`, `9.2 특수철근콘크리트 구조벽체 경계요소 설계`
* **원본 DLG 리소스 (2순위)**: `IDD_RCS_WALL_PMODE_DLG`, `IDD_RCS_BATCHWALL_*`
* **원본 추출 C 루틴 (1순위)**: `rc__CHK_BWUW_*.c`, `DPLUS_RCS.dll`

---

## 2. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/rc/wall.py`)
* **Pydantic 데이터 스키마 구축**:
  - `RCWallSection`: 벽체 두께($t_w$), 길이($l_w$), 층고($h_w$), 피복두께, $f_{ck}, f_y, f_{yt}$.
  - `RCWallRebar`: 복배근/단배근 구분, 수직 철근($\rho_v$, 간격 $s_v$), 수평 전단철근($\rho_h$, 간격 $s_h$), 양단부 경계요소 주철근 및 띠철근.
  - `RCWallLoads`: 계수축력($P_u$), 계수전단력($V_u$), 면내 계수모멘트($M_u$).
  - `RCWallResult`: 전단강도($V_c, V_s, \phi V_n$), 면내 휨-축력 P-M 내력, 특수경계요소(SBE) 필요성 판정(응력 기반 변위 기반), 경계요소 길이($c - 0.1 l_w$ 등), 횡보강근량($A_{sh}$), DCR 및 판정(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - 전단강도(KDS 14 20 40): $V_c = \min\left[ 0.28 \lambda \sqrt{f_{ck}} t_w d + \frac{N_u d}{4 l_w}, \; \left(0.05 \lambda \sqrt{f_{ck}} + \frac{l_w (0.1 \lambda \sqrt{f_{ck}} + 0.2 N_u / (l_w t_w))}{M_u / V_u - l_w / 2}\right) t_w d \right]$.
  - 전단 상한 검토: $V_n \le \frac{5}{6} \sqrt{f_{ck}} t_w d$.
  - 특수경계요소(SBE) 판정: 변위기반 응력집중 판정 $c \ge \frac{l_w}{600 (\delta_u / h_w)}$, 최대 압축응력 $\sigma \ge 0.2 f_{ck}$ 검토.
* **DoD 검증**: 콘크리트학회 예제집 9.1 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_rc_wall.py` 100% PASS).

### Step 2: 원본앱 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_rc_wall.js`)
* **원본앱 `IDD_RCS_WALL_PMODE_DLG` 1:1 계승 서브탭 구성**:
  - **Tab 1 [단면/재료]**: 벽체 두께($t_w$), 전단벽 길이($l_w$), 층고($h_w$), 콘크리트($f_{ck}$), 철근($f_y$).
  - **Tab 2 [철근배근]**: 복배근(2단)/단배근(1단), 수평근/수직근 규격(D10~D16) 및 간격, 단부 단속근 설정.
  - **Tab 3 [경계요소]**: 양단부 경계부재 폭/길이, 경계요소 집중 수직근(예: `6-D22`), 구속 띠철근 간격.
  - **Tab 4 [설계부재력]**: 축하중($P_u$), 면내 휨모멘트($M_u$), 면내 전단력($V_u$), 내진등급(특수/보통 전단벽).
* **상세 대화창(`...`) 서브 모달**:
  - `[특수경계요소 상세 모달]`: 설계변위($\delta_u$), 소성힌지 길이, 횡보강근 다리수 및 간격 산정기.
* **DoD 검증**: 브라우저 DOM 렌더링 정상, 폼 변경 시 이벤트 전파 및 유효성 검사, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_rc_wall.js`)
* **원본앱 VDraw 전단벽 드로잉 알고리즘 이식**:
  - **상단 뷰포트 (벽체 입면도 & 부재력도)**: 벽체 전고($h_w$), 층별 분할선, 수직/수평 철근 그리드, 전단력 및 모멘트 분포도 오버레이.
  - **하단 뷰포트 (벽체 평단면도 & 경계요소 상세)**: 벽체 두께($t_w$) 및 길이($l_w$), 복배근 수직근 원형 심볼 및 수평 전단근 배근선, 양단부 특수경계요소 구속영역 음영 처리, 단부 집중 주근 및 사각/크로스타이 띠철근, 치수선, 철근 태그.
* **인터랙션 기능**: 줌/팬, Fit, 경계요소 영역 마우스 호버 시 상세 치수 및 배근비 툴팁.
* **DoD 검증**: Canvas 그래픽스 정확 렌더링, 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_rc_wall.js`)
* **원본앱 5대 장구분 계승**:
  - **1. 설계 개요 및 벽체 단면 제원**: 부재명, 재료 강도, 벽체 형상 치수, 배근 방식(복배근).
  - **2. 설계 부재력 및 내진 설계 조건**: $P_u, M_u, V_u$, 전단벽 세장비($h_w/l_w$), 전단경간비($M_u / (V_u l_w)$).
  - **3. 전단강도 검토**: 8단계 KaTeX 전개식 ($V_c$ 산정 $\rightarrow$ $V_s$ 산정 $\rightarrow$ $\phi V_n$ $\rightarrow$ $\text{DCR}_v = V_u / \phi V_n$ $\rightarrow$ `  →  O.K / N.G` 판정).
  - **4. 면내 휨-축력 강도 검토**: 축력 고려 벽체 휨강도 $\phi M_n$ 전개식 $\rightarrow$ $\text{DCR}_m = M_u / \phi M_n$ $\rightarrow$ `  →  O.K / N.G` 판정.
  - **5. 특수경계요소(SBE) 필요성 및 상세 검토**: 변위 기반 중립축 판정식 $\rightarrow$ 경계요소 필요 여부 판정 $\rightarrow$ 소요 길이 및 횡구속 철근량($A_{sh}$) 검토 $\rightarrow$ `  →  O.K / N.G` 판정.
* **DoD 검증**: A4 인쇄 프리뷰 레이아웃, KaTeX 수식 무결성 확인.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**: 벽체 두께, 배근 변경 시 100ms 이내에 평단면도/경계요소 그래픽스와 계산서 동시 갱신.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `rc_shear_wall`의 `is_wip: false`로 정식 온라인 전환.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건.

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 콘크리트학회 예제집 9.1 전단벽 예제 대비 오차 $\le 0.10\%$ (`pytest tests/engine/test_rc_wall.py` 통과).
- [ ] **1:1 입력폼**: 원본앱 `IDD_RCS_WALL_PMODE_DLG` 4대 서브탭 브라우저 렌더링 확인.
- [ ] **2D 캔버스**: 벽체 평단면도, 복배근 그리드, 양단부 특수경계요소 영역 렌더링 확인.
- [ ] **A4 계산서**: 5대 장구분 8단계 KaTeX 전단강도 및 경계요소 판정식 출력 확인.
- [ ] **4열 통합**: 100ms 이내 3-View 동시 동기화 및 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16` 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
