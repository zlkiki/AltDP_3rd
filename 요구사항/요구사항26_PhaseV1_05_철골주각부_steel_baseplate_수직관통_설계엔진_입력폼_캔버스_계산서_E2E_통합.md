# 요구사항 26: Phase V1-5 철골 주각부 (steel_baseplate) 5대 공정 수직 관통 마스터 명세서

## 1. 개요 및 모듈 개요 (Module Overview)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**의 Phase V1(Tier 1 플래그십 5대 핵심 부재) 중 완결 부재인 **철골 주각부 (`steel_baseplate`)**를 부재 단위 수직 관통(Vertical Slice)하여 **Step 1(엔진)부터 Step 5(E2E 통합)**까지 100% 작동 가능한 상용 엔지니어링 모듈로 완성하기 위한 마스터 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_baseplate` (카탈로그 번호 No. 24, Tier 1 플래그십)
* **담당 핵심 파일**:
  - 엔진 & 스키마: [`src/engine/steel/baseplate.py`](file:///f:/PyProject/AltDP_3rd/src/engine/steel/baseplate.py), [`src/api/routes/steel.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/steel.py)
  - 입력폼 컴포넌트: `src/web/static/js/components/form_steel_baseplate.js`, `src/web/static/js/components/member_manager.js`
  - 그래픽 뷰포트: `src/web/static/js/visual/vector_steel_baseplate.js`, `src/web/static/js/visual/vector/vector_steel.js`
  - 구조계산서 렌더러: `src/web/static/js/report/redcr/SteelReportGenerator.js`, `src/web/static/js/report/redcr_steel_baseplate.js`
  - 통합 및 디스패처: `src/web/static/js/core/dispatcher.js`, `src/web/static/js/catalog.js`
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` C루틴 심볼 (`steel__CHK_USBP_*.c`, `solver_baseplate_*`, `DPLUS_STEEL.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 매뉴얼]`: 원본앱 기술 매뉴얼 Steel Baseplate 편 (`IDD_STL_USBP_PMODE_DLG`, `IDD_STL_USBP_SECT_DLG`, `IDD_STL_USBP_PLAT_DLG`)
  3. `[3순위 학회 예제집]`: 한국강구조학회·한국건축구조기술사회 『KDS 41 31 00 : 2019에 따른 강구조설계 예제집』 (오류 시 Patch-First 선 치유 원칙)
     - `제13장 예제 13.6.7`: 주각부 설계 - 축력이 지배하는 고정단 H형강 기둥 주각부 ($H\text{-}428\times 407\times 20\times 35$, SM355, 콘크리트 $f_{ck}=24\text{ MPa}$, 플레이트 $700\times 700\times 55\text{ mm}$, 페데스탈 $800\times 800\text{ mm}$, 지압강도 $\phi_c P_p = 7,430\text{ kN}$, 8-M24 앵커)
     - `제11장 예제 11.12`: 중심축하중을 받는 각형강관 기둥의 베이스플레이트 설계 ($300\times 300\times 12$ 각관, $450\times 450\times 24\text{ mm}$ 플레이트)
     - `제6장 예제 6.1, 6.2`: 대편심 모멘트 지배 주각부 (인장측 앵커볼트 인장력 $T_u$ 발생 및 콘크리트 파열 검토)
  4. `[4순위 국가건설기준]`: (오류 시 Patch-First 선 치유 원칙)
     - `KDS 14 31 25`: 강구조 연결 및 접합설계기준 (4.5 주각부 설계)
     - `KDS 14 20 54`: 콘크리트용 앵커 설계기준 (선설치 및 후설치 앵커볼트 인장·전단 강도)
     - `AISC Design Guide 1`: Base Plate and Anchor Rod Design (2nd Edition)

---

## 2. docs/07 제21절 기반 UI/UX 선행 검토 체크리스트

[`docs/07_web_application_ui_ux_specification.md 제21절`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)의 6대 필수 검토 항목을 충실히 반영하여 프론트엔드 연동 사양을 사전 확립합니다:

1. **[사이드바 & 카테고리 정합성]**:
   - 8대 카테고리 Pills 탭 중 `[Steel 강구조]` 그룹에 속하며, 영문 키 `steel_baseplate`, 한글 명칭 "철골 주각부 (Baseplate)".
   - 3단계 WorkTree(`Steel 강구조 > 접합부/주각 > 철골 주각부`) 및 즐겨찾기(⭐) 지원.
2. **[Pane 1 부재 매니저 요약 테이블]**:
   - 핵심 요약 컬럼: 부재 ID(`1F-BP1`), 기둥 단면(`H-400x400x13x21`), 베이스플레이트 치수(`PL-650x650x35`), 앵커볼트(`4-M24`), 지압 DCR, 플레이트 DCR, 앵커 DCR, 종합 판정 배지(`OK`/`NG`).
3. **[Pane 2 4대 서브탭 & 원본 1:1 서브 모달]**:
   - 원본 `IDD_STL_USBP_PMODE_DLG`를 1:1로 계승한 4대 서브탭:
     * **Tab 1 [단면/플레이트]**: 기둥 형강 단면(H형강, 각형강관, 원형강관, SDB 연동), 베이스플레이트 폭/길이/두께($B \times N \times t_p$), 플레이트 강종(SM355, SS275 등).
     * **Tab 2 [기초/페데스탈]**: 콘크리트 압축강도($f_{ck}$), 페데스탈 폭/길이($B_2 \times N_2$), 그라우트 두께($t_g$), 기초 형상.
     * **Tab 3 [앵커/보강리브]**: 앵커볼트 시공형식(선설치 헤드볼트 / 후설치 앵커), 볼트 직경(M20~M36), 매립깊이($h_{ef}$), 볼트 배열(2열/4열, 연단거리, 게이지 간격), 리브 스티프너(Rib/Wing Plate) 유무 및 치수.
     * **Tab 4 [설계하중]**: 다축 부재력 ($P_u$ 압축/인장, $M_{ux}, M_{uy}, V_{ux}, V_{uy}$) 및 복수 LCB 하중 포락 그리드.
   - 서브 대화창(`...`) 모달 3종: `[KS 표준 형강 DB 모달]`, `[앵커볼트 상세 배열 및 콘크리트 파열 모달]`, `[하중조합 포락 모달]`.
   - 3버튼 통합 액션 파이프라인 (`[💾 적용] [⚡ 검토] [✨ 설계]`).
4. **[Pane 3 세로 적층형 2단 그래픽 뷰포트]**:
   - **[상단 뷰포트]**: 주각부 정면 입면도, 기둥-베이스플레이트-그라우트층-콘크리트 페데스탈 수직 접합단면, 앵커볼트 매립 형상, 하부 콘크리트 지압응력 분포(전단면 등분포/사다리꼴 vs 대편심 삼각형 지압대) 다이어그램 오버레이.
   - **[하단 뷰포트]**: 베이스플레이트 상세 평면도, 외곽선($B \times N$), H/Box 기둥 단면 배치선, 앵커볼트 위치 홀(원형 심볼) 및 중심선, 연단거리/볼트간격 치수선, 리브 스티프너 배치선.
5. **[Pane 4 순백색 A4 8단계 KaTeX 구조계산서]**:
   - 상시 순백색(`#ffffff`) 고정 A4 용지 레이아웃.
   - 상세/요약 라디오 분기 및 `[☑ 사용자 입력 데이터 상세 포함]` 토글.
   - 5대 장구분 및 8단계 KaTeX 지압응력, 캔틸레버 소요두께, 앵커 인장/전단/복합응력 수식 전개.
   - 원본 고유 `  →  O.K / N.G` 판정 화살표.
6. **[실시간 반응성 및 성능]**:
   - 파라미터 변경 시 `ProjectStore` 중심 100ms 이내에 캔버스와 계산서가 비동기 갱신 보장.

---

## 3. 5대 정밀 수직 공정 세부 명세 (Step 1 ~ Step 5)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase V1-5 철골 주각부 (steel_baseplate) 5대 마이크로 공정 파이프라인                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Step 1: KDS 계산엔진]  ──► [Step 2: 1:1 서브탭폼] ──► [Step 3: 2D 캔버스] ──► [Step 4: A4 계산서] ──► [Step 5: E2E 통합] │
│ (Pydantic / 0.1% TDD)       (4대 서브탭 & 모달)       (세로적층 2단 뷰포트)     (순백색 A4 8단계 KaTeX)   (100ms 동기화/WIP해제)│
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Step 1: KDS 계산 엔진 & Pydantic 스키마 (`src/engine/steel/baseplate.py`, `src/api/routes/steel.py`)
* **Pydantic v2 데이터 입출력 스키마 구축**:
  - `BasePlateInput`: 기둥 단면 치수($d, b_f, t_w, t_f$), 강종($F_y$), 베이스플레이트 치수($B, N, t_p$, 강종 $F_{yp}$), 콘크리트 기초 치수($B_2, N_2$, 압축강도 $f_{ck}$), 앵커볼트 규격($d_a$, 강종 $f_{uta}$, 개수, 간격, 연단거리, $h_{ef}$), 설계하중($P_u, M_{ux}, M_{uy}, V_{ux}, V_{uy}$).
  - `BasePlateResult`: 하중 편심거리($e = M_u/P_u$), 편심 상태(소편심, 중편심, 대편심), 콘크리트 최대 지압응력($f_p$) 및 설계지압강도($\phi_c P_p$), 캔틸레버 굽힘암($m, n, \lambda n', l$), 소요 플레이트 두께($t_{req}$), 앵커볼트 소요인장력($T_u$), 앵커 강재인장강도($\phi N_{sa}$), 콘크리트 콘파칭강도($\phi N_{cb}$), 앵커 강재전단강도($\phi V_{sa}$), 콘크리트 프라이아웃강도($\phi V_{cp}$), 복합응력비, 종합 DCR 및 판정(`OK`/`NG`).
* **KDS 수치 계산 정밀 구현**:
  - **콘크리트 지압강도 (KDS 14 31 25 4.5.1 / KDS 14 20 20)**:
    * $A_1 = B \times N$, $A_2 = B_2 \times N_2$
    * 형상계수: $\sqrt{A_2 / A_1} \le 2.0$
    * 설계지압강도: $\phi_c P_p = \phi_c (0.85 f_{ck} A_1 \sqrt{A_2 / A_1}) \le \phi_c (1.7 f_{ck} A_1)$ ($\phi_c = 0.65$)
  - **편심 및 지압응력 분포 판정**:
    * 소편심 ($e \le N/6$): 전단면 압축, $f_p = \frac{P_u}{A_1} \left(1 + \frac{6e}{N}\right)$, $T_u = 0$
    * 중편심 ($N/6 < e \le e_{crit}$): 부분 압축, 압축대 길이 $Y_c = 3(N/2 - e)$, $f_p = \frac{2 P_u}{3 B (N/2 - e)}$, $T_u = 0$
    * 대편심 ($e > e_{crit}$): 앵커볼트 인장력 발생, 극한 평형 $f_p = \phi_c (0.85 f_{ck} \sqrt{A_2/A_1})$, 2차 방정식 해법을 통한 압축대 길이 $Y_c$ 및 앵커 소요인장력 $T_u = C - P_u$ 산출.
  - **베이스플레이트 휨 두께 (KDS 14 31 25 4.5.2 / AISC DG-1)**:
    * 캔틸레버 돌출길이: $m = (N - 0.95 d)/2$, $n = (B - 0.80 b_f)/2$ (H형강 기준)
    * 각형강관 기둥: $m = (N - 0.95 d)/2$, $n = (B - 0.95 b)/2$
    * 웨브-플랜지 사이 내측 휨: $n' = \frac{1}{4}\sqrt{d b_f}$
    * 지압응력비: $X = \frac{4 d b_f}{(d + b_f)^2} \frac{P_u}{\phi_c P_p} \le 1.0$, $\lambda = \frac{2\sqrt{X}}{1 + \sqrt{1 - X}} \le 1.0$
    * 지배 굽힘암: $l = \max(m, n, \lambda n')$
    * 소요 두께: $t_{req} = l \sqrt{\frac{2 P_u}{0.90 F_y B N}}$ (소편심) 또는 $t_{req} = l \sqrt{\frac{2 f_p}{0.90 F_y}}$ (대편심)
  - **앵커볼트 강도 검토 (KDS 14 20 54)**:
    * 강재 인장강도: $\phi N_{sa} = \phi_s n_{ta} A_{se} f_{uta}$ ($\phi_s = 0.75$)
    * 콘크리트 브레이크아웃: $\phi N_{cb} = \phi_c \frac{A_{Nc}}{A_{Nc0}} \psi_{ed,N} N_b$ ($N_b = k_c \lambda \sqrt{f_{ck}} h_{ef}^{1.5}$, $\phi_c = 0.70$)
    * 강재 전단강도: $\phi V_{sa} = \phi_s 0.60 n_{total} A_{se} f_{uta}$ ($\phi_s = 0.65$)
    * 콘크리트 프라이아웃: $\phi V_{cp} = \phi_c k_{cp} N_{cb}$ ($k_{cp} = 2.0$ if $h_{ef} \ge 65\text{ mm}$)
    * 인장-전단 복합응력: $\left(\frac{T_u}{\phi N_n}\right)^{1.67} + \left(\frac{V_u}{\phi V_n}\right)^{1.67} \le 1.0$
* **DoD 검증**: 강구조설계예제집 13.6.7(주각부 고정단 축력+모멘트) 및 11.12(각관 주각부) 대비 계산 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_baseplate.py` 100% PASS).

### Step 2: 원본앱 1:1 서브탭 입력폼 & 모달 (`src/web/static/js/components/form_steel_baseplate.js`)
* **원본앱 `IDD_STL_USBP_PMODE_DLG` 1:1 계승 4대 서브탭 구성**:
  - **Tab 1 [단면/플레이트]**: 기둥 단면 선택(H형강, 각형강관, 원형강관), 단면 치수 입력 및 `[단면 DB...]` 버튼, 베이스플레이트 치수($B \times N \times t_p$), 플레이트 강종(SM355, SS275 등).
  - **Tab 2 [기초/페데스탈]**: 콘크리트 설계압축강도($f_{ck}$), 페데스탈 치수($B_2 \times N_2$), 그라우트 두께($t_g$), 기초 연단 배치 위치.
  - **Tab 3 [앵커/보강리브]**: 앵커 시공형식(선설치/후설치), 직경(M20~M36), 매립깊이($h_{ef}$), 배치 열수(2열/4열), 볼트 연단거리 및 게이지 간격, 리브 스티프너(Rib Plate / Wing Plate) 체크박스 및 형상 치수.
  - **Tab 4 [설계하중]**: 설계 축하중($P_u$, 압축/인장), 휨모멘트($M_{ux}, M_{uy}$), 전단력($V_{ux}, V_{uy}$), 다중 하중조합 포락 그리드.
* **상세 대화창(`...`) 서브 모달 3종**:
  - `[KS 표준 형강 DB 모달]`: H형강, 각형강관 규격 검색 및 단면성질 1클릭 바인딩.
  - `[앵커볼트 상세 배열 및 콘크리트 파열 모달]`: 앵커볼트 개별 좌표, 콘크리트 연단거리, 매립 정착판 제원 대화형 설정.
  - `[하중조합 포락 모달]`: 지진/풍하중 조합력 그리드 관리.
* **DoD 검증**: 브라우저 DOM 렌더링 정상, 폼 변경 시 이벤트 전파 및 유효성 검사, 콘솔 에러 0건.

### Step 3: 2D VDraw 캔버스 배근/단면 그래픽스 (`src/web/static/js/visual/vector_steel_baseplate.js`)
* **원본앱 VDraw 주각부 그래픽스 알고리즘 이식 (세로 적층형 2단 뷰포트)**:
  - **상단 뷰포트 (주각부 정면 입면도 & 지압응력 다이어그램)**:
    * 기둥 하단 플랜지/웨브, 베이스플레이트 단면, 무수축 모르타르 그라우트층, 콘크리트 페데스탈 상부 입면 렌더링.
    * 앵커볼트 매립 형상(정착판/너트 기호) 및 매립깊이($h_{ef}$) 치수선.
    * 하부 콘크리트 지압응력 다이어그램 오버레이 (소편심 사다리꼴/등분포 vs 대편심 삼각 지압대 음영).
  - **하단 뷰포트 (베이스플레이트 정밀 평면도)**:
    * 베이스플레이트 외곽선($B \times N$) 및 도심축선($x-x, y-y$).
    * H형강 또는 각형강관 기둥 단면 배치선 및 용접선 기호.
    * 앵커볼트 위치 원형 심볼 및 볼트 구멍 지름, 연단거리/볼트 간격 치수선.
    * 리브 스티프너(Rib/Wing Plate) 배치선 렌더링.
* **인터랙션 기능**: 마우스 휠 줌/팬, Fit, 앵커볼트 또는 지압영역 호버 시 응력치/DCR 툴팁.
* **DoD 검증**: Canvas 그래픽스 정확 렌더링, 콘솔 에러 0건.

### Step 4: A4 5대 장구분 8단계 KaTeX 구조계산서 (`src/web/static/js/report/redcr_steel_baseplate.js`)
* **원본앱 5대 장구분 계승**:
  - **1. 설계 개요 및 주각부 제원 (Design Overview & Geometry)**: 기둥 단면, 강종($F_y$), 베이스플레이트 치수($B, N, t_p$), 콘크리트 강도($f_{ck}$), 기초 치수($B_2, N_2$), 앵커볼트 규격.
  - **2. 설계 부재력 및 편심 상태 판정 (Design Forces & Eccentricity)**: $P_u, M_u, V_u$, 편심 $e = M_u/P_u$, 임계 편심 $e_{crit}$ 대조를 통한 소편심/중편심/대편심 판정 KaTeX 전개.
  - **3. 콘크리트 기초 지압강도 검토 (Concrete Bearing Capacity)**: $A_1, A_2$, 형상계수 $\sqrt{A_2/A_1} \le 2.0$, 설계지압강도 $\phi_c P_p$ 산정 및 지압응력 DCR 검토 $\rightarrow$ `  →  O.K / N.G`.
  - **4. 베이스플레이트 휨 두께 검토 (Base Plate Thickness)**: 캔틸레버 굽힘암 $m, n, \lambda n', l$ 유도, 소요두께 $t_{req} \le t_p$ 검토 $\rightarrow$ `  →  O.K / N.G`.
  - **5. 앵커볼트 인장·전단 및 복합응력 검토 (Anchor Bolt Capacity)**: 앵커 인장력 $T_u$, 강재 인장 $\phi N_{sa}$, 콘크리트 브레이크아웃 $\phi N_{cb}$, 전단강도 $\phi V_n$, 인장-전단 상호작용비 검토 $\rightarrow$ `  →  O.K / N.G`.
* **DoD 검증**: A4 인쇄 프리뷰 레이아웃, KaTeX 수식 무결성 확인.

### Step 5: 4열 통합 E2E 검증 & 실사용 UI 확립
* **4-Pane 실시간 연동**: 베이스플레이트 치수, 기둥 단면 또는 앵커 변경 시 100ms 이내에 입면도/평면도, 지압 DCR, A4 계산서 동시 갱신.
* **WIP 해제**: `src/web/static/js/catalog.js` 및 메타데이터에서 `steel_baseplate`의 `is_wip: false`로 정식 온라인 전환.
* **Tier 1 플래그십 5대 부재 완성 검수**: RC 보(`rc_beam`), RC 기둥(`rc_column`), RC 전단벽(`rc_shear_wall`), 철골 보/기둥(`steel_beam_column`), 철골 주각부(`steel_baseplate`) 5종 4열 통합 전수 확인.
* **DoD 검증**: E2E 통합 테스트 Pass, 콘솔 에러 0건.

---

## 4. 세부 하위 구현계획서 구조 (Sub-Specifications)

본 마스터 요구사항 26은 5대 정밀 공정에 따라 아래 5개의 독립 세부 구현계획서로 분할되어 체계적으로 실행됩니다:

1. **[`요구사항26-1_PhaseV1_05_Step1_철골주각부_KDS계산엔진_및_Pydantic스키마.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-1_PhaseV1_05_Step1_철골주각부_KDS계산엔진_및_Pydantic스키마.md)**
   - KDS 14 31 25 주각부 지압·플레이트 휨·KDS 14 20 54 앵커볼트 순수 파이썬 정밀 수식
   - Pydantic v2 데이터 입출력 스키마 체계
   - 강구조설계예제집 13.6.7 / 11.12 3자 삼각대조 및 Pytest TDD
2. **[`요구사항26-2_PhaseV1_05_Step2_철골주각부_원본앱_1대1_서브탭_입력폼_및_모달.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-2_PhaseV1_05_Step2_철골주각부_원본앱_1대1_서브탭_입력폼_및_모달.md)**
   - Pane 1 다중 부재 매니저 주각부 요약 테이블 그리드
   - Pane 2 원본앱 `IDD_STL_USBP_PMODE_DLG` 1:1 계승 4대 서브탭 폼
   - 형강 DB 모달, 앵커볼트 상세 배열 모달, 하중조합 모달 연동
3. **[`요구사항26-3_PhaseV1_05_Step3_철골주각부_2D_VDraw_캔버스_상세도_및_지압응력_인터랙션.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-3_PhaseV1_05_Step3_철골주각부_2D_VDraw_캔버스_상세도_및_지압응력_인터랙션.md)**
   - Pane 3 세로 적층형 2단 그래픽 뷰포트
   - 상단: 주각부 정면 입면도, 앵커 매립, 콘크리트 지압응력 다이어그램 오버레이
   - 하단: 베이스플레이트 평면도, 기둥 단면선, 앵커 위치 심볼, 치수선, 리브 스티프너
4. **[`요구사항26-4_PhaseV1_05_Step4_철골주각부_A4_5대장구분_8단계_KaTeX_구조계산서.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-4_PhaseV1_05_Step4_철골주각부_A4_5대장구분_8단계_KaTeX_구조계산서.md)**
   - Pane 4 상시 순백색(`#ffffff`) A4 고정 구조계산서
   - 원본 5대 장구분 및 8단계 KaTeX 수식 유도 (지압강도, 소요두께, 앵커 인장/전단/복합응력)
   - 상세/요약 분기, 인쇄/PDF/Excel 익스포트
5. **[`요구사항26-5_PhaseV1_05_Step5_철골주각부_4열통합_E2E검증_및_실사용UI_온라인전환.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-5_PhaseV1_05_Step5_철골주각부_4열통합_E2E검증_및_실사용UI_온라인전환.md)**
   - 4-Pane 워크스페이스 100ms 실시간 동시 동기화 검증
   - `catalog.js` 및 메타데이터 WIP 해제 (`is_wip: false`)
   - Tier 1 플래그십 5대 부재 완성 전수 점검 및 브라우저 콘솔 에러 0건 검증

---

## 5. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **수치 무결성**: 강구조설계예제집(2019) 13.6.7(H형강 주각부), 11.12(각관 주각부) 대비 오차 $\le 0.10\%$ (`pytest tests/engine/test_steel_baseplate.py` 100% PASS).
- [ ] **1:1 입력폼**: 원본앱 `IDD_STL_USBP_PMODE_DLG` 4대 서브탭 브라우저 렌더링 및 KS 형강 DB / 앵커 모달 연동 확인.
- [ ] **2D 캔버스**: 세로 적층 2단 뷰포트(주각부 정면 입면/지압응력도 + 베이스플레이트 평면도/치수선) 렌더링 확인.
- [ ] **A4 계산서**: 5대 장구분 8단계 KaTeX 지압, 두께, 앵커 인장/전단/복합응력 수식 출력 확인.
- [ ] **4열 통합**: 100ms 이내 3-View 동시 동기화 및 브라우저 콘솔 에러 0건.
- [ ] **증거 제출**: `docs/16` 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
