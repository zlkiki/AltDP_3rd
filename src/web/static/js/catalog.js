/**
 * AltDP_3rd Master 61-Module Original App Catalog (SSOT)
 * docs/04, docs/07, docs/12 및 요구사항 20-2 기반 단일 진실 공급원
 * 
 * Total: 61 Modules
 * - Tier 1: 9 플래그십 부재 (엔진 VERIFIED)
 * - Tier 2: 26 실무 주요 부재 및 기초/합성/FEM 연동군 (엔진 VERIFIED)
 * - Tier 3: 26 특수/상세/일괄/연동/글로벌 모듈 (엔진 WIP)
 */

(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        const catalog = factory();
        root.CATALOG_61_MODULES = catalog.CATALOG_61_MODULES;
        root.CATALOG_STATS = catalog.CATALOG_STATS;
        root.CatalogManager = catalog;
    }
}(typeof self !== 'undefined' ? self : this, function () {

    const CATALOG_61_MODULES = [
        // =========================================================================
        // Tier 1: 최우선 플래그십 핵심 부재 (9종 - 엔진 VERIFIED)
        // =========================================================================
        {
            key: "rc/beam/rc_beam",
            name: "RC 보 (Beam)",
            midas_dlg: "IDD_RCS_BEAM_PMODE_DLG",
            category: "rc",
            group: "beam",
            id: "rc_beam",
            domain: "RC",
            tier: "Tier 1",
            standard: "KDS 14 20 10 / 22",
            engine_status: "VERIFIED",
            is_wip: false,
            status: "Online",
            geomType: "rc_rect",
            aliases: ["rc/beam/base", "rc_beam", "beam_base"],
            icon: "icon-beam",
            component: "form_rc_beam",
            renderer: "vector_rc_beam",
            report: "rc_beam_report"
        },
        {
            key: "rc/column/rc_column",
            name: "RC 기둥 (Column)",
            midas_dlg: "IDD_RCS_COLUMN_PMODE_DLG",
            category: "rc",
            group: "column",
            id: "rc_column",
            domain: "RC",
            tier: "Tier 1",
            standard: "KDS 14 20 10",
            engine_status: "VERIFIED",
            geomType: "rc_col",
            aliases: ["rc/column/base", "rc_column", "column_base"]
        },
        {
            key: "rc/wall/rc_shear_wall",
            name: "RC 전단벽 (Shear Wall)",
            midas_dlg: "IDD_RCS_WALL_PMODE_DLG",
            category: "rc",
            group: "wall",
            id: "rc_shear_wall",
            domain: "RC",
            tier: "Tier 1",
            standard: "KDS 14 20 40",
            engine_status: "VERIFIED",
            geomType: "rc_wall",
            aliases: ["rc/wall/base", "rc_wall", "rc_shear_wall", "wall_base"]
        },
        {
            key: "rc/retaining_wall/rc_retaining_wall",
            name: "RC 옹벽 (Retaining Wall)",
            midas_dlg: "IDD_RCS_RETAINING_WALL_INPUT_DLG",
            category: "rc",
            group: "retaining_wall",
            id: "rc_retaining_wall",
            domain: "RC",
            tier: "Tier 1",
            standard: "KDS 14 20 40 / KDS 11 80 05",
            engine_status: "VERIFIED",
            geomType: "rc_wall",
            aliases: ["rc/wall/canti", "rc_retaining_wall", "retaining_wall"]
        },
        {
            key: "rc/slab/rc_slab",
            name: "RC 슬래브 (Slab)",
            midas_dlg: "IDD_RCS_SLAB_PMODE_DLG",
            category: "rc",
            group: "slab",
            id: "rc_slab",
            domain: "RC",
            tier: "Tier 1",
            standard: "KDS 14 20 40",
            engine_status: "VERIFIED",
            geomType: "rc_slab",
            aliases: ["rc/slab/base", "rc_slab", "slab_base"]
        },
        {
            key: "rc/footing/rc_iso_footing",
            name: "RC 독립기초 (Isolated Footing)",
            midas_dlg: "IDD_RCS_FOOT_PMODE_DLG",
            category: "rc",
            group: "footing",
            id: "rc_iso_footing",
            domain: "RC",
            tier: "Tier 1",
            standard: "KDS 14 20 50",
            engine_status: "VERIFIED",
            geomType: "rc_footing",
            aliases: ["rc/footing/base", "rc_footing", "rc_iso_footing", "footing_base"]
        },
        {
            key: "steel/beam/steel_beam_column",
            name: "철골 보/기둥 (Beam & Column)",
            midas_dlg: "IDD_STL_BEAMCOLUMN_INPUT_DLG",
            category: "steel",
            group: "beam",
            id: "steel_beam_column",
            domain: "STEEL",
            tier: "Tier 1",
            standard: "KDS 14 31 10",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["steel/member/beam", "steel/member/column", "steel_beam", "steel_column", "steel_beam_column"]
        },
        {
            key: "steel/baseplate/steel_baseplate",
            name: "철골 주각부 (Base Plate)",
            midas_dlg: "IDD_STL_USBP_PMODE_DLG",
            category: "steel",
            group: "baseplate",
            id: "steel_baseplate",
            domain: "STEEL",
            tier: "Tier 1",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_baseplate",
            aliases: ["steel/connection/baseplate", "steel_baseplate"]
        },
        {
            key: "steel/conn/steel_bolt_conn",
            name: "철골 볼트 접합부 (Bolt Connection)",
            midas_dlg: "IDD_STL_BOLTCONNECTION_INPUT_DLG",
            category: "steel",
            group: "conn",
            id: "steel_bolt_conn",
            domain: "STEEL",
            tier: "Tier 1",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_conn",
            aliases: ["steel/connection/bolt", "steel/connection/bolt_bear", "steel/connection/bolt_tens", "steel_bolt_conn"]
        },

        // =========================================================================
        // Tier 2: 실무 주요 부재 및 기초/합성/FEM 연동군 (26종 - 엔진 VERIFIED)
        // =========================================================================
        {
            key: "rc/column/rc_gencolumn",
            name: "RC 임의형상 기둥",
            midas_dlg: "IDD_RCS_URGC_PMODE_DLG",
            category: "rc",
            group: "column",
            id: "rc_gencolumn",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 10",
            engine_status: "VERIFIED",
            geomType: "rc_col",
            aliases: ["rc/column/irreg", "gen_column", "rc_gencolumn"]
        },
        {
            key: "rc/wall/rc_comb_wall",
            name: "RC 이형 코어벽체",
            midas_dlg: "IDD_RCS_COMBINED_WALL_INPUT_DLG",
            category: "rc",
            group: "wall",
            id: "rc_comb_wall",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 40",
            engine_status: "VERIFIED",
            geomType: "rc_wall",
            aliases: ["combined_wall", "rc_comb_wall"]
        },
        {
            key: "rc/wall/rc_basement_wall",
            name: "RC 지하외벽",
            midas_dlg: "IDD_RCS_BASEWALL_INPUT_DLG",
            category: "rc",
            group: "wall",
            id: "rc_basement_wall",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 40",
            engine_status: "VERIFIED",
            geomType: "rc_wall",
            aliases: ["rc/wall/bmt", "basement_wall", "rc_basement_wall"]
        },
        {
            key: "rc/footing/rc_comb_footing",
            name: "RC 복합기초",
            midas_dlg: "IDD_RCS_COMBINED_FOOTING_INPUT_DLG",
            category: "rc",
            group: "footing",
            id: "rc_comb_footing",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 50",
            engine_status: "VERIFIED",
            geomType: "rc_footing",
            aliases: ["rc/footing/com", "rc_comb_footing", "comb_footing"]
        },
        {
            key: "rc/footing/rc_strip_footing",
            name: "RC 줄기초",
            midas_dlg: "IDD_RCS_STRIPFOOT_INPUT_DLG",
            category: "rc",
            group: "footing",
            id: "rc_strip_footing",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 50",
            engine_status: "VERIFIED",
            geomType: "rc_footing",
            aliases: ["rc_strip_footing", "strip_footing"]
        },
        {
            key: "rc/footing/rc_pile_footing",
            name: "RC 말뚝기초",
            midas_dlg: "IDD_RCS_FOUNDATION_INPUT_DLG",
            category: "rc",
            group: "footing",
            id: "rc_pile_footing",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 50",
            engine_status: "VERIFIED",
            geomType: "rc_footing",
            aliases: ["rc/footing/pile_cap", "rc_pile_footing", "pile_footing"]
        },
        {
            key: "rc/special/rc_anchor_bolt",
            name: "콘크리트용 앵커볼트",
            midas_dlg: "IDD_DGN_ANCH_BOLT_DLG",
            category: "rc",
            group: "special",
            id: "rc_anchor_bolt",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 54",
            engine_status: "VERIFIED",
            geomType: "steel_conn",
            aliases: ["anchor_bolt", "rc_anchor_bolt"]
        },
        {
            key: "steel/brace/steel_brace",
            name: "철골 가새",
            midas_dlg: "IDD_STL_BEAMCOL_SMODE_INPUT_SECT1_DLG",
            category: "steel",
            group: "brace",
            id: "steel_brace",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 10",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["steel_brace", "brace"]
        },
        {
            key: "steel/conn/steel_endplate",
            name: "모멘트 엔드플레이트 접합부",
            midas_dlg: "IDD_STL_FORCE_INPUT_FINEND_DLG",
            category: "steel",
            group: "conn",
            id: "steel_endplate",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_conn",
            aliases: ["steel/connection/endplate", "steel_endplate", "steel_moment_bolt"]
        },
        {
            key: "steel/conn/steel_welding",
            name: "철골 용접 접합부",
            midas_dlg: "IDD_STL_WELDING_INPUT_DLG",
            category: "steel",
            group: "conn",
            id: "steel_welding",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_conn",
            aliases: ["steel_welding", "welding"]
        },
        {
            key: "steel/special/steel_crane_girder",
            name: "크레인 주행보",
            midas_dlg: "IDD_STL_CRANEGIRDER_INPUT_DLG",
            category: "steel",
            group: "special",
            id: "steel_crane_girder",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 10",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["steel/special/crane_girder", "steel_crane_girder"]
        },
        {
            key: "steel/special/steel_purlin_girt",
            name: "중도리 / 띠장",
            midas_dlg: "IDD_STL_USPG_PMODE_DLG",
            category: "steel",
            group: "special",
            id: "steel_purlin_girt",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 10",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["steel_purlin_girt", "purlin_girt"]
        },
        {
            key: "steel/special/steel_web_opening",
            name: "웨브 개공보",
            midas_dlg: "IDD_STL_WEBOPEN_PMODE_DLG",
            category: "steel",
            group: "special",
            id: "steel_web_opening",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 10",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["steel/composite/web_open", "steel_web_opening"]
        },
        {
            key: "steel/conn/steel_embedplate",
            name: "임베디드 플레이트 (매립판)",
            midas_dlg: "IDD_STL_EMBPLATE_INPUT_DLG",
            category: "steel",
            group: "conn",
            id: "steel_embedplate",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_conn",
            aliases: ["steel_embed_plate", "steel_embedplate"]
        },
        {
            key: "src/beam/src_composite_beam",
            name: "합성보 (Composite Beam)",
            midas_dlg: "IDD_SRC_COMP_BEAM_PMODE_DLG",
            category: "src",
            group: "beam",
            id: "src_composite_beam",
            domain: "SRC",
            tier: "Tier 2",
            standard: "KDS 14 31 35",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["src_beam", "src_composite_beam", "misc/src/beam"]
        },
        {
            key: "src/baseplate/src_baseplate",
            name: "SRC 주각부 베이스플레이트",
            midas_dlg: "IDD_SRC_BASE_PLATE",
            category: "src",
            group: "baseplate",
            id: "src_baseplate",
            domain: "SRC",
            tier: "Tier 2",
            standard: "KDS 14 31 35",
            engine_status: "VERIFIED",
            geomType: "steel_baseplate",
            aliases: ["src_base_plate", "src_baseplate"]
        },
        {
            key: "src/column/src_column",
            name: "매립형 SRC 기둥",
            midas_dlg: "IDD_SRC_COLUMN_INPUT_DLG",
            category: "src",
            group: "column",
            id: "src_column",
            domain: "SRC",
            tier: "Tier 2",
            standard: "KDS 14 31 35",
            engine_status: "VERIFIED",
            geomType: "rc_col",
            aliases: ["src_column", "misc/src/column"]
        },
        {
            key: "src/column/src_cft_column",
            name: "콘크리트 충전강관(CFT) 기둥",
            midas_dlg: "IDD_SRC_UCFT_PMODE_DLG",
            category: "src",
            group: "column",
            id: "src_cft_column",
            domain: "SRC",
            tier: "Tier 2",
            standard: "KDS 14 31 35",
            engine_status: "VERIFIED",
            geomType: "rc_col",
            aliases: ["cft_column", "src_cft_column"]
        },
        {
            key: "alu/member/alu_beam_col",
            name: "알루미늄 보 / 기둥",
            midas_dlg: "IDD_GUAAG_PMODE_MAIN_DLG",
            category: "alu",
            group: "member",
            id: "alu_beam_col",
            domain: "ALU",
            tier: "Tier 2",
            standard: "KDS 14 31 40",
            engine_status: "VERIFIED",
            geomType: "steel_h",
            aliases: ["alu_beam_column", "alu_beam_col"]
        },
        {
            key: "fem/foundation/foundation_fem",
            name: "RC 전면 매트기초 FEM",
            midas_dlg: "DgnSolver/FES.EXE",
            category: "fem",
            group: "foundation",
            id: "foundation_fem",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 50",
            engine_status: "VERIFIED",
            geomType: "rc_footing",
            aliases: ["foundation_fem", "fem_foundation"]
        },
        {
            key: "fem/wall/wall_2way_fem",
            name: "RC 지하외벽 2방향 FEM",
            midas_dlg: "DgnSolver/FES.EXE",
            category: "fem",
            group: "wall",
            id: "wall_2way_fem",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 40",
            engine_status: "VERIFIED",
            geomType: "rc_wall",
            aliases: ["wall_2way_fem", "fem_wall"]
        },
        {
            key: "fem/baseplate/baseplate_fem",
            name: "주각부 비선형 접촉 FEM",
            midas_dlg: "DgnSolver/Iterative.exe",
            category: "fem",
            group: "baseplate",
            id: "baseplate_fem",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_baseplate",
            aliases: ["baseplate_fem", "fem_baseplate"]
        },
        {
            key: "fem/endplate/endplate_fem",
            name: "엔드플레이트 항복선 FEM",
            midas_dlg: "DgnSolver/Iterative.exe",
            category: "fem",
            group: "endplate",
            id: "endplate_fem",
            domain: "STEEL",
            tier: "Tier 2",
            standard: "KDS 14 31 25",
            engine_status: "VERIFIED",
            geomType: "steel_conn",
            aliases: ["endplate_fem", "fem_endplate"]
        },
        {
            key: "fem/slab/slab_fem",
            name: "이형/개구부 슬래브 FEM",
            midas_dlg: "DgnSolver/FES.EXE",
            category: "fem",
            group: "slab",
            id: "slab_fem",
            domain: "RC",
            tier: "Tier 2",
            standard: "KDS 14 20 40",
            engine_status: "VERIFIED",
            geomType: "rc_slab",
            aliases: ["slab_fem", "fem_slab"]
        },
        {
            key: "report/draw/cad_draw_dxf",
            name: "2D 배근 상세도 CAD (DXF)",
            midas_dlg: "CMainFormViewDraw",
            category: "report",
            group: "draw",
            id: "cad_draw_dxf",
            domain: "CAD",
            tier: "Tier 2",
            standard: "KDS 14 20 52",
            engine_status: "VERIFIED",
            geomType: "cad_draw",
            aliases: ["cad_draw_dxf", "draw_cad"]
        },
        {
            key: "report/qntt/quantity_excel",
            name: "KDS 표준 물량산출 (Excel)",
            midas_dlg: "CMainFormViewQntt",
            category: "report",
            group: "qntt",
            id: "quantity_excel",
            domain: "MISC",
            tier: "Tier 2",
            standard: "KDS 14 20 00",
            engine_status: "VERIFIED",
            geomType: "qntt_summary",
            aliases: ["quantity_excel", "qntt_excel"]
        },

        // =========================================================================
        // Tier 3: 특수/상세/일괄/연동/글로벌 모듈 (26종 - 엔진 WIP)
        // =========================================================================
        {
            key: "rc/special/rc_buttress",
            name: "버트레스 (부벽식 지주)",
            midas_dlg: "IDD_RCS_BUTTRESS_SMODE_INPUT_DLG",
            category: "rc",
            group: "special",
            id: "rc_buttress",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 40",
            engine_status: "WIP",
            geomType: "rc_wall",
            aliases: ["buttress", "rc_buttress"]
        },
        {
            key: "rc/special/rc_stair",
            name: "RC 계단실 경사슬래브",
            midas_dlg: "IDD_RCS_URST_PMODE_DLG",
            category: "rc",
            group: "special",
            id: "rc_stair",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 40",
            engine_status: "WIP",
            geomType: "rc_slab",
            aliases: ["rc_stair"]
        },
        {
            key: "rc/special/rc_corbel",
            name: "코벨 / 브라켓",
            midas_dlg: "IDD_RCS_CORBEL_DLG",
            category: "rc",
            group: "special",
            id: "rc_corbel",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 22",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["corbel", "rc_corbel"]
        },
        {
            key: "rc/table/rc_beam_table",
            name: "RC 보 강도 테이블",
            midas_dlg: "IDD_RCS_BEAM_MLIST_DLG",
            category: "rc",
            group: "table",
            id: "rc_beam_table",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 10",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["rc/beam/table", "rc_beam_table"]
        },
        {
            key: "rc/table/rc_slab_table",
            name: "RC 슬래브 강도 테이블",
            midas_dlg: "IDD_RCS_SLAB_LIST",
            category: "rc",
            group: "table",
            id: "rc_slab_table",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 40",
            engine_status: "WIP",
            geomType: "rc_slab",
            aliases: ["rc/slab/table", "rc_slab_table"]
        },
        {
            key: "rc/batch/rc_batch_beam",
            name: "일괄 보 (다중 부재)",
            midas_dlg: "IDD_RCS_BATCH_BEAM_BUILD_DLG",
            category: "rc",
            group: "batch",
            id: "rc_batch_beam",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 10",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["rc_batch_beam"]
        },
        {
            key: "rc/batch/rc_batch_column",
            name: "일괄 기둥 (다축 최적화)",
            midas_dlg: "IDD_RCS_BATCH_COLM_BUILD_DLG",
            category: "rc",
            group: "batch",
            id: "rc_batch_column",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 10",
            engine_status: "WIP",
            geomType: "rc_col",
            aliases: ["rc_batch_column"]
        },
        {
            key: "rc/batch/rc_batch_wall",
            name: "일괄 벽체 (시공성 고려)",
            midas_dlg: "IDD_RCS_BATCHWALL_INPUT_DLG",
            category: "rc",
            group: "batch",
            id: "rc_batch_wall",
            domain: "RC",
            tier: "Tier 3",
            standard: "KDS 14 20 40",
            engine_status: "WIP",
            geomType: "rc_wall",
            aliases: ["rc_batch_wall"]
        },
        {
            key: "steel/special/steel_stair",
            name: "철골 계단",
            midas_dlg: "IDD_STL_STAIR_INPUT_DLG",
            category: "steel",
            group: "special",
            id: "steel_stair",
            domain: "STEEL",
            tier: "Tier 3",
            standard: "KDS 14 31 10",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["steel_stair"]
        },
        {
            key: "steel/special/steel_corweb_beam",
            name: "파형웨브보",
            midas_dlg: "IDD_STL_BEAMCOL_INPUT_DLG",
            category: "steel",
            group: "special",
            id: "steel_corweb_beam",
            domain: "STEEL",
            tier: "Tier 3",
            standard: "KDS 14 31 10",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["steel_corweb_beam"]
        },
        {
            key: "steel/tool/steel_tool_unbrace",
            name: "비지지길이 자동 산정 툴",
            midas_dlg: "IDD_STL_TOOL_UNBRACE_LENGTH",
            category: "steel",
            group: "tool",
            id: "steel_tool_unbrace",
            domain: "STEEL",
            tier: "Tier 3",
            standard: "KDS 14 31 10",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["steel_tool_unbrace"]
        },
        {
            key: "steel/tool/steel_tool_brace_str",
            name: "브레이스 소요강도 산정 툴",
            midas_dlg: "IDD_STL_TOOL_BRACE_STRENGTH",
            category: "steel",
            group: "tool",
            id: "steel_tool_brace_str",
            domain: "STEEL",
            tier: "Tier 3",
            standard: "KDS 14 31 10",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["steel_tool_brace_str"]
        },
        {
            key: "steel/tool/steel_tool_link_stiff",
            name: "전단링크 스티프너 산정 툴",
            midas_dlg: "IDD_STL_TOOL_LINK_STIFFENER",
            category: "steel",
            group: "tool",
            id: "steel_tool_link_stiff",
            domain: "STEEL",
            tier: "Tier 3",
            standard: "KDS 14 31 10",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["steel_tool_link_stiff"]
        },
        {
            key: "steel/tool/steel_tool_vbrace_str",
            name: "V브레이스 보강도 산정 툴",
            midas_dlg: "IDD_STL_TOOL_BEAMSTR_VBRACE",
            category: "steel",
            group: "tool",
            id: "steel_tool_vbrace_str",
            domain: "STEEL",
            tier: "Tier 3",
            standard: "KDS 14 31 10",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["steel_tool_vbrace_str"]
        },
        {
            key: "alu/member/alu_beam_col_gen",
            name: "알루미늄 임의형상 보/기둥",
            midas_dlg: "IDD_GUAMT_PMODE_MAIN_DLG",
            category: "alu",
            group: "member",
            id: "alu_beam_col_gen",
            domain: "ALU",
            tier: "Tier 3",
            standard: "KDS 14 31 40",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["alu_beam_col_gen"]
        },
        {
            key: "rfm/slab/rfm_slab",
            name: "RC 슬래브 보강 (CFRP/강판)",
            midas_dlg: "IDD_UFSL_PMODE_DLG",
            category: "rfm",
            group: "slab",
            id: "rfm_slab",
            domain: "RFM",
            tier: "Tier 3",
            standard: "KDS 14 20 90",
            engine_status: "WIP",
            geomType: "rc_slab",
            aliases: ["rfm_slab"]
        },
        {
            key: "rfm/beam/rfm_beam",
            name: "RC 보 보강 (CFRP/강판)",
            midas_dlg: "IDD_UFBE_PMODE_DLG",
            category: "rfm",
            group: "beam",
            id: "rfm_beam",
            domain: "RFM",
            tier: "Tier 3",
            standard: "KDS 14 20 90",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["rfm_beam"]
        },
        {
            key: "rfm/column/rfm_column",
            name: "RC 기둥 보강 (재킷팅)",
            midas_dlg: "IDD_UFCO_PMODE_DLG",
            category: "rfm",
            group: "column",
            id: "rfm_column",
            domain: "RFM",
            tier: "Tier 3",
            standard: "KDS 14 20 90",
            engine_status: "WIP",
            geomType: "rc_col",
            aliases: ["rfm_column"]
        },
        {
            key: "pbd/rc/pbd_rc_beam",
            name: "RC 보 성능기반설계 (소성힌지)",
            midas_dlg: "IDS_RIBBON_MENU_PBD_RCS_BEAM",
            category: "pbd",
            group: "rc",
            id: "pbd_rc_beam",
            domain: "PBD",
            tier: "Tier 3",
            standard: "KDS 41 17 00",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["pbd_rc_beam"]
        },
        {
            key: "pbd/rc/pbd_rc_column",
            name: "RC 기둥 성능기반설계 (P-M-M)",
            midas_dlg: "IDS_RIBBON_MENU_PBD_RCS_COLUMN",
            category: "pbd",
            group: "rc",
            id: "pbd_rc_column",
            domain: "PBD",
            tier: "Tier 3",
            standard: "KDS 41 17 00",
            engine_status: "WIP",
            geomType: "rc_col",
            aliases: ["pbd_rc_column"]
        },
        {
            key: "pbd/rc/pbd_rc_wall",
            name: "RC 전단벽 성능기반설계 (전단)",
            midas_dlg: "IDS_RIBBON_MENU_PBD_RCS_WALL",
            category: "pbd",
            group: "rc",
            id: "pbd_rc_wall",
            domain: "PBD",
            tier: "Tier 3",
            standard: "KDS 41 17 00",
            engine_status: "WIP",
            geomType: "rc_wall",
            aliases: ["pbd_rc_wall"]
        },
        {
            key: "interop/gen/gen_mgt_interop",
            name: "MIDAS Gen 3D 모델 연동",
            midas_dlg: "DgnPlugIn/AnalysisDB.dll",
            category: "interop",
            group: "gen",
            id: "gen_mgt_interop",
            domain: "INTEROP",
            tier: "Tier 3",
            standard: "KDS 41 10 15",
            engine_status: "WIP",
            geomType: "interop_3d",
            aliases: ["gen_mgt_interop", "mgt_interop"]
        },
        {
            key: "intl/ec/ec_rc_member",
            name: "Eurocode 콘크리트 부재",
            midas_dlg: "DLG_DPLUS_EC.ini",
            category: "intl",
            group: "ec",
            id: "ec_rc_member",
            domain: "EUROCODE",
            tier: "Tier 3",
            standard: "EN 1992-1-1",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["ec_rc_member"]
        },
        {
            key: "intl/ec/ec_steel_member",
            name: "Eurocode 강구조 부재",
            midas_dlg: "DLG_DPLUS_EC.ini",
            category: "intl",
            group: "ec",
            id: "ec_steel_member",
            domain: "EUROCODE",
            tier: "Tier 3",
            standard: "EN 1993-1-1",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["ec_steel_member"]
        },
        {
            key: "intl/is/is_rc_member",
            name: "인도 IS 456 콘크리트 부재",
            midas_dlg: "DLG_DPLUS_IS.ini",
            category: "intl",
            group: "is",
            id: "is_rc_member",
            domain: "IS",
            tier: "Tier 3",
            standard: "IS 456:2000",
            engine_status: "WIP",
            geomType: "rc_rect",
            aliases: ["is_rc_member"]
        },
        {
            key: "intl/us/us_member",
            name: "미국 ACI/AISC 부재",
            midas_dlg: "DLG_DPLUS_DGN.ini",
            category: "intl",
            group: "us",
            id: "us_member",
            domain: "US",
            tier: "Tier 3",
            standard: "ACI 318 / AISC 360",
            engine_status: "WIP",
            geomType: "steel_h",
            aliases: ["us_member"]
        }
    ];

    const CATALOG_STATS = {
        total: 61,
        tier1: 9,
        tier2: 26,
        tier3: 26,
        verified: 35,
        wip: 26
    };

    /**
     * Finds a module specification by key or alias.
     */
    function getModule(keyOrAlias) {
        if (!keyOrAlias) return null;
        const target = keyOrAlias.toLowerCase();
        return CATALOG_61_MODULES.find(m => 
            m.key.toLowerCase() === target ||
            m.id.toLowerCase() === target ||
            (m.aliases && m.aliases.some(a => a.toLowerCase() === target))
        ) || null;
    }

    /**
     * Filters modules by tier ("Tier 1", "Tier 2", "Tier 3").
     */
    function getModulesByTier(tier) {
        return CATALOG_61_MODULES.filter(m => m.tier === tier);
    }

    /**
     * Filters modules by engine status ("VERIFIED", "WIP").
     */
    function getModulesByStatus(status) {
        return CATALOG_61_MODULES.filter(m => m.engine_status === status);
    }

    /**
     * Filters modules by major category ("rc", "steel", "src", "alu", "fem", etc.).
     */
    function getModulesByCategory(category) {
        return CATALOG_61_MODULES.filter(m => m.category === category);
    }

    return {
        CATALOG_61_MODULES,
        CATALOG_STATS,
        getModule,
        getModulesByTier,
        getModulesByStatus,
        getModulesByCategory
    };
}));
