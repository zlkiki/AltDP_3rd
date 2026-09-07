# 요구사항 26: Phase V1-5 철골 주각부 (steel_baseplate) 5대 공정 수직 관통 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**의 Phase V1(Tier 1 플래그십 5대 핵심 부재) 중 다섯 번째 모듈인 **철골 주각부 (`steel_baseplate`)**를 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 상세 요구사항 명세서입니다.

* **모듈 식별자**: `steel_baseplate` (카탈로그 번호 No. 24)
* **국가건설기준 (4순위)**: KDS 14 31 25 (강구조 연결 및 접합설계 - 주각부 설계), KDS 14 20 54 (콘크리트 앵커볼트)
* **공식 학회 예제집 (3순위)**: 강구조설계(2019) 예제집 `6.1 노출형 주각부 콘크리트 지압 및 베이스플레이트 두께 설계`, `6.2 앵커볼트 인장/전단 검토`
* **원본 DLG 리소스 (2순위)**: `IDD_STL_USBP_PMODE_DLG`, `ID_USBP_BASEPLATE`
* **원본 추출 C 루틴 (1순위)**: `steel__CHK_USBP_*.c`, `DPLUS_STEEL.dll`

---

## 2. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/steel/baseplate.py`)
* **Pydantic 데이터 스키마 구축**:
  - `BasePlateGeometry`: 베이스플레이트 폭($B$), 길이($N$), 두께($t_p$), 강재 재질($F_y$), 주각 기둥 단면($H \times B$), 콘크리트 기초 페데스탈 치수($A_1, A_2$), 콘크리트 강도($f_{ck}$).
  - `AnchorBoltConfig`: 앵커볼트 규격(M20~M36, 강도등급 4.6/8.8), 볼트 개수, 볼트 게이지/피치 간격, 매립깊이($h_{ef}$).
  - `BasePlateLoads`: 계수축력($P_u$, 압축/인장), 계수모멘트($M_u$), 계수전단력($V_u$).
  - `BasePlateResult`: 하중 편심거리($e = M_u/P_u$), 콘크리트 지압응력 분포(전단면 압축 vs 인장 앵커볼트 작용), 최대 지압응력($f_p$) 및 공칭지압강도($\phi_c P_p$), 베이스플레이트 소요두께($t_{req}$), 앵커볼트 인장내력 및 전단내력, 전단키(Shear Key) 검토, DCR 및 판정(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - 콘크리트 허용 지압강도: $P_p = 0.85 f_{ck} A_1 \sqrt{A_2 / A_1} \le 1.7 f_{ck} A_1$ ($\phi_c = 0.65$).
  - 대편심/소편심 판정: 임계 편심 $e_{crit} = \frac{N}{2} - \frac{P_u}{2 q_{max}}$ ($q_{max} = \phi_c f_p B$).
  - 캔틸레버 휨 두께 산정: 캔틸레버 길이 $m = (N - 0.95 d) / 2$, $n = (B - 0.80 b_f) / 2$, $n' = \frac{1}{4} \sqrt{d b_f}$, 소요두께 $t_{req} = l \sqrt{\frac{2 P_u}{0.9 F_y B N}}$ 또는 지압응력 기반 산정.
  - 앵커볼트 인장: 편심에 의한 인장력 $T_u$ 산정, 콘크리트 브레이크아웃 및 강재 인장파단 검토.
* **DoD 검증**: 강구조학회 예제집 6.1 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_baseplate.py` 100% PASS).

### Step 2: 원본앱 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_steel_baseplate.js`)
* **원본앱 `IDD_STL_USBP_PMODE_DLG` 1:1 계승 서브탭 구성**:
  - **Tab 1 [플레이트/기둥]**: 강재 기둥 단면 선택, 베이스플레이트 가로/세로($B \times N$), 강판 두께($t_p$), 강종(SM355 등).
  - **Tab 2 [기초/페데스탈]**: 콘크리트 주각 단면($A_2$), 콘크리트 강도($f_{ck}$), 그라우트 두께.
  - **Tab 3 [앵커볼트/전단키]**: 앵커 규격/등급, 배열(2열/4열), 연단거리, 매립길이, 전단키 유무/치수.
  - **Tab 4 [설계하중]**: 축력($P_u$, 압축/인장), 모멘트($M_u$), 전단력($V_u$).
* **상세 대화창(`...`) 서브 모달**:
  - `[앵커볼트 상세 배열 모달]`: 볼트 좌표별 위치, 용접 리브 스티프너 유무 및 보강 형상 설정.
* **DoD 검증**: 브라우저 DOM 렌더링 정상, 폼 변경 시 이벤트 전파 및 유효성 검사, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_steel_baseplate.js`)
* **원본앱 VDraw 주각부 상세도 드로잉 알고리즘 이식**:
  - **상단 뷰포트 (주각부 정면 입면도 & 응력 분포)**: 기둥 플랜지/웨브 연결부, 베이스플레이트 두께, 그라우트층, 콘크리트 페데스탈, 앵커볼트 매립 형상, 하부 삼각/사다리꼴 지압응력 다이어그램 오버레이.
  - **하단 뷰포트 (베이스플레이트 평면도)**: 베이스플레이트 외곽선($B \times N$), H/Box 기둥 단면 배치선, 앵커볼트 위치 홀(원형 심볼) 및 중심선, 연단거리/볼트간격 치수선, 리브 스티프너 배치선.
* **인터랙션 기능**: 줌/팬, Fit, 앵커볼트 또는 지압영역 호버 시 응력치/DCR 툴팁.
* **DoD 검증**: Canvas 그래픽스 정확 렌더링, 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_steel_baseplate.js`)
* **원본앱 5대 장구분 계승**:
  - **1. 설계 개요 및 주각부 제원**: 부재명, 강종, 기둥 단면, 베이스플레이트 치수, 콘크리트 페데스탈 제원.
  - **2. 설계 부재력 및 편심 검토**: $P_u, M_u, V_u$, 편심거리 $e = M_u/P_u$, 대편심/소편심 판정 KaTeX 전개.
  - **3. 콘크리트 지압강도 검토 (Bearing Strength)**: $A_2/A_1 \rightarrow f_p \rightarrow \phi_c P_p \rightarrow \text{DCR}_{bearing} \le 1.000$ $\rightarrow$ `  →  O.K / N.G`.
  - **4. 베이스플레이트 휨 두께 검토 (Plate Thickness)**: 캔틸레버 길이 $m, n, n' \rightarrow$ 모멘트 산정 $\rightarrow$ $t_{req} \le t_p \rightarrow$ `  →  O.K / N.G`.
  - **5. 앵커볼트 인장 및 전단 검토 (Anchor Bolts)**: 인장력 $T_u \rightarrow \phi R_n \rightarrow$ 마찰/전단키 전단 저항 검토 $\rightarrow$ `  →  O.K / N.G`.
* **DoD 검증**: A4 인쇄 프리뷰 레이아웃, KaTeX 수식 무결성 확인.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**: 베이스플레이트 치수 또는 앵커 변경 시 100ms 이내에 입/평면도, 지압 DCR, A4 계산서 동시 갱신.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `steel_baseplate`의 `is_wip: false`로 정식 온라인 전환.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건.

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 강구조설계예제집 6.1 주각부 예제 대비 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_baseplate.py` 통과).
- [ ] **1:1 입력폼**: 원본앱 `IDD_STL_USBP_PMODE_DLG` 4대 서브탭 브라우저 렌더링 확인.
- [ ] **2D 캔버스**: 주각부 정면도(지압응력도) 및 평면도(기둥, 볼트홀, 치수선) 렌더링 확인.
- [ ] **A4 계산서**: 5대 장구분 8단계 KaTeX 지압, 두께, 앵커 인장/전단 수식 출력 확인.
- [ ] **4열 통합**: 100ms 이내 3-View 동시 동기화 및 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16` 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
