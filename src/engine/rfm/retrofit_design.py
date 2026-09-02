"""Structural Retrofit and Strengthening Design Engine (KDS 14 20 90 / ACI 440.2R).

Implements:
1. CFRP (Carbon Fiber Reinforced Polymer) Plate and Sheet Flexural Strengthening
2. CFRP Debonding Strain Limit (epsilon_fe <= 0.004)
3. Steel Plate Flexural and Shear Strengthening
4. CFRP U-Wrap and Full-Wrap Shear Strengthening (Vf)
5. Capacity Enhancement Ratio (Strengthening Ratio)
6. Unstrengthened Limit State Safety Check
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional, Dict, Any


class RetrofitType(str, Enum):
    FLEXURE = "FLEXURE"
    SHEAR = "SHEAR"
    COMBINED = "COMBINED"


class RetrofitMethod(str, Enum):
    CFRP_PLATE = "CFRP_PLATE"        # 탄소섬유판 부착
    CFRP_SHEET = "CFRP_SHEET"        # 탄소섬유시트 (U-wrap / Full-wrap)
    STEEL_PLATE = "STEEL_PLATE"      # 강판 보강


class ExposureCondition(str, Enum):
    INTERIOR = "INTERIOR"            # 실내 (CE = 0.95)
    EXTERIOR = "EXTERIOR"            # 실외 (CE = 0.85)
    AGGRESSIVE = "AGGRESSIVE"        # 부식/해양 (CE = 0.75)


@dataclass
class CFRPProp:
    """CFRP material properties."""
    tf: float = 1.2                  # Thickness per ply (mm)
    bf: float = 200.0                # Width of CFRP plate/strip (mm)
    num_plies: int = 1               # Number of plies
    ffu: float = 2800.0              # Ultimate tensile strength (MPa)
    Ef: float = 165000.0             # Elastic modulus (MPa)
    eps_fu: float = 0.017            # Ultimate strain
    exposure: ExposureCondition = ExposureCondition.INTERIOR
    is_full_wrap: bool = False       # For shear: True for Full-wrap, False for U-wrap
    sf: float = 200.0                # Center-to-center spacing of strips (mm) (continuous if equal to bf)


@dataclass
class SteelPlateProp:
    """Steel plate retrofit properties."""
    tsp: float = 4.5                 # Plate thickness (mm)
    bsp: float = 200.0               # Plate width (mm)
    fys: float = 275.0               # Yield strength (MPa)
    Es: float = 200000.0             # Elastic modulus (MPa)


@dataclass
class ExistingBeamProp:
    """Existing RC beam section properties."""
    b: float = 300.0                 # Web width (mm)
    h: float = 600.0                 # Total height (mm)
    d: float = 540.0                 # Effective depth to rebar (mm)
    fck: float = 24.0                # Concrete compressive strength (MPa)
    
    # Tension reinforcement
    As: float = 1520.0               # Area of existing rebar (mm2) (e.g. 3-D25)
    fy: float = 400.0                # Rebar yield strength (MPa)
    
    # Shear reinforcement
    Av: float = 142.6                # Area of stirrups (mm2) (e.g. 2-D10)
    fyt: float = 400.0               # Stirrup yield strength (MPa)
    s: float = 200.0                 # Stirrup spacing (mm)
    
    # Existing unstrengthened loads
    M_DL: float = 45.0               # Dead load moment during retrofit (kN·m)


@dataclass
class RetrofitDesignInput:
    """Input parameters for retrofit design check."""
    retrofit_type: RetrofitType = RetrofitType.FLEXURE
    method: RetrofitMethod = RetrofitMethod.CFRP_PLATE
    
    existing: ExistingBeamProp = field(default_factory=ExistingBeamProp)
    cfrp: Optional[CFRPProp] = field(default_factory=CFRPProp)
    steel_plate: Optional[SteelPlateProp] = field(default_factory=SteelPlateProp)
    
    # Target Factored Design Loads
    Mu: float = 350.0                # Required factored moment (kN·m)
    Vu: float = 180.0                # Required factored shear force (kN)


@dataclass
class RetrofitDesignResult:
    """Comprehensive check results for retrofitted member."""
    is_safe: bool
    dcr_flexure: float
    dcr_shear: float
    
    # Original vs Retrofitted Capacities
    phi_Mn_orig: float               # Original RC flexural capacity (kN·m)
    phi_Mn_ret: float                # Retrofitted flexural capacity (kN·m)
    phi_Vn_orig: float               # Original RC shear capacity (kN)
    phi_Vn_ret: float                # Retrofitted shear capacity (kN)
    
    # Capacity enhancement ratios
    flexure_gain_ratio: float        # phi_Mn_ret / phi_Mn_orig
    shear_gain_ratio: float          # phi_Vn_ret / phi_Vn_orig
    
    # Debonding & Strain details
    eps_fe: float                    # Effective design strain of CFRP
    f_fe: float                      # Effective design stress of CFRP (MPa)
    debonding_governed: bool
    
    details: Dict[str, Any] = field(default_factory=dict)


def _calc_concrete_ec(fck: float) -> float:
    """Calculate concrete modulus of elasticity according to KDS 14 20 10."""
    fcu = fck + 4.0 if fck <= 40.0 else fck + 6.0
    return 8500.0 * (fcu ** (1.0 / 3.0))


def check_retrofit_member(input_data: RetrofitDesignInput) -> RetrofitDesignResult:
    """Check Retrofitted RC Member according to KDS 14 20 90 and ACI 440.2R."""
    ex = input_data.existing
    Ec = _calc_concrete_ec(ex.fck)
    
    # 1. Original Unretrofitted Capacities (KDS 14 20 20)
    # Flexure:
    # a = As * fy / (0.85 * fck * b)
    a_orig = (ex.As * ex.fy) / (0.85 * ex.fck * ex.b) if ex.fck * ex.b > 0 else 0.0
    Mn_orig_Nmm = ex.As * ex.fy * (ex.d - a_orig / 2.0)
    phi_f = 0.85
    phi_Mn_orig = (phi_f * Mn_orig_Nmm) / 1e6
    
    # Shear:
    # Vc = (1/6) * sqrt(fck) * b * d
    # Vs = (Av * fyt * d) / s
    Vc_N = (1.0 / 6.0) * math.sqrt(ex.fck) * ex.b * ex.d
    Vs_N = (ex.Av * ex.fyt * ex.d) / ex.s if ex.s > 0 else 0.0
    Vn_orig_N = Vc_N + Vs_N
    phi_v = 0.75
    phi_Vn_orig = (phi_v * Vn_orig_N) / 1000.0
    
    # 2. Retrofitted Flexural Capacity (phi_Mn_ret)
    eps_fe = 0.0
    f_fe = 0.0
    debonding_governed = False
    phi_Mn_ret = phi_Mn_orig
    
    if input_data.retrofit_type in [RetrofitType.FLEXURE, RetrofitType.COMBINED]:
        if input_data.method in [RetrofitMethod.CFRP_PLATE, RetrofitMethod.CFRP_SHEET]:
            cfrp = input_data.cfrp or CFRPProp()
            # Environmental reduction factor CE
            ce_map = {
                ExposureCondition.INTERIOR: 0.95,
                ExposureCondition.EXTERIOR: 0.85,
                ExposureCondition.AGGRESSIVE: 0.75,
            }
            CE = ce_map.get(cfrp.exposure, 0.95)
            eps_fu_star = CE * cfrp.eps_fu
            
            # Debonding strain reduction factor kappa_m (ACI 440.2R / KDS 14 20 90)
            # kappa_m = (1 / (60 * eps_fu_star)) * (1 - (n * Ef * tf) / 360000) <= 0.90
            n_tf_Ef = cfrp.num_plies * cfrp.Ef * cfrp.tf
            term = 1.0 - (n_tf_Ef / 360000.0)
            kappa_m = min(0.90, max(0.10, (1.0 / (60.0 * eps_fu_star)) * term if eps_fu_star > 0 else 0.90))
            
            # Effective strain: eps_fe = min(0.004, kappa_m * eps_fu_star)
            eps_fe_calc = kappa_m * eps_fu_star
            eps_fe = min(0.004, eps_fe_calc)
            debonding_governed = (0.004 <= eps_fe_calc) or (kappa_m < 0.90)
            f_fe = cfrp.Ef * eps_fe
            
            # Total CFRP area Af = num_plies * bf * tf
            Af = cfrp.num_plies * cfrp.bf * cfrp.tf
            
            # Additional tension force from CFRP: T_f = Af * f_fe
            T_f = Af * f_fe
            psi_f = 0.85  # Strength reduction factor for CFRP flexure
            
            # Equilibrium: C_c = T_s + psi_f * T_f = 0.85 * fck * b * a_ret
            a_ret = (ex.As * ex.fy + psi_f * T_f) / (0.85 * ex.fck * ex.b) if ex.fck * ex.b > 0 else 0.0
            
            # Moment about concrete centroid
            # df = h (CFRP bonded to soffit)
            df = ex.h
            Mn_ret_Nmm = ex.As * ex.fy * (ex.d - a_ret / 2.0) + psi_f * T_f * (df - a_ret / 2.0)
            phi_Mn_ret = (phi_f * Mn_ret_Nmm) / 1e6
            
        elif input_data.method == RetrofitMethod.STEEL_PLATE:
            sp = input_data.steel_plate or SteelPlateProp()
            Asp = sp.bsp * sp.tsp
            T_sp = Asp * sp.fys
            
            a_ret = (ex.As * ex.fy + T_sp) / (0.85 * ex.fck * ex.b) if ex.fck * ex.b > 0 else 0.0
            df = ex.h + sp.tsp / 2.0
            Mn_ret_Nmm = ex.As * ex.fy * (ex.d - a_ret / 2.0) + T_sp * (df - a_ret / 2.0)
            phi_Mn_ret = (phi_f * Mn_ret_Nmm) / 1e6
            
    # 3. Retrofitted Shear Capacity (phi_Vn_ret)
    phi_Vn_ret = phi_Vn_orig
    Vf_N = 0.0
    
    if input_data.retrofit_type in [RetrofitType.SHEAR, RetrofitType.COMBINED]:
        if input_data.method in [RetrofitMethod.CFRP_PLATE, RetrofitMethod.CFRP_SHEET]:
            cfrp = input_data.cfrp or CFRPProp()
            ce_map = {
                ExposureCondition.INTERIOR: 0.95,
                ExposureCondition.EXTERIOR: 0.85,
                ExposureCondition.AGGRESSIVE: 0.75,
            }
            CE = ce_map.get(cfrp.exposure, 0.95)
            eps_fu_star = CE * cfrp.eps_fu
            
            if cfrp.is_full_wrap:
                # Full wrapping
                eps_fe_v = min(0.004, 0.75 * eps_fu_star)
                psi_fv = 0.95
            else:
                # U-wrapping
                # kappa_v reduction factor (approx 0.65)
                kappa_v = min(0.75, 0.65)
                eps_fe_v = min(0.004, kappa_v * eps_fu_star)
                psi_fv = 0.85
                
            f_fe_v = cfrp.Ef * eps_fe_v
            # Afv = 2 * n * tf * bf (shear strips on both faces)
            Afv = 2.0 * cfrp.num_plies * cfrp.tf * cfrp.bf
            dfv = ex.d  # effective depth for shear
            sf = max(cfrp.bf, cfrp.sf)
            
            # Vf = (Afv * f_fe * dfv) / sf
            Vf_N = (Afv * f_fe_v * dfv) / sf if sf > 0 else 0.0
            # Total design shear
            Vn_ret_N = Vc_N + Vs_N + psi_fv * Vf_N
            phi_Vn_ret = (phi_v * Vn_ret_N) / 1000.0
            
        elif input_data.method == RetrofitMethod.STEEL_PLATE:
            sp = input_data.steel_plate or SteelPlateProp()
            # Steel side plate shear contribution
            # Vsp = 2 * tsp * d * (0.60 * fys)
            Vsp_N = 2.0 * sp.tsp * ex.d * (0.60 * sp.fys)
            Vn_ret_N = Vc_N + Vs_N + Vsp_N
            phi_Vn_ret = (phi_v * Vn_ret_N) / 1000.0

    # 4. Gain Ratios and DCRs
    flexure_gain = phi_Mn_ret / phi_Mn_orig if phi_Mn_orig > 0 else 1.0
    shear_gain = phi_Vn_ret / phi_Vn_orig if phi_Vn_orig > 0 else 1.0
    
    dcr_flexure = input_data.Mu / phi_Mn_ret if phi_Mn_ret > 0 else 0.0
    dcr_shear = input_data.Vu / phi_Vn_ret if phi_Vn_ret > 0 else 0.0
    
    # 5. Unstrengthened Limit Check (KDS 14 20 90: existing member must sustain 1.1*DL + 0.75*LL)
    # Ensure unstrengthened member can at least carry existing dead load
    unstrengthened_safe = (ex.M_DL <= phi_Mn_orig)
    
    is_safe = (dcr_flexure <= 1.0) and (dcr_shear <= 1.0) and unstrengthened_safe
    
    return RetrofitDesignResult(
        is_safe=is_safe,
        dcr_flexure=round(dcr_flexure, 4),
        dcr_shear=round(dcr_shear, 4),
        phi_Mn_orig=round(phi_Mn_orig, 2),
        phi_Mn_ret=round(phi_Mn_ret, 2),
        phi_Vn_orig=round(phi_Vn_orig, 2),
        phi_Vn_ret=round(phi_Vn_ret, 2),
        flexure_gain_ratio=round(flexure_gain, 3),
        shear_gain_ratio=round(shear_gain, 3),
        eps_fe=round(eps_fe, 6),
        f_fe=round(f_fe, 2),
        debonding_governed=debonding_governed,
        details={
            "Vc": round(Vc_N / 1000.0, 2),
            "Vs": round(Vs_N / 1000.0, 2),
            "Vf": round(Vf_N / 1000.0, 2),
            "unstrengthened_safe": unstrengthened_safe,
        }
    )
