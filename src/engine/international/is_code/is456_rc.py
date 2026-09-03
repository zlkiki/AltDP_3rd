"""Indian Standard IS 456:2000 Plain and Reinforced Concrete Design Adapter.

Implements Limit State Method (LSM) provisions:
- Partial safety factors gamma_c = 1.5, gamma_s = 1.15
- Neutral axis depth xu and limiting depth xu_max / d
- Limiting and actual flexural resistance Mu
- Design shear strength tau_c (Table 19) and shear stirrup capacity Vus
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class IS456BeamDesignResult:
    """Design results according to IS 456:2000."""
    xu: float                 # Neutral axis depth (mm)
    xu_max: float             # Limiting neutral axis depth (mm)
    is_under_reinforced: bool # True if xu <= xu_max
    M_u_lim: float            # Limiting flexural capacity (kN*m)
    M_u: float                # Design flexural capacity (kN*m)
    tau_c: float              # Design concrete shear strength (MPa)
    V_c: float                # Concrete shear capacity (kN)
    V_us: float               # Stirrup shear capacity (kN)
    V_u_cap: float            # Total shear capacity (kN)
    dcr_flexure: float        # Mu_applied / M_u
    dcr_shear: float          # Vu_applied / V_u_cap
    is_safe: bool             # Overall compliance


def check_is456_rc_beam(
    b: float,
    h: float,
    d: float,
    fck: float,               # Characteristic cube compressive strength (MPa)
    fy: float,                # Characteristic rebar yield strength (MPa)
    Ast: float,               # Tension steel area (mm2)
    Asv: float = 142.6,       # Shear stirrup area within spacing s (mm2)
    s: float = 200.0,         # Stirrup spacing (mm)
    fyv: Optional[float] = None, # Stirrup yield strength (MPa, default fy)
    Mu_applied: float = 0.0,  # Factored applied moment (kN*m)
    Vu_applied: float = 0.0,  # Factored applied shear (kN)
) -> IS456BeamDesignResult:
    """Perform IS 456:2000 flexural and shear verification for an RC beam section.
    
    Args:
        b: Beam width (mm)
        h: Beam depth (mm)
        d: Effective depth to tension rebar centroid (mm)
        fck: Concrete characteristic cube strength (MPa)
        fy: Rebar yield strength (MPa)
        Ast: Area of tension reinforcement (mm2)
        Asv: Area of stirrup legs (mm2)
        s: Stirrup spacing (mm)
        fyv: Stirrup yield strength (MPa)
        Mu_applied: Factored design moment (kN*m)
        Vu_applied: Factored design shear force (kN)
        
    Returns:
        IS456BeamDesignResult instance.
    """
    if fyv is None:
        fyv = fy

    # Limiting neutral axis ratio xu_max / d (IS 456 Cl. 38.1 Note)
    if fy <= 250.0:
        xu_max_ratio = 0.53
    elif fy <= 415.0:
        xu_max_ratio = 0.48
    else:
        xu_max_ratio = 0.46

    xu_max = xu_max_ratio * d

    # Neutral axis depth: C = T => 0.36 * fck * b * xu = 0.87 * fy * Ast
    xu = (0.87 * fy * Ast) / (0.36 * fck * b)
    is_under = xu <= xu_max

    # Limiting moment capacity Mu_lim
    mu_lim_nmm = 0.36 * xu_max_ratio * (1.0 - 0.42 * xu_max_ratio) * b * (d ** 2) * fck
    mu_lim = mu_lim_nmm / 1e6

    # Actual moment capacity Mu
    if is_under:
        mu_nmm = 0.87 * fy * Ast * (d - 0.42 * xu)
        mu = min(mu_lim, mu_nmm / 1e6)
    else:
        # Over-reinforced: capped at Mu_lim per IS 456
        mu = mu_lim

    mu = max(1.0, mu)

    # Design concrete shear strength tau_c (IS 456 Table 19 formula)
    pt = min(3.0, (100.0 * Ast) / (b * d))
    beta_param = (0.8 * fck) / (6.89 * max(0.1, pt))
    tau_c = (0.85 * math.sqrt(0.8 * fck) * (math.sqrt(1.0 + 5.0 * beta_param) - 1.0)) / (6.0 * beta_param)
    tau_c = max(0.2, min(1.5, tau_c))
    vc = (tau_c * b * d) / 1000.0  # kN

    # Shear stirrups capacity Vus (IS 456 Cl. 40.4)
    vus = (0.87 * fyv * Asv * d) / max(1.0, s) / 1000.0  # kN

    # Maximum shear stress tau_c_max (Table 20)
    tau_c_max = min(4.0, 0.62 * math.sqrt(fck))
    vu_max = (tau_c_max * b * d) / 1000.0

    vu_cap = min(vc + vus, vu_max)

    dcr_m = Mu_applied / mu if mu > 0 else 999.0
    dcr_v = Vu_applied / vu_cap if vu_cap > 0 else 999.0
    is_safe = (dcr_m <= 1.0) and (dcr_v <= 1.0)

    return IS456BeamDesignResult(
        xu=round(xu, 2),
        xu_max=round(xu_max, 2),
        is_under_reinforced=is_under,
        M_u_lim=round(mu_lim, 3),
        M_u=round(mu, 3),
        tau_c=round(tau_c, 3),
        V_c=round(vc, 3),
        V_us=round(vus, 3),
        V_u_cap=round(vu_cap, 3),
        dcr_flexure=round(dcr_m, 4),
        dcr_shear=round(dcr_v, 4),
        is_safe=is_safe,
    )
