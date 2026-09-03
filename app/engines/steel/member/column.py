# app/engines/steel/member/column.py
"""Steel Column (H형강/강관 강기둥 압축좌굴 및 P-M 상관식 H1-1) Engine - KDS 14 31 10 LRFD."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES, derive_steel_props

MODULE_INFO = {
    "id": "column",
    "name": "철골 기둥 (Steel Column)",
    "category": "steel",
    "group": "member",
    "geomType": "steel_h",
    "description": "KDS 14 31 LRFD에 따른 강기둥 휨/비틀림 압축좌굴강도(Pn) 및 축력-이축휨 P-M 상관식(H1-1) 검토"
}


class SteelColumnInputSchema(BaseModel):
    section_name: str = Field("H-350x350x12x19", description="KS 표준 강재 단면 일람")
    shape_type: str = Field("H_beam", description="단면 형태 (H_beam, box, pipe)")
    h: float = Field(350.0, description="단면 높이 h (mm)", ge=0.0)
    b: float = Field(350.0, description="단면 폭 b (mm)", ge=0.0)
    tw: float = Field(12.0, description="웨브 두께 tw (mm)", ge=0.0)
    tf: float = Field(19.0, description="플랜지 두께 tf (mm)", ge=0.0)
    r: float = Field(16.0, description="필릿 반경 r (mm)", ge=0.0)
    grade: str = Field("SM355", description="강종 (SS275, SM355, SHN355, SHN520 등)")
    
    L: float = Field(4000.0, description="부재 길이 L (mm)", ge=0.0)
    Kx: float = Field(1.0, description="X축 유효좌굴길이계수 Kx", ge=0.0)
    Ky: float = Field(1.0, description="Y축 유효좌굴길이계수 Ky", ge=0.0)
    
    Pu: float = Field(1800.0, description="설계 축압축력 Pu (kN)", ge=0.0)
    Mux: float = Field(120.0, description="설계 휨모멘트 Mux (kN*m)", ge=0.0)
    Muy: float = Field(50.0, description="설계 휨모멘트 Muy (kN*m)", ge=0.0)


def calc_fcr_steel(Fe: float, Fy: float) -> float:
    """Critical compressive stress Fcr (KDS 14 31 10 §4.2)"""
    if Fe <= 0:
        return 0.0
    if Fy / Fe <= 2.25:
        return (0.658 ** (Fy / Fe)) * Fy
    else:
        return 0.877 * Fe


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    stype = str(data.get("shape_type", "H_beam"))
    h = float(data.get("h", 350.0))
    b = float(data.get("b", 350.0))
    tw = float(data.get("tw", 12.0))
    tf = float(data.get("tf", 19.0))
    r = float(data.get("r", 16.0))
    grade = str(data.get("grade", "SM355"))
    
    L = float(data.get("L", 4000.0))
    Kx = float(data.get("Kx", 1.0))
    Ky = float(data.get("Ky", 1.0))
    
    Pu_kN = float(data.get("Pu", 1800.0))
    Mux_kNm = float(data.get("Mux", 120.0))
    Muy_kNm = float(data.get("Muy", 50.0))
    
    mat = STEEL_GRADES.get(grade, STEEL_GRADES["SM355"])
    Fy = mat["Fy"]
    E = mat["E"]
    G = mat["G"]
    
    sec_data = {"type": stype, "h": h, "b": b, "tw": tw, "tf": tf, "t": tw, "d": h, "r": r}
    sp = derive_steel_props(sec_data)
    Ag = sp["A"]
    
    # 1. Compressive Strength Pn (Flexural Buckling)
    Lx_eff = Kx * L
    Ly_eff = Ky * L
    
    Fe_x = ((math.pi ** 2) * E) / ((Lx_eff / sp["rx"]) ** 2) if sp["rx"] > 0 else 1.0
    Fe_y = ((math.pi ** 2) * E) / ((Ly_eff / sp["ry"]) ** 2) if sp["ry"] > 0 else 1.0
    
    Pn_x = calc_fcr_steel(Fe_x, Fy) * Ag
    Pn_y = calc_fcr_steel(Fe_y, Fy) * Ag
    Pn = min(Pn_x, Pn_y)
    
    # Torsional Buckling for H-beam
    if stype == "H_beam" and sp["J"] > 0:
        ro2 = (sp["Iz"] + sp["Iy"]) / Ag
        Fe_t = (((math.pi ** 2) * E * sp["Cw"]) / (Ly_eff ** 2) + G * sp["J"]) / (Ag * ro2) if ro2 > 0 else 1.0
        Pn_t = calc_fcr_steel(Fe_t, Fy) * Ag
        Pn = min(Pn, Pn_t)
        
    phi_c = 0.90
    phiPn_kN = phi_c * Pn * 1e-3
    
    # 2. Flexural Strength Mn
    phi_b = 0.90
    phiMnx_kNm = phi_b * (Fy * sp["Zx"]) * 1e-6
    phiMny_kNm = phi_b * (Fy * sp["Zy"]) * 1e-6
    
    # 3. P-M Interaction (KDS 14 31 10 H1-1a / H1-1b)
    p_ratio = Pu_kN / phiPn_kN if phiPn_kN > 0 else 999.0
    mx_term = abs(Mux_kNm) / phiMnx_kNm if phiMnx_kNm > 0 else 0.0
    my_term = abs(Muy_kNm) / phiMny_kNm if phiMny_kNm > 0 else 0.0
    
    if p_ratio >= 0.2:
        dcr_pm = p_ratio + (8.0 / 9.0) * (mx_term + my_term)
        formula_used = "H1-1a: Pr/Pc + 8/9(Mrx/Mcx + Mry/Mcy)"
    else:
        dcr_pm = p_ratio / 2.0 + (mx_term + my_term)
        formula_used = "H1-1b: Pr/(2Pc) + (Mrx/Mcx + Mry/Mcy)"
        
    # 4. Generate LRFD P-M Interaction Curve Points (Envelope)
    Mr_eq = math.hypot(Mux_kNm, Muy_kNm)
    phiMn_eq = math.hypot(phiMnx_kNm, phiMny_kNm) if math.hypot(phiMnx_kNm, phiMny_kNm) > 0 else 1.0
    
    pm_curve_points = []
    # Sweeping p_ratio from 1.0 down to 0.0
    p_steps = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1, 0.05, 0.0]
    for p_r in p_steps:
        p_val_kN = p_r * phiPn_kN
        if p_r >= 0.2:
            # p_r + 8/9 * m_r = 1.0  =>  m_r = (1.0 - p_r) * 9/8
            m_r = max(0.0, (1.0 - p_r) * (9.0 / 8.0))
        else:
            # p_r/2 + m_r = 1.0  =>  m_r = 1.0 - p_r / 2.0
            m_r = max(0.0, 1.0 - p_r / 2.0)
        m_val_kNm = m_r * phiMn_eq
        pm_curve_points.append({
            "phiPn": round(p_val_kN * 1e3, 1),
            "phiMn": round(m_val_kNm * 1e6, 1),
            "p_kN": round(p_val_kN, 1),
            "m_kNm": round(m_val_kNm, 1)
        })
        
    pm_summary = {
        "combo": "LRFD 계수하중",
        "Pu": Pu_kN * 1e3,
        "Mu": Mr_eq * 1e6,
        "Mrθ": Mr_eq * 1e6,
        "phiPn0": phiPn_kN * 1e3,
        "phiMnθ": phiMn_eq * 1e6,
        "dcr": round(dcr_pm, 3),
        "pmCurve": pm_curve_points
    }
    
    governing_dcr = dcr_pm
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "dcr": round(governing_dcr, 3),
        "H": h, "B": b, "tw": tw, "tf": tf, "grade": grade,
        "Pu": Pu_kN * 1e3, "Mu": Mr_eq * 1e6,
        "phi_Pn_max": phiPn_kN * 1e3, "phi_Mn": phiMn_eq * 1e6,
        "phiPn0_kN": round(phiPn_kN, 1), "phiMn_kNm": round(phiMn_eq, 1),
        "Pu_kN": Pu_kN, "Mux_kNm": Mux_kNm, "Muy_kNm": Muy_kNm,
        "pm": pm_summary,
        "pmCurve": pm_curve_points,
        "interaction": {
            "dcr": round(dcr_pm, 3),
            "formula": formula_used,
            "Pu_phiPn_ratio": round(p_ratio, 3),
            "Mux_phiMnx_ratio": round(mx_term, 3),
            "Muy_phiMny_ratio": round(my_term, 3)
        },
        "axial_compression": {
            "Pu_kN": Pu_kN,
            "phiPn_kN": round(phiPn_kN, 1),
            "slenderness_x": round(Lx_eff / sp["rx"], 1),
            "slenderness_y": round(Ly_eff / sp["ry"], 1)
        },
        "flexure": {
            "Mux_kNm": Mux_kNm,
            "phiMnx_kNm": round(phiMnx_kNm, 1),
            "Muy_kNm": Muy_kNm,
            "phiMny_kNm": round(phiMny_kNm, 1)
        },
        "section": {
            "shape": f"{stype} {int(h)}x{int(b)}x{int(tw)}x{int(tf)}",
            "grade": grade,
            "Ag_cm2": round(Ag * 1e-2, 1)
        }
    }
