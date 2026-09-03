# app/engines/rc/column/base.py
"""RC Column (기본 기둥 3D P-M 상관곡면 및 이축 휨 검토) Engine - KDS 14 20 20."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import (
    REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu
)
from app.engines.common.section_integrator import (
    clip_polygon_sutherland_hodgman, compute_polygon_shoelace
)

MODULE_INFO = {
    "id": "base",
    "name": "기둥 (RC Column)",
    "category": "rc",
    "group": "column",
    "geomType": "rc_rect",
    "description": "KDS 14 20에 따른 직사각형 기둥의 3차원 P-Mx-My 상관곡면 및 이축 압축/휨 검토"
}


class ColumnInputSchema(BaseModel):
    b: float = Field(600.0, description="기둥 폭 (mm)")
    h: float = Field(600.0, description="기둥 춤 (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="주근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    tie_dia: int = Field(10, description="대근 직경 (mm)")
    main_dia: int = Field(25, description="주근 직경 (mm)")
    num_y: int = Field(4, description="Y방향 주근 개수 (양단 포함)")
    num_z: int = Field(4, description="Z방향 주근 개수 (양단 포함)")
    Pu: float = Field(1500.0, description="설계 축력 (kN)")
    Mux: float = Field(200.0, description="X축(강축) 휨모멘트 (kN*m)")
    Muy: float = Field(150.0, description="Y축(약축) 휨모멘트 (kN*m)")
    is_spiral: bool = Field(False, description="나선철근 여부 (True=나선, False=띠철근)")


def generate_rebar_fibers(b: float, h: float, cover: float, tie_dia: int, main_dia: int, num_y: int, num_z: int) -> List[Dict[str, float]]:
    """Generates coordinate fibers (y, z, As) for perimeter reinforcement."""
    fibers = []
    as_bar = REBAR_AREA.get(main_dia, 506.7)
    
    y_min = -h / 2.0 + cover + tie_dia + main_dia / 2.0
    y_max = h / 2.0 - cover - tie_dia - main_dia / 2.0
    z_min = -b / 2.0 + cover + tie_dia + main_dia / 2.0
    z_max = b / 2.0 - cover - tie_dia - main_dia / 2.0
    
    # 4 faces layout
    for iy in range(num_y):
        y = y_min + (y_max - y_min) * iy / (num_y - 1) if num_y > 1 else 0.0
        for iz in range(num_z):
            z = z_min + (z_max - z_min) * iz / (num_z - 1) if num_z > 1 else 0.0
            # Only perimeter bars
            if iy == 0 or iy == num_y - 1 or iz == 0 or iz == num_z - 1:
                fibers.append({"y": y, "z": z, "As": as_bar})
                
    return fibers


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    b = float(data.get("b", 600.0))
    h = float(data.get("h", 600.0))
    fck = float(data.get("fck", 27.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 40.0))
    tie_dia = int(data.get("tie_dia", 10))
    main_dia = int(data.get("main_dia", 25))
    num_y = int(data.get("num_y", 4))
    num_z = int(data.get("num_z", 4))
    
    Pu_kN = float(data.get("Pu", 1500.0))
    Mux_kNm = float(data.get("Mux", 200.0))
    Muy_kNm = float(data.get("Muy", 150.0))
    is_spiral = bool(data.get("is_spiral", False))
    
    Es = 200000.0
    phi_axial = 0.70 if is_spiral else 0.65
    phi_flex = 0.85
    pure_factor = 0.85 if is_spiral else 0.80
    
    beta1 = calc_beta1(fck)
    eta = calc_eta(fck)
    ecu = get_eps_cu(fck)
    sb = eta * 0.85 * fck
    
    fibers = generate_rebar_fibers(b, h, cover, tie_dia, main_dia, num_y, num_z)
    Ag = b * h
    Ast = sum(f["As"] for f in fibers)
    
    # Pure compression limit (P0)
    Pn0 = 0.85 * fck * (Ag - Ast) + Ast * fy
    phiPn0_max = phi_axial * pure_factor * Pn0 * 1e-3  # kN
    
    # Resultant moment & angle
    Mr_kNm = math.hypot(Mux_kNm, Muy_kNm)
    theta = math.atan2(Muy_kNm, Mux_kNm) if Mr_kNm > 1e-3 else 0.0
    cosT, sinT = math.cos(theta), math.sin(theta)
    
    # Section vertices
    vy = [-h / 2.0, h / 2.0, h / 2.0, -h / 2.0]
    vz = [-b / 2.0, -b / 2.0, b / 2.0, b / 2.0]
    dnExt = max(y * cosT + z * sinT for y, z in zip(vy, vz))
    dnTens = min(f["y"] * cosT + f["z"] * sinT for f in fibers)
    
    Pu_N = Pu_kN * 1e3
    
    # Bisection to find neutral axis depth c corresponding to Pu
    c_low, c_high = 0.005 * h, 3.0 * h
    c_res = c_high
    phi_res = phi_axial
    Mn_res = 0.0
    
    for _ in range(35):
        c_mid = (c_low + c_high) / 2.0
        thr = dnExt - beta1 * c_mid
        
        # Concrete stress integration
        cy, cz = clip_polygon_sutherland_hodgman(vy, vz, cosT, sinT, thr)
        area, sy, sz = compute_polygon_shoelace(cy, cz)
        
        P_mid = sb * area
        Muz_mid = sb * sy
        Muy_mid = sb * sz
        
        # Rebar forces
        for f in fibers:
            dn = f["y"] * cosT + f["z"] * sinT
            eps = ecu * (dn - dnExt + c_mid) / c_mid if c_mid > 0 else 0.0
            fs = max(min(eps * Es, fy), -fy)
            fc = sb if dn >= thr else 0.0
            Fs = f["As"] * (fs - fc)
            P_mid += Fs
            Muz_mid += Fs * f["y"]
            Muy_mid += Fs * f["z"]
            
        eps_t = ecu * (dnTens - dnExt + c_mid) / c_mid if c_mid > 0 else 0.005
        phi_calc = phi_flex if eps_t <= -0.005 else (phi_axial if eps_t >= -0.002 else phi_axial + (phi_flex - phi_axial) * (-eps_t - 0.002) / 0.003)
        
        if phi_calc * P_mid < Pu_N:
            c_low = c_mid
        else:
            c_high = c_mid
            c_res = c_mid
            phi_res = phi_calc
            Mn_res = abs(Muz_mid * cosT + Muy_mid * sinT)
            
    phiMn_kNm = phi_res * Mn_res * 1e-6
    dcr_pm = Mr_kNm / phiMn_kNm if phiMn_kNm > 0 else (Pu_kN / phiPn0_max if phiPn0_max > 0 else 999.0)
    
    # Generate 25 points P-M Interaction Curve (Envelope)
    pm_curve_points = []
    # 1. Pure compression point
    pm_curve_points.append({"phiPn": round(phiPn0_max * 1e3, 1), "phiMn": 0.0, "p_kN": round(phiPn0_max, 1), "m_kNm": 0.0})
    
    # 2. Intermediate points by sweeping neutral axis depth c
    c_steps = [1.5 * h, 1.2 * h, 1.0 * h, 0.85 * h, 0.70 * h, 0.60 * h, 0.50 * h, 0.40 * h, 0.35 * h, 0.30 * h, 0.25 * h, 0.20 * h, 0.15 * h, 0.10 * h, 0.07 * h, 0.05 * h]
    for c_val in c_steps:
        thr_i = dnExt - beta1 * c_val
        cy_i, cz_i = clip_polygon_sutherland_hodgman(vy, vz, cosT, sinT, thr_i)
        area_i, sy_i, sz_i = compute_polygon_shoelace(cy_i, cz_i)
        
        P_i = sb * area_i
        Muz_i = sb * sy_i
        Muy_i = sb * sz_i
        
        for f in fibers:
            dn_i = f["y"] * cosT + f["z"] * sinT
            eps_i = ecu * (dn_i - dnExt + c_val) / c_val if c_val > 0 else 0.0
            fs_i = max(min(eps_i * Es, fy), -fy)
            fc_i = sb if dn_i >= thr_i else 0.0
            Fs_i = f["As"] * (fs_i - fc_i)
            P_i += Fs_i
            Muz_i += Fs_i * f["y"]
            Muy_i += Fs_i * f["z"]
            
        eps_t_i = ecu * (dnTens - dnExt + c_val) / c_val if c_val > 0 else 0.005
        phi_i = phi_flex if eps_t_i <= -0.005 else (phi_axial if eps_t_i >= -0.002 else phi_axial + (phi_flex - phi_axial) * (-eps_t_i - 0.002) / 0.003)
        
        phiPn_i = min(phiPn0_max * 1e3, phi_i * P_i)
        phiMn_i = phi_i * abs(Muz_i * cosT + Muy_i * sinT)
        pm_curve_points.append({
            "phiPn": round(phiPn_i, 1),
            "phiMn": round(phiMn_i, 1),
            "p_kN": round(phiPn_i / 1e3, 1),
            "m_kNm": round(phiMn_i / 1e6, 1)
        })
        
    # 3. Pure tension point
    T_pure_max = - phi_flex * Ast * fy
    pm_curve_points.append({"phiPn": round(T_pure_max, 1), "phiMn": 0.0, "p_kN": round(T_pure_max / 1e3, 1), "m_kNm": 0.0})
    
    # Axial only check
    dcr_axial = Pu_kN / phiPn0_max if phiPn0_max > 0 else 999.0
    
    # Shear Check with Axial Load Effect (KDS 14 20 22 4.3)
    Vu_kN = float(data.get("Vu", 100.0))
    tie_spacing = float(data.get("tie_spacing", 200.0))
    tie_legs = int(data.get("tie_legs", 2))
    d_col = h - cover - tie_dia - main_dia / 2.0
    
    # Axial force effect on Vc: Nu > 0 (Compression, Pu > 0)
    Nu_N = Pu_kN * 1e3
    if Nu_N >= 0:
        vc_factor = 1.0 + min(Nu_N / (14.0 * Ag), 2.0)
    else:
        vc_factor = max(1.0 + 0.3 * Nu_N / Ag, 0.0)
        
    Vc_col = (1.0 / 6.0) * vc_factor * math.sqrt(fck) * b * d_col
    Av_col = tie_legs * REBAR_AREA.get(tie_dia, 71.33)
    fyt_col = min(fy, 500.0)
    Vs_col = (Av_col * fyt_col * d_col / tie_spacing) if tie_spacing > 0 else 0.0
    Vs_col_max = (5.0 / 6.0) * math.sqrt(fck) * b * d_col - Vc_col
    Vs_col = min(Vs_col, max(Vs_col_max, 0.0))
    Vn_col = Vc_col + Vs_col
    phiVn_col = 0.75 * Vn_col * 1e-3  # kN
    dcr_shear = abs(Vu_kN) / phiVn_col if phiVn_col > 0 else 999.0
    
    governing_dcr = max(dcr_pm, dcr_axial, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    pm_summary = {
        "combo": "1.2D + 1.6L (설계하중)",
        "Pu": Pu_kN * 1e3,
        "Muz": Mux_kNm * 1e6,
        "Muy": Muy_kNm * 1e6,
        "Mu": Mr_kNm * 1e6,
        "Mrθ": Mr_kNm * 1e6,
        "theta": theta,
        "phiPn0": phiPn0_max * 1e3,
        "phiMnθ": phiMn_kNm * 1e6,
        "c_star": round(c_res, 1),
        "eps_t": round(eps_t, 5),
        "phi_f": round(phi_res, 3),
        "dcr": round(governing_dcr, 3),
        "pmCurve": pm_curve_points
    }
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "b": b, "h": h, "cover": cover, "mainDia": main_dia, "tieDia": tie_dia,
        "nB": num_z, "nH": num_y, "fck": fck, "fy": fy, "Es": Es,
        "Pu": Pu_kN * 1e3, "Muz": Mux_kNm * 1e6, "Muy": Muy_kNm * 1e6, "Mu": Mr_kNm * 1e6,
        "phi_Pn_max": phiPn0_max * 1e3, "phi_Mn": phiMn_kNm * 1e6,
        "c": round(c_res, 1), "eps_t": round(eps_t, 5), "phi": round(phi_res, 3),
        "dcr_pm": round(dcr_pm, 3),
        "dcr_axial": round(dcr_axial, 3),
        "dcr_shear": round(dcr_shear, 3),
        "phiPn0_kN": round(phiPn0_max, 1),
        "phiMn_kNm": round(phiMn_kNm, 1),
        "phiVn_kN": round(phiVn_col, 1),
        "Vc_kN": round(Vc_col * 1e-3, 1),
        "Vs_kN": round(Vs_col * 1e-3, 1),
        "Pu_kN": Pu_kN,
        "Mux_kNm": Mux_kNm,
        "Muy_kNm": Muy_kNm,
        "Vu_kN": Vu_kN,
        "rebar_ratio_pct": round((Ast / Ag) * 100.0, 2),
        "num_total_bars": len(fibers),
        "pm": pm_summary,
        "pmCurve": pm_curve_points,
        "section": {
            "b": b, "h": h, "cover": cover,
            "main_rebar": f"{len(fibers)}-D{main_dia}",
            "tie_rebar": f"D{tie_dia}@{int(tie_spacing)}"
        }
    }
