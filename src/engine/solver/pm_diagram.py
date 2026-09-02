"""3D P-M Interaction Diagram & DCR Solver for AltDP_3rd.

Generates 2D/3D nominal and design P-M-M interaction surfaces and evaluates
structural demand-capacity ratios (DCR) for RC column sections according to KDS 14 20 20.
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Dict, Any, Optional

from src.engine.materials import get_phi_flexure
from src.engine.solver.fiber_section import FiberSection, SectionForceResult


@dataclass
class PMCurvePoint:
    """Individual coordinate on the P-M interaction curve."""
    Pn: float                  # kN (Nominal axial capacity)
    Mn: float                  # kN*m (Nominal moment capacity)
    phi_Pn: float              # kN (Design axial capacity)
    phi_Mn: float              # kN*m (Design moment capacity)
    c: float                   # mm (Neutral axis depth)
    et: float                  # Net tensile strain
    phi: float                 # Strength reduction factor
    theta: float = 0.0         # rad (Angle of neutral axis)


@dataclass
class PMDiagramResult:
    """Complete P-M interaction envelope and properties."""
    theta: float               # rad
    Po: float                  # kN (Nominal pure compression)
    Pt: float                  # kN (Nominal pure tension, negative)
    Pn_max: float              # kN (Upper limit nominal axial load)
    phi_Pn_max: float          # kN (Upper limit design axial load)
    phi_Pt: float              # kN (Design pure tension)
    points: List[PMCurvePoint] # Sequence from pure compression to pure tension


class PMDiagramSolver:
    """2D & 3D P-M Interaction Diagram Generator and DCR Evaluator."""

    @staticmethod
    def generate_2d_diagram(
        sec: FiberSection,
        theta: float = 0.0,
        num_points: int = 40,
        is_spiral: bool = False
    ) -> PMDiagramResult:
        """Generate a 2D P-M interaction curve at neutral axis angle theta.
        
        Args:
            sec: Initialized FiberSection.
            theta: Angle of bending axis in radians (0 = X-axis bending).
            num_points: Number of sampling points along the curve.
            is_spiral: True for spiral column, False for tied column.
            
        Returns:
            PMDiagramResult with ordered list of PMCurvePoints.
        """
        # 1. Pure axial capacities
        Po = sec.compute_pure_compression()
        Pt = sec.compute_pure_tension()
        
        reduction_axial = 0.85 if is_spiral else 0.80
        phi_axial = 0.70 if is_spiral else 0.65
        phi_tension = 0.85
        
        Pn_max = reduction_axial * Po
        phi_Pn_max = phi_axial * Pn_max
        phi_Pt = phi_tension * Pt
        
        # Determine depth in direction of theta
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        all_u = [f.y * cos_t + f.x * sin_t for f in sec.concrete_fibers]
        h_eff = (max(all_u) - min(all_u)) if all_u else 500.0
        
        points: List[PMCurvePoint] = []
        
        # Top Point: Pure Compression (capped)
        points.append(PMCurvePoint(
            Pn=Pn_max,
            Mn=0.0,
            phi_Pn=phi_Pn_max,
            phi_Mn=0.0,
            c=1e5,
            et=-0.002,
            phi=phi_axial,
            theta=theta
        ))
        
        # c-values sweep from 1.8 * h_eff down to 0.03 * h_eff
        c_values = []
        for i in range(num_points):
            frac = i / (num_points - 1)
            # Power distribution to concentrate points near balance point
            c_val = h_eff * (1.8 * ((1.0 - frac) ** 2.2) + 0.03)
            c_values.append(c_val)
            
        ey = sec.rebar_mat.ey
        
        for c in c_values:
            res = sec.compute_forces(c=c, theta=theta)
            # Resultant moment in the direction of theta
            Mn = res.Mx * cos_t + res.My * sin_t
            
            # Strength reduction factor phi
            phi = get_phi_flexure(et=res.et, ey=ey, is_spiral=is_spiral)
            
            # Apply upper limit on design compression
            phi_Pn = min(phi * res.P, phi_Pn_max)
            phi_Mn = phi * Mn
            
            points.append(PMCurvePoint(
                Pn=res.P,
                Mn=Mn,
                phi_Pn=phi_Pn,
                phi_Mn=phi_Mn,
                c=c,
                et=res.et,
                phi=phi,
                theta=theta
            ))
            
        # Bottom Point: Pure Tension
        points.append(PMCurvePoint(
            Pn=Pt,
            Mn=0.0,
            phi_Pn=phi_Pt,
            phi_Mn=0.0,
            c=0.0,
            et=0.05,
            phi=phi_tension,
            theta=theta
        ))
        
        return PMDiagramResult(
            theta=theta,
            Po=Po,
            Pt=Pt,
            Pn_max=Pn_max,
            phi_Pn_max=phi_Pn_max,
            phi_Pt=phi_Pt,
            points=points
        )

    @classmethod
    def generate_3d_surface(
        cls,
        sec: FiberSection,
        num_theta: int = 16,
        num_points_per_ray: int = 30,
        is_spiral: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate a 3D P-M-M interaction surface mesh data."""
        surface_slices = []
        for it in range(num_theta):
            theta = 2.0 * math.pi * it / num_theta
            res_2d = cls.generate_2d_diagram(sec, theta=theta, num_points=num_points_per_ray, is_spiral=is_spiral)
            
            slice_data = {
                "theta_deg": round(math.degrees(theta), 1),
                "points": [
                    {
                        "Pn": round(p.Pn, 2),
                        "Pnx": round(p.Mn * math.cos(theta), 2),
                        "Pny": round(p.Mn * math.sin(theta), 2),
                        "phi_Pn": round(p.phi_Pn, 2),
                        "phi_Mux": round(p.phi_Mn * math.cos(theta), 2),
                        "phi_Muy": round(p.phi_Mn * math.sin(theta), 2),
                        "phi": round(p.phi, 3)
                    }
                    for p in res_2d.points
                ]
            }
            surface_slices.append(slice_data)
        return surface_slices

    @classmethod
    def calculate_dcr(
        cls,
        sec: FiberSection,
        Pu: float,
        Mux: float,
        Muy: float,
        is_spiral: bool = False
    ) -> Dict[str, Any]:
        """Evaluate Demand-Capacity Ratio (DCR) for a 3D load point (Pu, Mux, Muy).
        
        Args:
            sec: FiberSection object.
            Pu: Factored axial load (kN, Positive = Compression).
            Mux: Factored bending moment about X-axis (kN*m).
            Muy: Factored bending moment about Y-axis (kN*m).
            is_spiral: True for spiral column.
            
        Returns:
            Dictionary containing DCR, phi_Mn_capacity, is_safe, and evaluation details.
        """
        Mu_resultant = math.sqrt(Mux**2 + Muy**2)
        theta = math.atan2(Muy, Mux) if Mu_resultant > 1e-4 else 0.0
        
        # Generate 2D curve in the direction of resultant moment
        diag = cls.generate_2d_diagram(sec, theta=theta, num_points=50, is_spiral=is_spiral)
        
        # 1. Axial capacity boundary check
        if Pu > diag.phi_Pn_max:
            return {
                "dcr": 999.0,
                "capacity_Mu": 0.0,
                "is_safe": False,
                "status": "NG_AXIAL_EXCEEDED",
                "phi_Pn_max": diag.phi_Pn_max,
                "phi_Pt": diag.phi_Pt,
                "theta_deg": math.degrees(theta)
            }
        elif Pu < diag.phi_Pt:
            return {
                "dcr": 999.0,
                "capacity_Mu": 0.0,
                "is_safe": False,
                "status": "NG_TENSION_EXCEEDED",
                "phi_Pn_max": diag.phi_Pn_max,
                "phi_Pt": diag.phi_Pt,
                "theta_deg": math.degrees(theta)
            }
            
        # 2. Pure axial compression check without moment
        if Mu_resultant <= 1e-4:
            dcr_axial = Pu / diag.phi_Pn_max if diag.phi_Pn_max > 0 else 0.0
            return {
                "dcr": round(max(0.0, dcr_axial), 3),
                "capacity_Mu": 0.0,
                "is_safe": dcr_axial <= 1.0,
                "status": "OK" if dcr_axial <= 1.0 else "NG",
                "phi_Pn_max": diag.phi_Pn_max,
                "phi_Pt": diag.phi_Pt,
                "theta_deg": math.degrees(theta)
            }
            
        # 3. Find capacity_Mu at the given Pu on design envelope
        capacity_Mu = 0.0
        pts = diag.points
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i + 1]
            if (p1.phi_Pn >= Pu >= p2.phi_Pn) or (p2.phi_Pn >= Pu >= p1.phi_Pn):
                denom = p2.phi_Pn - p1.phi_Pn
                if abs(denom) > 1e-4:
                    t = (Pu - p1.phi_Pn) / denom
                    capacity_Mu = p1.phi_Mn + t * (p2.phi_Mn - p1.phi_Mn)
                    break
                else:
                    capacity_Mu = max(p1.phi_Mn, p2.phi_Mn)
                    break
                    
        if capacity_Mu <= 1e-4:
            capacity_Mu = max(p.phi_Mn for p in pts)
            
        dcr = Mu_resultant / capacity_Mu if capacity_Mu > 0 else 999.0
        is_safe = (dcr <= 1.0) and (Pu <= diag.phi_Pn_max)
        
        return {
            "dcr": round(dcr, 3),
            "demand_Mu": round(Mu_resultant, 2),
            "capacity_Mu": round(capacity_Mu, 2),
            "is_safe": is_safe,
            "status": "OK" if is_safe else "NG",
            "phi_Pn_max": round(diag.phi_Pn_max, 2),
            "phi_Pt": round(diag.phi_Pt, 2),
            "theta_deg": round(math.degrees(theta), 2)
        }
