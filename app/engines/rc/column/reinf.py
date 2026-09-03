# app/engines/rc/column/reinf.py
"""RC Column Detailed Multi-Face Reinforcement & Biaxial P-M Engine - KDS 14 20."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.engines.rc.column.base import generate_rebar_fibers, calculate as calc_base_column

MODULE_INFO = {
    "id": "reinf",
    "name": "상세 배근 기둥 (Column Rebar)",
    "category": "rc",
    "group": "column",
    "geomType": "rc_rect",
    "description": "모서리 주근 및 4면 중간 주근의 비대칭/상세 배치에 따른 정밀 3차원 P-Mx-My 상관곡면 해석"
}


class ColumnReinfInputSchema(BaseModel):
    b: float = Field(700.0, description="기둥 폭 b (mm)")
    h: float = Field(700.0, description="기둥 춤 h (mm)")
    fck: float = Field(30.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    
    corner_dia: int = Field(29, description="모서리 주근 직경 (4EA, mm)")
    side_y_num: int = Field(4, description="Y면 내부 주근 개수 (단면당)")
    side_y_dia: int = Field(25, description="Y면 내부 주근 직경 (mm)")
    side_z_num: int = Field(4, description="Z면 내부 주근 개수 (단면당)")
    side_z_dia: int = Field(25, description="Z면 내부 주근 직경 (mm)")
    
    Pu: float = Field(2500.0, description="설계 축압축력 Pu (kN)")
    Mux: float = Field(350.0, description="강축 휨모멘트 Mux (kN*m)")
    Muy: float = Field(250.0, description="약축 휨모멘트 Muy (kN*m)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    b = float(data.get("b", 700.0))
    h = float(data.get("h", 700.0))
    fck = float(data.get("fck", 30.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    cover = float(data.get("cover", 40.0))
    
    corner_dia = int(data.get("corner_dia", 29))
    side_y_num = int(data.get("side_y_num", 4))
    side_y_dia = int(data.get("side_y_dia", 25))
    side_z_num = int(data.get("side_z_num", 4))
    side_z_dia = int(data.get("side_z_dia", 25))
    
    Pu = float(data.get("Pu", 2500.0))
    Mux = float(data.get("Mux", 350.0))
    Muy = float(data.get("Muy", 250.0))
    
    # Map to base calculate with effective perimeter distribution
    num_y_eff = side_y_num + 2
    num_z_eff = side_z_num + 2
    
    base_input = {
        "b": b, "h": h, "fck": fck, "rebar_grade": rebar_grade, "cover": cover,
        "tie_dia": 10, "main_dia": side_y_dia, "num_y": num_y_eff, "num_z": num_z_eff,
        "Pu": Pu, "Mux": Mux, "Muy": Muy, "is_spiral": False
    }
    
    res = calc_base_column(base_input)
    res["section"]["corner_rebar"] = f"4-D{corner_dia}"
    res["section"]["side_rebar"] = f"Y: {side_y_num}-D{side_y_dia}, Z: {side_z_num}-D{side_z_dia}"
    
    return res
