"""Steel Design API Routes for AltDP_3rd (KDS 14 31 10).

Provides REST endpoints for Beam, Column/Beam-Column, Brace, and Web Opening design.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from src.engine.materials import SteelMaterial
from src.engine.steel.beam import SteelBeamInput, design_steel_beam
from src.engine.steel.column import SteelColumnInput, design_steel_column
from src.engine.steel.brace import SteelBraceInput, design_steel_brace, BraceConnection
from src.engine.steel.web_opening import WebOpeningInput, check_web_opening, OpeningShape

router = APIRouter(prefix="/api/steel", tags=["Structural Steel"])


# -------------------------------------------------------------
# 1. Steel Beam Request & Endpoint
# -------------------------------------------------------------
class SteelBeamRequest(BaseModel):
    name: str = "SB1"
    section_type: str = "H"
    H: float = Field(default=400.0, description="Height (mm)", ge=50.0)
    B: float = Field(default=200.0, description="Width (mm)", ge=50.0)
    tw: float = Field(default=8.0, description="Web thickness (mm)", ge=2.0)
    tf: float = Field(default=13.0, description="Flange thickness (mm)", ge=2.0)
    D: float = Field(default=0.0, description="Pipe diameter (mm)")
    t_wall: float = Field(default=0.0, description="Pipe/Box wall thickness (mm)")
    L: float = Field(default=6000.0, description="Span length (mm)", ge=100.0)
    Lb: float = Field(default=3000.0, description="Unbraced length (mm)", ge=100.0)
    Cb: float = Field(default=1.0, description="Moment gradient factor", ge=1.0)
    MA: float = Field(default=0.0, description="Quarter moment (kN*m)")
    MB: float = Field(default=0.0, description="Midspan moment (kN*m)")
    MC: float = Field(default=0.0, description="3/4 moment (kN*m)")
    Mux: float = Field(default=180.0, description="Major axis moment (kN*m)")
    Muy: float = Field(default=0.0, description="Minor axis moment (kN*m)")
    Vu: float = Field(default=120.0, description="Shear force (kN)")
    service_w: float = Field(default=15.0, description="Service load (kN/m)")
    Fy: float = Field(default=355.0, description="Yield strength (MPa)")
    Fu: float = Field(default=490.0, description="Tensile strength (MPa)")


@router.post("/beam/check")
@router.post("/beam/design")
async def check_beam_api(req: SteelBeamRequest):
    """Evaluate Steel Beam capacity according to KDS 14 31 10."""
    try:
        inp = SteelBeamInput(
            name=req.name,
            section_type=req.section_type,
            H=req.H,
            B=req.B,
            tw=req.tw,
            tf=req.tf,
            D=req.D,
            t_wall=req.t_wall,
            L=req.L,
            Lb=req.Lb,
            Cb=req.Cb,
            MA=req.MA,
            MB=req.MB,
            MC=req.MC,
            Mux=req.Mux,
            Muy=req.Muy,
            Vu=req.Vu,
            service_w=req.service_w,
            material=SteelMaterial(name="Steel", Fy=req.Fy, Fu=req.Fu)
        )
        res = design_steel_beam(inp)
        return {
            "success": True,
            "data": {
                "classification": res.compactness.overall_classification.value,
                "is_flange_compact": res.compactness.flange.is_compact if res.compactness.flange else True,
                "is_web_compact": res.compactness.web.is_compact if res.compactness.web else True,
                "Mp_x": res.Mp_x,
                "Lp": res.Lp,
                "Lr": res.Lr,
                "Mn_x": res.Mn_x,
                "phi_Mn_x": res.phi_Mn_x,
                "flexure_dcr_x": res.flexure_dcr_x,
                "phi_Mn_y": res.phi_Mn_y,
                "flexure_dcr_y": res.flexure_dcr_y,
                "total_flexure_dcr": res.total_flexure_dcr,
                "Cv": res.Cv,
                "Vn": res.Vn,
                "phi_Vn": res.phi_Vn,
                "shear_dcr": res.shear_dcr,
                "delta_act": res.delta_act,
                "delta_allow": res.delta_allow,
                "deflection_dcr": res.deflection_dcr,
                "max_dcr": res.max_dcr,
                "is_safe": res.is_safe,
                "summary": res.summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------------------------------------
# 2. Steel Column Request & Endpoint
# -------------------------------------------------------------
class SteelColumnRequest(BaseModel):
    name: str = "SC1"
    section_type: str = "H"
    H: float = Field(default=350.0, ge=50.0)
    B: float = Field(default=350.0, ge=50.0)
    tw: float = Field(default=12.0, ge=2.0)
    tf: float = Field(default=19.0, ge=2.0)
    D: float = Field(default=0.0)
    t_wall: float = Field(default=0.0)
    Lx: float = Field(default=4000.0, ge=100.0)
    Ly: float = Field(default=4000.0, ge=100.0)
    Kx: float = Field(default=1.0, ge=0.1)
    Ky: float = Field(default=1.0, ge=0.1)
    Lb: float = Field(default=4000.0, ge=100.0)
    Cb: float = Field(default=1.0, ge=1.0)
    Pu: float = Field(default=1200.0, description="Axial compression (kN)")
    Mux: float = Field(default=150.0, description="Major moment (kN*m)")
    Muy: float = Field(default=50.0, description="Minor moment (kN*m)")
    Fy: float = Field(default=355.0)
    Fu: float = Field(default=490.0)


@router.post("/column/design")
async def check_column_api(req: SteelColumnRequest):
    """Evaluate Steel Column / Beam-Column P-M interaction (KDS 14 31 10)."""
    try:
        inp = SteelColumnInput(
            name=req.name,
            section_type=req.section_type,
            H=req.H,
            B=req.B,
            tw=req.tw,
            tf=req.tf,
            D=req.D,
            t_wall=req.t_wall,
            Lx=req.Lx,
            Ly=req.Ly,
            Kx=req.Kx,
            Ky=req.Ky,
            Lb=req.Lb,
            Cb=req.Cb,
            Pu=req.Pu,
            Mux=req.Mux,
            Muy=req.Muy,
            material=SteelMaterial(name="Steel", Fy=req.Fy, Fu=req.Fu)
        )
        res = design_steel_column(inp)
        return {
            "success": True,
            "data": {
                "Ag": res.Ag,
                "Ae": res.Ae,
                "rx": res.rx,
                "ry": res.ry,
                "max_slenderness": res.max_slenderness,
                "is_slenderness_ok": res.is_slenderness_ok,
                "Fe": res.Fe,
                "Fcr": res.Fcr,
                "Pn": res.Pn,
                "phi_Pn": res.phi_Pn,
                "axial_dcr": res.axial_dcr,
                "phi_Mn_x": res.phi_Mn_x,
                "phi_Mn_y": res.phi_Mn_y,
                "flexure_dcr_x": res.flexure_dcr_x,
                "flexure_dcr_y": res.flexure_dcr_y,
                "pm_formula": res.pm_formula,
                "pm_dcr": res.pm_dcr,
                "max_dcr": res.max_dcr,
                "is_safe": res.is_safe,
                "summary": res.summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------------------------------------
# 3. Steel Brace Request & Endpoint
# -------------------------------------------------------------
class SteelBraceRequest(BaseModel):
    name: str = "BR1"
    section_type: str = "ANGLE"
    B: float = Field(default=100.0, ge=20.0)
    H: float = Field(default=100.0, ge=20.0)
    t: float = Field(default=10.0, ge=2.0)
    tw: float = Field(default=8.0)
    tf: float = Field(default=10.0)
    L: float = Field(default=4000.0, ge=100.0)
    K: float = Field(default=1.0, ge=0.1)
    connection_type: str = "BOLTED"
    bolt_hole_diameter: float = Field(default=22.0)
    num_bolt_holes: int = Field(default=2)
    connection_length_L: float = Field(default=150.0)
    eccentricity_x_bar: float = Field(default=28.2)
    Tu: float = Field(default=250.0, description="Tensile load (kN)")
    Pu: float = Field(default=150.0, description="Compressive load (kN)")
    Fy: float = Field(default=355.0)
    Fu: float = Field(default=490.0)


@router.post("/brace/design")
async def check_brace_api(req: SteelBraceRequest):
    """Evaluate Steel Brace tension yielding, rupture, and compression buckling."""
    try:
        conn = BraceConnection.BOLTED if req.connection_type.upper() == "BOLTED" else BraceConnection.WELDED
        inp = SteelBraceInput(
            name=req.name,
            section_type=req.section_type,
            B=req.B,
            H=req.H,
            t=req.t,
            tw=req.tw,
            tf=req.tf,
            L=req.L,
            K=req.K,
            connection_type=conn,
            bolt_hole_diameter=req.bolt_hole_diameter,
            num_bolt_holes=req.num_bolt_holes,
            connection_length_L=req.connection_length_L,
            eccentricity_x_bar=req.eccentricity_x_bar,
            Tu=req.Tu,
            Pu=req.Pu,
            material=SteelMaterial(name="Steel", Fy=req.Fy, Fu=req.Fu)
        )
        res = design_steel_brace(inp)
        return {
            "success": True,
            "data": {
                "Ag": res.Ag,
                "An": res.An,
                "Ae": res.Ae,
                "U": res.U,
                "r_min": res.r_min,
                "slenderness": res.slenderness,
                "is_slenderness_tension_ok": res.is_slenderness_tension_ok,
                "is_slenderness_comp_ok": res.is_slenderness_comp_ok,
                "phi_Pn_yield": res.phi_Pn_yield,
                "yield_dcr": res.yield_dcr,
                "phi_Pn_rupture": res.phi_Pn_rupture,
                "rupture_dcr": res.rupture_dcr,
                "tension_dcr": res.tension_dcr,
                "phi_Pn_comp": res.phi_Pn_comp,
                "comp_dcr": res.comp_dcr,
                "max_dcr": res.max_dcr,
                "is_safe": res.is_safe,
                "summary": res.summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------------------------------------
# 4. Web Opening Request & Endpoint
# -------------------------------------------------------------
class WebOpeningRequest(BaseModel):
    name: str = "WO1"
    shape: str = "RECTANGULAR"
    H: float = Field(default=500.0, ge=100.0)
    B: float = Field(default=200.0, ge=50.0)
    tw: float = Field(default=9.0, ge=2.0)
    tf: float = Field(default=14.0, ge=2.0)
    ao: float = Field(default=300.0, ge=10.0)
    ho: float = Field(default=200.0, ge=10.0)
    e: float = Field(default=0.0)
    has_reinforcement: bool = False
    br: float = Field(default=80.0)
    tr: float = Field(default=10.0)
    Mu: float = Field(default=200.0)
    Vu: float = Field(default=100.0)
    Fy: float = Field(default=355.0)
    Fu: float = Field(default=490.0)


@router.post("/web-opening/check")
async def check_web_opening_api(req: WebOpeningRequest):
    """Evaluate beam web opening shear, flexure, and Vierendeel action."""
    try:
        shape = OpeningShape.RECTANGULAR if req.shape.upper() == "RECTANGULAR" else OpeningShape.CIRCULAR
        inp = WebOpeningInput(
            name=req.name,
            shape=shape,
            H=req.H,
            B=req.B,
            tw=req.tw,
            tf=req.tf,
            ao=req.ao,
            ho=req.ho,
            e=req.e,
            has_reinforcement=req.has_reinforcement,
            br=req.br,
            tr=req.tr,
            Mu=req.Mu,
            Vu=req.Vu,
            material=SteelMaterial(name="Steel", Fy=req.Fy, Fu=req.Fu)
        )
        res = check_web_opening(inp)
        return {
            "success": True,
            "data": {
                "s_top": res.s_top,
                "s_bot": res.s_bot,
                "Vp_top": res.Vp_top,
                "Vp_bot": res.Vp_bot,
                "phi_Vn": res.phi_Vn,
                "shear_dcr": res.shear_dcr,
                "phi_Mn": res.phi_Mn,
                "flexure_dcr": res.flexure_dcr,
                "vierendeel_dcr": res.vierendeel_dcr,
                "max_dcr": res.max_dcr,
                "is_safe": res.is_safe,
                "summary": res.summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
