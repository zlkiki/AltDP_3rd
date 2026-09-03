"""
KDS 14 31 15 각형/원형 CFT 및 매립형 SRC 기둥 축력-휨모멘트(P-M) 상관곡선 해석 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any, List

MODULE_INFO = {
    "id": "misc_src_column",
    "name": "SRC/CFT 기둥 (매립·충전형) (SRC/CFT Column)",
    "category": "misc",
    "group": "src",
    "submodule": "column",
    "description": "KDS 14 31 15 각형강관 콘크리트 충전(CFT) 및 매립형 H형강(SRC) 기둥 P-M 상관곡선",
    "geomType": "src_section",
    "template": "src_section"
}

class ColSRCInput(BaseModel):
    section_type: str = Field("CFT_box", description="합성 단면 형태 (CFT_box, SRC_encased)")
    B: float = Field(500.0, description="단면 폭 B (mm)")
    H: float = Field(500.0, description="단면 높이 H (mm)")
    t_steel: float = Field(12.0, description="강판/강관 두께 (mm)")
    fck: float = Field(30.0, description="콘크리트 압축강도 (MPa)")
    fy_steel: float = Field(355.0, description="강재 항복강도 (MPa)")
    fy_rebar: float = Field(400.0, description="철근 항복강도 (MPa)")
    Pu: float = Field(3500.0, description="계수 축하중 (kN)")
    Mu: float = Field(420.0, description="계수 휨모멘트 (kN·m)")
    rebar_count: int = Field(8, description="주철근 개수 (SRC용)")
    rebar_dia: str = Field("D22", description="주철근 규격")

def calculate(data: ColSRCInput) -> Dict[str, Any]:
    B = data.B
    H = data.H
    t = data.t_steel
    fck = data.fck
    fys = data.fy_steel
    fyr = data.fy_rebar
    
    # 1. 단면 면적 산정
    if data.section_type == "CFT_box":
        # 외곽 강관
        As_steel = 2.0 * B * t + 2.0 * (H - 2.0 * t) * t
        Ac_conc = (B - 2.0 * t) * (H - 2.0 * t)
        As_rebar = 0.0
        # 소성단면계수 (강관)
        Zs_steel = (B * (H**2) / 4.0) - ((B - 2.0 * t) * ((H - 2.0 * t)**2) / 4.0)
        Zc_conc = ((B - 2.0 * t) * ((H - 2.0 * t)**2) / 4.0)
    else:  # SRC 매립형
        # H형강 400x400x13x21 가정
        As_steel = 2.0 * 200.0 * 16.0 + (350.0 - 32.0) * 10.0
        ab_map = {"D19": 286.5, "D22": 387.1, "D25": 506.7}
        ab = ab_map.get(data.rebar_dia, 387.1)
        As_rebar = data.rebar_count * ab
        Ac_conc = B * H - As_steel - As_rebar
        Zs_steel = 200.0 * 16.0 * (350.0 - 16.0) + 0.25 * 10.0 * ((350.0 - 32.0)**2)
        Zc_conc = (B * (H**2) / 4.0)
        
    # 2. 공칭 순수 축압축강도 P0
    # KDS 14 31 15: P0 = As * Fy + Asr * Fyr + C2 * fck * Ac (CFT는 C2=0.85, SRC는 0.85)
    C2 = 0.85
    P0 = (As_steel * fys + As_rebar * fyr + C2 * fck * Ac_conc) / 1000.0  # kN
    phi_c = 0.75
    phi_Pn_max = phi_c * P0
    
    # 3. 순수 휨 소성모멘트 M0
    M0 = (fys * Zs_steel + 0.5 * C2 * fck * Zc_conc) / 1e6  # kN·m
    phi_b = 0.90
    phi_Mn_max = phi_b * M0
    
    # 4. P-M 곡선 생성 (KDS 다각형 4점 단순 포락)
    # Point A: (0, P0)
    # Point B: (M0, 0.5*P0) -> 최대 모멘트점
    # Point C: (M0, 0)
    # Point D: (0, -As*Fy) -> 인장
    pm_points = [
        {"P": round(phi_Pn_max, 1), "M": 0.0},
        {"P": round(phi_Pn_max * 0.85, 1), "M": round(phi_Mn_max * 0.7, 1)},
        {"P": round(phi_Pn_max * 0.5, 1), "M": round(phi_Mn_max * 1.15, 1)},
        {"P": round(phi_Pn_max * 0.2, 1), "M": round(phi_Mn_max * 1.0, 1)},
        {"P": 0.0, "M": round(phi_Mn_max * 0.85, 1)},
        {"P": round(-phi_c * As_steel * fys / 1000.0, 1), "M": 0.0}
    ]
    
    # DCR 산정
    dcr_p = data.Pu / phi_Pn_max if phi_Pn_max > 0 else 999.0
    dcr_m = data.Mu / (phi_Mn_max * 1.15) if phi_Mn_max > 0 else 999.0
    max_dcr = max(dcr_p, dcr_m)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "axial_compression": {
            "title": "합성 단면 축압축강도 검토 (Composite Axial Capacity φPn,max)",
            "Pu_kN": data.Pu,
            "phi_Pn_max_kN": round(phi_Pn_max, 1),
            "As_steel_mm2": round(As_steel, 1),
            "Ac_conc_mm2": round(Ac_conc, 1),
            "dcr": round(dcr_p, 3),
            "phi": phi_c
        },
        "flexure": {
            "title": "합성 단면 휨모멘트 검토 (Composite Flexural Capacity φMn)",
            "Mu_kNm": data.Mu,
            "phi_Mn_max_kNm": round(phi_Mn_max * 1.15, 1),
            "dcr": round(dcr_m, 3),
            "phi": phi_b
        },
        "details": {
            "section_geometry": {
                "section_type": data.section_type,
                "width_B_mm": B,
                "height_H_mm": H,
                "steel_thickness_t_mm": t,
                "steel_area_As_mm2": round(As_steel, 1),
                "conc_area_Ac_mm2": round(Ac_conc, 1)
            }
        },
        "pm_points": pm_points,
        "pmCurve": [{"phiPn": round(pt["P"] * 1e3, 1), "phiMn": round(pt["M"] * 1e6, 1), "p_kN": pt["P"], "m_kNm": pt["M"]} for pt in pm_points],
        "pm": {
            "combo": "KDS 합성계수하중",
            "Pu": data.Pu * 1e3,
            "Mu": data.Mu * 1e6,
            "Mrθ": data.Mu * 1e6,
            "phiPn0": phi_Pn_max * 1e3,
            "phiMnθ": phi_Mn_max * 1.15 * 1e6,
            "dcr": round(max_dcr, 3),
            "pmCurve": [{"phiPn": round(pt["P"] * 1e3, 1), "phiMn": round(pt["M"] * 1e6, 1), "p_kN": pt["P"], "m_kNm": pt["M"]} for pt in pm_points]
        },
        "summary": f"{data.section_type} P-M 검토: phi_Pn={round(phi_Pn_max,1)}kN, phi_Mn={round(phi_Mn_max,1)}kN·m, DCR={round(max_dcr,2)} ({status})",
        "visual_data": {
            "type": "steel_box_pipe",
            "B": B,
            "H": H,
            "tw": t
        }
    }
