# app/engines/steel/connection/bolt.py
"""High-Strength Bolt Friction/Slip-Critical Connection Engine - KDS 14 31 25."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.ks_db import get_bolt_pretension, KS_BOLT_DIA_DB, KS_HIGH_BOLT_GRADE_DB

MODULE_INFO = {
    "id": "bolt",
    "name": "볼트 접합부 (마찰) (Friction Bolt)",
    "category": "steel",
    "group": "connection",
    "geomType": "steel_baseplate",
    "description": "KDS 14 31 25에 따른 F10T/F13T/F8T/S10T 고력볼트 마찰접합부 미끄럼 한계상태(Slip-Critical) 전단저항 검토"
}


class BoltConnInputSchema(BaseModel):
    bolt_grade: str = Field("F10T", description="고력볼트 등급 (F10T, F13T, F8T, S10T, A325, A490)")
    bolt_dia: int = Field(20, description="볼트 공칭 직경 (M16, M20, M22, M24, M27, M30, M36)", ge=0)
    num_bolts: int = Field(6, description="총 볼트 개수 (EA)", ge=1)
    num_shear_planes: int = Field(2, description="전단면 수 (1=단일전단, 2=이중전단)", ge=1)
    hole_type: str = Field("표준구멍", description="구멍 종류 (표준구멍, 대형구멍, 단슬롯, 장슬롯)")
    slip_coef_mu: float = Field(0.45, description="마찰계수 mu (블라스트 청소 미도장=0.45)", ge=0.0)
    
    Vu: float = Field(320.0, description="소요 전단력 Vu (kN)", ge=0.0)
    Tu: float = Field(0.0, description="소요 인장력 Tu (kN)", ge=0.0)


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    grade = str(data.get("bolt_grade", "F10T"))
    dia = int(data.get("bolt_dia", 20))
    n_bolts = int(data.get("num_bolts", 6))
    Ns = int(data.get("num_shear_planes", 2))
    hole_type = str(data.get("hole_type", "표준구멍"))
    mu = float(data.get("slip_coef_mu", 0.45))
    
    Vu = float(data.get("Vu", 320.0))
    Tu = float(data.get("Tu", 0.0))
    
    # 1. Slip Critical Resistance Rn per bolt (KDS 14 31 25 §4.1.3)
    # Rn = mu * Du * hf * Tb * Ns
    Du = 1.13  # Multiplier reflecting mean installed bolt tension
    hf = 1.0   # Factor for fillers
    Tb = get_bolt_pretension(grade, dia)  # kN
    
    # Hole factor phi_slip
    phi_slip = 1.0 if "표준" in hole_type else 0.85
    
    # Tension reduction factor ksc
    if Tu > 0:
        ksc = max(0.0, 1.0 - Tu / (1.13 * n_bolts * Tb))
    else:
        ksc = 1.0
        
    Rn_single = mu * Du * hf * Tb * Ns * ksc  # kN
    phiRn_total = phi_slip * (n_bolts * Rn_single)
    
    dcr_slip = Vu / phiRn_total if phiRn_total > 0 else 999.0
    status = "OK" if dcr_slip <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(dcr_slip, 3),
        "slip_resistance": {
            "dcr": round(dcr_slip, 3),
            "phiRn_total_kN": round(phiRn_total, 1),
            "Vu_demand_kN": Vu,
            "Rn_per_bolt_kN": round(Rn_single, 1),
            "pretension_Tb_kN": Tb,
            "tension_reduction_ksc": round(ksc, 3)
        },
        "connection_spec": {
            "bolts": f"{n_bolts}-{grade} M{dia}",
            "shear_planes": f"{Ns}-shear plane",
            "hole_type": hole_type,
            "mu_coefficient": mu
        }
    }
