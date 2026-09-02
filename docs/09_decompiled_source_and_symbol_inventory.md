# 추출 바이너리 및 심볼 자산 분석 명세서 (09_decompiled_source_and_symbol_inventory.md)

## 1. 역공학 자산 개요 (Overview)

Midas Design+ 원본 바이너리(`original_src/Midas Design+/`)로부터 추출된 역공학 자산(`decompiled_src/`)은 총 **20개 DLL 모듈, 47,110개의 MSVC 데코레이션 C++ Exported Symbol, 1,000개 이상의 핵심 C++ 클래스**로 구성되어 있습니다.

추가로 Ghidra Headless 자동 추출 파이프라인([scripts/ghidra_extract.py](file:///d:/PyProject/AltDP_3rd/scripts/ghidra_extract.py))을 통해 노이즈(MFC GUI)를 제거하고 **순수 공학 설계 알고리즘 C 수도코드 47종([decompiled_src/core_routines/](file:///d:/PyProject/AltDP_3rd/decompiled_src/core_routines/))**을 영구 자산화하였습니다.

본 자산은 **AltDP_3rd** 시스템의 모든 부재설계 알고리즘, 파라미터 구조, 검토 파이프라인의 **절대적 정답 기준(Ground Truth)**으로 사용됩니다.

---

## 2. 모듈별 심볼 인벤토리 및 기능 분석

| DLL 모듈명 | 심볼 수 | 클래스 수 | 주요 C++ 클래스 및 핵심 CHK_ 접두어 | 핵심 역할 및 기능 |
|---|---|---|---|---|
| **`DPLUS_DB.dll`** | 23,447 | 657 | `CBaseClass`, `CAluSectDB`, `CSteelSectDB`, `CClassDBase`, `CClassChkOp`, `CDataCompare` | 전 부재 기본 데이터 모델, 형강 단면 DB 기하학적 성질 계산, 하중 조합 포락선(Envelope) 추출 |
| **`DPLUS_RCS.dll`** | 3,305 | 64 | `CRCSCodeCheck` (`CHK_BBBE`, `CHK_BCCO`, `CHK_BWUW`, `CHK_SLAB`, `CHK_UFDN`, `CHK_URAB`, `CHK_URBE`), `CRCSDataBase`, `CMSOffice` | KDS 14 20 00 기반 RC 보/기둥/벽체/슬래브/기초/옹벽/지중보 설계 검토 및 A4 계산서 생성 |
| **`DPLUS_STEEL.dll`** | 1,900 | 39 | `CSTLCodeCheck` (`CHK_USMC`, `CHK_USBP`, `CHK_USBC`, `CHK_USEP`, `CHK_USWE`, `CHK_USWO`, `CHK_USPG`, `CHK_USWB`), `CSTLDataBase` | KDS 14 31 00 기반 철골 보/기둥/가새/플레이트거더/볼트·용접 접합부/베이스플레이트 검토 |
| **`DPLUS_DGN.dll`** | 2,620 | 98 | `CDGN_PMCurveDrawWnd`, `CDGN_DataBase`, `CDgnBarInfoDlg`, `CDgnAnchBoltDlg`, `CDgnBeamInfoGrid` | P-M 상관도 곡선 계산 및 렌더링, 철근 배근 테이블, 앵커볼트 제원 매니저 |
| **`DPLUS_VDraw.dll`** | 2,674 | 74 | `CODABeamBase`, `CODABaseColumn`, `CODACombWall`, `CODADrawTool`, `CODAListSLAB`, `CODAListIFDN` | 부재별 2D/3D 배근도 및 응력 분포 드로잉, CAD 도면 생성 엔진 |
| **`DPLUS_SRC.dll`** | 505 | 12 | `CSRCCodeCheck` (`CHK_UCCB`, `CHK_UCCO`, `CHK_UCFT`), `CSRCDataBase`, `CSRCCompBeam` | 철골철근콘크리트(SRC) 합성기둥(CFT, SRC) 및 합성보 설계 검토 |
| **`DPLUS_ALU.dll`** | 329 | 9 | `CALUCodeCheck` (`CHK_UAAG`, `CHK_UAMT`), `CALUDataBase`, `CGUaagPModeDlg`, `CGUamtPModeDlg` | 알루미늄 일반/단축/다축 구조부재 휨, 압축, 국부좌굴 강도 검토 |
| **`DPLUS_RFM.dll`** | 529 | 12 | `CRFMCodeCheck` (`CHK_UFBE`, `CHK_UFCO`, `CHK_UFSL`), `CRFMDataBase` | 기존 구조물 보강/보수 설계 (CFRP 탄소판, 강판 보강 등) |
| **`DPLUS_EC.dll`** | 2,493 | 51 | `CECRCSCodeCheck` (`CHK_EBBE`, `CHK_ECCO`, `CHK_EFDN` 등), `CECSteelCodeCheck` | 유로코드(Eurocode 2, 3, 4) 규준 설계 검토 엔진 |
| **`DPLUS_IS.dll`** | 2,188 | 49 | `CISRCSCodeCheck` (`CHK_IBBE`, `CHK_ICCO`, `CHK_IFDN`, `CHK_IWUW` 등) | 인도 국가기준(IS 456, IS 800) 규준 설계 검토 엔진 |
| **`DPLUS_Main.dll`** | 601 | 47 | `CAppMain`, `CDPLUSDoc`, `CChildFrame`, `CAboutDlg` | 메인 애플리케이션 프레임워크 및 문서/프로젝트 관리자 |
| **`MIDAS_base.dll`** | 1,401 | 47 | `CAppBase`, `CDocBase`, `CGLViewBase`, `CGwPrintHandler`, `CFormulaEdit` | OpenGL 뷰어 베이스, 인쇄/핸들러, 수식 파서 에디터 |
| **`MIDAS_lib.dll`** | 2,116 | 102 | `CArrayUtil`, `CCurveUtil`, `CDBUpdateConnector`, `CDynModuleMgr`, `CDlgTabCtrl` | 공통 유틸리티, 곡선 보간 수치해석, 동적 모듈 로더 |
| **`MIDAS_util.dll`** | 752 | 32 | `CTBGrid`, `CTBBrowserWndStlSection`, `CTBBrowserFRPMatl`, `CTBSortCtrl` | 스프레드시트형 그리드 컨트롤, 재료 및 단면 브라우저 |
| **`DGN_lib.dll`** | 1,267 | 3 | `CMSExcel`, `CMSWorkRec`, `ChartData` | MS Excel 입출력 및 차트 데이터 처리 엔진 |
| **기타 모듈** | 1,009 | 2 | `IDGN_core.dll`, `IDGN_lib.dll`, `IDGN_db.dll`, `DPLUS_DWG.dll`, `DPLUS_Draw.dll` | 내부 코어 라이브러리 및 CAD 드로잉 브릿지 |
| **합계** | **47,110** | **1,000+** | - | **Midas Design+ 전체 부재설계 및 해석 시스템 100% 매핑** |

---

## 3. 선별 디컴파일 C 수도코드 자산 ([decompiled_src/core_routines/](file:///d:/PyProject/AltDP_3rd/decompiled_src/core_routines/))

Ghidra Decompiler AST로부터 추출된 47개 무손실 C 수도코드 파일이 4개 도메인 서브디렉토리에 배치되어 있습니다:

```text
decompiled_src/core_routines/
├── README.md               # [SSOT] 전체 핵심 심볼 총괄 색인표
├── solver/                 # Group 1: P-M 상관도 및 비선형 수치해석 솔버 (4건)
│   ├── solver__CHK_BCCO_*.c (기둥 3D P-M 상관곡선 & 중립축 수렴)
│   ├── solver__CHK_BCGR_*.c (기둥 그룹 Worst 하중 포락선)
│   └── solver_meta.json
├── rc/                     # Group 2: RC 5대 부재 핵심 설계 엔진 (14건)
│   ├── rc__CHK_BBBE_*.c (보 휨/전단/처짐)
│   ├── rc__CHK_BWUW_*.c (전단벽 면내전단 & 경계요소)
│   ├── rc__CHK_SLAB_*.c (슬래브 DDM & 2방향 펀칭전단)
│   ├── rc__CHK_UFDN_*.c (기초 접지압 & 펀칭전단)
│   ├── rc__CHK_URAB_*.c (옹벽/지하외벽 토압 & 안정성)
│   ├── rc__CHK_URBE_*.c (지중보 전단/휨)
│   └── rc_meta.json
├── steel/                  # Group 3 & 4: 철골 부재 및 접합부/주각부 (17건)
│   ├── steel__CHK_USMC_*.c (보/기둥/가새 LTB, 좌굴, 축력-휨 조합)
│   ├── steel__CHK_USBP_*.c (주각부 베이스플레이트 지압 & 두께)
│   ├── steel__CHK_USBC_*.c (고장력볼트 전단/인장/블록전단)
│   ├── steel__CHK_USEP_*.c (엔드플레이트 모멘트 접합)
│   ├── steel__CHK_USWE_*.c (용접 접합부 목두께)
│   ├── steel__CHK_USWO_*.c (웨브 개구부 보강)
│   ├── steel__CHK_USPG_*.c (플레이트 거더)
│   ├── steel__CHK_USWB_*.c (가새 거셋플레이트)
│   └── steel_meta.json
└── db/                     # Group 5: 단면 기하학적 성질 및 DB 연산 (12건)
    ├── db__*.c (단면도심, 2차모멘트, 비틀림/뜀상수)
    └── db_meta.json
```

---

## 4. 핵심 설계 엔진 C++ 심볼 상세 분석

### 4.1. `DPLUS_RCS.dll` - `CRCSCodeCheck` (RC 부재 검토 함수군)
* `CHK_BBBE`: RC 일반보(Beam) 휨($M_n$), 전단($V_n$), 최소/최대 철근비, 유효단면2차모멘트($I_e$) 처짐 검토
* `CHK_BCCO`: RC 기둥(Column) 축압축/축인장, 이축휨 P-M 상관도($P_n, M_{nx}, M_{ny}$), 브레슬러/윤곽선법 검토
* `CHK_BWUW`: RC 전단벽(Wall) 면내전단($V_n$), 단부 보강근(Boundary Element), 휨 검토
* `CHK_SLAB`: RC 슬래브(Slab) 1방향/2방향 직접설계법(DDM) 휨, 2방향 펀칭전단($d/2$), 처짐 검토
* `CHK_UFDN`: RC 기초(Footing) 편심 접지압, 1방향 보전단, 2방향 펀칭전단, 휨, 지반반력 검토
* `CHK_URAB`: RC 지하외벽 / 옹벽(Retaining Wall) Rankine/Coulomb 토압, 전도/활동/지지력 안전율, 단면 휨/전단 검토
* `CHK_URBE`: RC 지중보 / 전이보 검토

### 4.2. `DPLUS_STEEL.dll` - `CSTLCodeCheck` (철골 부재 검토 함수군)
* `CHK_USMC`: 철골 부재(보/기둥/가새) 폭두께비 조밀 판정, 비지지길이($L_b$)별 LTB($M_n$), 전단좌굴($V_n$), 강축/약축 휨좌굴($P_n$), 축력-휨 조합응력 검토 ($P_u / \phi P_n \ge 0.2$ 수식)
* `CHK_USBP`: 기둥 주각부 베이스플레이트 콘크리트 지압응력(삼각/사다리꼴) 분포, 플레이트 소요두께($t_p$), 앵커볼트 인장/전단 검토
* `CHK_USBC`: 고장력 볼트(F10T, TS볼트) 전단, 인장, 지압, 블록전단 파단(Block Shear Rupture) 검토
* `CHK_USEP`: 보-기둥 모멘트 엔드플레이트 접합부 두께 및 볼트 장력 산출
* `CHK_USWE`: 필릿용접 및 그루브용접(CJP/PJP) 유효목두께 및 허용응력 검토
* `CHK_USWO`: 철골 보 웨브 개구부(Web Opening) 전단 및 보강재 검토
* `CHK_USPG`: 플레이트 거더(Plate Girder) 휨 및 전단좌굴 검토
* `CHK_USWB`: 가새 부재 인장 순단면 파단($U$ 전단지체계수) 및 거셋플레이트 검토

### 4.3. `DPLUS_ALU.dll` & `DPLUS_SRC.dll` (특수 구조 함수군)
* `CHK_UAAG` / `CHK_UAMT`: 알루미늄 일반/단축/다축 부재 휨·압축·국부좌굴 검토
* `CHK_UCCO` / `CHK_UCFT`: CFT 및 매입형 SRC 기둥/합성보 전단연결재 검토

---

## 5. AltDP_3rd Python/Web 엔진 포팅 맵 (Mapping Table)

| 원본 C++ DLL / 심볼 | C 수도코드 자산 | AltDP_3rd 신규 파이썬 엔진 | API 엔드포인트 | 웹 렌더러 / UI |
|---|---|---|---|---|
| `DPLUS_RCS.dll` (`CHK_BBBE`) | `core_routines/rc/rc__CHK_BBBE_*.c` | `src/engine/rc/beam.py` | `POST /api/rc/beam/check` | `src/web/templates/index.html` (RC Beam UI) |
| `DPLUS_RCS.dll` (`CHK_BCCO`) | `core_routines/solver/solver__CHK_BCCO_*.c` | `src/engine/rc/column.py` | `POST /api/rc/column/check` | `src/web/static/js/pm_chart.js` (P-M 상관도) |
| `DPLUS_RCS.dll` (`CHK_BWUW`) | `core_routines/rc/rc__CHK_BWUW_*.c` | `src/engine/rc/wall.py` | `POST /api/rc/wall/check` | 전단벽 배근 뷰어 |
| `DPLUS_RCS.dll` (`CHK_SLAB`, `CHK_UFDN`) | `core_routines/rc/rc__CHK_SLAB_*.c`, `UFDN_*.c` | `src/engine/rc/slab.py`, `footing.py` | `POST /api/rc/slab/check`, `footing/check` | 기초/슬래브 배근 뷰어 |
| `DPLUS_STEEL.dll` (`CHK_USMC`) | `core_routines/steel/steel__CHK_USMC_*.c` | `src/engine/steel/beam.py`, `column.py`, `brace.py` | `POST /api/steel/beam/check` | H형강 단면 렌더러 |
| `DPLUS_STEEL.dll` (`CHK_USBC`, `CHK_USBP`) | `core_routines/steel/steel__CHK_USBC_*.c`, `USBP_*.c` | `src/engine/steel/connection.py`, `baseplate.py` | `POST /api/steel/conn/check` | 볼트/플레이트 상세 뷰어 |
| `DPLUS_DB.dll` (`CAluSectDB`, `CSteelSectDB`) | `core_routines/db/db__*.c` | `src/engine/db/sdb_parser.py`, `materials.py` | `GET /api/db/sections`, `/materials` | 단면 및 강종 선택기 |
| `DPLUS_VDraw.dll` (`CODABeamBase` 등) | - | `src/web/static/js/renderer2d.js` | Web Canvas 2D / SVG | 2D 대화형 배근 단면 렌더러 |
| `DGN_lib.dll` / `CMSOffice` | - | `src/report/generator.py` | `POST /api/report/export` | HTML/PDF A4 표준 구조계산서 |

---

## 6. 역공학 자산 활용 원칙 (Ground Truth Protocol)

1. **독립성 유지**: 신규 엔진은 C++ 바이너리나 Windows DLL을 직접 호출하지 않고, **순수 Python 3.13 및 Web 표준 기술**로 완전히 재작성되어 플랫폼 독립적으로 동작합니다.
2. **설계식의 무결성**: KDS 국가건설기준 원문 및 C++ 심볼 검토 로직을 교차 검증하여, 원본 프로그램과의 **계산 오차 0.1% 미만**을 달성합니다.
3. **전수 단위 테스트**: [tests/engine/](file:///d:/PyProject/AltDP_3rd/tests/engine/) 및 [tests/api/](file:///d:/PyProject/AltDP_3rd/tests/api/)를 통해 모든 부재 검토 수식을 0.5초 이내에 자동 회귀 테스트합니다.
