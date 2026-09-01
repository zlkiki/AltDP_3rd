# Midas Design+ 원본 UI/UX 분석 및 웹 마이그레이션 종합 명세서 (07_web_application_ui_ux_specification.md)

본 문서는 Midas Design+ 원본 바이너리(`original_src/`, `decompiled_src/`)에서 추출된 UI/UX 프레임워크, 다이얼로그 모드, 2D/3D 드로잉 엔진, 그리드 컨트롤 및 계산서 출력 구조를 분석하고, 이를 **AltDP_3rd 모던 웹 애플리케이션**에 100% 무결하게 반영하기 위한 종합 명세서(SSOT)입니다.

---

## 1. Midas Design+ 원본 UI/UX 아키텍처 역공학 분석

### 1.1. 원본 3대 사용자 인터랙션 모드 (Interaction Modes)
원본 Midas Design+은 각 부재별로 **3단계 작업 모드 다이얼로그 패턴**을 채택하고 있습니다.

| 모드명 | 원본 C++ 클래스 접미사 | 주요 역할 및 동작 방식 | AltDP_3rd 웹 구현 대응 |
|---|---|---|---|
| **P-Mode** (Design Mode) | `*PModeDlg`<br>(예: `CURBBPModeDlg`, `CFootPModeDlg`) | • 파라메트릭 자동 설계 모드<br>• 단면 크기, 사용 재료, 설계 하중 입력 시 최적 철근/단면 자동 배근 산출 | **Auto-Design Mode**<br>단면/하중 입력 즉시 AI/알고리즘 기반 최적 단면/철근 자동 추천 |
| **S-Mode** (Check Mode) | `*SModeDlg`<br>(예: `CURBBSModeDlg`, `CSlabSModeDlg`) | • 단면 검토 모드<br>• 사용자가 직접 지정한 단면 제원 및 배근에 대해 KDS 안전율(DCR) 정밀 검토 | **Manual Check Mode**<br>2D 캔버스에서 직접 배근을 수정하며 실시간 DCR 게이지 업데이트 |
| **M-Mode** (List/Batch Mode) | `*MListDlg`<br>(예: `CURBBMListDlg`, `CSteelCraneGirderListDlg`) | • 다중 부재 일괄 관리 모드<br>• 층별/부재별 테이블 그리드에서 여러 단면을 일괄 검토 및 최악 DCR 부재 필터링 | **Batch Grid / Project Tree**<br>좌측 프로젝트 트리 및 상단 부재 테이블을 통한 다중 단면 일괄 관리 |

---

### 1.2. 원본 UI 모듈별 핵심 C++ 컴포넌트

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Midas Design+ 원본 UI/UX 5대 컴포넌트 맵                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. 윈도우/도킹 프레임워크 (MIDAS_base.dll, DPLUS_Main.dll)                  │
│    • CAppMain / CDocBase / CDockingDlgBarBase / CBCGPMiniFrameWnd           │
│    -> 좌우측 도킹 사이드바, 접이식 속성창, 플로팅 툴바                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. 수치 입력 그리드 & 재료 선택기 (MIDAS_util.dll, MIDAS_lib.dll)             │
│    • CTBGrid / CEditGrid / CTBBrowserWndStlSection / CCheckListBoxEx         │
│    -> 키보드 네비게이션 지원 스프레드시트 그리드, 형강 DB 콤보 브라우저     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. 2D/3D 배근도 및 CAD 드로잉 엔진 (DPLUS_VDraw.dll)                        │
│    • CODABeamBase / CODABaseColumn / CODACombWall / CODADrawTool            │
│    -> DrawMainBar, DrawStirrup, DrawSkinBar, DrawTxtInfo, DrawFrameHead    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. P-M 상관도 및 해석 다이어그램 (DPLUS_DGN.dll)                             │
│    • CDGN_PMCurveDrawWnd / CDgnPMCurveZoomDlg / CDgnBarTableDlg              │
│    -> 공칭/설계 강도 2중 곡선, 3D 상관곡면, 하중점 확대 및 DCR 하이라이트    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. A4 표준 구조계산서 출력 (DPLUS_RCS.dll, DGN_lib.dll)                      │
│    • CMSOffice / CMSExcel / ChartData                                       │
│    -> KDS 수식 전개식, 단면도/상관도 차트 이미지, 원클릭 인쇄/PDF           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 원본 2D 배근도 렌더러 (`CODABeamBase`, `CODABaseColumn`) 역공학 세부 사양

`DPLUS_VDraw.dll`의 `CODABeamBase` 및 `CODABaseColumn`에서 추출된 드로잉 렌더링 파이프라인의 수치 규칙을 웹 캔버스에 100% 이식합니다.

### 2.1. 도면 구성 요소 및 렌더링 순서 (Drawing Order)
1. **외곽 단면 프레임 (`DrawSect`, `DrawFrameBody`)**:
   - 콘크리트 외곽선(직사각형, T형, 원형) 렌더링
   - 콘크리트 해치/배경색상 채우기
2. **외곽 치수선 및 텍스트 (`DrawTxtInfo`, `DrawFrameHeadText`)**:
   - 부재 폭($b$), 높이($h$), 유효깊이($d$), 피복두께($d_c$) 치수선 및 화살표
   - 부재 기호 및 위치 태그 (단부 End-i, 중앙 Center, 단부 End-j)
3. **전단 철근 / 늑근 / 대근 (`DrawStirrup`)**:
   - 피복두께($d_c = 40\text{mm}$) 옵셋 적용 후 내부 사각형 패스
   - 표준 135도 갈고리(Hook) 절곡 형상 렌더링
4. **주철근 (`DrawMainBar`)**:
   - 상부근/하부근 위치 계산 및 원형 심볼 채우기
   - 2단 배근(Layer 2) 시 철근 중심간격($s \ge 25\text{mm}$) 옵셋 배치
5. **측면 스킨 철근 (`DrawSkinBar`)**:
   - 보 춤 $h \ge 900\text{mm}$ 초과 시 측면 수평 표피철근 자동 배치
6. **철근 정보 태그 (Rebar Callout)**:
   - 지시선 및 배근 텍스트 (예: `4-D25`, `2-D19`, `HD10 @ 150 (2-Legs)`)

---

## 3. AltDP_3rd 모던 웹 UI/UX 설계 명세

### 3.1. 테마 및 디자인 시스템 (AltDP Glassmorphism)

* **컬러 팔레트 (CSS Design Tokens)**:
  * `Background Base`: `#090d16` (Deep Dark Slate)
  * `Panel Surface`: `rgba(15, 23, 42, 0.75)` (Frosted Glassmorphic Surface)
  * `Border & Divider`: `rgba(255, 255, 255, 0.08)`
  * `Brand Accent (Primary)`: `#38bdf8` (Electric Sky Blue)
  * `Success (DCR ≤ 1.0)`: `#22c55e` (Emerald Green)
  * `Warning (0.9 < DCR ≤ 1.0)`: `#f59e0b` (Amber Yellow)
  * `Danger / NG (DCR > 1.0)`: `#ef4444` (Crimson Red)
* **타이포그래피**:
  * 본문 및 UI 레이블: `Pretendard`, `Inter`, sans-serif
  * 수치, 좌표, 설계식: `JetBrains Mono`, monospace

---

### 3.2. 화면 레이아웃 (4-Pane Responsive Workspace)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Top Navigation Bar: 프로젝트명 | 부재 카테고리 탭 (RC / Steel / SRC) | 계산서 출력 버튼 │
├──────────────┬──────────────────────────────────┬───────────────────────────┤
│ [Sidebar]    │ [Main Dynamic Canvas]            │ [Property & Design Panel] │
│ • 부재 트리  │ ┌──────────────────────────────┐ │ • 단면 치수 (b, h, L)     │
│   - RC 보    │ │   2D 배근 단면도 (대화형)    │ │ • 재료 강도 (fck, fy, fyt)│
│   - RC 기둥  │ │   - 마우스 휠: 줌 인/아웃    │ │ • 주근 / 전단근 배근 설정 │
│   - RC 벽체  │ │   - 드래그: 팬(Pan) 이동     │ │ • 설계 하중 (Mu, Vu, Pu)  │
│   - Steel 보 │ │   - 실시간 치수/철근 표시    │ ├───────────────────────────┤
│ • 하중 케이스│ └──────────────────────────────┘ │ [Safety Check Summary]    │
│ • 일괄 검토  │ ┌──────────────────────────────┐ │ • 휨 DCR: [0.76] (OK)     │
│              │ │   P-M 상관도 / 전단 포락선   │ │ • 전단 DCR: [0.82] (OK)   │
│              │ └──────────────────────────────┘ │ • 처짐 DCR: [0.45] (OK)   │
├──────────────┴──────────────────────────────────┴───────────────────────────┤
│ [Bottom Dock]: KDS 14 20 00 조항별 수식 계산 과정 상세 로그 (LaTeX 렌더링)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.3. 핵심 대화형 컴포넌트 사양

#### 1) 2D 인터랙티브 캔버스 렌더러 (`renderer2d.js`)
* **기능**:
  * HTML5 Canvas / SVG 듀얼 렌더링 지원
  * 단면 치수($b, h$) 변경 시 부드러운 트랜지션 애니메이션
  * 주근 호버 시 철근 직경, 순간격, 도심거리 툴팁 노출
  * 마우스 휠 줌(Zoom) 및 드래그 팬(Pan), 원클릭 뷰 초기화(Fit to Screen) 버튼 제공

#### 2) 대화형 P-M 상관도 차트 (`pm_chart.js`)
* **기능**:
  * 공칭강도 곡선($P_n-M_n$) 및 KDS 강도감소계수 반영 설계강도 곡선($\phi P_n-\phi M_n$) 동시 플로팅
  * 설계 하중점($(M_u, P_u)$) 플로팅 및 안전 여유도(DCR) 하이라이트
  * 주축($M_x$) / 약축($M_y$) 탭 전환 및 3D 상관곡면 뷰어(Three.js/WebGL 연동 지원)

#### 3) 스프레드시트 하중/배근 입력 그리드
* **기능**:
  * 엑셀 복사/붙여넣기(Ctrl+C / Ctrl+V) 100% 호환
  * 키보드 방향키 및 Enter/Tab 네비게이션 완벽 지원

#### 4) A4 원클릭 구조계산서 출력 시스템
* **기능**:
  * `@media print` CSS를 통한 브라우저 기본 PDF 저장 지원
  * KDS 설계 수식(MathJax/KaTeX), 단면 배근도 캔버스 이미지, P-M 차트 고해상도 벡터 자동 결합

---

## 4. UI/UX 구현 우선순위 및 단계별 마일스톤

1. **Phase 1: 디자인 시스템 및 기본 레이아웃 구축**
   - Frosted Glassmorphic 스타일시트([src/web/static/css/style.css](file:///f:/PyProject/AltDP_3rd/src/web/static/css/style.css)) 토큰 완성
   - 4-Pane 반응형 대시보드 템플릿([src/web/templates/index.html](file:///f:/PyProject/AltDP_3rd/src/web/templates/index.html)) 구성
2. **Phase 2: 2D 배근도 렌더러 (`renderer2d.js`) 고도화**
   - RC 보, 기둥, 전단벽, 슬래브, 기초의 단면 및 철근 자동 렌더링 로직 탑재
3. **Phase 3: P-M 상관도 및 실시간 DCR 게이지 연동 (`pm_chart.js`)**
   - 백엔드 P-M 계산 API 연동 및 실시간 인터랙션 구축
4. **Phase 4: 계산서 생성기 및 다중 부재 일괄 관리 그리드 완성**
   - A4 인쇄 템플릿 및 프로젝트 저장/불러오기(JSON) 연동
