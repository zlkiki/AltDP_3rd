"""
RC 보 배근 조합별 휨/전단 공칭·설계 내력 비교표(Capacity Table) 생성 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any, List

MODULE_INFO = {
    "id": "rc_beam_captable",
    "name": "보 내력표 (Beam Capacity Table)",
    "category": "rc",
    "group": "beam",
    "submodule": "captable",
    "description": "RC 보 규격 및 배근 단 수별 휨모멘트/전단 내력 일람표 자동 생성",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class BeamCapTableInput(BaseModel):
    b: float = Field(400.0, description="보 폭 (mm)")
    h: float = Field(700.0, description="보 춤 (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    stirrup_dia: str = Field("D10", description="스터럽 규격")
    stirrup_spacing: float = Field(150.0, description="스터럽 간격 (mm)")

def calculate(data: BeamCapTableInput) -> Dict[str, Any]:
    b = data.b
    h = data.h
    fck = data.fck
    fy = data.fy
    d = h - 65.0
    
    # 철근 지름 및 단면적
    rebar_db = {"D19": 19.1, "D22": 22.2, "D25": 25.4, "D29": 28.6, "D32": 31.8}
    rebar_area = {"D19": 286.5, "D22": 387.1, "D25": 506.7, "D29": 642.4, "D32": 794.2}
    
    table_rows = []
    rebar_list = ["D19", "D22", "D25", "D29", "D32"]
    counts = [2, 3, 4, 5, 6]
    
    phi_b = 0.85
    phi_v = 0.75
    beta1 = max(0.65, min(0.85, 0.85 - 0.007 * (fck - 28.0))) if fck > 28.0 else 0.85
    
    # 전단 기본 콘크리트 강도
    Vc = (1.0 / 6.0) * math.sqrt(fck) * b * d / 1000.0  # kN
    # 스터럽 강도 (2Leg)
    Av = 2.0 * 71.33 if data.stirrup_dia == "D10" else 2.0 * 126.7
    Vs = (Av * fy * d / data.stirrup_spacing) / 1000.0  # kN
    phi_Vn = phi_v * (Vc + Vs)
    
    for rname in rebar_list:
        ab = rebar_area[rname]
        for cnt in counts:
            As = cnt * ab
            a = (As * fy) / (0.85 * fck * b)
            if a < d:
                Mn = As * fy * (d - a / 2.0) / 1e6  # kN·m
                phi_Mn = phi_b * Mn
                rho = (As / (b * d)) * 100.0
                table_rows.append({
                    "rebar": f"{cnt}-{rname}",
                    "As_mm2": round(As, 1),
                    "rho_percent": round(rho, 2),
                    "a_mm": round(a, 1),
                    "Mn_kNm": round(Mn, 1),
                    "phi_Mn_kNm": round(phi_Mn, 1),
                    "phi_Vn_kN": round(phi_Vn, 1)
                })
    
    return {
        "status": "OK",
        "governing_dcr": 0.0,
        "max_dcr": 0.0,
        "section_info": f"{int(b)}x{int(h)} (fck={fck}, fy={fy})",
        "phi_Vc_kN": round(phi_v * Vc, 1),
        "phi_Vs_kN": round(phi_v * Vs, 1),
        "phi_Vn_kN": round(phi_Vn, 1),
        "capacity_table": table_rows[:15],
        "summary": f"보 내력 일람표 ({len(table_rows)}개 배근 조합 계산 완료)",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": h,
            "cover": 40.0,
            "top_rebar_count": 2,
            "bot_rebar_count": 4,
            "stirrup_space": data.stirrup_spacing
        }
    }

