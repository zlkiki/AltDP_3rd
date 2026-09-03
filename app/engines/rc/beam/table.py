# app/engines/rc/beam/table.py
"""RC Beam Table Batch Design (다수 보 일괄 표 입력 및 검토) Engine - KDS 14 20."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.engines.rc.beam.base import calculate as calc_single_beam

MODULE_INFO = {
    "id": "table",
    "name": "보 테이블 (Beam Table)",
    "category": "rc",
    "group": "beam",
    "geomType": "rc_rect",
    "description": "다수의 RC 보 단면 및 소요 하중을 테이블 형태로 일괄 입력하여 전체 부재의 휨/전단 DCR을 한번에 판정"
}


class BeamTableInputSchema(BaseModel):
    fck: float = Field(24.0, description="공통 콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="공통 철근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    
    # 3 Sample representative beams
    b1_name: str = Field("1G1", description="보 1 이름")
    b1_b: float = Field(400.0, description="보 1 폭 b (mm)")
    b1_h: float = Field(600.0, description="보 1 춤 h (mm)")
    b1_Mu: float = Field(220.0, description="보 1 소요모멘트 Mu (kN*m)")
    b1_Vu: float = Field(110.0, description="보 1 소요전단력 Vu (kN)")
    b1_top_bars: int = Field(4, description="보 1 상부 주근 개수 (D22)")
    b1_bot_bars: int = Field(4, description="보 1 하부 주근 개수 (D22)")
    
    b2_name: str = Field("1G2", description="보 2 이름")
    b2_b: float = Field(500.0, description="보 2 폭 b (mm)")
    b2_h: float = Field(700.0, description="보 2 춤 h (mm)")
    b2_Mu: float = Field(380.0, description="보 2 소요모멘트 Mu (kN*m)")
    b2_Vu: float = Field(160.0, description="보 2 소요전단력 Vu (kN)")
    b2_top_bars: int = Field(5, description="보 2 상부 주근 개수 (D25)")
    b2_bot_bars: int = Field(5, description="보 2 하부 주근 개수 (D25)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    cover = float(data.get("cover", 40.0))
    
    beams_input = [
        {
            "name": str(data.get("b1_name", "1G1")),
            "b": float(data.get("b1_b", 400.0)),
            "h": float(data.get("b1_h", 600.0)),
            "Mu": float(data.get("b1_Mu", 220.0)),
            "Vu": float(data.get("b1_Vu", 110.0)),
            "top_dia": 22, "top_num": int(data.get("b1_top_bars", 4)),
            "bot_dia": 22, "bot_num": int(data.get("b1_bot_bars", 4)),
            "stirrup_dia": 10, "stirrup_spacing": 200.0, "stirrup_legs": 2,
            "fck": fck, "rebar_grade": rebar_grade, "cover": cover
        },
        {
            "name": str(data.get("b2_name", "1G2")),
            "b": float(data.get("b2_b", 500.0)),
            "h": float(data.get("b2_h", 700.0)),
            "Mu": float(data.get("b2_Mu", 380.0)),
            "Vu": float(data.get("b2_Vu", 160.0)),
            "top_dia": 25, "top_num": int(data.get("b2_top_bars", 5)),
            "bot_dia": 25, "bot_num": int(data.get("b2_bot_bars", 5)),
            "stirrup_dia": 10, "stirrup_spacing": 150.0, "stirrup_legs": 2,
            "fck": fck, "rebar_grade": rebar_grade, "cover": cover
        }
    ]
    
    results = []
    max_dcr = 0.0
    
    for b_in in beams_input:
        res = calc_single_beam(b_in)
        dcr = res.get("governing_dcr", 0.0)
        max_dcr = max(max_dcr, dcr)
        results.append({
            "name": b_in["name"],
            "section": f"{int(b_in['b'])}x{int(b_in['h'])}",
            "rebar": f"Top {b_in['top_num']}-D{b_in['top_dia']} / Bot {b_in['bot_num']}-D{b_in['bot_dia']}",
            "phiMn_kNm": res["flexure"]["phiMn_kNm"],
            "phiVn_kN": res["shear"]["phiVn_kN"],
            "dcr": dcr,
            "status": res["status"]
        })
        
    overall_status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": overall_status,
        "governing_dcr": round(max_dcr, 3),
        "total_beams_evaluated": len(results),
        "batch_summary": {
            r["name"]: f"{r['section']} | DCR: {r['dcr']} ({r['status']})" for r in results
        },
        "beam_details": {
            r["name"]: {
                "section": r["section"],
                "rebar": r["rebar"],
                "phiMn_kNm": r["phiMn_kNm"],
                "phiVn_kN": r["phiVn_kN"],
                "dcr": r["dcr"],
                "status": r["status"]
            } for r in results
        }
    }
