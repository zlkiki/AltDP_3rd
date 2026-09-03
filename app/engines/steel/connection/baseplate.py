# app/engines/steel/connection/baseplate.py
"""Steel Column Base Plate (강기둥 주각부 베이스플레이트 및 앵커볼트 검토) Engine - KDS 14 31 25 / AISC DG1."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES
from app.engines.common.ks_db import get_bolt_strength, KS_BOLT_DIA_DB

MODULE_INFO = {
    "id": "baseplate",
    "name": "베이스 플레이트 (Base Plate)",
    "category": "steel",
    "group": "connection",
    "geomType": "steel_baseplate",
    "description": "KDS 14 31 및 AISC Design Guide 1에 따른 콘크리트 지압응력, 플레이트 휨두께(tp) 및 앵커볼트 인장력 검토"
}


class BasePlateInputSchema(BaseModel):
    col_sec: str = Field("H-300x300x10x15", description="강기둥 단면 선택 (KS 규격)")
    B: float = Field(500.0, description="베이스플레이트 폭 B (mm)", ge=0.0)
    N: float = Field(500.0, description="베이스플레이트 길이 N (mm)", ge=0.0)
    tp: float = Field(30.0, description="베이스플레이트 두께 tp (mm)", ge=0.0)
    
    col_d: float = Field(300.0, description="강기둥 높이 d (mm)", ge=0.0)
    col_bf: float = Field(300.0, description="강기둥 플랜지 폭 bf (mm)", ge=0.0)
    
    fck: float = Field(24.0, description="기초 콘크리트 압축강도 (MPa)", ge=0.0)
    plate_grade: str = Field("SM355", description="플레이트 강종")
    
    Pu: float = Field(800.0, description="설계 축압축력 (kN)", ge=0.0)
    Mu: float = Field(60.0, description="설계 휨모멘트 (kN*m)", ge=0.0)
    
    anchor_grade: str = Field("SS275", description="앵커볼트 강종 (SS275, SM355, SS400, Gr.55)")
    bolt_dia: int = Field(24, description="앵커볼트 공칭 직경 (M16, M20, M22, M24, M27, M30, M36)", ge=0)
    bolt_num: int = Field(4, description="앵커볼트 총 개수 (EA)", ge=1)
    bolt_dist: float = Field(400.0, description="인장측-압축측 볼트 간격 (mm)", ge=0.0)


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    B = float(data.get("B", 500.0))
    N = float(data.get("N", 500.0))
    tp = float(data.get("tp", 30.0))
    
    d = float(data.get("col_d", 300.0))
    bf = float(data.get("col_bf", 300.0))
    fck = float(data.get("fck", 24.0))
    grade = str(data.get("plate_grade", "SM355"))
    
    Pu = float(data.get("Pu", 800.0))  # kN
    Mu = float(data.get("Mu", 60.0))   # kN*m
    
    anchor_grade = str(data.get("anchor_grade", "SS275"))
    bolt_dia = int(data.get("bolt_dia", 24))
    bolt_num = int(data.get("bolt_num", 4))
    bolt_dist = float(data.get("bolt_dist", 400.0))
    
    Fy = STEEL_GRADES.get(grade, STEEL_GRADES.get("SM355", {"Fy": 355.0, "Fu": 490.0}))["Fy"]
    
    # 1. Concrete Bearing Strength (KDS 14 31 25 / AISC DG1)
    phi_c = 0.65
    fp_max = phi_c * 0.85 * fck  # MPa
    
    # Eccentricity
    e = (Mu / Pu) * 1e3 if Pu > 0 else 0.0  # mm
    e_crit = N / 6.0
    
    # Cantilever Overhangs (m, n, lambda*n')
    m = (N - 0.95 * d) / 2.0
    n = (B - 0.80 * bf) / 2.0
    n_prime = math.sqrt(d * bf) / 4.0
    
    if e <= e_crit and Pu > 0:
        # Small eccentricity: no anchor tension
        q_max = (Pu * 1e3) / (B * N) * (1.0 + 6.0 * e / N)  # MPa
        Tu_bolt = 0.0
    else:
        # Large eccentricity: bearing length Y calculation
        f = bolt_dist / 2.0
        # Quadratic to find bearing length Y
        # Y^2 - 2(N/2 + f) Y + 2(Pu*f + Mu*1e3) / (B * fp_max) = 0
        a_quad = 1.0
        b_quad = -2.0 * (N / 2.0 + f)
        c_quad = 2.0 * (Pu * 1e3 * f + Mu * 1e6) / (B * fp_max)
        disc = b_quad ** 2 - 4.0 * a_quad * c_quad
        
        if disc >= 0:
            Y = (-b_quad - math.sqrt(disc)) / (2.0 * a_quad)
        else:
            Y = N / 2.0
            
        q_max = fp_max
        Tu_total = (q_max * B * Y) * 1e-3 - Pu  # kN
        Tu_bolt = max(0.0, Tu_total / (bolt_num / 2.0))
        
    dcr_bearing = q_max / fp_max if fp_max > 0 else 999.0
    
    # 2. Base Plate Required Thickness tp_req (AISC DG1 Eq. 3.3.14)
    l_max = max(m, n, n_prime)
    phi_b = 0.90
    tp_req = l_max * math.sqrt((2.0 * q_max) / (phi_b * Fy))
    dcr_plate = tp_req / tp if tp > 0 else 999.0
    
    # 3. Anchor Bolt Tension (KDS 14 31 25 §4.1 / KS B 1016)
    phi_t = 0.75
    bst = get_bolt_strength(anchor_grade)
    Fub = bst.get("Fu", 410.0)  # Anchor bolt tensile strength (MPa)
    Fyb = bst.get("Fy", 275.0)
    Ab = math.pi * (bolt_dia ** 2) / 4.0
    phiTn_bolt = phi_t * 0.75 * Fub * Ab * 1e-3  # kN
    dcr_bolt = Tu_bolt / phiTn_bolt if phiTn_bolt > 0 else 0.0
    
    governing_dcr = max(dcr_bearing, dcr_plate, dcr_bolt)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "concrete_bearing": {
            "dcr": round(dcr_bearing, 3),
            "bearing_stress_MPa": round(q_max, 2),
            "fp_max_MPa": round(fp_max, 2)
        },
        "plate_bending": {
            "dcr": round(dcr_plate, 3),
            "tp_provided_mm": tp,
            "tp_required_mm": round(tp_req, 1),
            "cantilever_m_mm": round(m, 1),
            "cantilever_n_mm": round(n, 1)
        },
        "anchor_bolt": {
            "dcr": round(dcr_bolt, 3),
            "Tu_per_bolt_kN": round(Tu_bolt, 1),
            "phiTn_per_bolt_kN": round(phiTn_bolt, 1),
            "bolt_spec": f"{bolt_num}-{anchor_grade} M{bolt_dia} (Fu={int(Fub)}MPa)"
        },
        "section": {
            "plate": f"PL-{int(tp)}x{int(B)}x{int(N)} ({grade})",
            "column": f"H-{int(d)}x{int(bf)}"
        }
    }
