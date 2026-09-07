"""Standard WIP Response Models and 61-Module Original App Catalog.

Defines Pydantic schemas and metadata lookup for WIP (Work-In-Progress) modules
and verified engines according to docs/04, docs/12, and docs/13.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class WIPModuleDetail(BaseModel):
    """Metadata details for a structural member design module."""
    key: str = Field(..., description="Canonical module path key (e.g., rc/wall/rc_basement_wall)")
    name: str = Field(..., description="Human readable module name")
    midas_dlg: str = Field(..., description="Original app dialog ID (DLG_*.ini / docs/13)")
    category: str = Field(..., description="Top category (rc, steel, src, alu, rfm, fem, etc.)")
    group: str = Field(..., description="Subgroup (beam, column, wall, slab, footing, conn, etc.)")
    domain: str = Field(..., description="Engineering domain (RC, STEEL, SRC, ALU, etc.)")
    tier: str = Field(..., description="Prioritization tier (Tier 1, Tier 2, Tier 3)")
    standard: str = Field(..., description="Design standard code (e.g., KDS 14 20 40 : 2022)")
    engine_status: str = Field(..., description="Engine state: VERIFIED (completed) | WIP (in progress)")
    notice: str = Field(
        default="원본앱 1:1 서브탭 및 VDraw 드로잉 명세에 따라 전용 폼과 계산서가 순차 탑재됩니다.",
        description="User notification message"
    )


class WIPResponse(BaseModel):
    """Standard WIP JSON response schema when an unintegrated or WIP module is requested."""
    success: bool = Field(default=False, description="Execution success flag")
    status: str = Field(default="NOT_YET_IMPLEMENTED", description="Standard status code")
    code: str = Field(default="WIP_MODULE", description="Machine readable error/status code")
    message: str = Field(..., description="Human readable guidance message")
    module: WIPModuleDetail = Field(..., description="Module metadata specification")


# ==============================================================================
# Master Catalog of 61 Original App Modules (docs/04 & 요구사항 20)
# ==============================================================================

MODULE_CATALOG_61: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # Tier 1: 최우선 플래그십 핵심 부재 (9종)
    # --------------------------------------------------------------------------
    "rc_beam": {
        "key": "rc/beam/rc_beam",
        "name": "RC 보 (RC Beam)",
        "midas_dlg": "IDD_RCS_BEAM_PMODE_DLG",
        "category": "rc",
        "group": "beam",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 10 / 22",
        "engine_status": "VERIFIED",
        "aliases": ["rc/beam/base", "rc_beam", "beam_base"]
    },
    "rc_column": {
        "key": "rc/column/rc_column",
        "name": "RC 기둥 (RC Column)",
        "midas_dlg": "IDD_RCS_COLUMN_PMODE_DLG",
        "category": "rc",
        "group": "column",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 10 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["rc/column/base", "rc_column", "column_base"]
    },
    "rc_shear_wall": {
        "key": "rc/wall/rc_shear_wall",
        "name": "RC 전단벽 (RC Shear Wall)",
        "midas_dlg": "IDD_RCS_WALL_PMODE_DLG",
        "category": "rc",
        "group": "wall",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["rc/wall/base", "rc_wall", "rc_shear_wall", "wall_base"]
    },
    "rc_retaining_wall": {
        "key": "rc/wall/rc_retaining_wall",
        "name": "RC 옹벽 (RC Retaining Wall)",
        "midas_dlg": "IDD_RCS_RETAINING_WALL_INPUT_DLG",
        "category": "rc",
        "group": "wall",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 40 / KDS 11 80 05",
        "engine_status": "VERIFIED",
        "aliases": ["rc/wall/canti", "rc_retaining_wall", "retaining_wall"]
    },
    "rc_slab": {
        "key": "rc/slab/rc_slab",
        "name": "RC 슬래브 (RC Slab)",
        "midas_dlg": "IDD_RCS_SLAB_PMODE_DLG",
        "category": "rc",
        "group": "slab",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["rc/slab/base", "rc_slab", "slab_base"]
    },
    "rc_iso_footing": {
        "key": "rc/footing/rc_iso_footing",
        "name": "RC 독립기초 (RC Isolated Footing)",
        "midas_dlg": "IDD_RCS_FOOT_PMODE_DLG",
        "category": "rc",
        "group": "footing",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 50 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["rc/footing/base", "rc_footing", "rc_iso_footing", "footing_base"]
    },
    "steel_beam_column": {
        "key": "steel/member/steel_beam_column",
        "name": "철골 보/기둥 (Steel Beam/Column)",
        "midas_dlg": "IDD_STL_BEAMCOLUMN_INPUT_DLG",
        "category": "steel",
        "group": "member",
        "domain": "STEEL",
        "tier": "Tier 1",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["steel/member/beam", "steel/member/column", "steel_beam", "steel_column", "steel_beam_column"]
    },
    "steel_baseplate": {
        "key": "steel/connection/steel_baseplate",
        "name": "철골 주각부 베이스플레이트 (Steel Baseplate)",
        "midas_dlg": "IDD_STL_USBP_PMODE_DLG",
        "category": "steel",
        "group": "connection",
        "domain": "STEEL",
        "tier": "Tier 1",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["steel/connection/baseplate", "steel_baseplate"]
    },
    "steel_bolt_conn": {
        "key": "steel/connection/steel_bolt_conn",
        "name": "철골 볼트 접합부 (Steel Bolt Connection)",
        "midas_dlg": "IDD_STL_BOLTCONNECTION_INPUT_DLG",
        "category": "steel",
        "group": "connection",
        "domain": "STEEL",
        "tier": "Tier 1",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["steel/connection/bolt", "steel/connection/bolt_bear", "steel/connection/bolt_tens", "steel_bolt_conn"]
    },

    # --------------------------------------------------------------------------
    # Tier 2: 실무 주요 부재 및 기초/합성/FEM 연동군 (26종)
    # --------------------------------------------------------------------------
    "rc_gencolumn": {
        "key": "rc/column/rc_gencolumn",
        "name": "RC 임의형상 기둥 (Generic Column)",
        "midas_dlg": "IDD_RCS_URGC_PMODE_DLG",
        "category": "rc",
        "group": "column",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc/column/irreg", "gen_column", "rc_gencolumn"]
    },
    "rc_comb_wall": {
        "key": "rc/wall/rc_comb_wall",
        "name": "RC 이형 코어벽체 (Combined Wall)",
        "midas_dlg": "IDD_RCS_COMBINED_WALL_INPUT_DLG",
        "category": "rc",
        "group": "wall",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["combined_wall", "rc_comb_wall"]
    },
    "rc_basement_wall": {
        "key": "rc/wall/rc_basement_wall",
        "name": "RC 지하외벽 (Basement Wall)",
        "midas_dlg": "IDD_RCS_BASEWALL_INPUT_DLG",
        "category": "rc",
        "group": "wall",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc/wall/bmt", "basement_wall", "rc_basement_wall"]
    },
    "rc_comb_footing": {
        "key": "rc/footing/rc_comb_footing",
        "name": "RC 복합기초 (Combined Footing)",
        "midas_dlg": "IDD_RCS_COMBINED_FOOTING_INPUT_DLG",
        "category": "rc",
        "group": "footing",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc/footing/com", "rc_comb_footing", "comb_footing"]
    },
    "rc_strip_footing": {
        "key": "rc/footing/rc_strip_footing",
        "name": "RC 줄기초 (Strip Footing)",
        "midas_dlg": "IDD_RCS_STRIPFOOT_INPUT_DLG",
        "category": "rc",
        "group": "footing",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc_strip_footing", "strip_footing"]
    },
    "rc_pile_footing": {
        "key": "rc/footing/rc_pile_footing",
        "name": "RC 말뚝기초 (Pile Footing)",
        "midas_dlg": "IDD_RCS_FOUNDATION_INPUT_PILE_DLG",
        "category": "rc",
        "group": "footing",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc/footing/pile_cap", "rc_pile_footing", "pile_footing"]
    },
    "rc_anchor_bolt": {
        "key": "rc/connection/rc_anchor_bolt",
        "name": "콘크리트용 앵커볼트 (Anchor Bolt)",
        "midas_dlg": "IDD_DGN_ANCH_BOLT_DLG",
        "category": "rc",
        "group": "connection",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 54 : 2022",
        "engine_status": "WIP",
        "aliases": ["anchor_bolt", "rc_anchor_bolt"]
    },
    "steel_brace": {
        "key": "steel/member/steel_brace",
        "name": "철골 가새 (Steel Brace)",
        "midas_dlg": "IDD_STL_BEAMCOL_SMODE_BRACE",
        "category": "steel",
        "group": "member",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_brace", "brace"]
    },
    "steel_endplate": {
        "key": "steel/connection/steel_endplate",
        "name": "철골 모멘트 엔드플레이트 (Moment Endplate)",
        "midas_dlg": "IDD_STL_FORCE_INPUT_FINEND_DLG",
        "category": "steel",
        "group": "connection",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel/connection/endplate", "steel_endplate", "steel_moment_bolt"]
    },
    "steel_welding": {
        "key": "steel/connection/steel_welding",
        "name": "철골 용접 접합부 (Welded Connection)",
        "midas_dlg": "IDD_STL_WELDING_INPUT_DLG",
        "category": "steel",
        "group": "connection",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_welding", "welding"]
    },
    "steel_crane_girder": {
        "key": "steel/special/steel_crane_girder",
        "name": "철골 크레인 주행보 (Crane Runway Girder)",
        "midas_dlg": "IDD_STL_CRANEGIRDER_INPUT_DLG",
        "category": "steel",
        "group": "special",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel/special/crane_girder", "steel_crane_girder"]
    },
    "steel_purlin_girt": {
        "key": "steel/member/steel_purlin_girt",
        "name": "철골 중도리/띠장 (Purlin & Girt)",
        "midas_dlg": "IDD_STL_USPG_PMODE_DLG",
        "category": "steel",
        "group": "member",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_purlin_girt", "purlin_girt"]
    },
    "steel_web_opening": {
        "key": "steel/member/steel_web_opening",
        "name": "철골 웨브 개공보 (Web Opening Beam)",
        "midas_dlg": "IDD_STL_WEBOPEN_PMODE_DLG",
        "category": "steel",
        "group": "member",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel/composite/web_open", "steel_web_opening"]
    },
    "steel_embedplate": {
        "key": "steel/connection/steel_embedplate",
        "name": "철골 매립판 (Embedded Plate)",
        "midas_dlg": "IDD_STL_EMBPLATE_INPUT_DLG",
        "category": "steel",
        "group": "connection",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_embed_plate", "steel_embedplate"]
    },
    "src_composite_beam": {
        "key": "src/beam/src_composite_beam",
        "name": "SRC 합성보 (Composite Beam)",
        "midas_dlg": "IDD_SRC_COMP_BEAM_PMODE_DLG",
        "category": "src",
        "group": "beam",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35 : 2022",
        "engine_status": "WIP",
        "aliases": ["src_beam", "src_composite_beam", "misc/src/beam"]
    },
    "src_baseplate": {
        "key": "src/connection/src_baseplate",
        "name": "SRC 주각부 베이스플레이트 (SRC Baseplate)",
        "midas_dlg": "IDD_SRC_BASE_PLATE",
        "category": "src",
        "group": "connection",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35 : 2022",
        "engine_status": "WIP",
        "aliases": ["src_base_plate", "src_baseplate"]
    },
    "src_column": {
        "key": "src/column/src_column",
        "name": "매립형 SRC 기둥 (Encased SRC Column)",
        "midas_dlg": "IDD_SRC_COLUMN_INPUT_DLG",
        "category": "src",
        "group": "column",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35 : 2022",
        "engine_status": "WIP",
        "aliases": ["src_column", "misc/src/column"]
    },
    "src_cft_column": {
        "key": "src/column/src_cft_column",
        "name": "충전형 CFT 기둥 (Filled CFT Column)",
        "midas_dlg": "IDD_SRC_UCFT_PMODE_DLG",
        "category": "src",
        "group": "column",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35 : 2022",
        "engine_status": "WIP",
        "aliases": ["cft_column", "src_cft_column"]
    },
    "alu_beam_col": {
        "key": "alu/member/alu_beam_col",
        "name": "알루미늄 보/기둥 (Aluminium Beam/Column)",
        "midas_dlg": "IDD_GUAAG_PMODE_MAIN_DLG",
        "category": "alu",
        "group": "member",
        "domain": "ALU",
        "tier": "Tier 2",
        "standard": "KDS 14 31 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["alu_beam_column", "alu_beam_col"]
    },
    "foundation_fem": {
        "key": "fem/foundation/foundation_fem",
        "name": "RC 매트기초 FEM (Mat Foundation FEM)",
        "midas_dlg": "IDD_FEM_FOUNDATION_DLG",
        "category": "fem",
        "group": "foundation",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["foundation_fem", "fem_foundation"]
    },
    "wall_2way_fem": {
        "key": "fem/wall/wall_2way_fem",
        "name": "RC 지하외벽 2방향 FEM (2-Way Wall FEM)",
        "midas_dlg": "IDD_FEM_BASEWALL_DLG",
        "category": "fem",
        "group": "wall",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["wall_2way_fem", "fem_wall"]
    },
    "baseplate_fem": {
        "key": "fem/steel/baseplate_fem",
        "name": "주각부 접촉 FEM (Baseplate Contact FEM)",
        "midas_dlg": "IDD_FEM_BASEPLATE_DLG",
        "category": "fem",
        "group": "steel",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["baseplate_fem", "fem_baseplate"]
    },
    "endplate_fem": {
        "key": "fem/steel/endplate_fem",
        "name": "엔드플레이트 항복선 FEM (Endplate FEM)",
        "midas_dlg": "IDD_FEM_ENDPLATE_DLG",
        "category": "fem",
        "group": "steel",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["endplate_fem", "fem_endplate"]
    },
    "slab_fem": {
        "key": "fem/slab/slab_fem",
        "name": "이형/개구부 슬래브 FEM (Slab Plate FEM)",
        "midas_dlg": "IDD_FEM_SLAB_DLG",
        "category": "fem",
        "group": "slab",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["slab_fem", "fem_slab"]
    },
    "cad_draw_dxf": {
        "key": "cad/drawing/cad_draw_dxf",
        "name": "2D 배근 CAD 도면 생성 (AutoCAD DXF)",
        "midas_dlg": "IDD_DRAW_CAD_EXPORT_DLG",
        "category": "cad",
        "group": "drawing",
        "domain": "CAD",
        "tier": "Tier 2",
        "standard": "KDS 14 20 52 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["cad_draw_dxf", "draw_cad"]
    },
    "quantity_excel": {
        "key": "quantity/estimate/quantity_excel",
        "name": "KDS 표준 물량산출 (Excel BOM)",
        "midas_dlg": "IDD_QNTT_EXCEL_EXPORT_DLG",
        "category": "quantity",
        "group": "estimate",
        "domain": "MISC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 00 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["quantity_excel", "qntt_excel"]
    },

    # --------------------------------------------------------------------------
    # Tier 3: 특수 목적 / 상세 검토 / 일괄 관리 / 글로벌 어댑터군 (26종)
    # --------------------------------------------------------------------------
    "rc_buttress": {
        "key": "rc/special/rc_buttress",
        "name": "RC 버트레스 지주 (Buttress Wall)",
        "midas_dlg": "IDD_RCS_BUTTRESS_SMODE_DLG",
        "category": "rc",
        "group": "special",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["buttress", "rc_buttress", "misc/special/buttress"]
    },
    "rc_stair": {
        "key": "rc/special/rc_stair",
        "name": "RC 계단 (Staircase)",
        "midas_dlg": "IDD_RCS_URST_PMODE_DLG",
        "category": "rc",
        "group": "special",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc_stair", "misc/special/stair"]
    },
    "rc_corbel": {
        "key": "rc/special/rc_corbel",
        "name": "RC 코벨 / 브라켓 (Corbel & Bracket)",
        "midas_dlg": "IDD_RCS_CORBEL_DLG",
        "category": "rc",
        "group": "special",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 22 : 2022",
        "engine_status": "WIP",
        "aliases": ["corbel", "rc_corbel", "misc/special/bracket"]
    },
    "rc_beam_table": {
        "key": "rc/beam/rc_beam_table",
        "name": "RC 보 강도 일괄표 (Beam Strength Table)",
        "midas_dlg": "IDD_RCS_BEAM_MLIST_DLG",
        "category": "rc",
        "group": "beam",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc/beam/table", "rc_beam_table"]
    },
    "rc_slab_table": {
        "key": "rc/slab/rc_slab_table",
        "name": "RC 슬래브 강도 일괄표 (Slab Strength Table)",
        "midas_dlg": "IDD_RCS_SLAB_LIST",
        "category": "rc",
        "group": "slab",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc/slab/table", "rc_slab_table"]
    },
    "rc_batch_beam": {
        "key": "rc/batch/rc_batch_beam",
        "name": "RC 보 일괄설계 (Batch Beam Design)",
        "midas_dlg": "IDD_RCS_BATCH_BEAM_BUILD_DLG",
        "category": "rc",
        "group": "batch",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc_batch_beam"]
    },
    "rc_batch_column": {
        "key": "rc/batch/rc_batch_column",
        "name": "RC 기둥 일괄설계 (Batch Column Design)",
        "midas_dlg": "IDD_RCS_BATCH_COLM_BUILD_DLG",
        "category": "rc",
        "group": "batch",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc_batch_column"]
    },
    "rc_batch_wall": {
        "key": "rc/batch/rc_batch_wall",
        "name": "RC 벽체 일괄설계 (Batch Wall Design)",
        "midas_dlg": "IDD_RCS_BATCHWALL_INPUT_DLG",
        "category": "rc",
        "group": "batch",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["rc_batch_wall"]
    },
    "steel_stair": {
        "key": "steel/special/steel_stair",
        "name": "철골 계단 (Steel Staircase)",
        "midas_dlg": "IDD_STL_STAIR_INPUT_DLG",
        "category": "steel",
        "group": "special",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_stair"]
    },
    "steel_corweb_beam": {
        "key": "steel/member/steel_corweb_beam",
        "name": "철골 파형웨브보 (Corrugated Web Beam)",
        "midas_dlg": "IDD_STL_BEAMCOL_CW_DLG",
        "category": "steel",
        "group": "member",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_corrugated_beam", "steel_corweb_beam"]
    },
    "steel_tool_unbrace": {
        "key": "steel/tool/steel_tool_unbrace",
        "name": "비지지길이 산정 툴 (Unbraced Length Tool)",
        "midas_dlg": "IDD_STL_TOOL_UNBRACE_DLG",
        "category": "steel",
        "group": "tool",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_tool_unbrace"]
    },
    "steel_tool_brace_str": {
        "key": "steel/tool/steel_tool_brace_str",
        "name": "브레이스 소요강도 툴 (Brace Strength Tool)",
        "midas_dlg": "IDD_STL_TOOL_BRACE_DLG",
        "category": "steel",
        "group": "tool",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_tool_brace_str"]
    },
    "steel_tool_link_stiff": {
        "key": "steel/tool/steel_tool_link_stiff",
        "name": "전단링크 스티프너 툴 (Link Stiffener Tool)",
        "midas_dlg": "IDD_STL_TOOL_STIFF_DLG",
        "category": "steel",
        "group": "tool",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_tool_link_stiff"]
    },
    "steel_tool_vbrace_str": {
        "key": "steel/tool/steel_tool_vbrace_str",
        "name": "V브레이스 보강도 툴 (V-Brace Strength Tool)",
        "midas_dlg": "IDD_STL_TOOL_VBRACE_DLG",
        "category": "steel",
        "group": "tool",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10 : 2022",
        "engine_status": "WIP",
        "aliases": ["steel_tool_vbrace_str"]
    },
    "alu_beam_col_gen": {
        "key": "alu/member/alu_beam_col_gen",
        "name": "알루미늄 임의형상 보/기둥 (Generic ALU Beam/Column)",
        "midas_dlg": "IDD_GUAMT_PMODE_MAIN_DLG",
        "category": "alu",
        "group": "member",
        "domain": "ALU",
        "tier": "Tier 3",
        "standard": "KDS 14 31 40 : 2022",
        "engine_status": "WIP",
        "aliases": ["alu_gen_beam_column", "alu_beam_col_gen"]
    },
    "rfm_slab": {
        "key": "rfm/slab/rfm_slab",
        "name": "RC 슬래브 보수보강 (CFRP/Steel Plate Slab Retrofit)",
        "midas_dlg": "IDD_UFSL_PMODE_DLG",
        "category": "rfm",
        "group": "slab",
        "domain": "RFM",
        "tier": "Tier 3",
        "standard": "KDS 14 20 90 : 2022",
        "engine_status": "WIP",
        "aliases": ["rfm_slab"]
    },
    "rfm_beam": {
        "key": "rfm/beam/rfm_beam",
        "name": "RC 보 보수보강 (CFRP U-Wrap/Plate Beam Retrofit)",
        "midas_dlg": "IDD_UFBE_PMODE_DLG",
        "category": "rfm",
        "group": "beam",
        "domain": "RFM",
        "tier": "Tier 3",
        "standard": "KDS 14 20 90 : 2022",
        "engine_status": "WIP",
        "aliases": ["rfm_beam"]
    },
    "rfm_column": {
        "key": "rfm/column/rfm_column",
        "name": "RC 기둥 보수보강 (CFRP/Steel Jacketing Column Retrofit)",
        "midas_dlg": "IDD_UFCO_PMODE_DLG",
        "category": "rfm",
        "group": "column",
        "domain": "RFM",
        "tier": "Tier 3",
        "standard": "KDS 14 20 90 : 2022",
        "engine_status": "WIP",
        "aliases": ["rfm_column"]
    },
    "pbd_rc_beam": {
        "key": "pbd/rc/pbd_rc_beam",
        "name": "RC 보 성능기반설계 (PBD RC Beam Hinge)",
        "midas_dlg": "IDS_RIBBON_MENU_PBD_RCS_BEAM",
        "category": "pbd",
        "group": "rc",
        "domain": "PBD",
        "tier": "Tier 3",
        "standard": "KDS 41 17 00 : 2022",
        "engine_status": "WIP",
        "aliases": ["pbd_rc_beam"]
    },
    "pbd_rc_column": {
        "key": "pbd/rc/pbd_rc_column",
        "name": "RC 기둥 성능기반설계 (PBD RC Column Hinge)",
        "midas_dlg": "IDS_RIBBON_MENU_PBD_RCS_COLUMN",
        "category": "pbd",
        "group": "rc",
        "domain": "PBD",
        "tier": "Tier 3",
        "standard": "KDS 41 17 00 : 2022",
        "engine_status": "WIP",
        "aliases": ["pbd_rc_column"]
    },
    "pbd_rc_wall": {
        "key": "pbd/rc/pbd_rc_wall",
        "name": "RC 전단벽 성능기반설계 (PBD RC Wall Backbone)",
        "midas_dlg": "IDS_RIBBON_MENU_PBD_RCS_WALL",
        "category": "pbd",
        "group": "rc",
        "domain": "PBD",
        "tier": "Tier 3",
        "standard": "KDS 41 17 00 : 2022",
        "engine_status": "WIP",
        "aliases": ["pbd_rc_wall"]
    },
    "gen_mgt_interop": {
        "key": "interop/mgt/gen_mgt_interop",
        "name": "MIDAS Gen 3D 모델 연동 (.mgt Interop)",
        "midas_dlg": "IDD_GEN_MGT_INTEROP_DLG",
        "category": "interop",
        "group": "mgt",
        "domain": "INTEROP",
        "tier": "Tier 3",
        "standard": "KDS 41 10 15 : 2022",
        "engine_status": "VERIFIED",
        "aliases": ["gen_mgt_interop", "mgt_interop"]
    },
    "ec_rc_member": {
        "key": "international/ec/ec_rc_member",
        "name": "Eurocode 콘크리트 부재 (EN 1992-1-1 RC)",
        "midas_dlg": "IDD_DPLUS_EC_RC_DLG",
        "category": "international",
        "group": "ec",
        "domain": "EUROCODE",
        "tier": "Tier 3",
        "standard": "EN 1992-1-1",
        "engine_status": "VERIFIED",
        "aliases": ["ec_rc_member"]
    },
    "ec_steel_member": {
        "key": "international/ec/ec_steel_member",
        "name": "Eurocode 강구조 부재 (EN 1993-1-1 Steel)",
        "midas_dlg": "IDD_DPLUS_EC_STEEL_DLG",
        "category": "international",
        "group": "ec",
        "domain": "EUROCODE",
        "tier": "Tier 3",
        "standard": "EN 1993-1-1",
        "engine_status": "VERIFIED",
        "aliases": ["ec_steel_member"]
    },
    "is_rc_member": {
        "key": "international/is/is_rc_member",
        "name": "인도 IS 456 콘크리트 부재 (IS 456:2000 RC)",
        "midas_dlg": "IDD_DPLUS_IS_RC_DLG",
        "category": "international",
        "group": "is",
        "domain": "IS",
        "tier": "Tier 3",
        "standard": "IS 456:2000",
        "engine_status": "VERIFIED",
        "aliases": ["is_rc_member"]
    },
    "us_member": {
        "key": "international/us/us_member",
        "name": "미국 ACI/AISC 부재 (ACI 318-19 / AISC 360-16)",
        "midas_dlg": "IDD_GEN_DGNCALC_US_DLG",
        "category": "international",
        "group": "us",
        "domain": "US",
        "tier": "Tier 3",
        "standard": "ACI 318-19 / AISC 360-16",
        "engine_status": "VERIFIED",
        "aliases": ["us_member", "aci_aisc_member"]
    }
}


def get_wip_module_detail(category: str, group: str, module_id: str) -> Optional[WIPModuleDetail]:
    """Looks up module metadata from the 61-module catalog.
    
    Supports canonical paths, primary keys, and aliases.
    Returns None if the module does not match any original app module in the catalog.
    """
    search_key = f"{category}/{group}/{module_id}".lower()
    
    # 1. Direct match by canonical key
    for mod_id, meta in MODULE_CATALOG_61.items():
        if meta["key"].lower() == search_key:
            return WIPModuleDetail(
                key=meta["key"],
                name=meta["name"],
                midas_dlg=meta["midas_dlg"],
                category=meta["category"],
                group=meta["group"],
                domain=meta["domain"],
                tier=meta["tier"],
                standard=meta["standard"],
                engine_status=meta["engine_status"]
            )
            
    # 2. Match by primary module ID
    if module_id.lower() in MODULE_CATALOG_61:
        meta = MODULE_CATALOG_61[module_id.lower()]
        return WIPModuleDetail(
            key=meta["key"],
            name=meta["name"],
            midas_dlg=meta["midas_dlg"],
            category=meta["category"],
            group=meta["group"],
            domain=meta["domain"],
            tier=meta["tier"],
            standard=meta["standard"],
            engine_status=meta["engine_status"]
        )
        
    # 3. Match by aliases
    for mod_id, meta in MODULE_CATALOG_61.items():
        aliases = [a.lower() for a in meta.get("aliases", [])]
        if search_key in aliases or module_id.lower() in aliases:
            return WIPModuleDetail(
                key=meta["key"],
                name=meta["name"],
                midas_dlg=meta["midas_dlg"],
                category=meta["category"],
                group=meta["group"],
                domain=meta["domain"],
                tier=meta["tier"],
                standard=meta["standard"],
                engine_status=meta["engine_status"]
            )

    return None


def is_wip_module(category: str, group: str, module_id: str) -> bool:
    """Checks if a module is marked as WIP in the 61-module catalog."""
    detail = get_wip_module_detail(category, group, module_id)
    if detail:
        return detail.engine_status == "WIP"
    return False


def get_catalog_stats() -> Dict[str, Any]:
    """Returns tier distribution statistics for the 61-module catalog."""
    tier1 = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 1")
    tier2 = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 2")
    tier3 = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 3")
    verified = sum(1 for m in MODULE_CATALOG_61.values() if m["engine_status"] == "VERIFIED")
    wip = sum(1 for m in MODULE_CATALOG_61.values() if m["engine_status"] == "WIP")
    return {
        "total": len(MODULE_CATALOG_61),
        "tier1_count": tier1,
        "tier2_count": tier2,
        "tier3_count": tier3,
        "verified_count": verified,
        "wip_count": wip
    }
