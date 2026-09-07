# Midas Design+ 원본 UI/UX 역공학 종합 분석 명세서 (13_midas_design_plus_original_ui_specification.md)

본 문서는 Midas Design+ 원본 바이너리(`original_src/`), 디컴파일 소스 및 심볼(`decompiled_src/`), 언어 및 다이얼로그 리소스(`Language/Korean/`, `DgnLanguage/Korean/`)에서 추출된 MFC/BCGControlBar 윈도우 프레임워크, 리본 메뉴 구성, 4대 메인 폼뷰, 3대 인터랙션 모드, 부재별 다이얼로그 폼, 2D/3D 드로잉 엔진 및 원본 계산서 출력 체계를 총체적으로 역공학 분석한 기술 명세서(Ground Truth SSOT)입니다.

---

## 1. Midas Design+ 원본 윈도우 프레임워크 구조

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

## 2. 원본 리본 메뉴 구성 체계 (`Menu.ini` 심층 분석)

`Language/Korean/Menu.ini`에서 추출된 리본 메뉴 탭, 패널 및 세부 명령 항목의 전체 인벤토리입니다.

### 2.1. 리본 탭 및 패널 상세 분류

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

## 3. 원본 4대 메인 폼뷰 (`CMainFormView*`) 구조

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

## 4. 원본 3대 사용자 인터랙션 모드 (Interaction Modes)

| 모드명 | 원본 C++ 클래스 접미사 | 주요 역할 및 동작 방식 |
|---|---|---|
| **P-Mode** (Design Mode) | `*PModeDlg`<br>(예: `CURBBPModeDlg`, `CFootPModeDlg`) | • 파라메트릭 자동 설계 모드<br>• 단면 크기, 사용 재료, 설계 하중 입력 시 최적 철근/단면 자동 배근 산출 |
| **S-Mode** (Check Mode) | `*SModeDlg`<br>(예: `CURBBSModeDlg`, `CSlabSModeDlg`) | • 단면 검토 모드<br>• 사용자가 직접 지정한 단면 제원 및 배근에 대해 KDS 안전율(DCR) 정밀 검토 |
| **M-Mode** (List/Batch Mode) | `*MListDlg`<br>(예: `CURBBMListDlg`, `CSteelCraneGirderListDlg`) | • 다중 부재 일괄 관리 모드<br>• 층별/부재별 테이블 그리드에서 여러 단면을 일괄 검토 및 최악 DCR 부재 필터링 |

---

## 5. 부재별 원본 다이얼로그 폼 구조 (`DLG_*.ini` 분석)

### 5.1. RC 부재 다이얼로그 (`DLG_DPLUS_RCS.ini`)
* `IDD_RCS_BEAM_PMODE_DLG`: RC 보 재료(fck, fy, fys, 경량콘크리트), 단면(b, h, 피복, T형 유효폭), 표피철근, 처짐/내진(SMF/IMF/OMF/필로티), 배근유형(전단면/양단부중앙부), 주철근 간격/이음, 균열조건.
* `IDD_RCS_COLUMN_PMODE_DLG`: RC 기둥 제원, 주철근 원형/사각 배열, 띠철근/나선철근, P-M 상호작용 검토.
* `IDD_RCS_WALL_PMODE_DLG`: 전단벽 두께, 길이, 층고, 특수경계요소, 수평/수직 철근비.
* `IDD_RCS_SLAB_PMODE_DLG`: 1방향/2방향 슬래브 경간, 지점 조건, 배근 유형 A/B/C, 장단기 처짐 조건.
* `IDD_RCS_FOOT_PMODE_DLG`: 독립/복합 기초 치수, 기둥 배치, 상재하중, 지반 지비력.
* `IDD_RCS_RETAINING_WALL_INPUT_DLG`: 옹벽 저판, 벽체 높이, 토압 조건, 활동/전도/지반지지력 안정성.

### 5.2. Steel 부재 및 접합부 다이얼로그 (`DLG_DPLUS_Steel.ini`)
* `IDD_STL_BEAMCOLUMN_INPUT_DLG`: H형강, 각형강관 단면, 비지지길이($L_b$), 모멘트구배계수($C_b$), 휨좌굴/비틀림좌굴.
* `IDD_STL_BOLTCONNECTION_INPUT_DLG`: 고력볼트(F10T/F8T/A325), 직경, 볼트 배열(게이지/피치/연단거리), 마찰/지압.
* `IDD_STL_WELDING_INPUT_DLG`: 모살/맞댐 용접, 용접 위치, 유효 용접 치수.
* `IDD_STL_USBP_PMODE_DLG`: 베이스플레이트 가로/세로/두께, 앵커볼트 인장/전단, 기초 콘크리트 지압.

---

## 6. 원본 2D/3D 드로잉 엔진 분석 (`DPLUS_VDraw.dll`)

* **핵심 드로잉 클래스**: `CODABeamBase`, `CODABaseColumn`, `CODABaseFooting`, `CODABaseWall`, `CODABaseSteel`
* **주요 렌더링 메소드 파이프라인**:
  - `DrawSect`, `DrawFrameBody`: 콘크리트 외곽선 및 음영 채우기
  - `DrawStirrup`: 피복두께 옵셋 및 135도 갈고리(Hook) 절곡 형상
  - `DrawMainBar`: 주철근 기하학적 중심 좌표 산출 및 솔리드 서클
  - `DrawTxtInfo`, `DrawFrameHeadText`: 치수선(b, h, d), 배근 텍스트 태그 지시선

---

## 7. 원본 계산서 생성 체계 (`DgnReportBase.ini`, `GENDgnReportKR.ini`)

* **출력 목차 구조**:
  1. 일반 사항 (General Info): 설계 기준, 단위계, 부재명
  2. 재질 및 단면 (Material & Section): $f_{ck}, f_y, E_c$, 단면 크기, 2D 단면도
  3. 설계 하중 (Design Loads): 계수 하중 조합
  4. 단면 검토 (Member Check):
     - 휨모멘트 및 전단 강도 검토 ($M_n, \phi M_n, V_c, V_s, \phi V_n$)
     - 처짐 검토 (단기/장기 처짐, 시간 의존 계수)
     - 균열 검토 (건조/기타 환경, 허용 균열폭)
  5. 종합 판정: `IDS_DGNREPORTBASE_ARROW_OK` ("  →  O.K"), `IDS_DGNREPORTBASE_ARROW_NG` ("  →  N.G")
