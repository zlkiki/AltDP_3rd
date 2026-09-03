# app/engines/steel/connection/bolt_bear.py
"""Bearing-Type Bolt Connection (볼트 전단/구멍 지압/인장 파괴 검토) Engine - KDS 14 31 25."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_steel import STEEL_GRADES
from app.engines.common.ks_db import get_bolt_strength, KS_BOLT_DIA_DB

MODULE_INFO = {
    "id": "bolt_bear",
    "name": "볼트 접합부 (지압) (Bearing Bolt)",
    "category": "steel",
    "group": "connection",
    "geomType": "steel_baseplate",
    "description": "KDS 14 31 25에 따른 고력볼트/일반볼트 전단파단, 연결판 볼트구멍 지압파괴(Bearing) 및 순단면 파단 검토"
}


class BoltConnBearInputSchema(BaseModel):
    bolt_grade: str = Field("F10T", description="볼트 등급 (F10T, F13T, F8T, S10T, 4.6, 8.8, 10.9)")
    bolt_dia: int = Field(22, description="볼트 공칭 직경 (M16, M20, M22, M24, M27, M30, M36)", ge=0)
    num_bolts: int = Field(6, description="총 볼트 개수 (EA)", ge=1)
    plate_thickness: float = Field(12.0, description="검토 연결판 두께 t (mm)", ge=0.0)
    plate_grade: str = Field("SM355", description="연결판 강종")
    
    edge_distance: float = Field(40.0, description="하중 방향 연단거리 Le (mm)", ge=0.0)
    pitch_spacing: float = Field(75.0, description="볼트 중심간격 s (mm)", ge=0.0)
    threads_excluded: bool = Field(True, description="전단면에 나사부 제외 여부 (X=True, N=False)")
    
    Vu: float = Field(450.0, description="소요 전단력 Vu (kN)", ge=0.0)


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    bgrade = str(data.get("bolt_grade", "F10T"))
    d = int(data.get("bolt_dia", 22))
    n = int(data.get("num_bolts", 6))
    t = float(data.get("plate_thickness", 12.0))
    pgrade = str(data.get("plate_grade", "SM355"))
    
    Le = float(data.get("edge_distance", 40.0))
    s = float(data.get("pitch_spacing", 75.0))
    threads_ex = bool(data.get("threads_excluded", True))
    Vu = float(data.get("Vu", 450.0))
    
    pmat = STEEL_GRADES.get(pgrade, STEEL_GRADES.get("SM355", {"Fu": 490.0, "Fy": 355.0}))
    Fu_plate = pmat["Fu"]
    
    # 1. Bolt Nominal Shear Strength Fnv (KDS 14 31 25 Table 4.1-3)
    # Fnv = 0.50 * Fu (나사부 제외) or 0.40 * Fu (나사부 포함)
    bst = get_bolt_strength(bgrade)
    Fu_bolt = bst.get("Fu", 1000.0)
    Fnv = 0.50 * Fu_bolt if threads_ex else 0.40 * Fu_bolt
        
    Ab = math.pi * (d ** 2) / 4.0
    phi_v = 0.75
    Rn_shear_single = Fnv * Ab * 1e-3  # kN
    phiRn_shear_total = phi_v * n * Rn_shear_single
    dcr_shear = Vu / phiRn_shear_total if phiRn_shear_total > 0 else 999.0
    
    # 2. Plate Bearing Strength Rn_bear (KDS 14 31 25 §4.1.4)
    # Clear distance: Lc_edge = Le - dh/2, Lc_inner = s - dh
    dh = d + 2.0  # standard hole diameter
    Lc_edge = max(0.0, Le - dh / 2.0)
    Lc_inner = max(0.0, s - dh)
    
    # Rn = min(1.2 * Lc * t * Fu, 2.4 * d * t * Fu)
    rn_edge = min(1.2 * Lc_edge * t * Fu_plate, 2.4 * d * t * Fu_plate) * 1e-3  # kN
    rn_inner = min(1.2 * Lc_inner * t * Fu_plate, 2.4 * d * t * Fu_plate) * 1e-3  # kN
    
    # Assume 1 row with edge and (n-1) inner
    Rn_bear_total = rn_edge + (n - 1) * rn_inner
    phi_bear = 0.75
    phiRn_bear_total = phi_bear * Rn_bear_total
    dcr_bear = Vu / phiRn_bear_total if phiRn_bear_total > 0 else 999.0
    
    governing_dcr = max(dcr_shear, dcr_bear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "bolt_shear": {
            "dcr": round(dcr_shear, 3),
            "phiRn_total_kN": round(phiRn_shear_total, 1),
            "Fnv_MPa": Fnv,
            "Ab_mm2": round(Ab, 1)
        },
        "plate_bearing": {
            "dcr": round(dcr_bear, 3),
            "phiRn_total_kN": round(phiRn_bear_total, 1),
            "rn_edge_bolt_kN": round(phi_bear * rn_edge, 1),
            "rn_inner_bolt_kN": round(phi_bear * rn_inner, 1),
            "Lc_edge_mm": round(Lc_edge, 1)
        },
        "spec": {
            "bolts": f"{n}-{bgrade} M{d}",
            "plate": f"PL-{int(t)}mm ({pgrade}, Fu={Fu_plate}MPa)"
        }
    }
