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


@router.post("/column/check")
async def check_rc_column(req: RCColumnRequest):
    """Generate P-M diagram and evaluate RC column safety according to KDS 14 20 00."""
    try:
        inp = RCColumnInput(
            name=req.name,
            b=req.b,
            h=req.h,
            cover=req.cover,
            bar_diam=req.bar_diam,
            total_bars=req.total_bars,
            Pu=req.Pu,
            Mu=req.Mu,
            Vu=req.Vu,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy)
        )
        res = design_rc_column(inp)
        
        curve_data = [
            {
                "Pn": pt.Pn,
                "Mn": pt.Mn,
                "phi_Pn": pt.phi_Pn,
                "phi_Mn": pt.phi_Mn,
                "c": pt.c
            }
            for pt in res.pm_curve
        ]
        
        return {
            "success": True,
            "data": {
                "Ag": res.Ag,
                "Ast": res.Ast,
                "rho_g": res.rho_g,
                "Pn_max": res.Pn_max,
                "phi_Pn_max": res.phi_Pn_max,
                "capacity_Mu": res.capacity_Mu,
                "dcr": res.dcr,
                "is_safe": res.is_safe,
                "summary": res.summary,
                "pm_curve": curve_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
