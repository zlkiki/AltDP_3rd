"""Pydantic v2 Schemas for RC Column API Endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RCColumnDesignRequest(BaseModel):
    """Input payload for comprehensive RC column design."""
    name: str = Field(default="C1", description="Column tag/name")
    b: float = Field(default=600.0, description="Column width (mm)", ge=150.0)
    h: float = Field(default=600.0, description="Column depth (mm)", ge=150.0)
    cover: float = Field(default=60.0, description="Clear cover to rebar centroid (mm)", ge=20.0)
    
    # Rebar details
    bar_diam: float = Field(default=25.0, description="Longitudinal bar diameter (mm)", ge=10.0)
    total_bars: int = Field(default=12, description="Total number of longitudinal bars", ge=4)
    tie_diam: float = Field(default=10.0, description="Tie bar diameter (mm)", ge=6.0)
    tie_spacing: float = Field(default=300.0, description="Tie spacing (mm)", ge=50.0)
    tie_legs_x: int = Field(default=2, description="Tie legs in X direction", ge=2)
    tie_legs_y: int = Field(default=2, description="Tie legs in Y direction", ge=2)
    is_spiral: bool = Field(default=False, description="True if spiral column")
    
    # Framing & Slenderness
    Lu: float = Field(default=3600.0, description="Unsupported column length (mm)", ge=500.0)
    k: float = Field(default=1.0, description="Effective length factor", ge=0.5)
    is_braced: bool = Field(default=True, description="True if braced/non-sway frame")
    M1x: float = Field(default=0.0, description="Smaller end moment about X (kN*m)")
    M2x: float = Field(default=350.0, description="Larger end moment about X (kN*m)")
    M1y: float = Field(default=0.0, description="Smaller end moment about Y (kN*m)")
    M2y: float = Field(default=0.0, description="Larger end moment about Y (kN*m)")
    
    # Critical Section Design Forces
    Pu: float = Field(default=2500.0, description="Factored axial load (kN)")
    Mux: float = Field(default=350.0, description="Factored moment about X (kN*m)")
    Muy: float = Field(default=0.0, description="Factored moment about Y (kN*m)")
    Vux: float = Field(default=0.0, description="Factored shear in X (kN)")
    Vuy: float = Field(default=120.0, description="Factored shear in Y (kN)")
    
    # Materials
    fck: float = Field(default=30.0, description="Concrete compressive strength (MPa)", ge=15.0)
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)", ge=200.0)


class PMCurveRequest(BaseModel):
    """Input payload to generate 2D or 3D P-M interaction surfaces."""
    b: float = Field(default=600.0, description="Column width (mm)", ge=150.0)
    h: float = Field(default=600.0, description="Column depth (mm)", ge=150.0)
    cover: float = Field(default=60.0, description="Rebar cover (mm)", ge=20.0)
    bar_diam: float = Field(default=25.0, description="Bar diameter (mm)", ge=10.0)
    total_bars: int = Field(default=12, description="Total bars", ge=4)
    is_spiral: bool = Field(default=False)
    fck: float = Field(default=30.0, description="fck (MPa)")
    fy: float = Field(default=400.0, description="fy (MPa)")
    theta_deg: float = Field(default=0.0, description="Angle of bending in degrees")
    num_points: int = Field(default=40, description="Curve sampling points", ge=10, le=100)
