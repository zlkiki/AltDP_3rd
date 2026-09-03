# app/engines/common/ks_db.py
"""
KS Standard Bolts & Structural Steels Single Source of Truth (SSOT) Database.
Ref: KS B 1010, KS B 0233, KS B 1016, KDS 14 31 10, KDS 14 31 25.
"""
from typing import Dict, Any, List

# ==============================================================================
# 1. KS Bolt Diameter & Geometric Properties (KS B 1010 / KS B 0233)
# ==============================================================================
KS_BOLT_DIA_DB: Dict[int, Dict[str, Any]] = {
    16: {
        "name": "M16",
        "dia": 16.0,
        "area_nominal": 201.1,      # Ab (mm2) = pi * d^2 / 4
        "area_tensile": 157.0,      # As (mm2) 유효인장단면적
        "hole_std": 18.0,           # 표준구멍직경 (mm)
        "edge_dist_min": 28.0,      # 최소연단거리 (mm)
        "pitch_min": 48.0           # 최소피치 3d (mm)
    },
    20: {
        "name": "M20",
        "dia": 20.0,
        "area_nominal": 314.2,
        "area_tensile": 245.0,
        "hole_std": 22.0,
        "edge_dist_min": 34.0,
        "pitch_min": 60.0
    },
    22: {
        "name": "M22",
        "dia": 22.0,
        "area_nominal": 380.1,
        "area_tensile": 303.0,
        "hole_std": 24.0,
        "edge_dist_min": 38.0,
        "pitch_min": 66.0
    },
    24: {
        "name": "M24",
        "dia": 24.0,
        "area_nominal": 452.4,
        "area_tensile": 353.0,
        "hole_std": 27.0,
        "edge_dist_min": 42.0,
        "pitch_min": 72.0
    },
    27: {
        "name": "M27",
        "dia": 27.0,
        "area_nominal": 572.6,
        "area_tensile": 459.0,
        "hole_std": 30.0,
        "edge_dist_min": 48.0,
        "pitch_min": 81.0
    },
    30: {
        "name": "M30",
        "dia": 30.0,
        "area_nominal": 706.9,
        "area_tensile": 561.0,
        "hole_std": 33.0,
        "edge_dist_min": 52.0,
        "pitch_min": 90.0
    },
    36: {
        "name": "M36",
        "dia": 36.0,
        "area_nominal": 1017.9,
        "area_tensile": 817.0,
        "hole_std": 39.0,
        "edge_dist_min": 64.0,
        "pitch_min": 108.0
    }
}

# ==============================================================================
# 2. KS High-Strength Bolt Grades (KS B 1010 / KDS 14 31 25 Table 4.1-1)
# ==============================================================================
KS_HIGH_BOLT_GRADE_DB: Dict[str, Dict[str, Any]] = {
    "F10T": {
        "grade": "F10T",
        "name": "F10T (KS B 1010 표준 고력볼트)",
        "Fy": 900.0,
        "Fu": 1000.0,
        # 설계볼트장력 To (kN) - KDS 14 31 25 Table 4.1-1
        "pretension_Tb": {16: 100.0, 20: 165.0, 22: 205.0, 24: 240.0, 27: 310.0, 30: 380.0, 36: 550.0}
    },
    "S10T": {
        "grade": "S10T",
        "name": "S10T (토크셔 T/S 볼트)",
        "Fy": 900.0,
        "Fu": 1000.0,
        "pretension_Tb": {16: 100.0, 20: 165.0, 22: 205.0, 24: 240.0, 27: 310.0, 30: 380.0, 36: 550.0}
    },
    "F13T": {
        "grade": "F13T",
        "name": "F13T (KS B 1010 초고력볼트)",
        "Fy": 1170.0,
        "Fu": 1300.0,
        "pretension_Tb": {20: 215.0, 22: 265.0, 24: 310.0, 27: 400.0, 30: 495.0}
    },
    "F8T": {
        "grade": "F8T",
        "name": "F8T (KS B 1010 8T 고력볼트)",
        "Fy": 640.0,
        "Fu": 800.0,
        "pretension_Tb": {16: 80.0, 20: 130.0, 22: 165.0, 24: 190.0, 27: 250.0, 30: 305.0, 36: 440.0}
    },
    "A325": {
        "grade": "A325",
        "name": "ASTM A325 (고력볼트)",
        "Fy": 630.0,
        "Fu": 830.0,
        "pretension_Tb": {16: 85.0, 20: 142.0, 22: 176.0, 24: 205.0, 27: 267.0, 30: 326.0}
    },
    "A490": {
        "grade": "A490",
        "name": "ASTM A490 (초고력볼트)",
        "Fy": 895.0,
        "Fu": 1035.0,
        "pretension_Tb": {16: 107.0, 20: 179.0, 22: 221.0, 24: 257.0, 27: 334.0, 30: 408.0}
    }
}

# ==============================================================================
# 3. KS Ordinary Hex Bolt Grades (KS B 0233)
# ==============================================================================
KS_ORDINARY_BOLT_GRADE_DB: Dict[str, Dict[str, Any]] = {
    "4.6": {"grade": "4.6", "name": "강도구분 4.6 (일반 육각볼트)", "Fy": 240.0, "Fu": 400.0},
    "4.8": {"grade": "4.8", "name": "강도구분 4.8 (일반 육각볼트)", "Fy": 320.0, "Fu": 400.0},
    "8.8": {"grade": "8.8", "name": "강도구분 8.8 (중강도 볼트)", "Fy": 640.0, "Fu": 800.0},
    "10.9": {"grade": "10.9", "name": "강도구분 10.9 (고강도 볼트)", "Fy": 900.0, "Fu": 1000.0}
}

# ==============================================================================
# 4. KS Anchor Bolt Grades (KS B 1016 / KDS 14 31 25)
# ==============================================================================
KS_ANCHOR_BOLT_GRADE_DB: Dict[str, Dict[str, Any]] = {
    "SS275": {"grade": "SS275", "name": "SS275 (일반구조용 앵커볼트)", "Fy": 275.0, "Fu": 410.0},
    "SM355": {"grade": "SM355", "name": "SM355 (고강도 구조용 앵커볼트)", "Fy": 355.0, "Fu": 490.0},
    "SS400": {"grade": "SS400", "name": "SS400 (구규격 앵커볼트)", "Fy": 235.0, "Fu": 400.0},
    "Gr.55": {"grade": "Gr.55", "name": "ASTM F1554 Gr.55 (고강도 앵커)", "Fy": 380.0, "Fu": 517.0},
    "Gr.105": {"grade": "Gr.105", "name": "ASTM F1554 Gr.105 (초고강도 앵커)", "Fy": 724.0, "Fu": 862.0}
}

# ==============================================================================
# 5. KS Structural Steel Material Grades (KDS 14 31 10 Table 4.1-1)
# ==============================================================================
KS_STEEL_GRADE_DB: Dict[str, Dict[str, Any]] = {
    # 일반구조용 압연강재 (SS)
    "SS235": {"grade": "SS235", "name": "SS235 (일반구조용 Fy=235)", "Fy": 235.0, "Fu": 360.0, "E": 205000.0, "G": 79000.0},
    "SS275": {"grade": "SS275", "name": "SS275 (일반구조용 Fy=275 - 표준)", "Fy": 275.0, "Fu": 410.0, "E": 205000.0, "G": 79000.0},
    "SS355": {"grade": "SS355", "name": "SS355 (일반구조용 Fy=355)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    # 용접구조용 압연강재 (SM)
    "SM275": {"grade": "SM275", "name": "SM275 (용접구조용 Fy=275)", "Fy": 275.0, "Fu": 410.0, "E": 205000.0, "G": 79000.0},
    "SM355": {"grade": "SM355", "name": "SM355 (용접구조용 Fy=355 - 표준)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    "SM460": {"grade": "SM460", "name": "SM460 (고강도 용접 Fy=460)", "Fy": 460.0, "Fu": 570.0, "E": 205000.0, "G": 79000.0},
    # 건축구조용 압연강재 (SN - 내진판재)
    "SN275": {"grade": "SN275", "name": "SN275 (건축구조용 내진 Fy=275)", "Fy": 275.0, "Fu": 400.0, "E": 205000.0, "G": 79000.0},
    "SN355": {"grade": "SN355", "name": "SN355 (건축구조용 내진 Fy=355)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    # 건축구조용 H형강 (SHN - 내진H형강)
    "SHN275": {"grade": "SHN275", "name": "SHN275 (H형강 내진 Fy=275)", "Fy": 275.0, "Fu": 410.0, "E": 205000.0, "G": 79000.0},
    "SHN355": {"grade": "SHN355", "name": "SHN355 (H형강 내진 Fy=355 - 표준)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    "SHN460": {"grade": "SHN460", "name": "SHN460 (H형강 고강도 내진 Fy=460)", "Fy": 460.0, "Fu": 570.0, "E": 205000.0, "G": 79000.0},
    "SHN520": {"grade": "SHN520", "name": "SHN520 (H형강 초고강도 내진 Fy=520)", "Fy": 520.0, "Fu": 630.0, "E": 205000.0, "G": 79000.0},
    # 구조용 각형강관 (SRT / SNRT)
    "SRT275": {"grade": "SRT275", "name": "SRT275 (구조용 각형강관 Fy=275)", "Fy": 275.0, "Fu": 410.0, "E": 205000.0, "G": 79000.0},
    "SRT355": {"grade": "SRT355", "name": "SRT355 (구조용 각형강관 Fy=355)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    "SNRT275": {"grade": "SNRT275", "name": "SNRT275 (건축구조용 각형강관 Fy=275)", "Fy": 275.0, "Fu": 400.0, "E": 205000.0, "G": 79000.0},
    "SNRT355": {"grade": "SNRT355", "name": "SNRT355 (건축구조용 각형강관 Fy=355)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    # 구조용 원형강관 (SNT)
    "SNT275": {"grade": "SNT275", "name": "SNT275 (건축구조용 원형강관 Fy=275)", "Fy": 275.0, "Fu": 400.0, "E": 205000.0, "G": 79000.0},
    "SNT355": {"grade": "SNT355", "name": "SNT355 (건축구조용 원형강관 Fy=355)", "Fy": 355.0, "Fu": 490.0, "E": 205000.0, "G": 79000.0},
    "SSC275": {"grade": "SSC275", "name": "SSC275 (냉간성형 경량형강 Fy=275)", "Fy": 275.0, "Fu": 400.0, "E": 205000.0, "G": 79000.0}
}


def get_bolt_pretension(grade: str, dia: int) -> float:
    """
    Returns design bolt pretension To (kN) according to KDS 14 31 25 Table 4.1-1.
    """
    g_upper = grade.strip().upper()
    g_info = KS_HIGH_BOLT_GRADE_DB.get(g_upper)
    if g_info and "pretension_Tb" in g_info:
        return g_info["pretension_Tb"].get(dia, 165.0)
    
    # Fallback to F10T table
    table_f10t = KS_HIGH_BOLT_GRADE_DB["F10T"]["pretension_Tb"]
    return table_f10t.get(dia, 165.0)


def get_bolt_strength(grade: str) -> Dict[str, float]:
    """
    Retrieves Fy and Fu for any bolt grade (High-strength, Ordinary, or Anchor).
    """
    g = grade.strip()
    if g in KS_HIGH_BOLT_GRADE_DB:
        return {"Fy": KS_HIGH_BOLT_GRADE_DB[g]["Fy"], "Fu": KS_HIGH_BOLT_GRADE_DB[g]["Fu"]}
    if g in KS_ORDINARY_BOLT_GRADE_DB:
        return {"Fy": KS_ORDINARY_BOLT_GRADE_DB[g]["Fy"], "Fu": KS_ORDINARY_BOLT_GRADE_DB[g]["Fu"]}
    if g in KS_ANCHOR_BOLT_GRADE_DB:
        return {"Fy": KS_ANCHOR_BOLT_GRADE_DB[g]["Fy"], "Fu": KS_ANCHOR_BOLT_GRADE_DB[g]["Fu"]}
    # Fallback
    return {"Fy": 900.0, "Fu": 1000.0}
