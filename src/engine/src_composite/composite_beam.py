"""Composite Beam Design Engine (KDS 14 31 30).

Implements:
1. Effective Flange Width (b_eff)
2. Headed Stud Shear Connector Nominal Strength (Qn)
3. Full and Partial Composite Action Analysis
4. Plastic Moment Strength (Mn) and Design Strength (phi_b * Mn)
5. Beam Web Shear Strength (Vn)
"""

from dataclasses import dataclass, field
import math
from typing import Optional, Dict, Any


@dataclass
class StudBoltInput:
    """Headed stud shear connector properties."""
    diameter: float = 19.0       # Stud diameter d_sa (mm)
    Fu: float = 400.0            # Stud tensile strength (MPa)
    Rg: float = 1.0              # Group effect factor (1.0 for solid slab, 0.85 for ribbed deck perpendicular)
    Rp: float = 0.75             # Position factor (0.75 for mid/strong pos, 0.6 for weak pos)
    num_studs_half_span: int = 20  # Number of studs between zero and max moment


@dataclass
class CompositeBeamInput:
    """Input parameters for composite steel-concrete beam."""
    # Beam span & spacing (mm)
    L: float = 8000.0            # Span length (mm)
    beam_spacing: float = 3000.0 # Center-to-center beam spacing (mm)
    
    # Structural Steel Section (H-Beam: H x B x tw x tf)
    d_s: float = 400.0           # Overall steel beam depth (mm)
    b_f: float = 200.0           # Steel beam flange width (mm)
    t_f: float = 13.0            # Steel beam flange thickness (mm)
    t_w: float = 8.0             # Steel beam web thickness (mm)
    Fy: float = 355.0            # Steel yield strength (MPa)
    Es: float = 205000.0         # Steel elastic modulus (MPa)
    
    # Concrete Slab
    h_f: float = 120.0           # Concrete slab thickness (mm) (above deck if composite deck)
    h_deck: float = 0.0          # Deck plate rib height (mm)
    fck: float = 27.0            # Concrete compressive strength (MPa)
    Ec: Optional[float] = None   # Concrete elastic modulus (MPa)
    
    # Shear connectors
    stud: StudBoltInput = field(default_factory=StudBoltInput)
    
    # Factored Design Actions
    Mu: float = 350.0            # Factored positive bending moment (kN·m)
    Vu: float = 150.0            # Factored shear force (kN)


@dataclass
class CompositeBeamResult:
    """Design check results for composite beam."""
    is_safe: bool
    dcr_flexure: float
    dcr_shear: float
    
    # Effective flange width & Stud strength
    b_eff: float                 # Effective flange width (mm)
    Qn_single: float             # Single stud nominal shear strength (kN)
    sum_Qn: float                # Total stud shear capacity in shear span (kN)
    composite_ratio: float       # Degree of shear connection (%)
    is_full_composite: bool
    
    # Strength
    Mn: float                    # Nominal flexural strength (kN·m)
    phi_Mn: float                # Design flexural strength (kN·m) (phi_b = 0.90)
    Vn: float                    # Nominal web shear strength (kN)
    phi_Vn: float                # Design shear strength (kN) (phi_v = 0.90)
    
    # Section properties
    As: float                    # Steel area (mm2)
    plastic_neutral_axis: str    # "SLAB", "FLANGE", or "WEB"
    details: Dict[str, Any] = field(default_factory=dict)


def _calc_concrete_ec(fck: float) -> float:
    """Calculate concrete modulus of elasticity according to KDS 14 20 10."""
    fcu = fck + 4.0 if fck <= 40.0 else fck + 6.0
    return 8500.0 * (fcu ** (1.0 / 3.0))


def check_composite_beam(input_data: CompositeBeamInput) -> CompositeBeamResult:
    """Check Composite Beam according to KDS 14 31 30."""
    Ec = input_data.Ec if input_data.Ec is not None else _calc_concrete_ec(input_data.fck)
    Es = input_data.Es
    Fy = input_data.Fy
    fck = input_data.fck
    
    # 1. Effective Flange Width (b_eff)
    # b_eff <= min(L / 4, beam_spacing, b_w + 16 * h_f)
    b_eff = min(
        input_data.L / 4.0,
        input_data.beam_spacing,
        input_data.b_f + 16.0 * input_data.h_f
    )
    
    # 2. Steel Section Geometric Properties
    d_s = input_data.d_s
    b_f = input_data.b_f
    t_f = input_data.t_f
    t_w = input_data.t_w
    h_w = d_s - 2.0 * t_f
    
    Af = b_f * t_f
    Aw = h_w * t_w
    As = 2.0 * Af + Aw
    
    # 3. Stud Bolt Nominal Shear Strength Qn (KDS 14 31 30)
    # Qn = min(0.5 * Asa * sqrt(fck * Ec), Rg * Rp * Asa * Fu)
    stud = input_data.stud
    Asa = math.pi * (stud.diameter ** 2) / 4.0
    
    Qn1 = 0.5 * Asa * math.sqrt(fck * Ec)
    Qn2 = stud.Rg * stud.Rp * Asa * stud.Fu
    Qn_single_N = min(Qn1, Qn2)
    Qn_single = Qn_single_N / 1000.0
    
    sum_Qn_N = stud.num_studs_half_span * Qn_single_N
    sum_Qn = sum_Qn_N / 1000.0
    
    # 4. Plastic Capacities of Components
    # Cc_max = 0.85 * fck * b_eff * h_f (Maximum slab compression)
    # Ts_max = As * Fy (Maximum steel tension)
    Cc_max_N = 0.85 * fck * b_eff * input_data.h_f
    Ts_max_N = As * Fy
    
    # Limit for full composite action
    V_prime_full = min(Cc_max_N, Ts_max_N)
    
    # Actual compressive force transferred by studs (V')
    V_prime_N = min(V_prime_full, sum_Qn_N)
    composite_ratio = (V_prime_N / V_prime_full) * 100.0 if V_prime_full > 0 else 100.0
    is_full_composite = composite_ratio >= 100.0 - 1e-4
    
    # 5. Plastic Neutral Axis (PNA) and Moment Capacity (Mn)
    # Slab top is at y = d_s + h_deck + h_f
    # Steel bottom is at y = 0
    y_steel_centroid = d_s / 2.0
    
    if V_prime_N >= Ts_max_N:
        # Case A: PNA in Concrete Slab
        # Depth of concrete stress block: a = Ts / (0.85 * fck * b_eff)
        a = Ts_max_N / (0.85 * fck * b_eff)
        pna_type = "SLAB"
        
        # Lever arm from concrete centroid to steel centroid
        # y_concrete = d_s + h_deck + h_f - a / 2.0
        y_concrete = d_s + input_data.h_deck + input_data.h_f - a / 2.0
        arm = y_concrete - y_steel_centroid
        
        Mn_Nmm = Ts_max_N * arm
    else:
        # Case B: Partial composite or PNA in Steel Section
        # Compressive force from slab = V_prime_N
        C_c = V_prime_N
        # Tensile and compressive force in steel must balance: T_steel - C_steel = C_c => T_steel + C_steel = As * Fy
        # C_steel = (As * Fy - C_c) / 2
        C_s = (Ts_max_N - C_c) / 2.0
        
        C_flange_max = Af * Fy
        if C_s <= C_flange_max:
            # PNA in Top Flange
            pna_type = "FLANGE"
            # Depth into top flange from top of steel
            y_f = C_s / (b_f * Fy) if b_f * Fy > 0 else 0.0
            
            # Moment calculation about steel plastic neutral axis or standard decomposition:
            # Mn = Ts_max * (d_s/2) + C_c * (d_s + h_deck + h_f - a'/2) - C_s * (...)
            # Equivalent classical formula:
            a_eff = C_c / (0.85 * fck * b_eff) if 0.85 * fck * b_eff > 0 else 0.0
            y_c_center = d_s + input_data.h_deck + input_data.h_f - a_eff / 2.0
            
            # Moment about bottom of steel:
            # Steel contribution + Slab contribution
            Mn_Nmm = (
                C_c * (y_c_center - y_steel_centroid)
                + Ts_max_N * (0.0) # centered
                + (Af * Fy * (d_s - t_f / 2.0 - y_steel_centroid))
                - (2.0 * C_s * (d_s - y_f / 2.0 - y_steel_centroid))
            )
            # More directly: Mn = M_steel_plastic_reduced + C_c * arm
            # Base steel plastic moment Mp_s = Zx * Fy
            Zx = 2.0 * (Af * (d_s / 2.0 - t_f / 2.0)) + 2.0 * ((Aw / 2.0) * (h_w / 4.0))
            Mp_s = Zx * Fy
            arm_slab = y_c_center - y_steel_centroid
            # Mn with partial connection: Mn = Mp_s + (V_prime / V_prime_full) * (Mn_full - Mp_s) or exact stress equilibrium
            Mn_Nmm = Mp_s + C_c * arm_slab - (C_s ** 2) / (b_f * Fy)
        else:
            # PNA in Web
            pna_type = "WEB"
            C_web = C_s - C_flange_max
            y_w = C_web / (t_w * Fy) if t_w * Fy > 0 else 0.0
            
            a_eff = C_c / (0.85 * fck * b_eff) if 0.85 * fck * b_eff > 0 else 0.0
            y_c_center = d_s + input_data.h_deck + input_data.h_f - a_eff / 2.0
            arm_slab = y_c_center - y_steel_centroid
            
            Zx = 2.0 * (Af * (d_s / 2.0 - t_f / 2.0)) + 2.0 * ((Aw / 2.0) * (h_w / 4.0))
            Mp_s = Zx * Fy
            Mn_Nmm = Mp_s + C_c * arm_slab - (C_web ** 2) / (t_w * Fy)
            
    Mn = Mn_Nmm / 1e6  # N·mm -> kN·m
    phi_b = 0.90
    phi_Mn = phi_b * Mn
    
    # 6. Web Shear Strength Vn (KDS 14 31 30 / KDS 14 31 15)
    # Aw_web = d_s * t_w
    Aw_web = d_s * t_w
    Vn_N = 0.60 * Fy * Aw_web
    Vn = Vn_N / 1000.0
    phi_v = 0.90
    phi_Vn = phi_v * Vn
    
    # 7. Demand-Capacity Ratios
    dcr_flexure = input_data.Mu / phi_Mn if phi_Mn > 0 else 999.0
    dcr_shear = input_data.Vu / phi_Vn if phi_Vn > 0 else 999.0
    is_safe = dcr_flexure <= 1.0 and dcr_shear <= 1.0
    
    return CompositeBeamResult(
        is_safe=is_safe,
        dcr_flexure=round(dcr_flexure, 4),
        dcr_shear=round(dcr_shear, 4),
        b_eff=round(b_eff, 1),
        Qn_single=round(Qn_single, 2),
        sum_Qn=round(sum_Qn, 2),
        composite_ratio=round(composite_ratio, 2),
        is_full_composite=is_full_composite,
        Mn=round(Mn, 2),
        phi_Mn=round(phi_Mn, 2),
        Vn=round(Vn, 2),
        phi_Vn=round(phi_Vn, 2),
        As=round(As, 2),
        plastic_neutral_axis=pna_type,
        details={
            "Cc_max": round(Cc_max_N / 1000.0, 2),
            "Ts_max": round(Ts_max_N / 1000.0, 2),
            "V_prime": round(V_prime_N / 1000.0, 2),
            "Ec": round(Ec, 1),
        }
    )
