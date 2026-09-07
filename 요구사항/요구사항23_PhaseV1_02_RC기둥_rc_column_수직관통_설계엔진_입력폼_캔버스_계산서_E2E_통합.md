# 요구사항 23: Phase V1-2 RC 기둥 (rc_column) 5대 공정 수직 관통 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**의 Phase V1(Tier 1 플래그십 5대 핵심 부재) 중 두 번째 모듈인 **RC 기둥 (`rc_column`)**을 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 상세 요구사항 명세서입니다.

* **모듈 식별자**: `rc_column` (카탈로그 번호 No. 2)
* **국가건설기준 (4순위)**: KDS 14 20 10 (재료), KDS 14 20 20 (축력 및 휨), KDS 14 20 22 (기둥 전단)
* **공식 학회 예제집 (3순위)**: 콘크리트구조학회(2020) 예제집 `5.1 단주 축력-휨 P-M 상관곡선`, `5.2 원형/나선철근 기둥`, `5.3 장주 횡구속/비구속 모멘트확대법`
* **원본 DLG 리소스 (2순위)**: `IDD_RCS_COLUMN_PMODE_DLG`, `IDD_URCF_PMODE_DLG`
* **원본 추출 C 루틴 (1순위)**: `solver__CHK_BCCO_*.c`, `DPLUS_RCS.dll`, `DPLUS_DB.dll` (파이버 솔버)

---

## 2. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/rc/column.py`)
* **Pydantic 데이터 스키마 구축**:
  - `RCColumnSection`: 단면 형태(사각/원형), 단면 치수($b \times h$ 또는 $D$), 층고/부재길이($L_u$), 유효길이계수($k_x, k_y$), $f_{ck}, f_y, f_{yt}$, 띠철근/나선철근 구분.
  - `RCColumnRebar`: 4면 균등배치 또는 각 변별 주철근 배치, 전단 띠철근(지름, 다리수, 간격 $s$).
  - `RCColumnLoads`: 3축 부재력 ($P_u, M_{ux}, M_{uy}$), 단부 모멘트비 ($M_1/M_2$), 횡구속(Braced)/비구속(Unbraced) 골조 플래그.
  - `RCColumnResult`: 순수 압축내력($P_0, \phi P_{n,max}$), 균형파괴점($P_b, M_b$), 순수 휨내력($M_0$), 3D P-M 곡선 데이터포인트(200 파이버 적분), 이축휨 브레슬러(Bresler) 상호작용 지수, 모멘트확대계수($\delta_{ns}, \delta_s$), 전단 DCR 및 최종 판정(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - 최대 설계축강도: $\phi P_{n,max} = 0.80 \phi [0.85 f_{ck} (A_g - A_{st}) + f_y A_{st}]$ (띠철근 $\phi = 0.65$).
  - 파이버 수치적분 솔버 연동: 200개 단면 요소로 분할하여 중립축 회전각($\theta$) 및 곡률에 따른 P-M 3차원 상관곡면 생성.
  - 장주 효과(KDS 14 20 20): 세장비 판정 ($k l_u / r \le 34 - 12(M_1/M_2)$), 탄성 좌굴하중 $P_c = \pi^2 E I / (k l_u)^2$, 모멘트 확대 $M_c = \delta_{ns} M_2$.
  - 이축휨 검토: Bresler 상호작용식 $\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_0}$ 또는 파이버 3D 곡면 직접 내삽 판정.
* **DoD 검증**: 콘크리트학회 예제집 5.1/5.2 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_rc_column.py` 100% PASS).

### Step 2: Midas 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_rc_column.js`)
* **Midas 원본 `IDD_RCS_COLUMN_PMODE_DLG` 1:1 계승 서브탭 구성**:
  - **Tab 1 [단면/재료]**: 기둥 형상(사각/원형), $B, H$ 또는 $D$, 콘크리트 강도($f_{ck}$), 철근 강도($f_y, f_{yt}$), 피복두께.
  - **Tab 2 [철근배근]**: 주철근 배치 방식(균등배열, 코너철근+변철근), 철근 호칭경(D19~D35) 및 개수, 띠철근/나선철근 간격 $s$.
  - **Tab 3 [설계하중/부재력]**: 축하중($P_u$), 양단 모멘트($M_{ux}, M_{uy}$), 다중 하중조합(LCB) 그리드.
  - **Tab 4 [세장비/골조]**: 층고($L$), $k_x, k_y$, 골조 횡구속 여부, 지속하중 비($\beta_{dns}$).
* **상세 대화창(`...`) 서브 모달**:
  - `[기둥 철근 배열 상세 모달]`: 2변/4변 대칭, 단면 코너보강, 복합 띠철근(크로스타이) 상세 설정.
  - `[P-M 뷰어 확장 모달]`: 3D P-M 상관곡면 확대 인터랙티브 뷰.
* **DoD 검증**: 브라우저 DOM 렌더링 정상, 폼 변경 시 이벤트 전파 및 유효성 검사, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_rc_column.js`)
* **Midas VDraw 기둥 드로잉 및 P-M 차트 이식**:
  - **상단 뷰포트 (기둥 횡단면 배근도)**: 콘크리트 외곽선(사각/원형), 외곽 폐합 띠철근 및 내부 다이아몬드/크로스타이 띠철근, 주철근 원형 솔리드 심볼, 피복 옵셋선, 치수선, 철근 태그(예: `12-D25`).
  - **하단 뷰포트 (P-M 상관곡선 차트)**: KDS 설계 P-M 곡선(공칭강도 $P_n-M_n$ 및 설계강도 $\phi P_n-\phi M_n$), 최대 축강도 수평선($\phi P_{n,max}$), 균형파괴점($B$), 설계하중점($P_u, M_u$) 플롯 및 안전/위험 영역 시각화.
* **인터랙션 기능**: 줌/팬, Fit, 하중점 마우스 호버 시 DCR 및 여유도 툴팁 표시.
* **DoD 검증**: 단면 배근 및 P-M 곡선 정확 렌더링 확인, 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_rc_column.js`)
* **Midas 원본 5대 장구분 계승**:
  - **1. 설계 개요 및 기둥 단면 제원**: 부재명, 재료 강도, 단면 치수, 유효길이, 철근비($\rho_g = A_{st}/A_g$, 1%~8% 검토).
  - **2. 설계 부재력 및 세장비 검토**: $P_u, M_{ux}, M_{uy}$, 세장비 한계 검토, 모멘트확대계수($\delta_{ns}$) 산정 전개식.
  - **3. 축력-휨 P-M 강도 검토**: 8단계 KaTeX 전개식 ($P_0$ $\rightarrow$ $\phi P_{n,max}$ $\rightarrow$ 하중편심 $e = M_u/P_u$ $\rightarrow$ 파이버 수치해석 $\phi P_n(\phi M_n)$ 도출 $\rightarrow$ $\text{DCR} \le 1.000$ $\rightarrow$ `  →  O.K / N.G` 판정).
  - **4. 이축휨 상호작용 검토**: Bresler 역수식 또는 등가 1축 모멘트 산정 KaTeX 전개식 $\rightarrow$ `  →  O.K / N.G` 판정.
  - **5. 기둥 전단강도 검토**: 축압축력에 의한 전단강도 증대 $V_c = \frac{1}{6} \left(1 + \frac{P_u}{14 A_g}\right) \lambda \sqrt{f_{ck}} b_w d$ $\rightarrow$ $\phi V_n$ vs $V_u$ $\rightarrow$ `  →  O.K / N.G` 판정.
* **DoD 검증**: A4 인쇄 프리뷰 레이아웃, P-M 곡선 이미지 삽입, KaTeX 수식 무결성 확인.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**:
  - 기둥 치수나 철근 입력 변경 시 100ms 이내에 캔버스 배근도와 P-M 곡선 차트, A4 계산서 동시 갱신.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `rc_column`의 `is_wip: false`로 정식 온라인 전환.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건.

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 콘크리트학회 예제집 5.1 기둥 P-M 상관도 대비 오차 $\le 0.10\%$ (`pytest tests/engine/test_rc_column.py` 통과).
- [ ] **1:1 입력폼**: Midas 원본 `IDD_RCS_COLUMN_PMODE_DLG` 4대 서브탭 브라우저 렌더링 확인.
- [ ] **2D 캔버스 & P-M**: 기둥 배근도 및 200 파이버 P-M 상관곡선/하중점 플롯 확인.
- [ ] **A4 계산서**: 5대 장구분 8단계 KaTeX 수식 전개 및 `  →  O.K / N.G` 판정 표기 확인.
- [ ] **4열 통합**: 100ms 이내 3-View 동시 동기화 및 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16` 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
