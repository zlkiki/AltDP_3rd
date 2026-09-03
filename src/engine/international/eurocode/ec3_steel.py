"""Eurocode 3 (EN 1993-1-1:2005) Steel Member Design Adapter.

Implements Eurocode 3 member design checks:
- Section classification (Class 1, 2, 3, 4)
- Cross-section flexural and shear resistance (Mc,Rd, Vc,Rd)
- Lateral-torsional buckling resistance (Mb,Rd)
- Axial compression buckling resistance (Nb,Rd)
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class EC3SteelDesignResult:
    """Design results according to Eurocode 3."""
    section_class: int        # 1, 2, 3, or 4
    M_c_Rd: float             # Section flexural resistance (kN*m)
    M_b_Rd: float             # LTB flexural resistance (kN*m)
    V_pl_Rd: float            # Shear resistance (kN)
    N_b_Rd: float             # Compression buckling resistance (kN)
    chi_LT: float             # LTB reduction factor
    chi_N: float              # Column buckling reduction factor
    dcr_flexure: float        # M_Ed / M_b_Rd
    dcr_shear: float          # V_Ed / V_pl_Rd
    is_safe: bool             # Overall compliance


def check_ec3_steel_beam(
    h: float,
    b: float,
    tw: float,
    tf: float,
    r: float,
    A: float,
    Wpl_y: float,
    Wel_y: float,
    Iz: float,
    It: float,
    Iw: float,
    fy: float = 275.0,
    E: float = 210000.0,
    G: float = 81000.0,
    Lcr: float = 4000.0,
    M_Ed: float = 0.0,
    V_Ed: float = 0.0,
    gamma_M0: float = 1.00,
    gamma_M1: float = 1.00,
    C1: float = 1.0,
    Mu: Optional[float] = None,
    Vu: Optional[float] = None,
) -> EC3SteelDesignResult:
    """Perform Eurocode 3 flexural and shear verification for an I/H section beam.
    Args:
        h: Total section height (mm)
        b: Flange width (mm)
        tw: Web thickness (mm)
        tf: Flange thickness (mm)
        r: Root fillet radius (mm)
        A: Gross cross-sectional area (mm2)
        Wpl_y: Plastic section modulus major axis (mm3)
        Wel_y: Elastic section modulus major axis (mm3)
        Iz: Minor axis second moment of area (mm4)
        It: Torsional constant (mm4)
        Iw: Warping constant (mm6)
        fy: Yield strength (MPa)
        E: Young's modulus (MPa, default 210,000)
        G: Shear modulus (MPa, default 81,000)
        Lcr: Effective buckling length for LTB (mm)
        M_Ed: Factored design bending moment (kN*m)
        V_Ed: Factored design shear force (kN)
        gamma_M0: Partial factor for cross-section resistance (default 1.00)
        gamma_M1: Partial factor for member instability (default 1.00)
        C1: Moment diagram factor for LTB (default 1.0)
        
    Returns:
        EC3SteelDesignResult instance.
    """
    if Mu is not None:
        M_Ed = Mu
    if Vu is not None:
        V_Ed = Vu

    epsilon = math.sqrt(235.0 / max(1.0, fy))
    
    # Flange slenderness: c / tf where c = (b - tw - 2*r) / 2
    c_flange = (b - tw - 2.0 * r) / 2.0
    flange_ratio = c_flange / max(1.0, tf)

    # Web slenderness: d / tw where d = h - 2*tf - 2*r
    d_web = h - 2.0 * tf - 2.0 * r
    web_ratio = d_web / max(1.0, tw)

    # Classification
    if flange_ratio <= 9.0 * epsilon and web_ratio <= 72.0 * epsilon:
        sec_class = 1
    elif flange_ratio <= 10.0 * epsilon and web_ratio <= 83.0 * epsilon:
        sec_class = 2
    elif flange_ratio <= 14.0 * epsilon and web_ratio <= 124.0 * epsilon:
        sec_class = 3
    else:
        sec_class = 4

    # Major axis flexural resistance Mc,Rd
    if sec_class in (1, 2):
        wy = Wpl_y
    elif sec_class == 3:
        wy = Wel_y
    else:
        wy = 0.85 * Wel_y  # Effective section modulus approximation

    m_c_rd = (wy * fy) / gamma_M0 / 1e6  # kN*m

    # Shear resistance Vpl,Rd
    hw = h - 2.0 * tf
    av = max(hw * tw, A - 2.0 * b * tf + (tw + 2.0 * r) * tf)
    v_pl_rd = (av * (fy / math.sqrt(3.0))) / gamma_M0 / 1000.0  # kN

    # Elastic critical moment for LTB: Mcr
    pi_sq = math.pi ** 2
    term1 = C1 * (pi_sq * E * Iz) / (Lcr ** 2)
    term2 = (Iw / max(1.0, Iz)) + ((Lcr ** 2) * G * It) / (pi_sq * E * max(1.0, Iz))
    m_cr_nmm = term1 * math.sqrt(max(0.0, term2))
    m_cr = max(1e-3, m_cr_nmm / 1e6)  # kN*m

    # Non-dimensional slenderness for LTB
    lambda_bar_lt = math.sqrt(max(0.0, (wy * fy / 1e6) / m_cr))

    # Imperfection factor for LTB
    alpha_lt = 0.34 if (h / b) > 1.2 else 0.49
    
    if lambda_bar_lt <= 0.4:  # Plateau limit
        chi_lt = 1.0
    else:
        phi_lt = 0.5 * (1.0 + alpha_lt * (lambda_bar_lt - 0.2) + lambda_bar_lt ** 2)
        denom = phi_lt + math.sqrt(max(0.0, phi_lt ** 2 - lambda_bar_lt ** 2))
        chi_lt = min(1.0, max(0.05, 1.0 / denom))

    m_b_rd = chi_lt * (wy * fy) / gamma_M1 / 1e6  # kN*m

    # Axial compression buckling resistance Nb,Rd
    iz_rad = math.sqrt(Iz / max(1.0, A))
    lambda_bar_n = (Lcr / max(1.0, iz_rad)) / (math.pi * math.sqrt(E / fy))
    alpha_n = 0.34 if (h / b) > 1.2 else 0.49
    phi_n = 0.5 * (1.0 + alpha_n * (lambda_bar_n - 0.2) + lambda_bar_n ** 2)
    denom_n = phi_n + math.sqrt(max(0.0, phi_n ** 2 - lambda_bar_n ** 2))
    chi_n = min(1.0, max(0.05, 1.0 / denom_n))
    n_b_rd = chi_n * A * fy / gamma_M1 / 1000.0  # kN

    dcr_m = M_Ed / m_b_rd if m_b_rd > 0 else 999.0
    dcr_v = V_Ed / v_pl_rd if v_pl_rd > 0 else 999.0
    is_safe = (dcr_m <= 1.0) and (dcr_v <= 1.0)

    return EC3SteelDesignResult(
        section_class=sec_class,
        M_c_Rd=round(m_c_rd, 3),
        M_b_Rd=round(m_b_rd, 3),
        V_pl_Rd=round(v_pl_rd, 3),
        N_b_Rd=round(n_b_rd, 3),
        chi_LT=round(chi_lt, 4),
        chi_N=round(chi_n, 4),
        dcr_flexure=round(dcr_m, 4),
        dcr_shear=round(dcr_v, 4),
        is_safe=is_safe,
    )
