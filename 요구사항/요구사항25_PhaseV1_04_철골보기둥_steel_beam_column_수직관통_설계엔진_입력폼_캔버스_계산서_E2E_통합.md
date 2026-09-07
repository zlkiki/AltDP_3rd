# 요구사항 25: Phase V1-4 철골 보/기둥 (steel_beam_column) 5대 공정 수직 관통 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**의 Phase V1(Tier 1 플래그십 5대 핵심 부재) 중 네 번째 모듈인 **철골 보/기둥 (`steel_beam_column`)**을 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 상세 요구사항 명세서입니다.

* **모듈 식별자**: `steel_beam_column` (카탈로그 번호 No. 22)
* **국가건설기준 (4순위)**: KDS 14 31 10 (강구조설계기준 - 판폭두께비, 휨재, 압축재, 전단재, 조합력재)
* **공식 학회 예제집 (3순위)**: 강구조설계(2019) 예제집 `3.1 H형강 휨재 횡지지/비지지 LTB 좌굴`, `4.1 압축재 좌굴강도`, `5.1 축력-휨 P-M 상호작용`
* **원본 DLG 리소스 (2순위)**: `IDD_STL_BEAMCOLUMN_INPUT_DLG`, `IDD_STL_BEAMCOL_*`
* **원본 추출 C 루틴 (1순위)**: `steel__CHK_USMC_*.c`, `DPLUS_STEEL.dll`

---

## 2. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/steel/beam.py`, `column.py`)
* **Pydantic 데이터 스키마 구축**:
  - `SteelSection`: 단면 타입(H형강, 각형강관, 원형강관 등), 호칭규격(KS D 3502 단면 DB 파서 연동), $H, B, t_w, t_f, r$, 단면적($A$), 단면2차모멘트($I_x, I_y$), 소성단면계수($Z_x, Z_y$), 탄성계수($E$), 항복강도($F_y$).
  - `SteelMemberGeometry`: 부재 길이($L$), 강축/약축 유효좌굴길이계수($K_x, K_y$), 횡지지길이($L_b$), 모멘트구배계수($C_b$).
  - `SteelLoads`: 계수축력($P_u$, 인장/압축), 강축/약축 계수모멘트($M_{ux}, M_{uy}$), 계수전단력($V_{ux}, V_{uy}$).
  - `SteelDesignResult`: 판폭두께비 조밀/비조밀/세장 판정, 휨강도($\phi_b M_n$), 압축강도($\phi_c P_n$), 인장강도($\phi_t P_n$), 전단강도($\phi_v V_n$), P-M 축휨 상호작용 DCR(H1-1a / H1-1b) 및 판정(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - 판폭두께비 한계값: 플랜지 $\lambda_p = 0.38\sqrt{E/F_y}$, 웨브 $\lambda_p = 3.76\sqrt{E/F_y}$ (휨) 및 축압축비 연동.
  - 횡비틀림좌굴(LTB): 비지지길이 $L_p = 1.76 r_y \sqrt{E/F_y}$, $L_r = 1.95 r_{ts} \frac{E}{0.7 F_y} \sqrt{\frac{J c}{S_x h_0} + \sqrt{\left(\frac{J c}{S_x h_0}\right)^2 + 6.76\left(\frac{0.7 F_y}{E}\right)^2}}$.
  - 압축 좌굴(KDS 14 31 10): 탄성좌굴응력 $F_e = \frac{\pi^2 E}{(K L / r)^2}$, $F_{cr} = [0.658^{F_y / F_e}] F_y$ 또는 $0.877 F_e$.
  - 조합력 상호작용식:
    - $\frac{P_u}{\phi_c P_n} \ge 0.2 \implies \frac{P_u}{\phi_c P_n} + \frac{8}{9}\left(\frac{M_{ux}}{\phi_b M_{nx}} + \frac{M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$
    - $\frac{P_u}{\phi_c P_n} < 0.2 \implies \frac{P_u}{2 \phi_c P_n} + \left(\frac{M_{ux}}{\phi_b M_{nx}} + \frac{M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$
* **DoD 검증**: 강구조학회 예제집 3.1, 4.1, 5.1 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_beam.py` 및 `test_steel_column.py` 100% PASS).

### Step 2: 원본앱 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_steel_beam_column.js`)
* **원본앱 `IDD_STL_BEAMCOLUMN_INPUT_DLG` 1:1 계승 서브탭 구성**:
  - **Tab 1 [단면/재료]**: 강재 규격(SS275, SM355, SM460 등), 단면 타입(H, Box, Pipe), 단면 DB 선택 모달 연동.
  - **Tab 2 [부재길이/지지]**: 부재 길이($L$), 강축/약축 $K_x, K_y$, 횡비지지길이($L_b$), 횡구속 조건.
  - **Tab 3 [설계계수]**: 모멘트 구배계수($C_b$, 수동 입력 또는 $M_{max}, M_A, M_B, M_C$ 자동 산출), 2차 모멘트 확대계수($B_1, B_2$).
  - **Tab 4 [설계부재력]**: 다축 부재력 ($P_u, M_{ux}, M_{uy}, V_{ux}, V_{uy}$) 및 복수 LCB 하중 포락 그리드.
* **상세 대화창(`...`) 서브 모달**:
  - `[KS 표준 형강 DB 모달]`: H형강 규격 테이블(치수, 중량, 기하계수) 검색 및 1클릭 적용.
  - `[모멘트구배계수 Cb 계산기 모달]`: 단부 모멘트비 및 하중형태별 자동 산출.
* **DoD 검증**: 브라우저 DOM 렌더링 정상, 단면 DB 변경 시 기하성질 자동 반영, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_steel_beam_column.js`)
* **원본앱 VDraw 강재 단면 드로잉 알고리즘 이식**:
  - **상단 뷰포트 (부재 입면 및 좌굴형상)**: 부재 길이($L$), 지지점 및 가새 횡지지점 위치 표기, 모멘트 다이어그램($M_x, M_y$) 및 횡비틀림 좌굴 모드 시각화.
  - **하단 뷰포트 (H/Box 형강 상세 단면도)**: 플랜지/웨브 필릿 라운딩($r$) 반영 단면 정밀 렌더링, 치수선($H, B, t_w, t_f$), 도심축($x-x, y-y$), 단면 특성치 텍스트 박스, 응력집중 하이라이트.
* **인터랙션 기능**: 줌/팬, Fit, 단면 요소 마우스 호버 시 치수/국부좌굴 여유도 툴팁.
* **DoD 검증**: Canvas 그래픽스 정확 렌더링, 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_steel_beam_column.js`)
* **원본앱 5대 장구분 계승**:
  - **1. 설계 개요 및 형강 단면 제원**: 강종, 공칭항복강도, KS 표준 단면 규격, 단면 기하특성치($A, I, Z, S, r, J, C_w$).
  - **2. 단면 조밀성 판정 (Width-to-Thickness Ratio)**: 플랜지/웨브 판폭두께비 KaTeX 산정 $\rightarrow$ 조밀/비조밀/세장 판정 $\rightarrow$ `  →  O.K`.
  - **3. 휨강도 검토 (Flexural Strength)**: $M_p = F_y Z_x \rightarrow L_b$ vs $L_p, L_r \rightarrow \text{LTB 좌굴강도 } M_n \rightarrow \phi_b M_n$ $\rightarrow$ `  →  O.K / N.G`.
  - **4. 압축/인장강도 검토 (Axial Strength)**: 유효세장비 $KL/r \rightarrow F_e \rightarrow F_{cr} \rightarrow \phi_c P_n$ $\rightarrow$ `  →  O.K / N.G`.
  - **5. 조합력 상호작용 검토 (P-M Interaction)**: H1-1a / H1-1b KaTeX 수식 전개 $\rightarrow$ $\text{DCR} \le 1.000$ $\rightarrow$ `  →  O.K / N.G`.
* **DoD 검증**: A4 인쇄 프리뷰 레이아웃, KaTeX 수식 무결성 확인.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**: 단면 DB 선택 또는 부재력 수정 시 100ms 이내에 단면도, P-M DCR, A4 계산서 동시 갱신.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `steel_beam_column`의 `is_wip: false`로 정식 온라인 전환.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건.

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 강구조설계예제집 3.1, 4.1, 5.1 대비 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_*.py` 통과).
- [ ] **1:1 입력폼**: 원본앱 `IDD_STL_BEAMCOLUMN_INPUT_DLG` 4대 서브탭 브라우저 렌더링 확인.
- [ ] **2D 캔버스**: H/Box 형강 단면 정밀 외곽선, 필릿 라운딩, 치수선 렌더링 확인.
- [ ] **A4 계산서**: 5대 장구분 8단계 KaTeX 판폭두께비, LTB, 압축좌굴, P-M 상호작용 수식 출력 확인.
- [ ] **4열 통합**: 100ms 이내 3-View 동시 동기화 및 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16` 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
