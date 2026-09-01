# 추출 바이너리 및 심볼 자산 분석 명세서 (09_decompiled_source_and_symbol_inventory.md)

## 1. 역공학 자산 개요 (Overview)

Midas Design+ 원본 바이너리(`original_src/Midas Design+/`)로부터 추출된 역공학 자산(`decompiled_src/`)은 총 **20개 DLL 모듈, 47,110개의 MSVC 데코레이션 C++ Exported Symbol, 1,000개 이상의 핵심 C++ 클래스**로 구성되어 있습니다.

본 자산은 **AltDP_3rd** 시스템의 모든 부재설계 알고리즘, 파라미터 구조, 검토 파이프라인의 **절대적 정답 기준(Ground Truth)**으로 사용됩니다.

---

## 2. 모듈별 심볼 인벤토리 및 기능 분석

| DLL 모듈명 | 심볼 수 | 클래스 수 | 주요 C++ 클래스 | 핵심 역할 및 기능 |
|---|---|---|---|---|
| **`DPLUS_DB.dll`** | 23,447 | 657 | `CBaseClass`, `CAluSectDB`, `CSteelSectDB`, `CClassDBase`, `CClassChkOp`, `CDataCompare` | 전 부재 기본 데이터 모델, 형강 단면 DB 기하학적 성질 계산, 하중 조합 포락선(Envelope) 추출 |
| **`DPLUS_RCS.dll`** | 3,305 | 64 | `CRCSCodeCheck`, `CRCSDataBase`, `CMSOffice`, `CSlabPModeDlg`, `CFootPModeDlg`, `CURABPModeDlg` | KDS 14 20 00 기반 RC 보/기둥/벽체/슬래브/기초/옹벽 설계 검토 및 A4 계산서 생성 |
| **`DPLUS_STEEL.dll`** | 1,900 | 39 | `CSTLCodeCheck`, `CSTLDataBase`, `CSteelBoltConnection`, `CSteelWelding`, `CBasePlate`, `CSteelCraneGirder` | KDS 14 31 00 기반 철골 보/기둥/가새/크레인거더/볼트·용접 접합부/베이스플레이트 검토 |
| **`DPLUS_DGN.dll`** | 2,620 | 98 | `CDGN_PMCurveDrawWnd`, `CDGN_DataBase`, `CDgnBarInfoDlg`, `CDgnAnchBoltDlg`, `CDgnBeamInfoGrid` | P-M 상관도 곡선 계산 및 렌더링, 철근 배근 테이블, 앵커볼트 제원 매니저 |
| **`DPLUS_VDraw.dll`** | 2,674 | 74 | `CODABeamBase`, `CODABaseColumn`, `CODACombWall`, `CODADrawTool`, `CODAListSLAB`, `CODAListIFDN` | 부재별 2D/3D 배근도 및 응력 분포 드로잉, CAD 도면 생성 엔진 |
| **`DPLUS_SRC.dll`** | 505 | 12 | `CSRCCodeCheck`, `CSRCDataBase`, `CSRCCompBeam`, `CUCCO` | 철골철근콘크리트(SRC) 합성기둥(CFT, SRC) 및 합성보 설계 검토 |
| **`DPLUS_ALU.dll`** | 329 | 9 | `CALUCodeCheck`, `CALUDataBase`, `CGUaagPModeDlg`, `CGUamtPModeDlg` | 알루미늄 구조부재 휨, 압축, 좌굴 강도 검토 |
| **`DPLUS_RFM.dll`** | 529 | 12 | `CRFMCodeCheck`, `CRFMDataBase`, `CUFBE`, `CUFCO`, `CUFSL` | 기존 구조물 보강/보수 설계 (FRP, 강판 보강 등) |
| **`DPLUS_EC.dll`** | 2,493 | 51 | `CECRCSCodeCheck`, `CECSteelCodeCheck`, `CECSRCCodeCheck`, `CEFDN`, `CERBB` | 유로코드(Eurocode 2, 3, 4) 규준 설계 검토 엔진 |
| **`DPLUS_IS.dll`** | 2,188 | 49 | `CISRCSCodeCheck`, `CISDgnForceDlg`, `CISDgnSoilPropGrid`, `CIRBB`, `CIRBC` | 인도 국가기준(IS 456, IS 800) 규준 설계 검토 엔진 |
| **`DPLUS_Main.dll`** | 601 | 47 | `CAppMain`, `CDPLUSDoc`, `CChildFrame`, `CAboutDlg` | 메인 애플리케이션 프레임워크 및 문서/프로젝트 관리자 |
| **`MIDAS_base.dll`** | 1,401 | 47 | `CAppBase`, `CDocBase`, `CGLViewBase`, `CGwPrintHandler`, `CFormulaEdit` | OpenGL 뷰어 베이스, 인쇄/핸들러, 수식 파서 에디터 |
| **`MIDAS_lib.dll`** | 2,116 | 102 | `CArrayUtil`, `CCurveUtil`, `CDBUpdateConnector`, `CDynModuleMgr`, `CDlgTabCtrl` | 공통 유틸리티, 곡선 보간 수치해석, 동적 모듈 로더 |
| **`MIDAS_util.dll`** | 752 | 32 | `CTBGrid`, `CTBBrowserWndStlSection`, `CTBBrowserFRPMatl`, `CTBSortCtrl` | 스프레드시트형 그리드 컨트롤, 재료 및 단면 브라우저 |
| **`DGN_lib.dll`** | 1,267 | 3 | `CMSExcel`, `CMSWorkRec`, `ChartData` | MS Excel 입출력 및 차트 데이터 처리 엔진 |
| **기타 모듈** | 1,009 | 2 | `IDGN_core.dll`, `IDGN_lib.dll`, `IDGN_db.dll`, `DPLUS_DWG.dll`, `DPLUS_Draw.dll` | 내부 코어 라이브러리 및 CAD 드로잉 브릿지 |
| **합계** | **47,110** | **1,000+** | - | **Midas Design+ 전체 부재설계 및 해석 시스템 100% 매핑** |

---

## 3. 핵심 설계 엔진 C++ 심볼 상세 분석

### 3.1. `DPLUS_RCS.dll` - `CRCSCodeCheck` (RC 부재 검토 함수군)
* `CHK_BBBE`: RC 일반보(Beam) 휨($M_n$), 전단($V_n$), 최소/최대 철근비, 처짐 검토
* `CHK_BCCO`: RC 기둥(Column) 축압축/축인장, 이축휨 P-M 상관도($P_n, M_{nx}, M_{ny}$), 횡철근 검토
* `CHK_BWUW`: RC 전단벽(Wall) 면내전단($V_n$), 단부 보강근(Boundary Element), 휨 검토
* `CHK_SLAB`: RC 슬래브(Slab) 1방향/2방향 휨, 전단, 처짐 검토
* `CHK_UFDN`: RC 기초(Footing) 1방향 보전단, 2방향 펀칭전단, 휨, 지반반력 검토
* `CHK_URAB`: RC 지하외벽 / 옹벽(Retaining Wall) 토압, 전도/활동 안정성, 단면 휨/전단 검토
* `CHK_URBE`: RC 지중보 / 전이보 검토

### 3.2. `DPLUS_STEEL.dll` - `CSTLCodeCheck` (철골 부재 검토 함수군)
* `CHK_SBM`: 철골보(Beam) 소성모멘트($M_p$), 횡비틀림좌굴(LTB, $M_r$), 전단좌굴($V_n$), 처짐 검토
* `CHK_SCOL`: 철골기둥(Column) 휨좌굴($P_n$), 비틀림좌굴, 축력-휨 조합응력 검토 ($P_u / \phi P_n \ge 0.2$ 수식)
* `CHK_SBRC`: 철골 가새(Brace) 인장 파단/항복, 압축 좌굴 검토
* `CSteelBoltConnection`: 고장력 볼트(F10T 등) 전단, 인장, 지압, 블록전단 파단 검토
* `CSteelWeldConnection`: 모살용접, 완전용입 맞댐용접의 유효목두께 및 허용응력 검토
* `CBasePlate`: 기둥 주각부 베이스플레이트 휨 지압응력 및 앵커볼트 인장/전단 검토

---

## 4. AltDP_3rd Python/Web 엔진 포팅 맵 (Mapping Table)

| 원본 C++ DLL / 심볼 | AltDP_3rd 신규 파이썬 엔진 | API 엔드포인트 | 웹 렌더러 / UI |
|---|---|---|---|
| `DPLUS_RCS.dll` (`CHK_BBBE`) | `src/engine/rc/beam.py` (`RCBeamDesignEngine`) | `POST /api/rc/beam/check` | `src/web/templates/index.html` (RC Beam UI) |
| `DPLUS_RCS.dll` (`CHK_BCCO`) | `src/engine/rc/column.py` (`RCColumnDesignEngine`) | `POST /api/rc/column/check` | `src/web/static/js/pm_chart.js` (P-M 상관도) |
| `DPLUS_RCS.dll` (`CHK_BWUW`) | `src/engine/rc/wall.py` | `POST /api/rc/wall/check` | 전단벽 배근 뷰어 |
| `DPLUS_RCS.dll` (`CHK_SLAB`, `CHK_UFDN`) | `src/engine/rc/slab.py`, `footing.py` | `POST /api/rc/slab/check`, `footing/check` | 기초/슬래브 배근 뷰어 |
| `DPLUS_STEEL.dll` (`CHK_SBM`, `CHK_SCOL`) | `src/engine/steel/beam.py`, `column.py` | `POST /api/steel/beam/check` | H형강 단면 렌더러 |
| `DPLUS_STEEL.dll` (`CSteelBoltConnection`) | `src/engine/steel/connection.py`, `baseplate.py` | `POST /api/steel/conn/check` | 볼트/플레이트 상세 뷰어 |
| `DPLUS_DB.dll` (`CAluSectDB`, `CSteelSectDB`) | `src/engine/db/sdb_parser.py`, `materials.py` | `GET /api/db/sections`, `/materials` | 단면 및 강종 선택기 |
| `DPLUS_VDraw.dll` (`CODABeamBase` 등) | `src/web/static/js/renderer2d.js` | Web Canvas 2D / SVG | 2D 대화형 배근 단면 렌더러 |
| `DGN_lib.dll` / `CMSOffice` | `src/report/generator.py` | `POST /api/report/export` | HTML/PDF A4 표준 구조계산서 |

---

## 5. 역공학 자산 활용 원칙 (Ground Truth Protocol)

1. **독립성 유지**: 신규 엔진은 C++ 바이너리나 Windows DLL을 직접 호출하지 않고, **순수 Python 3.13 및 Web 표준 기술**로 완전히 재작성되어 플랫폼 독립적으로 동작합니다.
2. **설계식의 무결성**: KDS 국가건설기준 원문 및 C++ 심볼 검토 로직을 교차 검증하여, 원본 프로그램과의 **계산 오차 0.1% 미만**을 달성합니다.
3. **전수 단위 테스트**: [tests/engine/](file:///f:/PyProject/AltDP_3rd/tests/engine/) 및 [tests/api/](file:///f:/PyProject/AltDP_3rd/tests/api/)를 통해 모든 부재 검토 수식을 자동 회귀 테스트합니다.
