"""RC Retaining Wall & Basement Wall Design Engine (KDS 14 20 20 / KDS 14 20 60).

Provides:
- Cantilever Retaining Walls (T-type, L-type, Gravity, Basement Wall)
- Earth Pressure Theories: Rankine & Coulomb Active Pressure, Hydrostatic Water, Surcharge
- 3 External Stability Checks:
  1. Overturning Factor of Safety (Fs_ot >= 2.0 or 1.5)
  2. Sliding Factor of Safety (Fs_sl >= 1.5 with base friction & shear key passive thrust)
  3. Bearing Capacity & Contact Pressure (q_max <= qa, eccentricity e <= B/6)
- Internal Reinforced Concrete Design:
  - Stem Wall: Base bending moment Mu, shear Vu, main rebar As, vertical/horizontal temp steel
  - Toe Slab: Upward bearing cantilever bending & shear
  - Heel Slab: Downward soil/surcharge weight cantilever bending & shear
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import List, Tuple, Dict, Any, Optional

from src.engine.materials import ConcreteMaterial, RebarMaterial, get_phi_flexure, get_phi_shear


class RetainingWallType(str, Enum):
    CANTILEVER_T = "cantilever_t"       # Inverted T-shape (Toe + Stem + Heel)
    CANTILEVER_L = "cantilever_l"       # L-shape (Stem + Heel only or Toe only)
    GRAVITY = "gravity"                 # Plain / Mass concrete gravity wall
    BASEMENT_WALL = "basement_wall"     # Propped basement wall with floor slabs


@dataclass
class SoilProperties:
    """Soil and Ground Condition Properties."""
    unit_weight: float = 19.0           # kN/m3 (Soil moist unit weight gamma)
    sat_unit_weight: float = 20.0       # kN/m3 (Saturated unit weight)
    phi_deg: float = 30.0               # degrees (Internal friction angle)
    cohesion: float = 0.0               # kN/m2 (Soil cohesion c)
    base_friction_coef: float = 0.50    # mu = tan(delta_b) between base concrete and soil
    backfill_slope_deg: float = 0.0     # beta (Backfill inclination angle)
    water_table_depth: float = 5000.0   # mm from top of stem (default below base)
    surcharge_q: float = 10.0           # kN/m2 (Uniform surcharge load q)
    qa_allowable: float = 250.0         # kN/m2 (Allowable soil bearing capacity)


@dataclass
class RetainingWallGeometry:
    """Geometry Dimensions of Retaining Wall (mm)."""
    H_total: float = 4500.0             # Total height from bottom of base slab to top (mm)
    stem_t_top: float = 300.0           # Stem thickness at top (mm)
    stem_t_bot: float = 450.0           # Stem thickness at bottom (mm)
    base_width_B: float = 3000.0        # Total width of base footing (mm)
    base_t: float = 500.0               # Thickness of base slab (mm)
    toe_length: float = 900.0           # Length of Toe (front projection) (mm)
    heel_length: float = 1650.0         # Length of Heel (rear projection) (mm)
    front_embedment_Df: float = 800.0   # Front soil embedment depth above base (mm)
    shear_key_depth: float = 0.0        # Depth of shear key below base slab (mm)
    shear_key_width: float = 300.0      # Width of shear key (mm)


@dataclass
class RetainingWallInput:
    """Input parameters for Retaining Wall Check and Design."""
    name: str = "RW1"
    wall_type: RetainingWallType = RetainingWallType.CANTILEVER_T
    geometry: RetainingWallGeometry = field(default_factory=RetainingWallGeometry)
    soil: SoilProperties = field(default_factory=SoilProperties)
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=24.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    cover: float = 50.0                 # mm clear cover
    
    # Stem Reinforcement
    stem_main_bar_diam: float = 19.0    # mm
    stem_main_bar_spacing: float = 150.0# mm
    stem_dist_bar_diam: float = 13.0    # mm (Horizontal distribution rebar)
    stem_dist_bar_spacing: float = 200.0# mm
    
    # Toe Reinforcement
    toe_main_bar_diam: float = 16.0     # mm (Bottom rebar)
    toe_main_bar_spacing: float = 150.0 # mm
    
    # Heel Reinforcement
    heel_main_bar_diam: float = 19.0    # mm (Top rebar)
    heel_main_bar_spacing: float = 150.0# mm


@dataclass
class EarthPressureResult:
    """Calculated Lateral Earth Pressures."""
    Ka: float                           # Active earth pressure coefficient
    K0: float                           # At-rest earth pressure coefficient
    Pa_soil: float                      # kN/m (Resultant active thrust from soil)
    Pa_soil_arm: float                  # m (Moment arm from base bottom)
    Pa_surch: float                     # kN/m (Resultant thrust from surcharge)
    Pa_surch_arm: float                 # m
    Pw_water: float                     # kN/m (Hydrostatic water thrust)
    Pw_water_arm: float                 # m
    total_H: float                      # kN/m (Total lateral overturning force)
    total_overturning_moment_Mo: float  # kN*m/m (Total overturning moment about toe base)


@dataclass
class WallStabilityResult:
    """External Stability Assessment."""
    total_vertical_V: float             # kN/m (Total resisting vertical weight)
    total_resisting_moment_Mr: float    # kN*m/m (Total resisting moment about toe)
    overturning_moment_Mo: float        # kN*m/m
    
    # Overturning Check
    Fs_ot: float                        # Factor of safety against overturning
    is_overturning_ok: bool             # Fs_ot >= 2.0 (or 1.5)
    
    # Sliding Check
    resisting_force_Fr: float           # kN/m (Base friction + Cohesion + Key passive)
    driving_force_Fd: float             # kN/m (Total lateral force)
    Fs_sl: float                        # Factor of safety against sliding
    is_sliding_ok: bool                 # Fs_sl >= 1.5
    
    # Bearing Check
    eccentricity_e: float               # m (Distance from center of base)
    is_kern_ok: bool                    # e <= B / 6
    q_max: float                        # kN/m2 (Max contact pressure at toe)
    q_min: float                        # kN/m2 (Min contact pressure at heel)
    qa_allowable: float                 # kN/m2
    is_bearing_ok: bool                 # q_max <= qa


@dataclass
class SectionFlexureShear:
    """Internal Section Check Result."""
    Mu: float                           # kN*m/m (Factored moment)
    Vu: float                           # kN/m (Factored shear)
    d: float                            # mm
    As_req: float                       # mm2/m
    As_prov: float                      # mm2/m
    phi_Mn: float                       # kN*m/m
    phi_Vc: float                       # kN/m
    dcr_flexure: float
    dcr_shear: float
    is_flexure_ok: bool
    is_shear_ok: bool


@dataclass
class RetainingWallResult:
    """Comprehensive Retaining Wall Engineering Result."""
    name: str
    wall_type: RetainingWallType
    earth_pressure: EarthPressureResult
    stability: WallStabilityResult
    stem: SectionFlexureShear
    toe: SectionFlexureShear
    heel: SectionFlexureShear
    max_dcr: float
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class RCRetainingWall:
    """RC Retaining Wall Solver (KDS 14 20 60 / KDS 14 20 20)."""

    def __init__(self, wall_input: RetainingWallInput):
        self.inp = wall_input

    def calc_earth_pressure(self) -> EarthPressureResult:
        """Calculate Rankine active earth pressure and overturning moment."""
        geo = self.inp.geometry
        soil = self.inp.soil
        
        H_total_m = geo.H_total / 1000.0
        phi_rad = math.radians(soil.phi_deg)
        
        # Rankine Ka = tan^2(45 - phi/2)
        Ka = (math.tan(math.radians(45.0) - phi_rad / 2.0)) ** 2
        K0 = 1.0 - math.sin(phi_rad)
        
        # Active soil thrust Pa_soil = 0.5 * Ka * gamma * H^2
        # (Considering water table if above base)
        wt_depth_m = soil.water_table_depth / 1000.0
        
        if wt_depth_m >= H_total_m:
            # Fully dry / moist soil above water table
            Pa_soil = 0.5 * Ka * soil.unit_weight * (H_total_m ** 2)
            Pa_soil_arm = H_total_m / 3.0
            Pw_water = 0.0
            Pw_water_arm = 0.0
        else:
            # Submerged lower layer
            h1 = wt_depth_m
            h2 = H_total_m - wt_depth_m
            gamma_sub = max(0.0, soil.sat_unit_weight - 9.81)
            # Top layer thrust
            P1 = 0.5 * Ka * soil.unit_weight * (h1 ** 2)
            # Uniform surcharge from top layer on bottom layer
            q1 = soil.unit_weight * h1
            P2 = Ka * q1 * h2
            # Bottom layer soil thrust
            P3 = 0.5 * Ka * gamma_sub * (h2 ** 2)
            Pa_soil = P1 + P2 + P3
            # Combined arm
            Mo_soil = P1 * (h2 + h1 / 3.0) + P2 * (h2 / 2.0) + P3 * (h2 / 3.0)
            Pa_soil_arm = Mo_soil / Pa_soil if Pa_soil > 0 else H_total_m / 3.0
            # Water thrust
            Pw_water = 0.5 * 9.81 * (h2 ** 2)
            Pw_water_arm = h2 / 3.0
            
        # Surcharge thrust Pa_surch = Ka * q * H
        Pa_surch = Ka * soil.surcharge_q * H_total_m
        Pa_surch_arm = H_total_m / 2.0
        
        total_H = Pa_soil + Pa_surch + Pw_water
        Mo_total = (Pa_soil * Pa_soil_arm) + (Pa_surch * Pa_surch_arm) + (Pw_water * Pw_water_arm)
        
        return EarthPressureResult(
            Ka=Ka,
            K0=K0,
            Pa_soil=Pa_soil,
            Pa_soil_arm=Pa_soil_arm,
            Pa_surch=Pa_surch,
            Pa_surch_arm=Pa_surch_arm,
            Pw_water=Pw_water,
            Pw_water_arm=Pw_water_arm,
            total_H=total_H,
            total_overturning_moment_Mo=Mo_total
        )

    def check_stability(self) -> WallStabilityResult:
        """Check overturning, sliding, and bearing pressure stability."""
        geo = self.inp.geometry
        soil = self.inp.soil
        conc_gamma = self.inp.concrete.unit_weight
        
        ep = self.calc_earth_pressure()
        
        # Dimensions in meters
        H_m = geo.H_total / 1000.0
        tb_m = geo.base_t / 1000.0
        H_stem_m = H_m - tb_m
        B_m = geo.base_width_B / 1000.0
        t_top_m = geo.stem_t_top / 1000.0
        t_bot_m = geo.stem_t_bot / 1000.0
        toe_m = geo.toe_length / 1000.0
        heel_m = geo.heel_length / 1000.0
        
        # -------------------------------------------------------------
        # Vertical Weights and Resisting Moments about Toe (Point O)
        # -------------------------------------------------------------
        # 1. Base Slab Weight
        W_base = B_m * tb_m * conc_gamma
        x_base = B_m / 2.0
        
        # 2. Stem Rectangular part (t_top)
        W_stem_rect = t_top_m * H_stem_m * conc_gamma
        x_stem_rect = toe_m + (t_bot_m - t_top_m) + (t_top_m / 2.0)
        
        # 3. Stem Triangular taper part
        t_taper_m = t_bot_m - t_top_m
        if t_taper_m > 0:
            W_stem_tri = 0.5 * t_taper_m * H_stem_m * conc_gamma
            x_stem_tri = toe_m + (2.0 / 3.0) * t_taper_m
        else:
            W_stem_tri = 0.0
            x_stem_tri = 0.0
            
        # 4. Soil above Heel
        W_soil_heel = heel_m * H_stem_m * soil.unit_weight
        x_soil_heel = B_m - (heel_m / 2.0)
        
        # 5. Surcharge above Heel
        W_surch_heel = heel_m * soil.surcharge_q
        x_surch_heel = B_m - (heel_m / 2.0)
        
        # 6. Soil above Toe (Embedment)
        Df_m = geo.front_embedment_Df / 1000.0
        W_soil_toe = toe_m * max(0.0, Df_m - tb_m) * soil.unit_weight
        x_soil_toe = toe_m / 2.0
        
        total_V = W_base + W_stem_rect + W_stem_tri + W_soil_heel + W_surch_heel + W_soil_toe
        Mr_total = (
            W_base * x_base +
            W_stem_rect * x_stem_rect +
            W_stem_tri * x_stem_tri +
            W_soil_heel * x_soil_heel +
            W_surch_heel * x_surch_heel +
            W_soil_toe * x_soil_toe
        )
        
        Mo_total = ep.total_overturning_moment_Mo
        
        # 1. Overturning Safety Factor (Fs >= 2.0)
        Fs_ot = Mr_total / Mo_total if Mo_total > 0 else 999.0
        is_ot_ok = Fs_ot >= 2.0
        
        # 2. Sliding Safety Factor (Fs >= 1.5)
        # Resisting force Fr = V * mu + Cohesion*B + Passive thrust
        # Passive thrust on shear key or embedment
        Kp = (math.tan(math.radians(45.0) + math.radians(soil.phi_deg) / 2.0)) ** 2
        Pp = 0.5 * Kp * soil.unit_weight * (Df_m ** 2) if Df_m > 0 else 0.0
        
        Fr = (total_V * soil.base_friction_coef) + (soil.cohesion * B_m) + (0.5 * Pp)
        Fd = ep.total_H
        Fs_sl = Fr / Fd if Fd > 0 else 999.0
        is_sl_ok = Fs_sl >= 1.5
        
        # 3. Bearing & Contact Pressure
        # Location of resultant from toe: x_bar = (Mr - Mo) / V
        x_bar = (Mr_total - Mo_total) / total_V if total_V > 0 else B_m / 2.0
        e = abs((B_m / 2.0) - x_bar)  # Eccentricity
        
        is_kern_ok = e <= (B_m / 6.0)
        
        if is_kern_ok:
            q_avg = total_V / B_m
            q_max = q_avg * (1.0 + 6.0 * e / B_m)
            q_min = max(0.0, q_avg * (1.0 - 6.0 * e / B_m))
        else:
            # Tension separation (Resultant closer to toe)
            q_max = (2.0 * total_V) / (3.0 * max(0.05, x_bar))
            q_min = 0.0
            
        qa = soil.qa_allowable
        is_bearing_ok = (q_max <= qa) and (e <= B_m / 6.0)
        
        return WallStabilityResult(
            total_vertical_V=total_V,
            total_resisting_moment_Mr=Mr_total,
            overturning_moment_Mo=Mo_total,
            Fs_ot=Fs_ot,
            is_overturning_ok=is_ot_ok,
            resisting_force_Fr=Fr,
            driving_force_Fd=Fd,
            Fs_sl=Fs_sl,
            is_sliding_ok=is_sl_ok,
            eccentricity_e=e,
            is_kern_ok=is_kern_ok,
            q_max=q_max,
            q_min=q_min,
            qa_allowable=qa,
            is_bearing_ok=is_bearing_ok
        )

    def design_sections(self, stab: WallStabilityResult, ep: EarthPressureResult) -> Tuple[SectionFlexureShear, SectionFlexureShear, SectionFlexureShear]:
        """Design Stem base, Toe slab, and Heel slab sections."""
        geo = self.inp.geometry
        soil = self.inp.soil
        fck = self.inp.concrete.fck
        fy = self.inp.rebar.fy
        alpha1 = self.inp.concrete.alpha1
        cover = self.inp.cover
        phi_f = get_phi_flexure(et=0.005)
        phi_v = get_phi_shear()
        
        H_stem_m = (geo.H_total - geo.base_t) / 1000.0
        
        # -------------------------------------------------------------
        # 1. Stem Base Section (Cantilever fixed at top of base slab)
        # Load factors: 1.6 for earth/surcharge/water
        # -------------------------------------------------------------
        Pa_stem_soil = 0.5 * ep.Ka * soil.unit_weight * (H_stem_m ** 2)
        Pa_stem_surch = ep.Ka * soil.surcharge_q * H_stem_m
        
        Vu_stem = 1.6 * (Pa_stem_soil + Pa_stem_surch)  # kN/m
        Mu_stem = 1.6 * ((Pa_stem_soil * H_stem_m / 3.0) + (Pa_stem_surch * H_stem_m / 2.0))  # kN*m/m
        
        d_stem = geo.stem_t_bot - cover - (self.inp.stem_main_bar_diam / 2.0)
        area_main_stem = math.pi * (self.inp.stem_main_bar_diam ** 2) / 4.0
        As_prov_stem = (1000.0 / self.inp.stem_main_bar_spacing) * area_main_stem  # mm2/m
        
        As_req_stem = self._calc_required_as(Mu_stem, d_stem, 1000.0, fck, fy, alpha1, phi_f)
        
        a_stem = (As_prov_stem * fy) / (alpha1 * fck * 1000.0)
        Mn_stem = As_prov_stem * fy * (d_stem - a_stem / 2.0) / 1e6
        phi_Mn_stem = phi_f * Mn_stem
        
        Vc_stem = (1.0 / 6.0) * math.sqrt(fck) * 1000.0 * d_stem / 1000.0
        phi_Vc_stem = phi_v * Vc_stem
        
        stem_res = SectionFlexureShear(
            Mu=Mu_stem,
            Vu=Vu_stem,
            d=d_stem,
            As_req=As_req_stem,
            As_prov=As_prov_stem,
            phi_Mn=phi_Mn_stem,
            phi_Vc=phi_Vc_stem,
            dcr_flexure=Mu_stem / phi_Mn_stem if phi_Mn_stem > 0 else 0.0,
            dcr_shear=Vu_stem / phi_Vc_stem if phi_Vc_stem > 0 else 0.0,
            is_flexure_ok=(Mu_stem <= phi_Mn_stem),
            is_shear_ok=(Vu_stem <= phi_Vc_stem)
        )
        
        # -------------------------------------------------------------
        # 2. Toe Slab Section (Cantilever fixed at front of stem)
        # Upward ground contact pressure minus downward toe concrete weight
        # -------------------------------------------------------------
        toe_m = geo.toe_length / 1000.0
        tb_m = geo.base_t / 1000.0
        B_m = geo.base_width_B / 1000.0
        
        # Pressure at toe tip: stab.q_max, pressure at stem front
        slope_q = (stab.q_max - stab.q_min) / B_m if B_m > 0 else 0.0
        q_stem_front = max(0.0, stab.q_max - slope_q * toe_m)
        q_toe_avg = (stab.q_max + q_stem_front) / 2.0
        
        # Net upward factored pressure (1.6 * q_soil - 1.2 * conc_self)
        qu_toe_net = max(10.0, 1.6 * q_toe_avg - 1.2 * tb_m * self.inp.concrete.unit_weight)
        
        Vu_toe = qu_toe_net * toe_m  # kN/m
        Mu_toe = qu_toe_net * (toe_m ** 2) / 2.0  # kN*m/m
        
        d_toe = geo.base_t - cover - (self.inp.toe_main_bar_diam / 2.0)
        area_main_toe = math.pi * (self.inp.toe_main_bar_diam ** 2) / 4.0
        As_prov_toe = (1000.0 / self.inp.toe_main_bar_spacing) * area_main_toe
        
        As_req_toe = self._calc_required_as(Mu_toe, d_toe, 1000.0, fck, fy, alpha1, phi_f)
        a_toe = (As_prov_toe * fy) / (alpha1 * fck * 1000.0)
        Mn_toe = As_prov_toe * fy * (d_toe - a_toe / 2.0) / 1e6
        phi_Mn_toe = phi_f * Mn_toe
        
        Vc_toe = (1.0 / 6.0) * math.sqrt(fck) * 1000.0 * d_toe / 1000.0
        phi_Vc_toe = phi_v * Vc_toe
        
        toe_res = SectionFlexureShear(
            Mu=Mu_toe,
            Vu=Vu_toe,
            d=d_toe,
            As_req=As_req_toe,
            As_prov=As_prov_toe,
            phi_Mn=phi_Mn_toe,
            phi_Vc=phi_Vc_toe,
            dcr_flexure=Mu_toe / phi_Mn_toe if phi_Mn_toe > 0 else 0.0,
            dcr_shear=Vu_toe / phi_Vc_toe if phi_Vc_toe > 0 else 0.0,
            is_flexure_ok=(Mu_toe <= phi_Mn_toe),
            is_shear_ok=(Vu_toe <= phi_Vc_toe)
        )
        
        # -------------------------------------------------------------
        # 3. Heel Slab Section (Cantilever fixed at back of stem)
        # Downward weight (soil + surcharge + slab) minus upward soil reaction
        # -------------------------------------------------------------
        heel_m = geo.heel_length / 1000.0
        q_heel_tip = stab.q_min
        q_stem_back = max(0.0, stab.q_min + slope_q * heel_m)
        q_heel_avg = (q_heel_tip + q_stem_back) / 2.0
        
        w_down_factored = 1.2 * (H_stem_m * soil.unit_weight + tb_m * self.inp.concrete.unit_weight) + 1.6 * soil.surcharge_q
        qu_heel_net = max(10.0, w_down_factored - 0.9 * q_heel_avg)
        
        Vu_heel = qu_heel_net * heel_m  # kN/m
        Mu_heel = qu_heel_net * (heel_m ** 2) / 2.0  # kN*m/m
        
        d_heel = geo.base_t - cover - (self.inp.heel_main_bar_diam / 2.0)
        area_main_heel = math.pi * (self.inp.heel_main_bar_diam ** 2) / 4.0
        As_prov_heel = (1000.0 / self.inp.heel_main_bar_spacing) * area_main_heel
        
        As_req_heel = self._calc_required_as(Mu_heel, d_heel, 1000.0, fck, fy, alpha1, phi_f)
        a_heel = (As_prov_heel * fy) / (alpha1 * fck * 1000.0)
        Mn_heel = As_prov_heel * fy * (d_heel - a_heel / 2.0) / 1e6
        phi_Mn_heel = phi_f * Mn_heel
        
        Vc_heel = (1.0 / 6.0) * math.sqrt(fck) * 1000.0 * d_heel / 1000.0
        phi_Vc_heel = phi_v * Vc_heel
        
        heel_res = SectionFlexureShear(
            Mu=Mu_heel,
            Vu=Vu_heel,
            d=d_heel,
            As_req=As_req_heel,
            As_prov=As_prov_heel,
            phi_Mn=phi_Mn_heel,
            phi_Vc=phi_Vc_heel,
            dcr_flexure=Mu_heel / phi_Mn_heel if phi_Mn_heel > 0 else 0.0,
            dcr_shear=Vu_heel / phi_Vc_heel if phi_Vc_heel > 0 else 0.0,
            is_flexure_ok=(Mu_heel <= phi_Mn_heel),
            is_shear_ok=(Vu_heel <= phi_Vc_heel)
        )
        
        return stem_res, toe_res, heel_res

    def _calc_required_as(self, Mu: float, d: float, b: float, fck: float, fy: float, alpha1: float, phi: float) -> float:
        """Calculate required tension reinforcement area."""
        if Mu <= 0.0:
            return 0.0020 * b * d
        Mu_nmm = (Mu / phi) * 1e6
        Rn = Mu_nmm / (b * (d ** 2))
        m = fy / (alpha1 * fck)
        discriminant = 1.0 - (2.0 * m * Rn / fy)
        if discriminant < 0:
            rho = 0.025
        else:
            rho = (1.0 / m) * (1.0 - math.sqrt(discriminant))
        rho = max(rho, 0.0020)  # KDS min rebar ratio for walls/slabs
        return rho * b * d

    def solve(self) -> RetainingWallResult:
        """Perform comprehensive retaining wall check."""
        ep = self.calc_earth_pressure()
        stab = self.check_stability()
        stem_res, toe_res, heel_res = self.design_sections(stab, ep)
        
        dcr_list = [
            1.0 / (stab.Fs_ot / 2.0) if stab.Fs_ot > 0 else 9.9,
            1.0 / (stab.Fs_sl / 1.5) if stab.Fs_sl > 0 else 9.9,
            stab.q_max / stab.qa_allowable if stab.qa_allowable > 0 else 0.0,
            stem_res.dcr_flexure, stem_res.dcr_shear,
            toe_res.dcr_flexure, toe_res.dcr_shear,
            heel_res.dcr_flexure, heel_res.dcr_shear,
        ]
        max_dcr = max(dcr_list)
        
        is_safe = (
            stab.is_overturning_ok and
            stab.is_sliding_ok and
            stab.is_bearing_ok and
            stem_res.is_flexure_ok and stem_res.is_shear_ok and
            toe_res.is_flexure_ok and toe_res.is_shear_ok and
            heel_res.is_flexure_ok and heel_res.is_shear_ok
        )
        
        msgs = []
        if not stab.is_overturning_ok:
            msgs.append(f"Overturning safety factor Fs={stab.Fs_ot:.2f} < 2.0")
        if not stab.is_sliding_ok:
            msgs.append(f"Sliding safety factor Fs={stab.Fs_sl:.2f} < 1.5")
        if not stab.is_bearing_ok:
            msgs.append(f"Bearing capacity exceeded: q_max={stab.q_max:.1f} kPa > qa={stab.qa_allowable:.1f} kPa")
        if not stem_res.is_flexure_ok or not stem_res.is_shear_ok:
            msgs.append("Stem wall capacity exceeded")
        if not toe_res.is_flexure_ok or not toe_res.is_shear_ok:
            msgs.append("Toe slab capacity exceeded")
        if not heel_res.is_flexure_ok or not heel_res.is_shear_ok:
            msgs.append("Heel slab capacity exceeded")
            
        return RetainingWallResult(
            name=self.inp.name,
            wall_type=self.inp.wall_type,
            earth_pressure=ep,
            stability=stab,
            stem=stem_res,
            toe=toe_res,
            heel=heel_res,
            max_dcr=max_dcr,
            is_safe=is_safe,
            messages=msgs
        )
