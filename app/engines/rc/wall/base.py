# app/engines/rc/wall/base.py
"""RC Shear Wall (단일 전단벽 파이버 P-M 상관도 및 면내 전단강도) Engine - KDS 14 20 72."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu

MODULE_INFO = {
    "id": "base",
    "name": "전단벽 (Shear Wall)",
    "category": "rc",
    "group": "wall",
    "geomType": "rc_wall",
    "description": "KDS 14 20에 따른 RC 전단벽 수직철근 파이버 P-M 상관도 및 면내 전단강도(Vn) 검토"
}


class WallInputSchema(BaseModel):
    Lw: float = Field(3000.0, description="벽체 길이 Lw (mm)")
    tw: float = Field(250.0, description="벽체 두께 tw (mm)")
    Hw: float = Field(3000.0, description="벽체 층고 Hw (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(30.0, description="피복 두께 (mm)")
    
    Pu: float = Field(1200.0, description="설계 축력 (kN)")
    Mu: float = Field(800.0, description="설계 면내 휨모멘트 (kN*m)")
    Vu: float = Field(350.0, description="설계 면내 전단력 (kN)")
    
    vert_dia: int = Field(13, description="수직 철근 직경 (mm)")
    vert_spacing: float = Field(200.0, description="수직 철근 간격 (mm)")
    vert_curtains: int = Field(2, description="수직 배근 열 수 (1=단배근, 2=복배근)")
    
    horiz_dia: int = Field(10, description="수평 전단철근 직경 (mm)")
    horiz_spacing: float = Field(200.0, description="수평 전단철근 간격 (mm)")


def calculate(data: Any) -> Dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    elif not isinstance(data, dict):
        data = dict(data)

    Lw = float(data.get("Lw", 3000.0))  # mm
    tw = float(data.get("tw", 250.0))   # mm
    Hw = float(data.get("Hw", 3000.0))  # mm
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 40.0))
    
    Pu_kN = float(data.get("Pu", 1200.0))
    Mu_kNm = float(data.get("Mu", 800.0))
    Vu_kN = float(data.get("Vu", 350.0))
    
    vert_dia = int(data.get("vert_dia", 13))
    vert_spacing = float(data.get("vert_spacing", 200.0))
    vert_curtains = int(data.get("vert_curtains", 2))
    
    horiz_dia = int(data.get("horiz_dia", 10))
    horiz_spacing = float(data.get("horiz_spacing", 200.0))
    
    # 1. Vertical Reinforcement Discretization
    as_vert = vert_curtains * REBAR_AREA.get(vert_dia, 126.7)
    num_vert_bars = max(2, int(Lw / vert_spacing) + 1)
    
    fibers = []
    for i in range(num_vert_bars):
        x = -Lw / 2.0 + (Lw / (num_vert_bars - 1)) * i
        fibers.append({"x": x, "As": as_vert})
        
    Ast = sum(f["As"] for f in fibers)
    Ag = Lw * tw
    
    beta1 = calc_beta1(fck)
    eta = calc_eta(fck)
    ecu = get_eps_cu(fck)
    sb = eta * 0.85 * fck
    Es = 200000.0
    
    # 2. Wall Flexure / Axial (P-M Analysis)
    Pu_N = Pu_kN * 1e3
    phi_axial = 0.65
    phi_flex = 0.85
    
    c_low, c_high = 0.01 * Lw, 1.5 * Lw
    c_res = c_high
    Mn_res = 0.0
    
    for _ in range(30):
        c_mid = (c_low + c_high) / 2.0
        a = beta1 * c_mid
        a_clamped = min(a, Lw)
        
        Cc = sb * a_clamped * tw
        Mc = Cc * (Lw / 2.0 - a_clamped / 2.0)
        
        P_mid = Cc
        M_mid = Mc
        
        for f in fibers:
            dist_from_comp = Lw / 2.0 - f["x"]
            eps = ecu * (c_mid - dist_from_comp) / c_mid if c_mid > 0 else 0.0
            fs = max(min(eps * Es, fy), -fy)
            fc = sb if dist_from_comp <= a else 0.0
            Fs = f["As"] * (fs - fc)
            P_mid += Fs
            M_mid += Fs * f["x"]
            
        phi_calc = phi_flex
        if phi_calc * P_mid < Pu_N:
            c_low = c_mid
        else:
            c_high = c_mid
            c_res = c_mid
            Mn_res = abs(M_mid)
            
    phiMn_kNm = phi_flex * Mn_res * 1e-6
    dcr_flex = abs(Mu_kNm) / phiMn_kNm if phiMn_kNm > 0 else 999.0
    
    # 3. Wall In-plane Shear (KDS 14 20 72 §4.2)
    phi_v = 0.75
    d = 0.8 * Lw  # Effective shear depth
    
    # Concrete shear strength Vc
    hw_lw = Hw / Lw
    if hw_lw <= 2.0:
        alpha_c = 0.25 - 0.05 * hw_lw
    else:
        alpha_c = 0.17
    Vc = alpha_c * math.sqrt(fck) * tw * d * 1e-3  # kN
    
    # Horizontal steel shear strength Vs
    Av_h = 2 * REBAR_AREA.get(horiz_dia, 71.3)
    Vs = (Av_h * min(fy, 500.0) * d / horiz_spacing) * 1e-3 if horiz_spacing > 0 else 0.0  # kN
    
    # Max shear capacity limit
    Vn_max = 0.66 * math.sqrt(fck) * tw * d * 1e-3  # kN
    Vn = min(Vc + Vs, Vn_max)
    phiVn = phi_v * Vn
    dcr_shear = abs(Vu_kN) / phiVn if phiVn > 0 else 999.0
    
    # Minimum reinforcement ratios
    rho_v = Ast / Ag
    rho_h = (2 * REBAR_AREA.get(horiz_dia, 71.3)) / (tw * horiz_spacing)
    rho_min = 0.0025 if Vu_kN > 0.5 * phi_v * Vc else 0.0020
    
    # 4. Generate 20-point Wall P-M Interaction Curve (Envelope)
    pm_curve_points = []
    phiPn0_max = 0.80 * (0.85 * fck * (Ag - Ast) + fy * Ast) * 1e-3  # kN
    pm_curve_points.append({"phiPn": round(phiPn0_max * 1e3, 1), "phiMn": 0.0, "p_kN": round(phiPn0_max, 1), "m_kNm": 0.0})
    
    c_steps = [1.2 * Lw, 1.0 * Lw, 0.8 * Lw, 0.6 * Lw, 0.5 * Lw, 0.4 * Lw, 0.3 * Lw, 0.25 * Lw, 0.2 * Lw, 0.15 * Lw, 0.1 * Lw, 0.07 * Lw, 0.05 * Lw, 0.03 * Lw]
    for c_val in c_steps:
        a_val = min(beta1 * c_val, Lw)
        Cc_val = sb * a_val * tw
        Mc_val = Cc_val * (Lw / 2.0 - a_val / 2.0)
        P_val = Cc_val
        M_val = Mc_val
        for f in fibers:
            dist = Lw / 2.0 - f["x"]
            eps_val = ecu * (c_val - dist) / c_val if c_val > 0 else 0.0
            fs_val = max(min(eps_val * Es, fy), -fy)
            fc_val = sb if dist <= a_val else 0.0
            Fs_val = f["As"] * (fs_val - fc_val)
            P_val += Fs_val
            M_val += Fs_val * f["x"]
        
        phi_p_val = min(phiPn0_max * 1e3, phi_flex * P_val)
        phi_m_val = phi_flex * abs(M_val)
        pm_curve_points.append({
            "phiPn": round(phi_p_val, 1),
            "phiMn": round(phi_m_val, 1),
            "p_kN": round(phi_p_val / 1e3, 1),
            "m_kNm": round(phi_m_val / 1e6, 1)
        })
    
    T_pure_max = - phi_flex * Ast * fy
    pm_curve_points.append({"phiPn": round(T_pure_max, 1), "phiMn": 0.0, "p_kN": round(T_pure_max / 1e3, 1), "m_kNm": 0.0})
    
    pm_summary = {
        "combo": "1.2D + 1.6L (설계하중)",
        "Pu": Pu_kN * 1e3,
        "Mu": abs(Mu_kNm) * 1e6,
        "Mrθ": abs(Mu_kNm) * 1e6,
        "phiPn0": phiPn0_max * 1e3,
        "phiMnθ": phiMn_kNm * 1e6,
        "c_star": round(c_res, 1),
        "phi_f": phi_flex,
        "dcr": round(dcr_flex, 3),
        "pmCurve": pm_curve_points
    }
    
    governing_dcr = max(dcr_flex, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "dcr": round(governing_dcr, 3),
        "lw": Lw, "tw": tw, "hw": Hw, "L": Lw, "t": tw,
        "fck": fck, "fy": fy, "cover": cover, "vertDia": vert_dia, "vertSpacing": vert_spacing,
        "Pu": Pu_kN * 1e3, "Mu": abs(Mu_kNm) * 1e6, "Vu": abs(Vu_kN) * 1e3,
        "phi_Mn": phiMn_kNm * 1e6, "phi_Vn": phiVn * 1e3,
        "Pu_kN": Pu_kN, "Mu_kNm": Mu_kNm, "Vu_kN": Vu_kN,
        "phiMn_kNm": round(phiMn_kNm, 1), "phiVn_kN": round(phiVn, 1),
        "rho_v": rho_v, "rho_h": rho_h,
        "pm": pm_summary,
        "pmCurve": pm_curve_points,
        "flexure_axial": {
            "dcr": round(dcr_flex, 3),
            "phiMn_kNm": round(phiMn_kNm, 1),
            "Mu_kNm": Mu_kNm,
            "Pu_kN": Pu_kN,
            "c_mm": round(c_res, 1)
        },
        "in_plane_shear": {
            "dcr": round(dcr_shear, 3),
            "phiVn_kN": round(phiVn, 1),
            "Vu_kN": Vu_kN,
            "Vc_kN": round(Vc, 1),
            "Vs_kN": round(Vs, 1)
        },
        "rebar_ratios": {
            "rho_vertical_pct": round(rho_v * 100, 3),
            "rho_horizontal_pct": round(rho_h * 100, 3),
            "rho_min_pct": round(rho_min * 100, 2),
            "status": "OK" if rho_v >= rho_min and rho_h >= rho_min else "Warning"
        },
        "stiffness": {
            "Ig_mm4": round((tw * (Lw ** 3)) / 12.0, 1),
            "Ieff_factor": 0.70 if Pu_kN >= 0 else 0.35,
            "Ieff_mm4": round((0.70 if Pu_kN >= 0 else 0.35) * (tw * (Lw ** 3)) / 12.0, 1),
            "Ag_mm2": round(Ag, 1),
            "Aeff_factor": 0.50,
            "Aeff_mm2": round(0.50 * Ag, 1)
        },
        "section": {
            "Lw": Lw, "tw": tw, "Hw": Hw,
            "vert_rebar": f"D{vert_dia}@{int(vert_spacing)} ({vert_curtains} Curtains)",
            "horiz_rebar": f"D{horiz_dia}@{int(horiz_spacing)}"
        }
    }
