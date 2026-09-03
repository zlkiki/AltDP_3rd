# app/engines/rc/slab/reinf.py
"""RC Slab Detailed Reinforcement & Opening Trimmer Design Engine - KDS 14 20."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_AREA

MODULE_INFO = {
    "id": "reinf",
    "name": "슬래브 개구부 보강 (Slab Opening Rebar)",
    "category": "rc",
    "group": "slab",
    "geomType": "rc_slab",
    "description": "슬래브 관통 개구부(Opening) 주변 절단 철근량 보강근(Trimmer Bar) 및 대각 보강근(Diagonal Rebar) 산정"
}


class SlabReinfInputSchema(BaseModel):
    slab_thickness: float = Field(200.0, description="슬래브 두께 (mm)")
    opening_width_x: float = Field(600.0, description="개구부 X방향 폭 (mm)")
    opening_length_y: float = Field(600.0, description="개구부 Y방향 길이 (mm)")
    
    slab_rebar_dia: int = Field(13, description="슬래브 기본 배근 직경 (mm)")
    slab_rebar_spacing: float = Field(200.0, description="슬래브 기본 배근 간격 (mm)")
    
    trimmer_dia: int = Field(16, description="개구부 보강근(Trimmer) 직경 (mm)")
    diag_dia: int = Field(13, description="모서리 45도 대각 보강근 직경 (mm)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    t = float(data.get("slab_thickness", 200.0))
    ox = float(data.get("opening_width_x", 600.0))
    oy = float(data.get("opening_length_y", 600.0))
    
    s_dia = int(data.get("slab_rebar_dia", 13))
    s_spacing = float(data.get("slab_rebar_spacing", 200.0))
    t_dia = int(data.get("trimmer_dia", 16))
    diag_dia = int(data.get("diag_dia", 13))
    
    # Cut rebar count
    cut_x_bars = int(ox / s_spacing)
    cut_y_bars = int(oy / s_spacing)
    
    as_cut_x = cut_x_bars * REBAR_AREA.get(s_dia, 126.7)
    as_cut_y = cut_y_bars * REBAR_AREA.get(s_dia, 126.7)
    
    # Required parallel trimmer bars per side (Half of total cut area placed on each side)
    as_trimmer_bar = REBAR_AREA.get(t_dia, 198.6)
    req_trimmer_x_per_side = max(1, math.ceil((as_cut_x / 2.0) / as_trimmer_bar))
    req_trimmer_y_per_side = max(1, math.ceil((as_cut_y / 2.0) / as_trimmer_bar))
    
    # 45-degree diagonal crack control rebar (typically 2-D13 top & bot per corner)
    diag_bars_per_corner = 2
    
    return {
        "status": "OK",
        "governing_dcr": 0.0,
        "opening_geometry": {
            "size_mm": f"{int(ox)} x {int(oy)}",
            "slab_thickness_mm": t
        },
        "cut_reinforcement": {
            "cut_bars_x_dir": f"{cut_x_bars}-D{s_dia} (As = {int(as_cut_x)} mm²)",
            "cut_bars_y_dir": f"{cut_y_bars}-D{s_dia} (As = {int(as_cut_y)} mm²)"
        },
        "trimmer_rebar_required": {
            "x_direction_each_side": f"{req_trimmer_x_per_side}-D{t_dia} (Top & Bot)",
            "y_direction_each_side": f"{req_trimmer_y_per_side}-D{t_dia} (Top & Bot)"
        },
        "corner_diagonal_rebar": {
            "each_corner_spec": f"{diag_bars_per_corner}-D{diag_dia} (Top & Bot, 45-degree)"
        }
    }
