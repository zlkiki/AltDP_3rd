"""
src/engine/fem/element_dkmq.py
==============================
MITC4 (Mixed Interpolation of Tensorial Components) 4-Node Plate Bending Element.

Features:
- Bathe's standard MITC4 formulation (Zero shear locking for both thin and thick plates)
- 4 nodes, 3 DOFs per node: [w, th_x, th_y] (12 DOFs total)
  * w: out-of-plane displacement
  * th_x: rotation of normal in X (th_x = dw/dx in thin limit)
  * th_y: rotation of normal in Y (th_y = dw/dy in thin limit)
- 2x2 Gauss numerical integration for bending and tying edge shear strains
"""

import numpy as np
from typing import Tuple, Dict, Any


GAUSS_POINTS = [-1.0 / np.sqrt(3.0), 1.0 / np.sqrt(3.0)]
GAUSS_WEIGHTS = [1.0, 1.0]


def get_shape_functions(xi: float, eta: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Bilinear shape functions and natural derivatives."""
    N = 0.25 * np.array([
        (1 - xi) * (1 - eta),
        (1 + xi) * (1 - eta),
        (1 + xi) * (1 + eta),
        (1 - xi) * (1 + eta)
    ])
    dNdxi = 0.25 * np.array([
        -(1 - eta),
         (1 - eta),
         (1 + eta),
        -(1 + eta)
    ])
    dNdeta = 0.25 * np.array([
        -(1 - xi),
        -(1 + xi),
         (1 + xi),
         (1 - xi)
    ])
    return N, dNdxi, dNdeta


def compute_dkmq_stiffness(
    coords: np.ndarray,
    thickness: float,
    E: float,
    nu: float,
    shear_correction: float = 5.0 / 6.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute 12x12 stiffness matrix Ke using MITC4 formulation.
    """
    t = float(thickness)
    G = E / (2.0 * (1.0 + nu))
    
    # Bending Constitutive Matrix Db
    D_factor = (E * t**3) / (12.0 * (1.0 - nu**2))
    Db = D_factor * np.array([
        [1.0, nu, 0.0],
        [nu, 1.0, 0.0],
        [0.0, 0.0, (1.0 - nu) / 2.0]
    ])
    
    # Shear Constitutive Matrix Ds
    Ds = shear_correction * G * t * np.eye(2)
    
    # Edge vectors for MITC4 tying points
    # Edge 1: node 0 -> 1 (eta = -1)
    # Edge 2: node 1 -> 2 (xi = 1)
    # Edge 3: node 3 -> 2 (eta = 1)
    # Edge 4: node 0 -> 3 (xi = -1)
    x = coords[:, 0]
    y = coords[:, 1]
    
    Ke = np.zeros((12, 12))
    
    for i, xi in enumerate(GAUSS_POINTS):
        w_xi = GAUSS_WEIGHTS[i]
        for j, eta in enumerate(GAUSS_POINTS):
            w_eta = GAUSS_WEIGHTS[j]
            
            N, dNdxi, dNdeta = get_shape_functions(xi, eta)
            
            J = np.zeros((2, 2))
            J[0, 0] = np.dot(dNdxi, x)
            J[0, 1] = np.dot(dNdxi, y)
            J[1, 0] = np.dot(dNdeta, x)
            J[1, 1] = np.dot(dNdeta, y)
            
            detJ = np.linalg.det(J)
            if detJ <= 0:
                raise ValueError(f"Invalid element geometry (detJ = {detJ} <= 0).")
            invJ = np.linalg.inv(J)
            
            # Spatial derivatives of shape functions
            dN_spatial = np.zeros((4, 2))
            for k in range(4):
                dN_spatial[k, :] = invJ @ np.array([dNdxi[k], dNdeta[k]])
                
            # 1. Bending B-Matrix (Bb: 3x12)
            # kappa = [d(th_x)/dx, d(th_y)/dy, d(th_x)/dy + d(th_y)/dx]
            Bb = np.zeros((3, 12))
            for k in range(4):
                dNx = dN_spatial[k, 0]
                dNy = dN_spatial[k, 1]
                idx = 3 * k
                Bb[0, idx + 1] = dNx
                Bb[1, idx + 2] = dNy
                Bb[2, idx + 1] = dNy
                Bb[2, idx + 2] = dNx
                
            # 2. MITC4 Shear B-Matrix in natural coordinates (B_gamma_nat: 2x12)
            # gamma_xi = (1 - eta)/2 * gamma_xi^(A) + (1 + eta)/2 * gamma_xi^(C)
            # gamma_eta = (1 - xi)/2 * gamma_eta^(D) + (1 + xi)/2 * gamma_eta^(B)
            # Edge A (0->1): (w1 - w0)/2 - (x1-x0)/4 * (thx0+thx1) - (y1-y0)/4 * (thy0+thy1)
            # Edge C (3->2): (w2 - w3)/2 - (x2-x3)/4 * (thx3+thx2) - (y2-y3)/4 * (thy3+thy2)
            # Edge B (1->2): (w2 - w1)/2 - (x2-x1)/4 * (thx1+thx2) - (y2-y1)/4 * (thy1+thy2)
            # Edge D (0->3): (w3 - w0)/2 - (x3-x0)/4 * (thx0+thx3) - (y3-y0)/4 * (thy0+thy3)
            
            B_nat = np.zeros((2, 12))
            
            # gamma_xi at edge A (0-1)
            B_A = np.zeros(12)
            B_A[0] = -0.5
            B_A[3] = 0.5
            B_A[1] = -0.25 * (x[1] - x[0])
            B_A[4] = -0.25 * (x[1] - x[0])
            B_A[2] = -0.25 * (y[1] - y[0])
            B_A[5] = -0.25 * (y[1] - y[0])
            
            # gamma_xi at edge C (3-2)
            B_C = np.zeros(12)
            B_C[9] = -0.5
            B_C[6] = 0.5
            B_C[10] = -0.25 * (x[2] - x[3])
            B_C[7] = -0.25 * (x[2] - x[3])
            B_C[11] = -0.25 * (y[2] - y[3])
            B_C[8] = -0.25 * (y[2] - y[3])
            
            # gamma_eta at edge B (1-2)
            B_B = np.zeros(12)
            B_B[3] = -0.5
            B_B[6] = 0.5
            B_B[4] = -0.25 * (x[2] - x[1])
            B_B[7] = -0.25 * (x[2] - x[1])
            B_B[5] = -0.25 * (y[2] - y[1])
            B_B[8] = -0.25 * (y[2] - y[1])
            
            # gamma_eta at edge D (0-3)
            B_D = np.zeros(12)
            B_D[0] = -0.5
            B_D[9] = 0.5
            B_D[1] = -0.25 * (x[3] - x[0])
            B_D[10] = -0.25 * (x[3] - x[0])
            B_D[2] = -0.25 * (y[3] - y[0])
            B_D[11] = -0.25 * (y[3] - y[0])
            
            B_nat[0, :] = 0.5 * (1.0 - eta) * B_A + 0.5 * (1.0 + eta) * B_C
            B_nat[1, :] = 0.5 * (1.0 - xi) * B_D + 0.5 * (1.0 + xi) * B_B
            
            # Transform natural shear strains to physical coordinates: [gamma_xz, gamma_yz] = invJ^T @ [gamma_xi, gamma_eta]
            Bs = invJ.T @ B_nat
            
            dV = detJ * w_xi * w_eta
            Ke += (Bb.T @ Db @ Bb + Bs.T @ Ds @ Bs) * dV
            
    return Ke, Db


def compute_dkmq_internal_forces(
    coords: np.ndarray,
    thickness: float,
    E: float,
    nu: float,
    u_elem: np.ndarray
) -> Dict[str, float]:
    """Recover internal moments at element center."""
    t = float(thickness)
    D_factor = (E * t**3) / (12.0 * (1.0 - nu**2))
    Db = D_factor * np.array([
        [1.0, nu, 0.0],
        [nu, 1.0, 0.0],
        [0.0, 0.0, (1.0 - nu) / 2.0]
    ])
    
    x = coords[:, 0]
    y = coords[:, 1]
    
    N, dNdxi, dNdeta = get_shape_functions(0.0, 0.0)
    J = np.zeros((2, 2))
    J[0, 0] = np.dot(dNdxi, x)
    J[0, 1] = np.dot(dNdxi, y)
    J[1, 0] = np.dot(dNdeta, x)
    J[1, 1] = np.dot(dNdeta, y)
    invJ = np.linalg.inv(J)
    
    dN_spatial = np.zeros((4, 2))
    for k in range(4):
        dN_spatial[k, :] = invJ @ np.array([dNdxi[k], dNdeta[k]])
        
    Bb = np.zeros((3, 12))
    for k in range(4):
        dNx = dN_spatial[k, 0]
        dNy = dN_spatial[k, 1]
        idx = 3 * k
        Bb[0, idx + 1] = dNx
        Bb[1, idx + 2] = dNy
        Bb[2, idx + 1] = dNy
        Bb[2, idx + 2] = dNx
        
    kappa = Bb @ u_elem
    moments = Db @ kappa
    
    return {
        "Mxx": float(moments[0]),
        "Myy": float(moments[1]),
        "Mxy": float(moments[2]),
        "Vxz": float(abs(moments[0]) / 0.5),
        "Vyz": float(abs(moments[1]) / 0.5)
    }
