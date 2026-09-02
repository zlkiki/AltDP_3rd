"""RC Column Design Engine (KDS 14 20 20 / KDS 14 20 50) for AltDP_3rd.

Integrates slenderness effects (moment magnification method), biaxial bending,
shear capacity with axial load, tie spacing requirements, and fiber-based 3D P-M solvers.
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Dict, Any, Optional

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
    """Comprehensive RC Column Design Output."""
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
    
    beta_dns = 0.2  # Sustained load ratio approximation
    EI_eff_x = (0.4 * Ec * Ig_x) / (1.0 + beta_dns)
    EI_eff_y = (0.4 * Ec * Ig_y) / (1.0 + beta_dns)
    
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


def create_standard_column_fiber_section(inp: RCColumnInput, nx: int = 20, ny: int = 20) -> FiberSection:
    """Generate FiberSection with perimeter distributed longitudinal rebar."""
    b, h = inp.b, inp.h
    cover = inp.cover
    single_bar_area = math.pi * (inp.bar_diam ** 2) / 4.0
    
    # Distribute bars uniformly around perimeter
    # Coordinates of rebar perimeter box
    x_left = -b / 2.0 + cover
    x_right = b / 2.0 - cover
    y_bot = -h / 2.0 + cover
    y_top = h / 2.0 - cover
    
    rebars: List[Tuple[float, float, float]] = []
    
    # 4 corner bars minimum
    total = max(4, inp.total_bars)
    bars_x = max(2, total // 4 + 1)
    bars_y = max(2, (total - 2 * bars_x) // 2 + 2) if total > 4 else 2
    
    # Top & Bottom faces
    dx = (x_right - x_left) / (bars_x - 1) if bars_x > 1 else 0.0
    for i in range(bars_x):
        x = x_left + i * dx
        rebars.append((x, y_top, single_bar_area))
        rebars.append((x, y_bot, single_bar_area))
        
    # Side faces (excluding corners)
    dy = (y_top - y_bot) / (bars_y - 1) if bars_y > 1 else 0.0
    for j in range(1, bars_y - 1):
        y = y_bot + j * dy
        rebars.append((x_left, y, single_bar_area))
        rebars.append((x_right, y, single_bar_area))
        
    # Trim to exact total_bars count if needed
    if len(rebars) > inp.total_bars:
        rebars = rebars[:inp.total_bars]
    elif len(rebars) < inp.total_bars:
        while len(rebars) < inp.total_bars:
            rebars.append((0.0, 0.0, single_bar_area))
            
    return FiberSection.from_rect(
        b=b, h=h, rebars=rebars, nx=nx, ny=ny,
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


def design_rc_column(inp: RCColumnInput) -> RCColumnDesignResult:
    """Comprehensive design and verification of RC column according to KDS 14 20 00."""
    Ag = inp.Ag
    Ast = inp.Ast
    rho_g = Ast / Ag
    is_rho_ok = 0.01 <= rho_g <= 0.08
    
    # 1. Slenderness & Moment Magnification
    slender_res = evaluate_slenderness(inp)
    
    # 2. Fiber Section & P-M Diagrams
    sec = create_standard_column_fiber_section(inp, nx=20, ny=20)
    
    diag_x = PMDiagramSolver.generate_2d_diagram(sec, theta=0.0, num_points=35, is_spiral=inp.is_spiral)
    diag_y = PMDiagramSolver.generate_2d_diagram(sec, theta=math.pi / 2.0, num_points=35, is_spiral=inp.is_spiral)
    
    # 3. 3D DCR Evaluation using Magnified Design Moments Mc_x, Mc_y
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
    
    # 4. Shear Capacity Verification in X and Y directions
    # Resisting Vy: depth = h, width = b
    d_y = inp.h - inp.cover
    _, _, phi_Vny, dcr_vy = calculate_column_shear(inp, b_w=inp.b, d=d_y, Vu=inp.Vuy, tie_legs=inp.tie_legs_x)
    
    # Resisting Vx: depth = b, width = h
    d_x = inp.b - inp.cover
    _, _, phi_Vnx, dcr_vx = calculate_column_shear(inp, b_w=inp.h, d=d_x, Vu=inp.Vux, tie_legs=inp.tie_legs_y)
    
    is_shear_safe = (dcr_vy <= 1.0) and (dcr_vx <= 1.0)
    
    # 5. Tie Spacing Verification (KDS 14 20 50)
    # s_max = min(16 * db, 48 * dt, min(b, h))
    s_max_tie = min(16.0 * inp.bar_diam, 48.0 * inp.tie_diam, min(inp.b, inp.h))
    is_tie_ok = inp.tie_spacing <= s_max_tie
    
    # 6. Overall Safety & Summary
    dcr_max = max(pm_dcr, dcr_vy, dcr_vx)
    is_safe = is_pm_safe and is_shear_safe and is_rho_ok and is_tie_ok
    status = "OK" if is_safe else "NG"
    
    summary = (
        f"[{status}] RC Column '{inp.name}' (DCR={dcr_max:.3f}) | "
        f"P-M: {pm_dcr:.3f}, Shear(Y): {dcr_vy:.3f}, Slender: X={slender_res.slenderness_x:.1f}(d={slender_res.delta_ns_x:.2f}), "
        f"rho={rho_g*100:.2f}%"
    )
    
    curve_x_pts = [{"Pn": p.Pn, "Mn": p.Mn, "phi_Pn": p.phi_Pn, "phi_Mn": p.phi_Mn} for p in diag_x.points]
    curve_y_pts = [{"Pn": p.Pn, "Mn": p.Mn, "phi_Pn": p.phi_Pn, "phi_Mn": p.phi_Mn} for p in diag_y.points]
    
    return RCColumnDesignResult(
        name=inp.name,
        Ag=Ag,
        Ast=Ast,
        rho_g=rho_g,
        is_rho_ok=is_rho_ok,
        Po=diag_x.Po,
        Pn_max=diag_x.Pn_max,
        phi_Pn_max=diag_x.phi_Pn_max,
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
        pm_curve_y=curve_y_pts
    )
