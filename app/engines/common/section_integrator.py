# app/engines/common/section_integrator.py
"""Sutherland-Hodgman Polygon Clipping & Shoelace Section Integrator for 2D/3D P-M Analysis."""
import math
from typing import List, Dict, Any, Tuple


def clip_polygon_sutherland_hodgman(
    poly_y: List[float], 
    poly_z: List[float], 
    cosT: float, 
    sinT: float, 
    threshold: float
) -> Tuple[List[float], List[float]]:
    """
    Clips a 2D convex/concave polygon against a half-plane:
    (y * cosT + z * sinT - threshold >= 0).
    Returns (clipped_y, clipped_z).
    """
    n = len(poly_y)
    if n < 3:
        return [], []
        
    clipped_y: List[float] = []
    clipped_z: List[float] = []
    
    for i in range(n):
        j = (i + 1) % n
        gi = poly_y[i] * cosT + poly_z[i] * sinT - threshold
        gj = poly_y[j] * cosT + poly_z[j] * sinT - threshold
        in_i = (gi >= 0.0)
        in_j = (gj >= 0.0)
        
        if in_i:
            clipped_y.append(poly_y[i])
            clipped_z.append(poly_z[i])
            
        if in_i != in_j:
            # Intersection point
            denom = gi - gj
            if abs(denom) > 1e-12:
                t = gi / denom
                clipped_y.append(poly_y[i] + t * (poly_y[j] - poly_y[i]))
                clipped_z.append(poly_z[i] + t * (poly_z[j] - poly_z[i]))
                
    return clipped_y, clipped_z


def compute_polygon_shoelace(poly_y: List[float], poly_z: List[float]) -> Tuple[float, float, float]:
    """
    Computes (Area, Sy, Sz) for a polygon using Shoelace formula:
    Sy = integral(y * dA), Sz = integral(z * dA)
    """
    m = len(poly_y)
    if m < 3:
        return 0.0, 0.0, 0.0
        
    area2 = 0.0
    s6y = 0.0
    s6z = 0.0
    
    for i in range(m):
        j = (i + 1) % m
        cross = poly_y[i] * poly_z[j] - poly_y[j] * poly_z[i]
        area2 += cross
        s6y += (poly_y[i] + poly_y[j]) * cross
        s6z += (poly_z[i] + poly_z[j]) * cross
        
    area = area2 / 2.0
    Sy = s6y / 6.0
    Sz = s6z / 6.0
    return area, Sy, Sz


def integrate_concrete_stress_block(
    b: float,
    h: float,
    cosT: float,
    sinT: float,
    threshold: float,
    stress_intensity: float
) -> Tuple[float, float, float]:
    """
    Integrates concrete compressive stress block over a rectangular section [-h/2..h/2] x [-b/2..b/2].
    Returns (Cc, Mc_y, Mc_z).
    """
    vy = [-h / 2.0, h / 2.0, h / 2.0, -h / 2.0]
    vz = [-b / 2.0, -b / 2.0, b / 2.0, b / 2.0]
    
    cy, cz = clip_polygon_sutherland_hodgman(vy, vz, cosT, sinT, threshold)
    area, Sy, Sz = compute_polygon_shoelace(cy, cz)
    
    Cc = stress_intensity * area
    Mc_y = stress_intensity * Sy  # Muz component
    Mc_z = stress_intensity * Sz  # Muy component
    return Cc, Mc_y, Mc_z
