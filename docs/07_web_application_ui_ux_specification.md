# Midas Design+ 원본 UI/UX 분석 및 웹 마이그레이션 종합 명세서 (07_web_application_ui_ux_specification.md)

본 문서는 Midas Design+ 원본 바이너리(`original_src/`, `decompiled_src/`)에서 추출된 UI/UX 프레임워크, 계층형 워크트리(WorkTree) 메뉴, 다이얼로그 모드, 2D/3D 드로잉 엔진, 그리드 컨트롤 및 계산서 출력 구조를 분석하고, 이를 **AltDP_3rd 모던 웹 애플리케이션**에 100% 무결하게 반영하기 위한 종합 명세서(SSOT)입니다.

---

## 1. Midas Design+ 원본 UI/UX 아키텍처 역공학 분석

### 1.1. 원본 계층형 워크트리(WorkTree) 메뉴 구조 분석 (`DPLUS_Main.dll`, `MIDAS_base.dll`)

원본 Midas Design+은 방대한 구조 부재 설계/해석 기능을 효율적으로 탐색하고 관리하기 위해 `CMainFrame::CreateWorkTree` 및 `ExpandWorksTree*` 기반의 **계층형 트리 메뉴 네비게이션 아키텍처**를 사용합니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Midas Design+ 원본 WorkTree 계층형 메뉴 분류 체계                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📂 RC (철근콘크리트 부재 - DPLUS_RCS.dll)                                    │
│   ├── 📄 보 (RC Beam) - 일반보, 캔틸레버보, 연속보, 변단면보 (CHK_BBBE)      │
│   ├── 📄 기둥 (RC Column) - 직사각형, 원형, 다각형, 단주/장주 (CHK_BCCO)     │
│   ├── 📄 전단벽 (Shear Wall) - 일반 전단벽, 특수경계요소 (CHK_BWUW)          │
│   ├── 📄 슬래브 (RC Slab) - 1방향, 2방향, 캔틸레버, 플랫 플레이트 (CHK_SLAB)│
│   ├── 📄 기초 (Footing) - 독립기초, 복합기초, 줄기초, 말뚝기초 (CHK_UFDN)   │
│   ├── 📄 옹벽/지하외벽 (Retaining Wall) - 캔틸레버 옹벽, 지하외벽 (CHK_URAB) │
│   └── 📄 지중보 / 전이보 (Ground / Transfer Beam) (CHK_URBE)                │
│                                                                             │
│ 📂 STEEL (강구조 부재 - DPLUS_STEEL.dll)                                    │
│   ├── 📄 철골보 (Steel Beam) - H형강, I형강, ㄷ형강, 횡비틀림좌굴 (CHK_SBM)  │
│   ├── 📄 철골기둥 (Steel Column) - H형강, 각형강관, 원형강관 (CHK_SCOL)      │
│   ├── 📄 가새 (Brace) - 인장/압축 가새, V/X/K형 가새 (CHK_SBRC)             │
│   ├── 📄 트러스 (Steel Truss) - 평면/입체 트러스 부재 검토                   │
│   ├── 📄 크레인 거더 (Crane Girder) - 주행하중, 피로 및 횡충격 하중 검토     │
│   ├── 📄 개구부보 (Web Opening Beam) - 원형/각형 웹 개구부 보강 검토        │
│   ├── 📄 볼트 접합부 (Bolt Connection) - 마찰/지압, 모멘트/전단 접합        │
│   ├── 📄 용접 접합부 (Welding Connection) - 모살/맞댐 용접, 브래킷 접합     │
│   └── 📄 베이스플레이트 (Base Plate) - 주각부 지압, 앵커볼트 인장/전단       │
│                                                                             │
│ 📂 SRC (철골철근콘크리트 부재 - DPLUS_SRC.dll)                              │
│   ├── 📄 매입형 SRC 기둥 (Encased Composite Column)                         │
│   ├── 📄 충전형 CFT 기둥 (Concrete Filled Tube Column: 각형/원형)            │
│   └── 📄 합성보 (Composite Beam) - 데크플레이트, 스터드 앵커 전단연결재     │
│                                                                             │
│ 📂 ALUMINUM (알루미늄 부재 - DPLUS_ALU.dll)                                 │
│   ├── 📄 알루미늄 보 / 기둥 / 커튼월 멀리온 (Curtain Wall Mullion)          │
│   └── 📄 알루미늄 루버 및 패널 프레임 (CALUCodeCheck)                        │
│                                                                             │
│ 📂 REINFORCEMENT (구조보강 부재 - DPLUS_RFM.dll)                            │
│   ├── 📄 탄소섬유판/시트(CFRP) 휨/전단 보강 (CUFBE, CUFCO)                  │
│   ├── 📄 강판 접착 보강 (Steel Plate Bonding)                               │
│   └── 📄 단면 증설 보강 (Section Enlargement)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2. 원본 4대 메인 폼뷰 전환 구조 (`CMainFormView*`)
원본 시스템은 선택된 부재에 대해 상단 탭 또는 뷰 모드를 통해 **4가지 전용 폼뷰**로 실시간 전환합니다.

1. **`CMainFormViewMemb` (단면 상세 설계/검토 뷰)**:
   - 선택된 단일 부재의 파라메트릭 입력, 2D 단면 배근도 렌더링, P-M 상관도 및 안전율(DCR) 검토
2. **`CMainFormViewList` (다중 부재 일괄 관리 뷰)**:
   - 층별/부재별 스프레드시트 테이블에서 프로젝트 내 모든 부재를 일괄 검토 및 정렬/필터링
3. **`CMainFormViewDraw` (도면 생성 및 CAD 뷰)**:
   - 완성된 부재의 2D 배근 상세도, 입면도, 배근 일람표 CAD 도면 렌더링
4. **`CMainFormViewQntt` (물량 산출 및 집계표 뷰)**:
   - 콘크리트 체적($\text{m}^3$), 거푸집 면적($\text{m}^2$), 철근/형강 중량(ton) 자동 집계

---

### 1.3. 원본 3대 사용자 인터랙션 모드 (Interaction Modes)

| 모드명 | 원본 C++ 클래스 접미사 | 주요 역할 및 동작 방식 | AltDP_3rd 웹 구현 대응 |
|---|---|---|---|
| **P-Mode** (Design Mode) | `*PModeDlg`<br>(예: `CURBBPModeDlg`, `CFootPModeDlg`) | • 파라메트릭 자동 설계 모드<br>• 단면 크기, 사용 재료, 설계 하중 입력 시 최적 철근/단면 자동 배근 산출 | **Auto-Design Mode**<br>단면/하중 입력 즉시 AI/알고리즘 기반 최적 단면/철근 자동 추천 |
| **S-Mode** (Check Mode) | `*SModeDlg`<br>(예: `CURBBSModeDlg`, `CSlabSModeDlg`) | • 단면 검토 모드<br>• 사용자가 직접 지정한 단면 제원 및 배근에 대해 KDS 안전율(DCR) 정밀 검토 | **Manual Check Mode**<br>2D 캔버스에서 직접 배근을 수정하며 실시간 DCR 게이지 업데이트 |
| **M-Mode** (List/Batch Mode) | `*MListDlg`<br>(예: `CURBBMListDlg`, `CSteelCraneGirderListDlg`) | • 다중 부재 일괄 관리 모드<br>• 층별/부재별 테이블 그리드에서 여러 단면을 일괄 검토 및 최악 DCR 부재 필터링 | **Batch Grid / Project Tree**<br>좌측 트리 메뉴 및 상단 테이블을 통한 다중 단면 일괄 관리 |

---

## 2. AltDP_3rd 트리 메뉴 및 모던 웹 UI/UX 설계 명세

### 2.1. 좌측 계층형 사이드바 트리 메뉴 (AltDP_2nd 계승 및 고도화)

* **트리 컴포넌트 UX 규칙**:
  1. **접이식 아코디언 (Collapsible Accordion)**: 부재 대분류(RC, Steel, SRC, Alu, RFM)별 원클릭 폴딩/익스팬드.
  2. **실시간 안전율 배지 (Status Badge)**: 각 부재 노드 우측에 DCR 상태 칩 표시
     - `DCR ≤ 0.9`: 🟢 `0.76 (OK)`
     - `0.9 < DCR ≤ 1.0`: 🟡 `0.95 (Warning)`
     - `DCR > 1.0`: 🔴 `1.18 (NG)`
  3. **초고속 부재 검색바 (0.01s Fuzzy Filter)**: 상단 검색창에 `보`, `기둥`, `H-400`, `기초` 등을 입력 시 해당 트리 노드만 즉시 필터링.
  4. **우클릭 컨텍스트 메뉴 (Context Menu)**:
     - `단면 복사 / 붙여넣기`, `이름 변경`, `A4 계산서 즉시 출력`, `삭제`

---

### 2.2. 화면 레이아웃 (4-Pane Responsive Workspace)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Top Navigation Bar: 프로젝트명 | [단면 상세 뷰 | 일괄 리스트 뷰 | 도면 뷰 | 물량 뷰] | 🖨️ A4 계산서 출력│
├───────────────────┬──────────────────────────────────────────┬──────────────────────────────┤
│ [Left Tree Menu]  │ [Main Dynamic Canvas]                    │ [Property & Design Panel]    │
│ 🔍 부재 검색...   │ ┌──────────────────────────────────────┐ │ 📐 단면 제원 (Section)       │
│ 📂 RC (5)         │ │   2D 인터랙티브 배근 단면도          │ │  • 폭(b): 400 mm, 춤(h): 600 │
│   ├── 🟢 1F-B1    │ │   • 마우스 휠: 줌 인/아웃            │ │  • 피복(dc): 40 mm           │
│   ├── 🟡 1F-C1    │ │   • 드래그: 캔버스 팬(Pan) 이동      │ 🧪 재료 강도 (Material)     │
│   └── 🔴 2F-B2    │ │   • 철근 호버: 직경/도심거리 툴팁   │ │  • fck: 27 MPa, fy: 400 MPa│
│ 📂 STEEL (3)      │ └──────────────────────────────────────┘ 🔩 배근 설정 (Reinforcement)   │
│   ├── 🟢 G1 (H형강)│ ┌──────────────────────────────────────┐ │  • 상부근: 4-D25 (2단)        │
│   └── 🟢 C1 (각파이프)│ │   P-M 상관도 차트 (Chart.js / WebGL) │ │  • 하부근: 4-D25           │
│ 📂 SRC (1)        │ │   • 공칭(Pn-Mn) & 설계(φPn-φMn) 곡선 │ │  • 늑근: HD10 @ 150 (2-Legs)│
│ 📂 CONNECTION (2) │ │   • 설계하중점(Mu, Pu) & DCR 여유도 │ ⚡ 설계 하중 (Load Force)    │
│   └── 🟢 B1-접합부│ └──────────────────────────────────────┘ │  • Mu: 245 kN·m, Vu: 120 kN  │
├───────────────────┴──────────────────────────────────────────┴──────────────────────────────┤
│ [Bottom Dock]: 📑 KDS 14 20 00 조항별 실시간 수식 계산 로그 (LaTeX MathJax/KaTeX 렌더링)     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.3. 2D 대화형 배근도 렌더러 (`renderer2d.js`) 역공학 세부 사양

`DPLUS_VDraw.dll`의 `CODABeamBase` 및 `CODABaseColumn`에서 추출된 드로잉 렌더링 파이프라인의 수치 규칙을 웹 캔버스에 100% 이식합니다.

1. **외곽 단면 프레임 (`DrawSect`, `DrawFrameBody`)**:
   - 콘크리트 외곽선(직사각형, T형, 원형) 렌더링 및 음영 채우기
2. **외곽 치수선 및 텍스트 (`DrawTxtInfo`, `DrawFrameHeadText`)**:
   - 부재 폭($b$), 높이($h$), 유효깊이($d$), 피복두께($d_c$) 치수선 및 화살표 자동 플로팅
3. **전단 철근 / 늑근 / 대근 (`DrawStirrup`)**:
   - 피복두께($d_c = 40\text{mm}$) 옵셋 적용 후 내부 사각형 패스 및 표준 135도 갈고리(Hook) 절곡 형상 렌더링
4. **주철근 (`DrawMainBar`)**:
   - 상부근/하부근 위치 계산 및 원형 심볼 채우기 (2단 배근 시 철근 중심간격 $s \ge 25\text{mm}$ 옵셋 적용)
5. **측면 스킨 철근 (`DrawSkinBar`)**:
   - 보 춤 $h \ge 900\text{mm}$ 초과 시 측면 수평 표피철근 자동 배치
6. **철근 정보 태그 (Rebar Callout)**:
   - 지시선 및 배근 텍스트 (예: `4-D25`, `HD10 @ 150 (2-Legs)`)

---

## 3. UI/UX 구현 우선순위 및 단계별 마일스톤

1. **Phase 1: AltDP Glassmorphism 디자인 시스템 & 좌측 계층형 트리 메뉴 구축**
   - 부재 대분류/소분류 아코디언 트리 UI 및 검색 필터링 완성
2. **Phase 2: 2D 인터랙티브 배근 렌더러 (`renderer2d.js`) 고도화**
   - RC 보, 기둥, 전단벽, 슬래브, 기초의 단면 및 철근 자동 렌더링
3. **Phase 3: P-M 상관도 및 실시간 DCR 게이지 연동 (`pm_chart.js`)**
   - P-M 계산 API 연동, 설계 하중점 플로팅 및 안전 여유도 시각화
4. **Phase 4: 4대 뷰 모드(단면/일괄/도면/물량) 및 A4 구조계산서 출력 시스템 완성**
   - 원클릭 브라우저 PDF 인쇄 및 프로젝트 데이터 JSON 저장/불러오기
