"""
KDS 14 31 15 매립형 철골철근콘크리트(SRC) 보 소성응력분포법(PSDM) 휨/전단 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "misc_src_beam",
    "name": "SRC 보 (매립형) (SRC Beam)",
    "category": "misc",
    "group": "src",
    "submodule": "beam",
    "description": "KDS 14 31 15 매립형 H형강+RC 복합 단면 소성응력분포법(PSDM) 휨모멘트 및 전단 설계",
    "geomType": "src_section",
    "template": "src_section"
}

class BeamSRCInput(BaseModel):
    steel_sec: str = Field("H-400x200x8x13", description="매립 H형강 단면 선택 (KS 규격)")
    b: float = Field(450.0, description="콘크리트 보 폭 (mm)", ge=0.0)
    h: float = Field(750.0, description="콘크리트 보 높이 (mm)", ge=0.0)
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)", ge=0.0)
    fy_rebar: float = Field(400.0, description="철근 항복강도 (MPa)", ge=0.0)
    steel_H: float = Field(400.0, description="매립 H형강 높이 (mm)", ge=0.0)
    steel_B: float = Field(200.0, description="매립 H형강 폭 (mm)", ge=0.0)
    steel_tw: float = Field(8.0, description="매립 H형강 웨브 두께 (mm)", ge=0.0)
    steel_tf: float = Field(13.0, description="매립 H형강 플랜지 두께 (mm)", ge=0.0)
    fy_steel: float = Field(355.0, description="강재 항복강도 (MPa)", ge=0.0)
    Mu: float = Field(750.0, description="계수 휨모멘트 (kN·m)", ge=0.0)
    Vu: float = Field(450.0, description="계수 전단력 (kN)", ge=0.0)
    
    top_rebar_num: int = Field(4, description="상부 주철근 개수 (EA)", ge=0)
    top_rebar_dia: int = Field(22, description="상부 주철근 직경 (mm)", ge=0)
    bot_rebar_num: int = Field(4, description="하부 주철근 개수 (EA)", ge=0)
    bot_rebar_dia: int = Field(25, description="하부 주철근 직경 (mm)", ge=0)

def calculate(data: Any) -> Dict[str, Any]:
    get_v = lambda k, default: data.get(k, default) if isinstance(data, dict) else getattr(data, k, default)
    
    b = float(get_v("b", 450.0))
    h = float(get_v("h", 750.0))
    fck = float(get_v("fck", 27.0))
    fyr = float(get_v("fy_rebar", 400.0))
    s_H = float(get_v("steel_H", 400.0))
    s_B = float(get_v("steel_B", 200.0))
    s_tw = float(get_v("steel_tw", 8.0))
    s_tf = float(get_v("steel_tf", 13.0))
    fys = float(get_v("fy_steel", 355.0))
    Mu = float(get_v("Mu", 750.0))
    Vu = float(get_v("Vu", 450.0))
    
    top_num = int(get_v("top_rebar_num", 4))
    top_dia = int(get_v("top_rebar_dia", 22))
    bot_num = int(get_v("bot_rebar_num", 4))
    bot_dia = int(get_v("bot_rebar_dia", 25))
    
    # 1. 단면 요소별 특성치
    # 강재
    As_steel = 2.0 * s_B * s_tf + (s_H - 2.0 * s_tf) * s_tw
    Zs_steel = s_B * s_tf * (s_H - s_tf) + 0.25 * s_tw * ((s_H - 2.0 * s_tf)**2)
    Mps = (fys * Zs_steel) / 1e6  # kN·m
    
    # 철근
    As_bot = bot_num * (math.pi * bot_dia * bot_dia / 4.0)
    As_top = top_num * (math.pi * top_dia * top_dia / 4.0)
    d_bot = h - 60.0
    d_top = 60.0
    
    # 2. 콘크리트 및 철근의 휨 기여도
    a_conc = (As_bot * fyr) / (0.85 * fck * b) if (0.85 * fck * b) > 0 else 0.0
    Mpc_rc = (As_bot * fyr * (d_bot - a_conc / 2.0)) / 1e6  # kN·m
    
    # 전체 공칭 휨강도 Mn = Mps + Mpc_rc
    Mn_total = Mps + Mpc_rc
    phi_b = 0.90
    phi_Mn = phi_b * Mn_total
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 3. 전단강도 산정 (강재 웨브 + 콘크리트 전단)
    V_steel = (0.6 * fys * (s_H * s_tw)) / 1000.0  # kN
    Vc = (1.0 / 6.0) * math.sqrt(fck) * b * d_bot / 1000.0  # kN
    
    phi_v = 0.75
    phi_Vn = phi_v * (V_steel + Vc)
    dcr_shear = Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    max_dcr = max(dcr_flexure, dcr_shear)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    top_str = f"{top_num}-D{top_dia}"
    bot_str = f"{bot_num}-D{bot_dia}"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "flexure": {
            "title": "SRC 합성 단면 소성 휨모멘트 검토 (PSDM Flexural Capacity φMn)",
            "Mu_kNm": Mu,
            "phi_Mn_kNm": round(phi_Mn, 1),
            "Mps_steel_kNm": round(Mps, 1),
            "Mpc_rc_kNm": round(Mpc_rc, 1),
            "dcr": round(dcr_flexure, 3),
            "phi": phi_b
        },
        "shear": {
            "title": "SRC 합성 단면 전단강도 검토 (Composite Shear Capacity φVn)",
            "Vu_kN": Vu,
            "phi_Vn_kN": round(phi_Vn, 1),
            "V_steel_kN": round(V_steel, 1),
            "Vc_conc_kN": round(Vc, 1),
            "dcr": round(dcr_shear, 3),
            "phi": phi_v
        },
        "details": {
            "composite_section": {
                "rc_width_b_mm": b,
                "rc_height_h_mm": h,
                "steel_profile": f"H-{s_H}x{s_B}x{s_tw}x{s_tf}",
                "steel_area_As_mm2": round(As_steel, 1),
                "top_rebar": top_str,
                "bot_rebar": bot_str,
                "rebar_bot_As_mm2": round(As_bot, 1)
            }
        },
        "summary": f"SRC 보 PSDM 검토: phi_Mn={round(phi_Mn,1)}kN·m (철골={round(Mps,1)}, RC={round(Mpc_rc,1)}), 전단 DCR={round(dcr_shear,2)} ({status})",
        "visual_data": {
            "type": "steel_h",
            "H": s_H,
            "B": s_B,
            "tw": s_tw,
            "tf": s_tf
        }
    }
