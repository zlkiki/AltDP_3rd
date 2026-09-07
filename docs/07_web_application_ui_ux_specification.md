# 07. Web Application UI/UX 및 Midas Design+ 원본 역공학 종합 명세서 (07_web_application_ui_ux_specification.md)

본 문서는 **AltDP_3rd 모던 웹 부재설계 플랫폼**의 프론트엔드 아키텍처, 4-Pane 반응형 레이아웃, 독립 드래그 리사이저 엔진, 중앙 데이터 스토어(SSOT), 다중 단위계 관리, 파라메트릭 인풋 폼, 2D/3D 벡터 그래픽 엔진, 실시간 KDS 구조계산서 렌더러와 **Midas Design+ 원본 데스크톱 앱의 C++/MFC 역공학 분석(Ground Truth)** 및 상호 1:1 매핑 구현 사항을 총체적으로 집대성한 단일 진실 공급원(SSOT) 종합 명세서입니다.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 07_web_application_ui_ux_specification.md 3대 통합 구조도                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PART 1: 전반부] AltDP_3rd 모던 웹 UI/UX 아키텍처 및 디자인 시스템 (우리 앱 우선)                │
│   • 4대 핵심 UX 설계 철학 | 상단 마스터 툴바 | 스마트 사이드바 & 모듈 탐색기                    │
│   • 4분할 작업 영역(부재목록, 폼, 캔버스, 계산서) | 4대 독립 리사이저 | 토큰 & 단축키           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PART 2: 중반부] Midas Design+ 원본 데스크톱 UI/UX 역공학 분석 (Ground Truth)                     │
│   • 원본 MFC/BCGControlBar 프레임워크 | Menu.ini 리본 메뉴 11개 탭 | 4대 폼뷰 & 3대 모드        │
│   • 부재별 DLG_*.ini 다이얼로그 리소스 | VDraw 드로잉 파이프라인 | 원본 계산서 생성 체계        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PART 3: 후반부] 원본 ↔ 모던 웹 1:1 매핑 구현 명세 및 고유 엔지니어링 연동                        │
│   • 4대 메인 폼뷰 & 3대 인터랙션 모드 1:1 웹 구현 매핑 | 54종 모듈 및 2대 렌더링 파이프라인     │
│   • AltDP 고유 자산(FEM, 3D P-M, DXF, 물량, Gen) 4분할 연동 | Zero-Build 단일 서빙 아키텍처     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# [PART 1] AltDP_3rd 모던 웹 UI/UX 아키텍처 (우리 앱 우선)

## 1. 개요 및 4대 핵심 UX 설계 철학 (Design Philosophy)

AltDP_3rd는 건축 구조 엔지니어가 4대 카테고리(RC, Steel, SRC/PC, Misc/RFM) 54개 단위부재의 단면 내력 검토 및 최적 배근 설계를 웹 브라우저에서 쾌속으로 수행할 수 있도록 설계된 **Zero-Build 4분할 올인원 웹 애플리케이션**입니다.

### 🌟 4대 핵심 UX 원칙
1. **무결한 시인성 (Flawless Legibility & Fixed White Sheet)**:
   - 작업 인터페이스는 **다크 테마(Dark Mode)**와 **라이트 테마(Light Mode)**를 자유롭게 전환.
   - 단, **KDS 구조계산서 영역은 실제 A4 인쇄물과의 1:1 완벽 호환을 위해 테마와 무관하게 언제나 순백색(`#ffffff`) 배경과 고대비 텍스트(`#111827`)**를 고정 유지.
2. **독립 4분할 워크스페이스 (Isolated 4-Split Layout)**:
   - 탐색기, 부재 리스트, 입력 폼, 그래픽 정보부, 계산서 뷰포트가 드래그 시 서로 연쇄 간섭 없이 독립적으로 크기 조절.
3. **스마트 자동 숨김 & 고정핀 인터랙션 (Smart Collapsible Sidebar)**:
   - 집중 모드 시 3초 무조작 및 마우스 이탈 시 사이드바가 자동으로 접히며, 고정핀(📌)을 꽂으면 상시 고정 유지 (`Ctrl + B` 토글 지원).
4. **3버튼 통합 액션 파이프라인 (Optimized Action Pipeline)**:
   - **[💾 적용 (Apply)]**, **[⚡ 검토 (Check)]**, **[✨ 설계 (Design)]** 단일화 파이프라인 제공.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Top Master Toolbar : 브랜드/기준 로고 | 🔍 빠른 모듈 검색 (Ctrl+K) | 🌐 단위계(SI/MKS/US) | 테마(🌙/☀️) | 레이아웃 저장/초기화   │
├────────────────────────┬───────────────────────────────────────────────────────────────┬───────────────────────────────┤
│ [Left Sidebar]         │ [Left-Sub: Member & Input]    │ [Center: 2D Graphic View]     │ [Right: KDS Report Dock]      │
│ 📂 설계 모듈 탐색기    │ ┌───────────────────────────┐ │ ┌───────────────────────────┐ │ ┌───────────────────────────┐ │
│  • 카테고리 필스 (RC/St)│ │ 부재 리스트 (+추가/복제)  │ │ │ 2D/3D 대화형 캔버스       │ │ │ 기준 검토 & KDS 계산서  │ │
│  • 트리 전개 레벨 (1~3)│ ├───────────────────────────┤ │ │  • 배근 단면도 (SVG/Canvas)│ │ │  • 상시 순백색 용지 고정 │ │
│  • 💾 저장 / 📂 불러오기│ │ 사용자 입력부 (Input Form)│ │ │  • P-M 상관도 및 3D 곡면  │ │ │  • 실시간 DCR 게이지     │ │
│  • 📌 사이드바 고정핀  │ │  • 브레드크럼 네비게이션  │ │ │  • 줌(Zoom) / 팬(Pan)     │ │ │  • KaTeX 수식 유도 과정  │ │
│  • 실시간 DCR(OK/NG)  │ │  • 파라메트릭 입력 그리드 │ │ │  • 실시간 치수선/콜아웃   │ │ │  • A4 인쇄 / PDF / Excel │ │
│                        │ │  • [적용] [검토] [설계]   │ │ │  • DCR 컬러 레전드 바     │ │ │  • 종합 검토 판정표      │ │
│                        │ └───────────────────────────┘ │ └───────────────────────────┘ │ └───────────────────────────┘ │
├────────────────────────┴───────────────────────────────────────────────────────────────┴───────────────────────────────┤
│ 4대 독립 리사이저 (`layout_resizer.js`): Sidebar(H) ── Left/Right(H) ── Input/Canvas(H) ── Member/Form(V)            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 상단 마스터 툴바 (Top Master Toolbar)

상단 툴바는 전역 설정 및 빠른 도구 기능을 제공합니다:

1. **브랜드 & 기준 배지**:
   - `AltDP Member Designer` 로고 + `KDS 2022 / KDS 14 20 00 / 14 31 00` 기준 태그.
2. **사이드바 토글 버튼 (Ctrl+B)**:
   - 좌측 네비게이터를 즉시 열고 닫는 단축키 및 토글 버튼.
3. **초고속 모듈 검색바 (Ctrl+K, `#quick-search`)**:
   - 54종 단위부재(보, 기둥, 전단벽, 슬래브, 기초, H형강, 접합부 등) 퍼지 검색 및 즉시 활성화.
4. **4대 단위계 실시간 전환기 (`unit_manager.js`)**:
   - `SI`: $\text{kN, mm, MPa, kN}\cdot\text{m}$ (기본값)
   - `SI_M`: $\text{kN, m, kPa, kN}\cdot\text{m}$
   - `MKS`: $\text{tonf, m, kgf/cm}^2\text{, tonf}\cdot\text{m}$
   - `US`: $\text{kip, in, ksi, ft}\cdot\text{kip}$
   - *단위계 변경 시 입력폼 값, 캔버스 치수, 계산서 수식이 0.01초 내 자동 변환 및 유효숫자 포맷팅.*
5. **테마 & 레이아웃 관리**:
   - **다크/라이트 테마 (🌙/☀️)**: 고대비 엔지니어링 테마 토글 (`theme_manager.js`).
   - **레이아웃 기본값 저장 (`📌 Save Layout`)**: 분할 비율 및 사이드바 상태를 `localStorage`에 영속화.
   - **레이아웃 초기화 (`🔄 Reset Layout`)**: 기본 황금비 분할로 원클릭 복원.

---

## 3. 계층형 모듈 탐색기 및 스마트 사이드바 (Left Sidebar)

### 3.1. 사이드바 인터페이스 구성
* **프로젝트 파일 입출력 (Project I/O)**:
  - `💾 저장 (Export)`: 프로젝트 내 모든 부재의 제원, 재료, 배근, 하중을 단일 `.json` 파일로 다운로드 (`Ctrl + S`).
  - `📂 불러오기 (Import)`: 저장된 JSON 프로젝트 파일을 로드하여 다중 부재 상태 복원.
  - `📌 핀 고정 토글`: 워크스페이스 내 고정 패널 또는 마우스 이탈 시 자동 숨김(Auto-Hide, 3초 지연) 전환.
* **카테고리 필터 필스 (Category Pills)**:
  - `전체` | `RC` | `Steel` | `PC` | `기타` 원클릭 탭 필터링.
* **트리 확장 레벨 제어 (Tree Level Controller)**:
  - `Level 1`: 대분류(RC, Steel, SRC 등)만 표시.
  - `Level 2`: 중분류(보, 기둥, 전단벽, 슬래브 등)까지 전개.
  - `Level 3`: 프로젝트에 등록된 모든 개별 부재 노드까지 전체 전개.

### 3.2. 모듈별 부재 하위 트리 (Member Sub-Tree)
* 각 모듈에 등록된 부재(`Member`)가 1개 이상 존재할 경우, 모듈 하위에 부재 목록(`M-1`, `M-2` 등)을 서브트리 노드로 계층 렌더링.
* 모듈별 접기/펼치기 토글 화살표(`▶`/`▼`) 및 부재 개수 배지(`(N)`) 제공.
* 각 부재 항목별 DCR 상태 2단계 텍스트 글자 표기 (칩/배경색 제거, 폰트 컬러로만 구분):
  - **OK (`DCR ≤ 1.000`)**: **녹색 글자 (`OK`)** 표기.
  - **NG (`DCR > 1.000`)**: **빨간색 글자 (`NG`)** 표기 (클릭 시 초과 항목 위치로 즉시 이동).

---

## 4. 4분할 작업 영역 상세 명세 (4-Pillars)

### 4.1. Pane 1: 다중 부재 매니저 (Top-Left: `#pane-member-list`)
* **컴포넌트**: `member_manager.js`
* **주요 기능**:
  - `+ 추가 (Add)`: 현재 활성 모듈에 신규 부재 생성 (M-1, M-2, ...).
  - `복제 (Duplicate)`: 선택된 부재의 제원, 재료, 배근을 그대로 복제.
  - `삭제 (Delete)`: 부재 삭제 및 직전 부재 자동 활성화.
  - `이름 변경 (Rename)`: 더블클릭 또는 인라인 편집으로 부재명 변경.
  - 부재 전환 시 현재 입력 폼 상태를 자동 저장하고 대상 부재의 데이터를 0.01초 내 복원.
  - 부재 테이블에 단면 크기($b \times h$), 주요 철근, DCR 상태 실시간 요약 표시.

### 4.2. Pane 2: 파라메트릭 사용자 입력부 (Bottom-Left: `#pane-input-form`)
* **컴포넌트**: `form_generator.js`, `form_combobox.js`
* **주요 구성**:
  - **2단 적층형 헤더 (Vertical Stack Header)**:
    - 1행: `⚙️ 사용자 입력부 (Input)` 타이틀 바 및 활성 부재 뱃지(`[M-1]`).
    - 2행: 사용자 입력부 전체 가로 폭(100%)을 사용하는 전용 모듈 경로 배너 (`RC › 보 (Beam) › 직사각형 보`).
  - **KS 표준 콤보박스 (`form_combobox.js`)**:
    - 단일 클릭 즉각 드롭다운 팝업 리스트 + 키보드 직접 타이핑 하이브리드 지원.
    - KS D 3504 이형철근(`D10`~`D57`), 콘크리트 강도(`fck`), 철근 강종(`SD400` 등), 강재 강종(`SM355` 등), 고력볼트(`F10T`), KS 형강 규격 DB 연동.
  - **파라메트릭 입력 그룹**:
    - **재료 특성 (Material)**: 콘크리트 강도($f_{ck}$), 주철근($f_y$), 전단철근($f_{ys}$), 경량계수($\lambda$).
    - **단면 제원 (Geometry)**: 폭($b$), 높이($h$), 피복두께($d_c$), 슬래브 유효폭($b_{eff}$), 두께($t_f$).
    - **배근 상세 (Rebar Layout)**:
      - 상부근 / 하부근: 직경(D10~D35), 단수(1단/2단), 열별 개수.
      - 늑근 / 대근: 직경(HD10/HD13), 간격($s$: 100~300mm), Leg 수(2, 3, 4 Legs).
      - 표피철근: 보 춤 $h \ge 900\text{mm}$ 초과 시 측면 스킨철근 자동 배치 및 균등 분할.
    - **설계 부재력 (Loads)**: 계수 축력($P_u$), 휨모멘트($M_u$), 전단력($V_u$), 비틀림($T_u$).
  - **3버튼 통합 액션 툴바 & 단일화 파이프라인**:
    - **[💾 적용 (Apply)] 버튼**: 현재 폼의 수정값들을 `ProjectStore` 메모리(활성 부재 `inputs`)에 즉시 저장하고, 2D 캔버스, 부재 리스트 및 사이드바 트리를 실시간 갱신.
    - **[⚡ 검토 (Check)] 버튼**: 항상 **[적용]**을 1순위로 선행 실행한 뒤, 현재 입력 조건으로 백엔드 KDS 엔진을 호출하여 계산서 및 DCR 갱신.
    - **[✨ 설계 (Design)] 버튼**: 항상 **[적용]**을 1순위로 선행 실행한 뒤, `auto_designer.js` 엔진을 구동하여 $DCR \le 1.0$을 만족하는 최적 배근/단면을 자동 산출.

### 4.3. Pane 3: 2D 대화형 그래픽 정보부 (Center: `#pane-graphic-view`)
* **컴포넌트**: `visual/vector/vector_core.js`, `vector_rc_sec.js`, `vector_footing.js`, `vector_slab.js`, `vector_steel.js`, `canvas_renderer.js`, `zoom_controller.js`, `legend_bar.js`
* **주요 구성**:
  - **모듈형 2D 벡터 서브 렌더러**:
    - `CanvasCore`: ResizeObserver 반응형 종횡비 유지, 4대 단위계 치수선 포맷팅, 테마 팔레트 연동.
    - `DrawRc`: RC 26종 (보 1/2단 배근 및 25mm 이격, 회색 점선 스터럽, 기둥 둘레배근 및 Cross-tie, T형보, 기초 말뚝 그리드, 슬래브).
    - `DrawSteel`: Steel 13종 (H형강 플랜지/웨브 및 규격명 라벨, 중공 박스/파이프, 베이스플레이트 앵커볼트 4점).
    - `DrawPcMisc`: PC 7종/Misc 8종 (더블티 리브 및 긴장재 텐던, 사다리꼴 코벨/브라켓 인장주근 및 하중 화살표, SRC 매립형 H단면).
    - `LegendBar`: 좌측 상단 DCR 수치 뱃지 및 4단계 컬러(안전/적합/경고/초과) 스펙트럼 바.
  - **치수선 및 지시선 (Callout)**:
    - 단면 폭($b$), 높이($h$), 유효깊이($d$), 피복두께 치수선 및 화살표.
    - 배근 텍스트 태그 (예: `Top: 4-D25 (2단)`, `Stirrup: HD10 @ 150 (2-Legs)`).
  - **대화형 제어**:
    - 마우스 휠 줌(Zoom In/Out), 드래그 팬(Pan), `🔍 리셋` 뷰포트 맞춤.
    - 철근/요소 호버 시 직경, 중심거리, 단면적 툴팁 표시.

### 4.4. Pane 4: KDS 구조계산서 렌더러 (Right: `#pane-right-report`)
* **컴포넌트**: `redcr_common_renderer.js`, `sheetFormulas.js`, `verdictBadge.js`, `zoom_controller.js`
* **상시 순백색 용지 고정 (Pure White Sheet Container)**:
  - 다크 모드에서도 계산서 용지 내부(`.a4-sheet-container`)는 순백색(`#ffffff`) 배경과 고대비 텍스트(`#111827`, `#1f2937`)를 고정 유지하여 A4 인쇄물과의 1:1 완벽 호환 보장.
  - 패널 너비가 변해도 테이블과 수식이 왜곡되지 않도록 고정폭(794px / 210mm) 유지.
* **Universal 4-Pillar 계산서 조립 구조**:
  ```
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ Universal 4-Pillar Calculation Report Structure                                        │
  ├───────────────────────────────────────────┬────────────────────────────────────────────┤
  │ [Panel A: 좌측 시각화 & 입력 요약]        │ [Panel B: 우측 종합 검토표 & KDS 수식 과정]│
  │                                           │                                            │
  │ ③ [영역 3] 비주얼 단면 형상 & 배근도       │ ④ [영역 4] 한계상태별 안전성 종합 검토표    │
  │   • 고해상도 SVG 벡터 배근도              │   • 휨, 전단, 처짐, 균열 Demand vs Capacity│
  │   • 치수선 및 주요 배근 스펙 태그        │   • 실시간 DCR 및 OK/NG 판정 배지          │
  │                                           │                                            │
  │ ① [영역 1] 설계 입력 파라미터 요약        │ 📈 [공학 다이어그램 카드]                   │
  │   • 재료 강도, 단면 크기, 계수 하중      │   • P-M 상관곡선 / 지반 접지압 분포도      │
  │   • 환경 조건 및 내진 설계 범주           │                                            │
  │                                           │ ② [영역 2] 기준 기반 Step-by-Step 수식 과정 │
  │                                           │   • KaTeX LaTeX 렌더링 정밀 수식           │
  │                                           │   • a, c, ε_t, φM_n, V_c, V_s              │
  └───────────────────────────────────────────┴────────────────────────────────────────────┘
  ```
* **확대율 컨트롤러 & 마우스 휠 줌 (`zoom_controller.js`)**:
  - `[-]`, `[100%]`, `[+]`, `[Fit]` 버튼 및 줌 슬라이더(50% ~ 200%) 제공.
  - **`Ctrl + 마우스 휠` 인터랙션**: 리포트 영역 내에서 마우스 휠 조작 시 실시간 줌 인/아웃 지원.
* **A4 출력 및 멀티 익스포트**:
  - A4 표준 규격(210mm × 297mm, 여백 20mm, 페이지네이션, 머리말/꼬리말) CSS Paged Media 인쇄 (`@media print` 자동 서식).
  - WeasyPrint 기반 고품질 PDF 다운로드.
  - OpenPyXL 기반 다중 시트 통합 Excel(`.xlsx`) 내보내기.

---

## 5. 4대 독립 리사이저 엔진 (`layout_resizer.js`)

각 분할 패널은 다른 패널에 왜곡을 주지 않고 독립적으로 크기를 조절할 수 있습니다:

| 리사이저 ID | 조절 대상 | 동작 방식 및 바운딩 제약 |
|---|---|---|
| `resizer-sidebar-h` | 좌측 사이드바 ↔ 메인 워크스페이스 | 좌우 드래그 (너비: 200px ~ 480px) |
| `resizer-main-h` | 좌측 영역(인풋/캔버스) ↔ 우측 계산서 | 좌우 드래그 (좌우 분할 20% ~ 80%) |
| `resizer-left-h` | 인풋 폼 영역 ↔ 그래픽 캔버스 | 좌우 드래그 (인풋과 캔버스 분할 25% ~ 75%) |
| `resizer-left-v` | 부재 리스트 테이블 ↔ 인풋 폼 | 상하 드래그 (부재목록 높이: 80px ~ 400px) |

---

## 6. 디자인 시스템 토큰 (Design Tokens)

### 6.1. 테마 변수 (Color Palette)

| 토큰명 | 다크 테마 (Dark Mode) | 라이트 테마 (Light Mode) | A4 계산서 (Fixed White) |
| :--- | :--- | :--- | :--- |
| `--bg-primary` | `#0b0e14` (심해 네이비) | `#f8fafc` (소프트 화이트) | `#ffffff` (순백색 고정) |
| `--bg-secondary` | `#121722` (다크 카드) | `#ffffff` (순백색) | `#ffffff` |
| `--bg-surface` | `#20293a` (엘리베이션) | `#e2e8f0` (연회색) | `#f8fafc` (수식 블록) |
| `--border` | `#2b364c` | `#cbd5e1` | `#e5e7eb` (테이블 선) |
| `--text-main` | `#f1f5f9` (고대비 백색) | `#0f172a` (진한 네이비) | `#111827` (선명한 블랙) |
| `--text-muted` | `#94a3b8` | `#64748b` | `#4b5563` (보조 수식) |
| `--accent` | `#3b82f6` (블루) | `#2563eb` (로열 블루) | `#1d4ed8` (강조 링크) |
| `--success` | `#10b981` (안전/합격) | `#059669` | `#047857` (DCR $\le 1.0$) |
| `--danger` | `#ef4444` (초과/NG) | `#dc2626` | `#b91c1c` (DCR $> 1.0$) |

### 6.2. 타이포그래피 (Typography)
* **기본 본문 폰트**: `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
* **헤딩 및 타이틀**: `'Outfit', sans-serif`
* **구조 수식 및 코드**: `'Fira Code', 'Cascadia Code', monospace`

---

## 7. 키보드 단축키 매핑 (Global Shortcuts)

* `Ctrl + K`: 상단 빠른 모듈 검색창 포커스
* `Ctrl + B`: 좌측 사이드바 접기 / 펼치기 토글
* `Ctrl + S`: 프로젝트 전체 데이터 JSON 내보내기 (Export)
* `Ctrl + Wheel` (계산서 영역): A4 계산서 실시간 확대/축소 (50% ~ 200%)
* `Esc`: 모듈 검색창 닫기 및 팝업 닫기

---

## 8. 프론트엔드 모듈 및 자산 매핑 구조

AltDP_2nd의 웹 프론트엔드 파일을 AltDP_3rd 프로젝트로 직접 연계/통합하기 위한 파일 매핑 경로입니다:

| 기능 도메인 | AltDP_2nd 소스 경로 | AltDP_3rd 타겟 경로 | 주요 역할 |
|---|---|---|---|
| **메인 템플릿** | `AltDP_2nd/web/index.html` | `src/web/templates/index.html` | 4-Pane 레이아웃, 탑 네비바, 반응형 뷰포트 마크업 |
| **CSS 스타일** | `AltDP_2nd/web/css/*.css` | `src/web/static/css/*.css` | `theme.css`, `layout.css`, `components.css`, `canvas.css`, `report.css`, `print.css` |
| **리사이저** | `AltDP_2nd/web/js/components/layout_resizer.js` | `src/web/static/js/components/layout_resizer.js` | 4대 독립 리사이저 & 스마트 사이드바 제어 |
| **부재 관리자** | `AltDP_2nd/web/js/components/member_manager.js` | `src/web/static/js/components/member_manager.js` | 다중 부재 CRUD 및 폼-스토어 동기화 |
| **폼 생성기** | `AltDP_2nd/web/js/components/form_generator.js` | `src/web/static/js/components/form_generator.js` | 파라메트릭 인풋 폼 동적 빌더 & 실시간 검증 |
| **콤보박스** | `AltDP_2nd/web/js/components/form_combobox.js` | `src/web/static/js/components/form_combobox.js` | KS 철근/강재/콘크리트 표준 콤보 위젯 |
| **중앙 스토어** | `AltDP_2nd/web/js/store/project_store.js` | `src/web/static/js/store/project_store.js` | 전역 상태 관리, JSON I/O, 로컬스토리지 영속화 |
| **단위계 매니저** | `AltDP_2nd/web/js/store/unit_manager.js` | `src/web/static/js/store/unit_manager.js` | SI/MKS/US 4대 단위계 자동 환산 |
| **2D 벡터 렌더러** | `AltDP_2nd/web/js/visual/vector/*.js` | `src/web/static/js/visual/vector/*.js` | `vector_core.js`, `vector_rc_sec.js`, `vector_footing.js`, `vector_slab.js`, `vector_steel.js` |
| **KDS 계산서** | `AltDP_2nd/web/js/report/redcr_common_renderer.js` | `src/web/static/js/report/redcr_common_renderer.js` | KaTeX 수식, 종합 검토표, 한계상태 판정 배지 렌더러 |
| **자동 설계기** | `AltDP_2nd/web/js/designer/auto_designer.js` | `src/web/static/js/designer/auto_designer.js` | $DCR \le 1.0$ 만족 최적 단면/배근 자동 산출기 |

---

# [PART 2] Midas Design+ 원본 데스크톱 UI/UX 역공학 분석 (Ground Truth)

## 9. Midas Design+ 원본 윈도우 프레임워크 구조

원본 Midas Design+(`Design+.exe`)은 **MFC (Microsoft Foundation Classes)** 및 **BCGControlBar Pro (v31.2, `BCGCBPRO3120u141.dll`)** 라이브러리를 기반으로 구축된 SDI (Single Document Interface) 엔지니어링 데스크톱 프로그램입니다.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Midas Design+ 원본 윈도우 프레임워크 (`CMainFrame` : `CBCGPFrameWnd`)                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 상단 리본 바 (Ribbon Bar - `CBCGPRibbonBar`): 메인/모드/부재/하중/설정/도구 탭 네비게이션             │
│ 2. 퀵 액세스 툴바 (QAT): 신규, 열기, 저장, 실행취소(Undo), 재실행(Redo), 일괄출력                         │
├───────────────────┬─────────────────────────────────────────────────┬───────────────────────────────────┤
│ 3. 좌측 도킹 바   │ 4. 메인 뷰 에리어 (`CChildFrame` / Multi-View)   │ 5. 우측/중앙 인풋 및 검토 컨트롤  │
│    (WorkTree Dock)│ ┌─────────────────────────────────────────────┐ │ ┌───────────────────────────────┐ │
│   • 부재 탐색 트리│ │ 2D/3D 그래픽 캔버스 (`DPLUS_VDraw.dll`)      │ │ │ 파라메트릭 인풋 폼            │ │
│   • 층별/타입별   │ │  - 단면 배근도 (`CODABeamBase`, `CODABaseCol`)│ │ │  (재료, 단면, 하중, 배근)     │ │
│   • DCR 안전율 배지│ │  - P-M 상관도 및 3D 곡면 다이어그램          │ │ └───────────────────────────────┘ │
│   • 부재 추가/삭제│ │  - 철골 접합부 / 베이스플레이트 2D CAD      │ │ ┌───────────────────────────────┐ │
│                   │ └─────────────────────────────────────────────┘ │ │ 실시간 DCR 및 상태 게이지     │ │
│                   │ ┌─────────────────────────────────────────────┐ │ └───────────────────────────────┘ │
│                   │ │ 4대 메인 폼뷰 전환 (Memb / List / Dwg / Qntt) │ │ ┌───────────────────────────────┐ │
│                   │ └─────────────────────────────────────────────┘ │ │ KDS 실시간 수식 검토 요약로그  │ │
├───────────────────┴─────────────────────────────────────────────────┴───────────────────────────────────┤
│ 6. 하단 상태 표시줄 (Status Bar - `CBCGPRibbonStatusBar`): 현재 단위계, 좌표계, Zoom 배율, 해석 상태     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. 원본 리본 메뉴 구성 체계 (`Menu.ini` 심층 분석)

`Language/Korean/Menu.ini`에서 추출된 리본 메뉴 탭, 패널 및 세부 명령 항목의 전체 인벤토리입니다.

### 10.1. 리본 탭 및 패널 상세 분류

| 리본 탭 (Bar) | 카테고리 패널 | 주요 명령 항목 및 기능 (Action Items) | 원본 리소스 키 |
|---|---|---|---|
| **메인 (Main)** | 파일 / 프로젝트 | 새 파일, 열기, 저장, 다른 이름으로 저장, 가져오기(Gen/ADS/CAD), 내보내기, 일괄 출력, 최근 파일, 종료 | `IDS_MAIN_RIBBON_MENU_Main` |
| **모드/연동 (Mode/Link)** | 사용자 입력 환경 | • **프로젝트 모드** (`IDS_RIBBON_MENU_MODE_PROJECT`): 전체 건물 부재 일괄 관리<br>• **심플 모드** (`IDS_RIBBON_MENU_MODE_SIMPLE`): 단일 부재 급속 설계<br>• **검토 모드** (`IDS_RIBBON_MENU_MODE_CHECK`): 기존 배근의 안전성 검토 | `IDS_RIBBON_PANL_MODE_UI` |
| | 편집 모드 (4대 뷰) | • **부재 (`CMainFormViewMemb`)**: 단일 단면 파라메트릭 설계/검토<br>• **부재 목록 (`CMainFormViewList`)**: 전체 부재 스프레드시트 일괄 관리<br>• **도면 (`CMainFormViewDraw`)**: 배근 상세도 CAD 렌더링<br>• **물량 (`CMainFormViewQntt`)**: 콘크리트/철근 물량 집계표 | `IDS_RIBBON_PANL_MODE_EDIT` |
| | 연동 (MIDAS Link) | MIDAS Gen/Building/Civil 모델 연동, 연동 옵션, 연동 DB 동기화 | `IDS_RIBBON_PANL_LINK` |
| **콘크리트 (RC)** | 철근 콘크리트 부재 | 슬래브, 보, 기둥, 임의 형상 기둥, 전단벽, 이형 벽체, 지하외벽, 옹벽, 앵커볼트, 버트레스, 계단, 코벨/브라켓 | `IDS_RIBBON_BARR_RCS` |
| | 기초 (Footing) | 독립 기초, 복합 기초, 줄 기초, 말뚝 기초 | `IDS_RIBBON_PANL_RCS_FOOTING` |
| | 강도 테이블 | 철근 단면적 및 이음/정착 길이 기준 강도표 | `IDS_RIBBON_PANL_RCS_TABLE` |
| **강구조 (STEEL)** | 철골 부재 | 철골보, 철골기둥, 가새(Brace), 트러스, 크레인 주행보, 중도리/띠장, 웨브 개공보, 파형웨브보 | `IDS_RIBBON_BARR_STEEL` |
| | 접합부 (Connection) | 전단 볼트 접합부, 모멘트 볼트 접합부, 용접 접합부, 임베디드 플레이트, 주각부 베이스플레이트 | `IDS_RIBBON_PANL_STL_CONN` |
| | 내진 설계 도구 | 비지지 길이 계산기, 브레이스 강도 검토, 링크 스티프너, V형 브레이스 지지보 강도 | `IDS_RIBBON_PANL_SEISMIC_DESIGN_TOOL` |
| **합성부재 (SRC)** | 합성 부재 | 합성보 (데크플레이트), SRC 기둥 (매입형), CFT 기둥 (충전형), SRC 주각부 | `IDS_RIBBON_BARR_SRC` |
| **알루미늄 (ALU)** | 알루미늄 부재 | 보/기둥, 임의형상 보/기둥, 커튼월 멀리온, 루버 프레임 | `IDS_RIBBON_BARR_ALU` |
| **보강 (RFM)** | 구조 보강 | RC 슬래브/보/기둥 탄소섬유(CFRP) 보강, 강판 접착 보강, 단면증설 | `IDS_RIBBON_BARR_RFM` |
| **성능기반설계 (PBD)** | PBD 부재 검토 | RC 보/기둥/전단벽 비선형 변형능력 및 성능 평가 | `IDS_RIBBON_BARR_PBD` |
| **하중 (Load)** | 설계 하중 | 설계 하중 입력, 하중 조합 생성기, Word/Excel/RTF 내보내기 | `IDS_RIBBON_BARR_LOAD` |
| **설정 (Option)** | 설계 기준 & DB | 설계 기준(KDS 14 20 00 / 14 31 00 / ACI / AISC), 철근 DB, 형강 DB | `IDS_RIBBON_BARR_OPTION` |
| | 부재별 상세 설정 | 설계 설정, 검토 설정, 도면 설정, 계산서 설정, 사용자 설정 | `IDS_RIBBON_PANL_DGN_OPTION` |
| **도구 (Tool)** | 유틸리티 | 일괄 설계, 부재 재정렬, 단위 변환기, 정착/이음 계산기, 단면 변환 도구 | `IDS_RIBBON_BARR_TOOL` |

---

## 11. 원본 4대 메인 폼뷰 (`CMainFormView*`) 구조

Midas Design+은 선택된 부재와 작업 단계에 따라 4가지 전용 폼뷰 클래스를 동적으로 전환합니다.

1. **`CMainFormViewMemb` (단면 상세 설계/검토 뷰)**:
   - 선택된 단일 부재의 파라메트릭 입력, 2D 단면 배근도 렌더링, P-M 상관도 및 안전율(DCR) 검토.
2. **`CMainFormViewList` (다중 부재 일괄 관리 뷰)**:
   - 층별/부재별 스프레드시트 그리드 테이블에서 프로젝트 내 모든 부재를 일괄 검토 및 정렬/필터링.
3. **`CMainFormViewDraw` (도면 생성 및 CAD 뷰)**:
   - 완성된 부재의 2D 배근 상세도, 입면도, 배근 일람표 CAD 도면 렌더링 및 DWG 내보내기.
4. **`CMainFormViewQntt` (물량 산출 및 집계표 뷰)**:
   - 콘크리트 체적($\text{m}^3$), 거푸집 면적($\text{m}^2$), 철근/형강 중량(ton) 자동 집계 및 엑셀 출력.

---

## 12. 원본 3대 사용자 인터랙션 모드 (Interaction Modes)

| 모드명 | 원본 C++ 클래스 접미사 | 주요 역할 및 동작 방식 |
|---|---|---|
| **P-Mode** (Design Mode) | `*PModeDlg`<br>(예: `CURBBPModeDlg`, `CFootPModeDlg`) | • 파라메트릭 자동 설계 모드<br>• 단면 크기, 사용 재료, 설계 하중 입력 시 최적 철근/단면 자동 배근 산출 |
| **S-Mode** (Check Mode) | `*SModeDlg`<br>(예: `CURBBSModeDlg`, `CSlabSModeDlg`) | • 단면 검토 모드<br>• 사용자가 직접 지정한 단면 제원 및 배근에 대해 KDS 안전율(DCR) 정밀 검토 |
| **M-Mode** (List/Batch Mode) | `*MListDlg`<br>(예: `CURBBMListDlg`, `CSteelCraneGirderListDlg`) | • 다중 부재 일괄 관리 모드<br>• 층별/부재별 테이블 그리드에서 여러 단면을 일괄 검토 및 최악 DCR 부재 필터링 |

---

## 13. 부재별 원본 다이얼로그 폼 구조 (`DLG_*.ini` 분석)

### 13.1. RC 부재 다이얼로그 (`DLG_DPLUS_RCS.ini`)
* `IDD_RCS_BEAM_PMODE_DLG`: RC 보 재료(fck, fy, fys, 경량콘크리트), 단면(b, h, 피복, T형 유효폭), 표피철근, 처짐/내진(SMF/IMF/OMF/필로티), 배근유형(전단면/양단부중앙부), 주철근 간격/이음, 균열조건.
* `IDD_RCS_COLUMN_PMODE_DLG`: RC 기둥 제원, 주철근 원형/사각 배열, 띠철근/나선철근, P-M 상호작용 검토.
* `IDD_RCS_WALL_PMODE_DLG`: 전단벽 두께, 길이, 층고, 특수경계요소, 수평/수직 철근비.
* `IDD_RCS_SLAB_PMODE_DLG`: 1방향/2방향 슬래브 경간, 지점 조건, 배근 유형 A/B/C, 장단기 처짐 조건.
* `IDD_RCS_FOOT_PMODE_DLG`: 독립/복합 기초 치수, 기둥 배치, 상재하중, 지반 지비력.
* `IDD_RCS_RETAINING_WALL_INPUT_DLG`: 옹벽 저판, 벽체 높이, 토압 조건, 활동/전도/지반지지력 안정성.

### 13.2. Steel 부재 및 접합부 다이얼로그 (`DLG_DPLUS_Steel.ini`)
* `IDD_STL_BEAMCOLUMN_INPUT_DLG`: H형강, 각형강관 단면, 비지지길이($L_b$), 모멘트구배계수($C_b$), 휨좌굴/비틀림좌굴.
* `IDD_STL_BOLTCONNECTION_INPUT_DLG`: 고력볼트(F10T/F8T/A325), 직경, 볼트 배열(게이지/피치/연단거리), 마찰/지압.
* `IDD_STL_WELDING_INPUT_DLG`: 모살/맞댐 용접, 용접 위치, 유효 용접 치수.
* `IDD_STL_USBP_PMODE_DLG`: 베이스플레이트 가로/세로/두께, 앵커볼트 인장/전단, 기초 콘크리트 지압.

---

## 14. 원본 2D/3D 드로잉 엔진 분석 (`DPLUS_VDraw.dll`)

* **핵심 드로잉 클래스**: `CODABeamBase`, `CODABaseColumn`, `CODABaseFooting`, `CODABaseWall`, `CODABaseSteel`
* **주요 렌더링 메소드 파이프라인**:
  - `DrawSect`, `DrawFrameBody`: 콘크리트 외곽선 및 음영 채우기
  - `DrawStirrup`: 피복두께 옵셋 및 135도 갈고리(Hook) 절곡 형상
  - `DrawMainBar`: 주철근 기하학적 중심 좌표 산출 및 솔리드 서클
  - `DrawTxtInfo`, `DrawFrameHeadText`: 치수선(b, h, d), 배근 텍스트 태그 지시선

---

## 15. 원본 계산서 생성 체계 (`DgnReportBase.ini`, `GENDgnReportKR.ini`)

* **출력 목차 구조**:
  1. 일반 사항 (General Info): 설계 기준, 단위계, 부재명
  2. 재질 및 단면 (Material & Section): $f_{ck}, f_y, E_c$, 단면 크기, 2D 단면도
  3. 설계 하중 (Design Loads): 계수 하중 조합
  4. 단면 검토 (Member Check):
     - 휨모멘트 및 전단 강도 검토 ($M_n, \phi M_n, V_c, V_s, \phi V_n$)
     - 처짐 검토 (단기/장기 처짐, 시간 의존 계수)
     - 균열 검토 (건조/기타 환경, 허용 균열폭)
  5. 종합 판정: `IDS_DGNREPORTBASE_ARROW_OK` ("  →  O.K"), `IDS_DGNREPORTBASE_ARROW_NG` ("  →  N.G")

---

# [PART 3] 원본 ↔ 모던 웹 1:1 매핑 구현 명세 및 고유 엔지니어링 연동

## 16. Midas Design+ 4대 폼뷰 및 3대 인터랙션 모드 1:1 웹 구현 매핑

원본 Midas Design+의 데스크톱 SDI 환경을 AltDP_3rd의 반응형 웹 환경으로 1:1 완벽 이식하기 위한 구조적 매핑 사양입니다:

### 16.1. 4대 메인 폼뷰 1:1 웹 구현 매핑
1. **Memb View (`CMainFormViewMemb`) $\rightarrow$ 독립 4분할 워크스페이스**:
   - 단일 부재 정밀 4분할 워크스페이스 (속성 그리드 ↔ 2D 단면 배근도 ↔ P-M 상관곡선/DCR ↔ KDS 실시간 요약서).
   - `pane-member-list`, `pane-input-form`, `pane-graphic-view`, `pane-right-report`의 4열 동시 구동.
2. **List View (`CMainFormViewList`) $\rightarrow$ 상단 [부재 목록] 뷰 (`batch_grid.js`)**:
   - 다중 부재 일괄 스프레드시트 검토 뷰 (층별/부재별 트리 네비게이터, Excel형 그리드, 원클릭 일괄 DCR 히트맵).
3. **Draw View (`CMainFormViewDraw`) $\rightarrow$ 상단 [도면] CAD 뷰 (`draw_cad.js`)**:
   - 2D 배근 상세도 및 일람표 CAD 뷰어 (보/기둥 단면/입면 벡터 드로잉, 스케줄 테이블, DXF/SVG 다운로드).
4. **Qntt View (`CMainFormViewQntt`) $\rightarrow$ 상단 [물량] 대시보드 뷰 (`qntt_summary.js`)**:
   - 콘크리트/거푸집/철근/강재 자동 물량 산출 대시보드 (D10~D32 직경별 물량, 형강 중량, 도넛 차트 및 Excel 내보내기).

### 16.2. 3대 인터랙션 모드 1:1 웹 파이프라인 매핑
1. **P-Mode (Parametric Auto-Design Mode) $\rightarrow$ [✨ 설계 (Design)] 버튼 파이프라인**:
   - 설계 단면 가정 및 KDS 강도설계법/허용응력설계법에 따른 최적 철근 배근 및 형강 규격 자동 제안 (`auto_designer.js`).
2. **S-Mode (Section Check Mode) $\rightarrow$ [⚡ 검토 (Check)] 버튼 파이프라인**:
   - 기 배근된 단면 및 단면 제원에 대해 모멘트/전단/축력/비틀림 DCR을 즉각 해석/검토하는 엔지니어링 검토 모드.
3. **M-Mode (Member Management Mode) $\rightarrow$ 사이드바 및 다중 부재 매니저 (`member_manager.js`)**:
   - 부재 태그, 그룹핑, 층(Story) 배치, 하중 케이스 연계 등 구조 모델 메타데이터를 통합 관리하는 모드.

---

## 17. 54종 단위부재 분류 및 2대 렌더링 파이프라인 (SSOT)

AltDP_2nd의 정식 54종 모듈 체계와 2대 서식(특별 33종 vs 일반 21종)을 100% 수용합니다:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 54종 단위설계 모듈 4대 카테고리 매트릭스                                              │
├───────────────────┬──────────────┬──────────────┬──────────────────────────────────────┤
│ 카테고리 (Category)│ 하위 그룹    │ 모듈 수      │ 주요 렌더러 파이프라인                │
├───────────────────┼──────────────┼──────────────┼──────────────────────────────────────┤
│ 1. RC 콘크리트    │ 보, 기둥,    │ 26종 (48.1%) │ 🌟 특별: VectorRcSec, VectorFooting, │
│    (`rc`)         │ 기초, 슬래브,│              │    VectorSlab, VectorWall            │
│                   │ 벽체         │              │    Beam/Column/Footing/Slab/Wall     │
│                   │              │              │    ReportGenerator (19종)            │
│                   │              │              │ 📋 일반: DrawRc + RedcrCommon (7종)  │
├───────────────────┼──────────────┼──────────────┼──────────────────────────────────────┤
│ 2. Steel 강구조   │ 부재, 접합부,│ 13종 (24.1%) │ 🌟 특별: VectorSteel + SteelReport   │
│    (`steel`)      │ 합성, 특수   │              │    Generator (12종)                  │
│                   │              │              │ 📋 일반: DrawSteel + RedcrCommon (1종)│
├───────────────────┼──────────────┼──────────────┼──────────────────────────────────────┤
│ 3. PC/PSC 구조    │ 보, 슬래브,  │ 7종 (13.0%)  │ 📋 일반: DrawPcMisc + RedcrCommon    │
│    (`pc`)         │ 접합부       │              │    (7종 전수)                        │
├───────────────────┼──────────────┼──────────────┼──────────────────────────────────────┤
│ 4. Misc 기타/상세 │ 철근, SRC,   │ 8종 (14.8%)  │ 🌟 특별: VectorRcSec (SRC 2종)       │
│    (`misc`)       │ 특수요소     │              │ 📋 일반: DrawPcMisc + RedcrCommon (6종)│
└───────────────────┴──────────────┴──────────────┴──────────────────────────────────────┘
```

---

## 18. AltDP_3rd 고유 엔지니어링 자산의 4분할 UI 심리스 연동 체계

AltDP_3rd에서 개발된 고정밀 수치해석 및 자동화 자산은 4분할 레이아웃에 아래와 같이 유기적으로 결합됩니다:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ AltDP_3rd 고유 엔진 ↔ 4분할 인터랙티브 워크스페이스 연동 맵                                                  │
├──────────────────────┬──────────────────────────────┬────────────────────────────────────────────────────────┤
│ AltDP_3rd 엔지니어링 │ 워크스페이스 타겟 영역        │ 사용자 인터랙션 및 시각화 연동 방식                    │
├──────────────────────┼──────────────────────────────┼────────────────────────────────────────────────────────┤
│ **2D 평판/기초 FEM** │ Pane 3 (Graphic) &           │ • 메트기초, 지하외벽, 비정형슬래브 선택 시            │
│ (`src/engine/fem/`)  │ Pane 4 (Report)              │   Canvas에 DKMQ 메쉬 및 Von-Mises 응력 등고선 표출     │
│                      │                              │ • 계산서 영역에 비선형 지반 접촉압 분포표 자동 임베딩  │
├──────────────────────┼──────────────────────────────┼────────────────────────────────────────────────────────┤
│ **3D P-M 곡면 솔버** │ Pane 3 (Graphic)             │ • 기둥(RC/Steel) 선택 시 2D 단면 배근도 우측에         │
│ (`src/engine/solver`)│                              │   실시간 P-Mx-My 3D 인터랙티브 상관곡선 토글 뷰 제공   │
├──────────────────────┼──────────────────────────────┼────────────────────────────────────────────────────────┤
│ **2D CAD 배근상세도**│ Top Toolbar &                │ • 상단 [CAD 도면] 원클릭 버튼 및 Draw View 연계         │
│ (`src/engine/dxf/`)  │ Pane 4 (Export Action)       │ • ezdxf 기반 2D 철근 배근 상세도 .dxf 즉시 다운로드    │
├──────────────────────┼──────────────────────────────┼────────────────────────────────────────────────────────┤
│ **KDS 자동 물량산출**│ Top Toolbar &                │ • 상단 [물량 산출] 버튼 클릭 시 프로젝트 전 부재       │
│ (`quantity/`)        │ Pane 4 (Summary Modal)       │   콘크리트/거푸집/철근/강재 집계 및 다중시트 Excel 저장│
├──────────────────────┼──────────────────────────────┼────────────────────────────────────────────────────────┤
│ **MIDAS Gen 연동**   │ Left Sidebar (Project I/O)   │ • 좌측 사이드바 [📂 Gen 불러오기] 버튼 제공           │
│ (`interop/`)         │                              │ • .mgt 텍스트 임포트 시 최악하중 Governing LCB 자동  │
│                      │                              │   추출 후 부재 리스트(Pane 1)에 자동 일괄 바인딩       │
└──────────────────────┴──────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 19. 백엔드 동적 라우팅 및 단일 포트 고속 서빙

* **FastAPI 라우팅 구조**:
  - `GET /api/modules`: 54종 모듈 메타데이터 및 지오메트리 타입 반환
  - `GET /api/schema/{cat}/{grp}/{mod_id}`: Pydantic 기반 입력 스키마 및 단위/제약조건 반환
  - `POST /api/design/{cat}/{grp}/{mod_id}`: 단일화된 KDS 부재 검토/설계 엔드포인트
  - `GET /api/fem/...`, `POST /api/cad/...`, `POST /api/quantity/...`: 고유 확장 API 연계
* **Zero-Build 포터빌리티**:
  - 별도의 Node/npm 빌드 파이프라인 없이 순수 Vanilla JS + CSS로 구동
  - `run.ps1` 단일 실행으로 백엔드 API와 프론트엔드 정적 파일이 단일 포트(`8000`)에서 즉시 서빙
