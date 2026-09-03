# AltDP_3rd Web Application UI/UX 종합 명세서 (07_web_application_ui_ux_specification.md)

본 문서는 **AltDP_3rd 모던 웹 부재설계 플랫폼**의 프론트엔드 아키텍처, 4-Pane 반응형 레이아웃, 독립 드래그 리사이저 엔진, 중앙 데이터 스토어(SSOT), 다중 단위계 관리, 파라메트릭 인풋 폼, 2D/3D 벡터 그래픽 엔진, 실시간 KDS 구조계산서 렌더러 및 **AltDP_2nd의 정식 `UI_UX_디자인_표준명세서.md`의 디자인 토큰과 상호작용 체계**를 총체적으로 융합한 단일 진실 공급원(SSOT) 종합 명세서입니다.

*(※ Midas Design+ 원본 데스크톱 앱의 C++/MFC 역공학 분석 내용은 [`docs/13_midas_design_plus_original_ui_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md)를 참조하십시오.)*

---

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
│  • 실시간 DCR 배지     │ │  • 파라메트릭 입력 그리드 │ │ │  • 실시간 치수선/콜아웃   │ │ │  • A4 인쇄 / PDF / Excel │ │
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
* 각 부재 항목별 DCR 상태 점(녹색/노란색/적색) 및 DCR 수치 뱃지 실시간 동기화:
  - 🟢 **OK (`DCR ≤ 0.900`)**: 안전 여유 충분 (초록색 칩).
  - 🟡 **WARN (`0.901 < DCR ≤ 1.000`)**: 허용 내력 근접 (노란색 칩).
  - 🔴 **NG (`DCR > 1.000`)**: 내력 초과 (빨간색 칩 및 초과 항목 툴팁).

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
  │                                           │   • $a, c, \epsilon_t, \phi M_n, V_c, V_s$ │
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

## 9. Midas Design+ 역공학 기반 4대 메인 폼뷰 & 3대 인터랙션 모드 융합 명세

### 9.1. 4대 메인 폼뷰 (4 Main Form Views Architecture)
1. **Memb View (`CMainFormViewMemb`)**:
   - 단일 부재 정밀 4분할 워크스페이스 (속성 그리드 ↔ 2D 단면 배근도 ↔ P-M 상관곡선/DCR ↔ KDS 실시간 요약서).
2. **List View (`CMainFormViewList`)**:
   - 다중 부재 일괄 스프레드시트 검토 뷰 (층별/부재별 트리 네비게이터, Excel형 그리드, 원클릭 일괄 DCR 히트맵).
3. **Draw View (`CMainFormViewDraw`)**:
   - 2D 배근 상세도 및 일람표 CAD 뷰어 (보/기둥 단면/입면 벡터 드로잉, 스케줄 테이블, DXF/SVG 내보내기).
4. **Qntt View (`CMainFormViewQntt`)**:
   - 콘크리트/거푸집/철근/강재 자동 물량 산출 대시보드 (D10~D32 직경별 물량, 형강 중량, 도넛 차트 및 Excel 내보내기).

### 9.2. 3대 인터랙션 모드 (3 Interactive Operational Modes)
1. **P-Mode (Parametric Auto-Design Mode)**:
   - 설계 단면 가정 및 KDS 강도설계법/허용응력설계법에 따른 최적 철근 배근 및 형강 규격 자동 제안.
2. **S-Mode (Section Check Mode)**:
   - 기 배근된 단면 및 단면 제원에 대해 모멘트/전단/축력/비틀림 DCR을 즉각 해석/검토하는 엔지니어링 검토 모드.
3. **M-Mode (Member Management Mode)**:
   - 부재 태그, 그룹핑, 층(Story) 배치, 하중 케이스 연계 등 구조 모델 메타데이터를 통합 관리하는 모드.

