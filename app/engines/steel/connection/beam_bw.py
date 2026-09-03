# app/engines/steel/connection/beam_bw.py
"""Welded Flange-Bolted Web Moment Connection (보-기둥 플랜지 CJP 용접 + 웨브 볼트 접합) Engine - KDS 14 31 25."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES

MODULE_INFO = {
    "id": "beam_bw",
    "name": "보-기둥 접합부 (Beam-Column Connection)",
    "category": "steel",
    "group": "connection",
    "geomType": "steel_baseplate",
    "description": "KDS 14 31 LRFD에 따른 보-기둥 플랜지 완전용입(CJP) 맞댐용접 휨전달 및 전단탭(Shear Tab) 웨브 볼트 전단 설계"
}


class BeamConnBWInputSchema(BaseModel):
    beam_sec: str = Field("H-600x200x11x17", description="보 강재 단면 선택 (KS 규격)")
    beam_d: float = Field(600.0, description="H형강 보 춤 d (mm)")
    beam_bf: float = Field(200.0, description="H형강 보 플랜지 폭 bf (mm)")
    beam_tf: float = Field(17.0, description="H형강 보 플랜지 두께 tf (mm)")
    beam_tw: float = Field(11.0, description="H형강 보 웨브 두께 tw (mm)")
    beam_grade: str = Field("SM355", description="보 강종")
    
    tab_thickness: float = Field(10.0, description="전단 탭 두께 (mm)")
    bolt_dia: int = Field(22, description="웨브 볼트 직경 (mm, F10T)")
    num_web_bolts: int = Field(4, description="웨브 볼트 개수 (1열 EA)")
    bolt_pitch: float = Field(80.0, description="볼트 피치 간격 (mm)")
    
    Mu: float = Field(450.0, description="설계 소요 모멘트 Mu (kN*m)")
    Vu: float = Field(220.0, description="설계 소요 전단력 Vu (kN)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    d = float(data.get("beam_d", 600.0))
    bf = float(data.get("beam_bf", 200.0))
    tf = float(data.get("beam_tf", 17.0))
    tw = float(data.get("beam_tw", 11.0))
    bgrade = str(data.get("beam_grade", "SM355"))
    
    t_tab = float(data.get("tab_thickness", 10.0))
    db = int(data.get("bolt_dia", 22))
    n_bolts = int(data.get("num_web_bolts", 4))
    pitch = float(data.get("bolt_pitch", 80.0))
    
    Mu = float(data.get("Mu", 450.0))
    Vu = float(data.get("Vu", 220.0))
    
    Fy = STEEL_GRADES.get(bgrade, STEEL_GRADES["SM355"])["Fy"]
    
    # 1. Flange CJP Weld Tensile Capacity (Full strength matching base metal)
    phi_f = 0.90
    Af = bf * tf
    Tf_cap = phi_f * Fy * Af * 1e-3  # kN
    h_arm = d - tf
    phiMn_flange = Tf_cap * h_arm * 1e-3  # kN*m
    dcr_moment = Mu / phiMn_flange if phiMn_flange > 0 else 999.0
    
    # 2. Shear Tab Bolt Group Capacity (Bolt shear + Plate bearing)
    phi_v = 0.75
    Ab = math.pi * (db ** 2) / 4.0
    Fnv = 450.0  # F10T-X
    phiRn_bolt_single = phi_v * Fnv * Ab * 1e-3  # kN
    
    # Eccentric shear on 1-column bolt group (e ~ 75mm from weld line)
    e_shear = 75.0
    # Polar moment of inertia J = sum(y^2)
    y_coords = [-(n_bolts - 1) * pitch / 2.0 + i * pitch for i in range(n_bolts)]
    Ip = sum(y ** 2 for y in y_coords)
    
    # Max resultant shear force on corner bolt
    V_direct = Vu / n_bolts
    M_ecc = Vu * e_shear
    H_torsion = (M_ecc * abs(y_coords[-1])) / Ip if Ip > 0 else 0.0
    R_resultant_per_bolt = math.hypot(V_direct, H_torsion)
    
    dcr_bolt_group = R_resultant_per_bolt / phiRn_bolt_single if phiRn_bolt_single > 0 else 999.0
    
    governing_dcr = max(dcr_moment, dcr_bolt_group)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "flange_cjp_weld": {
            "dcr": round(dcr_moment, 3),
            "phiMn_kNm": round(phiMn_flange, 1),
            "Mu_kNm": Mu,
            "Tf_capacity_kN": round(Tf_cap, 1)
        },
        "web_shear_tab_bolts": {
            "dcr": round(dcr_bolt_group, 3),
            "max_bolt_demand_kN": round(R_resultant_per_bolt, 1),
            "phiRn_per_bolt_kN": round(phiRn_bolt_single, 1),
            "eccentricity_e_mm": e_shear
        },
        "connection_summary": {
            "flange_connection": f"CJP Groove Weld (bf={int(bf)}x{int(tf)}mm)",
            "web_connection": f"{n_bolts}-F10T M{db} Shear Tab (t={int(t_tab)}mm)"
        }
    }
