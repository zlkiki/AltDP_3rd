"""Indian Standard IS 800:2007 General Construction in Steel Design Adapter.

Implements Limit State Method (LSM) provisions:
- Partial safety factor gamma_m0 = 1.10, gamma_m1 = 1.25
- Section classification (Plastic, Compact, Semi-compact)
- Design bending strength Md
- Design shear strength Vd
- Design compressive strength Pd
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class IS800SteelDesignResult:
    """Design results according to IS 800:2007."""
    section_class: str        # "Plastic", "Compact", "Semi-compact", or "Slender"
    M_d: float                # Design bending strength (kN*m)
    V_d: float                # Design shear strength (kN)
    P_d: float                # Design compressive strength (kN)
    f_cd: float               # Design compressive stress (MPa)
    lambda_slenderness: float # Non-dimensional slenderness ratio
    dcr_flexure: float        # Mu / M_d
    dcr_shear: float          # Vu / V_d
    is_safe: bool             # Overall compliance


def check_is800_steel_beam(
    d_total: float,
    b_flange: float,
    tf: float,
    tw: float,
    r: float,
    Ag: float,
    Zp: float,
    Ze: float,
    ry: float,
    fy: float = 250.0,
    E: float = 200000.0,
    KL: float = 3000.0,
    Mu: float = 0.0,
    Vu: float = 0.0,
    gamma_m0: float = 1.10,
    gamma_m1: float = 1.25,
) -> IS800SteelDesignResult:
    """Perform IS 800:2007 flexural, shear, and compression verification.
    
    Args:
        d_total: Total depth of I/H section (mm)
        b_flange: Flange width (mm)
        tf: Flange thickness (mm)
        tw: Web thickness (mm)
        r: Root radius (mm)
        Ag: Gross area (mm2)
        Zp: Plastic section modulus (mm3)
        Ze: Elastic section modulus (mm3)
        ry: Radius of gyration about minor axis (mm)
        fy: Yield strength (MPa, default 250)
        E: Modulus of elasticity (MPa)
        KL: Effective length for compression (mm)
        Mu: Factored design moment (kN*m)
        Vu: Factored design shear force (kN)
        gamma_m0: Resistance factor (default 1.10)
        gamma_m1: Instability factor (default 1.25)
        
    Returns:
        IS800SteelDesignResult instance.
    """
    epsilon = math.sqrt(250.0 / max(1.0, fy))

    # Flange slenderness: b / tf (outstand: b_flange / 2)
    b_outstand = b_flange / 2.0
    flange_ratio = b_outstand / max(1.0, tf)

    # Web slenderness: d / tw
    d_web = d_total - 2.0 * tf - 2.0 * r
    web_ratio = d_web / max(1.0, tw)

    if flange_ratio <= 9.4 * epsilon and web_ratio <= 84.0 * epsilon:
        sec_class = "Plastic"
        beta_b = 1.0
        z_eff = Zp
    elif flange_ratio <= 10.5 * epsilon and web_ratio <= 105.0 * epsilon:
        sec_class = "Compact"
        beta_b = 1.0
        z_eff = Zp
    elif flange_ratio <= 15.7 * epsilon and web_ratio <= 126.0 * epsilon:
        sec_class = "Semi-compact"
        beta_b = Ze / Zp if Zp > 0 else 1.0
        z_eff = Ze
    else:
        sec_class = "Slender"
        beta_b = Ze / Zp if Zp > 0 else 1.0
        z_eff = 0.85 * Ze

    # Design bending strength Md (Cl. 8.2.1.2)
    m_d_nmm = (beta_b * z_eff * fy) / gamma_m0
    m_d = m_d_nmm / 1e6  # kN*m

    # Design shear strength Vd (Cl. 8.4.1)
    av = d_total * tw
    v_p_n = (av * fy) / math.sqrt(3.0)
    v_d = (v_p_n / gamma_m0) / 1000.0  # kN

    # Design compressive strength Pd (Cl. 7.1.2.1)
    kl_over_r = KL / max(1.0, ry)
    lambda_param = kl_over_r / (math.pi * math.sqrt(E / fy))
    alpha_imperfection = 0.34  # Buckling curve b for rolled I-sections
    phi = 0.5 * (1.0 + alpha_imperfection * (lambda_param - 0.2) + lambda_param ** 2)
    root_term = math.sqrt(max(0.0, phi ** 2 - lambda_param ** 2))
    f_cd = (fy / gamma_m0) / (phi + root_term)
    f_cd = min(fy / gamma_m0, max(1.0, f_cd))
    p_d = (Ag * f_cd) / 1000.0  # kN

    dcr_m = Mu / m_d if m_d > 0 else 999.0
    dcr_v = Vu / v_d if v_d > 0 else 999.0
    is_safe = (dcr_m <= 1.0) and (dcr_v <= 1.0)

    return IS800SteelDesignResult(
        section_class=sec_class,
        M_d=round(m_d, 3),
        V_d=round(v_d, 3),
        P_d=round(p_d, 3),
        f_cd=round(f_cd, 3),
        lambda_slenderness=round(lambda_param, 4),
        dcr_flexure=round(dcr_m, 4),
        dcr_shear=round(dcr_v, 4),
        is_safe=is_safe,
    )
