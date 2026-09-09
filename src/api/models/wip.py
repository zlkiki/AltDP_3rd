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

# ==============================================================================
# Master Catalog of 61 Original App Modules (docs/04 & 요구사항 20-2 SSOT)
# ==============================================================================

MODULE_CATALOG_61: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # Tier 1: 최우선 플래그십 핵심 부재 (9종 - 엔진 VERIFIED)
    # --------------------------------------------------------------------------
    "rc_beam": {
        "key": "rc/beam/rc_beam",
        "name": "RC 보 (Beam)",
        "midas_dlg": "IDD_RCS_BEAM_PMODE_DLG",
        "category": "rc",
        "group": "beam",
        "id": "rc_beam",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 10 / 22",
        "engine_status": "VERIFIED",
        "geomType": "rc_rect",
        "aliases": ["rc/beam/base", "rc_beam", "beam_base", "rc/beam/rc_beam"]
    },
    "rc_column": {
        "key": "rc/column/rc_column",
        "name": "RC 기둥 (Column)",
        "midas_dlg": "IDD_RCS_COLUMN_PMODE_DLG",
        "category": "rc",
        "group": "column",
        "id": "rc_column",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 20",
        "engine_status": "VERIFIED",
        "geomType": "rc_col",
        "aliases": ["rc/column/base", "rc_column", "column_base", "rc/column/rc_column"]
    },
    "rc_shear_wall": {
        "key": "rc/wall/rc_shear_wall",
        "name": "RC 전단벽 (Shear Wall)",
        "midas_dlg": "IDD_RCS_WALL_PMODE_DLG",
        "category": "rc",
        "group": "wall",
        "id": "rc_shear_wall",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 40",
        "engine_status": "VERIFIED",
        "geomType": "rc_wall",
        "aliases": ["rc/wall/base", "rc_wall", "rc_shear_wall", "wall_base", "rc/wall/rc_shear_wall"]
    },
    "rc_retaining_wall": {
        "key": "rc/retaining_wall/rc_retaining_wall",
        "name": "RC 옹벽 (Retaining Wall)",
        "midas_dlg": "IDD_RCS_RETAINING_WALL_INPUT_DLG",
        "category": "rc",
        "group": "retaining_wall",
        "id": "rc_retaining_wall",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 40 / KDS 11 80 05",
        "engine_status": "VERIFIED",
        "geomType": "rc_wall",
        "aliases": ["rc/wall/canti", "rc_retaining_wall", "retaining_wall", "rc/retaining_wall/rc_retaining_wall"]
    },
    "rc_slab": {
        "key": "rc/slab/rc_slab",
        "name": "RC 슬래브 (Slab)",
        "midas_dlg": "IDD_RCS_SLAB_PMODE_DLG",
        "category": "rc",
        "group": "slab",
        "id": "rc_slab",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 40",
        "engine_status": "VERIFIED",
        "geomType": "rc_slab",
        "aliases": ["rc/slab/base", "rc_slab", "slab_base", "rc/slab/rc_slab"]
    },
    "rc_iso_footing": {
        "key": "rc/footing/rc_iso_footing",
        "name": "RC 독립기초 (Isolated Footing)",
        "midas_dlg": "IDD_RCS_FOOT_PMODE_DLG",
        "category": "rc",
        "group": "footing",
        "id": "rc_iso_footing",
        "domain": "RC",
        "tier": "Tier 1",
        "standard": "KDS 14 20 50",
        "engine_status": "VERIFIED",
        "geomType": "rc_footing",
        "aliases": ["rc/footing/base", "rc_footing", "rc_iso_footing", "footing_base", "rc/footing/rc_iso_footing"]
    },
    "steel_beam_column": {
        "key": "steel/beam/steel_beam_column",
        "name": "철골 보/기둥 (Beam & Column)",
        "midas_dlg": "IDD_STL_BEAMCOLUMN_INPUT_DLG",
        "category": "steel",
        "group": "beam",
        "id": "steel_beam_column",
        "domain": "STEEL",
        "tier": "Tier 1",
        "standard": "KDS 14 31 10",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["steel/member/beam", "steel/member/column", "steel_beam", "steel_column", "steel_beam_column", "steel/beam/steel_beam_column", "steel/member/steel_beam_column"]
    },
    "steel_baseplate": {
        "key": "steel/baseplate/steel_baseplate",
        "name": "철골 주각부 (Base Plate)",
        "midas_dlg": "IDD_STL_USBP_PMODE_DLG",
        "category": "steel",
        "group": "baseplate",
        "id": "steel_baseplate",
        "domain": "STEEL",
        "tier": "Tier 1",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_baseplate",
        "aliases": ["steel/connection/baseplate", "steel_baseplate", "steel/baseplate/steel_baseplate", "steel/connection/steel_baseplate"]
    },
    "steel_bolt_conn": {
        "key": "steel/conn/steel_bolt_conn",
        "name": "철골 볼트 접합부 (Bolt Connection)",
        "midas_dlg": "IDD_STL_BOLTCONNECTION_INPUT_DLG",
        "category": "steel",
        "group": "conn",
        "id": "steel_bolt_conn",
        "domain": "STEEL",
        "tier": "Tier 1",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_conn",
        "aliases": ["steel/connection/bolt", "steel/connection/bolt_bear", "steel/connection/bolt_tens", "steel_bolt_conn", "steel/conn/steel_bolt_conn", "steel/connection/steel_bolt_conn"]
    },

    # --------------------------------------------------------------------------
    # Tier 2: 실무 주요 부재 및 기초/합성/FEM 연동군 (26종 - 엔진 VERIFIED)
    # --------------------------------------------------------------------------
    "rc_gencolumn": {
        "key": "rc/column/rc_gencolumn",
        "name": "RC 임의형상 기둥",
        "midas_dlg": "IDD_RCS_URGC_PMODE_DLG",
        "category": "rc",
        "group": "column",
        "id": "rc_gencolumn",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 10",
        "engine_status": "VERIFIED",
        "geomType": "rc_col",
        "aliases": ["rc/column/irreg", "gen_column", "rc_gencolumn", "rc/column/rc_gencolumn"]
    },
    "rc_comb_wall": {
        "key": "rc/wall/rc_comb_wall",
        "name": "RC 이형 코어벽체",
        "midas_dlg": "IDD_RCS_COMBINED_WALL_INPUT_DLG",
        "category": "rc",
        "group": "wall",
        "id": "rc_comb_wall",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40",
        "engine_status": "VERIFIED",
        "geomType": "rc_wall",
        "aliases": ["combined_wall", "rc_comb_wall", "rc/wall/rc_comb_wall"]
    },
    "rc_basement_wall": {
        "key": "rc/wall/rc_basement_wall",
        "name": "RC 지하외벽",
        "midas_dlg": "IDD_RCS_BASEWALL_INPUT_DLG",
        "category": "rc",
        "group": "wall",
        "id": "rc_basement_wall",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40",
        "engine_status": "VERIFIED",
        "geomType": "rc_wall",
        "aliases": ["rc/wall/bmt", "basement_wall", "rc_basement_wall", "rc/wall/rc_basement_wall"]
    },
    "rc_comb_footing": {
        "key": "rc/footing/rc_comb_footing",
        "name": "RC 복합기초",
        "midas_dlg": "IDD_RCS_COMBINED_FOOTING_INPUT_DLG",
        "category": "rc",
        "group": "footing",
        "id": "rc_comb_footing",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50",
        "engine_status": "VERIFIED",
        "geomType": "rc_footing",
        "aliases": ["rc/footing/com", "rc_comb_footing", "comb_footing", "rc/footing/rc_comb_footing"]
    },
    "rc_strip_footing": {
        "key": "rc/footing/rc_strip_footing",
        "name": "RC 줄기초",
        "midas_dlg": "IDD_RCS_STRIPFOOT_INPUT_DLG",
        "category": "rc",
        "group": "footing",
        "id": "rc_strip_footing",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50",
        "engine_status": "VERIFIED",
        "geomType": "rc_footing",
        "aliases": ["rc_strip_footing", "strip_footing", "rc/footing/rc_strip_footing"]
    },
    "rc_pile_footing": {
        "key": "rc/footing/rc_pile_footing",
        "name": "RC 말뚝기초",
        "midas_dlg": "IDD_RCS_FOUNDATION_INPUT_DLG",
        "category": "rc",
        "group": "footing",
        "id": "rc_pile_footing",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50",
        "engine_status": "VERIFIED",
        "geomType": "rc_footing",
        "aliases": ["rc/footing/pile_cap", "rc_pile_footing", "pile_footing", "rc/footing/rc_pile_footing"]
    },
    "rc_anchor_bolt": {
        "key": "rc/special/rc_anchor_bolt",
        "name": "콘크리트용 앵커볼트",
        "midas_dlg": "IDD_DGN_ANCH_BOLT_DLG",
        "category": "rc",
        "group": "special",
        "id": "rc_anchor_bolt",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 54",
        "engine_status": "VERIFIED",
        "geomType": "steel_conn",
        "aliases": ["anchor_bolt", "rc_anchor_bolt", "rc/special/rc_anchor_bolt", "rc/connection/rc_anchor_bolt"]
    },
    "steel_brace": {
        "key": "steel/brace/steel_brace",
        "name": "철골 가새",
        "midas_dlg": "IDD_STL_BEAMCOL_SMODE_INPUT_SECT1_DLG",
        "category": "steel",
        "group": "brace",
        "id": "steel_brace",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["steel_brace", "brace", "steel/brace/steel_brace", "steel/member/steel_brace"]
    },
    "steel_endplate": {
        "key": "steel/conn/steel_endplate",
        "name": "모멘트 엔드플레이트 접합부",
        "midas_dlg": "IDD_STL_FORCE_INPUT_FINEND_DLG",
        "category": "steel",
        "group": "conn",
        "id": "steel_endplate",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_conn",
        "aliases": ["steel/connection/endplate", "steel_endplate", "steel_moment_bolt", "steel/conn/steel_endplate"]
    },
    "steel_welding": {
        "key": "steel/conn/steel_welding",
        "name": "철골 용접 접합부",
        "midas_dlg": "IDD_STL_WELDING_INPUT_DLG",
        "category": "steel",
        "group": "conn",
        "id": "steel_welding",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_conn",
        "aliases": ["steel_welding", "welding", "steel/conn/steel_welding", "steel/connection/steel_welding"]
    },
    "steel_crane_girder": {
        "key": "steel/special/steel_crane_girder",
        "name": "크레인 주행보",
        "midas_dlg": "IDD_STL_CRANEGIRDER_INPUT_DLG",
        "category": "steel",
        "group": "special",
        "id": "steel_crane_girder",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["steel/special/crane_girder", "steel_crane_girder", "steel/special/steel_crane_girder"]
    },
    "steel_purlin_girt": {
        "key": "steel/special/steel_purlin_girt",
        "name": "중도리 / 띠장",
        "midas_dlg": "IDD_STL_USPG_PMODE_DLG",
        "category": "steel",
        "group": "special",
        "id": "steel_purlin_girt",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["steel_purlin_girt", "purlin_girt", "steel/special/steel_purlin_girt", "steel/member/steel_purlin_girt"]
    },
    "steel_web_opening": {
        "key": "steel/special/steel_web_opening",
        "name": "웨브 개공보",
        "midas_dlg": "IDD_STL_WEBOPEN_PMODE_DLG",
        "category": "steel",
        "group": "special",
        "id": "steel_web_opening",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 10",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["steel/composite/web_open", "steel_web_opening", "steel/special/steel_web_opening"]
    },
    "steel_embedplate": {
        "key": "steel/conn/steel_embedplate",
        "name": "임베디드 플레이트 (매립판)",
        "midas_dlg": "IDD_STL_EMBPLATE_INPUT_DLG",
        "category": "steel",
        "group": "conn",
        "id": "steel_embedplate",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_conn",
        "aliases": ["steel_embed_plate", "steel_embedplate", "steel/conn/steel_embedplate", "steel/connection/steel_embedplate"]
    },
    "src_composite_beam": {
        "key": "src/beam/src_composite_beam",
        "name": "합성보 (Composite Beam)",
        "midas_dlg": "IDD_SRC_COMP_BEAM_PMODE_DLG",
        "category": "src",
        "group": "beam",
        "id": "src_composite_beam",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["src_beam", "src_composite_beam", "misc/src/beam", "src/beam/src_composite_beam"]
    },
    "src_baseplate": {
        "key": "src/baseplate/src_baseplate",
        "name": "SRC 주각부 베이스플레이트",
        "midas_dlg": "IDD_SRC_BASE_PLATE",
        "category": "src",
        "group": "baseplate",
        "id": "src_baseplate",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35",
        "engine_status": "VERIFIED",
        "geomType": "steel_baseplate",
        "aliases": ["src_base_plate", "src_baseplate", "src/baseplate/src_baseplate", "src/connection/src_baseplate"]
    },
    "src_column": {
        "key": "src/column/src_column",
        "name": "매립형 SRC 기둥",
        "midas_dlg": "IDD_SRC_COLUMN_INPUT_DLG",
        "category": "src",
        "group": "column",
        "id": "src_column",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35",
        "engine_status": "VERIFIED",
        "geomType": "rc_col",
        "aliases": ["src_column", "misc/src/column", "src/column/src_column"]
    },
    "src_cft_column": {
        "key": "src/column/src_cft_column",
        "name": "콘크리트 충전강관(CFT) 기둥",
        "midas_dlg": "IDD_SRC_UCFT_PMODE_DLG",
        "category": "src",
        "group": "column",
        "id": "src_cft_column",
        "domain": "SRC",
        "tier": "Tier 2",
        "standard": "KDS 14 31 35",
        "engine_status": "VERIFIED",
        "geomType": "rc_col",
        "aliases": ["cft_column", "src_cft_column", "src/column/src_cft_column"]
    },
    "alu_beam_col": {
        "key": "alu/member/alu_beam_col",
        "name": "알루미늄 보 / 기둥",
        "midas_dlg": "IDD_GUAAG_PMODE_MAIN_DLG",
        "category": "alu",
        "group": "member",
        "id": "alu_beam_col",
        "domain": "ALU",
        "tier": "Tier 2",
        "standard": "KDS 14 31 40",
        "engine_status": "VERIFIED",
        "geomType": "steel_h",
        "aliases": ["alu_beam_column", "alu_beam_col", "alu/member/alu_beam_col"]
    },
    "foundation_fem": {
        "key": "fem/foundation/foundation_fem",
        "name": "RC 전면 매트기초 FEM",
        "midas_dlg": "DgnSolver/FES.EXE",
        "category": "fem",
        "group": "foundation",
        "id": "foundation_fem",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 50",
        "engine_status": "VERIFIED",
        "geomType": "rc_footing",
        "aliases": ["foundation_fem", "fem_foundation", "fem/foundation/foundation_fem"]
    },
    "wall_2way_fem": {
        "key": "fem/wall/wall_2way_fem",
        "name": "RC 지하외벽 2방향 FEM",
        "midas_dlg": "DgnSolver/FES.EXE",
        "category": "fem",
        "group": "wall",
        "id": "wall_2way_fem",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40",
        "engine_status": "VERIFIED",
        "geomType": "rc_wall",
        "aliases": ["wall_2way_fem", "fem_wall", "fem/wall/wall_2way_fem"]
    },
    "baseplate_fem": {
        "key": "fem/baseplate/baseplate_fem",
        "name": "주각부 비선형 접촉 FEM",
        "midas_dlg": "DgnSolver/Iterative.exe",
        "category": "fem",
        "group": "baseplate",
        "id": "baseplate_fem",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_baseplate",
        "aliases": ["baseplate_fem", "fem_baseplate", "fem/steel/baseplate_fem", "fem/baseplate/baseplate_fem"]
    },
    "endplate_fem": {
        "key": "fem/endplate/endplate_fem",
        "name": "엔드플레이트 항복선 FEM",
        "midas_dlg": "DgnSolver/Iterative.exe",
        "category": "fem",
        "group": "endplate",
        "id": "endplate_fem",
        "domain": "STEEL",
        "tier": "Tier 2",
        "standard": "KDS 14 31 25",
        "engine_status": "VERIFIED",
        "geomType": "steel_conn",
        "aliases": ["endplate_fem", "fem_endplate", "fem/steel/endplate_fem", "fem/endplate/endplate_fem"]
    },
    "slab_fem": {
        "key": "fem/slab/slab_fem",
        "name": "이형/개구부 슬래브 FEM",
        "midas_dlg": "DgnSolver/FES.EXE",
        "category": "fem",
        "group": "slab",
        "id": "slab_fem",
        "domain": "RC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 40",
        "engine_status": "VERIFIED",
        "geomType": "rc_slab",
        "aliases": ["slab_fem", "fem_slab", "fem/slab/slab_fem"]
    },
    "cad_draw_dxf": {
        "key": "report/draw/cad_draw_dxf",
        "name": "2D 배근 상세도 CAD (DXF)",
        "midas_dlg": "CMainFormViewDraw",
        "category": "report",
        "group": "draw",
        "id": "cad_draw_dxf",
        "domain": "CAD",
        "tier": "Tier 2",
        "standard": "KDS 14 20 52",
        "engine_status": "VERIFIED",
        "geomType": "cad_draw",
        "aliases": ["cad_draw_dxf", "draw_cad", "cad/drawing/cad_draw_dxf", "report/draw/cad_draw_dxf"]
    },
    "quantity_excel": {
        "key": "report/qntt/quantity_excel",
        "name": "KDS 표준 물량산출 (Excel)",
        "midas_dlg": "CMainFormViewQntt",
        "category": "report",
        "group": "qntt",
        "id": "quantity_excel",
        "domain": "MISC",
        "tier": "Tier 2",
        "standard": "KDS 14 20 00",
        "engine_status": "VERIFIED",
        "geomType": "qntt_summary",
        "aliases": ["quantity_excel", "qntt_excel", "quantity/estimate/quantity_excel", "report/qntt/quantity_excel"]
    },

    # --------------------------------------------------------------------------
    # Tier 3: 특수/상세/일괄/연동/글로벌 모듈 (26종 - 엔진 WIP)
    # --------------------------------------------------------------------------
    "rc_buttress": {
        "key": "rc/special/rc_buttress",
        "name": "버트레스 (부벽식 지주)",
        "midas_dlg": "IDD_RCS_BUTTRESS_SMODE_INPUT_DLG",
        "category": "rc",
        "group": "special",
        "id": "rc_buttress",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40",
        "engine_status": "WIP",
        "geomType": "rc_wall",
        "aliases": ["buttress", "rc_buttress", "misc/special/buttress", "rc/special/rc_buttress"]
    },
    "rc_stair": {
        "key": "rc/special/rc_stair",
        "name": "RC 계단실 경사슬래브",
        "midas_dlg": "IDD_RCS_URST_PMODE_DLG",
        "category": "rc",
        "group": "special",
        "id": "rc_stair",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40",
        "engine_status": "WIP",
        "geomType": "rc_slab",
        "aliases": ["rc_stair", "misc/special/stair", "rc/special/rc_stair"]
    },
    "rc_corbel": {
        "key": "rc/special/rc_corbel",
        "name": "코벨 / 브라켓",
        "midas_dlg": "IDD_RCS_CORBEL_DLG",
        "category": "rc",
        "group": "special",
        "id": "rc_corbel",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 22",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["corbel", "rc_corbel", "misc/special/bracket", "rc/special/rc_corbel"]
    },
    "rc_beam_table": {
        "key": "rc/table/rc_beam_table",
        "name": "RC 보 강도 테이블",
        "midas_dlg": "IDD_RCS_BEAM_MLIST_DLG",
        "category": "rc",
        "group": "table",
        "id": "rc_beam_table",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 10",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["rc/beam/table", "rc_beam_table", "rc/table/rc_beam_table"]
    },
    "rc_slab_table": {
        "key": "rc/table/rc_slab_table",
        "name": "RC 슬래브 강도 테이블",
        "midas_dlg": "IDD_RCS_SLAB_LIST",
        "category": "rc",
        "group": "table",
        "id": "rc_slab_table",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40",
        "engine_status": "WIP",
        "geomType": "rc_slab",
        "aliases": ["rc/slab/table", "rc_slab_table", "rc/table/rc_slab_table"]
    },
    "rc_batch_beam": {
        "key": "rc/batch/rc_batch_beam",
        "name": "일괄 보 (다중 부재)",
        "midas_dlg": "IDD_RCS_BATCH_BEAM_BUILD_DLG",
        "category": "rc",
        "group": "batch",
        "id": "rc_batch_beam",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 10",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["rc_batch_beam", "rc/batch/rc_batch_beam"]
    },
    "rc_batch_column": {
        "key": "rc/batch/rc_batch_column",
        "name": "일괄 기둥 (다축 최적화)",
        "midas_dlg": "IDD_RCS_BATCH_COLM_BUILD_DLG",
        "category": "rc",
        "group": "batch",
        "id": "rc_batch_column",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 10",
        "engine_status": "WIP",
        "geomType": "rc_col",
        "aliases": ["rc_batch_column", "rc/batch/rc_batch_column"]
    },
    "rc_batch_wall": {
        "key": "rc/batch/rc_batch_wall",
        "name": "일괄 벽체 (시공성 고려)",
        "midas_dlg": "IDD_RCS_BATCHWALL_INPUT_DLG",
        "category": "rc",
        "group": "batch",
        "id": "rc_batch_wall",
        "domain": "RC",
        "tier": "Tier 3",
        "standard": "KDS 14 20 40",
        "engine_status": "WIP",
        "geomType": "rc_wall",
        "aliases": ["rc_batch_wall", "rc/batch/rc_batch_wall"]
    },
    "steel_stair": {
        "key": "steel/special/steel_stair",
        "name": "철골 계단",
        "midas_dlg": "IDD_STL_STAIR_INPUT_DLG",
        "category": "steel",
        "group": "special",
        "id": "steel_stair",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["steel_stair", "steel/special/steel_stair"]
    },
    "steel_corweb_beam": {
        "key": "steel/special/steel_corweb_beam",
        "name": "파형웨브보",
        "midas_dlg": "IDD_STL_BEAMCOL_INPUT_DLG",
        "category": "steel",
        "group": "special",
        "id": "steel_corweb_beam",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["steel_corrugated_beam", "steel_corweb_beam", "steel/special/steel_corweb_beam"]
    },
    "steel_tool_unbrace": {
        "key": "steel/tool/steel_tool_unbrace",
        "name": "비지지길이 자동 산정 툴",
        "midas_dlg": "IDD_STL_TOOL_UNBRACE_LENGTH",
        "category": "steel",
        "group": "tool",
        "id": "steel_tool_unbrace",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["steel_tool_unbrace", "steel/tool/steel_tool_unbrace"]
    },
    "steel_tool_brace_str": {
        "key": "steel/tool/steel_tool_brace_str",
        "name": "브레이스 소요강도 산정 툴",
        "midas_dlg": "IDD_STL_TOOL_BRACE_STRENGTH",
        "category": "steel",
        "group": "tool",
        "id": "steel_tool_brace_str",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["steel_tool_brace_str", "steel/tool/steel_tool_brace_str"]
    },
    "steel_tool_link_stiff": {
        "key": "steel/tool/steel_tool_link_stiff",
        "name": "전단링크 스티프너 산정 툴",
        "midas_dlg": "IDD_STL_TOOL_LINK_STIFFENER",
        "category": "steel",
        "group": "tool",
        "id": "steel_tool_link_stiff",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["steel_tool_link_stiff", "steel/tool/steel_tool_link_stiff"]
    },
    "steel_tool_vbrace_str": {
        "key": "steel/tool/steel_tool_vbrace_str",
        "name": "V브레이스 보강도 산정 툴",
        "midas_dlg": "IDD_STL_TOOL_BEAMSTR_VBRACE",
        "category": "steel",
        "group": "tool",
        "id": "steel_tool_vbrace_str",
        "domain": "STEEL",
        "tier": "Tier 3",
        "standard": "KDS 14 31 10",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["steel_tool_vbrace_str", "steel/tool/steel_tool_vbrace_str"]
    },
    "alu_beam_col_gen": {
        "key": "alu/member/alu_beam_col_gen",
        "name": "알루미늄 임의형상 보/기둥",
        "midas_dlg": "IDD_GUAMT_PMODE_MAIN_DLG",
        "category": "alu",
        "group": "member",
        "id": "alu_beam_col_gen",
        "domain": "ALU",
        "tier": "Tier 3",
        "standard": "KDS 14 31 40",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["alu_gen_beam_column", "alu_beam_col_gen", "alu/member/alu_beam_col_gen"]
    },
    "rfm_slab": {
        "key": "rfm/slab/rfm_slab",
        "name": "RC 슬래브 보강 (CFRP/강판)",
        "midas_dlg": "IDD_UFSL_PMODE_DLG",
        "category": "rfm",
        "group": "slab",
        "id": "rfm_slab",
        "domain": "RFM",
        "tier": "Tier 3",
        "standard": "KDS 14 20 90",
        "engine_status": "WIP",
        "geomType": "rc_slab",
        "aliases": ["rfm_slab", "rfm/slab/rfm_slab"]
    },
    "rfm_beam": {
        "key": "rfm/beam/rfm_beam",
        "name": "RC 보 보강 (CFRP/강판)",
        "midas_dlg": "IDD_UFBE_PMODE_DLG",
        "category": "rfm",
        "group": "beam",
        "id": "rfm_beam",
        "domain": "RFM",
        "tier": "Tier 3",
        "standard": "KDS 14 20 90",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["rfm_beam", "rfm/beam/rfm_beam"]
    },
    "rfm_column": {
        "key": "rfm/column/rfm_column",
        "name": "RC 기둥 보강 (재킷팅)",
        "midas_dlg": "IDD_UFCO_PMODE_DLG",
        "category": "rfm",
        "group": "column",
        "id": "rfm_column",
        "domain": "RFM",
        "tier": "Tier 3",
        "standard": "KDS 14 20 90",
        "engine_status": "WIP",
        "geomType": "rc_col",
        "aliases": ["rfm_column", "rfm/column/rfm_column"]
    },
    "pbd_rc_beam": {
        "key": "pbd/rc/pbd_rc_beam",
        "name": "RC 보 성능기반설계 (소성힌지)",
        "midas_dlg": "IDS_RIBBON_MENU_PBD_RCS_BEAM",
        "category": "pbd",
        "group": "rc",
        "id": "pbd_rc_beam",
        "domain": "PBD",
        "tier": "Tier 3",
        "standard": "KDS 41 17 00",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["pbd_rc_beam", "pbd/rc/pbd_rc_beam"]
    },
    "pbd_rc_column": {
        "key": "pbd/rc/pbd_rc_column",
        "name": "RC 기둥 성능기반설계 (P-M-M)",
        "midas_dlg": "IDS_RIBBON_MENU_PBD_RCS_COLUMN",
        "category": "pbd",
        "group": "rc",
        "id": "pbd_rc_column",
        "domain": "PBD",
        "tier": "Tier 3",
        "standard": "KDS 41 17 00",
        "engine_status": "WIP",
        "geomType": "rc_col",
        "aliases": ["pbd_rc_column", "pbd/rc/pbd_rc_column"]
    },
    "pbd_rc_wall": {
        "key": "pbd/rc/pbd_rc_wall",
        "name": "RC 전단벽 성능기반설계 (전단)",
        "midas_dlg": "IDS_RIBBON_MENU_PBD_RCS_WALL",
        "category": "pbd",
        "group": "rc",
        "id": "pbd_rc_wall",
        "domain": "PBD",
        "tier": "Tier 3",
        "standard": "KDS 41 17 00",
        "engine_status": "WIP",
        "geomType": "rc_wall",
        "aliases": ["pbd_rc_wall", "pbd/rc/pbd_rc_wall"]
    },
    "gen_mgt_interop": {
        "key": "interop/gen/gen_mgt_interop",
        "name": "MIDAS Gen 3D 모델 연동",
        "midas_dlg": "DgnPlugIn/AnalysisDB.dll",
        "category": "interop",
        "group": "gen",
        "id": "gen_mgt_interop",
        "domain": "INTEROP",
        "tier": "Tier 3",
        "standard": "KDS 41 10 15",
        "engine_status": "WIP",
        "geomType": "interop_3d",
        "aliases": ["gen_mgt_interop", "mgt_interop", "interop/mgt/gen_mgt_interop", "interop/gen/gen_mgt_interop"]
    },
    "ec_rc_member": {
        "key": "intl/ec/ec_rc_member",
        "name": "Eurocode 콘크리트 부재",
        "midas_dlg": "DLG_DPLUS_EC.ini",
        "category": "intl",
        "group": "ec",
        "id": "ec_rc_member",
        "domain": "EUROCODE",
        "tier": "Tier 3",
        "standard": "EN 1992-1-1",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["ec_rc_member", "international/ec/ec_rc_member", "intl/ec/ec_rc_member"]
    },
    "ec_steel_member": {
        "key": "intl/ec/ec_steel_member",
        "name": "Eurocode 강구조 부재",
        "midas_dlg": "DLG_DPLUS_EC.ini",
        "category": "intl",
        "group": "ec",
        "id": "ec_steel_member",
        "domain": "EUROCODE",
        "tier": "Tier 3",
        "standard": "EN 1993-1-1",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["ec_steel_member", "international/ec/ec_steel_member", "intl/ec/ec_steel_member"]
    },
    "is_rc_member": {
        "key": "intl/is/is_rc_member",
        "name": "인도 IS 456 콘크리트 부재",
        "midas_dlg": "DLG_DPLUS_IS.ini",
        "category": "intl",
        "group": "is",
        "id": "is_rc_member",
        "domain": "IS",
        "tier": "Tier 3",
        "standard": "IS 456:2000",
        "engine_status": "WIP",
        "geomType": "rc_rect",
        "aliases": ["is_rc_member", "international/is/is_rc_member", "intl/is/is_rc_member"]
    },
    "us_member": {
        "key": "intl/us/us_member",
        "name": "미국 ACI/AISC 부재",
        "midas_dlg": "DLG_DPLUS_DGN.ini",
        "category": "intl",
        "group": "us",
        "id": "us_member",
        "domain": "US",
        "tier": "Tier 3",
        "standard": "ACI 318 / AISC 360",
        "engine_status": "WIP",
        "geomType": "steel_h",
        "aliases": ["us_member", "aci_aisc_member", "international/us/us_member", "intl/us/us_member"]
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
    """Returns tier distribution statistics for the 61-module catalog.
    
    Per Requirements 20-2 Section 2.3:
    summary: { total: 61, tier1: 9, tier2: 26, tier3: 26, verified: 35, wip: 26 }
    """
    tier1 = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 1")
    tier2 = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 2")
    tier3 = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 3")
    verified = sum(1 for m in MODULE_CATALOG_61.values() if m["engine_status"] == "VERIFIED")
    wip = sum(1 for m in MODULE_CATALOG_61.values() if m["engine_status"] == "WIP")
    return {
        "total": len(MODULE_CATALOG_61),
        "tier1": tier1,
        "tier2": tier2,
        "tier3": tier3,
        "verified": verified,
        "wip": wip
    }

