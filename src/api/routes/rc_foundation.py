"""RC Footing and Retaining Wall FastAPI Routes for AltDP_3rd."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.footing import (
    ColumnType,
    SpreadFootingInput,
    RCSpreadFooting,
    CombinedFootingInput,
    RCCombinedFooting,
    UndergroundBeamInput,
    RCUndergroundBeam
)
from src.engine.rc.retaining_wall import (
    RetainingWallType,
    SoilProperties,
    RetainingWallGeometry,
    RetainingWallInput,
    RCRetainingWall
)
from src.api.schemas.rc_foundation import (
    SpreadFootingRequest,
    CombinedFootingRequest,
    UndergroundBeamRequest,
    RetainingWallRequest
)

router = APIRouter(prefix="/api/rc/foundation", tags=["Reinforced Concrete Foundation & Retaining Wall"])


@router.post("/spread-footing/design")
async def design_spread_footing(req: SpreadFootingRequest) -> Dict[str, Any]:
    """Design and check Isolated/Spread Footing (bearing, 1-way shear, punching, flexure)."""
    try:
        col_type = ColumnType.INTERIOR
        if req.col_type.lower() == "edge":
            col_type = ColumnType.EDGE
        elif req.col_type.lower() == "corner":
            col_type = ColumnType.CORNER
            
        inp = SpreadFootingInput(
            name=req.name,
            Bx=req.Bx,
            Ly=req.Ly,
            thickness_H=req.thickness_H,
            depth_Df=req.depth_Df,
            cover=req.cover,
            col_cx=req.col_cx,
            col_cy=req.col_cy,
            col_type=col_type,
            qa_allowable=req.qa_allowable,
            soil_unit_weight=req.soil_unit_weight,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            rebar_x_diam=req.rebar_x_diam,
            rebar_x_spacing=req.rebar_x_spacing,
            rebar_y_diam=req.rebar_y_diam,
            rebar_y_spacing=req.rebar_y_spacing,
            P_serv=req.P_serv,
            Mx_serv=req.Mx_serv,
            My_serv=req.My_serv,
            Pu=req.Pu,
            Mux=req.Mux,
            Muy=req.Muy
        )
        footing = RCSpreadFooting(inp)
        res = footing.solve()
        
        # 2D Canvas Visualization Data
        vis_2d = {
            "footing_polygon": [
                [-req.Bx / 2.0, -req.Ly / 2.0],
                [req.Bx / 2.0, -req.Ly / 2.0],
                [req.Bx / 2.0, req.Ly / 2.0],
                [-req.Bx / 2.0, req.Ly / 2.0]
            ],
            "column_polygon": [
                [-req.col_cx / 2.0, -req.col_cy / 2.0],
                [req.col_cx / 2.0, -req.col_cy / 2.0],
                [req.col_cx / 2.0, req.col_cy / 2.0],
                [-req.col_cx / 2.0, req.col_cy / 2.0]
            ],
            "punching_perimeter": [
                [-(req.col_cx + res.shear.d_avg) / 2.0, -(req.col_cy + res.shear.d_avg) / 2.0],
                [(req.col_cx + res.shear.d_avg) / 2.0, -(req.col_cy + res.shear.d_avg) / 2.0],
                [(req.col_cx + res.shear.d_avg) / 2.0, (req.col_cy + res.shear.d_avg) / 2.0],
                [-(req.col_cx + res.shear.d_avg) / 2.0, (req.col_cy + res.shear.d_avg) / 2.0]
            ],
            "bearing_profile": {
                "q_max": res.bearing.q_max,
                "q_min": res.bearing.q_min,
                "ex": res.bearing.ex,
                "ey": res.bearing.ey
            }
        }
        
        return {
            "status": "success",
            "name": res.name,
            "is_safe": res.is_safe,
            "max_dcr": round(res.max_dcr, 3),
            "bearing": {
                "q_max": round(res.bearing.q_max, 2),
                "q_min": round(res.bearing.q_min, 2),
                "qa_allowable": res.bearing.qa_allowable,
                "ex": round(res.bearing.ex, 1),
                "ey": round(res.bearing.ey, 1),
                "is_tension_separated": res.bearing.is_tension_separated,
                "dcr": round(res.bearing.dcr_bearing, 3),
                "is_ok": res.bearing.is_bearing_ok
            },
            "shear": {
                "Vu_1way_x": round(res.shear.Vu_1way_x, 1),
                "phi_Vc_1way_x": round(res.shear.phi_Vc_1way_x, 1),
                "dcr_1way_x": round(res.shear.dcr_1way_x, 3),
                "Vu_1way_y": round(res.shear.Vu_1way_y, 1),
                "phi_Vc_1way_y": round(res.shear.phi_Vc_1way_y, 1),
                "dcr_1way_y": round(res.shear.dcr_1way_y, 3),
                "Vu_2way": round(res.shear.Vu_2way, 1),
                "phi_Vc_2way": round(res.shear.phi_Vc_2way, 1),
                "governing_eqn": res.shear.governing_eqn,
                "dcr_2way": round(res.shear.dcr_2way, 3),
                "is_2way_ok": res.shear.is_2way_ok
            },
            "flexure": {
                "Mux": round(res.flexure.Mux, 1),
                "phi_Mn_x": round(res.flexure.phi_Mn_x, 1),
                "As_req_x": round(res.flexure.As_req_x, 1),
                "As_prov_x": round(res.flexure.As_prov_x, 1),
                "dcr_x": round(res.flexure.dcr_flexure_x, 3),
                "Muy": round(res.flexure.Muy, 1),
                "phi_Mn_y": round(res.flexure.phi_Mn_y, 1),
                "As_req_y": round(res.flexure.As_req_y, 1),
                "As_prov_y": round(res.flexure.As_prov_y, 1),
                "dcr_y": round(res.flexure.dcr_flexure_y, 3)
            },
            "visualization": vis_2d,
            "messages": res.messages
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/combined-footing/design")
async def design_combined_footing(req: CombinedFootingRequest) -> Dict[str, Any]:
    """Design and check 2-Column Combined Footing."""
    try:
        inp = CombinedFootingInput(
            name=req.name,
            Bx=req.Bx,
            Ly=req.Ly,
            thickness_H=req.thickness_H,
            cover=req.cover,
            col1_cx=req.col1_cx,
            col1_cy=req.col1_cy,
            col1_dist_from_left=req.col1_dist_from_left,
            col1_P_serv=req.col1_P_serv,
            col1_Pu=req.col1_Pu,
            col2_cx=req.col2_cx,
            col2_cy=req.col2_cy,
            col2_dist_from_left=req.col2_dist_from_left,
            col2_P_serv=req.col2_P_serv,
            col2_Pu=req.col2_Pu,
            qa_allowable=req.qa_allowable,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            top_bar_diam=req.top_bar_diam,
            top_bar_count=req.top_bar_count,
            bot_bar_diam=req.bot_bar_diam,
            bot_bar_count=req.bot_bar_count
        )
        engine = RCCombinedFooting(inp)
        res = engine.solve()
        
        return {
            "status": "success",
            "name": res.name,
            "is_safe": res.is_safe,
            "max_dcr": round(res.max_dcr, 3),
            "bearing": {
                "q_left": round(res.q_left, 2),
                "q_right": round(res.q_right, 2),
                "q_max": round(res.q_max, 2),
                "dcr": round(res.dcr_bearing, 3),
                "is_ok": res.is_bearing_ok
            },
            "longitudinal_flexure": {
                "Mu_top_max": round(res.Mu_top_max, 1),
                "phi_Mn_top": round(res.phi_Mn_top, 1),
                "dcr_top": round(res.dcr_top_flexure, 3),
                "is_top_ok": res.is_top_ok,
                "Mu_bot_max": round(res.Mu_bot_max, 1),
                "phi_Mn_bot": round(res.phi_Mn_bot, 1),
                "dcr_bot": round(res.dcr_bot_flexure, 3),
                "is_bot_ok": res.is_bot_ok
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tie-beam/design")
async def design_tie_beam(req: UndergroundBeamRequest) -> Dict[str, Any]:
    """Design and check Tie / Underground Beam."""
    try:
        inp = UndergroundBeamInput(
            name=req.name,
            b=req.b,
            h=req.h,
            length=req.length,
            cover=req.cover,
            connected_col_Pu=req.connected_col_Pu,
            Pu_tension=req.Pu_tension,
            Mu=req.Mu,
            Vu=req.Vu,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            top_bars_count=req.top_bars_count,
            top_bar_diam=req.top_bar_diam,
            bot_bars_count=req.bot_bars_count,
            bot_bar_diam=req.bot_bar_diam,
            stirrup_diam=req.stirrup_diam,
            stirrup_spacing=req.stirrup_spacing
        )
        beam = RCUndergroundBeam(inp)
        res = beam.solve()
        
        return {
            "status": "success",
            "name": res.name,
            "is_safe": res.is_safe,
            "max_dcr": round(res.max_dcr, 3),
            "axial_tension": {
                "min_required_kN": round(res.min_required_axial_kN, 1),
                "phi_Pnt": round(res.phi_Pnt, 1),
                "dcr": round(res.dcr_axial, 3),
                "is_ok": res.is_axial_ok
            },
            "flexure": {
                "Mu": req.Mu,
                "phi_Mn": round(res.phi_Mn, 1),
                "dcr": round(res.dcr_flexure, 3),
                "is_ok": res.is_flexure_ok
            },
            "shear": {
                "Vu": req.Vu,
                "phi_Vc": round(res.phi_Vc, 1),
                "dcr": round(res.dcr_shear, 3),
                "is_ok": res.is_shear_ok
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retaining-wall/design")
async def design_retaining_wall(req: RetainingWallRequest) -> Dict[str, Any]:
    """Design and check RC Retaining Wall (Earth pressure, 3 Stability checks, Stem/Toe/Heel)."""
    try:
        wall_type = RetainingWallType.CANTILEVER_T
        if req.wall_type.lower() == "cantilever_l":
            wall_type = RetainingWallType.CANTILEVER_L
        elif req.wall_type.lower() == "gravity":
            wall_type = RetainingWallType.GRAVITY
        elif req.wall_type.lower() == "basement_wall":
            wall_type = RetainingWallType.BASEMENT_WALL
            
        inp = RetainingWallInput(
            name=req.name,
            wall_type=wall_type,
            geometry=RetainingWallGeometry(
                H_total=req.H_total,
                stem_t_top=req.stem_t_top,
                stem_t_bot=req.stem_t_bot,
                base_width_B=req.base_width_B,
                base_t=req.base_t,
                toe_length=req.toe_length,
                heel_length=req.heel_length,
                front_embedment_Df=req.front_embedment_Df
            ),
            soil=SoilProperties(
                unit_weight=req.soil_unit_weight,
                sat_unit_weight=req.sat_unit_weight,
                phi_deg=req.phi_deg,
                cohesion=req.cohesion,
                base_friction_coef=req.base_friction_coef,
                surcharge_q=req.surcharge_q,
                water_table_depth=req.water_table_depth,
                qa_allowable=req.qa_allowable
            ),
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            cover=req.cover,
            stem_main_bar_diam=req.stem_main_bar_diam,
            stem_main_bar_spacing=req.stem_main_bar_spacing,
            toe_main_bar_diam=req.toe_main_bar_diam,
            toe_main_bar_spacing=req.toe_main_bar_spacing,
            heel_main_bar_diam=req.heel_main_bar_diam,
            heel_main_bar_spacing=req.heel_main_bar_spacing
        )
        wall = RCRetainingWall(inp)
        res = wall.solve()
        
        # 2D Geometry profile for Canvas rendering
        H_m = req.H_total / 1000.0
        tb_m = req.base_t / 1000.0
        B_m = req.base_width_B / 1000.0
        toe_m = req.toe_length / 1000.0
        t_bot_m = req.stem_t_bot / 1000.0
        t_top_m = req.stem_t_top / 1000.0
        
        wall_polygon = [
            [0.0, 0.0],
            [B_m, 0.0],
            [B_m, tb_m],
            [toe_m + t_bot_m, tb_m],
            [toe_m + (t_bot_m - t_top_m) + t_top_m, H_m],
            [toe_m + (t_bot_m - t_top_m), H_m],
            [toe_m, tb_m],
            [0.0, tb_m]
        ]
        
        return {
            "status": "success",
            "name": res.name,
            "wall_type": res.wall_type,
            "is_safe": res.is_safe,
            "max_dcr": round(res.max_dcr, 3),
            "earth_pressure": {
                "Ka": round(res.earth_pressure.Ka, 4),
                "total_H": round(res.earth_pressure.total_H, 2),
                "total_Mo": round(res.earth_pressure.total_overturning_moment_Mo, 2)
            },
            "stability": {
                "Fs_overturning": round(res.stability.Fs_ot, 2),
                "is_overturning_ok": res.stability.is_overturning_ok,
                "Fs_sliding": round(res.stability.Fs_sl, 2),
                "is_sliding_ok": res.stability.is_sliding_ok,
                "q_max": round(res.stability.q_max, 2),
                "q_min": round(res.stability.q_min, 2),
                "qa_allowable": res.stability.qa_allowable,
                "eccentricity_m": round(res.stability.eccentricity_e, 3),
                "is_bearing_ok": res.stability.is_bearing_ok
            },
            "stem": {
                "Mu": round(res.stem.Mu, 2),
                "phi_Mn": round(res.stem.phi_Mn, 2),
                "dcr_flexure": round(res.stem.dcr_flexure, 3),
                "Vu": round(res.stem.Vu, 2),
                "phi_Vc": round(res.stem.phi_Vc, 2),
                "dcr_shear": round(res.stem.dcr_shear, 3),
                "As_req": round(res.stem.As_req, 1),
                "As_prov": round(res.stem.As_prov, 1)
            },
            "toe": {
                "Mu": round(res.toe.Mu, 2),
                "phi_Mn": round(res.toe.phi_Mn, 2),
                "dcr_flexure": round(res.toe.dcr_flexure, 3),
                "Vu": round(res.toe.Vu, 2),
                "phi_Vc": round(res.toe.phi_Vc, 2),
                "dcr_shear": round(res.toe.dcr_shear, 3)
            },
            "heel": {
                "Mu": round(res.heel.Mu, 2),
                "phi_Mn": round(res.heel.phi_Mn, 2),
                "dcr_flexure": round(res.heel.dcr_flexure, 3),
                "Vu": round(res.heel.Vu, 2),
                "phi_Vc": round(res.heel.phi_Vc, 2),
                "dcr_shear": round(res.heel.dcr_shear, 3)
            },
            "visualization": {
                "wall_polygon": wall_polygon
            },
            "messages": res.messages
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
