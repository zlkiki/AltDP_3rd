"""RC Column Design & P-M Interaction Module (KDS 14 20 00 / ACI 318) for AltDP_3rd.

Calculates axial capacity (Pn_max), generates P-M interaction diagrams,
and verifies structural capacity under combined axial compression and bending.
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Dict, Any

from src.engine.db.materials import ConcreteMaterial, RebarMaterial, get_phi_flexure


@dataclass
class RCColumnInput:
    """RC Column Geometry, Rebar Layout, and Design Forces."""
    name: str = "C1"
    b: float = 600.0           # mm (Width)
    h: float = 600.0           # mm (Height / Depth)
    cover: float = 60.0        # mm (Clear cover to rebar centroid)
    
    # Rebar details: e.g. 12-D25 (4 corner + 4 face bars)
    bar_diam: float = 25.0     # mm
    num_bars_x: int = 4        # Bars along X-face
    num_bars_y: int = 4        # Bars along Y-face
    total_bars: int = 12       # Total number of longitudinal bars
    
    # Factored Design Forces
    Pu: float = 2500.0         # kN (Factored axial load)
    Mu: float = 350.0          # kN*m (Factored bending moment)
    Vu: float = 120.0          # kN (Factored shear force)
    
    is_spiral: bool = False    # True if spiral column, False if tied
    
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=30.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))

    @property
    def Ast(self) -> float:
        """Total longitudinal rebar area (mm2)."""
        single_bar_area = math.pi * (self.bar_diam ** 2) / 4.0
        return self.total_bars * single_bar_area

    @property
    def Ag(self) -> float:
        """Gross section area (mm2)."""
        return self.b * self.h


@dataclass
class PMPoint:
    """P-M Diagram Coordinate Point."""
    Pn: float                  # kN (Nominal axial capacity)
    Mn: float                  # kN*m (Nominal moment capacity)
    phi_Pn: float              # kN (Design axial capacity)
    phi_Mn: float              # kN*m (Design moment capacity)
    c: float                   # mm (Neutral axis depth)
    et: float                  # Net tensile strain
    phi: float                 # Reduction factor


@dataclass
class RCColumnResult:
    """RC Column Design Output."""
    Ag: float                  # mm2
    Ast: float                 # mm2
    rho_g: float               # Ast / Ag (Reinforcement ratio)
    Pn_max: float              # kN (Maximum nominal axial capacity)
    phi_Pn_max: float          # kN (Maximum design axial capacity)
    
    # P-M Interaction Diagram points
    pm_curve: List[PMPoint]
    
    # Capacity evaluation for the given (Pu, Mu) point
    capacity_Mu: float         # kN*m (Available phi_Mn at design Pu)
    dcr: float                 # Demand-Capacity Ratio (Mu / capacity_Mu)
    is_safe: bool
    summary: str


def design_rc_column(inp: RCColumnInput, num_points: int = 30) -> RCColumnResult:
    """Generate P-M interaction diagram and evaluate safety for an RC column."""
    b = inp.b
    h = inp.h
    Ag = inp.Ag
    Ast = inp.Ast
    rho_g = Ast / Ag
    fck = inp.concrete.fck
    fy = inp.rebar.fy
    Es = inp.rebar.Es
    ecu = inp.concrete.ecu
    alpha1 = inp.concrete.alpha1
    beta1 = inp.concrete.beta1
    
    # Max Axial Capacity (KDS 14 20 10)
    # Po = 0.85 * fck * (Ag - Ast) + fy * Ast
    Po_N = 0.85 * fck * (Ag - Ast) + fy * Ast
    reduction_factor_axial = 0.85 if inp.is_spiral else 0.80
    phi_axial = 0.70 if inp.is_spiral else 0.65
    
    Pn_max_N = reduction_factor_axial * Po_N
    Pn_max = Pn_max_N / 1e3
    phi_Pn_max = phi_axial * Pn_max
    
    # Discretize rebar layers along depth h
    d_top = inp.cover
    d_bot = h - inp.cover
    d_mid = h / 2.0
    
    # Rebar layer distribution approximation (Top, Mid, Bot)
    # E.g., for 12 bars: 4 top, 4 bot, 4 distributed in web
    bars_top = inp.num_bars_x
    bars_bot = inp.num_bars_x
    bars_side = inp.total_bars - bars_top - bars_bot
    
    single_bar_area = math.pi * (inp.bar_diam ** 2) / 4.0
    layers = [
        (d_top, bars_top * single_bar_area),
        (d_bot, bars_bot * single_bar_area)
    ]
    if bars_side > 0:
        layers.append((d_mid, bars_side * single_bar_area))
        
    # Generate P-M Curve points by varying c from 2*h down to 0.05*h
    c_values = [h * (0.05 + 1.95 * (i / (num_points - 1))**1.5) for i in range(num_points)]
    c_values.reverse()
    
    pm_points: List[PMPoint] = []
    
    # Add pure compression point
    pm_points.append(PMPoint(
        Pn=Pn_max,
        Mn=0.0,
        phi_Pn=phi_Pn_max,
        phi_Mn=0.0,
        c=9999.0,
        et=-0.002,
        phi=phi_axial
    ))
    
    for c in c_values:
        # Concrete compressive force
        a = min(beta1 * c, h)
        Cc = alpha1 * fck * b * a  # N
        yc = h / 2.0 - a / 2.0     # distance from plastic centroid (center)
        
        Pn_N = Cc
        Mn_Nmm = Cc * yc
        
        et_extreme = 0.0
        for d_i, As_i in layers:
            strain_i = ecu * (c - d_i) / c
            if d_i == d_bot:
                et_extreme = -strain_i  # positive tension strain
                
            # Elastic-perfectly plastic steel stress
            stress_i = max(min(strain_i * Es, fy), -fy)
            
            # Net force
            Fs_i = stress_i * As_i
            # If in compression zone, subtract concrete area displaced
            if d_i <= a:
                Fs_i -= 0.85 * fck * As_i
                
            Pn_N += Fs_i
            Mn_Nmm += Fs_i * (h / 2.0 - d_i)
            
        ey = fy / Es
        phi = get_phi_flexure(et_extreme, ey)
        if not inp.is_spiral and phi < 0.65:
            phi = 0.65
            
        Pn_kN = Pn_N / 1e3
        Mn_kNm = Mn_Nmm / 1e6
        
        phi_Pn_kN = min(phi * Pn_kN, phi_Pn_max)
        phi_Mn_kNm = phi * Mn_kNm
        
        pm_points.append(PMPoint(
            Pn=Pn_kN,
            Mn=Mn_kNm,
            phi_Pn=phi_Pn_kN,
            phi_Mn=phi_Mn_kNm,
            c=c,
            et=et_extreme,
            phi=phi
        ))
        
    # Capacity evaluation for the given Pu
    # Find capacity_Mu on the design envelope at Pu
    capacity_Mu = 0.0
    for i in range(len(pm_points) - 1):
        p1 = pm_points[i]
        p2 = pm_points[i + 1]
        if (p1.phi_Pn >= inp.Pu >= p2.phi_Pn) or (p2.phi_Pn >= inp.Pu >= p1.phi_Pn):
            if abs(p1.phi_Pn - p2.phi_Pn) > 1e-4:
                ratio = (inp.Pu - p1.phi_Pn) / (p2.phi_Pn - p1.phi_Pn)
                capacity_Mu = p1.phi_Mn + ratio * (p2.phi_Mn - p1.phi_Mn)
                break
    if capacity_Mu == 0.0:
        capacity_Mu = max(p.phi_Mn for p in pm_points)
        
    dcr = inp.Mu / capacity_Mu if capacity_Mu > 0 else (999.0 if inp.Pu > phi_Pn_max else 0.0)
    is_safe = (dcr <= 1.0) and (inp.Pu <= phi_Pn_max) and (0.01 <= rho_g <= 0.08)
    
    status = "OK" if is_safe else "NG"
    summary = f"[{status}] Column DCR: {dcr:.3f} (Pu={inp.Pu:.0f} kN, Mu={inp.Mu:.0f} kN*m, phi_Mn_cap={capacity_Mu:.1f} kN*m, rho={rho_g*100:.2f}%)"
    
    return RCColumnResult(
        Ag=Ag,
        Ast=Ast,
        rho_g=rho_g,
        Pn_max=Pn_max,
        phi_Pn_max=phi_Pn_max,
        pm_curve=pm_points,
        capacity_Mu=capacity_Mu,
        dcr=dcr,
        is_safe=is_safe,
        summary=summary
    )
