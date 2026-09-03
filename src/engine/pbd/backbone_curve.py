"""Backbone Curve Generation and Performance Level Evaluation.

Implements multi-linear moment-rotation (M-theta) and force-displacement (P-delta, V-gamma)
backbone curve generation according to ASCE 41-17 / KDS 41 17 00 and evaluates IO/LS/CP performance levels.
"""

from typing import List, Tuple, Optional
from src.engine.pbd.models import (
    BackbonePoint,
    HingeParameters,
    HingePerformance,
    PerformanceLevel,
)


def generate_backbone_curve(
    theta_y: float,
    my: float,
    params: HingeParameters,
    symmetric: bool = True,
) -> List[BackbonePoint]:
    """Generate coordinate points for a multilinear plastic hinge backbone curve.
    
    Curve points sequence for positive quadrant:
      Point 0: (0, 0) - Origin
      Point 1: (theta_y, My) - Yield point
      Point 2: (theta_y + a, My * (1 + alpha)) - Capping / peak resistance point
      Point 3: (theta_y + b, My * c) - Residual strength point
      Point 4: (theta_y + b + delta_f, 0.0) - Ultimate collapse / drop to zero
      
    Args:
        theta_y: Yield rotation (rad) or yield deformation. Must be > 0.
        my: Yield moment (kN*m) or yield force. Must be > 0.
        params: Hinge parameters (a, b, c, alpha, etc.).
        symmetric: If True, prepends negative quadrant points (-theta, -M).
        
    Returns:
        List of BackbonePoint coordinates.
    """
    if theta_y <= 0:
        theta_y = 1e-5
    if my <= 0:
        my = 1e-3

    a = max(0.0, params.a)
    b = max(a, params.b)
    c = max(0.0, min(1.0, params.c))
    alpha = max(0.0, params.alpha)

    # Positive quadrant points
    theta_u = theta_y + a
    m_u = my * (1.0 + alpha)

    theta_r = theta_y + b
    m_r = my * c

    # Failure point where resistance drops to zero
    delta_f = max(0.005, 0.15 * (b if b > 0 else theta_y))
    theta_f = theta_r + delta_f

    pos_points = [
        BackbonePoint(theta_rad=round(0.0, 7), moment_knm=round(0.0, 4)),
        BackbonePoint(theta_rad=round(theta_y, 7), moment_knm=round(my, 4)),
        BackbonePoint(theta_rad=round(theta_u, 7), moment_knm=round(m_u, 4)),
        BackbonePoint(theta_rad=round(theta_r, 7), moment_knm=round(m_r, 4)),
        BackbonePoint(theta_rad=round(theta_f, 7), moment_knm=round(0.0, 4)),
    ]

    if not symmetric:
        return pos_points

    # Negative quadrant points (mirrored)
    neg_points = [
        BackbonePoint(theta_rad=round(-theta_f, 7), moment_knm=round(0.0, 4)),
        BackbonePoint(theta_rad=round(-theta_r, 7), moment_knm=round(-m_r, 4)),
        BackbonePoint(theta_rad=round(-theta_u, 7), moment_knm=round(-m_u, 4)),
        BackbonePoint(theta_rad=round(-theta_y, 7), moment_knm=round(-my, 4)),
    ]

    return neg_points + pos_points


def evaluate_performance_level(
    theta_demand: float,
    theta_y: float,
    params: HingeParameters,
) -> Tuple[str, float]:
    """Evaluate performance level (IO, LS, CP, COLLAPSE) and DCR against CP limit.
    
    Total rotation limits are defined as:
      theta_IO = theta_y + params.io_limit
      theta_LS = theta_y + params.ls_limit
      theta_CP = theta_y + params.cp_limit
      
    Args:
        theta_demand: Imposed rotation demand from nonlinear analysis (rad).
        theta_y: Yield rotation (rad).
        params: Hinge acceptance criteria parameters.
        
    Returns:
        Tuple of (performance_level_str, dcr_cp).
    """
    abs_demand = abs(theta_demand)
    theta_io = theta_y + params.io_limit
    theta_ls = theta_y + params.ls_limit
    theta_cp = theta_y + params.cp_limit

    dcr_cp = abs_demand / theta_cp if theta_cp > 0 else 999.0

    if abs_demand <= theta_io:
        level = PerformanceLevel.IO.value
    elif abs_demand <= theta_ls:
        level = PerformanceLevel.LS.value
    elif abs_demand <= theta_cp:
        level = PerformanceLevel.CP.value
    else:
        level = PerformanceLevel.COLLAPSE.value

    return level, round(dcr_cp, 4)


def create_hinge_performance_summary(
    member_id: int,
    member_type: str,
    my: float,
    theta_y: float,
    params: HingeParameters,
    demand_theta: Optional[float] = None,
    symmetric: bool = True,
) -> HingePerformance:
    """Build complete HingePerformance DTO combining backbone curve and performance evaluation.
    
    Args:
        member_id: Member unique ID.
        member_type: Type designation (e.g. RC_BEAM, STEEL_COLUMN).
        my: Yield moment or force.
        theta_y: Yield rotation or deformation.
        params: ASCE 41-17 / KDS 41 17 00 hinge parameters.
        demand_theta: Optional demand rotation to evaluate performance state.
        symmetric: Whether to output symmetric backbone curve.
        
    Returns:
        HingePerformance DTO.
    """
    curve = generate_backbone_curve(theta_y, my, params, symmetric=symmetric)
    
    io_limit_rad = round(theta_y + params.io_limit, 7)
    ls_limit_rad = round(theta_y + params.ls_limit, 7)
    cp_limit_rad = round(theta_y + params.cp_limit, 7)

    if demand_theta is not None:
        level, dcr = evaluate_performance_level(demand_theta, theta_y, params)
    else:
        level = PerformanceLevel.IO.value
        dcr = None

    return HingePerformance(
        member_id=member_id,
        member_type=member_type,
        my_knm=round(my, 4),
        theta_y_rad=round(theta_y, 7),
        io_limit_rad=io_limit_rad,
        ls_limit_rad=ls_limit_rad,
        cp_limit_rad=cp_limit_rad,
        backbone_curve=curve,
        performance_level=level,
        demand_theta_rad=demand_theta,
        dcr_cp=dcr,
    )
