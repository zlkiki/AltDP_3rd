"""Pydantic Request/Response Schemas for RC Slab & Punching Shear."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class SlabSupportTypeEnum(str, Enum):
    cantilever = "cantilever"
    simply_supported = "simply_supported"
    one_end_continuous = "one_end_continuous"
    both_ends_continuous = "both_ends_continuous"


class ColumnLocationEnum(str, Enum):
    interior = "interior"
    edge = "edge"
    corner = "corner"


class OneWaySlabCheckRequest(BaseModel):
    name: str = "S1"
    span_L: float = Field(default=4000.0, description="Clear span length (mm)", ge=500.0)
    thickness_h: float = Field(default=180.0, description="Slab thickness (mm)", ge=50.0)
    cover: float = Field(default=25.0, description="Clear cover (mm)", ge=10.0)
    support_type: SlabSupportTypeEnum = SlabSupportTypeEnum.both_ends_continuous
    
    # Reinforcement (per 1m strip)
    main_bar_diam: float = Field(default=13.0, description="Main bar diameter (mm)", ge=6.0)
    main_spacing: float = Field(default=150.0, description="Main bar spacing (mm)", ge=25.0)
    temp_bar_diam: float = Field(default=10.0, description="Temperature bar diameter (mm)", ge=6.0)
    temp_spacing: float = Field(default=200.0, description="Temperature bar spacing (mm)", ge=25.0)
    
    # Materials & Loads
    fck: float = Field(default=24.0, description="Concrete strength (MPa)", ge=10.0)
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)", ge=200.0)
    Mu: float = Field(default=25.0, description="Factored bending moment per 1m (kN*m/m)")
    Vu: float = Field(default=35.0, description="Factored 1-way shear force per 1m (kN/m)")


class TwoWaySlabDDMRequest(BaseModel):
    name: str = "S2_DDM"
    l1: float = Field(default=6000.0, description="Span length in moment direction (mm)", ge=1000.0)
    l2: float = Field(default=6000.0, description="Transverse span length (mm)", ge=1000.0)
    c1: float = Field(default=500.0, description="Column dimension along l1 (mm)", ge=100.0)
    c2: float = Field(default=500.0, description="Column dimension along l2 (mm)", ge=100.0)
    thickness_h: float = Field(default=200.0, description="Slab thickness (mm)", ge=50.0)
    qu: float = Field(default=12.0, description="Factored uniform area load (kN/m2)", ge=0.1)
    is_interior_span: bool = Field(default=True, description="True for interior span, False for end span")
    has_edge_beam: bool = Field(default=False, description="True if edge beam is present")
    fck: float = Field(default=27.0, description="Concrete strength (MPa)", ge=10.0)
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)", ge=200.0)


class PunchingShearCheckRequest(BaseModel):
    column_name: str = "C1"
    location: ColumnLocationEnum = ColumnLocationEnum.interior
    c1: float = Field(default=500.0, description="Column dimension in moment direction (mm)", ge=100.0)
    c2: float = Field(default=500.0, description="Transverse column dimension (mm)", ge=100.0)
    slab_h: float = Field(default=250.0, description="Slab thickness (mm)", ge=80.0)
    eff_depth_d: float = Field(default=200.0, description="Effective depth d (mm)", ge=50.0)
    Vu: float = Field(default=450.0, description="Factored punching shear force (kN)")
    Munb: float = Field(default=60.0, description="Factored unbalanced moment (kN*m)")
    fck: float = Field(default=27.0, description="Concrete strength (MPa)", ge=10.0)
