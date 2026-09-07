# 17. Midas Design+ 61종 전체 모듈 종합 카탈로그 및 4대 자산 인벤토리 (SSOT)

---

## 1. 개요 및 관리 목적

본 문서는 **Midas Design+ (`Design+.exe`)** 원본 바이너리 및 리소스([`original_src/Midas Design+/`](file:///f:/PyProject/AltDP_3rd/original_src/Midas%20Design+/)), 디컴파일 C 수도코드 및 심볼([`decompiled_src/`](file:///f:/PyProject/AltDP_3rd/decompiled_src/)), 그리고 관련 기술 사양서([`docs/04_rc_design_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/04_rc_design_specification.md), [`docs/05_steel_design_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/05_steel_design_specification.md), [`docs/06_python_engine_architecture_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md), [`docs/15_fem_analysis_and_external_solver_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md))에 정의된 **총 61종 전수 모듈(RC 21종, Steel 16종, SRC 4종, ALU 2종, RFM 3종, FEM 5종, PBD 3종, CAD/물량/연동 3종, 글로벌 4종)**의 정의를 단 1종의 누락이나 축약 없이 총망라하여, **4대 참조 우선순위 자산(1순위 추출 소스, 2순위 매뉴얼/리소스, 3순위 kcsc2md 예제집, 4순위 KDS 구조기준)**과 구현 대상 파이썬 엔진 파일을 1:1로 매핑한 **전체 총괄 단일 진실 공급원(Master Inventory SSOT)**입니다.

> [!IMPORTANT]
> **🚨 4대 포팅 참조 우선순위 계층 (SSOT Priority Hierarchy)**:
> 1. **🥇 [1순위 (최우선)] 추출된 원본 소스**: `decompiled_src/core_routines/*.c` (47종 핵심 C루틴), `symbols/*.txt` (20개 DLL, 47,110 심볼)
> 2. **🥈 [2순위] 매뉴얼 및 원본 리소스**: `original_src/Midas Design+/Language/Korean/` (`Menu.ini`, `DLG_*.ini`), 공식 기술 매뉴얼
> 3. **🥉 [3순위] kcsc2md 공식 예제집**: `F:/PyProject/KCSC2MD/output/예제집/` (콘크리트구조학회 2020 & 강구조설계 2019 공인 예제집 0.1% 오차 검증 데이터)
> 4. **📚 [4순위] kcsc2md 국가건설기준**: `F:/PyProject/KCSC2MD/output/kds_md/` (KDS 14 20 00 / 14 31 00 / 41 00 00 국토교통부 표준 원문 & LaTeX 수식)

---

## 2. 콘크리트 (RC) 모듈군 전수 인벤토리 (21종)
*상세 사양서 단일 진실 공급원: [`docs/04_rc_design_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/04_rc_design_specification.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 리소스/메뉴 ID | [1순위] 추출 소스/심볼 | [2순위] 원본 DLG 리소스 | [3순위] kcsc2md 예제집 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **1** | **보 (Beam)** | `rc_beam` | `IDS_RIBBON_MENU_RCS_BEAM` | `rc__CHK_BBBE_*.c`<br>`DPLUS_RCS.dll` | `IDD_RCS_BEAM_PMODE_DLG`<br>`IDD_RCS_DEFL_DLG` | 콘크리트예제집 3.1 휨<br>4.1 전단내력 | KDS 14 20 10<br>KDS 14 20 22 | **Tier 1** | 독립 단순/연속 RC 보 휨·전단·처짐(Branson)<br>`src/engine/rc/beam.py` |
| **2** | **기둥 (Column)** | `rc_column` | `IDS_RIBBON_MENU_RCS_COLUMN` | `solver__CHK_BCCO_*.c`<br>`DPLUS_RCS.dll` | `IDD_RCS_COLUMN_PMODE_DLG`<br>`IDD_URCF_PMODE_DLG` | 콘크리트예제집 5.1<br>기둥 P-M 상관곡선 | KDS 14 20 10 | **Tier 1** | 독립 RC 기둥 200 파이버 P-M 상관곡면 및 이축휨<br>`src/engine/rc/column.py` |
| **3** | 기둥 (Column) | `rc_gencolumn` | `IDS_RIBBON_MENU_RCS_GENCOLUMN` | `CHK_BCCO_GEN`<br>`DPLUS_RCS.dll` | `IDD_RCS_URGC_PMODE_DLG`<br>`IDD_RCS_COLM_GEN_*` | 콘크리트예제집 5.5<br>비정형 단면 P-M | KDS 14 20 10 | **Tier 2** | L/T/십자/다각형 임의형상 단면 2D 파이버 P-M 해석<br>`src/engine/rc/column.py` |
| **4** | **전단벽 (Wall)** | `rc_shear_wall` | `IDS_RIBBON_MENU_RCS_SHEAR_WALL` | `rc__CHK_BWUW_*.c`<br>`DPLUS_RCS.dll` | `IDD_RCS_WALL_PMODE_DLG`<br>`IDD_RCS_BATCHWALL_*` | 콘크리트예제집 9.1<br>전단벽 배근/경계요소 | KDS 14 20 40 | **Tier 1** | 일반 전단벽 수평/수직 전단강도 및 특수경계요소 검토<br>`src/engine/rc/wall.py` |
| **5** | 전단벽 (Wall) | `rc_comb_wall` | `IDS_RIBBON_MENU_RCS_COMB_WALL` | `solver_wall__*`<br>`CURBWPModeDlg` | `IDD_RCS_COMBINED_WALL_*`<br>`CURBWPModeDlg` | 콘크리트예제집 9.3<br>이형 코어벽체 | KDS 14 20 40 | **Tier 2** | L형, T형, ㄷ형 다지 코어벽체 3차원 P-M 및 전단<br>`src/engine/rc/wall.py` |
| **6** | 지하외벽 (Wall) | `rc_basement_wall` | `IDS_RIBBON_MENU_RCS_BASEMENT_WALL` | `solver_wall__*`<br>`CURBUPModeDlg` | `IDD_RCS_BASEWALL_INPUT_DLG`<br>`CURBUPModeDlg` | 콘크리트예제집 8.4<br>지하외벽 토압/수압 | KDS 14 20 40 | **Tier 2** | 다층 지하 횡토압/수압 작용 외벽 1방향/2방향 휨<br>`src/engine/rc/wall.py` |
| **7** | **옹벽 (Wall)** | `rc_retaining_wall` | `IDS_RIBBON_MENU_RCS_RETAIN_WALL` | `rc__CHK_URAB_*.c`<br>`DPLUS_RCS.dll` | `IDD_RCS_RETAINING_WALL_*` | 콘크리트예제집 8.3<br>옹벽 외적안정/저판 | KDS 14 20 40<br>KDS 11 80 05 | **Tier 1** | 캔틸레버 옹벽 토압, 전도/활동/지지력 안정 및 배근<br>`src/engine/rc/retaining_wall.py` |
| **8** | **슬래브 (Slab)** | `rc_slab` | `IDS_RIBBON_MENU_RCS_SLAB` | `rc__CHK_SLAB_*.c`<br>`DPLUS_RCS.dll` | `IDD_RCS_SLAB_PMODE_DLG`<br>`IDD_RCS_SLAB_DESIGN_DLG` | 콘크리트예제집 7.1<br>2방향 직접설계법 | KDS 14 20 40 | **Tier 1** | 1방향/2방향 슬래브 DDM/EFM 휨모멘트 및 펀칭전단<br>`src/engine/rc/slab.py` |
| **9** | **독립기초 (Fdn)** | `rc_iso_footing` | `IDS_RIBBON_MENU_RCS_ISO_FOOTING` | `rc__CHK_UFDN_*.c`<br>`DPLUS_RCS.dll` | `IDD_RCS_FOOT_PMODE_DLG`<br>`IDD_URCF_PMODE_DLG` | 콘크리트예제집 8.1<br>독립기초 지내력 | KDS 14 20 50 | **Tier 1** | 단일 기둥 독립기초 지반 접지압, 펀칭전단, 휨배근<br>`src/engine/rc/footing.py` |
| **10**| 복합기초 (Fdn) | `rc_comb_footing` | `IDS_RIBBON_MENU_RCS_COMB_FOOTING` | `CHK_UFDN_COMB`<br>`DPLUS_RCS.dll` | `IDD_RCS_COMBINED_FOOTING_*` | 콘크리트예제집 8.2<br>2주 복합기초 | KDS 14 20 50 | **Tier 2** | 2개 이상 복합 기둥 하중 평형 및 전단/휨 단면설계<br>`src/engine/rc/footing.py` |
| **11**| 줄기초 (Fdn) | `rc_strip_footing` | `IDS_RIBBON_MENU_RCS_STRIP_FOOTING` | `CHK_UFDN_STRIP`<br>`DPLUS_RCS.dll` | `IDD_RCS_STRIPFOOT_INPUT_DLG`<br>`IDD_RCS_STRIPFOOT_*` | 조적/벽체 하부<br>연속 줄기초 | KDS 14 20 50 | **Tier 2** | 벽체 하부 연속 줄기초 단위폭 휨, 1방향 전단<br>`src/engine/rc/footing.py` |
| **12**| 말뚝기초 (Fdn) | `rc_pile_footing` | `IDS_RIBBON_MENU_RCS_FOUNDATION` | `CHK_UFDN_PILE`<br>`DPLUS_RCS.dll` | `IDD_RCS_FOUNDATION_INPUT_*` | 말뚝배열 반력/펀칭 | KDS 14 20 50 | **Tier 2** | 파일캡(Pile Cap) 말뚝 배열 반력 분배 및 펀칭전단<br>`src/engine/rc/footing.py` |
| **13**| 특수/앵커 | `rc_anchor_bolt` | `IDS_RIBBON_MENU_RCS_ANCHOR_BOLT` | `CDgnAnchBoltDlg`<br>`DPLUS_DGN.dll` | `IDD_DGN_ANCH_BOLT_DLG` | 콘크리트예제집 12.1<br>선설치/후설치 앵커 | KDS 14 20 54 | **Tier 2** | 콘크리트용 앵커볼트 인장파열, 콘파괴, 전단마찰<br>`src/engine/rc/footing.py` |
| **14**| 특수/버트레스 | `rc_buttress` | `IDS_RIBBON_MENU_RCS_BUTTRESS` | `CHK_URAB_BUTTRESS`<br>`DPLUS_RCS.dll` | `IDD_RCS_BUTTRESS_SMODE_*` | 버트레스 지주설계 | KDS 14 20 40 | **Tier 3** | 부벽식 옹벽 버트레스(Buttress) 지주 휨/전단/인장타이<br>`src/engine/rc/retaining_wall.py` |
| **15**| 특수/계단 | `rc_stair` | `IDS_RIBBON_MENU_RCS_STAIR` | `CHK_STAIR`<br>`DPLUS_RCS.dll` | `IDD_RCS_URST_PMODE_DLG` | 계단 경사슬래브 | KDS 14 20 40 | **Tier 3** | RC 계단실 경사 슬래브 휨/전단 및 계단참 단면설계<br>`src/engine/rc/slab.py` |
| **16**| 특수/코벨 | `rc_corbel` | `IDS_RIBBON_MENU_RCS_CORBEL` | `CHK_CORBEL`<br>`DPLUS_RCS.dll` | `IDD_RCS_CORBEL_*` | 콘크리트예제집 6.2<br>코벨 브래킷 전단마찰 | KDS 14 20 22 | **Tier 3** | 기둥 돌출 코벨/브라켓 전단마찰($A_{vf}$) 및 인장타이<br>`src/engine/rc/beam.py` |
| **17**| 테이블/일람표 | `rc_beam_table` | `IDS_RIBBON_MENU_RCS_BEAM_LIST` | `CDgnBeamInfoGrid`<br>`DPLUS_DGN.dll` | `IDD_RCS_BEAM_MLIST_DLG`<br>`IDD_RCS_URBL_PMODE_DLG` | 보 배근 테이블 | KDS 14 20 10 | **Tier 3** | 층별/경간별 RC 보 단면 및 배근 일괄 강도 테이블<br>`src/engine/rc/beam.py` |
| **18**| 테이블/일람표 | `rc_slab_table` | `IDS_RIBBON_MENU_RCS_SLAB_LIST` | `CDgnSlabInfoGrid`<br>`DPLUS_DGN.dll` | `IDD_RCS_SLAB_LIST`<br>`IDD_RCS_URSL_PMODE_DLG` | 슬래브 배근 테이블 | KDS 14 20 40 | **Tier 3** | 영역별 슬래브 두께 및 상/하부 배근 강도 테이블<br>`src/engine/rc/slab.py` |
| **19**| 일괄/다중부재 | `rc_batch_beam` | `IDS_RIBBON_MENU_RCS_BATCH_BEAM` | `rc__CHK_BBBE_*.c`<br>`BatchBeam` | `IDD_RCS_BATCH_BEAM_BUILD_*` | 다중 부재 일괄검토 | KDS 14 20 10 | **Tier 3** | 프로젝트 전체 RC 보 다중 부재 일괄 최적 배근/검토<br>`src/engine/rc/beam.py` |
| **20**| 일괄/다중부재 | `rc_batch_column` | `IDS_RIBBON_MENU_RCS_BATCH_COLUMN`| `solver__CHK_BCCO_*.c`<br>`BatchCol` | `IDD_RCS_BATCH_COLM_BUILD_*` | 다중 기둥 일괄 P-M | KDS 14 20 10 | **Tier 3** | 건물 전체 RC 기둥 다축 최적 단면/배근 일괄 산정<br>`src/engine/rc/column.py` |
| **21**| 일괄/다중부재 | `rc_batch_wall` | `IDS_RIBBON_MENU_RCS_BATCH_WALL` | `rc__SMART_CHK_BWUW_*.c` | `IDD_RCS_BATCHWALL_INPUT_DLG`<br>`IDD_RCS_BATCH_WALL_BUILD` | 다중 벽체 일괄검토 | KDS 14 20 40 | **Tier 3** | 건물 전체 전단벽 시공성 고려 일괄 전단/경계요소<br>`src/engine/rc/wall.py` |

---

## 3. 철골 (Steel) 모듈군 전수 인벤토리 (16종)
*상세 사양서 단일 진실 공급원: [`docs/05_steel_design_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/05_steel_design_specification.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 리소스/메뉴 ID | [1순위] 추출 소스/심볼 | [2순위] 원본 DLG 리소스 | [3순위] kcsc2md 예제집 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **22**| **보/기둥 (Member)**| `steel_beam_column` | `IDS_RIBBON_MENU_STL_BEAM_COLUMN` | `steel__CHK_USMC_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_BEAMCOLUMN_INPUT_DLG`<br>`IDD_STL_BEAMCOL_*` | 강구조예제집 3.1 LTB<br>4.1 Euler 좌굴/P-M | KDS 14 31 10 | **Tier 1** | H/Box 형강 휨(LTB), 압축좌굴, 전단, 축력-휨 P-M<br>`src/engine/steel/beam.py`, `column.py` |
| **23**| 가새/트러스 | `steel_brace` | `steel__CHK_USWB_*.c` | `steel__CHK_USWB_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_BEAMCOL_SMODE_*` | 강구조예제집 2.1<br>인장파단/세장비 | KDS 14 31 10 | **Tier 2** | 가새 인장 순단면 파단($U$ 전단지체), 압축 좌굴($KL/r$)<br>`src/engine/steel/brace.py` |
| **24**| **주각부 (Base)** | `steel_baseplate` | `IDS_RIBBON_MENU_STL_BASE_PLATE` | `steel__CHK_USBP_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_USBP_PMODE_DLG`<br>`ID_USBP_BASEPLATE` | 강구조예제집 6.1<br>주각부 지압/휨 | KDS 14 31 25 | **Tier 1** | 주각부 콘크리트 지압(삼각/사다리꼴), 두께, 앵커볼트<br>`src/engine/steel/baseplate.py` |
| **25**| **접합부 (Conn)** | `steel_bolt_conn` | `IDS_RIBBON_MENU_STL_BOLT_CONNECTION` | `steel__CHK_USBC_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_BOLTCONNECTION_INPUT_DLG`<br>`IDD_STL_BOLTCONN_*` | 강구조예제집 6.2<br>볼트 마찰/지압접합 | KDS 14 31 25 | **Tier 1** | 고장력볼트 마찰접합 전단, 지압, 블록전단파단(Block Shear)<br>`src/engine/steel/connection.py` |
| **26**| 접합부 (Conn) | `steel_endplate` | `IDS_RIBBON_MENU_STL_MOMENT_BOLT` | `steel__CHK_USEP_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_FORCE_INPUT_FINEND_DLG`<br>`IDD_STL_BOLTCONN_*` | 강구조예제집 6.3<br>항복선 이론 판두께 | KDS 14 31 25 | **Tier 2** | 모멘트 접합 확장 엔드플레이트 항복선 및 볼트 인장<br>`src/engine/steel/endplate.py` |
| **27**| 접합부 (Conn) | `steel_welding` | `IDS_RIBBON_MENU_STL_WELDING` | `steel__CHK_USWE_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_WELDING_INPUT_DLG`<br>`IDD_STL_WELDING_SMODE_*` | 강구조예제집 6.5<br>필릿/맞댐 용접 | KDS 14 31 25 | **Tier 2** | 필릿/그루브 용접 유효목두께 및 허용응력/강도 검토<br>`src/engine/steel/connection.py` |
| **28**| 특수/주행보 | `steel_crane_girder`| `IDS_RIBBON_MENU_STL_CRANE_GIRDER` | `CHK_USCG`<br>`DPLUS_STEEL.dll` | `IDD_STL_CRANEGIRDER_INPUT_DLG`<br>`IDD_STL_CRANEGIRDER_*` | 휠하중/수평충격/피로 | KDS 14 31 10 | **Tier 2** | 크레인 주행거더 수평/수직 충격, 처짐, 피로한계상태<br>`src/engine/steel/beam.py` |
| **29**| 특수/중도리 | `steel_purlin_girt` | `IDS_RIBBON_MENU_STL_PURLIN_GIRT` | `steel__CHK_USPG_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_USPG_PMODE_DLG`<br>`ID_DGN_STEEL_PURLIN_GIRT` | 냉간성형 C/Z 2축휨 | KDS 14 31 10 | **Tier 2** | 지붕 중도리(Purlin) 및 벽체 띠장(Girt) 이축휨/처짐<br>`src/engine/steel/beam.py` |
| **30**| 특수/개구부 | `steel_web_opening` | `IDS_RIBBON_MENU_STL_WEB_OPENING` | `steel__CHK_USWO_*.c`<br>`DPLUS_STEEL.dll` | `IDD_STL_WEBOPEN_PMODE_DLG`<br>`ID_DGN_STEEL_WEB_OPENING` | Vierendeel 개구부 | KDS 14 31 10 | **Tier 2** | 보 웨브 원형/사각 개구부 Vierendeel 휨-전단 및 보강재<br>`src/engine/steel/web_opening.py` |
| **31**| 접합부/매립판 | `steel_embedplate` | `IDS_RIBBON_MENU_STL_EMBEDPLATE` | `CHK_USEM`<br>`DPLUS_STEEL.dll` | `IDD_STL_EMBPLATE_INPUT_DLG`<br>`ID_USBP_EMBEDPLATE` | 매립 강판 스터드앵커 | KDS 14 31 25 | **Tier 2** | 콘크리트 매립 강판 전단/인장 스터드 앵커 콘파괴<br>`src/engine/steel/connection.py` |
| **32**| 특수/계단 | `steel_stair` | `IDS_RIBBON_MENU_STL_STAIR` | `CHK_USSTAIR`<br>`DPLUS_STEEL.dll` | `IDD_STL_STAIR_INPUT_DLG`<br>`ID_DGN_STEEL_STAIR` | 철골계단 디딤판/스트링거 | KDS 14 31 10 | **Tier 3** | C형강/플레이트 철골 계단 스트링거 거더 및 디딤판<br>`src/engine/steel/beam.py` |
| **33**| 특수/파형웨브 | `steel_corweb_beam` | `IDS_RIBBON_MENU_STL_CORWEB_BEAM` | `CHK_USCWB`<br>`DPLUS_STEEL.dll` | `IDD_STL_BEAMCOL_*` | 파형웨브 전단좌굴 | KDS 14 31 10 | **Tier 3** | 사인곡선/사다리꼴 파형웨브보 전단좌굴 및 플랜지 휨<br>`src/engine/steel/beam.py` |
| **34**| 보조툴/비지지 | `steel_tool_unbrace`| `IDS_RIBBON_MENU_STL_TOOL_UNBRACE_LENGTH` | `CSTLTool::CalcUnbrace`<br>`DPLUS_STEEL.dll` | `IDD_STL_TOOL_UNBRACE_*` | 비지지길이 $L_b$ 산정 | KDS 14 31 10 | **Tier 3** | 부재 경계조건 및 가새 연결점 기반 자동 비지지길이 산출<br>`src/engine/steel/compactness.py` |
| **35**| 보조툴/가새강도 | `steel_tool_brace_str` | `IDS_RIBBON_MENU_STL_TOOL_BRACE_STRENGTH` | `CSTLTool::CalcBraceStr`<br>`DPLUS_STEEL.dll` | `IDD_STL_TOOL_BRACE_*` | 브레이싱 소요강도 | KDS 14 31 10 | **Tier 3** | 기둥/보 좌굴 방지용 브레이싱 소요 강도 및 강성 산출<br>`src/engine/steel/brace.py` |
| **36**| 보조툴/스티프너 | `steel_tool_link_stiff`| `IDS_RIBBON_MENU_STL_TOOL_LINK_STIFFENER`| `CSTLTool::CalcLinkStiff`<br>`DPLUS_STEEL.dll`| `IDD_STL_TOOL_STIFF_*` | 전단링크 스티프너 | KDS 14 31 10 | **Tier 3** | 편심가새(EBF) 전단링크 웨브 스티프너 배치 및 간격<br>`src/engine/steel/brace.py` |
| **37**| 보조툴/V브레이스 | `steel_tool_vbrace_str`| `IDS_RIBBON_MENU_STL_TOOL_BEAMSTR_VBRACE`| `CSTLTool::CalcVBraceStr`<br>`DPLUS_STEEL.dll`| `IDD_STL_TOOL_VBRACE_*` | V브레이스 보 보강 | KDS 14 31 10 | **Tier 3** | V형/역V형 가새 접합 보의 수직 불평형 하중 및 강도<br>`src/engine/steel/brace.py` |

---

## 4. 합성구조 (SRC) 모듈군 전수 인벤토리 (4종)
*상세 사양서 단일 진실 공급원: [`docs/06_python_engine_architecture_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 리소스/메뉴 ID | [1순위] 추출 소스/심볼 | [2순위] 원본 DLG 리소스 | [3순위] kcsc2md 예제집 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **38**| **합성보 (Beam)** | `src_composite_beam` | `IDS_RIBBON_MENU_SRC_COMPOSITE_BEAM`| `CSRCCodeCheck::CHK_UCCB`<br>`DPLUS_SRC.dll` | `IDD_SRC_COMP_BEAM_PMODE_DLG`<br>`ID_DGN_SRC_COMPOSITE_BEAM` | 합성슬래브/보 휨내력 | KDS 14 31 35 | **Tier 2** | 강재보+슬래브 완전/부분 합성거동, 전단연결재(Stud)<br>`src/engine/src_composite/` |
| **39**| **주각부 (Base)** | `src_baseplate` | `IDS_RIBBON_MENU_SRC_BASE_PLATE` | `CSRCBasePlate`<br>`DPLUS_SRC.dll` | `IDD_SRC_BASE_PLATE`<br>`ID_DGN_SRC_BASE_PLATE` | SRC 주각부 지압 | KDS 14 31 35 | **Tier 2** | 매립형/노출형 SRC 복합 기둥 주각부 지압 및 앵커<br>`src/engine/src_composite/` |
| **40**| **SRC 기둥 (Col)** | `src_column` | `IDS_RIBBON_MENU_SRC_COLUMN` | `CSRCCodeCheck::CHK_UCCO`<br>`DPLUS_SRC.dll` | `IDD_SRC_COLUMN_INPUT_DLG`<br>`ID_DGN_SRC_COLUMN` | 강구조예제집 5.3<br>매립형 SRC 기둥 | KDS 14 31 35 | **Tier 2** | H/십자형강 매립형 콘크리트 기둥 소성압축 및 P-M 곡선<br>`src/engine/src_composite/` |
| **41**| **CFT 기둥 (Col)** | `src_cft_column` | `IDS_RIBBON_MENU_SRC_CFT_COLUMN` | `CSRCCodeCheck::CHK_UCFT`<br>`DPLUS_SRC.dll` | `IDD_SRC_UCFT_PMODE_DLG`<br>`ID_DGN_SRC_CFT_COLUMN` | 강관 콘크리트 충전 | KDS 14 31 35 | **Tier 2** | 원형/각형 강관 콘크리트 충전(CFT) 구속효과 및 P-M<br>`src/engine/src_composite/` |

---

## 5. 알루미늄 (ALU) 모듈군 전수 인벤토리 (2종)
*상세 사양서 단일 진실 공급원: [`docs/06_python_engine_architecture_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 리소스/메뉴 ID | [1순위] 추출 소스/심볼 | [2순위] 원본 DLG 리소스 | [3순위] kcsc2md 예제집 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **42**| 보/기둥 (Member) | `alu_beam_col` | `IDS_RIBBON_MENU_ALU_BEAMCOL` | `CALUCodeCheck::CHK_UAAG`<br>`DPLUS_ALU.dll` | `IDD_GUAAG_PMODE_MAIN_DLG`<br>`IDD_GUAAG_SMODE_SECT1_DLG` | 알루미늄 구조기준 | KDS 14 31 40 | **Tier 2** | 알루미늄 표준 압출단면 휨, 압축, 국부좌굴, HAZ 저감<br>`src/engine/alu/` |
| **43**| 임의형상 (Member) | `alu_beam_col_gen` | `IDS_RIBBON_MENU_ALU_BEAMCOLGEN` | `CALUCodeCheck::CHK_UAMT`<br>`DPLUS_ALU.dll` | `IDD_GUAMT_PMODE_MAIN_DLG`<br>`IDD_GUAMT_SMODE_SECT1_DLG` | 다축 임의형상 알루미늄 | KDS 14 31 40 | **Tier 3** | 커튼월 등 비정형 다실 중공 알루미늄 압출형재 다축 설계<br>`src/engine/alu/` |

---

## 6. 보수/보강 (RFM) 모듈군 전수 인벤토리 (3종)
*상세 사양서 단일 진실 공급원: [`docs/06_python_engine_architecture_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 리소스/메뉴 ID | [1순위] 추출 소스/심볼 | [2순위] 원본 DLG 리소스 | [3순위] kcsc2md 예제집 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **44**| 슬래브 보강 | `rfm_slab` | `IDS_RIBBON_MENU_RFM_SLAB` | `CRFMCodeCheck::CHK_UFSL`<br>`DPLUS_RFM.dll` | `IDD_UFSL_PMODE_DLG`<br>`ID_DGN_RFM_SLAB` | 안전성평가기준 보강 | KDS 14 20 90 | **Tier 3** | RC 슬래브 하부 CFRP 탄소섬유판/강판 부착 휨/처짐 보강<br>`src/engine/rfm/` |
| **45**| 보 보강 | `rfm_beam` | `IDS_RIBBON_MENU_RFM_BEAM` | `CRFMCodeCheck::CHK_UFBE`<br>`DPLUS_RFM.dll` | `IDD_UFBE_PMODE_DLG`<br>`ID_DGN_RFM_BEAM` | CFRP 휨/전단 보강 | KDS 14 20 90 | **Tier 3** | 기존 RC 보 휨(하부판) 및 전단(U-Jacketing) 보수보강<br>`src/engine/rfm/` |
| **46**| 기둥 보강 | `rfm_column` | `IDS_RIBBON_MENU_RFM_COLUMN` | `CRFMCodeCheck::CHK_UFCO`<br>`DPLUS_RFM.dll` | `IDD_UFCO_PMODE_DLG`<br>`ID_DGN_RFM_COLUMN` | 강판/CFRP 재킷팅 | KDS 14 20 90 | **Tier 3** | RC 기둥 강판 재킷팅 및 섬유보강 구속압축도 증진 P-M<br>`src/engine/rfm/` |

---

## 7. 2D FEM 평판 휨 & 접촉 솔버 연동 부재군 (5종)
*상세 사양서 단일 진실 공급원: [`docs/15_fem_analysis_and_external_solver_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 솔버 바이너리 | [1순위] 추출 소스/심볼 | [2순위] 연동 명세 | [3순위] kcsc2md 예제집 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **47**| **기초 FEM** | `foundation_fem` | `DgnSolver/FES.EXE`<br>`mfsolver.exe` | `CDBSolverTool`<br>`DPLUS_DB.dll` | [`docs/15`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) 3.1절 | Winkler 탄성지반 매트 | KDS 14 20 50 | **Tier 2** | 전면 매트기초 후판휨(DKMQ)+지반스프링 인장분리 비선형해석<br>`src/engine/fem/foundation_fem.py` |
| **48**| **외벽 FEM** | `wall_2way_fem` | `DgnSolver/FES.EXE`<br>`mfsolver.exe` | `CDBSolverTool`<br>`DPLUS_DB.dll` | [`docs/15`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) 3.2절 | 2방향 지하외벽 토압 | KDS 14 20 40 | **Tier 2** | 횡토압/수압 작용 지하외벽 2방향 판휨 및 다층 지지 경계해석<br>`src/engine/fem/wall_2way_fem.py` |
| **49**| **주각부 FEM** | `baseplate_fem` | `DgnSolver/Iterative.exe` | `CDBSolverTool`<br>`DPLUS_STEEL.dll` | [`docs/15`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) 3.3절 | 비선형 접촉 주각부 | KDS 14 31 25 | **Tier 2** | 콘크리트 압축 지압-앵커볼트 인장 상호작용 비선형 접촉 FEM<br>`src/engine/fem/baseplate_fem.py` |
| **50**| **엔드플레이트 FEM** | `endplate_fem` | `DgnSolver/Iterative.exe` | `CDBSolverTool`<br>`DPLUS_STEEL.dll` | [`docs/15`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) 3.4절 | 항복선(Yield Line) | KDS 14 31 25 | **Tier 2** | 모멘트 접합 엔드플레이트 소성 항복선 수치해석 및 프라잉력<br>`src/engine/fem/endplate_fem.py` |
| **51**| **슬래브 FEM** | `slab_fem` | `DgnSolver/FES.EXE` | `CDBSolverTool`<br>`DPLUS_DB.dll` | [`docs/15`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) 3.5절 | 개구부 슬래브 응력 | KDS 14 20 40 | **Tier 2** | 다각형 이형 슬래브 및 개구부 주변 응력집중 판휨 해석<br>`src/engine/fem/slab_fem.py` |

---

## 8. 성능기반설계 (PBD) 모듈군 전수 인벤토리 (3종)
*상세 사양서 단일 진실 공급원: [`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 리소스/메뉴 ID | [1순위] 추출 소스/심볼 | [2순위] 원본 매뉴얼 | [3순위] 검증 기준 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **52**| PBD 보 | `pbd_rc_beam` | `IDS_RIBBON_MENU_PBD_RCS_BEAM` | `DPLUS_RCS.dll`<br>`PBD_Beam` | `Menu.ini` PBD 세션 | ASCE 41-17 보 소성힌지 | KDS 41 17 00 | **Tier 3** | 보 단부 휨 모멘트-회전각($M-\theta$) 비선형 백본곡선 산정<br>`src/engine/pbd/` |
| **53**| PBD 기둥 | `pbd_rc_column` | `IDS_RIBBON_MENU_PBD_RCS_COLUMN`| `DPLUS_RCS.dll`<br>`PBD_Column` | `Menu.ini` PBD 세션 | ASCE 41-17 기둥 P-M-M | KDS 41 17 00 | **Tier 3** | 축력 연동 축력-휨 소성힌지 및 성능수준(IO, LS, CP) 평가<br>`src/engine/pbd/` |
| **54**| PBD 전단벽 | `pbd_rc_wall` | `IDS_RIBBON_MENU_PBD_RCS_WALL` | `DPLUS_RCS.dll`<br>`PBD_Wall` | `Menu.ini` PBD 세션 | 전단벽 면내 비선형 전단 | KDS 41 17 00 | **Tier 3** | 전단벽 수평 변위-전단력 소성 백본곡선 및 취약도 평가<br>`src/engine/pbd/` |

---

## 9. CAD 도면 / 물량산출 / 모델 연동 모듈군 (3종)
*상세 사양서 단일 진실 공급원: [`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)*

| No | 부재 분류 | 모듈 식별자 (`type`) | 원본 바이너리/모듈 | [1순위] 추출 소스/심볼 | [2순위] 원본 폼뷰/모드 | [3순위] 표준 양식 | [4순위] KDS 조항 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **55**| **CAD 도면** | `cad_draw_dxf` | `DPLUS_VDraw.dll`<br>`DPLUS_DWG.dll` | `CODABeamBase`<br>`CODADrawTool` | `CMainFormViewDraw`<br>(Draw View) | KDS 구조도면 상세도 | KDS 14 20 52 | **Tier 2** | ezdxf 기반 부재 배근 상세도, 단면도, 주근/대근 DXF CAD 생성<br>`src/report/cad_exporter.py` |
| **56**| **물량 산출** | `quantity_excel` | `DGN_lib.dll`<br>`CMSExcel` | `CMSWorkRec`<br>`ChartData` | `CMainFormViewQntt`<br>(Qntt View) | 건축적산 표준품셈 | KDS 14 20 00 | **Tier 2** | 콘크리트 루베, 거푸집 헤베, 철근 직경별 톤수 집계 Excel 익스포트<br>`src/report/excel_exporter.py` |
| **57**| **Gen 연동** | `gen_mgt_interop` | `DgnPlugIn/AnalysisDB.dll`<br>`GEN_UmdDataBase.dll` | `GEN_DgnCalc_KR.dll`<br>`AnalysisDB` | MIDAS Gen 3D 모델 | .mgt 텍스트 스크립트 | KDS 41 10 15 | **Tier 3** | Gen 3D 해석 모델 파싱, 3차원 부재력 DB 구축, Governing LCB 선별<br>`src/engine/interop/` |

---

## 10. 글로벌 규준 (International Codes) 어댑터군 (4종)
*상세 사양서 단일 진실 공급원: [`docs/09_decompiled_source_and_symbol_inventory.md`](file:///f:/PyProject/AltDP_3rd/docs/09_decompiled_source_and_symbol_inventory.md)*

| No | 규준 분류 | 모듈 식별자 (`type`) | 원본 바이너리/모듈 | [1순위] 추출 소스/심볼 | [2순위] 원본 DLG 리소스 | [3순위] 국제 공인 예제 | [4순위] 국제 기준 코드 | 티어 | 핵심 설계 기능 및 구현 대상 파일 |
|:---:|---|---|---|---|---|---|---|:---:|---|
| **58**| 유로코드 콘크리트 | `ec_rc_member` | `DPLUS_EC.dll` | `CECRCSCodeCheck`<br>`CHK_EBBE`, `CHK_ECCO` | `IDD_ESMC_PMODE_DLG`<br>`DLG_DPLUS_EC.ini` | Eurocode 2 Worked Ex. | EN 1992-1-1 (EC2) | **Tier 3** | Eurocode 2 부분안전계수($\gamma_c, \gamma_s$) 기반 RC 부재 휨/압축<br>`src/engine/international/` |
| **59**| 유로코드 강구조 | `ec_steel_member` | `DPLUS_EC.dll` | `CECSteelCodeCheck`<br>`CHK_ESMC`, `CHK_ESBP` | `IDD_STL_BOLTCONN_EC_*` | Eurocode 3 Worked Ex. | EN 1993-1-1 (EC3) | **Tier 3** | Eurocode 3 판폭두께 Class 1~4 판정 및 $\gamma_{M0}$ 부재 강도<br>`src/engine/international/` |
| **60**| 인도 콘크리트 | `is_rc_member` | `DPLUS_IS.dll` | `CISRCSCodeCheck`<br>`CHK_IBBE`, `CHK_ICCO` | `DLG_DPLUS_IS.ini` | IS 456 Design Aids | IS 456:2000 | **Tier 3** | 인도 국가기준 IS 456 한계상태설계법(LSM) RC 보/기둥 설계<br>`src/engine/international/` |
| **61**| 미국 콘크리트/강재 | `us_member` | `GEN_DgnCalc_US.dll` | `US-Calc`<br>`DPLUS_DGN.dll` | `DLG_DPLUS_DGN.ini` | ACI 318 / AISC 360 Ex. | ACI 318-19<br>AISC 360-16 | **Tier 3** | 미국 기준 imperial 단위계(kip, in, psi) 및 LRFD 부재 설계<br>`src/engine/international/` |

---

## 11. 61종 전수 모듈 티어(Tier)별 총괄 통계 및 로드맵 매핑

| 티어 구분 | 대상 부재 및 모듈 목록 | 모듈 수 | 구현 상태 및 우선순위 |
|---|---|:---:|---|
| **Tier 1 (최우선 기반 부재군)** | • **RC 6종**: `rc_beam`, `rc_column`, `rc_shear_wall`, `rc_retaining_wall`, `rc_slab`, `rc_iso_footing`<br>• **Steel 3종**: `steel_beam_column`, `steel_baseplate`, `steel_bolt_conn` | **9종** | **엔진 100% 완료 (`src/engine/`)**<br>docs 07 반응형 4-Pane UI 완성 대상 |
| **Tier 2 (확장 및 FEM 연동군)** | • **RC 6종**: `rc_gencolumn`, `rc_comb_wall`, `rc_basement_wall`, `rc_comb_footing`, `rc_strip_footing`, `rc_pile_footing`<br>• **Steel 7종**: `steel_brace`, `steel_endplate`, `steel_welding`, `steel_crane_girder`, `steel_purlin_girt`, `steel_web_opening`, `steel_embedplate`<br>• **SRC 4종**: `src_composite_beam`, `src_baseplate`, `src_column`, `src_cft_column`<br>• **ALU 1종**: `alu_beam_col`<br>• **FEM 5종**: `foundation_fem`, `wall_2way_fem`, `baseplate_fem`, `endplate_fem`, `slab_fem`<br>• **CAD/물량 2종**: `cad_draw_dxf`, `quantity_excel`<br>• **앵커 1종**: `rc_anchor_bolt` | **26종** | **엔진 100% 완료 (`src/engine/`)**<br>docs 07 4대 폼뷰 및 계산서 연동 대상 |
| **Tier 3 (고급 특수/일괄/연동군)** | • **RC 8종**: `rc_buttress`, `rc_stair`, `rc_corbel`, `rc_beam_table`, `rc_slab_table`, `rc_batch_beam`, `rc_batch_column`, `rc_batch_wall`<br>• **Steel 5종**: `steel_stair`, `steel_corweb_beam`, `steel_tool_unbrace`, `steel_tool_brace_str`, `steel_tool_link_stiff`, `steel_tool_vbrace_str` (툴 통합 5종)<br>• **ALU 1종**: `alu_beam_col_gen`<br>• **RFM 3종**: `rfm_slab`, `rfm_beam`, `rfm_column`<br>• **PBD 3종**: `pbd_rc_beam`, `pbd_rc_column`, `pbd_rc_wall`<br>• **Gen연동 1종**: `gen_mgt_interop`<br>• **글로벌 4종**: `ec_rc_member`, `ec_steel_member`, `is_rc_member`, `us_member` | **26종** | **Phase 9 ~ 11 단계적 전개**<br>Zero-Dependency 모듈식 포팅 |
| **총계** | **Midas Design+ 원본 61종 전체 부재/해석/연동 모듈 전수** | **61종** | **1종의 누락이나 축약 없이 100% 명세 구축** |
