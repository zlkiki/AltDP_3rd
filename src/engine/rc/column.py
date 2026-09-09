"""RC Column Design Engine (KDS 14 20 20 / KDS 14 20 22 / KDS 14 20 50) for AltDP_3rd.

Integrates slenderness effects (moment magnification method), biaxial bending,
shear capacity with axial compression, tie spacing detailing, and 200-fiber P-M solvers.
Conforms to Requirement 23 and AltDP-Core CalculationTracer AST & Geometry specifications.
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Dict, Any, Optional

from src.core.tracer import CalculationTracer
from src.core.geometry import (
    Point2D, PolygonGeometry, RebarPoint, StirrupLoop,
    DimensionLine, PMCurveData, SectionGeometry
)
from src.engine.materials import ConcreteMaterial, RebarMaterial, get_phi_flexure, get_phi_shear
from src.engine.solver.fiber_section import FiberSection
from src.engine.solver.pm_diagram import PMDiagramSolver, PMDiagramResult, PMCurvePoint


@dataclass
class RCColumnInput:
    """RC Column Geometry, Rebar Configuration, Framing, and Design Forces."""
    name: str = "C1"
    b: float = 600.0           # mm (Section width / dimension in X)
    h: float = 600.0           # mm (Section depth / dimension in Y)
    cover: float = 60.0        # mm (Clear cover to rebar centroid)
    
    # Rebar details
    bar_diam: float = 25.0     # mm (Longitudinal bar diameter)
    total_bars: int = 12       # Total number of longitudinal bars (e.g. 12-D25)
    tie_diam: float = 10.0     # mm (Tie / stirrup diameter)
    tie_spacing: float = 300.0 # mm (Tie spacing along column height)
    tie_legs_x: int = 2        # Number of shear legs resisting Vy
    tie_legs_y: int = 2        # Number of shear legs resisting Vx
    is_spiral: bool = False    # True if spiral column, False if tied
    
    # Slenderness & Framing Parameters (KDS 14 20 20)
    Lu: float = 3600.0         # mm (Unsupported length of column)
    k: float = 1.0             # Effective length factor (1.0 for braced frame, >1.0 for unbraced)
    is_braced: bool = True     # True for non-sway (braced) frame
    M1x: float = 0.0           # kN*m (Smaller factored end moment about X)
    M2x: float = 350.0         # kN*m (Larger factored end moment about X, positive)
    M1y: float = 0.0           # kN*m (Smaller factored end moment about Y)
    M2y: float = 0.0           # kN*m (Larger factored end moment about Y)
    beta_dns: float = 0.2      # Ratio of maximum factored sustained load to total factored load
    
    # Factored Design Forces at critical section
    Pu: float = 2500.0         # kN (Factored axial load, positive = compression)
    Mux: float = 350.0         # kN*m (Factored bending moment about X-axis)
    Muy: float = 0.0           # kN*m (Factored bending moment about Y-axis)
    Vux: float = 0.0           # kN (Factored shear force along X)
    Vuy: float = 120.0         # kN (Factored shear force along Y)
    
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
class SlendernessResult:
    """KDS 14 20 20 Slenderness & Moment Magnification Output."""
    is_slender_x: bool
    is_slender_y: bool
    slenderness_x: float       # k * Lu / r_x
    slenderness_y: float       # k * Lu / r_y
    slenderness_limit_x: float
    slenderness_limit_y: float
    delta_ns_x: float          # Non-sway moment magnification factor about X
    delta_ns_y: float          # Non-sway moment magnification factor about Y
    Pc_x: float                # kN (Euler buckling load about X)
    Pc_y: float                # kN (Euler buckling load about Y)
    Mc_x: float                # kN*m (Magnified factored design moment about X)
    Mc_y: float                # kN*m (Magnified factored design moment about Y)
    min_eccentricity_x: float  # mm (15 + 0.03 * h)
    min_eccentricity_y: float  # mm (15 + 0.03 * b)


@dataclass
class RCColumnDesignResult:
    """Comprehensive RC Column Design Output with Tracer AST and Parametric Geometry."""
    name: str
    Ag: float                  # mm2
    Ast: float                 # mm2
    rho_g: float               # Ast / Ag
    is_rho_ok: bool            # True if 0.01 <= rho_g <= 0.08
    
    # Axial & P-M Capacities
    Po: float                  # kN
    Pn_max: float              # kN
    phi_Pn_max: float          # kN
    phi_Pt: float              # kN
    
    # Slenderness & Magnified Moments
    slenderness: SlendernessResult
    
    # Demand & Capacity Evaluation
    design_Pu: float           # kN
    design_Mux: float          # kN*m (including slenderness & min eccentricity)
    design_Muy: float          # kN*m
    capacity_Mu: float         # kN*m
    pm_dcr: float              # Demand-Capacity Ratio for P-M-M interaction
    is_pm_safe: bool
    
    # Shear Capacity (KDS 14 20 22 with Axial Compression)
    Vux: float                 # kN
    phi_Vnx: float             # kN
    shear_dcr_x: float
    Vuy: float                 # kN
    phi_Vny: float             # kN
    shear_dcr_y: float
    is_shear_safe: bool
    
    # Rebar Details & Tie Check (KDS 14 20 50)
    tie_spacing: float         # mm
    tie_spacing_max: float     # mm
    is_tie_ok: bool
    
    # Summary
    dcr_max: float
    is_safe: bool
    summary: str
    
    # P-M Diagram curve points for UI plotting
    pm_curve_x: List[Dict[str, float]]
    pm_curve_y: List[Dict[str, float]]
    
    # AltDP-Core Platform Extensions
    tracer: Optional[Dict[str, Any]] = None
    geometry: Optional[Dict[str, Any]] = None
    bresler_dcr: float = 0.0


def evaluate_slenderness(inp: RCColumnInput) -> SlendernessResult:
    """Calculate slenderness ratio, Euler buckling load, and magnified moments (KDS 14 20 20)."""
    # Radius of gyration r for rectangular column: r = 0.3 * dimension
    rx = 0.30 * inp.h
    ry = 0.30 * inp.b
    
    slenderness_x = (inp.k * inp.Lu) / rx
    slenderness_y = (inp.k * inp.Lu) / ry
    
    # Slenderness limit for braced frame: 34 - 12 * (M1 / M2) <= 40
    ratio_x = (inp.M1x / inp.M2x) if abs(inp.M2x) > 1e-4 else 0.0
    ratio_y = (inp.M1y / inp.M2y) if abs(inp.M2y) > 1e-4 else 0.0
    
    if inp.is_braced:
        limit_x = min(40.0, max(22.0, 34.0 - 12.0 * ratio_x))
        limit_y = min(40.0, max(22.0, 34.0 - 12.0 * ratio_y))
    else:
        limit_x = 22.0
        limit_y = 22.0
        
    is_slender_x = slenderness_x > limit_x
    is_slender_y = slenderness_y > limit_y
    
    # Minimum design eccentricity: emin = 15 + 0.03 * h (mm)
    emin_x = 15.0 + 0.03 * inp.h
    emin_y = 15.0 + 0.03 * inp.b
    M2_min_x = (inp.Pu * emin_x) / 1e3  # kN*m
    M2_min_y = (inp.Pu * emin_y) / 1e3  # kN*m
    
    M2_effective_x = max(abs(inp.M2x), abs(inp.Mux), M2_min_x)
    M2_effective_y = max(abs(inp.M2y), abs(inp.Muy), M2_min_y)
    
    # Effective flexural stiffness (EI)eff = 0.4 * Ec * Ig / (1 + beta_dns)
    # Ig about X = b * h^3 / 12, Ig about Y = h * b^3 / 12
    Ec = inp.concrete.Ec
    Ig_x = (inp.b * (inp.h ** 3)) / 12.0
    Ig_y = (inp.h * (inp.b ** 3)) / 12.0
    
    rebars = get_column_rebar_coordinates(inp)
    Ise_x = sum(r[2] * (r[1] ** 2) for r in rebars) if rebars else 0.0
    Ise_y = sum(r[2] * (r[0] ** 2) for r in rebars) if rebars else 0.0
    Es = inp.rebar.Es
    
    beta_dns = max(0.0, inp.beta_dns)
    EI_eff_x = ((0.2 * Ec * Ig_x + Es * Ise_x) if Ise_x > 0 else (0.4 * Ec * Ig_x)) / (1.0 + beta_dns)
    EI_eff_y = ((0.2 * Ec * Ig_y + Es * Ise_y) if Ise_y > 0 else (0.4 * Ec * Ig_y)) / (1.0 + beta_dns)
    
    # Euler buckling capacity Pc = pi^2 * EI / (k * Lu)^2 (N -> kN)
    Pc_x_N = (math.pi ** 2) * EI_eff_x / ((inp.k * inp.Lu) ** 2)
    Pc_y_N = (math.pi ** 2) * EI_eff_y / ((inp.k * inp.Lu) ** 2)
    Pc_x = Pc_x_N / 1e3
    Pc_y = Pc_y_N / 1e3
    
    # Cm equivalent moment factor
    Cm_x = max(0.4, 0.6 + 0.4 * ratio_x) if abs(inp.M2x) > 1e-4 else 1.0
    Cm_y = max(0.4, 0.6 + 0.4 * ratio_y) if abs(inp.M2y) > 1e-4 else 1.0
    
    # delta_ns = Cm / (1 - Pu / (0.75 * Pc)) >= 1.0
    if is_slender_x and Pc_x > 0 and inp.Pu < 0.75 * Pc_x:
        delta_ns_x = max(1.0, Cm_x / (1.0 - inp.Pu / (0.75 * Pc_x)))
    else:
        delta_ns_x = 1.0
        
    if is_slender_y and Pc_y > 0 and inp.Pu < 0.75 * Pc_y:
        delta_ns_y = max(1.0, Cm_y / (1.0 - inp.Pu / (0.75 * Pc_y)))
    else:
        delta_ns_y = 1.0
        
    Mc_x = delta_ns_x * M2_effective_x
    Mc_y = delta_ns_y * M2_effective_y
    
    return SlendernessResult(
        is_slender_x=is_slender_x,
        is_slender_y=is_slender_y,
        slenderness_x=round(slenderness_x, 2),
        slenderness_y=round(slenderness_y, 2),
        slenderness_limit_x=round(limit_x, 2),
        slenderness_limit_y=round(limit_y, 2),
        delta_ns_x=round(delta_ns_x, 3),
        delta_ns_y=round(delta_ns_y, 3),
        Pc_x=round(Pc_x, 1),
        Pc_y=round(Pc_y, 1),
        Mc_x=round(Mc_x, 2),
        Mc_y=round(Mc_y, 2),
        min_eccentricity_x=round(emin_x, 1),
        min_eccentricity_y=round(emin_y, 1)
    )


def get_column_rebar_coordinates(inp: RCColumnInput) -> List[Tuple[float, float, float]]:
    """Generate symmetric perimeter coordinates (x, y, area) for longitudinal bars."""
    b, h = inp.b, inp.h
    cover = inp.cover
    single_bar_area = math.pi * (inp.bar_diam ** 2) / 4.0
    
    x_left = -b / 2.0 + cover
    x_right = b / 2.0 - cover
    y_bot = -h / 2.0 + cover
    y_top = h / 2.0 - cover
    
    total = max(4, inp.total_bars)
    
    # 4 corner bars minimum
    if total == 4:
        return [
            (x_left, y_top, single_bar_area),
            (x_right, y_top, single_bar_area),
            (x_right, y_bot, single_bar_area),
            (x_left, y_bot, single_bar_area)
        ]
        
    rem = total - 4
    if rem % 4 == 0:
        n_per_side = rem // 4
        n_top = n_bot = n_left = n_right = n_per_side
    else:
        # Distribute based on aspect ratio
        ratio_x = (b - 2 * cover) / max(1.0, (b + h - 4 * cover))
        n_x_total = int(round(rem * ratio_x))
        if n_x_total % 2 != 0:
            n_x_total += 1 if n_x_total < rem else -1
        n_y_total = rem - n_x_total
        n_top = n_bot = n_x_total // 2
        n_left = n_right = n_y_total // 2
        while (n_top + n_bot + n_left + n_right) < rem:
            n_top += 1
            if (n_top + n_bot + n_left + n_right) < rem:
                n_bot += 1

    rebars: List[Tuple[float, float, float]] = []
    
    # Top edge (corners + intermediates)
    dx_top = (x_right - x_left) / (n_top + 1)
    for i in range(n_top + 2):
        rebars.append((x_left + i * dx_top, y_top, single_bar_area))
        
    # Right edge (intermediates only)
    dy_right = (y_bot - y_top) / (n_right + 1)
    for j in range(1, n_right + 1):
        rebars.append((x_right, y_top + j * dy_right, single_bar_area))
        
    # Bottom edge (corners + intermediates)
    dx_bot = (x_left - x_right) / (n_bot + 1)
    for i in range(n_bot + 2):
        rebars.append((x_right + i * dx_bot, y_bot, single_bar_area))
        
    # Left edge (intermediates only)
    dy_left = (y_top - y_bot) / (n_left + 1)
    for j in range(1, n_left + 1):
        rebars.append((x_left, y_bot + j * dy_left, single_bar_area))
        
    # Deduplicate points within 1mm
    unique_rebars: List[Tuple[float, float, float]] = []
    for r in rebars:
        if not any(abs(r[0] - u[0]) < 1.0 and abs(r[1] - u[1]) < 1.0 for u in unique_rebars):
            unique_rebars.append(r)
            
    return unique_rebars[:total]


def create_standard_column_fiber_section(inp: RCColumnInput, nx: int = 20, ny: int = 20) -> FiberSection:
    """Generate FiberSection with perimeter distributed longitudinal rebar."""
    rebars = get_column_rebar_coordinates(inp)
    return FiberSection.from_rect(
        b=inp.b, h=inp.h, rebars=rebars, nx=nx, ny=ny,
        concrete=inp.concrete, rebar_mat=inp.rebar
    )


def calculate_column_shear(
    inp: RCColumnInput,
    b_w: float,
    d: float,
    Vu: float,
    tie_legs: int
) -> Tuple[float, float, float, float]:
    """Calculate RC column shear capacity with axial compression (KDS 14 20 22).
    
    Vc = (1/6) * (1 + Nu / (14 * Ag)) * lambda * sqrt(fck) * bw * d
    Vs = Av * fyt * d / s
    phi_Vn = phi_v * (Vc + Vs)
    """
    Ag = inp.Ag
    fck = inp.concrete.fck
    lambda_fac = inp.concrete.lambda_factor
    Nu_N = max(0.0, inp.Pu * 1e3)  # Compressive axial force in N
    
    # Concrete shear capacity with axial compression
    axial_factor = 1.0 + (Nu_N / (14.0 * Ag))
    Vc_N = (1.0 / 6.0) * axial_factor * lambda_fac * math.sqrt(fck) * b_w * d
    Vc = Vc_N / 1e3  # kN
    
    # Steel shear capacity
    tie_area = math.pi * (inp.tie_diam ** 2) / 4.0
    Av = tie_legs * tie_area
    fyt = inp.rebar.fy
    s = inp.tie_spacing
    
    Vs_N = (Av * fyt * d) / s if s > 0 else 0.0
    Vs_max_N = (2.0 / 3.0) * math.sqrt(fck) * b_w * d
    Vs = min(Vs_N, Vs_max_N) / 1e3  # kN
    
    phi_v = get_phi_shear()
    phi_Vn = phi_v * (Vc + Vs)
    dcr_v = Vu / phi_Vn if phi_Vn > 0 else 0.0
    
    return Vc, Vs, phi_Vn, dcr_v


def create_column_section_geometry(
    inp: RCColumnInput,
    pm_diag_x: Optional[PMDiagramResult] = None,
    pm_diag_y: Optional[PMDiagramResult] = None,
    dcr_x: float = 0.0,
    dcr_y: float = 0.0,
    capacity_Mux: float = 0.0,
    capacity_Muy: float = 0.0
) -> SectionGeometry:
    """Package CAD 2D parametric geometry and 200-fiber P-M curves."""
    b, h = inp.b, inp.h
    cover = inp.cover
    rebar_coords = get_column_rebar_coordinates(inp)
    
    # Boundary polygon
    boundary = [
        Point2D(-b / 2.0, -h / 2.0),
        Point2D(b / 2.0, -h / 2.0),
        Point2D(b / 2.0, h / 2.0),
        Point2D(-b / 2.0, h / 2.0)
    ]
    
    # Rebars
    rebars = [
        RebarPoint(x=x, y=y, dia=inp.bar_diam, layer=1, tag=f"{int(inp.bar_diam)}")
        for x, y, _ in rebar_coords
    ]
    
    # Stirrups
    stirrup_cover = max(20.0, cover - inp.bar_diam / 2.0 - inp.tie_diam / 2.0)
    sx_min = -b / 2.0 + stirrup_cover
    sx_max = b / 2.0 - stirrup_cover
    sy_min = -h / 2.0 + stirrup_cover
    sy_max = h / 2.0 - stirrup_cover
    
    stirrup_path = [
        Point2D(sx_min, sy_min),
        Point2D(sx_max, sy_min),
        Point2D(sx_max, sy_max),
        Point2D(sx_min, sy_max),
        Point2D(sx_min, sy_min)
    ]
    stirrups = [
        StirrupLoop(
            path=stirrup_path,
            dia=inp.tie_diam,
            is_closed=True,
            hook_angle=135.0,
            legs_x=inp.tie_legs_x,
            legs_y=inp.tie_legs_y
        )
    ]
    
    # Dimensions
    dimensions = [
        DimensionLine(
            p1=Point2D(-b / 2.0, h / 2.0),
            p2=Point2D(b / 2.0, h / 2.0),
            text=f"b = {int(b)} mm",
            dim_type="horizontal",
            offset=35.0
        ),
        DimensionLine(
            p1=Point2D(b / 2.0, -h / 2.0),
            p2=Point2D(b / 2.0, h / 2.0),
            text=f"h = {int(h)} mm",
            dim_type="vertical",
            offset=35.0
        )
    ]
    
    pm_curve_x = None
    if pm_diag_x:
        pm_curve_x = PMCurveData(
            theta_deg=0.0,
            nominal_curve=[{"Pn": round(p.Pn, 1), "Mn": round(p.Mn, 1)} for p in pm_diag_x.points],
            design_curve=[{"phi_Pn": round(p.phi_Pn, 1), "phi_Mn": round(p.phi_Mn, 1), "phi": round(p.phi, 3)} for p in pm_diag_x.points],
            demand_point={"Pu": round(inp.Pu, 1), "Mu": round(inp.Mux, 1), "dcr": round(dcr_x, 3)},
            capacity_point={"phi_Pn": round(inp.Pu, 1), "phi_Mn": round(capacity_Mux, 1)},
            Po=pm_diag_x.Po,
            Pt=pm_diag_x.Pt,
            Pn_max=pm_diag_x.Pn_max,
            phi_Pn_max=pm_diag_x.phi_Pn_max,
            phi_Pt=pm_diag_x.phi_Pt
        )
        
    pm_curve_y = None
    if pm_diag_y:
        pm_curve_y = PMCurveData(
            theta_deg=90.0,
            nominal_curve=[{"Pn": round(p.Pn, 1), "Mn": round(p.Mn, 1)} for p in pm_diag_y.points],
            design_curve=[{"phi_Pn": round(p.phi_Pn, 1), "phi_Mn": round(p.phi_Mn, 1), "phi": round(p.phi, 3)} for p in pm_diag_y.points],
            demand_point={"Pu": round(inp.Pu, 1), "Mu": round(inp.Muy, 1), "dcr": round(dcr_y, 3)},
            capacity_point={"phi_Pn": round(inp.Pu, 1), "phi_Mn": round(capacity_Muy, 1)},
            Po=pm_diag_y.Po,
            Pt=pm_diag_y.Pt,
            Pn_max=pm_diag_y.Pn_max,
            phi_Pn_max=pm_diag_y.phi_Pn_max,
            phi_Pt=pm_diag_y.phi_Pt
        )
        
    return SectionGeometry(
        boundary=boundary,
        rebars=rebars,
        stirrups=stirrups,
        dimensions=dimensions,
        pm_curve_x=pm_curve_x,
        pm_curve_y=pm_curve_y
    )


def calculate_bresler_capacity(
    Po: float,
    diag_x: PMDiagramResult,
    diag_y: PMDiagramResult,
    Pu: float,
    Mux: float,
    Muy: float
) -> Tuple[float, float]:
    """Evaluate Bresler reciprocal nominal capacity Pn and DCR (KDS 14 20 20).
    
    1/Pn = 1/Pnx + 1/Pny - 1/P0
    phi = 0.65 for compression-controlled column
    """
    if Pu <= 0:
        return 0.0, 0.0
        
    ey = abs(Mux) / Pu if Pu > 0 else 0.0  # mm
    ex = abs(Muy) / Pu if Pu > 0 else 0.0  # mm
    
    # 1. Find Pnx from diag_x corresponding to ey
    Pnx = Po
    if ey > 1e-4:
        for i in range(len(diag_x.points) - 1):
            p1 = diag_x.points[i]
            p2 = diag_x.points[i + 1]
            e1 = (p1.Mn / p1.Pn * 1e3) if p1.Pn > 1e-2 else 1e9
            e2 = (p2.Mn / p2.Pn * 1e3) if p2.Pn > 1e-2 else 1e9
            if (e1 <= ey <= e2) or (e2 <= ey <= e1):
                denom = e2 - e1
                t = (ey - e1) / denom if abs(denom) > 1e-4 else 0.0
                Pnx = p1.Pn + t * (p2.Pn - p1.Pn)
                break
                
    # 2. Find Pny from diag_y corresponding to ex
    Pny = Po
    if ex > 1e-4:
        for i in range(len(diag_y.points) - 1):
            p1 = diag_y.points[i]
            p2 = diag_y.points[i + 1]
            e1 = (p1.Mn / p1.Pn * 1e3) if p1.Pn > 1e-2 else 1e9
            e2 = (p2.Mn / p2.Pn * 1e3) if p2.Pn > 1e-2 else 1e9
            if (e1 <= ex <= e2) or (e2 <= ex <= e1):
                denom = e2 - e1
                t = (ex - e1) / denom if abs(denom) > 1e-4 else 0.0
                Pny = p1.Pn + t * (p2.Pn - p1.Pn)
                break
                
    # Uniaxial simplification
    if ex <= 1e-4:
        P_bresler = Pnx
    elif ey <= 1e-4:
        P_bresler = Pny
    else:
        inv_P = (1.0 / Pnx) + (1.0 / Pny) - (1.0 / Po) if (Pnx > 0 and Pny > 0 and Po > 0) else 0.0
        P_bresler = 1.0 / inv_P if inv_P > 0 else 0.0
        
    phi = 0.65
    phi_Pn_bresler = phi * P_bresler
    dcr_bresler = Pu / phi_Pn_bresler if phi_Pn_bresler > 0 else 0.0
    return P_bresler, round(dcr_bresler, 3)


def design_rc_column(
    inp: RCColumnInput,
    tracer: Optional[CalculationTracer] = None
) -> RCColumnDesignResult:
    """Comprehensive design and verification of RC column according to KDS 14 20 00.
    
    Injects calculation steps into CalculationTracer AST and packages SectionGeometry.
    """
    if tracer is None:
        tracer = CalculationTracer(
            title=f"RC 기둥 '{inp.name}' 구조계산서",
            standard="KDS 14 20 20 / KDS 14 20 22",
            member_name=inp.name
        )
        
    Ag = inp.Ag
    Ast = inp.Ast
    rho_g = Ast / Ag
    is_rho_ok = 0.01 <= rho_g <= 0.08
    
    # -------------------------------------------------------------
    # Chapter 1: Section & Longitudinal Rebar Ratio
    # -------------------------------------------------------------
    tracer.step(
        chapter="제 1장. 단면 제원 및 철근비 검토",
        section="1.1 기둥 전단면적(Ag) 및 총 주철근 단면적(Ast)",
        standard_ref="KDS 14 20 20 (4.1.2)",
        formula=r"A_g = b \cdot h, \quad A_{st} = n \cdot \frac{\pi d_b^2}{4}",
        substitutions={"b": f"{inp.b:.0f} mm", "h": f"{inp.h:.0f} mm", "n": inp.total_bars, "d_b": f"{inp.bar_diam:.1f} mm"},
        result=f"Ag = {Ag:,.0f} mm², Ast = {Ast:,.1f} mm²",
        unit="mm²",
        description="콘크리트 기둥 전체 단면적 및 배치 주철근 총량 산정"
    )
    
    tracer.step(
        chapter="제 1장. 단면 제원 및 철근비 검토",
        section="1.2 축방향 주철근비(rho_g) 산정",
        standard_ref="KDS 14 20 20 (4.1.2(1))",
        formula=r"\rho_g = \frac{A_{st}}{A_g}",
        substitutions={"A_{st}": f"{Ast:.1f} mm^2", "A_g": f"{Ag:.0f} mm^2"},
        result=f"{rho_g * 100:.2f}",
        unit="%",
        description="기둥 단면의 축방향 주철근비"
    )
    
    dcr_rho = round(max(0.01 / rho_g if rho_g > 0 else 999.0, rho_g / 0.08), 3)
    tracer.evaluation(
        chapter="제 1장. 단면 제원 및 철근비 검토",
        title="주철근비 규준 적합성 (0.01 <= rho_g <= 0.08)",
        equation=r"0.01 \le \rho_g \le 0.08",
        left_val=f"{rho_g * 100:.2f}%",
        right_val="1.00% ~ 8.00%",
        unit="%",
        dcr=dcr_rho,
        status="OK" if is_rho_ok else "NG",
        standard_ref="KDS 14 20 20 (4.1.2(1))"
    )
    
    # -------------------------------------------------------------
    # Chapter 2: Pure Compression & Maximum Factored Axial Capacity
    # -------------------------------------------------------------
    # Po = 0.85 * fck * (Ag - Ast) + fy * Ast
    Po_N = 0.85 * inp.concrete.fck * (Ag - Ast) + inp.rebar.fy * Ast
    Po = Po_N / 1e3  # kN
    
    alpha_pn = 0.85 if inp.is_spiral else 0.80
    phi_axial = 0.70 if inp.is_spiral else 0.65
    Pn_max = alpha_pn * Po
    phi_Pn_max = phi_axial * Pn_max
    
    tracer.step(
        chapter="제 2장. 축하중 지지력 및 설계축강도 상한",
        section="2.1 순수 압축강도(P0) 산정",
        standard_ref="KDS 14 20 20 (4.1-1)",
        formula=r"P_0 = 0.85 f_{ck} (A_g - A_{st}) + f_y A_{st}",
        substitutions={"f_{ck}": f"{inp.concrete.fck:.1f} MPa", "A_g": f"{Ag:.0f} mm^2", "A_{st}": f"{Ast:.1f} mm^2", "f_y": f"{inp.rebar.fy:.0f} MPa"},
        result=f"{Po:,.1f}",
        unit="kN",
        description="단면의 공칭 순수 축압축 내력"
    )
    
    tracer.step(
        chapter="제 2장. 축하중 지지력 및 설계축강도 상한",
        section="2.2 최대 설계축강도(phi Pn,max) 산정",
        standard_ref="KDS 14 20 20 (4.1.2(2))",
        formula=r"\phi P_{n,max} = \alpha \cdot \phi \cdot P_0",
        substitutions={"\\alpha": alpha_pn, "\\phi": phi_axial, "P_0": f"{Po:.1f} kN"},
        result=f"{phi_Pn_max:,.1f}",
        unit="kN",
        description="우발적 편심을 고려한 최대 설계축강도 상한치"
    )
    
    dcr_axial_cap = round(inp.Pu / phi_Pn_max if phi_Pn_max > 0 else 999.0, 3)
    tracer.evaluation(
        chapter="제 2장. 축하중 지지력 및 설계축강도 상한",
        title="최대 설계축강도 상한 만족 검토 (Pu <= phi Pn,max)",
        equation=r"P_u \le \phi P_{n,max}",
        left_val=f"{inp.Pu:,.1f}",
        right_val=f"{phi_Pn_max:,.1f}",
        unit="kN",
        dcr=dcr_axial_cap,
        status="OK" if dcr_axial_cap <= 1.0 else "NG",
        standard_ref="KDS 14 20 20 (4.1.2(2))"
    )

    # -------------------------------------------------------------
    # Chapter 3: Slenderness & Moment Magnification
    # -------------------------------------------------------------
    slender_res = evaluate_slenderness(inp)
    
    tracer.step(
        chapter="제 3장. 장주 효과 및 모멘트 확대 검토",
        section="3.1 세장비(kLu/r) 산정 및 한계 세장비 판정",
        standard_ref="KDS 14 20 20 (4.3.1)",
        formula=r"\frac{k L_u}{r} \le 34 - 12 \left(\frac{M_1}{M_2}\right) \le 40",
        substitutions={"k": inp.k, "L_u": f"{inp.Lu:.0f} mm", "r_x": f"{0.30 * inp.h:.1f} mm"},
        result=f"k L_u / r = {slender_res.slenderness_x:.1f} (한계: {slender_res.slenderness_limit_x:.1f})",
        unit="-",
        description="횡구속(Non-sway) 골조의 기둥 세장비 판정"
    )
    
    tracer.step(
        chapter="제 3장. 장주 효과 및 모멘트 확대 검토",
        section="3.2 오일러 좌굴하중(Pc) 및 모멘트 확대계수(delta_ns)",
        standard_ref="KDS 14 20 20 (4.3.2)",
        formula=r"P_c = \frac{\pi^2 (EI)_{eff}}{(k L_u)^2}, \quad \delta_{ns} = \frac{C_m}{1 - P_u / (0.75 P_c)} \ge 1.0",
        substitutions={"P_u": f"{inp.Pu:,.1f} kN", "P_c": f"{slender_res.Pc_x:,.1f} kN"},
        result=f"delta_ns = {slender_res.delta_ns_x:.3f}, Pc = {slender_res.Pc_x:,.1f}",
        unit="kN",
        description="비횡구속 모멘트 확대계수 및 좌굴 임계하중"
    )
    
    tracer.step(
        chapter="제 3장. 장주 효과 및 모멘트 확대 검토",
        section="3.3 확대 계수설계모멘트(Mc) 산정 (최소 편심 emin 고려)",
        standard_ref="KDS 14 20 20 (4.3.3)",
        formula=r"M_c = \delta_{ns} \cdot \max(M_2, P_u \cdot e_{min}), \quad e_{min} = 15 + 0.03 h",
        substitutions={"\\delta_{ns}": slender_res.delta_ns_x, "e_{min}": f"{slender_res.min_eccentricity_x:.1f} mm"},
        result=f"{slender_res.Mc_x:,.2f}",
        unit="kN·m",
        description="최소 편심 모멘트 및 장주 모멘트 확대 반영 최종 설계휨모멘트"
    )
    
    tracer.evaluation(
        chapter="제 3장. 장주 효과 및 모멘트 확대 검토",
        title="장주 효과 안정성 판정 (Pu < 0.75 Pc)",
        equation=r"P_u \le 0.75 P_c",
        left_val=f"{inp.Pu:,.1f}",
        right_val=f"{0.75 * slender_res.Pc_x:,.1f}",
        unit="kN",
        dcr=round(inp.Pu / (0.75 * slender_res.Pc_x) if slender_res.Pc_x > 0 else 1.0, 3),
        status="OK" if inp.Pu < 0.75 * slender_res.Pc_x else "NG",
        standard_ref="KDS 14 20 20 (4.3.2)"
    )

    # -------------------------------------------------------------
    # Chapter 4: 200-Fiber P-M Diagram & Biaxial Bending
    # -------------------------------------------------------------
    sec = create_standard_column_fiber_section(inp, nx=20, ny=20)
    
    diag_x = PMDiagramSolver.generate_2d_diagram(sec, theta=0.0, num_points=200, is_spiral=inp.is_spiral)
    diag_y = PMDiagramSolver.generate_2d_diagram(sec, theta=math.pi / 2.0, num_points=200, is_spiral=inp.is_spiral)
    
    dcr_eval = PMDiagramSolver.calculate_dcr(
        sec=sec,
        Pu=inp.Pu,
        Mux=slender_res.Mc_x,
        Muy=slender_res.Mc_y,
        is_spiral=inp.is_spiral
    )
    
    pm_dcr = dcr_eval["dcr"]
    is_pm_safe = dcr_eval["is_safe"]
    capacity_Mu = dcr_eval["capacity_Mu"]
    
    tracer.step(
        chapter="제 4장. 휨-압축 P-M 상관 강도 검토",
        section="4.1 200 파이버 비선형 수치적분 설계휨강도(phi Mn) 산정",
        standard_ref="KDS 14 20 20 (4.1.1)",
        formula=r"\phi M_{nx} = \phi \left[\int \sigma_c (y - y_0) dA_c + \sum A_{si} f_{si} (y_i - y_0)\right]",
        substitutions={"P_u": f"{inp.Pu:,.1f} kN", "M_{ux}": f"{slender_res.Mc_x:,.2f} kN·m"},
        result=f"{capacity_Mu:,.2f}",
        unit="kN·m",
        description="설계 축력 작용 시 단면의 파이버 수치적분 설계 휨내력"
    )
    
    # Bresler reciprocal biaxial evaluation
    P_bresler, bresler_dcr = calculate_bresler_capacity(
        Po=Po,
        diag_x=diag_x,
        diag_y=diag_y,
        Pu=inp.Pu,
        Mux=slender_res.Mc_x,
        Muy=slender_res.Mc_y
    )
    
    tracer.step(
        chapter="제 4장. 휨-압축 P-M 상관 강도 검토",
        section="4.2 Bresler 이축휨 상호작용 검토",
        standard_ref="KDS 14 20 20 (4.1.3)",
        formula=r"\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_0}",
        substitutions={"P_u": f"{inp.Pu:,.1f} kN", "M_{ux}": f"{slender_res.Mc_x:.1f}", "M_{uy}": f"{slender_res.Mc_y:.1f}"},
        result=f"phi_Pn = {0.65 * P_bresler:,.1f} (DCR = {bresler_dcr:.3f})",
        unit="kN",
        description="이축 휨 상태에서의 공칭 하중 역수 상호작용 강도"
    )
    
    tracer.evaluation(
        chapter="제 4장. 휨-압축 P-M 상관 강도 검토",
        title="휨-압축 P-M 상관 강도비 검토 (Mu <= phi Mn)",
        equation=r"M_u \le \phi M_n",
        left_val=f"{slender_res.Mc_x:,.2f}",
        right_val=f"{capacity_Mu:,.2f}",
        unit="kN·m",
        dcr=pm_dcr,
        status="OK" if is_pm_safe else "NG",
        standard_ref="KDS 14 20 20 (4.1.1)"
    )

    # -------------------------------------------------------------
    # Chapter 5: Shear Capacity with Axial Load & Tie Detailing
    # -------------------------------------------------------------
    d_y = inp.h - inp.cover
    Vcy, Vsy, phi_Vny, dcr_vy = calculate_column_shear(inp, b_w=inp.b, d=d_y, Vu=inp.Vuy, tie_legs=inp.tie_legs_x)
    
    d_x = inp.b - inp.cover
    Vcx, Vsx, phi_Vnx, dcr_vx = calculate_column_shear(inp, b_w=inp.h, d=d_x, Vu=inp.Vux, tie_legs=inp.tie_legs_y)
    
    is_shear_safe = (dcr_vy <= 1.0) and (dcr_vx <= 1.0)
    
    tracer.step(
        chapter="제 5장. 전단강도 및 띠철근 상세 검토",
        section="5.1 축압력을 받는 콘크리트 및 전단철근 부담 전단강도(Vc, Vs)",
        standard_ref="KDS 14 20 22 (4.3.2)",
        formula=r"V_c = \frac{1}{6}\left(1 + \frac{N_u}{14 A_g}\right)\lambda\sqrt{f_{ck}} b_w d, \quad V_s = \frac{A_v f_{yt} d}{s}",
        substitutions={"N_u": f"{inp.Pu:,.1f} kN", "b_w": f"{inp.b:.0f} mm", "d": f"{d_y:.0f} mm", "s": f"{inp.tie_spacing:.0f} mm"},
        result=f"Vc = {Vcy:,.1f} kN, Vs = {Vsy:,.1f} kN -> phi_Vn = {phi_Vny:,.1f}",
        unit="kN",
        description="축압력 증가 효과를 반영한 기둥의 설계전단강도"
    )
    
    # Tie Spacing Check (KDS 14 20 50)
    s_max_tie = min(16.0 * inp.bar_diam, 48.0 * inp.tie_diam, min(inp.b, inp.h))
    is_tie_ok = inp.tie_spacing <= s_max_tie
    
    tracer.step(
        chapter="제 5장. 전단강도 및 띠철근 상세 검토",
        section="5.2 띠철근 최대 배근 간격 한계(s_max)",
        standard_ref="KDS 14 20 50 (4.2.1)",
        formula=r"s_{max} = \min(16 d_b, 48 d_{tie}, \min(b, h))",
        substitutions={"16 d_b": f"{16.0 * inp.bar_diam:.1f} mm", "48 d_{tie}": f"{48.0 * inp.tie_diam:.1f} mm", "min(b, h)": f"{min(inp.b, inp.h):.0f} mm"},
        result=f"{s_max_tie:,.1f}",
        unit="mm",
        description="주철근 좌굴 방지를 위한 띠철근 최대 허용 간격"
    )
    
    tracer.evaluation(
        chapter="제 5장. 전단강도 및 띠철근 상세 검토",
        title="전단 강도비 적합성 판정 (Vu <= phi Vn)",
        equation=r"V_{uy} \le \phi V_{ny}",
        left_val=f"{inp.Vuy:,.1f}",
        right_val=f"{phi_Vny:,.1f}",
        unit="kN",
        dcr=round(dcr_vy, 3),
        status="OK" if dcr_vy <= 1.0 else "NG",
        standard_ref="KDS 14 20 22 (4.1.1)"
    )
    
    tracer.evaluation(
        chapter="제 5장. 전단강도 및 띠철근 상세 검토",
        title="띠철근 배근 간격 준수 여부 (s <= s_max)",
        equation=r"s \le s_{max}",
        left_val=f"{inp.tie_spacing:.0f}",
        right_val=f"{s_max_tie:.0f}",
        unit="mm",
        dcr=round(inp.tie_spacing / s_max_tie, 3),
        status="OK" if is_tie_ok else "NG",
        standard_ref="KDS 14 20 50 (4.2.1)"
    )

    # -------------------------------------------------------------
    # Overall Safety Summary & Packaging
    # -------------------------------------------------------------
    dcr_max = max(pm_dcr, dcr_vy, dcr_vx, dcr_rho)
    is_safe = is_pm_safe and is_shear_safe and is_rho_ok and is_tie_ok and tracer.is_safe
    status = "OK" if is_safe else "NG"
    
    summary = (
        f"[{status}] RC Column '{inp.name}' (DCR={dcr_max:.3f}) | "
        f"P-M: {pm_dcr:.3f}, Shear(Y): {dcr_vy:.3f}, Slender: X={slender_res.slenderness_x:.1f}(d={slender_res.delta_ns_x:.2f}), "
        f"rho={rho_g*100:.2f}%"
    )
    
    curve_x_pts = [{"Pn": p.Pn, "Mn": p.Mn, "phi_Pn": p.phi_Pn, "phi_Mn": p.phi_Mn} for p in diag_x.points]
    curve_y_pts = [{"Pn": p.Pn, "Mn": p.Mn, "phi_Pn": p.phi_Pn, "phi_Mn": p.phi_Mn} for p in diag_y.points]
    
    # Package CAD 2D Parametric Geometry
    geom = create_column_section_geometry(
        inp=inp,
        pm_diag_x=diag_x,
        pm_diag_y=diag_y,
        dcr_x=pm_dcr,
        dcr_y=bresler_dcr,
        capacity_Mux=capacity_Mu,
        capacity_Muy=0.0
    )
    
    return RCColumnDesignResult(
        name=inp.name,
        Ag=Ag,
        Ast=Ast,
        rho_g=rho_g,
        is_rho_ok=is_rho_ok,
        Po=Po,
        Pn_max=Pn_max,
        phi_Pn_max=phi_Pn_max,
        phi_Pt=diag_x.phi_Pt,
        slenderness=slender_res,
        design_Pu=inp.Pu,
        design_Mux=slender_res.Mc_x,
        design_Muy=slender_res.Mc_y,
        capacity_Mu=capacity_Mu,
        pm_dcr=pm_dcr,
        is_pm_safe=is_pm_safe,
        Vux=inp.Vux,
        phi_Vnx=phi_Vnx,
        shear_dcr_x=round(dcr_vx, 3),
        Vuy=inp.Vuy,
        phi_Vny=phi_Vny,
        shear_dcr_y=round(dcr_vy, 3),
        is_shear_safe=is_shear_safe,
        tie_spacing=inp.tie_spacing,
        tie_spacing_max=s_max_tie,
        is_tie_ok=is_tie_ok,
        dcr_max=round(dcr_max, 3),
        is_safe=is_safe,
        summary=summary,
        pm_curve_x=curve_x_pts,
        pm_curve_y=curve_y_pts,
        tracer=tracer.to_dict(),
        geometry=geom.to_dict(),
        bresler_dcr=bresler_dcr
    )
