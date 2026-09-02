"""RC Design API Routes for AltDP_3rd (Beams, Columns, Auto-Design)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from src.engine.db.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.beam import RCBeamInput, design_rc_beam, RCBeamResult
from src.engine.rc.column import RCColumnInput, design_rc_column
from src.engine.rc.rebar_layout import (
    auto_design_beam_rebar,
    create_rebar_arrangement,
    BeamRebarArrangement
)
from src.api.schemas.rc_beam import RCBeamCheckRequest, RCBeamAutoDesignRequest

router = APIRouter(prefix="/api/rc", tags=["Reinforced Concrete"])


class RCColumnRequest(BaseModel):
    name: str = "C1"
    b: float = Field(default=600.0, description="Column width (mm)", ge=100.0)
    h: float = Field(default=600.0, description="Column depth (mm)", ge=100.0)
    cover: float = Field(default=60.0, description="Rebar cover (mm)", ge=20.0)
    bar_diam: float = Field(default=25.0, description="Bar diameter (mm)", ge=10.0)
    total_bars: int = Field(default=12, description="Total longitudinal bars", ge=4)
    Pu: float = Field(default=2500.0, description="Design axial force (kN)")
    Mu: float = Field(default=350.0, description="Design moment (kN*m)")
    Vu: float = Field(default=120.0, description="Design shear (kN)")
    fck: float = Field(default=30.0, description="Concrete strength (MPa)")
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)")


@router.post("/beam/check")
async def check_rc_beam(req: RCBeamCheckRequest):
    """Evaluate RC beam structural capacity, torsion, deflection, and crack width according to KDS 14 20 00."""
    try:
        stirrup_mat = RebarMaterial(fy=req.fyt) if req.fyt is not None else None
        inp = RCBeamInput(
            name=req.name,
            b=req.b,
            h=req.h,
            cover=req.cover,
            cover_prime=req.cover_prime,
            side_cover=req.side_cover,
            As=req.As,
            As_prime=req.As_prime,
            Av=req.Av,
            s=req.s,
            Mu=req.Mu,
            Vu=req.Vu,
            Tu=req.Tu,
            Ma=req.Ma,
            span_length=req.span_length,
            num_tension_bars=req.num_tension_bars,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy),
            rebar_stirrup=stirrup_mat
        )
        res = design_rc_beam(inp)
        
        # Determine 2D arrangement preview
        rebar_layout_info = create_rebar_arrangement(
            b=req.b,
            h=req.h,
            bar_size="D22",
            num_bars=req.num_tension_bars,
            cover=req.cover - 10.0
        )
        
        return {
            "success": True,
            "data": {
                # Flexure
                "d": res.d,
                "d_prime": res.d_prime,
                "a": res.a,
                "c": res.c,
                "fs_prime": res.fs_prime,
                "is_top_yielding": res.is_top_yielding,
                "et": res.et,
                "phi_b": res.phi_b,
                "Mn": res.Mn,
                "phi_Mn": res.phi_Mn,
                "flexure_dcr": res.flexure_dcr,
                "rho": res.rho,
                "rho_min": res.rho_min,
                "rho_max": res.rho_max,
                
                # Shear
                "Vc": res.Vc,
                "Vs": res.Vs,
                "Vs_max": res.Vs_max,
                "Vn": res.Vn,
                "phi_v": res.phi_v,
                "phi_Vn": res.phi_Vn,
                "shear_dcr": res.shear_dcr,
                "s_max": res.s_max,
                "Av_min": res.Av_min,
                
                # Torsion
                "Tcr": res.Tcr,
                "Tth": res.Tth,
                "is_torsion_ignored": res.is_torsion_ignored,
                "At_over_s_req": res.At_over_s_req,
                "Al_req": res.Al_req,
                "Al_min": res.Al_min,
                "phi_Tn": res.phi_Tn,
                "torsion_dcr": res.torsion_dcr,
                "combined_stress": res.combined_stress,
                "combined_limit": res.combined_limit,
                "combined_dcr": res.combined_dcr,
                
                # Serviceability
                "Ig": res.Ig,
                "Mcr": res.Mcr,
                "Icr": res.Icr,
                "Ie": res.Ie,
                "delta_elastic": res.delta_elastic,
                "lambda_delta": res.lambda_delta,
                "delta_long": res.delta_long,
                "delta_total": res.delta_total,
                "delta_allowable": res.delta_allowable,
                "deflection_dcr": res.deflection_dcr,
                "crack_width": res.crack_width,
                "crack_dcr": res.crack_dcr,
                
                # Safety
                "is_safe": res.is_safe,
                "summary": res.summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/beam/auto-design")
async def auto_design_beam(req: RCBeamAutoDesignRequest):
    """Automatically calculate optimal rebar sizing and 1-layer / 2-layer arrangement."""
    try:
        result = auto_design_beam_rebar(
            b=req.b,
            h=req.h,
            As_req=req.As_req,
            cover=req.cover,
            stirrup_size=req.stirrup_size,
            max_aggregate=req.max_aggregate,
            preferred_sizes=req.preferred_sizes
        )
        
        selected_data = None
        if result.selected_arrangement:
            arr = result.selected_arrangement
            selected_data = {
                "bar_size": arr.bar_size,
                "total_bars": arr.total_bars,
                "num_layers": arr.num_layers,
                "total_area": arr.total_area,
                "effective_d": arr.effective_d,
                "centroid_from_bottom": arr.centroid_from_bottom,
                "layers": [
                    {
                        "layer_index": lyr.layer_index,
                        "num_bars": lyr.num_bars,
                        "db": lyr.db,
                        "y_centroid": lyr.y_centroid,
                        "x_coords": lyr.x_coords,
                        "clear_spacing": lyr.clear_spacing
                    }
                    for lyr in arr.layers
                ]
            }
            
        candidates_data = [
            {
                "bar_size": c.bar_size,
                "total_bars": c.total_bars,
                "num_layers": c.num_layers,
                "total_area": c.total_area,
                "effective_d": c.effective_d,
                "is_valid": c.is_valid
            }
            for c in result.all_candidates
        ]
        
        return {
            "success": True,
            "data": {
                "As_req": result.As_req,
                "selected": selected_data,
                "candidates": candidates_data,
                "stirrup": {
                    "size": result.stirrup_size,
                    "spacing": result.stirrup_spacing,
                    "legs": result.stirrup_legs,
                    "area": result.stirrup_area
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from src.api.schemas.rc_column import RCColumnDesignRequest, PMCurveRequest
from src.engine.rc.column import (
    RCColumnInput,
    design_rc_column,
    create_standard_column_fiber_section,
    RCColumnDesignResult
)
from src.engine.solver.pm_diagram import PMDiagramSolver
import math


@router.post("/column/design")
async def design_column_comprehensive(req: RCColumnDesignRequest):
    """Comprehensive RC Column design under slenderness, biaxial bending, shear, and tie detailing."""
    try:
        inp = RCColumnInput(
            name=req.name,
            b=req.b,
            h=req.h,
            cover=req.cover,
            bar_diam=req.bar_diam,
            total_bars=req.total_bars,
            tie_diam=req.tie_diam,
            tie_spacing=req.tie_spacing,
            tie_legs_x=req.tie_legs_x,
            tie_legs_y=req.tie_legs_y,
            is_spiral=req.is_spiral,
            Lu=req.Lu,
            k=req.k,
            is_braced=req.is_braced,
            M1x=req.M1x,
            M2x=req.M2x,
            M1y=req.M1y,
            M2y=req.M2y,
            Pu=req.Pu,
            Mux=req.Mux,
            Muy=req.Muy,
            Vux=req.Vux,
            Vuy=req.Vuy,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy)
        )
        res = design_rc_column(inp)
        
        return {
            "success": True,
            "data": {
                "name": res.name,
                "Ag": res.Ag,
                "Ast": res.Ast,
                "rho_g": res.rho_g,
                "is_rho_ok": res.is_rho_ok,
                "Po": res.Po,
                "Pn_max": res.Pn_max,
                "phi_Pn_max": res.phi_Pn_max,
                "phi_Pt": res.phi_Pt,
                "slenderness": {
                    "is_slender_x": res.slenderness.is_slender_x,
                    "is_slender_y": res.slenderness.is_slender_y,
                    "slenderness_x": res.slenderness.slenderness_x,
                    "slenderness_y": res.slenderness.slenderness_y,
                    "slenderness_limit_x": res.slenderness.slenderness_limit_x,
                    "slenderness_limit_y": res.slenderness.slenderness_limit_y,
                    "delta_ns_x": res.slenderness.delta_ns_x,
                    "delta_ns_y": res.slenderness.delta_ns_y,
                    "Pc_x": res.slenderness.Pc_x,
                    "Pc_y": res.slenderness.Pc_y,
                    "Mc_x": res.slenderness.Mc_x,
                    "Mc_y": res.slenderness.Mc_y,
                    "min_eccentricity_x": res.slenderness.min_eccentricity_x,
                    "min_eccentricity_y": res.slenderness.min_eccentricity_y,
                },
                "design_forces": {
                    "Pu": res.design_Pu,
                    "Mux": res.design_Mux,
                    "Muy": res.design_Muy,
                    "capacity_Mu": res.capacity_Mu,
                    "pm_dcr": res.pm_dcr,
                    "is_pm_safe": res.is_pm_safe
                },
                "shear": {
                    "Vux": res.Vux,
                    "phi_Vnx": res.phi_Vnx,
                    "shear_dcr_x": res.shear_dcr_x,
                    "Vuy": res.Vuy,
                    "phi_Vny": res.phi_Vny,
                    "shear_dcr_y": res.shear_dcr_y,
                    "is_shear_safe": res.is_shear_safe
                },
                "tie_check": {
                    "spacing": res.tie_spacing,
                    "spacing_max": res.tie_spacing_max,
                    "is_tie_ok": res.is_tie_ok
                },
                "dcr_max": res.dcr_max,
                "is_safe": res.is_safe,
                "summary": res.summary,
                "pm_curve_x": res.pm_curve_x,
                "pm_curve_y": res.pm_curve_y
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/column/pm-curve")
async def generate_column_pm_curve(req: PMCurveRequest):
    """Generate 2D/3D P-M interaction diagram points for given cross-section and angle."""
    try:
        inp = RCColumnInput(
            b=req.b,
            h=req.h,
            cover=req.cover,
            bar_diam=req.bar_diam,
            total_bars=req.total_bars,
            is_spiral=req.is_spiral,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy)
        )
        sec = create_standard_column_fiber_section(inp, nx=20, ny=20)
        theta_rad = math.radians(req.theta_deg)
        diag = PMDiagramSolver.generate_2d_diagram(
            sec=sec,
            theta=theta_rad,
            num_points=req.num_points,
            is_spiral=req.is_spiral
        )
        
        points = [
            {
                "Pn": round(p.Pn, 2),
                "Mn": round(p.Mn, 2),
                "phi_Pn": round(p.phi_Pn, 2),
                "phi_Mn": round(p.phi_Mn, 2),
                "c": round(p.c, 1),
                "et": round(p.et, 5),
                "phi": round(p.phi, 3)
            }
            for p in diag.points
        ]
        
        return {
            "success": True,
            "data": {
                "theta_deg": req.theta_deg,
                "Po": round(diag.Po, 2),
                "Pn_max": round(diag.Pn_max, 2),
                "phi_Pn_max": round(diag.phi_Pn_max, 2),
                "phi_Pt": round(diag.phi_Pt, 2),
                "points": points
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/column/check")
async def check_rc_column(req: RCColumnRequest):
    """Generate P-M diagram and evaluate RC column safety (Legacy/Compact Endpoint)."""
    try:
        inp = RCColumnInput(
            name=req.name,
            b=req.b,
            h=req.h,
            cover=req.cover,
            bar_diam=req.bar_diam,
            total_bars=req.total_bars,
            Pu=req.Pu,
            Mux=req.Mu,
            Vuy=req.Vu,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy)
        )
        res = design_rc_column(inp)
        
        return {
            "success": True,
            "data": {
                "Ag": res.Ag,
                "Ast": res.Ast,
                "rho_g": res.rho_g,
                "Pn_max": res.Pn_max,
                "phi_Pn_max": res.phi_Pn_max,
                "capacity_Mu": res.capacity_Mu,
                "dcr": res.pm_dcr,
                "is_safe": res.is_safe,
                "summary": res.summary,
                "pm_curve": res.pm_curve_x
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

