# app/engines/rc/slab/table.py
"""RC Slab Batch Table Design Engine - KDS 14 20."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.engines.rc.slab.base import calculate as calc_single_slab

MODULE_INFO = {
    "id": "table",
    "name": "슬래브 테이블 (Slab Table)",
    "category": "rc",
    "group": "slab",
    "geomType": "rc_slab",
    "description": "층별/패널별 다수의 슬래브 설계 제원을 테이블 형태로 일괄 입력하여 휨/두께 DCR을 한번에 판정"
}


class SlabTableInputSchema(BaseModel):
    fck: float = Field(24.0, description="공통 콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="공통 철근 강종")
    
    s1_name: str = Field("S1 (주거 세대)", description="슬래브 1 패널명")
    s1_Lx: float = Field(3600.0, description="슬래브 1 단변 (mm)")
    s1_Ly: float = Field(4800.0, description="슬래브 1 장변 (mm)")
    s1_t: float = Field(210.0, description="슬래브 1 두께 (mm)")
    s1_DL: float = Field(5.0, description="슬래브 1 DL (kN/m²)")
    s1_LL: float = Field(2.0, description="슬래브 1 LL (kN/m²)")
    
    s2_name: str = Field("S2 (지하 주차장)", description="슬래브 2 패널명")
    s2_Lx: float = Field(8000.0, description="슬래브 2 단변 (mm)")
    s2_Ly: float = Field(8000.0, description="슬래브 2 장변 (mm)")
    s2_t: float = Field(350.0, description="슬래브 2 두께 (mm)")
    s2_DL: float = Field(7.0, description="슬래브 2 DL (kN/m²)")
    s2_LL: float = Field(5.0, description="슬래브 2 LL (kN/m²)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    
    slabs = [
        {
            "name": str(data.get("s1_name", "S1 (주거 세대)")),
            "Lx": float(data.get("s1_Lx", 3600.0)),
            "Ly": float(data.get("s1_Ly", 4800.0)),
            "thickness": float(data.get("s1_t", 210.0)),
            "DL": float(data.get("s1_DL", 5.0)),
            "LL": float(data.get("s1_LL", 2.0)),
            "fck": fck, "rebar_grade": rebar_grade, "cover": 25.0,
            "main_dia": 10, "main_spacing": 200.0, "temp_dia": 10, "temp_spacing": 250.0
        },
        {
            "name": str(data.get("s2_name", "S2 (지하 주차장)")),
            "Lx": float(data.get("s2_Lx", 8000.0)),
            "Ly": float(data.get("s2_Ly", 8000.0)),
            "thickness": float(data.get("s2_t", 350.0)),
            "DL": float(data.get("s2_DL", 7.0)),
            "LL": float(data.get("s2_LL", 5.0)),
            "fck": fck, "rebar_grade": rebar_grade, "cover": 30.0,
            "main_dia": 16, "main_spacing": 150.0, "temp_dia": 13, "temp_spacing": 200.0
        }
    ]
    
    results = []
    max_dcr = 0.0
    
    for s in slabs:
        res = calc_single_slab(s)
        dcr = res.get("governing_dcr", 0.0)
        max_dcr = max(max_dcr, dcr)
        results.append({
            "name": s["name"],
            "span": f"{int(s['Lx'])}x{int(s['Ly'])} (t={int(s['thickness'])}mm)",
            "system": res["system"],
            "dcr": dcr,
            "status": res["status"]
        })
        
    return {
        "status": "OK" if max_dcr <= 1.0 else "NG",
        "governing_dcr": round(max_dcr, 3),
        "panels_summary": {
            r["name"]: f"{r['span']} | {r['system']} | DCR: {r['dcr']} ({r['status']})" for r in results
        }
    }
