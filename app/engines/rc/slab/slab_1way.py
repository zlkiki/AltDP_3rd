# app/engines/rc/slab/slab_1way.py
"""RC 1-Way Slab (1방향 단순/연속 슬래브 정밀 설계) Engine - KDS 14 20 70."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.rc.slab.base import calculate as calc_base_slab

MODULE_INFO = {
    "id": "slab_1way",
    "name": "1방향 슬래브 (1-Way Slab)",
    "category": "rc",
    "group": "slab",
    "geomType": "rc_slab",
    "description": "KDS 14 20 70에 따른 1방향 슬래브 정/부모멘트, 최소 두께 및 처짐 제한, 배력근 검토"
}


class Slab1WayInputSchema(BaseModel):
    span: float = Field(3500.0, description="슬래브 스팬 L (mm)")
    thickness: float = Field(150.0, description="슬래브 두께 (mm)")
    support_condition: str = Field("1단 연속 (L/24)", description="지지 조건 (단순지지, 1단연속, 양단연속, 캔틸레버)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(25.0, description="피복 두께 (mm)")
    
    DL: float = Field(4.5, description="고정하중 (kN/m²)")
    LL: float = Field(2.5, description="활하중 (kN/m²)")
    
    main_dia: int = Field(10, description="주철근 직경 (mm)")
    main_spacing: float = Field(150.0, description="주철근 간격 (mm)")
    temp_dia: int = Field(10, description="배력근 직경 (mm)")
    temp_spacing: float = Field(250.0, description="배력근 간격 (mm)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    span = float(data.get("span", 3500.0))
    t = float(data.get("thickness", 150.0))
    cond = str(data.get("support_condition", "1단 연속 (L/24)"))
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    cover = float(data.get("cover", 25.0))
    
    DL = float(data.get("DL", 4.5))
    LL = float(data.get("LL", 2.5))
    
    main_dia = int(data.get("main_dia", 10))
    main_spacing = float(data.get("main_spacing", 150.0))
    temp_dia = int(data.get("temp_dia", 10))
    temp_spacing = float(data.get("temp_spacing", 250.0))
    
    base_input = {
        "Lx": span, "Ly": span * 3.0, "thickness": t, "fck": fck,
        "rebar_grade": rebar_grade, "cover": cover, "DL": DL, "LL": LL,
        "main_dia": main_dia, "main_spacing": main_spacing,
        "temp_dia": temp_dia, "temp_spacing": temp_spacing
    }
    
    res = calc_base_slab(base_input)
    res["support_condition"] = cond
    return res
