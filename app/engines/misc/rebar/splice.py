# app/engines/misc/rebar/splice.py
"""Rebar Development Length & Lap Splice (철근 정착 및 겹침이음길이 산정) Engine - KDS 14 20 52."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY

MODULE_INFO = {
    "id": "splice",
    "name": "철근 정착·이음 (Bar Development & Splice)",
    "category": "misc",
    "group": "rebar",
    "geomType": "rc_rect",
    "description": "KDS 14 20 52에 따른 인장/압축 이형철근 정착길이(ld), 표준갈고리 정착길이(ldh) 및 A/B급 겹침이음길이 정밀 산정"
}


class RebarSpliceInputSchema(BaseModel):
    bar_dia: int = Field(22, description="철근 호칭 직경 db (mm)", ge=0)
    rebar_grade: str = Field("SD400", description="철근 강종 (SD300, SD400, SD500, SD600)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)", ge=0.0)
    
    is_top_bar: bool = Field(False, description="상부근 여부 (타설 깊이 300mm 초과, alpha=1.3)")
    is_epoxy: bool = Field(False, description="에폭시 도막 철근 여부 (beta=1.2 or 1.5)")
    is_lightweight: bool = Field(False, description="경량골재 콘크리트 여부 (lambda=0.85)")
    
    cover: float = Field(40.0, description="순 피복두께 (mm)", ge=0.0)
    clear_spacing: float = Field(50.0, description="철근 순간격 (mm)", ge=0.0)
    splice_class: str = Field("B", description="이음 등급 (A급=1.0*ld, B급=1.3*ld)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    db = int(data.get("bar_dia", 22))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    fck = float(data.get("fck", 24.0))
    
    is_top_bar = bool(data.get("is_top_bar", False))
    is_epoxy = bool(data.get("is_epoxy", False))
    is_lightweight = bool(data.get("is_lightweight", False))
    
    cover = float(data.get("cover", 40.0))
    clear_spacing = float(data.get("clear_spacing", 50.0))
    splice_class = str(data.get("splice_class", "B")).upper()
    
    # 1. Modification Factors (KDS 14 20 52 §4.1)
    alpha = 1.3 if is_top_bar else 1.0  # Reinforcement location factor
    beta = 1.2 if is_epoxy else 1.0     # Coating factor (if cover >= 3db and spacing >= 6db then 1.2 else 1.5)
    gamma = 0.8 if db <= 19 else 1.0   # Bar size factor
    lambda_val = 0.85 if is_lightweight else 1.0  # Lightweight concrete factor
    
    sqrt_fck = min(math.sqrt(fck), 8.4)  # Upper limit sqrt(fck) <= 8.4 MPa (70 MPa)
    
    # Confinement term (c + Ktr) / db limit <= 2.5
    # c: min of cover or clear_spacing / 2
    c_term = min(cover + db / 2.0, clear_spacing / 2.0 + db / 2.0)
    confinement_ratio = min(c_term / db, 2.5) if db > 0 else 2.5
    
    # 2. Tension Development Length ld (KDS 14 20 52 Eq. 4.1-1)
    # ld = (0.90 * fy / (lambda * sqrt(fck))) * (alpha * beta * gamma / (c+Ktr)/db) * db
    ld_raw = (0.90 * fy / (lambda_val * sqrt_fck)) * (alpha * beta * gamma / confinement_ratio) * db
    ld_tension = max(ld_raw, 300.0)  # Min 300mm
    
    # 3. Lap Splice Length (Tension Class A vs Class B)
    splice_factor = 1.0 if splice_class == "A" else 1.3
    splice_tension = max(splice_factor * ld_tension, 300.0)
    
    # 4. Compression Development Length ldc (KDS 14 20 52 §4.2)
    ldc1 = 0.25 * fy * db / sqrt_fck
    ldc2 = 0.043 * fy * db
    ld_comp = max(ldc1, ldc2, 200.0)
    splice_comp = max(0.072 * fy * db if fy > 400.0 else 0.072 * 400.0 * db, 300.0)
    
    # 5. Standard Hook Development Length ldh (KDS 14 20 52 §4.3)
    # ldh = (0.24 * beta * fy / (lambda * sqrt(fck))) * db
    ldh_raw = (0.24 * beta * fy / (lambda_val * sqrt_fck)) * db
    # Side cover >= 65mm & 90-deg hook tail cover >= 50mm -> 0.7 factor
    hook_factor = 0.7 if cover >= 65.0 else 1.0
    ldh = max(ldh_raw * hook_factor, 8.0 * db, 150.0)
    
    ld_t_res = int(math.ceil(ld_tension / 10.0) * 10)
    ls_t_res = int(math.ceil(splice_tension / 10.0) * 10)
    ld_c_res = int(math.ceil(ld_comp / 10.0) * 10)
    ls_c_res = int(math.ceil(splice_comp / 10.0) * 10)
    ldh_res = int(math.ceil(ldh / 10.0) * 10)
    
    splice_items = [
        {"label": "인장 정착길이 (ld)", "length_mm": ld_t_res, "code": "KDS 14 20 52 §4.1", "color": "#1976d2"},
        {"label": f"인장 이음길이 (ls, {splice_class}급)", "length_mm": ls_t_res, "code": "KDS 14 20 52 §4.5", "color": "#dc2626"},
        {"label": "압축 정착길이 (ldc)", "length_mm": ld_c_res, "code": "KDS 14 20 52 §4.2", "color": "#059669"},
        {"label": "압축 이음길이 (lsc)", "length_mm": ls_c_res, "code": "KDS 14 20 52 §4.5", "color": "#d97706"},
        {"label": "표준 갈고리 정착길이 (ldh)", "length_mm": ldh_res, "code": "KDS 14 20 52 §4.3", "color": "#7c3aed"}
    ]

    return {
        "status": "OK",
        "governing_dcr": 0.0,
        "dcr": 0.0,
        "db": db, "fck": fck, "fy": fy,
        "splice_chart": splice_items,
        "tension_development": {
            "ld_tension_mm": ld_t_res,
            "ld_raw_mm": round(ld_tension, 1),
            "confinement_ratio": round(confinement_ratio, 2)
        },
        "tension_splice": {
            "splice_class": splice_class,
            "splice_length_mm": ls_t_res,
            "factor": splice_factor
        },
        "compression_development": {
            "ld_comp_mm": ld_c_res,
            "splice_comp_mm": ls_c_res
        },
        "standard_hook": {
            "ldh_mm": ldh_res,
            "min_straight_lead_mm": int(8 * db)
        },
        "factors": {
            "alpha": alpha, "beta": beta, "gamma": gamma, "lambda": lambda_val,
            "sqrt_fck_clamped": round(sqrt_fck, 2)
        }
    }
