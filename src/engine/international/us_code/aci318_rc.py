"""US ACI 318-19 Building Code Requirements for Structural Concrete Adapter.

Implements ACI 318-19 strength design provisions:
- Concrete stress block factor beta1
- Net tensile strain et and transition strength reduction factor phi (0.65 to 0.90)
- Nominal and design flexural strength (Mn, phi*Mn)
- Nominal and design shear strength (Vc, Vs, phi*Vn with phi_v = 0.75)
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class ACI318BeamDesignResult:
    """Design results according to ACI 318-19."""
    beta1: float              # Stress block depth factor
    c_depth: float            # Neutral axis depth (mm)
    epsilon_t: float          # Net tensile strain in extreme tension steel
    phi_flexure: float        # Strength reduction factor for moment (0.65 to 0.90)
    phi_shear: float          # Strength reduction factor for shear (0.75)
    M_n: float                # Nominal flexural strength (kN*m)
    phi_M_n: float            # Design flexural strength (kN*m)
    V_c: float                # Nominal concrete shear strength (kN)
    V_s: float                # Nominal shear reinforcement strength (kN)
    V_n: float                # Total nominal shear strength (kN)
    phi_V_n: float            # Design shear strength (kN)
    dcr_flexure: float        # Mu / phi_M_n
    dcr_shear: float          # Vu / phi_V_n
    is_safe: bool             # Overall compliance


def check_aci318_rc_beam(
    b: float,
    h: float,
    d: float,
    fc_prime: float,
    fy: float,
    As: float,
    As_prime: float = 0.0,
    d_prime: float = 50.0,
    Av: float = 142.6,
    s: float = 200.0,
    fyt: Optional[float] = None,
    Mu: float = 0.0,
    Vu: float = 0.0,
    Es: float = 200000.0,
    lambda_factor: float = 1.0,
) -> ACI318BeamDesignResult:
    """Perform ACI 318-19 flexural and shear design check for an RC beam section.
    
    Args:
        b: Web width bw (mm)
        h: Total section height (mm)
        d: Distance from extreme compression fiber to centroid of tension steel (mm)
        fc_prime: Specified concrete compressive strength (MPa)
        fy: Specified yield strength of tension reinforcement (MPa)
        As: Area of nonprestressed tension reinforcement (mm2)
        As_prime: Area of compression reinforcement (mm2)
        d_prime: Distance to compression reinforcement centroid (mm)
        Av: Area of shear reinforcement within spacing s (mm2)
        s: Center-to-center spacing of shear reinforcement (mm)
        fyt: Specified yield strength of transverse reinforcement (MPa, default fy)
        Mu: Factored design moment (kN*m)
        Vu: Factored design shear force (kN)
        Es: Modulus of elasticity of rebar (MPa, default 200,000)
        lambda_factor: Lightweight concrete modification factor (default 1.0)
        
    Returns:
        ACI318BeamDesignResult instance.
    """
    if fyt is None:
        fyt = fy

    # Stress block factor beta1 (ACI 318-19 Table 22.2.2.4.3)
    if fc_prime <= 28.0:
        beta1 = 0.85
    elif fc_prime < 55.0:
        beta1 = 0.85 - 0.05 * (fc_prime - 28.0) / 7.0
    else:
        beta1 = 0.65
    beta1 = max(0.65, min(0.85, beta1))

    # Compression stress block depth a and neutral axis depth c
    # Check compression steel yielding
    a = ((As - As_prime) * fy) / (0.85 * fc_prime * b)
    c = a / beta1

    # Net tensile strain epsilon_t (ACI 318-19 Table 21.2.2)
    eps_cu = 0.003
    eps_ty = fy / Es
    if c > 0:
        eps_t = eps_cu * (d - c) / c
    else:
        eps_t = 0.05

    # Strength reduction factor phi
    if eps_t >= eps_ty + 0.003:  # Tension-controlled
        phi_flexure = 0.90
    elif eps_t <= eps_ty:        # Compression-controlled
        phi_flexure = 0.65
    else:                        # Transition region
        phi_flexure = 0.65 + 0.25 * (eps_t - eps_ty) / 0.003

    phi_flexure = max(0.65, min(0.90, phi_flexure))
    phi_shear = 0.75

    # Nominal moment strength Mn
    if As_prime > 0.0 and c > d_prime:
        eps_s_prime = eps_cu * (c - d_prime) / c
        fs_prime = min(fy, eps_s_prime * Es)
        a_adj = (As * fy - As_prime * fs_prime) / (0.85 * fc_prime * b)
        mn_nmm = (
            (As * fy - As_prime * fs_prime) * (d - a_adj / 2.0)
            + As_prime * fs_prime * (d - d_prime)
        )
    else:
        mn_nmm = As * fy * (d - a / 2.0)

    mn = max(1.0, mn_nmm / 1e6)  # kN*m
    phi_mn = phi_flexure * mn

    # Shear strength (ACI 318-19 Table 22.5.5.1 simplified)
    vc_n = 0.17 * lambda_factor * math.sqrt(fc_prime) * b * d
    vc = vc_n / 1000.0  # kN

    vs_n = (Av * fyt * d) / max(1.0, s)
    vs = vs_n / 1000.0  # kN

    vn_max = (0.17 + 0.66) * math.sqrt(fc_prime) * b * d / 1000.0
    vn = min(vc + vs, vn_max)
    phi_vn = phi_shear * vn

    dcr_m = Mu / phi_mn if phi_mn > 0 else 999.0
    dcr_v = Vu / phi_vn if phi_vn > 0 else 999.0
    is_safe = (dcr_m <= 1.0) and (dcr_v <= 1.0)

    return ACI318BeamDesignResult(
        beta1=round(beta1, 4),
        c_depth=round(c, 2),
        epsilon_t=round(eps_t, 6),
        phi_flexure=round(phi_flexure, 4),
        phi_shear=phi_shear,
        M_n=round(mn, 3),
        phi_M_n=round(phi_mn, 3),
        V_c=round(vc, 3),
        V_s=round(vs, 3),
        V_n=round(vn, 3),
        phi_V_n=round(phi_vn, 3),
        dcr_flexure=round(dcr_m, 4),
        dcr_shear=round(dcr_v, 4),
        is_safe=is_safe,
    )
