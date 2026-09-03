"""US AISC 360-16 Specification for Structural Steel Buildings (LRFD) Adapter.

Implements AISC 360-16 LRFD member design provisions:
- Chapter F: Flexure of doubly symmetric I-shaped members (Mp, LTB with Lp, Lr, Cb)
- Chapter E: Compression of members without slender elements (Fe, Fcr, Pn)
- Chapter G: Shear of web without tension field action (Vn)
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class AISC360SteelDesignResult:
    """Design results according to AISC 360-16 LRFD."""
    M_p: float                # Plastic moment capacity (kN*m)
    M_n: float                # Nominal flexural strength (kN*m)
    phi_M_n: float            # Design flexural strength (kN*m, phi_b = 0.90)
    P_n: float                # Nominal compressive strength (kN)
    phi_P_n: float            # Design compressive strength (kN, phi_c = 0.90)
    V_n: float                # Nominal shear strength (kN)
    phi_V_n: float            # Design shear strength (kN, phi_v = 0.90)
    ltb_zone: int             # 1: Plastic, 2: Inelastic LTB, 3: Elastic LTB
    dcr_flexure: float        # Mu / phi_M_n
    dcr_shear: float          # Vu / phi_V_n
    is_safe: bool             # Overall compliance


def check_aisc360_steel_beam(
    d_depth: float,
    bf: float,
    tf: float,
    tw: float,
    Ag: float,
    Zx: float,
    Sx: float,
    ry: float,
    J_torsion: float,
    Cw: float,
    Fy: float = 345.0,        # MPa (e.g. ASTM A992 / 50 ksi)
    E: float = 200000.0,      # MPa (29,000 ksi)
    Lb: float = 3000.0,       # mm (Unbraced length)
    Cb: float = 1.0,          # Moment gradient factor
    Mu: float = 0.0,          # kN*m
    Vu: float = 0.0,          # kN
    K: float = 1.0,           # Effective length factor for compression
    L_col: Optional[float] = None, # mm
) -> AISC360SteelDesignResult:
    """Perform AISC 360-16 LRFD flexural, shear, and compression verification.
    
    Args:
        d_depth: Total member depth (mm)
        bf: Flange width (mm)
        tf: Flange thickness (mm)
        tw: Web thickness (mm)
        Ag: Gross area (mm2)
        Zx: Plastic section modulus about x-axis (mm3)
        Sx: Elastic section modulus about x-axis (mm3)
        ry: Radius of gyration about y-axis (mm)
        J_torsion: Torsional constant (mm4)
        Cw: Warping constant (mm6)
        Fy: Specified minimum yield stress (MPa)
        E: Modulus of elasticity (MPa)
        Lb: Length between points that are braced against lateral displacement (mm)
        Cb: Lateral-torsional buckling modification factor
        Mu: Required flexural strength (kN*m)
        Vu: Required shear strength (kN)
        K: Effective length factor for compression
        L_col: Column unbraced length for compression (mm, default Lb)
        
    Returns:
        AISC360SteelDesignResult instance.
    """
    if L_col is None:
        L_col = Lb

    phi_b = 0.90
    phi_c = 0.90
    phi_v = 0.90

    # Plastic moment capacity
    mp_nmm = Fy * Zx
    mp = mp_nmm / 1e6  # kN*m

    # Limiting laterally unbraced lengths Lp and Lr (AISC 360-16 Section F2)
    e_over_fy = E / max(1.0, Fy)
    lp = 1.76 * ry * math.sqrt(e_over_fy)

    # Effective radius for LTB: rts
    h0 = d_depth - tf  # Distance between flange centroids
    iy = (ry ** 2) * Ag
    rts_sq = math.sqrt(iy * Cw) / max(1.0, Sx)
    rts = math.sqrt(max(1.0, rts_sq))

    c_param = 1.0  # For doubly symmetric I-shapes
    term_root = math.sqrt(
        ((J_torsion * c_param) / (Sx * h0)) ** 2
        + 6.76 * ((0.7 * Fy) / E) ** 2
    )
    lr = 1.95 * rts * (E / (0.7 * Fy)) * math.sqrt(
        (J_torsion * c_param) / (Sx * h0) + term_root
    )

    # Calculate nominal flexural strength Mn
    if Lb <= lp:
        # Zone 1: Full plastic yielding
        mn = mp
        ltb_zone = 1
    elif Lb <= lr:
        # Zone 2: Inelastic lateral-torsional buckling
        ratio = (Lb - lp) / max(1.0, lr - lp)
        mr = 0.7 * Fy * Sx / 1e6
        mn = min(mp, Cb * (mp - (mp - mr) * ratio))
        ltb_zone = 2
    else:
        # Zone 3: Elastic lateral-torsional buckling
        fcr_term = (Lb / max(1.0, rts)) ** 2
        fcr = (Cb * (math.pi ** 2) * E / fcr_term) * math.sqrt(
            1.0 + 0.078 * ((J_torsion * c_param) / (Sx * h0)) * fcr_term
        )
        mn = min(mp, fcr * Sx / 1e6)
        ltb_zone = 3

    phi_mn = phi_b * mn

    # Shear strength (Section G2.1)
    aw = d_depth * tw
    web_ratio = (d_depth - 2.0 * tf) / max(1.0, tw)
    limit_g = 2.24 * math.sqrt(e_over_fy)
    if web_ratio <= limit_g:
        cv1 = 1.0
    else:
        cv1 = min(1.0, limit_g / web_ratio)
    vn = (0.6 * Fy * aw * cv1) / 1000.0  # kN
    phi_vn = phi_v * vn

    # Column compressive strength (Chapter E)
    kl_over_r = (K * L_col) / max(1.0, ry)
    fe = ((math.pi ** 2) * E) / (kl_over_r ** 2)
    if kl_over_r <= 4.71 * math.sqrt(e_over_fy):
        fcr_col = (0.658 ** (Fy / fe)) * Fy
    else:
        fcr_col = 0.877 * fe
    pn = (fcr_col * Ag) / 1000.0  # kN
    phi_pn = phi_c * pn

    dcr_m = Mu / phi_mn if phi_mn > 0 else 999.0
    dcr_v = Vu / phi_vn if phi_vn > 0 else 999.0
    is_safe = (dcr_m <= 1.0) and (dcr_v <= 1.0)

    return AISC360SteelDesignResult(
        M_p=round(mp, 3),
        M_n=round(mn, 3),
        phi_M_n=round(phi_mn, 3),
        P_n=round(pn, 3),
        phi_P_n=round(phi_pn, 3),
        V_n=round(vn, 3),
        phi_V_n=round(phi_vn, 3),
        ltb_zone=ltb_zone,
        dcr_flexure=round(dcr_m, 4),
        dcr_shear=round(dcr_v, 4),
        is_safe=is_safe,
    )
