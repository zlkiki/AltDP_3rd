"""RC Design API Routes for AltDP_3rd."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from src.engine.db.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.beam import RCBeamInput, design_rc_beam
from src.engine.rc.column import RCColumnInput, design_rc_column

router = APIRouter(prefix="/api/rc", tags=["Reinforced Concrete"])


class RCBeamRequest(BaseModel):
    name: str = "B1"
    b: float = Field(default=400.0, description="Beam width (mm)", ge=50.0)
    h: float = Field(default=600.0, description="Total height (mm)", ge=50.0)
    cover: float = Field(default=50.0, description="Rebar cover (mm)", ge=20.0)
    As: float = Field(default=1935.0, description="Tension rebar area (mm2)", gt=0.0)
    Av: float = Field(default=142.6, description="Stirrup area (mm2)", ge=0.0)
    s: float = Field(default=200.0, description="Stirrup spacing (mm)", ge=50.0)
    Mu: float = Field(default=250.0, description="Design moment (kN*m)")
    Vu: float = Field(default=150.0, description="Design shear (kN)")
    fck: float = Field(default=24.0, description="Concrete strength (MPa)")
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)")


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
async def check_rc_beam(req: RCBeamRequest):
    """Evaluate RC beam capacity according to KDS 14 20 00."""
    try:
        inp = RCBeamInput(
            name=req.name,
            b=req.b,
            h=req.h,
            cover=req.cover,
            As=req.As,
            Av=req.Av,
            s=req.s,
            Mu=req.Mu,
            Vu=req.Vu,
            concrete=ConcreteMaterial(fck=req.fck),
            rebar=RebarMaterial(fy=req.fy)
        )
        res = design_rc_beam(inp)
        return {
            "success": True,
            "data": {
                "d": res.d,
                "a": res.a,
                "c": res.c,
                "phi_b": res.phi_b,
                "Mn": res.Mn,
                "phi_Mn": res.phi_Mn,
                "flexure_dcr": res.flexure_dcr,
                "Vc": res.Vc,
                "Vs": res.Vs,
                "phi_Vn": res.phi_Vn,
                "shear_dcr": res.shear_dcr,
                "rho": res.rho,
                "is_safe": res.is_safe,
                "summary": res.summary
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
        
        # Serialize P-M curve
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
