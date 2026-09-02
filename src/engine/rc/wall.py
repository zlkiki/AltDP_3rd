"""RC Shear Wall Design Engine (KDS 14 20 22 / KDS 14 20 70 / KDS 14 20 20).

Provides:
- In-plane shear capacity (Vc, Vs, Vn, phi*Vn, upper limit 0.83*sqrt(fck)*Acv)
- Minimum vertical and horizontal reinforcement checks & double-curtain rules
- Special Boundary Element (SBE) checks (Displacement-based & Stress-based)
- Boundary element sizing and transverse confining steel requirements
- Section summary and 2D visualization data generation
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Dict, Any, Optional

from src.engine.materials import ConcreteMaterial, RebarMaterial, get_phi_shear, get_phi_flexure
from src.engine.solver.fiber_section import FiberSection


@dataclass
class BoundaryElementConfig:
    """Boundary Element (단부 경계요소) geometry and rebar."""
    length: float = 400.0          # mm (단부 경계요소 길이 along lw)
    width: float = 300.0           # mm (단부 폭, 보통 tw와 동일하거나 확대)
    bar_diam: float = 22.0         # mm (주근 직경)
    total_bars: int = 8            # 단부 주근 개수 (e.g. 8-D22)
    tie_diam: float = 10.0         # mm (횡보강 띠철근 직경)
    tie_spacing: float = 100.0     # mm (횡보강 띠철근 간격)
    tie_legs_x: int = 2            # X방향 횡보강 가닥수
    tie_legs_y: int = 2            # Y방향 횡보강 가닥수


@dataclass
class RCWallInput:
    """RC Shear Wall input geometry, materials, rebar, and design forces."""
    name: str = "W1"
    lw: float = 4000.0             # mm (Wall length / horizontal dimension)
    tw: float = 300.0              # mm (Wall thickness)
    hw: float = 3000.0             # mm (Clear height of wall / story height)
    cover: float = 40.0            # mm (Clear cover to rebar)
    
    # Web reinforcement (복부 배근)
    vert_bar_diam: float = 13.0    # mm (복부 수직철근 직경 e.g. D13)
    vert_spacing: float = 200.0    # mm (복부 수직철근 간격)
    vert_layers: int = 2           # 복부 수직철근 레이어 수 (1=단배근, 2=복배근)
    
    horiz_bar_diam: float = 13.0   # mm (복부 수평전단철근 직경 e.g. D13)
    horiz_spacing: float = 200.0   # mm (복부 수평철근 간격)
    horiz_layers: int = 2          # 복부 수평철근 레이어 수 (1=단배근, 2=복배근)
    
    # Boundary elements (단부 배근)
    left_boundary: Optional[BoundaryElementConfig] = None
    right_boundary: Optional[BoundaryElementConfig] = None
    
    # Materials
    concrete: ConcreteMaterial = field(default_factory=lambda: ConcreteMaterial(fck=27.0))
    rebar: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    rebar_shear: RebarMaterial = field(default_factory=lambda: RebarMaterial(fy=400.0))
    
    # Design Actions (Factored forces)
    Pu: float = 1500.0             # kN (Factored axial load, positive = compression)
    Vu: float = 650.0              # kN (Factored in-plane shear force)
    Mu: float = 1800.0             # kN*m (Factored in-plane bending moment)
    
    # Seismic & Displacement parameters (KDS 14 20 70)
    delta_u: float = 30.0          # mm (Design inelastic top displacement / target drift)
    is_seismic: bool = True        # Special / Intermediate seismic detailing


@dataclass
class WallShearResult:
    """Shear capacity check results for RC Shear Wall."""
    Vu: float                      # kN
    phi_Vn: float                  # kN
    Vc: float                      # kN
    Vs: float                      # kN
    Vn: float                      # kN
    Vn_max: float                  # kN (0.83 * sqrt(fck) * hd)
    dcr: float                     # Vu / (phi * Vn)
    alpha_c: float                 # Aspect ratio coefficient (0.17 ~ 0.25)
    aspect_ratio: float            # hw / lw
    d: float                       # mm (Effective depth)
    is_ok: bool                    # dcr <= 1.0


@dataclass
class WallRebarRatioResult:
    """Reinforcement ratio checks (minimum & maximum) for RC Shear Wall."""
    rho_l: float                   # Actual longitudinal (vertical) ratio
    rho_l_min: float               # Minimum required vertical ratio
    rho_t: float                   # Actual transverse (horizontal) ratio
    rho_t_min: float               # Minimum required horizontal ratio
    max_spacing_limit: float       # mm (min(3*tw, 450 mm))
    is_double_curtain_required: bool
    is_double_curtain_provided: bool
    is_vert_ok: bool
    is_horiz_ok: bool
    is_spacing_ok: bool


@dataclass
class BoundaryElementCheckResult:
    """Special Boundary Element (SBE) evaluation result (KDS 14 20 70 4.3)."""
    is_sbe_required: bool
    trigger_method: str            # "Displacement-based", "Stress-based", "None", or "Both"
    c: float                       # mm (Neutral axis depth)
    c_limit_disp: float            # mm (lw / (600 * (delta_u / hw)))
    sigma_max: float               # MPa (Max compression stress: Pu/Ag + Mu/Z)
    sigma_limit: float             # MPa (0.2 * fck)
    required_be_length: float      # mm (max(c - 0.1*lw, c/2))
    provided_be_length: float      # mm
    required_Ash: float            # mm2 (Required transverse confining steel)
    provided_Ash: float            # mm2
    is_length_ok: bool
    is_ash_ok: bool
    is_ok: bool


@dataclass
class RCWallDesignResult:
    """Comprehensive design summary for RC Shear Wall."""
    wall_name: str
    shear: WallShearResult
    rebar_ratio: WallRebarRatioResult
    boundary_element: BoundaryElementCheckResult
    is_safe: bool
    dcr_governing: float
    governing_mode: str
    messages: List[str] = field(default_factory=list)


class RCShearWall:
    """RC Shear Wall engineering design solver conforming to KDS 14 20 22 / 70."""

    def __init__(self, wall_input: RCWallInput):
        self.input = wall_input
        self._validate_input()

    def _validate_input(self) -> None:
        if self.input.lw <= 0 or self.input.tw <= 0 or self.input.hw <= 0:
            raise ValueError("Wall dimensions (lw, tw, hw) must be strictly positive.")
        if self.input.vert_spacing <= 0 or self.input.horiz_spacing <= 0:
            raise ValueError("Rebar spacing must be strictly positive.")

    @property
    def Ag(self) -> float:
        """Gross section area of wall (mm2)."""
        return self.input.lw * self.input.tw

    @property
    def Z(self) -> float:
        """Section modulus for in-plane bending (mm3): Z = tw * lw^2 / 6."""
        return (self.input.tw * (self.input.lw ** 2)) / 6.0

    @property
    def aspect_ratio(self) -> float:
        """Wall aspect ratio hw / lw."""
        return self.input.hw / self.input.lw

    def calc_shear_capacity(self) -> WallShearResult:
        """Calculate in-plane shear capacity Vc, Vs, Vn, phi*Vn (KDS 14 20 22 4.3)."""
        lw = self.input.lw
        tw = self.input.tw
        hw = self.input.hw
        fck = self.input.concrete.fck
        lambda_factor = self.input.concrete.lambda_factor
        fy_s = self.input.rebar_shear.fy
        Pu = self.input.Pu * 1e3  # N (Axial load, positive = compression)
        Vu = abs(self.input.Vu)   # kN
        
        # Effective depth d = 0.8 * lw
        d = 0.8 * lw
        
        # Aspect ratio coefficient alpha_c
        ar = hw / lw
        if ar <= 1.5:
            alpha_c = 0.25
        elif ar >= 2.0:
            alpha_c = 0.17
        else:
            alpha_c = 0.25 - ((0.25 - 0.17) / (2.0 - 1.5)) * (ar - 1.5)
            
        # Concrete shear capacity Vc (N)
        # Vc = (alpha_c * lambda * sqrt(fck) + Nu / (4 * lw * tw)) * tw * d
        axial_term = max(0.0, Pu / (4.0 * lw * tw)) if Pu > 0 else (Pu / (4.0 * lw * tw))
        vc_stress = alpha_c * lambda_factor * math.sqrt(fck) + axial_term
        Vc_N = max(0.0, vc_stress * tw * d)
        Vc_kN = Vc_N / 1e3
        
        # Horizontal rebar shear capacity Vs (N)
        # Av = layers * pi * d_b^2 / 4
        bar_area_h = math.pi * (self.input.horiz_bar_diam ** 2) / 4.0
        Av = self.input.horiz_layers * bar_area_h
        s2 = self.input.horiz_spacing
        Vs_N = (Av * fy_s * d) / s2
        Vs_kN = Vs_N / 1e3
        
        # Upper limit: Vn_max = 0.83 * sqrt(fck) * tw * d
        Vn_max_N = 0.83 * math.sqrt(fck) * tw * d
        Vn_max_kN = Vn_max_N / 1e3
        
        Vn_kN = min(Vc_kN + Vs_kN, Vn_max_kN)
        
        phi_v = get_phi_shear() # 0.75
        phi_Vn = phi_v * Vn_kN
        dcr = Vu / phi_Vn if phi_Vn > 0 else 999.0
        is_ok = dcr <= 1.0
        
        return WallShearResult(
            Vu=Vu,
            phi_Vn=round(phi_Vn, 2),
            Vc=round(Vc_kN, 2),
            Vs=round(Vs_kN, 2),
            Vn=round(Vn_kN, 2),
            Vn_max=round(Vn_max_kN, 2),
            dcr=round(dcr, 3),
            alpha_c=round(alpha_c, 4),
            aspect_ratio=round(ar, 3),
            d=round(d, 1),
            is_ok=is_ok
        )

    def check_reinforcement_ratios(self) -> WallRebarRatioResult:
        """Check minimum/maximum rebar ratios and double-curtain requirements."""
        tw = self.input.tw
        lw = self.input.lw
        fck = self.input.concrete.fck
        lambda_factor = self.input.concrete.lambda_factor
        Vu_N = abs(self.input.Vu) * 1e3 # N
        
        # Vertical rebar ratio
        bar_area_v = math.pi * (self.input.vert_bar_diam ** 2) / 4.0
        # Total web vertical area per mm of wall length = layers * bar_area_v / spacing
        rho_l = (self.input.vert_layers * bar_area_v) / (self.input.vert_spacing * tw)
        
        # Horizontal rebar ratio
        bar_area_h = math.pi * (self.input.horiz_bar_diam ** 2) / 4.0
        rho_t = (self.input.horiz_layers * bar_area_h) / (self.input.horiz_spacing * tw)
        
        # Threshold: Vu <= 0.5 * phi * Vc (approx 0.5 * 0.75 * 0.17 * sqrt(fck) * tw * d)
        shear_res = self.calc_shear_capacity()
        phi_Vc = 0.75 * shear_res.Vc
        
        if self.input.Vu <= 0.5 * phi_Vc:
            rho_l_min = 0.0012
            rho_t_min = 0.0020
        else:
            rho_l_min = 0.0025
            rho_t_min = 0.0025
            
        # Double curtain requirement (KDS 14 20 22 / 70)
        # Required if tw >= 250 mm or Vu > 0.17 * lambda * sqrt(fck) * Acv
        Acv = tw * lw
        double_curtain_shear_threshold_N = 0.17 * lambda_factor * math.sqrt(fck) * Acv
        req_double = (tw >= 250.0) or (Vu_N > double_curtain_shear_threshold_N)
        prov_double = (self.input.vert_layers >= 2) and (self.input.horiz_layers >= 2)
        
        max_spacing = min(3.0 * tw, 450.0)
        spacing_ok = (self.input.vert_spacing <= max_spacing) and (self.input.horiz_spacing <= max_spacing)
        
        return WallRebarRatioResult(
            rho_l=round(rho_l, 5),
            rho_l_min=rho_l_min,
            rho_t=round(rho_t, 5),
            rho_t_min=rho_t_min,
            max_spacing_limit=max_spacing,
            is_double_curtain_required=req_double,
            is_double_curtain_provided=prov_double,
            is_vert_ok=(rho_l >= rho_l_min),
            is_horiz_ok=(rho_t >= rho_t_min),
            is_spacing_ok=spacing_ok
        )

    def estimate_neutral_axis_depth(self) -> float:
        """Estimate neutral axis depth c (mm) under Pu and Mu."""
        # Simplified plastic/elastic section estimation
        # c = (Pu/Ag + Mu/Z) / (2 * (Mu/Z)) * lw approximately or fiber solver
        Pu_N = self.input.Pu * 1e3
        Mu_Nmm = abs(self.input.Mu) * 1e6
        lw = self.input.lw
        tw = self.input.tw
        fck = self.input.concrete.fck
        
        # Approximate equilibrium under factored axial and flexural load:
        # P_comp = alpha1 * fck * tw * beta1 * c
        # For pure axial + high moment:
        c_approx = (Pu_N + (Mu_Nmm / (0.8 * lw))) / (0.85 * fck * tw)
        # Limit c between 0.05 * lw and lw
        c_val = max(0.05 * lw, min(lw * 0.95, c_approx))
        return c_val

    def check_boundary_elements(self) -> BoundaryElementCheckResult:
        """Evaluate Special Boundary Element (SBE) requirement (KDS 14 20 70 4.3)."""
        lw = self.input.lw
        tw = self.input.tw
        hw = self.input.hw
        fck = self.input.concrete.fck
        fy = self.input.rebar.fy
        Pu_N = self.input.Pu * 1e3
        Mu_Nmm = abs(self.input.Mu) * 1e6
        
        # 1. Displacement-based check (KDS 14 20 70 4.3.2)
        # Drift ratio delta_u / hw (minimum 0.005)
        drift_ratio = max(0.005, self.input.delta_u / hw)
        c_limit_disp = lw / (600.0 * drift_ratio)
        c_est = self.estimate_neutral_axis_depth()
        disp_trigger = (c_est >= c_limit_disp)
        
        # 2. Stress-based check (KDS 14 20 70 4.3.3)
        # sigma_max = Pu / Ag + Mu / Z
        sigma_max = (Pu_N / self.Ag) + (Mu_Nmm / self.Z)
        sigma_limit = 0.20 * fck
        stress_trigger = (sigma_max >= sigma_limit)
        
        if disp_trigger and stress_trigger:
            trigger_method = "Both"
        elif disp_trigger:
            trigger_method = "Displacement-based"
        elif stress_trigger:
            trigger_method = "Stress-based"
        else:
            trigger_method = "None"
            
        is_sbe_required = disp_trigger or stress_trigger
        
        # Required boundary element extension length be >= max(c - 0.1*lw, c/2)
        if is_sbe_required:
            req_be_length = max(c_est - 0.1 * lw, c_est / 2.0)
        else:
            req_be_length = 0.0
            
        # Provided boundary element
        prov_be_length = 0.0
        prov_Ash = 0.0
        req_Ash = 0.0
        
        if self.input.left_boundary:
            prov_be_length = max(prov_be_length, self.input.left_boundary.length)
            # Provided Ash = legs * bar_area
            tie_area = math.pi * (self.input.left_boundary.tie_diam ** 2) / 4.0
            prov_Ash = self.input.left_boundary.tie_legs_x * tie_area
            
            # Required Ash = 0.09 * s * bc * fck / fyh
            s = self.input.left_boundary.tie_spacing
            bc = self.input.left_boundary.width - 2 * self.input.cover
            req_Ash = max(
                0.3 * (s * bc * fck / fy) * ((self.input.left_boundary.length * self.input.left_boundary.width) / ((self.input.left_boundary.length - 2*self.input.cover) * bc) - 1.0),
                0.09 * (s * bc * fck / fy)
            )
        else:
            prov_be_length = 0.0
            prov_Ash = 0.0
            req_Ash = 0.0
            
        length_ok = (prov_be_length >= req_be_length) if is_sbe_required else True
        ash_ok = (prov_Ash >= req_Ash) if is_sbe_required else True
        is_ok = (not is_sbe_required) or (length_ok and ash_ok)
        
        return BoundaryElementCheckResult(
            is_sbe_required=is_sbe_required,
            trigger_method=trigger_method,
            c=round(c_est, 1),
            c_limit_disp=round(c_limit_disp, 1),
            sigma_max=round(sigma_max, 2),
            sigma_limit=round(sigma_limit, 2),
            required_be_length=round(req_be_length, 1),
            provided_be_length=round(prov_be_length, 1),
            required_Ash=round(req_Ash, 1),
            provided_Ash=round(prov_Ash, 1),
            is_length_ok=length_ok,
            is_ash_ok=ash_ok,
            is_ok=is_ok
        )

    def design_check(self) -> RCWallDesignResult:
        """Run all design checks and summarize safety."""
        shear_res = self.calc_shear_capacity()
        rebar_res = self.check_reinforcement_ratios()
        be_res = self.check_boundary_elements()
        
        messages = []
        if not shear_res.is_ok:
            messages.append(f"Shear failure: Vu ({shear_res.Vu:.1f} kN) > phi*Vn ({shear_res.phi_Vn:.1f} kN)")
        if not rebar_res.is_vert_ok:
            messages.append(f"Vertical rebar ratio rho_l ({rebar_res.rho_l:.4f}) < min ({rebar_res.rho_l_min:.4f})")
        if not rebar_res.is_horiz_ok:
            messages.append(f"Horizontal rebar ratio rho_t ({rebar_res.rho_t:.4f}) < min ({rebar_res.rho_t_min:.4f})")
        if rebar_res.is_double_curtain_required and not rebar_res.is_double_curtain_provided:
            messages.append("Double curtain rebar required but single curtain provided.")
        if be_res.is_sbe_required and not be_res.is_ok:
            messages.append(f"Special Boundary Element required ({be_res.trigger_method}) but detailing insufficient.")
            
        governing_dcr = shear_res.dcr
        governing_mode = "In-Plane Shear"
        
        is_safe = shear_res.is_ok and rebar_res.is_vert_ok and rebar_res.is_horiz_ok and rebar_res.is_spacing_ok and be_res.is_ok
        
        return RCWallDesignResult(
            wall_name=self.input.name,
            shear=shear_res,
            rebar_ratio=rebar_res,
            boundary_element=be_res,
            is_safe=is_safe,
            dcr_governing=governing_dcr,
            governing_mode=governing_mode,
            messages=messages
        )

    def get_section_geometry_dict(self) -> Dict[str, Any]:
        """Generate 2D geometric points and reinforcement coordinates for rendering."""
        lw = self.input.lw
        tw = self.input.tw
        
        # Wall contour polygon (X in [-lw/2, lw/2], Y in [-tw/2, tw/2])
        poly = [
            {"x": -lw / 2, "y": -tw / 2},
            {"x": lw / 2, "y": -tw / 2},
            {"x": lw / 2, "y": tw / 2},
            {"x": -lw / 2, "y": tw / 2},
        ]
        
        # Web vertical rebar dots
        rebars = []
        cover = self.input.cover
        y_top = tw / 2 - cover
        y_bot = -tw / 2 + cover
        
        # Spacing along X
        num_spaces = max(1, int(round((lw - 2 * cover) / self.input.vert_spacing)))
        actual_s = (lw - 2 * cover) / num_spaces
        
        for i in range(num_spaces + 1):
            x = -lw / 2 + cover + i * actual_s
            if self.input.vert_layers >= 2:
                rebars.append({"x": round(x, 1), "y": round(y_top, 1), "diam": self.input.vert_bar_diam, "type": "web_vert"})
                rebars.append({"x": round(x, 1), "y": round(y_bot, 1), "diam": self.input.vert_bar_diam, "type": "web_vert"})
            else:
                rebars.append({"x": round(x, 1), "y": 0.0, "diam": self.input.vert_bar_diam, "type": "web_vert"})
                
        # Boundary elements zones
        be_zones = []
        if self.input.left_boundary:
            be_zones.append({
                "type": "left_boundary",
                "x_min": -lw / 2,
                "x_max": -lw / 2 + self.input.left_boundary.length,
                "y_min": -tw / 2,
                "y_max": tw / 2
            })
        if self.input.right_boundary:
            be_zones.append({
                "type": "right_boundary",
                "x_min": lw / 2 - self.input.right_boundary.length,
                "x_max": lw / 2,
                "y_min": -tw / 2,
                "y_max": tw / 2
            })
            
        return {
            "name": self.input.name,
            "lw": lw,
            "tw": tw,
            "hw": self.input.hw,
            "polygon": poly,
            "rebars": rebars,
            "boundary_zones": be_zones
        }
