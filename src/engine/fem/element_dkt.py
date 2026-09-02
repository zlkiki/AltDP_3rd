"""
src/engine/fem/element_dkt.py
=============================
DKT (Discrete Kirchhoff Triangle) 3-Node Plate Bending Element.

Features:
- 3-node triangular plate bending element with 3 DOFs per node: [w, th_x, th_y] (9 DOFs total)
- Batoz formulation (1982) with complete Kirchhoff kinematic coupling
- 3-point Gauss numerical integration
"""

import numpy as np
from typing import Tuple, Dict, Any


# 3-point Hammer integration rule on standard triangle
INT_POINTS = [
    (1.0 / 6.0, 1.0 / 6.0),
    (2.0 / 3.0, 1.0 / 6.0),
    (1.0 / 6.0, 2.0 / 3.0)
]
INT_WEIGHT = 1.0 / 6.0


def compute_dkt_stiffness(
    coords: np.ndarray,
    thickness: float,
    E: float,
    nu: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute 9x9 element stiffness matrix Ke for DKT plate bending element using Batoz formulation.
    
    Args:
        coords: 3x2 array [[x1, y1], [x2, y2], [x3, y3]] in CCW order
        thickness: Plate thickness (m)
        E: Young's Modulus
        nu: Poisson's ratio
        
    Returns:
        Ke: 9x9 element stiffness matrix
        Db: 3x3 constitutive matrix
    """
    x = coords[:, 0]
    y = coords[:, 1]
    
    # Side vectors (edges: 4=1-2, 5=2-3, 6=3-1)
    x12 = x[0] - x[1]
    x23 = x[1] - x[2]
    x31 = x[2] - x[0]
    
    y12 = y[0] - y[1]
    y23 = y[1] - y[2]
    y31 = y[2] - y[0]
    
    # Triangle Area (2A = det)
    two_area = x[0] * (y[1] - y[2]) + x[1] * (y[2] - y[0]) + x[2] * (y[0] - y[1])
    if two_area <= 0.0:
        raise ValueError(f"Invalid triangle geometry (2*Area = {two_area} <= 0). Ensure CCW node ordering.")
    
    area = 0.5 * two_area
    t = float(thickness)
    D_factor = (E * t**3) / (12.0 * (1.0 - nu**2))
    Db = D_factor * np.array([
        [1.0, nu, 0.0],
        [nu, 1.0, 0.0],
        [0.0, 0.0, (1.0 - nu) / 2.0]
    ])
    
    # Side lengths squared
    l4_sq = x12**2 + y12**2
    l5_sq = x23**2 + y23**2
    l6_sq = x31**2 + y31**2
    
    # Coefficients for edges 4, 5, 6
    # Edge 4 (1-2)
    a4 = -y12 / l4_sq
    b4 = 0.75 * x12 * y12 / l4_sq
    c4 = (0.25 * x12**2 - 0.5 * y12**2) / l4_sq
    d4 = -x12 / l4_sq
    e4 = (0.25 * y12**2 - 0.5 * x12**2) / l4_sq
    
    # Edge 5 (2-3)
    a5 = -y23 / l5_sq
    b5 = 0.75 * x23 * y23 / l5_sq
    c5 = (0.25 * x23**2 - 0.5 * y23**2) / l5_sq
    d5 = -x23 / l5_sq
    e5 = (0.25 * y23**2 - 0.5 * x23**2) / l5_sq
    
    # Edge 6 (3-1)
    a6 = -y31 / l6_sq
    b6 = 0.75 * x31 * y31 / l6_sq
    c6 = (0.25 * x31**2 - 0.5 * y31**2) / l6_sq
    d6 = -x31 / l6_sq
    e6 = (0.25 * y31**2 - 0.5 * x31**2) / l6_sq
    
    # Area coordinate derivatives: dL/dx = y_jk / 2A, dL/dy = -x_jk / 2A
    P = np.array([y23, y31, y12]) / two_area   # dL_i / dx
    Q = np.array([-x23, -x31, -x12]) / two_area # dL_i / dy
    
    Ke = np.zeros((9, 9))
    
    for (xi, eta) in INT_POINTS:
        L1 = xi
        L2 = eta
        L3 = 1.0 - L1 - L2
        
        # Batoz Hx and Hy shape function derivatives w.r.t L1, L2, L3
        # Node 1, 2, 3 DOFs: [w1, thx1, thy1, w2, thx2, thy2, w3, thx3, thy3]
        # Intermediate shape functions:
        N4 = 4.0 * L1 * L2
        N5 = 4.0 * L2 * L3
        N6 = 4.0 * L3 * L1
        
        # Derivatives w.r.t xi (L1) and eta (L2)
        # dN/dxi:
        dN4_xi = 4.0 * L2
        dN5_xi = -4.0 * L2
        dN6_xi = 4.0 * (L3 - L1)
        
        # dN/deta:
        dN4_eta = 4.0 * L1
        dN5_eta = 4.0 * (L3 - L2)
        dN6_eta = -4.0 * L1
        
        # Formulate Hx and Hy vectors (9-components)
        # Hx for w_i, thx_i, thy_i
        # dHx/dxi and dHx/deta, dHy/dxi and dHy/deta
        dHx_xi = np.array([
            1.5 * (a4 * dN4_xi - a6 * dN6_xi),
            b4 * dN4_xi + b6 * dN6_xi,
            c4 * dN4_xi + c6 * dN6_xi - (1.0 - 2.0*L1),
            1.5 * (a5 * dN5_xi - a4 * dN4_xi),
            b5 * dN5_xi + b4 * dN4_xi,
            c5 * dN5_xi + c4 * dN4_xi,
            1.5 * (a6 * dN6_xi - a5 * dN5_xi),
            b6 * dN6_xi + b5 * dN5_xi,
            c6 * dN6_xi + c5 * dN5_xi + (1.0 - 2.0*L3)
        ])
        
        dHx_eta = np.array([
            1.5 * (a4 * dN4_eta - a6 * dN6_eta),
            b4 * dN4_eta + b6 * dN6_eta,
            c4 * dN4_eta + c6 * dN6_eta,
            1.5 * (a5 * dN5_eta - a4 * dN4_eta),
            b5 * dN5_eta + b4 * dN4_eta,
            c5 * dN5_eta + c4 * dN4_eta - (1.0 - 2.0*L2),
            1.5 * (a6 * dN6_eta - a5 * dN5_eta),
            b6 * dN6_eta + b5 * dN5_eta,
            c6 * dN6_eta + c5 * dN5_eta + (1.0 - 2.0*L3)
        ])
        
        dHy_xi = np.array([
            1.5 * (d4 * dN4_xi - d6 * dN6_xi),
            -c4 * dN4_xi - c6 * dN6_xi + (1.0 - 2.0*L1),
            -b4 * dN4_xi - b6 * dN6_xi,
            1.5 * (d5 * dN5_xi - d4 * dN4_xi),
            -c5 * dN5_xi - c4 * dN4_xi,
            -b5 * dN5_xi - b4 * dN4_xi,
            1.5 * (d6 * dN6_xi - d5 * dN5_xi),
            -c6 * dN6_xi - c5 * dN5_xi - (1.0 - 2.0*L3),
            -b6 * dN6_xi - b5 * dN5_xi
        ])
        
        dHy_eta = np.array([
            1.5 * (d4 * dN4_eta - d6 * dN6_eta),
            -c4 * dN4_eta - c6 * dN6_eta,
            -b4 * dN4_eta - b6 * dN6_eta,
            1.5 * (d5 * dN5_eta - d4 * dN4_eta),
            -c5 * dN5_eta - c4 * dN4_eta + (1.0 - 2.0*L2),
            -b5 * dN5_eta - b4 * dN4_eta,
            1.5 * (d6 * dN6_eta - d5 * dN5_eta),
            -c6 * dN6_eta - c5 * dN5_eta - (1.0 - 2.0*L3),
            -b6 * dN6_eta - b5 * dN5_eta
        ])
        
        # Chain rule to convert (xi, eta) derivatives to (x, y):
        # d/dx = P[0] * d/dxi + P[1] * d/deta
        # d/dy = Q[0] * d/dxi + Q[1] * d/deta
        dHx_dx = P[0] * dHx_xi + P[1] * dHx_eta
        dHx_dy = Q[0] * dHx_xi + Q[1] * dHx_eta
        dHy_dx = P[0] * dHy_xi + P[1] * dHy_eta
        dHy_dy = Q[0] * dHy_xi + Q[1] * dHy_eta
        
        # Curvature strain-displacement matrix Bb (3x9)
        # kappa = [d(thx)/dx, d(thy)/dy, d(thx)/dy + d(thy)/dx]
        Bb = np.zeros((3, 9))
        Bb[0, :] = dHx_dx
        Bb[1, :] = dHy_dy
        Bb[2, :] = dHx_dy + dHy_dx
        
        Ke += (Bb.T @ Db @ Bb) * (area * INT_WEIGHT * 2.0)
        
    return Ke, Db
