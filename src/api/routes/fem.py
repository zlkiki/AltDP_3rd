"""
src/api/routes/fem.py
=====================
FastAPI REST API Endpoints for 2D FEM Analysis Modules (Foundation, Wall, Baseplate, Endplate, Slab).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from src.engine.fem.foundation_fem import FoundationFEMSolver
from src.engine.fem.wall_2way_fem import Wall2WayFEMSolver
from src.engine.fem.baseplate_fem import BasePlateFEMSolver
from src.engine.fem.endplate_fem import EndPlateFEMSolver
from src.engine.fem.slab_fem import IrregularSlabFEMSolver

router = APIRouter(prefix="/api/v1/fem", tags=["2D FEM Structural Analysis"])


# 1. Foundation FEM Request Schemas
class ColumnLoadInput(BaseModel):
    x: float = Field(..., description="Column X coordinate (m)")
    y: float = Field(..., description="Column Y coordinate (m)")
    P: float = Field(..., description="Axial load P (kN, compression > 0)")
    Mx: float = Field(0.0, description="Bending moment Mx (kNm)")
    My: float = Field(0.0, description="Bending moment My (kNm)")

class FoundationFEMRequest(BaseModel):
    length_x: float = Field(5.0, description="Foundation width (m)")
    length_y: float = Field(5.0, description="Foundation length (m)")
    thickness: float = Field(0.5, description="Thickness (m)")
    fck: float = Field(24.0, description="Concrete strength (MPa)")
    subgrade_modulus_ks: float = Field(20000.0, description="Subgrade modulus (kN/m^3)")
    nx: int = Field(8, description="Mesh divisions in X")
    ny: int = Field(8, description="Mesh divisions in Y")
    column_loads: List[ColumnLoadInput] = Field(default_factory=list)


@router.post("/foundation/solve")
async def solve_foundation_fem(req: FoundationFEMRequest):
    """Solve Mat/Footing Foundation 2D FEM with Tension Cut-off."""
    try:
        solver = FoundationFEMSolver(
            length_x=req.length_x,
            length_y=req.length_y,
            thickness=req.thickness,
            fck=req.fck,
            subgrade_modulus_ks=req.subgrade_modulus_ks,
            nx=req.nx,
            ny=req.ny
        )
        if not req.column_loads:
            # Add default center column load if none provided
            solver.add_column_load(req.length_x / 2.0, req.length_y / 2.0, P=1000.0)
        else:
            for cl in req.column_loads:
                solver.add_column_load(cl.x, cl.y, cl.P, cl.Mx, cl.My)
                
        result = solver.solve_nonlinear()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Foundation FEM analysis failed: {str(e)}")


# 2. 2-Way Basement Wall Request Schemas
class Wall2WayFEMRequest(BaseModel):
    length_b: float = Field(6.0, description="Wall length (m)")
    height_h: float = Field(3.5, description="Wall height (m)")
    thickness: float = Field(0.35, description="Wall thickness (m)")
    fck: float = Field(24.0, description="Concrete fck (MPa)")
    fy: float = Field(400.0, description="Rebar fy (MPa)")
    soil_gamma: float = Field(18.0, description="Soil density (kN/m^3)")
    surcharge_q: float = Field(10.0, description="Surface surcharge (kN/m^2)")
    water_table_depth: Optional[float] = Field(None, description="Water table depth from top (m)")
    boundary_bottom: str = Field("FIXED", description="Support condition (FIXED/PINNED)")
    boundary_top: str = Field("PINNED", description="Support condition (FIXED/PINNED)")
    boundary_left: str = Field("PINNED", description="Support condition (FIXED/PINNED)")
    boundary_right: str = Field("PINNED", description="Support condition (FIXED/PINNED)")


@router.post("/wall-2way/solve")
async def solve_wall_2way_fem(req: Wall2WayFEMRequest):
    """Solve 2-Way Basement Wall FEM under lateral earth and water pressures."""
    try:
        solver = Wall2WayFEMSolver(
            length_b=req.length_b,
            height_h=req.height_h,
            thickness=req.thickness,
            fck=req.fck,
            fy=req.fy,
            boundary_bottom=req.boundary_bottom,
            boundary_top=req.boundary_top,
            boundary_left=req.boundary_left,
            boundary_right=req.boundary_right
        )
        result = solver.solve(
            soil_gamma=req.soil_gamma,
            water_table_depth=req.water_table_depth,
            surcharge_q=req.surcharge_q
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"2-Way Wall FEM analysis failed: {str(e)}")


# 3. Baseplate FEM Request Schemas
class AnchorBoltInput(BaseModel):
    x_mm: float
    y_mm: float
    bolt_dia_mm: float = 24.0

class BasePlateFEMRequest(BaseModel):
    plate_bx: float = Field(500.0, description="Plate width X (mm)")
    plate_by: float = Field(500.0, description="Plate length Y (mm)")
    plate_thickness: float = Field(30.0, description="Plate thickness (mm)")
    steel_fy: float = Field(275.0, description="Steel fy (MPa)")
    concrete_fck: float = Field(24.0, description="Concrete fck (MPa)")
    axial_p_kn: float = Field(600.0, description="Column axial load (kN)")
    moment_mx_knm: float = Field(0.0, description="Moment Mx (kNm)")
    moment_my_knm: float = Field(0.0, description="Moment My (kNm)")
    anchor_bolts: List[AnchorBoltInput] = Field(default_factory=list)


@router.post("/baseplate/solve")
async def solve_baseplate_fem(req: BasePlateFEMRequest):
    """Solve Column Base Plate Nonlinear Contact FEM."""
    try:
        solver = BasePlateFEMSolver(
            plate_bx=req.plate_bx,
            plate_by=req.plate_by,
            plate_thickness=req.plate_thickness,
            steel_fy=req.steel_fy,
            concrete_fck=req.concrete_fck
        )
        if not req.anchor_bolts:
            solver.add_anchor_bolt(-req.plate_bx*0.35, -req.plate_by*0.35)
            solver.add_anchor_bolt( req.plate_bx*0.35, -req.plate_by*0.35)
            solver.add_anchor_bolt(-req.plate_bx*0.35,  req.plate_by*0.35)
            solver.add_anchor_bolt( req.plate_bx*0.35,  req.plate_by*0.35)
        else:
            for ab in req.anchor_bolts:
                solver.add_anchor_bolt(ab.x_mm, ab.y_mm, ab.bolt_dia_mm)
                
        solver.set_column_load(req.axial_p_kn, req.moment_mx_knm, req.moment_my_knm)
        result = solver.solve_contact()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Baseplate FEM analysis failed: {str(e)}")


# 4. Moment Endplate FEM Request Schemas
class EndPlateFEMRequest(BaseModel):
    plate_width_bp: float = Field(250.0, description="Plate width (mm)")
    plate_height_hp: float = Field(650.0, description="Plate height (mm)")
    plate_thickness_tp: float = Field(28.0, description="Plate thickness (mm)")
    beam_depth_d: float = Field(500.0, description="Beam depth (mm)")
    flange_width_bf: float = Field(200.0, description="Flange width (mm)")
    flange_thickness_tf: float = Field(16.0, description="Flange thickness (mm)")
    web_thickness_tw: float = Field(10.0, description="Web thickness (mm)")
    steel_fy: float = Field(355.0, description="Steel fy (MPa)")
    bolt_grade_fub: float = Field(1000.0, description="Bolt grade Fub (MPa)")
    bolt_dia_db: float = Field(24.0, description="Bolt diameter (mm)")
    moment_mu_knm: float = Field(200.0, description="Factored Moment Mu (kNm)")
    axial_pu_kn: float = Field(0.0, description="Factored Axial Pu (kN)")


@router.post("/endplate/solve")
async def solve_endplate_fem(req: EndPlateFEMRequest):
    """Solve Moment End-Plate Yield Line & Local Bending FEM."""
    try:
        solver = EndPlateFEMSolver(
            plate_width_bp=req.plate_width_bp,
            plate_height_hp=req.plate_height_hp,
            plate_thickness_tp=req.plate_thickness_tp,
            beam_depth_d=req.beam_depth_d,
            flange_width_bf=req.flange_width_bf,
            flange_thickness_tf=req.flange_thickness_tf,
            web_thickness_tw=req.web_thickness_tw,
            steel_fy=req.steel_fy,
            bolt_grade_fub=req.bolt_grade_fub,
            bolt_dia_db=req.bolt_dia_db
        )
        result = solver.solve(moment_mu_knm=req.moment_mu_knm, axial_pu_kn=req.axial_pu_kn)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Endplate FEM analysis failed: {str(e)}")


# 5. Irregular Slab FEM Request Schemas
class OpeningInput(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float

class ColumnSupportInput(BaseModel):
    x: float
    y: float
    col_bx_mm: float = 400.0
    col_by_mm: float = 400.0

class SlabFEMRequest(BaseModel):
    length_lx: float = Field(8.0, description="Slab length X (m)")
    length_ly: float = Field(6.0, description="Slab length Y (m)")
    thickness: float = Field(0.20, description="Slab thickness (m)")
    fck: float = Field(24.0, description="Concrete fck (MPa)")
    fy: float = Field(400.0, description="Rebar fy (MPa)")
    dead_load_kpa: float = Field(5.0, description="Dead load (kN/m^2)")
    live_load_kpa: float = Field(2.5, description="Live load (kN/m^2)")
    openings: List[OpeningInput] = Field(default_factory=list)
    column_supports: List[ColumnSupportInput] = Field(default_factory=list)


@router.post("/slab/solve")
async def solve_slab_fem(req: SlabFEMRequest):
    """Solve 2D Irregular Slab with Openings FEM."""
    try:
        solver = IrregularSlabFEMSolver(
            length_lx=req.length_lx,
            length_ly=req.length_ly,
            thickness=req.thickness,
            fck=req.fck,
            fy=req.fy
        )
        for op in req.openings:
            solver.add_opening(op.x_min, op.x_max, op.y_min, op.y_max)
            
        if not req.column_supports:
            # Add 4 corner/interior column supports
            solver.add_column_support(1.0, 1.0)
            solver.add_column_support(req.length_lx - 1.0, 1.0)
            solver.add_column_support(1.0, req.length_ly - 1.0)
            solver.add_column_support(req.length_lx - 1.0, req.length_ly - 1.0)
        else:
            for col in req.column_supports:
                solver.add_column_support(col.x, col.y, col.col_bx_mm, col.col_by_mm)
                
        solver.set_uniform_load(dead_load_kpa=req.dead_load_kpa, live_load_kpa=req.live_load_kpa)
        result = solver.solve()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Slab FEM analysis failed: {str(e)}")
