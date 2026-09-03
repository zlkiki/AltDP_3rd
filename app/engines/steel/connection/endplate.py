# app/engines/steel/connection/endplate.py
"""Bolted Moment End-Plate Connection Engine - KDS 14 31 25 / AISC DG4 & DG16."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES

MODULE_INFO = {
    "id": "endplate",
    "name": "엔드플레이트 접합부 (End Plate Connection)",
    "category": "steel",
    "group": "connection",
    "geomType": "steel_baseplate",
    "description": "KDS 14 31 및 AISC DG4에 따른 확장형 4볼트/8볼트 엔드플레이트 모멘트접합 항복선 메커니즘(Yield Line) 및 볼트 인장파단 검토"
}


class EndPlateInputSchema(BaseModel):
    bp: float = Field(250.0, description="엔드플레이트 폭 bp (mm)")
    tp: float = Field(25.0, description="엔드플레이트 두께 tp (mm)")
    plate_grade: str = Field("SM355", description="엔드플레이트 강종")
    
    beam_d: float = Field(500.0, description="접합 보 높이 d (mm)")
    beam_bf: float = Field(200.0, description="접합 보 플랜지 폭 bf (mm)")
    beam_tf: float = Field(16.0, description="접합 보 플랜지 두께 tf (mm)")
    
    bolt_dia: int = Field(24, description="고력볼트 직경 (mm, F10T)")
    bolt_pf: float = Field(50.0, description="보 플랜지~볼트 중심거리 pf (mm)")
    bolt_g: float = Field(100.0, description="인장 볼트 게이지 g (mm)")
    
    Mu: float = Field(320.0, description="설계 소요 모멘트 Mu (kN*m)")
    Vu: float = Field(120.0, description="설계 소요 전단력 Vu (kN)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    bp = float(data.get("bp", 250.0))
    tp = float(data.get("tp", 25.0))
    pgrade = str(data.get("plate_grade", "SM355"))
    
    d_beam = float(data.get("beam_d", 500.0))
    bf = float(data.get("beam_bf", 200.0))
    tf = float(data.get("beam_tf", 16.0))
    
    db = int(data.get("bolt_dia", 24))
    pf = float(data.get("bolt_pf", 50.0))
    g = float(data.get("bolt_g", 100.0))
    
    Mu = float(data.get("Mu", 320.0))  # kN*m
    Vu = float(data.get("Vu", 120.0))  # kN
    
    Fyp = STEEL_GRADES.get(pgrade, STEEL_GRADES["SM355"])["Fy"]
    
    # 1. Bolt Tensile Rupture Limit (4 tension bolts at tension flange)
    # Lever arm h0 ~ d_beam - tf/2
    h0 = d_beam - tf / 2.0
    T_req = (Mu * 1e6) / h0 * 1e-3  # Total tension force (kN)
    
    Ab = math.pi * (db ** 2) / 4.0
    Fnt = 620.0  # F10T nominal tensile stress (MPa)
    phi_t = 0.75
    phiBnt = phi_t * Fnt * Ab * 1e-3  # kN per bolt
    
    # 4 bolts carrying tension (kN * mm * 1e-3 = kN*m)
    phiMn_bolt = 4.0 * phiBnt * h0 * 1e-3  # kN*m
    dcr_bolt = Mu / phiMn_bolt if phiMn_bolt > 0 else 999.0
    
    # 2. End-Plate Yield-Line Bending Capacity (AISC DG4 Eq. 3.1)
    # Yield-line parameter Yp
    s = 0.5 * math.sqrt(bp * g)
    Yp = (bp / 2.0) * (h0 / pf + 1.0) + (2.0 / g) * (h0 + pf)
    
    phi_b = 0.90
    Mn_plate = phi_b * Fyp * (tp ** 2) * Yp * 1e-6  # kN*m
    dcr_plate = Mu / Mn_plate if Mn_plate > 0 else 999.0
    
    governing_dcr = max(dcr_bolt, dcr_plate)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "moment_capacity": {
            "dcr": round(governing_dcr, 3),
            "Mu_demand_kNm": Mu,
            "phiMn_bolt_kNm": round(phiMn_bolt, 1),
            "phiMn_plate_kNm": round(Mn_plate, 1),
            "governing_failure_mode": "End-Plate Bending" if Mn_plate < phiMn_bolt else "Bolt Tensile Rupture"
        },
        "plate_check": {
            "tp_provided_mm": tp,
            "yield_line_Yp": round(Yp, 1),
            "Fyp_MPa": Fyp
        },
        "bolt_tension": {
            "T_demand_total_kN": round(T_req, 1),
            "phiBnt_per_bolt_kN": round(phiBnt, 1),
            "tension_bolts": f"4-F10T M{db}"
        }
    }
