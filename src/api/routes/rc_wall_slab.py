"""RC Shear Wall and Slab/Punching Shear FastAPI Routes for AltDP_3rd."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.wall import RCShearWall, RCWallInput, BoundaryElementConfig
from src.engine.rc.slab import (
    RCOneWaySlab,
    OneWaySlabInput,
    SlabSupportCondition,
    RCTwoWaySlabDDM,
    TwoWaySlabDDMInput,
    PunchingShearEngine,
    PunchingShearInput,
    ColumnLocation
)
from src.api.schemas.rc_wall import RCWallCheckRequest
from src.api.schemas.rc_slab import (
    OneWaySlabCheckRequest,
    TwoWaySlabDDMRequest,
    PunchingShearCheckRequest
)

router = APIRouter(prefix="/api/rc", tags=["Reinforced Concrete Wall & Slab"])


@router.post("/wall/check")
async def check_rc_wall(req: RCWallCheckRequest) -> Dict[str, Any]:
    """Evaluate RC Shear Wall in-plane shear, rebar limits, and Special Boundary Element requirements."""
    try:
        left_be = None
        if req.left_boundary:
            left_be = BoundaryElementConfig(
                length=req.left_boundary.length,
                width=req.left_boundary.width,
                bar_diam=req.left_boundary.bar_diam,
                total_bars=req.left_boundary.total_bars,
                tie_diam=req.left_boundary.tie_diam,
                tie_spacing=req.left_boundary.tie_spacing,
                tie_legs_x=req.left_boundary.tie_legs_x,
                tie_legs_y=req.left_boundary.tie_legs_y
            )
            
        right_be = None
        if req.right_boundary:
            right_be = BoundaryElementConfig(
                length=req.right_boundary.length,
                width=req.right_boundary.width,
                bar_diam=req.right_boundary.bar_diam,
                total_bars=req.right_boundary.total_bars,
                tie_diam=req.right_boundary.tie_diam,
                tie_spacing=req.right_boundary.tie_spacing,
                tie_legs_x=req.right_boundary.tie_legs_x,
                tie_legs_y=req.right_boundary.tie_legs_y
            )
            
        inp = RCWallInput(
            name=req.name,
            lw=req.lw,
            tw=req.tw,
            hw=req.hw,
            cover=req.cover,
            vert_bar_diam=req.vert_bar_diam,
            vert_spacing=req.vert_spacing,
            vert_layers=req.vert_layers,
            horiz_bar_diam=req.horiz_bar_diam,
            horiz_spacing=req.horiz_spacing,
            horiz_layers=req.horiz_layers,
            left_boundary=left_be,
            right_boundary=right_be,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            rebar_shear=RebarMaterial(fy=req.fys),
            Pu=req.Pu,
            Vu=req.Vu,
            Mu=req.Mu,
            delta_u=req.delta_u
        )
        
        wall = RCShearWall(inp)
        res = wall.design_check()
        geom = wall.get_section_geometry_dict()
        
        return {
            "success": True,
            "data": {
                "wall_name": res.wall_name,
                "is_safe": res.is_safe,
                "dcr_governing": res.dcr_governing,
                "governing_mode": res.governing_mode,
                "messages": res.messages,
                "shear": {
                    "Vu": res.shear.Vu,
                    "phi_Vn": res.shear.phi_Vn,
                    "Vc": res.shear.Vc,
                    "Vs": res.shear.Vs,
                    "Vn": res.shear.Vn,
                    "Vn_max": res.shear.Vn_max,
                    "dcr": res.shear.dcr,
                    "alpha_c": res.shear.alpha_c,
                    "aspect_ratio": res.shear.aspect_ratio,
                    "d": res.shear.d,
                    "is_ok": res.shear.is_ok
                },
                "rebar_ratio": {
                    "rho_l": res.rebar_ratio.rho_l,
                    "rho_l_min": res.rebar_ratio.rho_l_min,
                    "rho_t": res.rebar_ratio.rho_t,
                    "rho_t_min": res.rebar_ratio.rho_t_min,
                    "max_spacing_limit": res.rebar_ratio.max_spacing_limit,
                    "is_double_curtain_required": res.rebar_ratio.is_double_curtain_required,
                    "is_double_curtain_provided": res.rebar_ratio.is_double_curtain_provided,
                    "is_vert_ok": res.rebar_ratio.is_vert_ok,
                    "is_horiz_ok": res.rebar_ratio.is_horiz_ok,
                    "is_spacing_ok": res.rebar_ratio.is_spacing_ok
                },
                "boundary_element": {
                    "is_sbe_required": res.boundary_element.is_sbe_required,
                    "trigger_method": res.boundary_element.trigger_method,
                    "c": res.boundary_element.c,
                    "c_limit_disp": res.boundary_element.c_limit_disp,
                    "sigma_max": res.boundary_element.sigma_max,
                    "sigma_limit": res.boundary_element.sigma_limit,
                    "required_be_length": res.boundary_element.required_be_length,
                    "provided_be_length": res.boundary_element.provided_be_length,
                    "required_Ash": res.boundary_element.required_Ash,
                    "provided_Ash": res.boundary_element.provided_Ash,
                    "is_length_ok": res.boundary_element.is_length_ok,
                    "is_ash_ok": res.boundary_element.is_ash_ok,
                    "is_ok": res.boundary_element.is_ok
                },
                "geometry_2d": geom
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slab/one-way/check")
async def check_one_way_slab(req: OneWaySlabCheckRequest) -> Dict[str, Any]:
    """Check 1-way slab minimum thickness for deflection, flexural capacity, and temperature rebar."""
    try:
        support_map = {
            "cantilever": SlabSupportCondition.CANTILEVER,
            "simply_supported": SlabSupportCondition.SIMPLY_SUPPORTED,
            "one_end_continuous": SlabSupportCondition.ONE_END_CONTINUOUS,
            "both_ends_continuous": SlabSupportCondition.BOTH_ENDS_CONTINUOUS
        }
        
        inp = OneWaySlabInput(
            name=req.name,
            span_L=req.span_L,
            thickness_h=req.thickness_h,
            cover=req.cover,
            support_type=support_map.get(req.support_type.value, SlabSupportCondition.BOTH_ENDS_CONTINUOUS),
            main_bar_diam=req.main_bar_diam,
            main_spacing=req.main_spacing,
            temp_bar_diam=req.temp_bar_diam,
            temp_spacing=req.temp_spacing,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            Mu=req.Mu,
            Vu=req.Vu
        )
        slab = RCOneWaySlab(inp)
        res = slab.design_check()
        
        return {
            "success": True,
            "data": {
                "name": res.name,
                "is_safe": res.is_safe,
                "h_provided": res.h_provided,
                "h_min": res.h_min,
                "is_thickness_ok": res.is_thickness_ok,
                "d": res.d,
                "As_main": res.As_main,
                "a": res.a,
                "phi_Mn": res.phi_Mn,
                "dcr_flexure": res.dcr_flexure,
                "is_flexure_ok": res.is_flexure_ok,
                "As_temp_req": res.As_temp_req,
                "As_temp_prov": res.As_temp_prov,
                "is_temp_ok": res.is_temp_ok,
                "phi_Vc": res.phi_Vc,
                "dcr_shear": res.dcr_shear,
                "is_shear_ok": res.is_shear_ok,
                "messages": res.messages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slab/two-way/ddm")
async def calculate_two_way_slab_ddm(req: TwoWaySlabDDMRequest) -> Dict[str, Any]:
    """Calculate 2-way slab Direct Design Method (DDM) total static moment and strip distribution."""
    try:
        inp = TwoWaySlabDDMInput(
            name=req.name,
            l1=req.l1,
            l2=req.l2,
            c1=req.c1,
            c2=req.c2,
            thickness_h=req.thickness_h,
            qu=req.qu,
            is_interior_span=req.is_interior_span,
            has_edge_beam=req.has_edge_beam,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy)
        )
        ddm = RCTwoWaySlabDDM(inp)
        res = ddm.calculate_ddm_moments()
        
        return {
            "success": True,
            "data": {
                "name": req.name,
                "M0": res.M0,
                "ln": res.ln,
                "longitudinal_moments": {
                    "neg_interior_Mu": res.neg_interior_Mu,
                    "pos_Mu": res.pos_Mu,
                    "neg_exterior_Mu": res.neg_exterior_Mu
                },
                "column_strip": {
                    "neg_interior": res.col_strip_neg_interior,
                    "pos": res.col_strip_pos,
                    "neg_exterior": res.col_strip_neg_exterior
                },
                "middle_strip": {
                    "neg_interior": res.mid_strip_neg_interior,
                    "pos": res.mid_strip_pos,
                    "neg_exterior": res.mid_strip_neg_exterior
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slab/punching")
async def check_punching_shear(req: PunchingShearCheckRequest) -> Dict[str, Any]:
    """Evaluate 2-way punching shear capacity (3 KDS formulas) and unbalanced moment stress."""
    try:
        loc_map = {
            "interior": ColumnLocation.INTERIOR,
            "edge": ColumnLocation.EDGE,
            "corner": ColumnLocation.CORNER
        }
        inp = PunchingShearInput(
            column_name=req.column_name,
            location=loc_map.get(req.location.value, ColumnLocation.INTERIOR),
            c1=req.c1,
            c2=req.c2,
            slab_h=req.slab_h,
            eff_depth_d=req.eff_depth_d,
            Vu=req.Vu,
            Munb=req.Munb,
            concrete=ConcreteMaterial(fck=req.fck)
        )
        engine = PunchingShearEngine(inp)
        res = engine.check_punching_shear()
        
        return {
            "success": True,
            "data": {
                "column_name": res.column_name,
                "location": res.location.value,
                "b0": res.b0,
                "Ac": res.Ac,
                "beta_ratio": res.beta_ratio,
                "alpha_s": res.alpha_s,
                "capacity": {
                    "vc1": res.vc1,
                    "vc2": res.vc2,
                    "vc3": res.vc3,
                    "vc_nominal": res.vc_nominal,
                    "phi_vc": res.phi_vc
                },
                "stress": {
                    "gamma_v": res.gamma_v,
                    "gamma_f": res.gamma_f,
                    "vu_direct": res.vu_direct,
                    "vu_moment": res.vu_moment,
                    "vu_total": res.vu_total
                },
                "dcr": res.dcr,
                "is_safe": res.is_safe,
                "perimeter_points": res.perimeter_points
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
