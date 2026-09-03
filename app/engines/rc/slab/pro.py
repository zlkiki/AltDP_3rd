# app/engines/rc/slab/pro.py
"""RC Slab-Beam Integrated Professional Flexure & Shear Engine - KDS 14 20."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.rc.slab.base import calculate as calc_base_slab

MODULE_INFO = {
    "id": "pro",
    "name": "일체형 슬래브-보 (Slab Pro)",
    "category": "rc",
    "group": "slab",
    "geomType": "rc_slab",
    "description": "보 부재와 일체로 타설된 연속 슬래브의 부모멘트 단면 및 단부 전단력 정밀 검토"
}


class SlabProInputSchema(BaseModel):
    Lx: float = Field(4500.0, description="단변 스팬 (mm)")
    Ly: float = Field(6500.0, description="장변 스팬 (mm)")
    thickness: float = Field(220.0, description="슬래브 두께 (mm)")
    beam_width: float = Field(400.0, description="지지 보 폭 (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    
    DL: float = Field(5.5, description="고정하중 (kN/m²)")
    LL: float = Field(4.0, description="활하중 (kN/m²)")
    
    top_dia: int = Field(13, description="지점부 상부 주철근 직경 (mm)")
    top_spacing: float = Field(150.0, description="상부 주철근 간격 (mm)")
    bot_dia: int = Field(13, description="중앙부 하부 주철근 직경 (mm)")
    bot_spacing: float = Field(175.0, description="하부 주철근 간격 (mm)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    Lx = float(data.get("Lx", 4500.0))
    Ly = float(data.get("Ly", 6500.0))
    t = float(data.get("thickness", 220.0))
    bw = float(data.get("beam_width", 400.0))
    fck = float(data.get("fck", 27.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    
    DL = float(data.get("DL", 5.5))
    LL = float(data.get("LL", 4.0))
    
    top_dia = int(data.get("top_dia", 13))
    top_spacing = float(data.get("top_spacing", 150.0))
    bot_dia = int(data.get("bot_dia", 13))
    bot_spacing = float(data.get("bot_spacing", 175.0))
    
    base_input = {
        "Lx": Lx, "Ly": Ly, "thickness": t, "fck": fck,
        "rebar_grade": rebar_grade, "cover": 30.0, "DL": DL, "LL": LL,
        "main_dia": bot_dia, "main_spacing": bot_spacing,
        "temp_dia": top_dia, "temp_spacing": top_spacing
    }
    
    res = calc_base_slab(base_input)
    res["section"]["support_beam_width"] = bw
    return res
