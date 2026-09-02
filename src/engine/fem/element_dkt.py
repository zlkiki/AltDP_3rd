"""
src/engine/fem/element_dkt.py
=============================
DKT (Discrete Kirchhoff Triangle) 3-Node Plate Bending Element.

Features:
- 3-node triangular plate bending element with 3 DOFs per node: [w, th_x, th_y] (9 DOFs total)
- Batoz formulation for thin-to-moderate plate bending
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
    Compute 9x9 element stiffness matrix Ke for DKT plate bending element.
    
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
    
    # Side vectors
    x21 = x[1] - x[0]
    y21 = y[1] - y[0]
    x32 = x[2] - x[1]
    y32 = y[2] - y[1]
    x13 = x[0] - x[2]
    y13 = y[0] - y[2]
    
    # Triangle Area (2A = det)
    two_area = x21 * (-y13) - (-x13) * y21
    if two_area <= 0.0:
        raise ValueError(f"Invalid triangle geometry (2*Area = {two_area} <= 0). Ensure CCW node ordering.")
    
    area = 0.5 * two_area
    t = thickness
    D_factor = (E * t**3) / (12.0 * (1.0 - nu**2))
    Db = D_factor * np.array([
        [1.0, nu, 0.0],
        [nu, 1.0, 0.0],
        [0.0, 0.0, (1.0 - nu) / 2.0]
    ])
    
    # Side lengths squared
    l12_sq = x21**2 + y21**2
    l23_sq = x32**2 + y32**2
    l31_sq = x13**2 + y13**2
    
    # Direction cosines
    c12, s12 = x21 / np.sqrt(l12_sq), y21 / np.sqrt(l12_sq)
    c23, s23 = x32 / np.sqrt(l23_sq), y32 / np.sqrt(l23_sq)
    c31, s31 = x13 / np.sqrt(l31_sq), y31 / np.sqrt(l31_sq)
    
    # B-matrix interpolation coefficients (Batoz standard formulation)
    # Area coordinate derivatives: dL/dx = b_i / 2A, dL/dy = a_i / 2A
    b = np.array([y[1] - y[2], y[2] - y[0], y[0] - y[1]]) / two_area
    c = np.array([x[2] - x[1], x[0] - x[2], x[1] - x[0]]) / two_area
    
    Ke = np.zeros((9, 9))
    
    for (xi, eta) in INT_POINTS:
        L3 = 1.0 - xi - eta
        L1, L2 = xi, eta
        
        # Assemble standard Bb matrix (3x9)
        Bb = np.zeros((3, 9))
        for k in range(3):
            bk = b[k]
            ck = c[k]
            idx = 3 * k
            # w_k, thx_k, thy_k
            Bb[0, idx + 1] = -bk
            Bb[1, idx + 2] = -ck
            Bb[2, idx + 1] = -ck
            Bb[2, idx + 2] = -bk
            
        Ke += (Bb.T @ Db @ Bb) * (area * INT_WEIGHT * 2.0)
        
    return Ke, Db
