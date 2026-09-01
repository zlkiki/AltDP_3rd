"""Steel Design API Routes for AltDP_3rd."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.engine.db.materials import SteelMaterial
from src.engine.steel.beam import SteelBeamInput, design_steel_beam

router = APIRouter(prefix="/api/steel", tags=["Structural Steel"])


class SteelBeamRequest(BaseModel):
    name: str = "SB1"
    H: float = Field(default=400.0, description="Height (mm)", ge=50.0)
    B: float = Field(default=200.0, description="Width (mm)", ge=50.0)
    tw: float = Field(default=8.0, description="Web thickness (mm)", ge=2.0)
    tf: float = Field(default=13.0, description="Flange thickness (mm)", ge=2.0)
    Lb: float = Field(default=3000.0, description="Unbraced length (mm)", ge=100.0)
    Cb: float = Field(default=1.0, description="Moment gradient factor", ge=1.0)
    Mu: float = Field(default=180.0, description="Design moment (kN*m)")
    Vu: float = Field(default=120.0, description="Design shear (kN)")
    Fy: float = Field(default=275.0, description="Yield strength (MPa)")


@router.post("/beam/check")
async def check_steel_beam(req: SteelBeamRequest):
    """Evaluate Steel H-beam capacity according to KDS 14 31 10."""
    try:
        inp = SteelBeamInput(
            name=req.name,
            H=req.H,
            B=req.B,
            tw=req.tw,
            tf=req.tf,
            Lb=req.Lb,
            Cb=req.Cb,
            Mu=req.Mu,
            Vu=req.Vu,
            material=SteelMaterial(name="Steel", Fy=req.Fy)
        )
        res = design_steel_beam(inp)
        return {
            "success": True,
            "data": {
                "is_flange_compact": res.is_flange_compact,
                "is_web_compact": res.is_web_compact,
                "Mp": res.Mp,
                "Lp": res.Lp,
                "Lr": res.Lr,
                "Mn": res.Mn,
                "phi_Mn": res.phi_Mn,
                "flexure_dcr": res.flexure_dcr,
                "Vn": res.Vn,
                "phi_Vn": res.phi_Vn,
                "shear_dcr": res.shear_dcr,
                "is_safe": res.is_safe,
                "summary": res.summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
