"""FastAPI Routes for Special Structures: SRC/CFT, Aluminium, and Retrofit."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.engine.src_composite.composite_column import (
    CFTColumnInput,
    SRCColumnInput,
    CFTType,
    check_cft_column,
    check_src_column,
)
from src.engine.src_composite.composite_beam import (
    CompositeBeamInput,
    StudBoltInput,
    check_composite_beam,
)
from src.engine.alu.alu_design import (
    AluSectionInput,
    AluAlloyType,
    AluSectionShape,
    check_alu_member,
)
from src.engine.rfm.retrofit_design import (
    RetrofitDesignInput,
    ExistingBeamProp,
    CFRPProp,
    SteelPlateProp,
    RetrofitType,
    RetrofitMethod,
    ExposureCondition,
    check_retrofit_member,
)

router = APIRouter(prefix="/api/v1/special", tags=["Special Structures"])


# ---------------------------------------------------------------------------
# 1. CFT Column Request / Response
# ---------------------------------------------------------------------------
class CFTColumnRequest(BaseModel):
    cft_type: str = Field("RECTANGULAR", description="RECTANGULAR or CIRCULAR")
    B: float = Field(400.0, description="Width in mm")
    H: float = Field(400.0, description="Height in mm")
    D: float = Field(400.0, description="Outer diameter in mm")
    t: float = Field(12.0, description="Wall thickness in mm")
    fck: float = Field(30.0, description="Concrete compressive strength in MPa")
    Fy: float = Field(355.0, description="Steel yield strength in MPa")
    L: float = Field(4000.0, description="Column length in mm")
    K: float = Field(1.0, description="Effective length factor")
    Pu: float = Field(3000.0, description="Factored axial compressive force in kN")


@router.post("/cft-column/check")
async def check_cft_column_endpoint(req: CFTColumnRequest):
    try:
        cft_type = CFTType.RECTANGULAR if req.cft_type.upper() == "RECTANGULAR" else CFTType.CIRCULAR
        inp = CFTColumnInput(
            cft_type=cft_type,
            B=req.B,
            H=req.H,
            D=req.D,
            t=req.t,
            fck=req.fck,
            Fy=req.Fy,
            L=req.L,
            K=req.K,
            Pu=req.Pu,
        )
        res = check_cft_column(inp)
        return {
            "status": "success",
            "is_safe": res.is_safe,
            "dcr_axial": res.dcr_axial,
            "Pno": res.Pno,
            "phi_Pn": res.phi_Pn,
            "Pn": res.Pn,
            "Pe_x": res.Pe_x,
            "Pe_y": res.Pe_y,
            "steel_ratio": res.steel_ratio,
            "is_compact": res.is_compact,
            "details": res.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 2. Encased SRC Column Request / Response
# ---------------------------------------------------------------------------
class SRCColumnRequest(BaseModel):
    B: float = Field(600.0, description="Concrete section width in mm")
    H: float = Field(600.0, description="Concrete section height in mm")
    cover: float = Field(50.0, description="Clear cover in mm")
    As: float = Field(11980.0, description="Steel core area in mm2")
    Is_x: float = Field(204000000.0, description="Steel core moment of inertia X in mm4")
    Is_y: float = Field(67500000.0, description="Steel core moment of inertia Y in mm4")
    Fy: float = Field(355.0, description="Steel yield strength in MPa")
    num_rebars: int = Field(8, description="Number of longitudinal rebars")
    rebar_dia: float = Field(22.0, description="Rebar diameter in mm")
    fck: float = Field(30.0, description="Concrete compressive strength in MPa")
    L: float = Field(4000.0, description="Column length in mm")
    K: float = Field(1.0, description="Effective length factor")
    Pu: float = Field(4000.0, description="Factored axial load in kN")


@router.post("/src-column/check")
async def check_src_column_endpoint(req: SRCColumnRequest):
    try:
        inp = SRCColumnInput(
            B=req.B,
            H=req.H,
            cover=req.cover,
            As=req.As,
            Is_x=req.Is_x,
            Is_y=req.Is_y,
            Fy=req.Fy,
            num_rebars=req.num_rebars,
            rebar_dia=req.rebar_dia,
            fck=req.fck,
            L=req.L,
            K=req.K,
            Pu=req.Pu,
        )
        res = check_src_column(inp)
        return {
            "status": "success",
            "is_safe": res.is_safe,
            "dcr_axial": res.dcr_axial,
            "Pno": res.Pno,
            "phi_Pn": res.phi_Pn,
            "Pn": res.Pn,
            "steel_ratio": res.steel_ratio,
            "details": res.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 3. Composite Beam Request / Response
# ---------------------------------------------------------------------------
class CompositeBeamRequest(BaseModel):
    L: float = Field(8000.0, description="Beam span in mm")
    beam_spacing: float = Field(3000.0, description="Beam spacing in mm")
    d_s: float = Field(400.0, description="Steel beam height in mm")
    b_f: float = Field(200.0, description="Steel beam flange width in mm")
    t_f: float = Field(13.0, description="Flange thickness in mm")
    t_w: float = Field(8.0, description="Web thickness in mm")
    Fy: float = Field(355.0, description="Steel yield strength in MPa")
    h_f: float = Field(120.0, description="Concrete slab thickness in mm")
    fck: float = Field(27.0, description="Concrete compressive strength in MPa")
    stud_dia: float = Field(19.0, description="Stud diameter in mm")
    num_studs_half_span: int = Field(20, description="Number of studs per half span")
    Mu: float = Field(350.0, description="Factored bending moment in kN*m")
    Vu: float = Field(150.0, description="Factored shear force in kN")


@router.post("/composite-beam/check")
async def check_composite_beam_endpoint(req: CompositeBeamRequest):
    try:
        stud = StudBoltInput(
            diameter=req.stud_dia,
            num_studs_half_span=req.num_studs_half_span,
        )
        inp = CompositeBeamInput(
            L=req.L,
            beam_spacing=req.beam_spacing,
            d_s=req.d_s,
            b_f=req.b_f,
            t_f=req.t_f,
            t_w=req.t_w,
            Fy=req.Fy,
            h_f=req.h_f,
            fck=req.fck,
            stud=stud,
            Mu=req.Mu,
            Vu=req.Vu,
        )
        res = check_composite_beam(inp)
        return {
            "status": "success",
            "is_safe": res.is_safe,
            "dcr_flexure": res.dcr_flexure,
            "dcr_shear": res.dcr_shear,
            "b_eff": res.b_eff,
            "Qn_single": res.Qn_single,
            "sum_Qn": res.sum_Qn,
            "composite_ratio": res.composite_ratio,
            "is_full_composite": res.is_full_composite,
            "phi_Mn": res.phi_Mn,
            "phi_Vn": res.phi_Vn,
            "plastic_neutral_axis": res.plastic_neutral_axis,
            "details": res.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 4. Aluminium Member Request / Response
# ---------------------------------------------------------------------------
class AluminiumRequest(BaseModel):
    alloy: str = Field("6061-T6", description="Alloy name e.g. 6061-T6, 6063-T6")
    shape: str = Field("I_SHAPE", description="I_SHAPE, RECT_TUBE, CIRC_TUBE")
    Ag: float = Field(4500.0, description="Gross area in mm2")
    Aw: float = Field(1800.0, description="Web shear area in mm2")
    Sx: float = Field(350000.0, description="Elastic section modulus X in mm3")
    Sy: float = Field(120000.0, description="Elastic section modulus Y in mm3")
    Zx: float = Field(400000.0, description="Plastic section modulus X in mm3")
    Zy: float = Field(160000.0, description="Plastic section modulus Y in mm3")
    rx: float = Field(88.0, description="Radius of gyration X in mm")
    ry: float = Field(51.6, description="Radius of gyration Y in mm")
    Lx: float = Field(3000.0, description="Length X in mm")
    Ly: float = Field(3000.0, description="Length Y in mm")
    Lb: float = Field(3000.0, description="Unbraced length for LTB in mm")
    is_welded_in_haz: bool = Field(False, description="HAZ reduction flag")
    Pu: float = Field(150.0, description="Factored axial force in kN")
    Mux: float = Field(25.0, description="Factored moment X in kN*m")
    Muy: float = Field(0.0, description="Factored moment Y in kN*m")
    Vu: float = Field(35.0, description="Factored shear force in kN")


@router.post("/aluminum/check")
async def check_aluminum_endpoint(req: AluminiumRequest):
    try:
        alloy_map = {
            "6061-T6": AluAlloyType.A6061_T6,
            "6063-T6": AluAlloyType.A6063_T6,
            "6082-T6": AluAlloyType.A6082_T6,
            "5083-H112": AluAlloyType.A5083_H112,
            "5083-O": AluAlloyType.A5083_O,
        }
        alloy = alloy_map.get(req.alloy, AluAlloyType.A6061_T6)
        inp = AluSectionInput(
            alloy=alloy,
            Ag=req.Ag,
            Aw=req.Aw,
            Sx=req.Sx,
            Sy=req.Sy,
            Zx=req.Zx,
            Zy=req.Zy,
            rx=req.rx,
            ry=req.ry,
            Lx=req.Lx,
            Ly=req.Ly,
            Lb=req.Lb,
            is_welded_in_haz=req.is_welded_in_haz,
            Pu=req.Pu,
            Mux=req.Mux,
            Muy=req.Muy,
            Vu=req.Vu,
        )
        res = check_alu_member(inp)
        return {
            "status": "success",
            "is_safe": res.is_safe,
            "max_dcr": res.max_dcr,
            "dcr_axial": res.dcr_axial,
            "dcr_flexure_x": res.dcr_flexure_x,
            "dcr_shear": res.dcr_shear,
            "dcr_combined": res.dcr_combined,
            "phi_Pt": res.phi_Pt,
            "phi_Pc": res.phi_Pc,
            "phi_Mnx": res.phi_Mnx,
            "phi_Vn": res.phi_Vn,
            "khaz": res.khaz,
            "details": res.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 5. Retrofit Design Request / Response
# ---------------------------------------------------------------------------
class RetrofitRequest(BaseModel):
    retrofit_type: str = Field("FLEXURE", description="FLEXURE, SHEAR, COMBINED")
    method: str = Field("CFRP_PLATE", description="CFRP_PLATE, CFRP_SHEET, STEEL_PLATE")
    b: float = Field(300.0, description="Beam width in mm")
    h: float = Field(600.0, description="Beam height in mm")
    d: float = Field(540.0, description="Effective depth in mm")
    fck: float = Field(24.0, description="Concrete compressive strength in MPa")
    As: float = Field(1520.0, description="Existing rebar area in mm2")
    fy: float = Field(400.0, description="Rebar yield strength in MPa")
    Av: float = Field(142.6, description="Stirrup area in mm2")
    s: float = Field(200.0, description="Stirrup spacing in mm")
    cfrp_tf: float = Field(1.2, description="CFRP thickness in mm")
    cfrp_bf: float = Field(200.0, description="CFRP width in mm")
    num_plies: int = Field(1, description="Number of CFRP plies")
    Mu: float = Field(350.0, description="Factored required moment in kN*m")
    Vu: float = Field(180.0, description="Factored required shear in kN")


@router.post("/retrofit/check")
async def check_retrofit_endpoint(req: RetrofitRequest):
    try:
        ret_type = RetrofitType(req.retrofit_type.upper())
        method = RetrofitMethod(req.method.upper())
        
        ex = ExistingBeamProp(
            b=req.b,
            h=req.h,
            d=req.d,
            fck=req.fck,
            As=req.As,
            fy=req.fy,
            Av=req.Av,
            s=req.s,
        )
        cfrp = CFRPProp(
            tf=req.cfrp_tf,
            bf=req.cfrp_bf,
            num_plies=req.num_plies,
        )
        inp = RetrofitDesignInput(
            retrofit_type=ret_type,
            method=method,
            existing=ex,
            cfrp=cfrp,
            Mu=req.Mu,
            Vu=req.Vu,
        )
        res = check_retrofit_member(inp)
        return {
            "status": "success",
            "is_safe": res.is_safe,
            "dcr_flexure": res.dcr_flexure,
            "dcr_shear": res.dcr_shear,
            "phi_Mn_orig": res.phi_Mn_orig,
            "phi_Mn_ret": res.phi_Mn_ret,
            "phi_Vn_orig": res.phi_Vn_orig,
            "phi_Vn_ret": res.phi_Vn_ret,
            "flexure_gain_ratio": res.flexure_gain_ratio,
            "shear_gain_ratio": res.shear_gain_ratio,
            "eps_fe": res.eps_fe,
            "debonding_governed": res.debonding_governed,
            "details": res.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
