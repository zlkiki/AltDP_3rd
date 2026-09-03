"""Eurocode 2 (EN 1992-1-1:2004 / A1:2014) RC Member Design Adapter.

Implements Eurocode partial safety factor limit state design for reinforced concrete:
- Material design strengths: fcd = acc * fck / gamma_c, fyd = fyk / gamma_s
- Flexural design resistance MRd with rectangular stress block (lambda, eta)
- Shear resistance VRd,c (unreinforced), VRd,s (stirrup truss model), VRd,max (crushing limit)
"""

import math
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class EC2BeamDesignResult:
    """Design results according to Eurocode 2."""
    M_Rd: float               # Design flexural resistance (kN*m)
    V_Rd_c: float             # Concrete shear resistance without stirrups (kN)
    V_Rd_s: float             # Stirrup shear resistance (kN)
    V_Rd_max: float           # Concrete strut crushing shear limit (kN)
    V_Rd: float               # Governing shear resistance (kN)
    cot_theta: float          # Strut angle cotangent used (1.0 to 2.5)
    fcd: float                # Design concrete compressive strength (MPa)
    fyd: float                # Design rebar yield strength (MPa)
    dcr_flexure: float        # Mu / M_Rd
    dcr_shear: float          # Vu / V_Rd
    is_safe: bool             # Overall compliance


def check_ec2_rc_beam(
    b: float,
    h: float,
    d: float,
    fck: float,
    fyk: float,
    As: float,
    As_prime: float = 0.0,
    d_prime: float = 50.0,
    Asw: float = 142.6,
    s: float = 200.0,
    fywk: Optional[float] = None,
    Mu: float = 0.0,
    Vu: float = 0.0,
    gamma_c: float = 1.50,
    gamma_s: float = 1.15,
    acc: float = 0.85,
    cot_theta: float = 2.5,
) -> EC2BeamDesignResult:
    """Perform Eurocode 2 flexural and shear verification for an RC beam section.
    
    Args:
        b: Width of beam bw (mm)
        h: Total height of beam (mm)
        d: Effective depth to tension steel (mm)
        fck: Characteristic concrete compressive cylinder strength (MPa)
        fyk: Characteristic rebar yield strength (MPa)
        As: Area of tension reinforcement (mm2)
        As_prime: Area of compression reinforcement (mm2)
        d_prime: Effective depth to compression steel (mm)
        Asw: Area of shear links within spacing s (mm2)
        s: Spacing of shear links (mm)
        fywk: Characteristic shear link yield strength (MPa, default fyk)
        Mu: Design factored bending moment (kN*m)
        Vu: Design factored shear force (kN)
        gamma_c: Concrete partial factor (default 1.50)
        gamma_s: Steel partial factor (default 1.15)
        acc: Long-term coefficient for concrete (default 0.85)
        cot_theta: Strut inclination cotangent (1.0 <= cot_theta <= 2.5, default 2.5)
        
    Returns:
        EC2BeamDesignResult with resistances, DCRs, and safety status.
    """
    if fywk is None:
        fywk = fyk

    # Design material strengths
    fcd = (acc * fck) / gamma_c
    fyd = fyk / gamma_s
    fywd = fywk / gamma_s

    # Stress block parameters (EN 1992-1-1 Cl. 3.1.7)
    if fck <= 50.0:
        lambda_val = 0.80
        eta_val = 1.00
    else:
        lambda_val = 0.80 - (fck - 50.0) / 400.0
        eta_val = 1.00 - (fck - 50.0) / 200.0

    # Neutral axis depth x
    net_tension_force = (As - As_prime) * fyd
    x = net_tension_force / (eta_val * fcd * b * lambda_val)

    # Singly or doubly reinforced moment resistance
    lever_arm_c = d - 0.5 * lambda_val * x
    if As_prime > 0.0 and d_prime < x:
        m_rd_nmm = (
            (As - As_prime) * fyd * lever_arm_c
            + As_prime * fyd * (d - d_prime)
        )
    else:
        m_rd_nmm = As * fyd * lever_arm_c
    m_rd = max(1.0, m_rd_nmm / 1e6)

    # Shear resistance without shear reinforcement (Cl. 6.2.2)
    k_size = min(2.0, 1.0 + math.sqrt(200.0 / max(1.0, d)))
    rho_l = min(0.02, As / (b * d))
    c_rd_c = 0.18 / gamma_c
    v_min = 0.035 * (k_size ** 1.5) * math.sqrt(fck)
    v_rd_c_stress = max(c_rd_c * k_size * ((100.0 * rho_l * fck) ** (1.0 / 3.0)), v_min)
    v_rd_c = (v_rd_c_stress * b * d) / 1000.0  # kN

    # Shear resistance with shear reinforcement (Cl. 6.2.3 variable strut angle)
    cot_theta_clamped = max(1.0, min(2.5, cot_theta))
    tan_theta = 1.0 / cot_theta_clamped
    z = min(d - 0.5 * lambda_val * x, 0.9 * d)

    v_rd_s = (Asw / s) * z * fywd * cot_theta_clamped / 1000.0  # kN

    # Strut crushing limit VRd,max
    nu1 = 0.6 * (1.0 - fck / 250.0)
    alpha_cw = 1.0  # For non-prestressed structures
    v_rd_max = (alpha_cw * b * z * nu1 * fcd / (cot_theta_clamped + tan_theta)) / 1000.0  # kN

    v_rd = min(v_rd_max, v_rd_s)

    dcr_m = Mu / m_rd if m_rd > 0 else 999.0
    dcr_v = Vu / v_rd if v_rd > 0 else 999.0
    is_safe = (dcr_m <= 1.0) and (dcr_v <= 1.0)

    return EC2BeamDesignResult(
        M_Rd=round(m_rd, 3),
        V_Rd_c=round(v_rd_c, 3),
        V_Rd_s=round(v_rd_s, 3),
        V_Rd_max=round(v_rd_max, 3),
        V_Rd=round(v_rd, 3),
        cot_theta=cot_theta_clamped,
        fcd=round(fcd, 3),
        fyd=round(fyd, 3),
        dcr_flexure=round(dcr_m, 4),
        dcr_shear=round(dcr_v, 4),
        is_safe=is_safe,
    )
