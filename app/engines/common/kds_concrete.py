# app/engines/common/kds_concrete.py
"""KDS 14 20 Concrete Structure Standard Utility & Rebar Properties."""
import math
from typing import Dict, Tuple

# KS D 3504 Nominal Rebar Properties (Yield Strengths)
REBAR_FY: Dict[str, float] = {
    "SD240": 240.0,
    "SD300": 300.0,
    "SD350": 350.0,
    "SD400": 400.0,
    "SD500": 500.0,
    "SD600": 600.0,
    "SD700": 700.0
}

# KS D 3504 Standard Rebar Diameters & Nominal Areas (mm²)
REBAR_AREA: Dict[int, float] = {
    10: 71.33,
    13: 126.7,
    16: 198.6,
    19: 286.5,
    22: 387.1,
    25: 506.7,
    29: 642.4,
    32: 794.2,
    35: 956.6,
    38: 1140.0,
    41: 1340.0,
    43: 1452.0,
    51: 2027.0,
    57: 2580.0
}

# KS D 3504 Standard Rebar Unit Masses (kg/m)
REBAR_UNIT_MASS: Dict[int, float] = {
    10: 0.560,
    13: 0.995,
    16: 1.56,
    19: 2.25,
    22: 3.04,
    25: 3.98,
    29: 5.04,
    32: 6.23,
    35: 7.51,
    38: 8.95,
    41: 10.36,
    51: 15.91
}

# Steel elastic modulus (MPa)
ES = 200000.0


def calc_alpha1(fck: float) -> float:
    """
    Equivalent rectangular stress block depth factor alpha_1 (KDS 14 20 20 : 2022).
    fck <= 40 MPa -> 0.80
    fck > 40 MPa -> max(0.80 - 0.002*(fck - 40), 0.66)
    """
    if fck <= 40.0:
        return 0.80
    return max(0.80 - 0.002 * (fck - 40.0), 0.66)


def calc_beta1(fck: float) -> float:
    """
    Equivalent rectangular stress block depth factor beta_1 (KDS 14 20 20 : 2022).
    fck <= 40 MPa -> 0.80 (2022 표준)
    fck > 40 MPa -> max(0.80 - 0.005*(fck - 40), 0.65)
    """
    if fck <= 40.0:
        return 0.80
    return max(0.80 - 0.005 * (fck - 40.0), 0.65)


def calc_eta(fck: float) -> float:
    """
    Stress block strength factor eta (KDS 14 20 20 : 2022).
    fck <= 40 MPa -> 1.00
    fck > 40 MPa -> max(1.00 - (fck - 40) / 200.0, 0.92)
    """
    if fck <= 40.0:
        return 1.00
    return max(1.00 - (fck - 40.0) / 200.0, 0.92)


def get_eps_cu(fck: float) -> float:
    """
    Ultimate concrete compressive strain eps_cu (KDS 14 20 20 : 2022).
    eps_cu = 0.0033 for fck <= 40 MPa
    eps_cu = max(0.0033 - 0.00003*(fck - 40), 0.0021) for fck > 40 MPa
    """
    if fck <= 40.0:
        return 0.0033
    return max(0.0033 - 0.00003 * (fck - 40.0), 0.0021)


def calc_fr(fck: float) -> float:
    """Modulus of rupture fr = 0.63 * sqrt(fck) (KDS 14 20 10 4.3.2)"""
    return 0.63 * math.sqrt(max(fck, 0.0))


def calc_Ec(fck: float) -> float:
    """Concrete elastic modulus Ec = 8500 * (fck + 4)^(1/3) [MPa] (KDS 14 20 10 4.3.1)"""
    return 8500.0 * math.pow(max(fck + 4.0, 0.0), 1.0 / 3.0)


def calc_phi_flexure(eps_t: float, fyk: float = 400.0, spiral: bool = False) -> float:
    """
    Strength reduction factor phi for flexure/axial tension according to tension strain eps_t (KDS 14 20 10).
    eps_ty = fyk / 200000.0
    Tension controlled (eps_t >= 2.5 * eps_ty): phi = 0.85
    Compression controlled (eps_t <= eps_ty): phi = 0.70 (spiral: 0.70, tied: 0.65)
    Transition zone: linear interpolation
    """
    eps_ty = fyk / ES
    phi_c = 0.70 if spiral else 0.65
    phi_t = 0.85
    
    if eps_t >= 2.5 * eps_ty:
        return phi_t
    if eps_t <= eps_ty:
        return phi_c
    
    return phi_c + (phi_t - phi_c) * (eps_t - eps_ty) / (1.5 * eps_ty)


def get_effective_depth(h: float, main_dia: float, cover: float, stir_dia: float) -> float:
    """Effective depth d = h - cover - stir_dia - main_dia / 2"""
    return h - cover - stir_dia - main_dia / 2.0

