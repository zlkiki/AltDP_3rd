"""Pydantic Schemas for RC Beam API."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RCBeamCheckRequest(BaseModel):
    """Request payload for RC Beam capacity and serviceability check."""
    name: str = "B1"
    b: float = Field(default=400.0, description="Beam width bw (mm)", ge=50.0)
    h: float = Field(default=600.0, description="Total depth h (mm)", ge=50.0)
    cover: float = Field(default=50.0, description="Tension rebar cover to centroid (mm)", ge=20.0)
    cover_prime: float = Field(default=50.0, description="Compression rebar cover to centroid (mm)", ge=20.0)
    side_cover: float = Field(default=40.0, description="Side cover to stirrups (mm)", ge=20.0)
    
    As: float = Field(default=1935.0, description="Tension rebar area (mm2)", gt=0.0)
    As_prime: float = Field(default=0.0, description="Compression rebar area (mm2)", ge=0.0)
    
    Av: float = Field(default=142.6, description="Stirrup area per spacing (mm2)", ge=0.0)
    s: float = Field(default=200.0, description="Stirrup spacing (mm)", ge=50.0)
    
    Mu: float = Field(default=250.0, description="Factored design moment (kN*m)")
    Vu: float = Field(default=150.0, description="Factored design shear (kN)")
    Tu: float = Field(default=0.0, description="Factored design torsion (kN*m)")
    
    Ma: float = Field(default=160.0, description="Service load moment (kN*m)")
    span_length: float = Field(default=6000.0, description="Clear span length (mm)", ge=500.0)
    
    fck: float = Field(default=24.0, description="Concrete compressive strength (MPa)", ge=15.0)
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)", ge=200.0)
    fyt: Optional[float] = Field(default=None, description="Stirrup yield strength (MPa)")
    num_tension_bars: int = Field(default=5, description="Number of bottom layer bars", ge=1)


class RCBeamAutoDesignRequest(BaseModel):
    """Request payload for RC Beam automatic rebar layout design."""
    b: float = Field(default=400.0, description="Beam width (mm)", ge=100.0)
    h: float = Field(default=600.0, description="Beam height (mm)", ge=100.0)
    As_req: float = Field(default=1800.0, description="Required tension rebar area (mm2)", gt=0.0)
    cover: float = Field(default=40.0, description="Clear concrete cover (mm)", ge=20.0)
    stirrup_size: str = Field(default="D10", description="Stirrup bar size (D10, D13)")
    max_aggregate: float = Field(default=25.0, description="Max aggregate size (mm)", ge=10.0)
    preferred_sizes: Optional[List[str]] = Field(
        default=["D16", "D19", "D22", "D25", "D29"],
        description="Candidate rebar sizes"
    )
