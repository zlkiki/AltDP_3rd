"""Pydantic DTO Schemas for RC Footing, Retaining Wall, and Tie Beam."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SpreadFootingRequest(BaseModel):
    name: str = Field(default="F1", description="Footing identifier")
    Bx: float = Field(default=2400.0, description="Footing width in X (mm)")
    Ly: float = Field(default=2400.0, description="Footing length in Y (mm)")
    thickness_H: float = Field(default=600.0, description="Thickness (mm)")
    depth_Df: float = Field(default=1500.0, description="Embedment depth (mm)")
    cover: float = Field(default=75.0, description="Clear cover (mm)")
    
    col_cx: float = Field(default=500.0, description="Column width in X (mm)")
    col_cy: float = Field(default=500.0, description="Column width in Y (mm)")
    col_type: str = Field(default="interior", description="Column position: interior/edge/corner")
    
    fck: float = Field(default=24.0, description="Concrete compressive strength (MPa)")
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)")
    qa_allowable: float = Field(default=250.0, description="Allowable soil bearing capacity (kPa)")
    soil_unit_weight: float = Field(default=18.0, description="Soil unit weight (kN/m3)")
    
    rebar_x_diam: float = Field(default=16.0, description="Rebar diameter in X (mm)")
    rebar_x_spacing: float = Field(default=150.0, description="Rebar spacing in X (mm)")
    rebar_y_diam: float = Field(default=16.0, description="Rebar diameter in Y (mm)")
    rebar_y_spacing: float = Field(default=150.0, description="Rebar spacing in Y (mm)")
    
    P_serv: float = Field(default=1000.0, description="Service vertical load (kN)")
    Mx_serv: float = Field(default=50.0, description="Service moment about X (kN*m)")
    My_serv: float = Field(default=40.0, description="Service moment about Y (kN*m)")
    
    Pu: float = Field(default=1400.0, description="Factored vertical load (kN)")
    Mux: float = Field(default=70.0, description="Factored moment about X (kN*m)")
    Muy: float = Field(default=55.0, description="Factored moment about Y (kN*m)")


class CombinedFootingRequest(BaseModel):
    name: str = Field(default="CF1", description="Combined footing identifier")
    Bx: float = Field(default=2000.0, description="Transverse width (mm)")
    Ly: float = Field(default=6500.0, description="Longitudinal length (mm)")
    thickness_H: float = Field(default=800.0, description="Thickness (mm)")
    cover: float = Field(default=75.0, description="Clear cover (mm)")
    
    col1_cx: float = Field(default=500.0, description="Col 1 width X (mm)")
    col1_cy: float = Field(default=500.0, description="Col 1 width Y (mm)")
    col1_dist_from_left: float = Field(default=400.0, description="Col 1 center from left edge (mm)")
    col1_P_serv: float = Field(default=800.0, description="Col 1 service load (kN)")
    col1_Pu: float = Field(default=1100.0, description="Col 1 factored load (kN)")
    
    col2_cx: float = Field(default=600.0, description="Col 2 width X (mm)")
    col2_cy: float = Field(default=600.0, description="Col 2 width Y (mm)")
    col2_dist_from_left: float = Field(default=5000.0, description="Col 2 center from left edge (mm)")
    col2_P_serv: float = Field(default=1400.0, description="Col 2 service load (kN)")
    col2_Pu: float = Field(default=1900.0, description="Col 2 factored load (kN)")
    
    fck: float = Field(default=27.0, description="Concrete strength (MPa)")
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)")
    qa_allowable: float = Field(default=300.0, description="Allowable bearing (kPa)")
    
    top_bar_diam: float = Field(default=22.0, description="Top rebar diameter (mm)")
    top_bar_count: int = Field(default=14, description="Top rebar count")
    bot_bar_diam: float = Field(default=19.0, description="Bottom rebar diameter (mm)")
    bot_bar_count: int = Field(default=12, description="Bottom rebar count")


class UndergroundBeamRequest(BaseModel):
    name: str = Field(default="TB1", description="Tie beam identifier")
    b: float = Field(default=400.0, description="Beam width (mm)")
    h: float = Field(default=600.0, description="Beam depth (mm)")
    length: float = Field(default=6000.0, description="Span length (mm)")
    cover: float = Field(default=50.0, description="Clear cover (mm)")
    
    connected_col_Pu: float = Field(default=2000.0, description="Connected Column Factored Load (kN)")
    Pu_tension: float = Field(default=200.0, description="Direct axial tension (kN)")
    Mu: float = Field(default=80.0, description="Factored bending moment (kN*m)")
    Vu: float = Field(default=60.0, description="Factored shear force (kN)")
    
    fck: float = Field(default=24.0, description="Concrete strength (MPa)")
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)")
    
    top_bars_count: int = Field(default=4, description="Top bars count")
    top_bar_diam: float = Field(default=22.0, description="Top bar diameter (mm)")
    bot_bars_count: int = Field(default=4, description="Bottom bars count")
    bot_bar_diam: float = Field(default=22.0, description="Bottom bar diameter (mm)")
    stirrup_diam: float = Field(default=10.0, description="Stirrup diameter (mm)")
    stirrup_spacing: float = Field(default=200.0, description="Stirrup spacing (mm)")


class RetainingWallRequest(BaseModel):
    name: str = Field(default="RW1", description="Retaining wall identifier")
    wall_type: str = Field(default="cantilever_t", description="cantilever_t/cantilever_l/gravity/basement_wall")
    
    H_total: float = Field(default=4500.0, description="Total wall height (mm)")
    stem_t_top: float = Field(default=300.0, description="Stem top thickness (mm)")
    stem_t_bot: float = Field(default=450.0, description="Stem bottom thickness (mm)")
    base_width_B: float = Field(default=3200.0, description="Base footing width (mm)")
    base_t: float = Field(default=500.0, description="Base slab thickness (mm)")
    toe_length: float = Field(default=1000.0, description="Toe projection length (mm)")
    heel_length: float = Field(default=1750.0, description="Heel projection length (mm)")
    front_embedment_Df: float = Field(default=800.0, description="Front embedment depth (mm)")
    
    soil_unit_weight: float = Field(default=19.0, description="Soil unit weight (kN/m3)")
    sat_unit_weight: float = Field(default=20.0, description="Saturated soil unit weight (kN/m3)")
    phi_deg: float = Field(default=30.0, description="Internal friction angle (deg)")
    cohesion: float = Field(default=0.0, description="Cohesion (kPa)")
    base_friction_coef: float = Field(default=0.55, description="Friction coef tan(delta)")
    surcharge_q: float = Field(default=10.0, description="Surcharge load (kPa)")
    water_table_depth: float = Field(default=6000.0, description="Water table depth from top (mm)")
    qa_allowable: float = Field(default=300.0, description="Allowable soil bearing (kPa)")
    
    fck: float = Field(default=24.0, description="Concrete strength (MPa)")
    fy: float = Field(default=400.0, description="Rebar yield strength (MPa)")
    cover: float = Field(default=50.0, description="Clear cover (mm)")
    
    stem_main_bar_diam: float = Field(default=19.0, description="Stem main rebar diameter (mm)")
    stem_main_bar_spacing: float = Field(default=150.0, description="Stem main rebar spacing (mm)")
    toe_main_bar_diam: float = Field(default=16.0, description="Toe bottom rebar diameter (mm)")
    toe_main_bar_spacing: float = Field(default=150.0, description="Toe bottom rebar spacing (mm)")
    heel_main_bar_diam: float = Field(default=19.0, description="Heel top rebar diameter (mm)")
    heel_main_bar_spacing: float = Field(default=150.0, description="Heel top rebar spacing (mm)")
