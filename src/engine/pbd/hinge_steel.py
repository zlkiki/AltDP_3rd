"""Steel Plastic Hinge Engine according to ASCE 41-17 / AISC 341 / KDS 41 17 00.

Calculates plastic hinge parameters (a, b, c, IO, LS, CP) and yield properties
for Steel Beams (flexure with compactness/lateral bracing),
Steel Columns (P-M interaction & axial compression effects),
and Steel Braces (tension-yielding and compression-buckling).
"""

import math
from typing import Optional
from src.engine.pbd.models import (
    HingeParameters,
    HingePerformance,
    MemberType,
)
from src.engine.pbd.backbone_curve import create_hinge_performance_summary


def _interp_1d(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """Clamp and perform 1D linear interpolation."""
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    ratio = (x - x0) / (x1 - x0)
    return y0 + ratio * (y1 - y0)


def calculate_steel_beam_hinge_parameters(
    bf: float,
    tf: float,
    h: float,
    tw: float,
    fy: float,
    es: float = 205000.0,
    lb: float = 3000.0,
    ry: float = 50.0,
) -> HingeParameters:
    """Calculate ASCE 41-17 Table 9-6 plastic hinge parameters for a steel beam.
    
    Checks compactness (flange & web slenderness) and unbraced length Lb / ry.
    
    Args:
        bf: Flange width (mm)
        tf: Flange thickness (mm)
        h: Clear web depth (mm)
        tw: Web thickness (mm)
        fy: Steel yield strength (MPa)
        es: Steel elastic modulus (MPa)
        lb: Unbraced lateral length (mm)
        ry: Weak-axis radius of gyration (mm)
        
    Returns:
        HingeParameters instance.
    """
    # Flange slenderness: bf / (2 * tf)
    lambda_f = bf / (2.0 * max(1.0, tf))
    # Web slenderness: h / tw
    lambda_w = h / max(1.0, tw)
    # Slenderness limits
    e_over_fy = math.sqrt(es / max(1.0, fy))
    lambda_hd_f = 0.31 * e_over_fy
    lambda_md_f = 0.38 * e_over_fy
    lambda_hd_w = 2.45 * e_over_fy
    lambda_md_w = 3.76 * e_over_fy
    
    # Lateral bracing limits
    lb_over_ry = lb / max(1.0, ry)
    l_pd = 0.086 * (es / fy) * 1.0  # Normalized Lb/ry limit for high ductility
    l_md = 0.17 * (es / fy) * 1.0
    
    is_high_ductile = (lambda_f <= lambda_hd_f) and (lambda_w <= lambda_hd_w) and (lb_over_ry <= l_pd)
    is_mod_ductile = (lambda_f <= lambda_md_f) and (lambda_w <= lambda_md_w) and (lb_over_ry <= l_md)
    
    if is_high_ductile:
        # ASCE 41-17 Table 9-6 (High Ductility member)
        a = 0.030
        b = 0.040
        c = 0.60
        io = 0.005
        ls = 0.025
        cp = 0.035
    elif is_mod_ductile:
        # Moderate Ductility member
        a = 0.020
        b = 0.030
        c = 0.40
        io = 0.003
        ls = 0.015
        cp = 0.025
    else:
        # Low Ductility / Slender member
        a = 0.010
        b = 0.015
        c = 0.20
        io = 0.0015
        ls = 0.008
        cp = 0.012

    return HingeParameters(
        a=a,
        b=b,
        c=c,
        io_limit=io,
        ls_limit=ls,
        cp_limit=cp,
        alpha=0.03,
    )


def calculate_steel_column_hinge_parameters(
    P_axial: float,
    P_cl: float,
    is_compact: bool = True,
) -> HingeParameters:
    """Calculate ASCE 41-17 Table 9-7 plastic hinge parameters for a steel column.
    
    Args:
        P_axial: Axial compression load (kN). Positive for compression.
        P_cl: Nominal axial compression capacity (kN).
        is_compact: True if section satisfies seismically compact limits.
        
    Returns:
        HingeParameters instance.
    """
    ratio = max(0.0, P_axial / (P_cl if P_cl > 0 else 1.0))
    
    if is_compact:
        # High ductility section under varying axial load ratio P/Pcl
        # Interpolate between low axial (P/Pcl <= 0.2) and high axial (P/Pcl >= 0.5)
        a = _interp_1d(ratio, 0.20, 0.50, 0.028, 0.008)
        b = _interp_1d(ratio, 0.20, 0.50, 0.038, 0.015)
        c = _interp_1d(ratio, 0.20, 0.50, 0.60, 0.20)
        io = _interp_1d(ratio, 0.20, 0.50, 0.005, 0.002)
        ls = _interp_1d(ratio, 0.20, 0.50, 0.022, 0.006)
        cp = _interp_1d(ratio, 0.20, 0.50, 0.032, 0.010)
    else:
        # Non-compact section
        a = _interp_1d(ratio, 0.20, 0.50, 0.015, 0.004)
        b = _interp_1d(ratio, 0.20, 0.50, 0.022, 0.008)
        c = _interp_1d(ratio, 0.20, 0.50, 0.40, 0.15)
        io = _interp_1d(ratio, 0.20, 0.50, 0.003, 0.001)
        ls = _interp_1d(ratio, 0.20, 0.50, 0.012, 0.003)
        cp = _interp_1d(ratio, 0.20, 0.50, 0.018, 0.005)

    return HingeParameters(
        a=round(a, 6),
        b=round(b, 6),
        c=round(c, 4),
        io_limit=round(io, 6),
        ls_limit=round(ls, 6),
        cp_limit=round(cp, 6),
        alpha=0.02,
    )


def calculate_steel_brace_hinge_parameters(
    is_tension: bool = True,
    kl_over_r: float = 80.0,
    width_thickness_ratio: float = 15.0,
) -> HingeParameters:
    """Calculate ASCE 41-17 Table 9-8 axial plastic hinge parameters for steel braces.
    
    Args:
        is_tension: True for tension-yielding brace, False for compression-buckling.
        kl_over_r: Slenderness ratio KL/r.
        width_thickness_ratio: Governing width-to-thickness ratio (b/t).
        
    Returns:
        HingeParameters instance. Note that rotation limits represent displacement ratios (Delta/Delta_y - 1).
    """
    if is_tension:
        # Tension-yielding brace: very ductile deformation capacity
        a = 0.070  # Ductile elongation limit (approx 7 to 9 times yield)
        b = 0.090
        c = 0.80   # Strain hardening residual capacity
        io = 0.010
        ls = 0.050
        cp = 0.070
        alpha = 0.05
    else:
        # Compression-buckling brace: post-buckling degradation
        # Steeper degradation as slenderness increases
        res_ratio = _interp_1d(kl_over_r, 40.0, 120.0, 0.35, 0.20)
        a = _interp_1d(kl_over_r, 40.0, 120.0, 0.008, 0.004)
        b = _interp_1d(kl_over_r, 40.0, 120.0, 0.030, 0.015)
        c = res_ratio
        io = 0.002
        ls = 0.010
        cp = 0.020
        alpha = 0.0

    return HingeParameters(
        a=round(a, 6),
        b=round(b, 6),
        c=round(c, 4),
        io_limit=round(io, 6),
        ls_limit=round(ls, 6),
        cp_limit=round(cp, 6),
        alpha=alpha,
    )


def create_steel_beam_hinge(
    member_id: int,
    zx: float,
    fy: float,
    bf: float,
    tf: float,
    h: float,
    tw: float,
    span_len: float,
    ix: float,
    es: float = 205000.0,
    demand_theta: Optional[float] = None,
) -> HingePerformance:
    """Create complete steel beam plastic hinge performance summary."""
    params = calculate_steel_beam_hinge_parameters(
        bf=bf, tf=tf, h=h, tw=tw, fy=fy, es=es
    )
    # Plastic moment capacity: Mp = Zx * Fy
    mp = (zx * fy) / 1e6  # kN*m
    
    # Elastic yield rotation: theta_y = Mp * L / (6 * Es * Ix)
    theta_y = (mp * 1e6 * span_len) / (6.0 * es * ix)
    
    return create_hinge_performance_summary(
        member_id=member_id,
        member_type=MemberType.STEEL_BEAM.value,
        my=mp,
        theta_y=theta_y,
        params=params,
        demand_theta=demand_theta,
    )
