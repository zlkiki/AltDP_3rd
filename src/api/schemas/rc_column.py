"""Pydantic v2 Schemas for RC Column API Endpoints.

Includes metadata-driven 4-subtab definitions (section, rebar, load, option)
for automated dynamic form rendering conforming to Requirement 23.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RCColumnDesignRequest(BaseModel):
    """Input payload for comprehensive RC column design with 4-subtab metadata."""
    name: str = Field(
        default="C1",
        description="Column tag/name",
        json_schema_extra={"tab": "section", "group": "general", "label": "부재명"}
    )
    
    # 1. Section & Materials (단면 및 재료)
    b: float = Field(
        default=600.0,
        description="Column width in X direction (mm)",
        ge=150.0,
        le=3000.0,
        json_schema_extra={"tab": "section", "group": "geometry", "unit": "mm", "label": "단면 폭 (b)"}
    )
    h: float = Field(
        default=600.0,
        description="Column depth in Y direction (mm)",
        ge=150.0,
        le=3000.0,
        json_schema_extra={"tab": "section", "group": "geometry", "unit": "mm", "label": "단면 높이 (h)"}
    )
    cover: float = Field(
        default=60.0,
        description="Distance to longitudinal rebar centroid (mm)",
        ge=20.0,
        le=150.0,
        json_schema_extra={"tab": "section", "group": "geometry", "unit": "mm", "label": "철근 중심 피복 (dc)"}
    )
    fck: float = Field(
        default=30.0,
        description="Concrete compressive strength (MPa)",
        ge=15.0,
        le=100.0,
        json_schema_extra={"tab": "section", "group": "materials", "unit": "MPa", "label": "콘크리트 강도 (fck)"}
    )
    fy: float = Field(
        default=400.0,
        description="Longitudinal rebar yield strength (MPa)",
        ge=200.0,
        le=800.0,
        json_schema_extra={"tab": "section", "group": "materials", "unit": "MPa", "label": "주철근 항복강도 (fy)"}
    )
    
    # 2. Reinforcement Detailing (철근 배근)
    bar_diam: float = Field(
        default=25.0,
        description="Longitudinal bar nominal diameter (mm)",
        ge=10.0,
        le=50.0,
        json_schema_extra={"tab": "rebar", "group": "main_rebar", "unit": "mm", "label": "주철근 직경 (db)"}
    )
    total_bars: int = Field(
        default=12,
        description="Total number of longitudinal bars",
        ge=4,
        le=48,
        json_schema_extra={"tab": "rebar", "group": "main_rebar", "unit": "EA", "label": "주철근 총 개수"}
    )
    tie_diam: float = Field(
        default=10.0,
        description="Transverse tie / stirrup diameter (mm)",
        ge=6.0,
        le=25.0,
        json_schema_extra={"tab": "rebar", "group": "tie_rebar", "unit": "mm", "label": "띠철근 직경 (dt)"}
    )
    tie_spacing: float = Field(
        default=300.0,
        description="Tie spacing along column height (mm)",
        ge=50.0,
        le=600.0,
        json_schema_extra={"tab": "rebar", "group": "tie_rebar", "unit": "mm", "label": "띠철근 배근 간격 (s)"}
    )
    tie_legs_x: int = Field(
        default=2,
        description="Number of tie shear legs resisting Vy",
        ge=2,
        le=8,
        json_schema_extra={"tab": "rebar", "group": "tie_rebar", "unit": "개", "label": "X방향 전단 다리수"}
    )
    tie_legs_y: int = Field(
        default=2,
        description="Number of tie shear legs resisting Vx",
        ge=2,
        le=8,
        json_schema_extra={"tab": "rebar", "group": "tie_rebar", "unit": "개", "label": "Y방향 전단 다리수"}
    )
    is_spiral: bool = Field(
        default=False,
        description="True for spiral reinforcement column, False for tied column",
        json_schema_extra={"tab": "rebar", "group": "tie_rebar", "label": "나선철근 여부"}
    )
    
    # 3. Design Factored Loads (설계 하중)
    Pu: float = Field(
        default=2500.0,
        description="Factored axial load (kN, compression positive)",
        json_schema_extra={"tab": "load", "group": "axial_moment", "unit": "kN", "label": "계수 축력 (Pu)"}
    )
    Mux: float = Field(
        default=350.0,
        description="Factored bending moment about X-axis (kN·m)",
        json_schema_extra={"tab": "load", "group": "axial_moment", "unit": "kN·m", "label": "계수 모멘트 X (Mux)"}
    )
    Muy: float = Field(
        default=0.0,
        description="Factored bending moment about Y-axis (kN·m)",
        json_schema_extra={"tab": "load", "group": "axial_moment", "unit": "kN·m", "label": "계수 모멘트 Y (Muy)"}
    )
    Vux: float = Field(
        default=0.0,
        description="Factored shear force along X-axis (kN)",
        json_schema_extra={"tab": "load", "group": "shear", "unit": "kN", "label": "계수 전단력 X (Vux)"}
    )
    Vuy: float = Field(
        default=120.0,
        description="Factored shear force along Y-axis (kN)",
        json_schema_extra={"tab": "load", "group": "shear", "unit": "kN", "label": "계수 전단력 Y (Vuy)"}
    )
    
    # 4. Slenderness & Framing Options (장주 및 골조 옵션)
    Lu: float = Field(
        default=3600.0,
        description="Unsupported length of column (mm)",
        ge=500.0,
        le=20000.0,
        json_schema_extra={"tab": "option", "group": "slenderness", "unit": "mm", "label": "비지지 길이 (Lu)"}
    )
    k: float = Field(
        default=1.0,
        description="Effective buckling length factor",
        ge=0.5,
        le=5.0,
        json_schema_extra={"tab": "option", "group": "slenderness", "label": "유효좌굴길이계수 (k)"}
    )
    is_braced: bool = Field(
        default=True,
        description="True for braced / non-sway frame",
        json_schema_extra={"tab": "option", "group": "slenderness", "label": "횡구속(Non-sway) 여부"}
    )
    M1x: float = Field(
        default=0.0,
        description="Smaller end moment about X (kN·m)",
        json_schema_extra={"tab": "option", "group": "end_moments", "unit": "kN·m", "label": "상단 모멘트 X (M1x)"}
    )
    M2x: float = Field(
        default=350.0,
        description="Larger end moment about X (kN·m)",
        json_schema_extra={"tab": "option", "group": "end_moments", "unit": "kN·m", "label": "하단 모멘트 X (M2x)"}
    )
    M1y: float = Field(
        default=0.0,
        description="Smaller end moment about Y (kN·m)",
        json_schema_extra={"tab": "option", "group": "end_moments", "unit": "kN·m", "label": "상단 모멘트 Y (M1y)"}
    )
    M2y: float = Field(
        default=0.0,
        description="Larger end moment about Y (kN·m)",
        json_schema_extra={"tab": "option", "group": "end_moments", "unit": "kN·m", "label": "하단 모멘트 Y (M2y)"}
    )


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
    num_points: int = Field(default=200, description="Curve sampling points", ge=10, le=500)


def get_rc_column_ui_schema() -> Dict[str, Any]:
    """Extract 4-subtab metadata from Pydantic schema for front-end form generation."""
    schema = RCColumnDesignRequest.model_json_schema()
    properties = schema.get("properties", {})
    
    tabs = {
        "section": {"label": "단면/재료", "fields": []},
        "rebar": {"label": "철근배근", "fields": []},
        "load": {"label": "설계하중", "fields": []},
        "option": {"label": "장주/옵션", "fields": []}
    }
    
    for key, prop in properties.items():
        extra = prop.get("json_schema_extra", {})
        tab_key = extra.get("tab", "section")
        field_def = {
            "key": key,
            "label": extra.get("label", prop.get("title", key)),
            "unit": extra.get("unit", ""),
            "group": extra.get("group", "default"),
            "default": prop.get("default", None),
            "type": prop.get("type", "number"),
            "minimum": prop.get("minimum", None),
            "maximum": prop.get("maximum", None),
            "description": prop.get("description", "")
        }
        if tab_key in tabs:
            tabs[tab_key]["fields"].append(field_def)
            
    return {
        "title": "RC 기둥 설계 입력 (KDS 14 20 20)",
        "tabs": tabs,
        "raw_schema": schema
    }
