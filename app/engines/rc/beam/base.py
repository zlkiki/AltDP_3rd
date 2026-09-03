# app/engines/rc/beam/base.py
"""RC Beam (기본 직사각형 보 휨/전단/처짐 검토 및 설계) Engine - KDS 14 20 20/22."""
import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import (
    REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu, get_effective_depth
)
from app.engines.common.units import to_si_force, to_si_moment

MODULE_INFO = {
    "id": "base",
    "name": "보 (RC Beam)",
    "category": "rc",
    "group": "beam",
    "geomType": "rc_rect",
    "description": "KDS 14 20 콘크리트구조 설계기준에 따른 직사각형 보 휨 및 전단 성능 검토"
}


class BeamInputSchema(BaseModel):
    b: float = Field(400.0, description="보 폭 (mm)")
    h: float = Field(600.0, description="보 춤 (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종 (SD400, SD500 등)")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    Mu: float = Field(250.0, description="소요 휨모멘트 (kN*m)")
    Vu: float = Field(120.0, description="소요 전단력 (kN)")
    top_dia: int = Field(22, description="상부 주근 직경 (mm)")
    top_num: int = Field(4, description="상부 주근 개수 (EA)")
    bot_dia: int = Field(22, description="하부 주근 직경 (mm)")
    bot_num: int = Field(4, description="하부 주근 개수 (EA)")
    stirrup_dia: int = Field(10, description="전단철근 직경 (mm)")
    stirrup_spacing: float = Field(200.0, description="전단철근 간격 (mm)")
    stirrup_legs: int = Field(2, description="전단철근 가닥 수")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    b = float(data.get("b", 400.0))
    h = float(data.get("h", 600.0))
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 40.0))
    
    Mu_kNm = float(data.get("Mu", 250.0))
    Vu_kN = float(data.get("Vu", 120.0))
    
    top_dia = int(data.get("top_dia", 22))
    top_num = int(data.get("top_num", 4))
    bot_dia = int(data.get("bot_dia", 22))
    bot_num = int(data.get("bot_num", 4))
    
    stirrup_dia = int(data.get("stirrup_dia", 10))
    stirrup_spacing = float(data.get("stirrup_spacing", 200.0))
    stirrup_legs = int(data.get("stirrup_legs", 2))
    
    Es = 200000.0
    phi_m = 0.85
    phi_v = 0.75
    
    beta1 = calc_beta1(fck)
    eta = calc_eta(fck)
    ecu = get_eps_cu(fck)
    sb = eta * 0.85 * fck
    
    # Positive moment: bottom rebar in tension, top in compression
    As_t = bot_num * REBAR_AREA.get(bot_dia, 387.1)
    As_c = top_num * REBAR_AREA.get(top_dia, 387.1)
    
    d = get_effective_depth(h, bot_dia, cover, stirrup_dia)
    d_c = cover + stirrup_dia + top_dia / 2.0
    
    # 1. Flexure Analysis (c iteration)
    a = As_t * fy / (sb * b)
    fs_c = fy
    for _ in range(30):
        c_iter = a / beta1
        if c_iter <= 0:
            break
        es_c = ecu * (c_iter - d_c) / c_iter if c_iter > d_c else 0.0
        fs_c = min(es_c * Es, fy)
        a_new = (As_t * fy - As_c * max(fs_c - sb, 0.0)) / (sb * b)
        a_next = 0.5 * a + 0.5 * a_new
        if abs(a_next - a) < 0.001:
            a = a_next
            break
        a = a_next
        
    c = a / beta1
    et = ecu * (d - c) / c if c > 0 else 0.005
    phi_flex = phi_m if et >= 0.005 else (0.65 + (phi_m - 0.65) * (et - 0.002) / 0.003 if et > 0.002 else 0.65)
    
    Cc = sb * a * b
    Cs = As_c * max(fs_c - sb, 0.0)
    Mn = Cc * (d - a / 2.0) + Cs * (d - d_c)
    phiMn = phi_flex * Mn * 1e-6  # kN*m
    dcr_flex = abs(Mu_kNm) / phiMn if phiMn > 0 else 999.0
    
    # 2. Shear Analysis (KDS 14 20 22)
    Vc = (1.0 / 6.0) * math.sqrt(fck) * b * d
    Av = stirrup_legs * REBAR_AREA.get(stirrup_dia, 71.33)
    fyt = min(fy, 500.0)
    Vs = (Av * fyt * d / stirrup_spacing) if stirrup_spacing > 0 else 0.0
    
    Vs_max = (5.0 / 6.0) * math.sqrt(fck) * b * d - Vc
    Vs_max = max(Vs_max, 0.0)
    Vs = min(Vs, Vs_max)
    Vn = Vc + Vs
    phiVn = phi_v * Vn * 1e-3  # kN
    dcr_shear = abs(Vu_kN) / phiVn if phiVn > 0 else 999.0
    
    # Shear spacing limit (KDS 14 20 22 4.2.5)
    s_limit = min(d / 2.0, 600.0) if Vs <= (1.0 / 3.0) * math.sqrt(fck) * b * d else min(d / 4.0, 300.0)
    s_status = "OK" if stirrup_spacing <= s_limit else "NG"
    
    # Classification: Deformation-controlled (Flexure) vs Force-controlled (Shear)
    is_deformation_controlled = et >= 0.005 and dcr_shear <= 1.0
    behavior_type = "DEFORMATION_CONTROLLED" if is_deformation_controlled else "FORCE_CONTROLLED"
    
    # Governing DCR & Status
    governing_dcr = max(dcr_flex, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 and s_status == "OK" else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "behavior_type": behavior_type,
        "b": b, "h": h, "d": round(d, 1), "cover": cover, "dc": round(d_c, 1),
        "fck": fck, "fy": fy, "fys": fyt, "Es": Es,
        "n_top": top_num, "topDia": top_dia, "As_top": round(As_c, 1),
        "n_bot": bot_num, "botDia": bot_dia, "As_bot": round(As_t, 1),
        "As": round(As_t, 1),
        "stirLegs": stirrup_legs, "stirDia": stirrup_dia, "stirSpacing": stirrup_spacing, "Av": round(Av, 1),
        "s_limit": round(s_limit, 1), "s_status": s_status,
        "Mu": Mu_kNm * 1e6, "Vu": Vu_kN * 1e3,
        "phi_Mn": phiMn * 1e6, "phi_Vn": phiVn * 1e3,
        "Mn": Mn, "Vn": Vn, "Vc": Vc, "Vs": Vs,
        "c": round(c, 1), "a": round(a, 1), "eps_t": round(et, 5), "phi": round(phi_flex, 3),
        "eta": round(eta, 3), "beta1": round(beta1, 3),
        "flexure": {
            "dcr": round(dcr_flex, 3),
            "phiMn_kNm": round(phiMn, 2),
            "phiMn": phiMn * 1e6,
            "Mu_kNm": Mu_kNm,
            "Mu": Mu_kNm * 1e6,
            "c_mm": round(c, 1),
            "a_mm": round(a, 1),
            "c_final": round(c, 1),
            "a_final": round(a, 1),
            "eps_t": round(et, 5),
            "phi": round(phi_flex, 3),
            "As": round(As_t, 1),
            "As_prime": round(As_c, 1),
            "rho": round(As_t / (b * d), 5),
            "rho_min": round(max(0.25 * math.sqrt(fck) / fy, 1.4 / fy), 5),
            "rho_max": round(0.714 * beta1 * (sb / fy) * (ecu / (ecu + 0.004)), 5)
        },
        "shear": {
            "dcr": round(dcr_shear, 3),
            "phiVn_kN": round(phiVn, 2),
            "phiVn": phiVn * 1e3,
            "Vu_kN": Vu_kN,
            "Vu": Vu_kN * 1e3,
            "Vc_kN": round(Vc * 1e-3, 2),
            "Vs_kN": round(Vs * 1e-3, 2),
            "Vc": Vc,
            "Vs": Vs,
            "Av": round(Av, 1),
            "stirLegs": stirrup_legs,
            "stirDia": stirrup_dia,
            "stirSpacing": stirrup_spacing,
            "s_limit": round(s_limit, 1),
            "s_status": s_status
        },
        "section": {
            "b": b, "h": h, "d": round(d, 1), "cover": cover,
            "top_rebar": f"{top_num}-D{top_dia}",
            "bot_rebar": f"{bot_num}-D{bot_dia}",
            "stirrup": f"D{stirrup_dia}@{int(stirrup_spacing)}"
        }
    }
