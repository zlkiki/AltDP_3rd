"""Pydantic Request/Response Schemas for RC Shear Wall."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BoundaryElementSchema(BaseModel):
    length: float = Field(default=400.0, description="Boundary element length along wall (mm)", ge=50.0)
    width: float = Field(default=300.0, description="Boundary element thickness (mm)", ge=50.0)
    bar_diam: float = Field(default=22.0, description="Longitudinal bar diameter (mm)", ge=10.0)
    total_bars: int = Field(default=8, description="Number of boundary bars", ge=2)
    tie_diam: float = Field(default=10.0, description="Confining tie diameter (mm)", ge=6.0)
    tie_spacing: float = Field(default=100.0, description="Tie spacing (mm)", ge=25.0)
    tie_legs_x: int = Field(default=2, description="Number of tie legs in X", ge=1)
    tie_legs_y: int = Field(default=2, description="Number of tie legs in Y", ge=1)


class RCWallCheckRequest(BaseModel):
    name: str = "W1"
    lw: float = Field(default=4000.0, description="Wall length (mm)", ge=200.0)
    tw: float = Field(default=300.0, description="Wall thickness (mm)", ge=100.0)
    hw: float = Field(default=3000.0, description="Wall story height (mm)", ge=500.0)
    cover: float = Field(default=40.0, description="Clear cover (mm)", ge=10.0)
    
    # Web reinforcement
    vert_bar_diam: float = Field(default=13.0, description="Web vertical bar diameter (mm)", ge=6.0)
    vert_spacing: float = Field(default=200.0, description="Web vertical bar spacing (mm)", ge=25.0)
    vert_layers: int = Field(default=2, description="Number of vertical curtains (1 or 2)", ge=1, le=4)
    
    horiz_bar_diam: float = Field(default=13.0, description="Web horizontal bar diameter (mm)", ge=6.0)
    horiz_spacing: float = Field(default=200.0, description="Web horizontal bar spacing (mm)", ge=25.0)
    horiz_layers: int = Field(default=2, description="Number of horizontal curtains (1 or 2)", ge=1, le=4)
    
    # Boundary elements
    left_boundary: Optional[BoundaryElementSchema] = None
    right_boundary: Optional[BoundaryElementSchema] = None
    
    # Materials
    fck: float = Field(default=27.0, description="Concrete compressive strength (MPa)", ge=10.0)
    fy: float = Field(default=400.0, description="Vertical rebar yield strength (MPa)", ge=200.0)
    fys: float = Field(default=400.0, description="Horizontal rebar yield strength (MPa)", ge=200.0)
    
    # Factored Forces
    Pu: float = Field(default=1500.0, description="Factored axial force (kN, + = comp)")
    Vu: float = Field(default=650.0, description="Factored in-plane shear (kN)")
    Mu: float = Field(default=1800.0, description="Factored in-plane bending moment (kN*m)")
    
    # Seismic & Displacement
    delta_u: float = Field(default=30.0, description="Design inelastic top displacement (mm)", ge=0.0)
