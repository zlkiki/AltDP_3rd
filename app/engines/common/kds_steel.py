# app/engines/common/kds_steel.py
"""KDS 14 31 Steel Structure Standard Utility & KS Section Properties."""
import math
from typing import Dict, Any

from app.engines.common.ks_db import KS_STEEL_GRADE_DB, KS_BOLT_DIA_DB, KS_HIGH_BOLT_GRADE_DB, get_bolt_pretension, get_bolt_strength

# KS Standard Structural Steel Grades (Yield Fy, Tensile Fu in MPa)
STEEL_GRADES: Dict[str, Dict[str, float]] = {
    k: {"Fy": v["Fy"], "Fu": v["Fu"], "E": v.get("E", 205000.0), "G": v.get("G", 79000.0)}
    for k, v in KS_STEEL_GRADE_DB.items()
}

# LRFD Resistance Factors (KDS 14 31 10 / 25)
PHI_STEEL: Dict[str, float] = {
    "flexure": 0.90,
    "shear": 0.90,
    "compression": 0.90,
    "tension_yield": 0.90,
    "tension_rupture": 0.75,
    "bearing_concrete": 0.65,
    "bolt_slip": 1.00,
    "bolt_shear": 0.75,
    "bolt_tension": 0.75,
}


def get_steel_grade_props(grade: str = "SM355") -> Dict[str, float]:
    """Retrieve steel material properties for a given grade."""
    return STEEL_GRADES.get(grade, STEEL_GRADES["SM355"])


def derive_steel_props(s: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derives section properties (A, Iz, Iy, Sx, Sy, Zx, Zy, rx, ry, J, Cw, rts, etc.)
    for H_beam, box, or pipe shapes.
    """
    stype = s.get("type", "H_beam")
    
    if stype == "H_beam":
        h = s.get("h", 400.0)
        b = s.get("b", 200.0)
        tw = s.get("tw", 8.0)
        tf = s.get("tf", 13.0)
        r = s.get("r", 16.0)
        
        A = 2.0 * b * tf + (h - 2.0 * tf) * tw + 0.8584 * (r ** 2)
        Iz = (b * (h ** 3) - (b - tw) * ((h - 2.0 * tf) ** 3)) / 12.0
        Iy = (2.0 * tf * (b ** 3) + (h - 2.0 * tf) * (tw ** 3)) / 12.0
        
        Sx = Iz / (h / 2.0)
        Sy = Iy / (b / 2.0)
        
        hw = h - 2.0 * tf
        Zx = b * tf * (h - tf) + tw * (hw ** 2) / 4.0
        Zy = (b ** 2) * tf / 2.0 + hw * (tw ** 2) / 4.0
        
        rx = math.sqrt(Iz / A) if A > 0 else 0.0
        ry = math.sqrt(Iy / A) if A > 0 else 0.0
        
        ho = h - tf
        Cw = (Iy * (ho ** 2)) / 4.0
        
        # Torsional constant J
        J = (2.0 * b * (tf ** 3) + (h - 2.0 * tf) * (tw ** 3)) / 3.0
        
        # Slenderness ratios
        lambda_f = (b / 2.0) / tf if tf > 0 else 0.0
        lambda_w = (h - 2.0 * tf - 2.0 * r) / tw if tw > 0 else 0.0
        aw = (hw * tw) / (b * tf) if (b * tf) > 0 else 0.0
        
        # Effective radius of gyration rts
        rts = math.sqrt(math.sqrt(Iy * Cw) / Sx) if Sx > 0 else ry
        
        return {
            "type": "H_beam", "A": A, "Iz": Iz, "Iy": Iy, "Sx": Sx, "Sy": Sy, "Zx": Zx, "Zy": Zy,
            "rx": rx, "ry": ry, "Cw": Cw, "ho": ho, "rts": rts, "J": J, "r": r,
            "lambda_f": lambda_f, "lambda_w": lambda_w, "aw": aw, "hasLTB": True
        }
        
    elif stype == "box":
        h = s.get("h", 300.0)
        b = s.get("b", 300.0)
        t = s.get("t", 12.0)
        
        hi = h - 2.0 * t
        bi = b - 2.0 * t
        
        A = b * h - bi * hi
        Iz = (b * (h ** 3) - bi * (hi ** 3)) / 12.0
        Iy = (h * (b ** 3) - hi * (bi ** 3)) / 12.0
        
        Sx = Iz / (h / 2.0)
        Sy = Iy / (b / 2.0)
        
        Zx = (b * (h ** 2) - bi * (hi ** 2)) / 4.0
        Zy = (h * (b ** 2) - hi * (bi ** 2)) / 4.0
        
        rx = math.sqrt(Iz / A) if A > 0 else 0.0
        ry = math.sqrt(Iy / A) if A > 0 else 0.0
        
        J = 4.0 * ((b - t) ** 2) * ((h - t) ** 2) * t / (2.0 * (b + h - 2.0 * t))
        
        lambda_f = (b - 3.0 * t) / t if t > 0 else 0.0
        lambda_w = (h - 3.0 * t) / t if t > 0 else 0.0
        
        return {
            "type": "box", "A": A, "Iz": Iz, "Iy": Iy, "Sx": Sx, "Sy": Sy, "Zx": Zx, "Zy": Zy,
            "rx": rx, "ry": ry, "Cw": 0.0, "ho": 0.0, "rts": 0.0, "J": J, "r": 0.0,
            "lambda_f": lambda_f, "lambda_w": lambda_w, "aw": 0.0, "hasLTB": False
        }
        
    else:  # pipe
        D = s.get("d", 200.0)
        t = s.get("t", 8.0)
        
        Di = D - 2.0 * t
        PI = math.pi
        
        A = PI * (D * D - Di * Di) / 4.0
        Iz = PI * (D**4 - Di**4) / 64.0
        Iy = Iz
        
        Sx = Iz / (D / 2.0)
        Sy = Sx
        
        Zx = (D**3 - Di**3) / 6.0
        Zy = Zx
        
        rx = math.sqrt(Iz / A) if A > 0 else 0.0
        ry = rx
        
        J = 2.0 * Iz
        
        lambda_f = D / t if t > 0 else 0.0
        lambda_w = D / t if t > 0 else 0.0
        
        return {
            "type": "pipe", "A": A, "Iz": Iz, "Iy": Iy, "Sx": Sx, "Sy": Sy, "Zx": Zx, "Zy": Zy,
            "rx": rx, "ry": ry, "Cw": 0.0, "ho": 0.0, "rts": 0.0, "J": J, "r": 0.0,
            "lambda_f": lambda_f, "lambda_w": lambda_w, "aw": 0.0, "hasLTB": False
        }
