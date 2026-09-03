# app/engines/steel/connection/bolt_tens.py
"""Bolted Tension Connection & Prying Action (T-Stub 인장 지렛대 작용 검토) Engine - KDS 14 31 25."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES
from app.engines.common.ks_db import get_bolt_strength, KS_BOLT_DIA_DB

MODULE_INFO = {
    "id": "bolt_tens",
    "name": "볼트 접합부 (인장·지렛대) (Prying Action)",
    "category": "steel",
    "group": "connection",
    "geomType": "steel_baseplate",
    "description": "KDS 14 31 25 및 AISC Manual에 따른 T-Stub/플랜지 인장 접합부의 지렛대 작용(Prying Action) 추가 볼트 인장력(q) 및 플랜지 휨 두께 검토"
}


class BoltTensConnInputSchema(BaseModel):
    flange_width_b: float = Field(200.0, description="T-Stub 플랜지 폭 b (mm)", ge=0.0)
    flange_thick_tf: float = Field(20.0, description="T-Stub 플랜지 두께 tf (mm)", ge=0.0)
    plate_grade: str = Field("SM355", description="플랜지 강종")
    
    bolt_grade: str = Field("F10T", description="볼트 등급 (F10T, F13T, F8T, 8.8, 10.9)")
    bolt_dia: int = Field(22, description="볼트 공칭 직경 (M16, M20, M22, M24, M27, M30, M36)", ge=0)
    num_tension_bolts: int = Field(2, description="인장 볼트 개수 (EA)", ge=1)
    
    dist_a: float = Field(40.0, description="볼트 중심~플랜지 끝단 거리 a (mm)", ge=0.0)
    dist_b: float = Field(45.0, description="볼트 중심~웨브 페이스 거리 b (mm)", ge=0.0)
    p_length: float = Field(100.0, description="볼트 1개당 유효 분담 길이 p (mm)", ge=0.0)
    
    Tu_total: float = Field(240.0, description="총 소요 인장력 Tu (kN)", ge=0.0)


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    b = float(data.get("flange_width_b", 200.0))
    tf = float(data.get("flange_thick_tf", 20.0))
    grade = str(data.get("plate_grade", "SM355"))
    bgrade = str(data.get("bolt_grade", "F10T"))
    
    db = int(data.get("bolt_dia", 22))
    n_bolts = int(data.get("num_tension_bolts", 2))
    
    a = float(data.get("dist_a", 40.0))
    dist_b = float(data.get("dist_b", 45.0))
    p = float(data.get("p_length", 100.0))
    
    Tu_total = float(data.get("Tu_total", 240.0))
    T_per_bolt = Tu_total / n_bolts if n_bolts > 0 else Tu_total
    
    Fy = STEEL_GRADES.get(grade, STEEL_GRADES.get("SM355", {"Fy": 355.0, "Fu": 490.0}))["Fy"]
    
    # 1. Bolt Available Tensile Strength B (KDS 14 31 25 Table 4.1-3: Fnt = 0.75 * Fu)
    phi_t = 0.75
    Ab = math.pi * (db ** 2) / 4.0
    bst = get_bolt_strength(bgrade)
    Fu_bolt = bst.get("Fu", 1000.0)
    Fnt = 0.75 * Fu_bolt  # MPa
    B_cap = phi_t * Fnt * Ab * 1e-3  # kN per bolt
    
    # 2. Prying Action Parameters (AISC Manual Part 9)
    dh = db + 2.0  # Hole diameter
    b_prime = dist_b - db / 2.0
    a_prime = min(a + db / 2.0, 1.25 * dist_b + db / 2.0)
    
    rho = b_prime / a_prime
    delta = 1.0 - dh / p if p > 0 else 0.5
    
    # Required thickness for no prying action tc
    tc = math.sqrt((4.0 * B_cap * 1e3 * b_prime) / (0.90 * Fy * p)) if (0.90 * Fy * p) > 0 else tf
    
    # Alpha prime parameter
    term1 = (1.0 / delta) * ((tc / tf) ** 2 - 1.0) if tf > 0 else 0.0
    term2 = (T_per_bolt / B_cap) if B_cap > 0 else 1.0
    alpha_prime = (1.0 / delta) * ((term2 / ((tf / tc) ** 2)) - 1.0) if tf > 0 and tc > 0 else 0.0
    
    if alpha_prime < 0:
        q_prying = 0.0
        T_total_with_prying = T_per_bolt
        prying_mode = "No Prying Action (Flange is thick)"
    elif alpha_prime <= 1.0:
        q_prying = B_cap * (alpha_prime * delta * rho) / (1.0 + alpha_prime * delta * rho)
        T_total_with_prying = T_per_bolt + q_prying
        prying_mode = "Moderate Prying Action"
    else:
        q_prying = B_cap * (delta * rho) / (1.0 + delta * rho)
        T_total_with_prying = T_per_bolt + q_prying
        prying_mode = "Severe Prying Action (Flange yielding governs)"
        
    dcr_bolt_with_prying = T_total_with_prying / B_cap if B_cap > 0 else 999.0
    dcr_flange_thick = tc / tf if tf > 0 else 999.0
    
    governing_dcr = max(dcr_bolt_with_prying, T_per_bolt / B_cap)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "bolt_tension_with_prying": {
            "dcr": round(dcr_bolt_with_prying, 3),
            "T_direct_per_bolt_kN": round(T_per_bolt, 1),
            "Q_prying_force_kN": round(q_prying, 1),
            "T_total_per_bolt_kN": round(T_total_with_prying, 1),
            "phiBnt_capacity_kN": round(B_cap, 1),
            "prying_regime": prying_mode
        },
        "flange_thickness_check": {
            "tf_provided_mm": tf,
            "tc_required_for_no_prying_mm": round(tc, 1),
            "alpha_prime": round(alpha_prime, 3)
        },
        "spec": {
            "bolts": f"{n_bolts}-F10T M{db}",
            "flange": f"PL-{int(tf)}mm ({grade})"
        }
    }
