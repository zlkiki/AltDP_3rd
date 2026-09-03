"""RC Plastic Hinge Engine according to ASCE 41-17 / KDS 41 17 00.

Calculates plastic hinge parameters (a, b, c, IO, LS, CP) and yield properties
for RC Beams, RC Columns (with axial load & shear mode classification),
and RC Shear Walls (flexure & shear hinges).
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


def _interp_2d(
    x: float, x0: float, x1: float,
    y: float, y0: float, y1: float,
    q00: float, q01: float, q10: float, q11: float,
) -> float:
    """Bilinear interpolation clamped within ranges [x0, x1] and [y0, y1]."""
    xc = max(x0, min(x1, x))
    yc = max(y0, min(y1, y))
    
    # Interpolate along y for x0 and x1
    r0 = _interp_1d(yc, y0, y1, q00, q01)
    r1 = _interp_1d(yc, y0, y1, q10, q11)
    
    # Interpolate along x
    return _interp_1d(xc, x0, x1, r0, r1)


def calculate_rc_beam_hinge_parameters(
    b: float,
    h: float,
    d: float,
    fck: float,
    fy: float,
    As: float,
    As_prime: float,
    V_design: float,
    conforming: bool = True,
) -> HingeParameters:
    """Calculate ASCE 41-17 Table 10-7 plastic hinge parameters for an RC beam.
    
    Args:
        b: Section width (mm)
        h: Section total depth (mm)
        d: Section effective depth (mm)
        fck: Concrete compressive strength (MPa)
        fy: Rebar yield strength (MPa)
        As: Tension steel area (mm2)
        As_prime: Compression steel area (mm2)
        V_design: Factored shear force (kN)
        conforming: True if closed stirrups with s <= d/3 are provided
        
    Returns:
        HingeParameters instance.
    """
    rho = As / (b * d)
    rho_prime = As_prime / (b * d)
    beta1 = max(0.65, min(0.85, 0.85 - 0.05 * (max(28.0, fck) - 28.0) / 7.0))
    rho_bal = 0.85 * beta1 * (fck / fy) * (600.0 / (600.0 + fy))
    
    rho_diff_ratio = (rho - rho_prime) / (rho_bal if rho_bal > 1e-6 else 0.02)
    
    # Shear stress ratio: V / (b*d*sqrt(fck)) in MPa
    v_stress = (V_design * 1000.0) / (b * d)
    v_ratio = v_stress / math.sqrt(max(1.0, fck))

    # Grid endpoints: rho_diff [0.0, 0.5], v_ratio [0.25, 0.50]
    if conforming:
        # ASCE 41-17 Table 10-7 Condition i (Conforming transverse reinforcement)
        # q00 = (rho<=0, v<=0.25), q01 = (rho<=0, v>=0.50), q10 = (rho>=0.5, v<=0.25), q11 = (rho>=0.5, v>=0.50)
        a = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.025, 0.020, 0.020, 0.012)
        b_rot = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.050, 0.040, 0.030, 0.020)
        c = 0.20
        io = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.010, 0.005, 0.005, 0.003)
        ls = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.025, 0.020, 0.020, 0.012)
        cp = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.050, 0.040, 0.030, 0.020)
    else:
        # Non-conforming transverse reinforcement
        a = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.020, 0.012, 0.010, 0.005)
        b_rot = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.030, 0.020, 0.015, 0.010)
        c = 0.20
        io = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.005, 0.003, 0.003, 0.001)
        ls = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.015, 0.010, 0.010, 0.005)
        cp = _interp_2d(rho_diff_ratio, 0.0, 0.5, v_ratio, 0.25, 0.50, 0.030, 0.020, 0.015, 0.010)

    return HingeParameters(
        a=round(a, 6),
        b=round(b_rot, 6),
        c=round(c, 4),
        io_limit=round(io, 6),
        ls_limit=round(ls, 6),
        cp_limit=round(cp, 6),
        alpha=0.03,
    )


def calculate_rc_column_hinge_parameters(
    b: float,
    h: float,
    fck: float,
    P_axial: float,
    V_plastic: float,
    V_nominal: float,
    conforming: bool = True,
) -> HingeParameters:
    """Calculate ASCE 41-17 Table 10-8 plastic hinge parameters for an RC column.
    
    Accounts for axial force ratio (P / Ag*fck) and shear-to-flexure failure mode branching.
    
    Args:
        b: Column section width (mm)
        h: Column section depth (mm)
        fck: Concrete compressive strength (MPa)
        P_axial: Axial compression load (kN). Positive for compression.
        V_plastic: Shear corresponding to plastic moment development (kN)
        V_nominal: Nominal shear strength (kN)
        conforming: True if conforming transverse ties provided
        
    Returns:
        HingeParameters instance.
    """
    ag = b * h
    axial_capacity = (ag * fck) / 1000.0  # kN
    nu = max(0.0, P_axial / (axial_capacity if axial_capacity > 0 else 1.0))
    
    v_ratio = V_plastic / (V_nominal if V_nominal > 1e-3 else 1.0)
    
    # Behavior mode classification
    # Condition i: Flexure controlled (Vp/Vn <= 0.6)
    # Condition ii: Flexure-shear controlled (0.6 < Vp/Vn < 1.0)
    # Condition iii: Shear controlled (Vp/Vn >= 1.0)
    if v_ratio >= 1.0:
        # Shear controlled - brittle response
        return HingeParameters(
            a=0.002,
            b=0.004,
            c=0.0,
            io_limit=0.001,
            ls_limit=0.002,
            cp_limit=0.004,
            alpha=0.0,
        )

    # Branch between Condition i (v_ratio <= 0.6) and Condition ii (v_ratio = 1.0)
    # Axial ratio endpoints: [0.1, 0.6]
    if conforming:
        # Condition i
        a_i = _interp_1d(nu, 0.1, 0.6, 0.020, 0.008)
        b_i = _interp_1d(nu, 0.1, 0.6, 0.040, 0.012)
        io_i = _interp_1d(nu, 0.1, 0.6, 0.008, 0.002)
        ls_i = _interp_1d(nu, 0.1, 0.6, 0.020, 0.006)
        cp_i = _interp_1d(nu, 0.1, 0.6, 0.040, 0.012)
        
        # Condition ii
        a_ii = _interp_1d(nu, 0.1, 0.6, 0.015, 0.005)
        b_ii = _interp_1d(nu, 0.1, 0.6, 0.025, 0.008)
        io_ii = _interp_1d(nu, 0.1, 0.6, 0.005, 0.001)
        ls_ii = _interp_1d(nu, 0.1, 0.6, 0.015, 0.004)
        cp_ii = _interp_1d(nu, 0.1, 0.6, 0.025, 0.008)
    else:
        # Non-conforming
        a_i = _interp_1d(nu, 0.1, 0.6, 0.012, 0.004)
        b_i = _interp_1d(nu, 0.1, 0.6, 0.020, 0.006)
        io_i = _interp_1d(nu, 0.1, 0.6, 0.004, 0.001)
        ls_i = _interp_1d(nu, 0.1, 0.6, 0.010, 0.003)
        cp_i = _interp_1d(nu, 0.1, 0.6, 0.020, 0.006)
        
        a_ii = _interp_1d(nu, 0.1, 0.6, 0.008, 0.002)
        b_ii = _interp_1d(nu, 0.1, 0.6, 0.012, 0.004)
        io_ii = _interp_1d(nu, 0.1, 0.6, 0.002, 0.0005)
        ls_ii = _interp_1d(nu, 0.1, 0.6, 0.006, 0.002)
        cp_ii = _interp_1d(nu, 0.1, 0.6, 0.012, 0.004)

    # Interpolate along Vp/Vn between 0.6 and 1.0
    if v_ratio <= 0.6:
        a, b_rot, io, ls, cp = a_i, b_i, io_i, ls_i, cp_i
    else:
        a = _interp_1d(v_ratio, 0.6, 1.0, a_i, a_ii)
        b_rot = _interp_1d(v_ratio, 0.6, 1.0, b_i, b_ii)
        io = _interp_1d(v_ratio, 0.6, 1.0, io_i, io_ii)
        ls = _interp_1d(v_ratio, 0.6, 1.0, ls_i, ls_ii)
        cp = _interp_1d(v_ratio, 0.6, 1.0, cp_i, cp_ii)

    return HingeParameters(
        a=round(a, 6),
        b=round(b_rot, 6),
        c=0.20,
        io_limit=round(io, 6),
        ls_limit=round(ls, 6),
        cp_limit=round(cp, 6),
        alpha=0.03,
    )


def calculate_rc_wall_hinge_parameters(
    is_flexure: bool = True,
    has_boundary_elements: bool = True,
    nu: float = 0.1,
    v_stress_ratio: float = 0.2,
) -> HingeParameters:
    """Calculate ASCE 41-17 Table 10-19/20 parameters for RC Shear Wall hinges.
    
    Args:
        is_flexure: True for flexural (M-theta), False for shear (V-gamma)
        has_boundary_elements: Whether conforming boundary element is provided
        nu: Axial stress ratio P / (Ag * fck)
        v_stress_ratio: Shear stress ratio v / sqrt(fck) in MPa
        
    Returns:
        HingeParameters instance.
    """
    if is_flexure:
        # Table 10-19: Flexure-controlled walls
        if has_boundary_elements:
            a = _interp_1d(nu, 0.05, 0.30, 0.020, 0.008)
            b = _interp_1d(nu, 0.05, 0.30, 0.035, 0.015)
            io = _interp_1d(nu, 0.05, 0.30, 0.005, 0.002)
            ls = _interp_1d(nu, 0.05, 0.30, 0.015, 0.006)
            cp = _interp_1d(nu, 0.05, 0.30, 0.030, 0.012)
        else:
            a = _interp_1d(nu, 0.05, 0.30, 0.010, 0.004)
            b = _interp_1d(nu, 0.05, 0.30, 0.018, 0.008)
            io = _interp_1d(nu, 0.05, 0.30, 0.003, 0.001)
            ls = _interp_1d(nu, 0.05, 0.30, 0.008, 0.003)
            cp = _interp_1d(nu, 0.05, 0.30, 0.015, 0.006)
        c = 0.20
    else:
        # Table 10-20: Shear-controlled walls (drift/shear strain gamma)
        a = 0.008
        b = 0.015
        c = 0.40
        io = 0.003
        ls = 0.006
        cp = 0.012

    return HingeParameters(
        a=round(a, 6),
        b=round(b, 6),
        c=round(c, 4),
        io_limit=round(io, 6),
        ls_limit=round(ls, 6),
        cp_limit=round(cp, 6),
        alpha=0.02,
    )


def create_rc_beam_hinge(
    member_id: int,
    b: float,
    h: float,
    d: float,
    fck: float,
    fy: float,
    As: float,
    As_prime: float,
    span_len: float,
    V_design: float,
    conforming: bool = True,
    demand_theta: Optional[float] = None,
) -> HingePerformance:
    """Create complete RC beam plastic hinge performance summary."""
    params = calculate_rc_beam_hinge_parameters(
        b=b, h=h, d=d, fck=fck, fy=fy, As=As, As_prime=As_prime,
        V_design=V_design, conforming=conforming
    )
    # Singly reinforced flexural yield strength
    a_depth = (As * fy) / (0.85 * fck * b)
    my = As * fy * (d - a_depth / 2.0) / 1e6  # kN*m
    
    # Effective stiffness and yield rotation: theta_y = My * L / (6 * Ec * Ieff)
    ec = 8500.0 * (fck + 8.0) ** (1.0 / 3.0)  # MPa
    ig = (b * h ** 3) / 12.0
    ieff = 0.35 * ig  # ASCE 41 cracked beam stiffness
    theta_y = (my * 1e6 * span_len) / (6.0 * ec * ieff)
    
    return create_hinge_performance_summary(
        member_id=member_id,
        member_type=MemberType.RC_BEAM.value,
        my=my,
        theta_y=theta_y,
        params=params,
        demand_theta=demand_theta,
    )
