"""RC Slab Design & Punching Shear Engine (KDS 14 20 20 / KDS 14 20 22).

Provides:
- 1-Way Slab: Minimum thickness, flexural moment capacity, shrinkage/temperature steel
- 2-Way Slab: Direct Design Method (DDM) longitudinal & transverse strip moments
- Punching Shear: 2-way critical perimeter (b0), 3 KDS shear capacity formulas,
  eccentric shear stress distribution due to unbalanced moment (gamma_v * Munb)
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import List, Tuple, Dict, Any, Optional

from src.engine.materials import ConcreteMaterial, RebarMaterial, get_phi_flexure, get_phi_shear


class SlabSupportCondition(str, Enum):
    CANTILEVER = "cantilever"
    SIMPLY_SUPPORTED = "simply_supported"
    ONE_END_CONTINUOUS = "one_end_continuous"
    BOTH_ENDS_CONTINUOUS = "both_ends_continuous"


class ColumnLocation(str, Enum):
    INTERIOR = "interior"
    EDGE = "edge"
    CORNER = "corner"


# ============================================================================
# 1-Way Slab Data Classes & Engine
# ============================================================================

@dataclass
class OneWaySlabInput:
    """1-Way Slab Input parameters."""
    name: str = "S1"
    span_L: float = 4000.0         # mm (Clear span length)
    thickness_h: float = 180.0     # mm (Slab thickness)
    cover: float = 25.0            # mm (Clear cover)
    support_type: SlabSupportCondition = SlabSupportCondition.BOTH_ENDS_CONTINUOUS
    
    # Reinforcement (per 1m strip width)
    main_bar_diam: float = 13.0    # mm (Main rebar diameter)
    main_spacing: float = 150.0    # mm (Main rebar spacing)
    temp_bar_diam: float = 10.0    # mm (Shrinkage/temp rebar diameter)
    temp_spacing: float = 200.0    # mm (Shrinkage/temp rebar spacing)
    
    # Materials
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=24.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    
    # Factored Forces per 1m width
    Mu: float = 25.0               # kN*m/m (Factored bending moment)
    Vu: float = 35.0               # kN/m (Factored 1-way shear force)


@dataclass
class OneWaySlabResult:
    """1-Way Slab check result."""
    name: str
    h_provided: float              # mm
    h_min: float                   # mm (KDS minimum thickness for deflection)
    is_thickness_ok: bool
    
    # Flexure (1m strip)
    d: float                       # mm (Effective depth)
    As_main: float                 # mm2/m
    a: float                       # mm (Stress block depth)
    phi_Mn: float                  # kN*m/m
    dcr_flexure: float
    is_flexure_ok: bool
    
    # Shrinkage & Temperature
    As_temp_req: float             # mm2/m
    As_temp_prov: float            # mm2/m
    is_temp_ok: bool
    
    # 1-way Shear
    phi_Vc: float                  # kN/m
    dcr_shear: float
    is_shear_ok: bool
    
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class RCOneWaySlab:
    """1-Way RC Slab Engineering Solver (KDS 14 20 20)."""

    def __init__(self, slab_input: OneWaySlabInput):
        self.input = slab_input

    def calc_min_thickness(self) -> float:
        """Calculate KDS 14 20 20 minimum thickness for deflection control."""
        L = self.input.span_L
        fy = self.input.rebar.fy
        
        # Base L/N ratios
        if self.input.support_type == SlabSupportCondition.CANTILEVER:
            base_ratio = 10.0
        elif self.input.support_type == SlabSupportCondition.SIMPLY_SUPPORTED:
            base_ratio = 20.0
        elif self.input.support_type == SlabSupportCondition.ONE_END_CONTINUOUS:
            base_ratio = 24.0
        else: # BOTH_ENDS_CONTINUOUS
            base_ratio = 28.0
            
        # Modification for fy != 400 MPa
        fy_mod = (0.43 + fy / 700.0) if fy != 400.0 else 1.0
        h_min = (L / base_ratio) * fy_mod
        return h_min

    def design_check(self) -> OneWaySlabResult:
        """Perform comprehensive 1-way slab flexure, shear, and detailing check."""
        h = self.input.thickness_h
        h_min = self.calc_min_thickness()
        is_thick_ok = (h >= h_min)
        
        b = 1000.0 # mm (1m design strip)
        d = h - self.input.cover - self.input.main_bar_diam / 2.0
        
        # Main rebar area per 1m
        bar_area_main = math.pi * (self.input.main_bar_diam ** 2) / 4.0
        num_bars_main = b / self.input.main_spacing
        As_main = num_bars_main * bar_area_main
        
        # Flexural capacity
        fck = self.input.concrete.fck
        fy = self.input.rebar.fy
        a = (As_main * fy) / (0.85 * fck * b)
        phi_f = get_phi_flexure(0.005) # 0.85
        Mn_Nmm = As_main * fy * (d - a / 2.0)
        phi_Mn = (phi_f * Mn_Nmm) / 1e6 # kN*m/m
        
        dcr_flexure = self.input.Mu / phi_Mn if phi_Mn > 0 else 999.0
        is_flex_ok = dcr_flexure <= 1.0
        
        # Shrinkage / Temp Rebar (KDS 14 20 20)
        if fy <= 400.0:
            rho_temp = 0.0020
        else:
            rho_temp = max(0.0014, 0.0020 * 400.0 / fy)
        As_temp_req = rho_temp * b * h
        
        bar_area_temp = math.pi * (self.input.temp_bar_diam ** 2) / 4.0
        num_bars_temp = b / self.input.temp_spacing
        As_temp_prov = num_bars_temp * bar_area_temp
        is_temp_ok = (As_temp_prov >= As_temp_req)
        
        # 1-way Shear capacity Vc = (1/6) * lambda * sqrt(fck) * b * d
        lam = self.input.concrete.lambda_factor
        Vc_N = (1.0 / 6.0) * lam * math.sqrt(fck) * b * d
        phi_v = get_phi_shear() # 0.75
        phi_Vc = (phi_v * Vc_N) / 1e3 # kN/m
        dcr_shear = self.input.Vu / phi_Vc if phi_Vc > 0 else 999.0
        is_shear_ok = dcr_shear <= 1.0
        
        messages = []
        if not is_thick_ok:
            messages.append(f"Thickness h={h}mm < min {h_min:.1f}mm (Deflection check required).")
        if not is_flex_ok:
            messages.append(f"Flexural overstress: Mu={self.input.Mu} kN*m/m > phi*Mn={phi_Mn:.1f} kN*m/m")
        if not is_temp_ok:
            messages.append(f"Temp rebar {As_temp_prov:.1f}mm2/m < req {As_temp_req:.1f}mm2/m")
        if not is_shear_ok:
            messages.append(f"Shear overstress: Vu={self.input.Vu} kN/m > phi*Vc={phi_Vc:.1f} kN/m")
            
        is_safe = is_thick_ok and is_flex_ok and is_temp_ok and is_shear_ok
        
        return OneWaySlabResult(
            name=self.input.name,
            h_provided=h,
            h_min=round(h_min, 1),
            is_thickness_ok=is_thick_ok,
            d=round(d, 1),
            As_main=round(As_main, 1),
            a=round(a, 1),
            phi_Mn=round(phi_Mn, 2),
            dcr_flexure=round(dcr_flexure, 3),
            is_flexure_ok=is_flex_ok,
            As_temp_req=round(As_temp_req, 1),
            As_temp_prov=round(As_temp_prov, 1),
            is_temp_ok=is_temp_ok,
            phi_Vc=round(phi_Vc, 2),
            dcr_shear=round(dcr_shear, 3),
            is_shear_ok=is_shear_ok,
            is_safe=is_safe,
            messages=messages
        )


# ============================================================================
# 2-Way Slab Direct Design Method (DDM) Data Classes & Engine
# ============================================================================

@dataclass
class TwoWaySlabDDMInput:
    """2-Way Slab Direct Design Method (DDM) inputs."""
    name: str = "S2_DDM"
    l1: float = 6000.0             # mm (Span length in direction moments are determined)
    l2: float = 6000.0             # mm (Transverse span length)
    c1: float = 500.0              # mm (Column dimension parallel to l1)
    c2: float = 500.0              # mm (Column dimension parallel to l2)
    thickness_h: float = 200.0     # mm (Slab thickness)
    qu: float = 12.0               # kN/m2 (Factored uniform area load)
    is_interior_span: bool = True  # True = Interior span, False = Exterior end span
    has_edge_beam: bool = False    # True if edge beam present
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=27.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))


@dataclass
class DDMMomentDistribution:
    """DDM Total Static Moment & Strip Moment Distribution."""
    M0: float                      # kN*m (Total factored static moment)
    ln: float                      # mm (Clear span)
    
    # Longitudinal Span moments (kN*m)
    neg_interior_Mu: float         # Negative moment at interior support
    pos_Mu: float                  # Positive moment in span
    neg_exterior_Mu: float         # Negative moment at exterior support
    
    # Transverse Strip Moments (kN*m)
    # Column Strip (주열대)
    col_strip_neg_interior: float
    col_strip_pos: float
    col_strip_neg_exterior: float
    
    # Middle Strip (중간대)
    mid_strip_neg_interior: float
    mid_strip_pos: float
    mid_strip_neg_exterior: float


class RCTwoWaySlabDDM:
    """2-Way Slab Direct Design Method Solver (KDS 14 20 20)."""

    def __init__(self, slab_input: TwoWaySlabDDMInput):
        self.input = slab_input

    def calculate_ddm_moments(self) -> DDMMomentDistribution:
        """Calculate total static moment M0 and distribute across strips."""
        l1 = self.input.l1
        l2 = self.input.l2
        c1 = self.input.c1
        qu = self.input.qu # kN/m2
        
        # Clear span ln >= 0.65 * l1
        ln = max(0.65 * l1, l1 - c1)
        
        # M0 = (qu * l2 * ln^2) / 8 (in kN*m)
        # qu in kN/m2, l2 in m, ln in m
        l2_m = l2 / 1000.0
        ln_m = ln / 1000.0
        M0 = (qu * l2_m * (ln_m ** 2)) / 8.0
        
        if self.input.is_interior_span:
            neg_int = 0.65 * M0
            pos = 0.35 * M0
            neg_ext = 0.0
            
            # Transverse Strip distribution for flat plate (alpha_f1 = 0)
            # Column Strip: 75% for neg_int, 60% for pos
            col_neg_int = 0.75 * neg_int
            mid_neg_int = 0.25 * neg_int
            col_pos = 0.60 * pos
            mid_pos = 0.40 * pos
            col_neg_ext = 0.0
            mid_neg_ext = 0.0
        else:
            # Flat plate end span without beams
            neg_int = 0.70 * M0
            pos = 0.52 * M0
            neg_ext = 0.26 * M0
            
            col_neg_int = 0.75 * neg_int
            mid_neg_int = 0.25 * neg_int
            col_pos = 0.60 * pos
            mid_pos = 0.40 * pos
            col_neg_ext = 1.00 * neg_ext # 100% to column strip if beta_t ~ 0
            mid_neg_ext = 0.00
            
        return DDMMomentDistribution(
            M0=round(M0, 2),
            ln=round(ln, 1),
            neg_interior_Mu=round(neg_int, 2),
            pos_Mu=round(pos, 2),
            neg_exterior_Mu=round(neg_ext, 2),
            col_strip_neg_interior=round(col_neg_int, 2),
            col_strip_pos=round(col_pos, 2),
            col_strip_neg_exterior=round(col_neg_ext, 2),
            mid_strip_neg_interior=round(mid_neg_int, 2),
            mid_strip_pos=round(mid_pos, 2),
            mid_strip_neg_exterior=round(mid_neg_ext, 2)
        )


# ============================================================================
# Punching Shear Data Classes & Engine (KDS 14 20 22 4.4)
# ============================================================================

@dataclass
class PunchingShearInput:
    """Punching Shear check input at column-slab connection."""
    column_name: str = "C1"
    location: ColumnLocation = ColumnLocation.INTERIOR
    c1: float = 500.0              # mm (Column dimension in moment transfer direction)
    c2: float = 500.0              # mm (Column dimension transverse)
    slab_h: float = 250.0          # mm (Slab thickness)
    eff_depth_d: float = 200.0     # mm (Effective depth d)
    Vu: float = 450.0              # kN (Factored punching shear force)
    Munb: float = 60.0             # kN*m (Unbalanced factored moment transferred to column)
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=27.0))


@dataclass
class PunchingShearResult:
    """Punching Shear check results."""
    column_name: str
    location: ColumnLocation
    b0: float                      # mm (Critical perimeter)
    Ac: float                      # mm2 (Critical section area = b0 * d)
    beta_ratio: float              # Long/short column dimension ratio
    alpha_s: float                 # 40 (interior), 30 (edge), 20 (corner)
    
    # 3 KDS Concrete Capacity Formulas (MPa)
    vc1: float
    vc2: float
    vc3: float
    vc_nominal: float              # min(vc1, vc2, vc3) (MPa)
    phi_vc: float                  # phi * vc_nominal (MPa)
    
    # Unbalanced moment stress
    gamma_v: float                 # Fraction of moment transferred by shear
    gamma_f: float                 # 1 - gamma_v (transferred by flexure)
    vu_direct: float               # MPa (Vu / Ac)
    vu_moment: float               # MPa (gamma_v * Munb * c / Jc)
    vu_total: float                # MPa (vu_direct + vu_moment)
    
    dcr: float                     # vu_total / phi_vc
    is_safe: bool
    perimeter_points: List[Dict[str, float]] = field(default_factory=list)


class PunchingShearEngine:
    """Two-Way Punching Shear solver conforming to KDS 14 20 22 4.4."""

    def __init__(self, inp: PunchingShearInput):
        self.input = inp

    def calculate_critical_perimeter(self) -> Tuple[float, List[Dict[str, float]]]:
        """Calculate b0 (mm) and polygon coordinates of critical section at d/2."""
        c1 = self.input.c1
        c2 = self.input.c2
        d = self.input.eff_depth_d
        loc = self.input.location
        
        # d/2 offset dimensions
        b1 = c1 + d
        b2 = c2 + d
        
        if loc == ColumnLocation.INTERIOR:
            b0 = 2.0 * b1 + 2.0 * b2
            poly = [
                {"x": -b1 / 2, "y": -b2 / 2},
                {"x": b1 / 2, "y": -b2 / 2},
                {"x": b1 / 2, "y": b2 / 2},
                {"x": -b1 / 2, "y": b2 / 2},
            ]
        elif loc == ColumnLocation.EDGE:
            # Edge along c2 (column free at top of c1)
            b0 = 2.0 * (c1 + d / 2.0) + b2
            poly = [
                {"x": 0.0, "y": -b2 / 2},
                {"x": c1 + d / 2.0, "y": -b2 / 2},
                {"x": c1 + d / 2.0, "y": b2 / 2},
                {"x": 0.0, "y": b2 / 2},
            ]
        else: # CORNER
            b0 = (c1 + d / 2.0) + (c2 + d / 2.0)
            poly = [
                {"x": 0.0, "y": 0.0},
                {"x": c1 + d / 2.0, "y": 0.0},
                {"x": c1 + d / 2.0, "y": c2 + d / 2.0},
                {"x": 0.0, "y": c2 + d / 2.0},
            ]
            
        return b0, poly

    def check_punching_shear(self) -> PunchingShearResult:
        """Perform 3-formula KDS punching shear capacity and eccentric shear check."""
        c1 = self.input.c1
        c2 = self.input.c2
        d = self.input.eff_depth_d
        fck = self.input.concrete.fck
        lam = self.input.concrete.lambda_factor
        Vu_N = self.input.Vu * 1e3
        Munb_Nmm = abs(self.input.Munb) * 1e6
        
        b0, poly = self.calculate_critical_perimeter()
        Ac = b0 * d # mm2
        
        # Aspect ratio beta
        beta = max(c1, c2) / min(c1, c2)
        
        # alpha_s factor
        if self.input.location == ColumnLocation.INTERIOR:
            alpha_s = 40.0
        elif self.input.location == ColumnLocation.EDGE:
            alpha_s = 30.0
        else:
            alpha_s = 20.0
            
        sqrt_fck = math.sqrt(fck)
        
        # 3 KDS Formulas (MPa)
        vc1 = (1.0 + 2.0 / beta) * (1.0 / 6.0) * lam * sqrt_fck
        vc2 = ((alpha_s * d / b0) + 2.0) * (1.0 / 12.0) * lam * sqrt_fck
        vc3 = (1.0 / 3.0) * lam * sqrt_fck
        
        vc_nom = min(vc1, vc2, vc3)
        phi_v = get_phi_shear() # 0.75
        phi_vc = phi_v * vc_nom
        
        # Direct shear stress
        vu_direct = Vu_N / Ac
        
        # Unbalanced moment shear transfer
        b1 = c1 + d
        b2 = c2 + d
        gamma_v = 1.0 - (1.0 / (1.0 + (2.0 / 3.0) * math.sqrt(b1 / b2)))
        gamma_f = 1.0 - gamma_v
        
        # Polar moment of inertia Jc / c
        if self.input.location == ColumnLocation.INTERIOR:
            # Jc/c for interior rectangular section
            # Jc = d*(b1^3)/6 + (b1*d^3)/6 + d*b2*(b1^2)/2
            Jc = (d * (b1 ** 3)) / 6.0 + (b1 * (d ** 3)) / 6.0 + (d * b2 * (b1 ** 2)) / 2.0
            c_AB = b1 / 2.0
            vu_moment = (gamma_v * Munb_Nmm * c_AB) / Jc
        else:
            # Edge/corner simplified polar modulus
            Jc_over_c = (Ac * b1) / 3.0
            vu_moment = (gamma_v * Munb_Nmm) / Jc_over_c
            
        vu_total = vu_direct + vu_moment
        dcr = vu_total / phi_vc if phi_vc > 0 else 999.0
        is_safe = (dcr <= 1.0)
        
        return PunchingShearResult(
            column_name=self.input.column_name,
            location=self.input.location,
            b0=round(b0, 1),
            Ac=round(Ac, 1),
            beta_ratio=round(beta, 2),
            alpha_s=alpha_s,
            vc1=round(vc1, 3),
            vc2=round(vc2, 3),
            vc3=round(vc3, 3),
            vc_nominal=round(vc_nom, 3),
            phi_vc=round(phi_vc, 3),
            gamma_v=round(gamma_v, 3),
            gamma_f=round(gamma_f, 3),
            vu_direct=round(vu_direct, 3),
            vu_moment=round(vu_moment, 3),
            vu_total=round(vu_total, 3),
            dcr=round(dcr, 3),
            is_safe=is_safe,
            perimeter_points=poly
        )
