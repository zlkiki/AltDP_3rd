"""FastAPI Routes for International Design Codes, Unit Conversions, and PBD Hinges.

Provides endpoints for:
- Real-time ultra-precision unit conversion across SI, MKS, and US Imperial systems
- Global design code verification (Eurocode 2/3, US ACI/AISC, Indian IS 456/800)
- Performance-Based Design (PBD) plastic hinge curve and acceptance evaluation
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.engine.international.units import (
    UnitSystem,
    UnitType,
    convert_unit,
    convert_dict_units,
)
from src.engine.international.eurocode import (
    check_ec2_rc_beam,
    check_ec3_steel_beam,
)
from src.engine.international.us_code import (
    check_aci318_rc_beam,
    check_aisc360_steel_beam,
)
from src.engine.international.is_code import (
    check_is456_rc_beam,
    check_is800_steel_beam,
)
from src.engine.pbd import (
    create_rc_beam_hinge,
    create_steel_beam_hinge,
    calculate_rc_column_hinge_parameters,
    calculate_steel_column_hinge_parameters,
    calculate_steel_brace_hinge_parameters,
    create_hinge_performance_summary,
    MemberType,
)

router = APIRouter(prefix="/api/v1/intl", tags=["International Codes & PBD"])


# -------------------------------------------------------------
# DTOs
# -------------------------------------------------------------
class UnitConvertRequest(BaseModel):
    """Batch or single unit conversion request."""
    values: Dict[str, float] = Field(..., description="Key-value mapping of numeric parameters")
    unit_types: Dict[str, str] = Field(..., description="Mapping of parameter keys to UnitType names")
    from_system: str = Field(..., description="Source unit system: SI, MKS, or US_IMPERIAL")
    to_system: str = Field(..., description="Target unit system: SI, MKS, or US_IMPERIAL")


class SingleUnitConvertRequest(BaseModel):
    """Single scalar unit conversion."""
    value: float
    unit_type: str
    from_system: str
    to_system: str


class DesignCheckRequest(BaseModel):
    """Global design code check request."""
    code: str = Field(..., description="Target design code: EUROCODE, ACI, AISC, or IS")
    member_type: str = Field(..., description="Member type: RC_BEAM, STEEL_BEAM, etc.")
    parameters: Dict[str, Any] = Field(..., description="Design input parameters")


class PBDHingeRequest(BaseModel):
    """PBD plastic hinge generation request."""
    member_id: int = 1
    member_type: str = Field("RC_BEAM", description="Member type enum string")
    parameters: Dict[str, Any]
    demand_theta: Optional[float] = None


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@router.post("/convert-units")
def convert_units_endpoint(req: UnitConvertRequest):
    """Batch convert numeric values between engineering unit systems."""
    try:
        from_sys = UnitSystem(req.from_system.upper())
        to_sys = UnitSystem(req.to_system.upper())
        type_mapping = {k: UnitType(v.upper()) for k, v in req.unit_types.items()}
        converted = convert_dict_units(req.values, type_mapping, from_sys, to_sys)
        return {
            "status": "success",
            "from_system": from_sys.value,
            "to_system": to_sys.value,
            "converted_values": converted,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/convert-single")
def convert_single_endpoint(req: SingleUnitConvertRequest):
    """Convert a single scalar value across unit systems."""
    try:
        converted = convert_unit(
            req.value,
            req.unit_type,
            req.from_system,
            req.to_system,
        )
        return {
            "status": "success",
            "original_value": req.value,
            "converted_value": converted,
            "unit_type": req.unit_type.upper(),
            "from_system": req.from_system.upper(),
            "to_system": req.to_system.upper(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/design-check")
def design_check_endpoint(req: DesignCheckRequest):
    """Evaluate structural member resistance under Eurocode, US, or Indian standards."""
    code = req.code.upper()
    mtype = req.member_type.upper()
    p = req.parameters

    try:
        if code in ("EUROCODE", "EC", "EC2", "EC3"):
            if "RC" in mtype or "CONCRETE" in mtype:
                res = check_ec2_rc_beam(
                    b=float(p.get("b", 300.0)),
                    h=float(p.get("h", 500.0)),
                    d=float(p.get("d", 450.0)),
                    fck=float(p.get("fck", 25.0)),
                    fyk=float(p.get("fyk", 400.0)),
                    As=float(p.get("As", 1200.0)),
                    As_prime=float(p.get("As_prime", 0.0)),
                    Mu=float(p.get("Mu", 100.0)),
                    Vu=float(p.get("Vu", 60.0)),
                )
                return {"code": "EUROCODE_2", "member_type": mtype, "result": res.__dict__, "is_safe": res.is_safe}
            elif "STEEL" in mtype:
                res = check_ec3_steel_beam(
                    h=float(p.get("h", 400.0)),
                    b=float(p.get("b", 200.0)),
                    tw=float(p.get("tw", 8.0)),
                    tf=float(p.get("tf", 13.0)),
                    r=float(p.get("r", 16.0)),
                    A=float(p.get("A", 8410.0)),
                    Wpl_y=float(p.get("Wpl_y", 1307e3)),
                    Wel_y=float(p.get("Wel_y", 1156e3)),
                    Iz=float(p.get("Iz", 1740e4)),
                    It=float(p.get("It", 39.5e4)),
                    Iw=float(p.get("Iw", 64.8e10)),
                    fy=float(p.get("fy", 275.0)),
                    Mu=float(p.get("Mu", 200.0)),
                    Vu=float(p.get("Vu", 100.0)),
                )
                return {"code": "EUROCODE_3", "member_type": mtype, "result": res.__dict__, "is_safe": res.is_safe}

        elif code in ("US", "ACI", "AISC", "US_IMPERIAL"):
            if "RC" in mtype or "CONCRETE" in mtype:
                res = check_aci318_rc_beam(
                    b=float(p.get("b", 300.0)),
                    h=float(p.get("h", 500.0)),
                    d=float(p.get("d", 450.0)),
                    fc_prime=float(p.get("fc_prime", 28.0)),
                    fy=float(p.get("fy", 420.0)),
                    As=float(p.get("As", 1200.0)),
                    As_prime=float(p.get("As_prime", 0.0)),
                    Mu=float(p.get("Mu", 100.0)),
                    Vu=float(p.get("Vu", 60.0)),
                )
                return {"code": "ACI_318_19", "member_type": mtype, "result": res.__dict__, "is_safe": res.is_safe}
            elif "STEEL" in mtype:
                res = check_aisc360_steel_beam(
                    d_depth=float(p.get("d", 400.0)),
                    bf=float(p.get("bf", 200.0)),
                    tf=float(p.get("tf", 13.0)),
                    tw=float(p.get("tw", 8.0)),
                    Ag=float(p.get("Ag", 8410.0)),
                    Zx=float(p.get("Zx", 1307e3)),
                    Sx=float(p.get("Sx", 1156e3)),
                    ry=float(p.get("ry", 45.0)),
                    J_torsion=float(p.get("J", 39.5e4)),
                    Cw=float(p.get("Cw", 64.8e10)),
                    Fy=float(p.get("Fy", 345.0)),
                    Mu=float(p.get("Mu", 200.0)),
                    Vu=float(p.get("Vu", 100.0)),
                )
                return {"code": "AISC_360_16", "member_type": mtype, "result": res.__dict__, "is_safe": res.is_safe}

        elif code in ("IS", "INDIAN", "IS456", "IS800"):
            if "RC" in mtype or "CONCRETE" in mtype:
                res = check_is456_rc_beam(
                    b=float(p.get("b", 300.0)),
                    h=float(p.get("h", 500.0)),
                    d=float(p.get("d", 450.0)),
                    fck=float(p.get("fck", 25.0)),
                    fy=float(p.get("fy", 415.0)),
                    Ast=float(p.get("Ast", 1200.0)),
                    Mu_applied=float(p.get("Mu", 100.0)),
                    Vu_applied=float(p.get("Vu", 60.0)),
                )
                return {"code": "IS_456_2000", "member_type": mtype, "result": res.__dict__, "is_safe": res.is_safe}
            elif "STEEL" in mtype:
                res = check_is800_steel_beam(
                    d_total=float(p.get("d", 400.0)),
                    b_flange=float(p.get("b", 200.0)),
                    tf=float(p.get("tf", 13.0)),
                    tw=float(p.get("tw", 8.0)),
                    r=float(p.get("r", 16.0)),
                    Ag=float(p.get("Ag", 8410.0)),
                    Zp=float(p.get("Zp", 1307e3)),
                    Ze=float(p.get("Ze", 1156e3)),
                    ry=float(p.get("ry", 45.0)),
                    fy=float(p.get("fy", 250.0)),
                    Mu=float(p.get("Mu", 150.0)),
                    Vu=float(p.get("Vu", 80.0)),
                )
                return {"code": "IS_800_2007", "member_type": mtype, "result": res.__dict__, "is_safe": res.is_safe}

        raise HTTPException(status_code=400, detail=f"Unsupported code '{code}' or member_type '{mtype}'.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/pbd/hinge-evaluate")
def pbd_hinge_evaluate_endpoint(req: PBDHingeRequest):
    """Generate plastic hinge backbone and evaluate ASCE 41-17 acceptance criteria."""
    mtype = req.member_type.upper()
    p = req.parameters

    try:
        if mtype == MemberType.RC_BEAM.value:
            res = create_rc_beam_hinge(
                member_id=req.member_id,
                b=float(p.get("b", 400.0)),
                h=float(p.get("h", 600.0)),
                d=float(p.get("d", 540.0)),
                fck=float(p.get("fck", 27.0)),
                fy=float(p.get("fy", 400.0)),
                As=float(p.get("As", 1800.0)),
                As_prime=float(p.get("As_prime", 400.0)),
                span_len=float(p.get("span_len", 6000.0)),
                V_design=float(p.get("V_design", 80.0)),
                demand_theta=req.demand_theta,
            )
            return res.model_dump()
        elif mtype == MemberType.STEEL_BEAM.value:
            res = create_steel_beam_hinge(
                member_id=req.member_id,
                zx=float(p.get("zx", 1500e3)),
                fy=float(p.get("fy", 275.0)),
                bf=float(p.get("bf", 200.0)),
                tf=float(p.get("tf", 16.0)),
                h=float(p.get("h", 400.0)),
                tw=float(p.get("tw", 9.0)),
                span_len=float(p.get("span_len", 7000.0)),
                ix=float(p.get("ix", 30000e4)),
                demand_theta=req.demand_theta,
            )
            return res.model_dump()
        else:
            raise HTTPException(status_code=400, detail=f"Member type '{mtype}' hinge not implemented via this quick endpoint.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
