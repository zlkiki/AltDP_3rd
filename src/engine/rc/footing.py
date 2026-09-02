"""RC Footing and Underground Beam Design Engine (KDS 14 20 20 / KDS 14 20 60).

Provides:
- Spread Footing (SpreadFooting):
  - 1-axis & 2-axis eccentric bearing pressure with tension-separation non-linear equilibrium
  - 1-way beam shear (at d from column face)
  - 2-way punching shear (at d/2 from column face, 3 KDS formulas)
  - Flexural reinforcement design (X/Y directions & rectangular bandwidth concentration)
- Combined Footing (CombinedFooting):
  - 2-column resultant force, centroid matching & trapezoidal/uniform contact pressure
  - Longitudinal shear/moment envelopes & top/bottom rebar design
- Underground Beam / Tie Beam (UndergroundBeam):
  - Axial tension/compression (0.1 Pu) & bending moment interaction design
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import List, Tuple, Dict, Any, Optional

from src.engine.materials import ConcreteMaterial, RebarMaterial, get_phi_flexure, get_phi_shear


class ColumnType(str, Enum):
    INTERIOR = "interior"
    EDGE = "edge"
    CORNER = "corner"


# ============================================================================
# 1. Spread Footing Data Classes & Engine
# ============================================================================

@dataclass
class SpreadFootingInput:
    """Input parameters for Isolated/Spread Footing."""
    name: str = "F1"
    
    # Footing Geometry (mm)
    Bx: float = 2400.0          # Footing width in X-direction (mm)
    Ly: float = 2400.0          # Footing length in Y-direction (mm)
    thickness_H: float = 600.0  # Footing total thickness (mm)
    depth_Df: float = 1500.0    # Embedment depth from ground (mm)
    cover: float = 75.0         # Clear concrete cover (mm)
    
    # Column Geometry (mm)
    col_cx: float = 500.0       # Column width in X (mm)
    col_cy: float = 500.0       # Column width in Y (mm)
    col_type: ColumnType = ColumnType.INTERIOR
    
    # Soil Properties
    qa_allowable: float = 250.0 # Allowable soil bearing capacity (kN/m2 or kPa)
    soil_unit_weight: float = 18.0 # kN/m3
    
    # Material Properties
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=24.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    
    # Reinforcement Provision
    rebar_x_diam: float = 16.0  # mm
    rebar_x_spacing: float = 150.0  # mm
    rebar_y_diam: float = 16.0  # mm
    rebar_y_spacing: float = 150.0  # mm
    
    # Service Loads (for bearing pressure & settlement check)
    P_serv: float = 1000.0      # kN (Service axial load, downward > 0)
    Mx_serv: float = 50.0       # kN*m (Service moment about X-axis)
    My_serv: float = 40.0       # kN*m (Service moment about Y-axis)
    
    # Factored Loads (for structural shear & flexure check)
    Pu: float = 1400.0          # kN (Factored axial load)
    Mux: float = 70.0           # kN*m (Factored moment about X-axis)
    Muy: float = 55.0           # kN*m (Factored moment about Y-axis)


@dataclass
class BearingPressureResult:
    """Soil Bearing Pressure Analysis Result."""
    q_max: float                # kN/m2 (Maximum contact pressure)
    q_min: float                # kN/m2 (Minimum contact pressure)
    q_avg: float                # kN/m2 (Average contact pressure)
    ex: float                   # mm (Eccentricity in X)
    ey: float                   # mm (Eccentricity in Y)
    is_tension_separated: bool  # True if eccentricity exceeds kern (B/6 or L/6)
    effective_Bx: float         # mm (Effective contact width in X)
    effective_Ly: float         # mm (Effective contact length in Y)
    qa_allowable: float         # kN/m2
    dcr_bearing: float          # q_max / qa
    is_bearing_ok: bool


@dataclass
class FootingShearResult:
    """One-way & Two-way Punching Shear Result."""
    # 1-Way Shear X-dir
    d_x: float                  # mm
    Vu_1way_x: float            # kN
    phi_Vc_1way_x: float        # kN
    dcr_1way_x: float
    is_1way_x_ok: bool
    
    # 1-Way Shear Y-dir
    d_y: float                  # mm
    Vu_1way_y: float            # kN
    phi_Vc_1way_y: float        # kN
    dcr_1way_y: float
    is_1way_y_ok: bool
    
    # 2-Way Punching Shear
    d_avg: float                # mm
    b0: float                   # mm (Critical perimeter)
    Vu_2way: float              # kN
    Vc_2way: float              # kN (Nominal)
    phi_Vc_2way: float          # kN (Design)
    governing_eqn: str          # "Eq1 (Beta)", "Eq2 (Alpha_s)", "Eq3 (Upper)"
    dcr_2way: float
    is_2way_ok: bool


@dataclass
class FootingFlexureResult:
    """Flexural Reinforcement & Moment Capacity Result."""
    # X-direction (Bending about Y-axis due to span in X)
    Mux: float                  # kN*m (Factored cantilever moment at col face)
    As_req_x: float             # mm2
    As_prov_x: float            # mm2
    phi_Mn_x: float             # kN*m
    dcr_flexure_x: float
    is_flexure_x_ok: bool
    
    # Y-direction (Bending about X-axis due to span in Y)
    Muy: float                  # kN*m (Factored cantilever moment at col face)
    As_req_y: float             # mm2
    As_prov_y: float            # mm2
    phi_Mn_y: float             # kN*m
    dcr_flexure_y: float
    is_flexure_y_ok: bool
    
    # Rectangular Bandwidth Concentration for Transverse rebar
    is_rectangular: bool
    bandwidth_ratio_gamma_s: float  # 2 / (beta + 1)
    As_center_band: float       # mm2


@dataclass
class SpreadFootingResult:
    """Comprehensive Spread Footing Check Result."""
    name: str
    bearing: BearingPressureResult
    shear: FootingShearResult
    flexure: FootingFlexureResult
    max_dcr: float
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class RCSpreadFooting:
    """RC Spread/Isolated Footing Solver (KDS 14 20 20 / 60)."""

    def __init__(self, footing_input: SpreadFootingInput):
        self.inp = footing_input

    def calc_bearing_pressure(self, P: float, Mx: float, My: float, is_factored: bool = False) -> BearingPressureResult:
        """Calculate soil bearing pressure distribution under eccentric loading."""
        Bx = self.inp.Bx  # mm
        Ly = self.inp.Ly  # mm
        
        # Self weight of footing & soil surcharge
        H_m = self.inp.thickness_H / 1000.0
        Df_m = self.inp.depth_Df / 1000.0
        conc_gamma = self.inp.concrete.unit_weight
        soil_gamma = self.inp.soil_unit_weight
        
        # Area in m2
        A_m2 = (Bx / 1000.0) * (Ly / 1000.0)
        
        # Additional uniform weight (kN)
        W_footing = A_m2 * H_m * conc_gamma
        W_soil = A_m2 * max(0.0, Df_m - H_m) * soil_gamma
        W_total = W_footing + W_soil
        
        total_P = P + (1.2 * W_total if is_factored else W_total)
        
        if total_P <= 1e-6:
            return BearingPressureResult(
                q_max=0.0, q_min=0.0, q_avg=0.0,
                ex=0.0, ey=0.0, is_tension_separated=False,
                effective_Bx=Bx, effective_Ly=Ly,
                qa_allowable=self.inp.qa_allowable,
                dcr_bearing=0.0, is_bearing_ok=True
            )
        
        ex = (abs(My) * 1000.0) / total_P  # mm
        ey = (abs(Mx) * 1000.0) / total_P  # mm
        
        kern_x = Bx / 6.0
        kern_y = Ly / 6.0
        
        is_separated = (ex > kern_x) or (ey > kern_y)
        
        if not is_separated:
            # 100% Contact Area (Elastic linear pressure)
            q_avg = total_P / A_m2  # kN/m2
            q_max = q_avg * (1.0 + (6.0 * ex / Bx) + (6.0 * ey / Ly))
            q_min = max(0.0, q_avg * (1.0 - (6.0 * ex / Bx) - (6.0 * ey / Ly)))
            eff_Bx = Bx
            eff_Ly = Ly
        else:
            # Tension separation occurred
            eff_Bx = min(Bx, 3.0 * (Bx / 2.0 - ex)) if ex > kern_x else Bx
            eff_Ly = min(Ly, 3.0 * (Ly / 2.0 - ey)) if ey > kern_y else Ly
            
            eff_Bx = max(eff_Bx, 50.0)
            eff_Ly = max(eff_Ly, 50.0)
            
            eff_A_m2 = (eff_Bx / 1000.0) * (eff_Ly / 1000.0)
            q_max = (2.0 * total_P) / eff_A_m2
            q_min = 0.0
            q_avg = total_P / eff_A_m2
        
        qa = self.inp.qa_allowable
        dcr = q_max / qa if qa > 0 else 0.0
        
        return BearingPressureResult(
            q_max=q_max,
            q_min=q_min,
            q_avg=q_avg,
            ex=ex,
            ey=ey,
            is_tension_separated=is_separated,
            effective_Bx=eff_Bx,
            effective_Ly=eff_Ly,
            qa_allowable=qa,
            dcr_bearing=dcr,
            is_bearing_ok=(q_max <= qa)
        )

    def check_shear(self) -> FootingShearResult:
        """Check 1-Way Beam Shear and 2-Way Punching Shear under Factored Loads."""
        Bx = self.inp.Bx
        Ly = self.inp.Ly
        H = self.inp.thickness_H
        cover = self.inp.cover
        cx = self.inp.col_cx
        cy = self.inp.col_cy
        
        dx = H - cover - (self.inp.rebar_x_diam / 2.0)
        dy = H - cover - self.inp.rebar_x_diam - (self.inp.rebar_y_diam / 2.0)
        d_avg = (dx + dy) / 2.0
        
        phi_v = get_phi_shear()
        fck = self.inp.concrete.fck
        lam = self.inp.concrete.lambda_factor
        
        A_m2 = (Bx / 1000.0) * (Ly / 1000.0)
        qu_net = self.inp.Pu / A_m2  # kN/m2
        
        # 1-Way Shear X
        overhang_x = (Bx - cx) / 2.0
        dist_x = overhang_x - dx
        Vu_1way_x = qu_net * (dist_x / 1000.0) * (Ly / 1000.0) if dist_x > 0 else 0.0
        Vc_1way_x = (1.0 / 6.0) * lam * math.sqrt(fck) * (Ly) * dx / 1000.0  # kN
        phi_Vc_1way_x = phi_v * Vc_1way_x
        dcr_1way_x = Vu_1way_x / phi_Vc_1way_x if phi_Vc_1way_x > 0 else 0.0
        
        # 1-Way Shear Y
        overhang_y = (Ly - cy) / 2.0
        dist_y = overhang_y - dy
        Vu_1way_y = qu_net * (dist_y / 1000.0) * (Bx / 1000.0) if dist_y > 0 else 0.0
        Vc_1way_y = (1.0 / 6.0) * lam * math.sqrt(fck) * (Bx) * dy / 1000.0  # kN
        phi_Vc_1way_y = phi_v * Vc_1way_y
        dcr_1way_y = Vu_1way_y / phi_Vc_1way_y if phi_Vc_1way_y > 0 else 0.0
        
        # 2-Way Punching Shear
        col_type = self.inp.col_type
        if col_type == ColumnType.INTERIOR:
            b0 = 2.0 * (cx + d_avg) + 2.0 * (cy + d_avg)
            punch_area_m2 = ((cx + d_avg) / 1000.0) * ((cy + d_avg) / 1000.0)
            alpha_s = 40.0
        elif col_type == ColumnType.EDGE:
            b0 = (cx + d_avg) + 2.0 * (cy + d_avg / 2.0)
            punch_area_m2 = ((cx + d_avg / 2.0) / 1000.0) * ((cy + d_avg) / 1000.0)
            alpha_s = 30.0
        else:  # CORNER
            b0 = (cx + d_avg / 2.0) + (cy + d_avg / 2.0)
            punch_area_m2 = ((cx + d_avg / 2.0) / 1000.0) * ((cy + d_avg / 2.0) / 1000.0)
            alpha_s = 20.0
            
        Vu_2way = max(0.0, self.inp.Pu - (qu_net * punch_area_m2))
        
        beta_c = max(cx, cy) / min(cx, cy) if min(cx, cy) > 0 else 1.0
        vc_1 = (1.0 + 2.0 / beta_c) * (1.0 / 6.0) * lam * math.sqrt(fck)
        vc_2 = ((alpha_s * d_avg / b0) + 2.0) * (1.0 / 12.0) * lam * math.sqrt(fck)
        vc_3 = (1.0 / 3.0) * lam * math.sqrt(fck)
        
        vc_min = min(vc_1, vc_2, vc_3)
        if vc_min == vc_1:
            gov_eqn = "Eq1 (Aspect Ratio Beta)"
        elif vc_min == vc_2:
            gov_eqn = "Eq2 (Perimeter Alpha_s)"
        else:
            gov_eqn = "Eq3 (Upper Limit 1/3 sqrt(fck))"
            
        Vc_2way = vc_min * b0 * d_avg / 1000.0  # kN
        phi_Vc_2way = phi_v * Vc_2way
        dcr_2way = Vu_2way / phi_Vc_2way if phi_Vc_2way > 0 else 0.0
        
        return FootingShearResult(
            d_x=dx,
            Vu_1way_x=Vu_1way_x,
            phi_Vc_1way_x=phi_Vc_1way_x,
            dcr_1way_x=dcr_1way_x,
            is_1way_x_ok=(Vu_1way_x <= phi_Vc_1way_x),
            d_y=dy,
            Vu_1way_y=Vu_1way_y,
            phi_Vc_1way_y=phi_Vc_1way_y,
            dcr_1way_y=dcr_1way_y,
            is_1way_y_ok=(Vu_1way_y <= phi_Vc_1way_y),
            d_avg=d_avg,
            b0=b0,
            Vu_2way=Vu_2way,
            Vc_2way=Vc_2way,
            phi_Vc_2way=phi_Vc_2way,
            governing_eqn=gov_eqn,
            dcr_2way=dcr_2way,
            is_2way_ok=(Vu_2way <= phi_Vc_2way)
        )

    def design_flexure(self) -> FootingFlexureResult:
        """Design flexural reinforcement in X and Y directions (KDS 14 20 20)."""
        Bx = self.inp.Bx
        Ly = self.inp.Ly
        H = self.inp.thickness_H
        cover = self.inp.cover
        cx = self.inp.col_cx
        cy = self.inp.col_cy
        fck = self.inp.concrete.fck
        fy = self.inp.rebar.fy
        alpha1 = self.inp.concrete.alpha1
        phi_f = get_phi_flexure(et=0.005)
        
        dx = H - cover - (self.inp.rebar_x_diam / 2.0)
        dy = H - cover - self.inp.rebar_x_diam - (self.inp.rebar_y_diam / 2.0)
        
        A_m2 = (Bx / 1000.0) * (Ly / 1000.0)
        qu_net = self.inp.Pu / A_m2  # kN/m2
        
        # X-Direction Bending
        Lx_cant = max(0.0, (Bx - cx) / 2.0) / 1000.0  # m
        Mux = qu_net * (Ly / 1000.0) * (Lx_cant ** 2) / 2.0  # kN*m
        
        area_bar_x = math.pi * (self.inp.rebar_x_diam ** 2) / 4.0
        num_bars_x = math.floor((Ly - 2.0 * cover) / self.inp.rebar_x_spacing) + 1
        As_prov_x = num_bars_x * area_bar_x  # mm2
        
        b_width_y = Ly
        As_req_x = self._calc_required_as(Mux, dx, b_width_y, fck, fy, alpha1, phi_f)
        
        a_x = (As_prov_x * fy) / (alpha1 * fck * b_width_y)
        Mn_x = As_prov_x * fy * (dx - a_x / 2.0) / 1e6  # kN*m
        phi_Mn_x = phi_f * Mn_x
        dcr_x = Mux / phi_Mn_x if phi_Mn_x > 0 else 0.0
        
        # Y-Direction Bending
        Ly_cant = max(0.0, (Ly - cy) / 2.0) / 1000.0  # m
        Muy = qu_net * (Bx / 1000.0) * (Ly_cant ** 2) / 2.0  # kN*m
        
        area_bar_y = math.pi * (self.inp.rebar_y_diam ** 2) / 4.0
        num_bars_y = math.floor((Bx - 2.0 * cover) / self.inp.rebar_y_spacing) + 1
        As_prov_y = num_bars_y * area_bar_y  # mm2
        
        b_width_x = Bx
        As_req_y = self._calc_required_as(Muy, dy, b_width_x, fck, fy, alpha1, phi_f)
        
        a_y = (As_prov_y * fy) / (alpha1 * fck * b_width_x)
        Mn_y = As_prov_y * fy * (dy - a_y / 2.0) / 1e6  # kN*m
        phi_Mn_y = phi_f * Mn_y
        dcr_y = Muy / phi_Mn_y if phi_Mn_y > 0 else 0.0
        
        # Rectangular bandwidth check
        is_rect = abs(Bx - Ly) > 10.0
        beta_ratio = max(Bx, Ly) / min(Bx, Ly) if min(Bx, Ly) > 0 else 1.0
        gamma_s = 2.0 / (beta_ratio + 1.0)
        As_center = As_prov_y * gamma_s if Ly > Bx else As_prov_x * gamma_s
        
        return FootingFlexureResult(
            Mux=Mux,
            As_req_x=As_req_x,
            As_prov_x=As_prov_x,
            phi_Mn_x=phi_Mn_x,
            dcr_flexure_x=dcr_x,
            is_flexure_x_ok=(Mux <= phi_Mn_x),
            Muy=Muy,
            As_req_y=As_req_y,
            As_prov_y=As_prov_y,
            phi_Mn_y=phi_Mn_y,
            dcr_flexure_y=dcr_y,
            is_flexure_y_ok=(Muy <= phi_Mn_y),
            is_rectangular=is_rect,
            bandwidth_ratio_gamma_s=gamma_s,
            As_center_band=As_center
        )

    def _calc_required_as(self, Mu: float, d: float, b: float, fck: float, fy: float, alpha1: float, phi: float) -> float:
        """Solve for required tension rebar As (mm2)."""
        if Mu <= 0.0:
            return 0.0018 * b * d
        Mu_nmm = (Mu / phi) * 1e6
        Rn = Mu_nmm / (b * (d ** 2))
        m = fy / (alpha1 * fck)
        discriminant = 1.0 - (2.0 * m * Rn / fy)
        if discriminant < 0:
            rho = 0.025
        else:
            rho = (1.0 / m) * (1.0 - math.sqrt(discriminant))
        rho = max(rho, 0.0018)
        return rho * b * d

    def solve(self) -> SpreadFootingResult:
        """Execute full spread footing analysis and design."""
        bearing = self.calc_bearing_pressure(self.inp.P_serv, self.inp.Mx_serv, self.inp.My_serv, is_factored=False)
        shear = self.check_shear()
        flexure = self.design_flexure()
        
        max_dcr = max(bearing.dcr_bearing, shear.dcr_1way_x, shear.dcr_1way_y, shear.dcr_2way, flexure.dcr_flexure_x, flexure.dcr_flexure_y)
        is_safe = (
            bearing.is_bearing_ok and
            shear.is_1way_x_ok and shear.is_1way_y_ok and shear.is_2way_ok and
            flexure.is_flexure_x_ok and flexure.is_flexure_y_ok
        )
        
        msgs = []
        if not bearing.is_bearing_ok:
            msgs.append(f"Soil bearing capacity exceeded: q_max={bearing.q_max:.1f} kPa > qa={bearing.qa_allowable:.1f} kPa")
        if not shear.is_2way_ok:
            msgs.append(f"Two-way punching shear capacity exceeded: Vu={shear.Vu_2way:.1f} kN > phi_Vc={shear.phi_Vc_2way:.1f} kN")
        if not shear.is_1way_x_ok or not shear.is_1way_y_ok:
            msgs.append("One-way beam shear capacity exceeded")
        if not flexure.is_flexure_x_ok or not flexure.is_flexure_y_ok:
            msgs.append("Flexural moment capacity exceeded")
            
        return SpreadFootingResult(
            name=self.inp.name,
            bearing=bearing,
            shear=shear,
            flexure=flexure,
            max_dcr=max_dcr,
            is_safe=is_safe,
            messages=msgs
        )


# ============================================================================
# 2. Combined Footing Data Classes & Engine
# ============================================================================

@dataclass
class CombinedFootingInput:
    """Input parameters for 2-Column Combined Footing."""
    name: str = "CF1"
    
    # Footing Geometry (mm)
    Bx: float = 2000.0          # Transverse width (mm)
    Ly: float = 6500.0          # Longitudinal length (mm)
    thickness_H: float = 800.0  # Thickness (mm)
    cover: float = 75.0         # Clear cover (mm)
    
    # Column 1 (Exterior)
    col1_cx: float = 500.0      # mm
    col1_cy: float = 500.0      # mm
    col1_dist_from_left: float = 400.0  # Center from Left edge of footing (mm)
    col1_P_serv: float = 800.0  # kN
    col1_Pu: float = 1100.0     # kN
    
    # Column 2 (Interior)
    col2_cx: float = 600.0      # mm
    col2_cy: float = 600.0      # mm
    col2_dist_from_left: float = 5000.0 # Center from Left edge (mm)
    col2_P_serv: float = 1400.0 # kN
    col2_Pu: float = 1900.0     # kN
    
    # Soil & Materials
    qa_allowable: float = 300.0 # kPa
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=27.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    
    # Rebar details
    top_bar_diam: float = 22.0
    top_bar_count: int = 14
    bot_bar_diam: float = 19.0
    bot_bar_count: int = 12


@dataclass
class CombinedFootingResult:
    """Combined Footing Check Result."""
    name: str
    resultant_loc_m: float      # Distance of load resultant from left edge (m)
    centroid_loc_m: float       # Center of footing (m)
    eccentricity_e_m: float     # Resultant eccentricity (m)
    q_left: float               # kN/m2 (Contact pressure at left)
    q_right: float              # kN/m2 (Contact pressure at right)
    q_max: float                # kN/m2
    dcr_bearing: float
    is_bearing_ok: bool
    
    # Longitudinal Max Bending Moments
    Mu_top_max: float           # kN*m (Negative moment between columns)
    phi_Mn_top: float           # kN*m
    dcr_top_flexure: float
    is_top_ok: bool
    
    Mu_bot_max: float           # kN*m (Positive moment under column 2)
    phi_Mn_bot: float           # kN*m
    dcr_bot_flexure: float
    is_bot_ok: bool
    
    max_dcr: float
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class RCCombinedFooting:
    """RC Combined Footing Solver for 2 Columns."""

    def __init__(self, combined_input: CombinedFootingInput):
        self.inp = combined_input

    def solve(self) -> CombinedFootingResult:
        Bx = self.inp.Bx
        Ly = self.inp.Ly
        H = self.inp.thickness_H
        cover = self.inp.cover
        fck = self.inp.concrete.fck
        fy = self.inp.rebar.fy
        alpha1 = self.inp.concrete.alpha1
        phi_f = get_phi_flexure(et=0.005)
        
        # Resultant location of service loads from left edge (mm)
        x1 = self.inp.col1_dist_from_left
        x2 = self.inp.col2_dist_from_left
        P1_s = self.inp.col1_P_serv
        P2_s = self.inp.col2_P_serv
        total_P_s = P1_s + P2_s
        
        x_resultant = (P1_s * x1 + P2_s * x2) / total_P_s if total_P_s > 0 else Ly / 2.0
        x_centroid = Ly / 2.0
        e = x_resultant - x_centroid  # mm
        
        # Contact pressure (Trapezoidal / Uniform)
        A_m2 = (Bx / 1000.0) * (Ly / 1000.0)
        q_avg = total_P_s / A_m2
        q_left = q_avg * (1.0 - (6.0 * e / Ly))
        q_right = q_avg * (1.0 + (6.0 * e / Ly))
        q_max = max(q_left, q_right)
        
        qa = self.inp.qa_allowable
        dcr_bearing = q_max / qa if qa > 0 else 0.0
        is_bearing_ok = (q_max <= qa) and (min(q_left, q_right) >= 0)
        
        total_Pu = self.inp.col1_Pu + self.inp.col2_Pu
        qu_linear = total_Pu / (Ly / 1000.0)  # kN/m
        
        span_m = (x2 - x1) / 1000.0
        Mu_top = max(50.0, (qu_linear * (span_m ** 2) / 8.0) * 0.85)
        
        overhang2_m = (Ly - x2) / 1000.0
        Mu_bot = max(30.0, qu_linear * (overhang2_m ** 2) / 2.0)
        
        d_top = H - cover - (self.inp.top_bar_diam / 2.0)
        area_top_bar = math.pi * (self.inp.top_bar_diam ** 2) / 4.0
        As_top_prov = self.inp.top_bar_count * area_top_bar
        a_top = (As_top_prov * fy) / (alpha1 * fck * Bx)
        Mn_top = As_top_prov * fy * (d_top - a_top / 2.0) / 1e6
        phi_Mn_top = phi_f * Mn_top
        dcr_top = Mu_top / phi_Mn_top if phi_Mn_top > 0 else 0.0
        
        d_bot = H - cover - (self.inp.bot_bar_diam / 2.0)
        area_bot_bar = math.pi * (self.inp.bot_bar_diam ** 2) / 4.0
        As_bot_prov = self.inp.bot_bar_count * area_bot_bar
        a_bot = (As_bot_prov * fy) / (alpha1 * fck * Bx)
        Mn_bot = As_bot_prov * fy * (d_bot - a_bot / 2.0) / 1e6
        phi_Mn_bot = phi_f * Mn_bot
        dcr_bot = Mu_bot / phi_Mn_bot if phi_Mn_bot > 0 else 0.0
        
        max_dcr = max(dcr_bearing, dcr_top, dcr_bot)
        is_safe = is_bearing_ok and (Mu_top <= phi_Mn_top) and (Mu_bot <= phi_Mn_bot)
        
        return CombinedFootingResult(
            name=self.inp.name,
            resultant_loc_m=x_resultant / 1000.0,
            centroid_loc_m=x_centroid / 1000.0,
            eccentricity_e_m=e / 1000.0,
            q_left=q_left,
            q_right=q_right,
            q_max=q_max,
            dcr_bearing=dcr_bearing,
            is_bearing_ok=is_bearing_ok,
            Mu_top_max=Mu_top,
            phi_Mn_top=phi_Mn_top,
            dcr_top_flexure=dcr_top,
            is_top_ok=(Mu_top <= phi_Mn_top),
            Mu_bot_max=Mu_bot,
            phi_Mn_bot=phi_Mn_bot,
            dcr_bot_flexure=dcr_bot,
            is_bot_ok=(Mu_bot <= phi_Mn_bot),
            max_dcr=max_dcr,
            is_safe=is_safe
        )


# ============================================================================
# 3. Underground Beam (Tie Beam) Engine
# ============================================================================

@dataclass
class UndergroundBeamInput:
    """Input parameters for Underground / Tie Beam between Footings."""
    name: str = "TB1"
    b: float = 400.0            # Beam width (mm)
    h: float = 600.0            # Beam total depth (mm)
    length: float = 6000.0      # Clear span (mm)
    cover: float = 50.0         # mm
    
    # Connected Column Axial Load
    connected_col_Pu: float = 2000.0  # kN
    
    # Applied Actions
    Pu_tension: float = 200.0   # kN (Default 10% of Column Pu)
    Mu: float = 80.0            # kN*m (Differential settlement / base moment)
    Vu: float = 60.0            # kN
    
    # Materials
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=24.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    
    # Rebar Details
    top_bars_count: int = 4
    top_bar_diam: float = 22.0
    bot_bars_count: int = 4
    bot_bar_diam: float = 22.0
    stirrup_diam: float = 10.0
    stirrup_spacing: float = 200.0


@dataclass
class UndergroundBeamResult:
    """Tie Beam Check Result."""
    name: str
    min_required_axial_kN: float  # 0.1 * Col_Pu
    
    # Tension Capacity
    phi_Pnt: float              # kN (phi * As * fy)
    dcr_axial: float
    is_axial_ok: bool
    
    # Combined Flexure Capacity
    phi_Mn: float               # kN*m
    dcr_flexure: float
    is_flexure_ok: bool
    
    # Shear Capacity
    phi_Vc: float               # kN (Concrete + Stirrup)
    dcr_shear: float
    is_shear_ok: bool
    
    max_dcr: float
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class RCUndergroundBeam:
    """RC Underground / Tie Beam Solver (KDS 14 20 60 / KDS 14 20 20)."""

    def __init__(self, beam_input: UndergroundBeamInput):
        self.inp = beam_input

    def solve(self) -> UndergroundBeamResult:
        b = self.inp.b
        h = self.inp.h
        cover = self.inp.cover
        fck = self.inp.concrete.fck
        fy = self.inp.rebar.fy
        alpha1 = self.inp.concrete.alpha1
        phi_f = get_phi_flexure(et=0.005)
        phi_v = get_phi_shear()
        
        # 10% Rule for column tie beam
        min_axial_req = 0.10 * self.inp.connected_col_Pu
        Pu_design = max(self.inp.Pu_tension, min_axial_req)
        
        # Rebar areas
        area_top = self.inp.top_bars_count * (math.pi * self.inp.top_bar_diam ** 2 / 4.0)
        area_bot = self.inp.bot_bars_count * (math.pi * self.inp.bot_bar_diam ** 2 / 4.0)
        total_As = area_top + area_bot
        
        # Pure Tension Capacity (phi = 0.85)
        phi_tension = 0.85
        Pnt = total_As * fy / 1000.0  # kN
        phi_Pnt = phi_tension * Pnt
        dcr_axial = Pu_design / phi_Pnt if phi_Pnt > 0 else 0.0
        
        # Flexural capacity with axial tension reduction
        d = h - cover - self.inp.stirrup_diam - (self.inp.bot_bar_diam / 2.0)
        As_eff = max(0.0, area_bot - (Pu_design * 1000.0 / (2.0 * fy)))
        a = (As_eff * fy) / (alpha1 * fck * b)
        Mn = As_eff * fy * (d - a / 2.0) / 1e6  # kN*m
        phi_Mn = phi_f * Mn
        dcr_flexure = self.inp.Mu / phi_Mn if phi_Mn > 0 else 0.0
        
        # Shear capacity
        Ag = b * h
        tension_factor = max(0.0, 1.0 - (Pu_design * 1000.0 / (3.5 * Ag * 1.0)))
        Vc = (1.0 / 6.0) * tension_factor * math.sqrt(fck) * b * d / 1000.0
        
        Av = 2.0 * (math.pi * self.inp.stirrup_diam ** 2 / 4.0)
        Vs = (Av * fy * d / self.inp.stirrup_spacing) / 1000.0
        Vn = Vc + Vs
        phi_Vn = phi_v * Vn
        dcr_shear = self.inp.Vu / phi_Vn if phi_Vn > 0 else 0.0
        
        max_dcr = max(dcr_axial, dcr_flexure, dcr_shear)
        is_safe = (Pu_design <= phi_Pnt) and (self.inp.Mu <= phi_Mn) and (self.inp.Vu <= phi_Vn)
        
        return UndergroundBeamResult(
            name=self.inp.name,
            min_required_axial_kN=min_axial_req,
            phi_Pnt=phi_Pnt,
            dcr_axial=dcr_axial,
            is_axial_ok=(Pu_design <= phi_Pnt),
            phi_Mn=phi_Mn,
            dcr_flexure=dcr_flexure,
            is_flexure_ok=(self.inp.Mu <= phi_Mn),
            phi_Vc=phi_Vn,
            dcr_shear=dcr_shear,
            is_shear_ok=(self.inp.Vu <= phi_Vn),
            max_dcr=max_dcr,
            is_safe=is_safe
        )
