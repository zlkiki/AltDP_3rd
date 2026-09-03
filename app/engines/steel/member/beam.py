# app/engines/steel/member/beam.py
"""Steel Beam (H형강 강보 휨, 전단, 횡지지 LTB 검토) Engine - KDS 14 31 10 LRFD."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES, derive_steel_props

MODULE_INFO = {
    "id": "beam",
    "name": "철골 보 (Steel Beam)",
    "category": "steel",
    "group": "member",
    "geomType": "steel_h",
    "description": "KDS 14 31 LRFD 기준에 따른 H형강 보 휨강도(Mn, LTB, FLB, WLB) 및 전단강도(Vn) 검토"
}


class SteelBeamInputSchema(BaseModel):
    section_name: str = Field("H-400x200x8x13", description="KS 표준 H형강 단면 일람")
    h: float = Field(400.0, description="H형강 높이 h (mm)", ge=0.0)
    b: float = Field(200.0, description="H형강 폭 b (mm)", ge=0.0)
    tw: float = Field(8.0, description="웨브 두께 tw (mm)", ge=0.0)
    tf: float = Field(13.0, description="플랜지 두께 tf (mm)", ge=0.0)
    r: float = Field(16.0, description="필릿 반경 r (mm)", ge=0.0)
    grade: str = Field("SM355", description="강종 (SS275, SM355, SHN355, SHN520 등)")
    Lb: float = Field(3000.0, description="비지지길이 Lb (mm)", ge=0.0)
    Cb: float = Field(1.0, description="횡비틀림좌굴 모멘트 구배계수 Cb", ge=0.0)
    
    Mu: float = Field(220.0, description="설계 휨모멘트 Mux (kN*m)", ge=0.0)
    Vu: float = Field(150.0, description="설계 전단력 Vuz (kN)", ge=0.0)


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    h = float(data.get("h", 400.0))
    b = float(data.get("b", 200.0))
    tw = float(data.get("tw", 8.0))
    tf = float(data.get("tf", 13.0))
    r = float(data.get("r", 16.0))
    grade = str(data.get("grade", "SM355"))
    Lb = float(data.get("Lb", 3000.0))
    Cb = float(data.get("Cb", 1.0))
    
    Mu_kNm = float(data.get("Mu", 220.0))
    Vu_kN = float(data.get("Vu", 150.0))
    
    mat = STEEL_GRADES.get(grade, STEEL_GRADES["SM355"])
    Fy = mat["Fy"]
    Fu = mat["Fu"]
    E = mat["E"]
    
    sec_data = {"type": "H_beam", "h": h, "b": b, "tw": tw, "tf": tf, "r": r}
    sp = derive_steel_props(sec_data)
    
    # 1. Flexural Strength Mn (Strong Axis)
    Mp = Fy * sp["Zx"]  # N*mm
    Sx = sp["Sx"]
    
    # Flange Local Buckling (FLB)
    lpf = 0.38 * math.sqrt(E / Fy)
    lrf = 1.0 * math.sqrt(E / Fy)
    if sp["lambda_f"] > lrf:
        kc = max(0.35, min(0.76, 4.0 / math.sqrt(sp["lambda_w"])))
        Mn_flb = 0.9 * E * kc * Sx / (sp["lambda_f"] ** 2)
    elif sp["lambda_f"] > lpf:
        Mn_flb = Mp - (Mp - 0.7 * Fy * Sx) * (sp["lambda_f"] - lpf) / (lrf - lpf)
    else:
        Mn_flb = Mp
        
    # Web Local Buckling (WLB)
    lpw = 3.76 * math.sqrt(E / Fy)
    lrw = 5.70 * math.sqrt(E / Fy)
    if sp["lambda_w"] > lrw:
        Rpg = max(0.0, 1.0 - (sp["aw"] / (1200.0 + 300.0 * sp["aw"])) * (sp["lambda_w"] - lrw))
        Mn_wlb = Rpg * Fy * Sx
    elif sp["lambda_w"] > lpw:
        Mn_wlb = Mp - (Mp - 0.7 * Fy * Sx) * (sp["lambda_w"] - lpw) / (lrw - lpw)
    else:
        Mn_wlb = Mp
        
    # Lateral-Torsional Buckling (LTB)
    Lp = 1.76 * sp["ry"] * math.sqrt(E / Fy)
    jTerm = sp["J"] / (Sx * sp["ho"]) if (Sx * sp["ho"]) > 0 else 0
    Lr = 1.95 * sp["rts"] * (E / (0.7 * Fy)) * math.sqrt(jTerm + math.sqrt(jTerm ** 2 + 6.76 * (0.7 * Fy / E) ** 2)) if sp["rts"] > 0 else 0
    
    if Lb <= Lp:
        Mn_ltb = Mp
    elif Lb <= Lr:
        Mn = Cb * (Mp - (Mp - 0.7 * Fy * Sx) * (Lb - Lp) / (Lr - Lp))
        Mn_ltb = min(Mn, Mp)
    else:
        Fcr = Cb * (math.pi ** 2) * E / ((Lb / sp["rts"]) ** 2) * math.sqrt(1.0 + 0.078 * jTerm * ((Lb / sp["rts"]) ** 2)) if sp["rts"] > 0 else 0
        Mn_ltb = min(Fcr * Sx, Mp)
        
    Mn = min(Mn_flb, Mn_wlb, Mn_ltb)
    phi_b = 0.90
    phiMn_kNm = phi_b * Mn * 1e-6
    dcr_flex = abs(Mu_kNm) / phiMn_kNm if phiMn_kNm > 0 else 999.0
    
    # 2. Shear Strength Vn (KDS 14 31 10 §4.3.3)
    Aw = h * tw
    kv = 5.34
    ratio_w = (h - 2 * tf) / tw
    lim1 = 1.10 * math.sqrt(kv * E / Fy)
    lim2 = 1.37 * math.sqrt(kv * E / Fy)
    
    if ratio_w <= lim1:
        Cv = 1.0
    elif ratio_w <= lim2:
        Cv = 1.10 * math.sqrt(kv * E / Fy) / ratio_w
    else:
        Cv = 1.51 * E * kv / ((ratio_w ** 2) * Fy)
        
    Vn = 0.6 * Fy * Aw * Cv
    phi_v = 0.90
    phiVn_kN = phi_v * Vn * 1e-3
    dcr_shear = abs(Vu_kN) / phiVn_kN if phiVn_kN > 0 else 999.0
    
    governing_dcr = max(dcr_flex, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "flexure": {
            "dcr": round(dcr_flex, 3),
            "phiMn_kNm": round(phiMn_kNm, 1),
            "Mu_kNm": Mu_kNm,
            "Mp_kNm": round(phi_b * Mp * 1e-6, 1),
            "Lp_mm": round(Lp, 0),
            "Lr_mm": round(Lr, 0),
            "Lb_mm": Lb,
            "controlling_mode": "Yielding" if Mn == Mp else ("LTB" if Mn == Mn_ltb else "FLB/WLB")
        },
        "shear": {
            "dcr": round(dcr_shear, 3),
            "phiVn_kN": round(phiVn_kN, 1),
            "Vu_kN": Vu_kN,
            "Cv": round(Cv, 3)
        },
        "section": {
            "name": f"H-{int(h)}x{int(b)}x{int(tw)}x{int(tf)}",
            "grade": grade,
            "Fy_MPa": Fy,
            "A_cm2": round(sp["A"] * 1e-2, 1),
            "Ix_cm4": round(sp["Iz"] * 1e-4, 1),
            "Iy_cm4": round(sp["Iy"] * 1e-4, 1)
        }
    }
