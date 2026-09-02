"""Fiber Section Numerical Integration Solver for AltDP_3rd.

Implements nonlinear fiber section discretization and stress-strain integration
for RC columns and arbitrary cross-sections under axial load and biaxial bending.
Complies with KDS 14 20 20 / ACI 318 and reverse engineered Midas Design+ solver logic.
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Optional, Union
from enum import Enum

from src.engine.materials import ConcreteMaterial, RebarMaterial


class MaterialType(str, Enum):
    CONCRETE = "concrete"
    REBAR = "rebar"


@dataclass
class Fiber:
    """Individual 2D fiber element with coordinates and area."""
    x: float               # mm (x-coordinate from section centroid)
    y: float               # mm (y-coordinate from section centroid)
    area: float            # mm2 (Fiber tributary area)
    material_type: MaterialType = MaterialType.CONCRETE
    
    # Optional material reference
    fck: float = 24.0      # MPa (Concrete compressive strength if concrete)
    fy: float = 400.0      # MPa (Yield strength if rebar)
    Es: float = 200000.0   # MPa (Elastic modulus if rebar)


@dataclass
class SectionForceResult:
    """Integrated section forces under strain profile (c, theta)."""
    P: float               # kN (Positive = Compression, Negative = Tension)
    Mx: float              # kN*m (Bending moment about X-axis)
    My: float              # kN*m (Bending moment about Y-axis)
    et: float              # Extreme tension steel strain (positive for tension)
    ec_max: float          # Maximum concrete compressive strain (positive)
    c: float               # mm (Neutral axis depth)
    theta: float           # rad (Neutral axis inclination angle)


class FiberSection:
    """Nonlinear Fiber Discretization and Stress Integration Engine."""

    def __init__(self, concrete: Optional[ConcreteMaterial] = None, rebar_mat: Optional[RebarMaterial] = None):
        self.concrete = concrete or ConcreteMaterial(fck=24.0)
        self.rebar_mat = rebar_mat or RebarMaterial(fy=400.0)
        self.concrete_fibers: List[Fiber] = []
        self.rebar_fibers: List[Fiber] = []
        
        # Section bounds
        self.x_min: float = 0.0
        self.x_max: float = 0.0
        self.y_min: float = 0.0
        self.y_max: float = 0.0

    @classmethod
    def from_rect(
        cls,
        b: float,
        h: float,
        rebars: List[Tuple[float, float, float]],  # List of (x, y, area)
        nx: int = 30,
        ny: int = 30,
        concrete: Optional[ConcreteMaterial] = None,
        rebar_mat: Optional[RebarMaterial] = None
    ) -> "FiberSection":
        """Create a rectangular fiber section centered at origin (0, 0).
        
        Args:
            b: Width in X-direction (mm)
            h: Height in Y-direction (mm)
            rebars: List of (x, y, area) for each longitudinal bar
            nx: Number of fiber divisions along X
            ny: Number of fiber divisions along Y
            concrete: Concrete material specification
            rebar_mat: Rebar material specification
        """
        sec = cls(concrete=concrete, rebar_mat=rebar_mat)
        sec.x_min, sec.x_max = -b / 2.0, b / 2.0
        sec.y_min, sec.y_max = -h / 2.0, h / 2.0
        
        dx = b / nx
        dy = h / ny
        dA = dx * dy
        
        # Generate concrete grid fibers
        for ix in range(nx):
            x = -b / 2.0 + (ix + 0.5) * dx
            for iy in range(ny):
                y = -h / 2.0 + (iy + 0.5) * dy
                sec.concrete_fibers.append(Fiber(
                    x=x, y=y, area=dA,
                    material_type=MaterialType.CONCRETE,
                    fck=sec.concrete.fck
                ))
                
        # Add rebar fibers
        for rx, ry, rarea in rebars:
            sec.rebar_fibers.append(Fiber(
                x=rx, y=ry, area=rarea,
                material_type=MaterialType.REBAR,
                fy=sec.rebar_mat.fy,
                Es=sec.rebar_mat.Es
            ))
            
        return sec

    @classmethod
    def from_circle(
        cls,
        diameter: float,
        rebars: List[Tuple[float, float, float]],
        n_rings: int = 15,
        n_theta: int = 36,
        concrete: Optional[ConcreteMaterial] = None,
        rebar_mat: Optional[RebarMaterial] = None
    ) -> "FiberSection":
        """Create a circular fiber section centered at origin (0, 0)."""
        sec = cls(concrete=concrete, rebar_mat=rebar_mat)
        R = diameter / 2.0
        sec.x_min, sec.x_max = -R, R
        sec.y_min, sec.y_max = -R, R
        
        dr = R / n_rings
        dth = 2.0 * math.pi / n_theta
        
        for ir in range(n_rings):
            r = (ir + 0.5) * dr
            dA = r * dr * dth
            for it in range(n_theta):
                th = (it + 0.5) * dth
                x = r * math.cos(th)
                y = r * math.sin(th)
                sec.concrete_fibers.append(Fiber(
                    x=x, y=y, area=dA,
                    material_type=MaterialType.CONCRETE,
                    fck=sec.concrete.fck
                ))
                
        for rx, ry, rarea in rebars:
            sec.rebar_fibers.append(Fiber(
                x=rx, y=ry, area=rarea,
                material_type=MaterialType.REBAR,
                fy=sec.rebar_mat.fy,
                Es=sec.rebar_mat.Es
            ))
            
        return sec

    @property
    def gross_concrete_area(self) -> float:
        """Total sum of concrete fiber areas (Ag)."""
        return sum(f.area for f in self.concrete_fibers)

    @property
    def total_rebar_area(self) -> float:
        """Total sum of rebar areas (Ast)."""
        return sum(f.area for f in self.rebar_fibers)

    def compute_pure_compression(self) -> float:
        """KDS 14 20 20 Nominal Pure Axial Compressive Capacity Po (kN).
        
        Po = 0.85 * fck * (Ag - Ast) + fy * Ast
        """
        Ag = self.gross_concrete_area
        Ast = self.total_rebar_area
        fck = self.concrete.fck
        fy = self.rebar_mat.fy
        Po_N = 0.85 * fck * (Ag - Ast) + fy * Ast
        return Po_N / 1e3

    def compute_pure_tension(self) -> float:
        """KDS 14 20 20 Nominal Pure Axial Tensile Capacity Pt (kN).
        
        Pt = -fy * Ast (Negative denotes tension)
        """
        Ast = self.total_rebar_area
        fy = self.rebar_mat.fy
        Pt_N = -fy * Ast
        return Pt_N / 1e3

    def compute_forces(
        self,
        c: float,
        theta: float = 0.0,
        ecu: Optional[float] = None
    ) -> SectionForceResult:
        """Compute integrated axial force P, Mx, My and extreme strains for given neutral axis.
        
        Coordinate System:
          - (x, y) coordinates on section.
          - Neutral axis inclined at angle theta (rad) with respect to X-axis.
          - Perpendicular distance from NA: d_perp = x * sin(theta) + y * cos(theta).
          - Top extreme compressive fiber distance from NA: d_max.
          - Strain: eps(x, y) = ecu * (d_perp_max - d_perp) / c
        
        Args:
            c: Neutral axis depth (mm) measured from extreme compression fiber.
            theta: Inclination angle of neutral axis in radians (0 = bending about X-axis).
            ecu: Ultimate concrete compressive strain (default from ConcreteMaterial).
            
        Returns:
            SectionForceResult containing P (kN), Mx (kN*m), My (kN*m), et, ec_max.
        """
        if ecu is None:
            ecu = self.concrete.ecu
            
        fck = self.concrete.fck
        alpha1 = self.concrete.alpha1
        beta1 = self.concrete.beta1
        
        # Calculate projection of every fiber onto the axis perpendicular to NA:
        # u = x * (-math.sin(theta)) + y * math.cos(theta)  (Normal direction)
        # Let normal vector n = (-sin(theta), cos(theta)) or (cos(theta), sin(theta))
        # Convention: theta=0 -> n = (0, 1), so u = y (y_max is extreme compression)
        # theta=pi/2 -> n = (1, 0), so u = x (x_max is extreme compression)
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        
        # Fiber projection u = y * cos_t + x * sin_t
        all_u_c = [f.y * cos_t + f.x * sin_t for f in self.concrete_fibers]
        u_max = max(all_u_c) if all_u_c else 0.0
        u_min = min(all_u_c) if all_u_c else 0.0
        
        # Extreme compression edge position = u_max
        # NA position: u_na = u_max - c
        u_na = u_max - c
        
        # Equivalent rectangular stress block depth a = beta1 * c
        # Active compression zone: u >= u_max - a and u >= u_na
        a = min(beta1 * c, u_max - u_min)
        u_stress_block = u_max - a
        
        P_N = 0.0
        Mx_Nmm = 0.0
        My_Nmm = 0.0
        
        # 1. Integrate Concrete Fibers
        # Using Whitney Stress Block: sigma_c = alpha1 * fck for u >= u_stress_block
        if c > 1e-4:
            for i, f in enumerate(self.concrete_fibers):
                u_i = all_u_c[i]
                if u_i >= u_stress_block:
                    # Compression force (Positive)
                    fc_i = alpha1 * fck * f.area
                    P_N += fc_i
                    Mx_Nmm += fc_i * f.y
                    My_Nmm += fc_i * f.x
                    
        # 2. Integrate Rebar Fibers
        et_extreme = -999.0
        for f in self.rebar_fibers:
            u_s = f.y * cos_t + f.x * sin_t
            
            # Strain at rebar
            if c > 1e-4:
                strain_s = ecu * (u_s - u_na) / c
            else:
                # Pure tension or infinite tension strain
                strain_s = -0.010
                
            # Extreme tensile strain (positive value)
            if -strain_s > et_extreme:
                et_extreme = -strain_s
                
            # Elastic-perfectly plastic stress (Positive = Comp, Negative = Tens)
            stress_s = max(min(strain_s * f.Es, f.fy), -f.fy)
            
            # Displaced concrete correction if rebar is in compression zone
            if c > 1e-4 and u_s >= u_stress_block:
                stress_s -= alpha1 * fck
                
            fs_force = stress_s * f.area
            P_N += fs_force
            Mx_Nmm += fs_force * f.y
            My_Nmm += fs_force * f.x
            
        P_kN = P_N / 1e3
        Mx_kNm = Mx_Nmm / 1e6
        My_kNm = My_Nmm / 1e6
        
        return SectionForceResult(
            P=P_kN,
            Mx=Mx_kNm,
            My=My_kNm,
            et=et_extreme if et_extreme != -999.0 else 0.0,
            ec_max=ecu if c > 0 else 0.0,
            c=c,
            theta=theta
        )
