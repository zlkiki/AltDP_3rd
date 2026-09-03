"""PBD (Performance-Based Design) Data Models and DTOs.

Defines schemas for plastic hinge parameters, backbone curves,
and performance level evaluations according to ASCE 41-17 / KDS 41 17 00.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PerformanceLevel(str, Enum):
    """Performance levels according to ASCE 41-17 / KDS 41 17 00."""
    IO = "IO"                # Immediate Occupancy (즉시거주)
    LS = "LS"                # Life Safety (인명안전)
    CP = "CP"                # Collapse Prevention (붕괴방지)
    COLLAPSE = "COLLAPSE"    # Collapse (붕괴/허용치 초과)


class MemberType(str, Enum):
    """Member types supported for plastic hinge generation."""
    RC_BEAM = "RC_BEAM"
    RC_COLUMN = "RC_COLUMN"
    RC_WALL_FLEXURE = "RC_WALL_FLEXURE"
    RC_WALL_SHEAR = "RC_WALL_SHEAR"
    STEEL_BEAM = "STEEL_BEAM"
    STEEL_COLUMN = "STEEL_COLUMN"
    STEEL_BRACE_TENSION = "STEEL_BRACE_TENSION"
    STEEL_BRACE_COMPRESSION = "STEEL_BRACE_COMPRESSION"


class BackbonePoint(BaseModel):
    """Single coordinate point in a moment-rotation or force-displacement curve."""
    theta_rad: float = Field(..., description="Rotation (rad) or deformation")
    moment_knm: float = Field(..., description="Bending moment (kN*m) or force (kN)")


class HingeParameters(BaseModel):
    """ASCE 41-17 / KDS 41 17 00 Plastic Hinge Backbone and Acceptance Criteria parameters."""
    a: float = Field(..., description="Plastic rotation angle at capping / peak resistance (rad)")
    b: float = Field(..., description="Plastic rotation angle at residual strength degradation (rad)")
    c: float = Field(..., description="Residual strength ratio (Mr / My)")
    io_limit: float = Field(..., description="Immediate Occupancy permissible plastic rotation (rad)")
    ls_limit: float = Field(..., description="Life Safety permissible plastic rotation (rad)")
    cp_limit: float = Field(..., description="Collapse Prevention permissible plastic rotation (rad)")
    alpha: float = Field(0.03, description="Hardening slope ratio ((Mu - My) / My)")


class HingePerformance(BaseModel):
    """Complete plastic hinge performance evaluation result DTO."""
    member_id: int = Field(..., description="Member identifier")
    member_type: str = Field(..., description="Structural member type")
    my_knm: float = Field(..., description="Yield moment My (kN*m) or yield force (kN)")
    theta_y_rad: float = Field(..., description="Yield rotation theta_y (rad) or yield deformation")
    io_limit_rad: float = Field(..., description="Total rotation at IO limit (rad)")
    ls_limit_rad: float = Field(..., description="Total rotation at LS limit (rad)")
    cp_limit_rad: float = Field(..., description="Total rotation at CP limit (rad)")
    backbone_curve: List[BackbonePoint] = Field(..., description="Multilinear backbone curve points")
    performance_level: str = Field(..., description="Evaluated level: IO, LS, CP, or COLLAPSE")
    demand_theta_rad: Optional[float] = Field(None, description="Demand rotation (rad) if evaluated")
    dcr_cp: Optional[float] = Field(None, description="Demand-Capacity Ratio against CP limit")
