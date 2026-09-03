# app/engines/rc/footing/base.py
"""RC Spread Footing (독립기초 지내력, 휨, 1방향 보전단, 2방향 펀칭전단) Engine - KDS 14 20 70."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu

MODULE_INFO = {
    "id": "base",
    "name": "독립기초 (Single Footing)",
    "category": "rc",
    "group": "footing",
    "geomType": "rc_footing",
    "description": "KDS 14 20에 따른 독립 확대기초 편심 지내력, 저판 휨, 1방향 보전단 및 2방향 펀칭전단 검토"
}


class FootingInputSchema(BaseModel):
    B: float = Field(2500.0, description="기초 폭 X (mm)")
    L: float = Field(2500.0, description="기초 길이 Y (mm)")
    H: float = Field(700.0, description="기초 두께 (mm)")
    cx: float = Field(500.0, description="기둥 폭 cx (mm)")
    cy: float = Field(500.0, description="기둥 춤 cy (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(80.0, description="기초 하부 피복 (mm)")
    qa: float = Field(200.0, description="허용 지내력 (kN/m²)")
    
    # Service loads for soil pressure
    P_serv: float = Field(800.0, description="사용 축하중 (kN)")
    Mx_serv: float = Field(50.0, description="사용 모멘트 Mx (kN*m)")
    My_serv: float = Field(50.0, description="사용 모멘트 My (kN*m)")
    
    # Factored loads for concrete design
    Pu: float = Field(1100.0, description="설계 축하중 (kN)")
    Mux: float = Field(70.0, description="설계 모멘트 Mux (kN*m)")
    Muy: float = Field(70.0, description="설계 모멘트 Muy (kN*m)")
    
    bar_dia: int = Field(19, description="저판 주근 직경 (mm)")
    bar_spacing: float = Field(150.0, description="주근 간격 (mm)")


def calculate(data: Any) -> Dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    elif not isinstance(data, dict):
        data = dict(data)
        
    B = float(data.get("B", 2500.0))  # mm
    L = float(data.get("L", 2500.0))  # mm
    H = float(data.get("H", 700.0))   # mm
    cx = float(data.get("cx", 500.0))
    cy = float(data.get("cy", 500.0))
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 80.0))
    qa = float(data.get("qa", 200.0))  # kN/m²
    
    P_serv = float(data.get("P_serv", 800.0))
    Mx_serv = float(data.get("Mx_serv", 50.0))
    My_serv = float(data.get("My_serv", 50.0))
    
    Pu = float(data.get("Pu", 1100.0))
    Mux = float(data.get("Mux", 70.0))
    Muy = float(data.get("Muy", 70.0))
    
    bar_dia = int(data.get("bar_dia", 19))
    bar_spacing = float(data.get("bar_spacing", 150.0))
    
    # 1. Soil Bearing Pressure Check (Service)
    B_m = B * 1e-3
    L_m = L * 1e-3
    A_footing = B_m * L_m
    Zx = B_m * (L_m ** 2) / 6.0
    Zy = L_m * (B_m ** 2) / 6.0
    
    q_avg = P_serv / A_footing
    q_max = q_avg + abs(Mx_serv) / Zx + abs(My_serv) / Zy
    q_min = q_avg - abs(Mx_serv) / Zx - abs(My_serv) / Zy
    dcr_soil = q_max / qa if qa > 0 else 999.0
    
    # 2. Factored Soil Pressure (Ultimate)
    qu_max = Pu / A_footing + abs(Mux) / Zx + abs(Muy) / Zy
    qu_avg = Pu / A_footing
    
    d = H - cover - bar_dia / 2.0  # effective depth (mm)
    
    # 3. Flexure Check at Column Face (X & Y directions)
    lx = (B - cx) / 2.0  # cantilever overhang X (mm)
    ly = (L - cy) / 2.0  # cantilever overhang Y (mm)
    Mu_face_x = qu_max * (L * 1e-3) * ((lx * 1e-3) ** 2) / 2.0  # kN*m
    Mu_face_y = qu_max * (B * 1e-3) * ((ly * 1e-3) ** 2) / 2.0  # kN*m
    
    # Provided steel area in width L & width B
    num_bars_x = max(2, int(L / bar_spacing) + 1)
    num_bars_y = max(2, int(B / bar_spacing) + 1)
    As_prov_x = num_bars_x * REBAR_AREA.get(bar_dia, 286.5)
    As_prov_y = num_bars_y * REBAR_AREA.get(bar_dia, 286.5)
    
    # Minimum shrinkage and temperature reinforcement (KDS 14 20 50)
    As_min_x = 0.0018 * L * H
    As_min_y = 0.0018 * B * H
    
    sb = 0.85 * fck
    a_x = As_prov_x * fy / (sb * L)
    a_y = As_prov_y * fy / (sb * B)
    phi_flex = 0.85
    Mn_x = As_prov_x * fy * (d - a_x / 2.0) * 1e-6  # kN*m
    Mn_y = As_prov_y * fy * (d - a_y / 2.0) * 1e-6  # kN*m
    phiMn_x = phi_flex * Mn_x
    phiMn_y = phi_flex * Mn_y
    dcr_flex_x = Mu_face_x / phiMn_x if phiMn_x > 0 else 999.0
    dcr_flex_y = Mu_face_y / phiMn_y if phiMn_y > 0 else 999.0
    dcr_flex = max(dcr_flex_x, dcr_flex_y)
    
    # 4. One-way Shear Check (at distance d from column face)
    crit_dist_1way = lx - d
    phi_shear = 0.75
    if crit_dist_1way > 0:
        Vu_1way = qu_max * (L * 1e-3) * (crit_dist_1way * 1e-3)  # kN
        Vc_1way = (1.0 / 6.0) * math.sqrt(fck) * L * d * 1e-3  # kN
        phiVc_1way = phi_shear * Vc_1way
        dcr_1way = Vu_1way / phiVc_1way if phiVc_1way > 0 else 0.0
    else:
        Vu_1way = 0.0
        phiVc_1way = 1.0
        dcr_1way = 0.0
        
    # 5. Two-way Punching Shear Check (at d/2 from column perimeter)
    bo = 2.0 * ((cx + d) + (cy + d))  # punching perimeter (mm)
    Ap = (cx + d) * (cy + d) * 1e-6    # punching inner area (m²)
    Vu_punch = Pu - qu_avg * Ap        # factored punching force (kN)
    
    beta_c = max(cx, cy) / min(cx, cy)
    vc1 = (1.0 + 2.0 / beta_c) * (1.0 / 6.0) * math.sqrt(fck)
    vc2 = (40.0 * d / bo + 2.0) * (1.0 / 12.0) * math.sqrt(fck)
    vc3 = 0.35 * math.sqrt(fck)
    vc_punch = min(vc1, vc2, vc3)
    
    Vc_punch = vc_punch * bo * d * 1e-3  # kN
    phiVc_punch = phi_shear * Vc_punch
    dcr_punch = Vu_punch / phiVc_punch if phiVc_punch > 0 else 999.0
    
    governing_dcr = max(dcr_soil, dcr_flex, dcr_1way, dcr_punch)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "dcr": round(governing_dcr, 3),
        "Bx": B, "By": L, "B": B, "L": L, "H": H, "D": H, "h": H,
        "cx": cx, "cy": cy, "col_w": cx, "col_h": cy,
        "d": round(d, 1), "cover": cover, "fck": fck, "fy": fy,
        "qmax": round(q_max, 1), "qmin": round(q_min, 1), "qa": qa,
        "Pu": Pu, "P_serv": P_serv,
        "soil_bearing": {
            "dcr": round(dcr_soil, 3),
            "q_max": round(q_max, 1),
            "q_min": round(q_min, 1),
            "q_max_kPa": round(q_max, 1),
            "q_min_kPa": round(q_min, 1),
            "qa": qa,
            "qa_kPa": qa,
            "P_serv_kN": P_serv,
            "eccentricity_e_mm": round((abs(Mx_serv) / P_serv) * 1e3 if P_serv > 0 else 0, 1)
        },
        "flexure": {
            "dcr": round(dcr_flex, 3),
            "Mu_kNm": round(Mu_face_x, 1),
            "Mu_face_x_kNm": round(Mu_face_x, 1),
            "Mu_face_y_kNm": round(Mu_face_y, 1),
            "phiMn_kNm": round(phiMn_x, 1),
            "As_prov_mm2": round(As_prov_x, 1),
            "rebar_detail": f"D{bar_dia}@{int(bar_spacing)} (X: {num_bars_x}EA, Y: {num_bars_y}EA)"
        },
        "one_way_shear": {
            "dcr": round(dcr_1way, 3),
            "Vu_kN": round(Vu_1way, 1),
            "phiVc_kN": round(phiVc_1way, 1)
        },
        "punching_shear": {
            "dcr": round(dcr_punch, 3),
            "Vu_kN": round(Vu_punch, 1),
            "phiVc_kN": round(phiVc_punch, 1),
            "bo_mm": round(bo, 1)
        },
        "section": {
            "footing_size": f"{int(B)} x {int(L)} x {int(H)} mm",
            "column_size": f"{int(cx)} x {int(cy)} mm",
            "bottom_rebar": f"D{bar_dia}@{int(bar_spacing)}"
        }
    }
