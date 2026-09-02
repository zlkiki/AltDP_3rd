"""Steel Brace Design Module (KDS 14 31 10 / AISC 360 LRFD) for AltDP_3rd.

Evaluates tension yielding, tension rupture (effective net area with shear lag U factor),
compression buckling, and slenderness limits (L/r <= 200 / 300) for structural steel braces.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional

from src.engine.materials import SteelMaterial
from src.engine.steel.compactness import (
    check_h_section_compactness,
    check_box_section_compactness,
    check_pipe_section_compactness,
    check_angle_section_compactness,
    SectionCompactnessResult
)


class BraceConnection(str, Enum):
    WELDED = "WELDED"
    BOLTED = "BOLTED"


@dataclass
class SteelBraceInput:
    """Steel Brace Geometry and Loading Parameters."""
    name: str = "BR1"
    section_type: str = "ANGLE"   # "ANGLE", "2ANGLE", "H", "BOX", "PIPE", "CHANNEL"
    
    # Section Dimensions (mm)
    B: float = 100.0              # Width / Leg 1
    H: float = 100.0              # Height / Leg 2 / Outer Diameter
    t: float = 10.0               # Thickness
    tw: float = 8.0               # Web thickness (for H/Channel)
    tf: float = 10.0              # Flange thickness (for H/Channel)
    
    # Member Length & End Boundary
    L: float = 4000.0             # mm (Total length)
    K: float = 1.0                # Effective length factor
    
    # Connection Parameters for Shear Lag & Net Area
    connection_type: BraceConnection = BraceConnection.BOLTED
    bolt_hole_diameter: float = 22.0  # mm (Standard hole for M20)
    num_bolt_holes: int = 2           # Number of holes in critical net section
    connection_length_L: float = 150.0  # mm (Connection weld length or distance between outer bolts)
    eccentricity_x_bar: float = 28.2    # mm (Distance from connection plane to centroid)
    
    # Factored Design Forces
    Tu: float = 250.0             # kN (Factored tensile force)
    Pu: float = 150.0             # kN (Factored compressive force)
    
    material: SteelMaterial = field(default_factory=lambda: SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0))


@dataclass
class SteelBraceResult:
    """Steel Brace Design Output."""
    Ag: float                     # mm2 (Gross area)
    An: float                     # mm2 (Net area)
    Ae: float                     # mm2 (Effective net area)
    U: float                      # Shear lag factor
    r_min: float                  # mm (Minimum radius of gyration)
    slenderness: float            # K * L / r_min
    is_slenderness_tension_ok: bool  # L/r <= 300
    is_slenderness_comp_ok: bool     # KL/r <= 200
    
    # Tension Capacity
    phi_t_yield: float            # 0.90
    phi_Pn_yield: float           # kN (0.90 * Fy * Ag)
    yield_dcr: float              # Tu / phi_Pn_yield
    
    phi_t_rupture: float          # 0.75
    phi_Pn_rupture: float         # kN (0.75 * Fu * Ae)
    rupture_dcr: float            # Tu / phi_Pn_rupture
    
    tension_dcr: float            # max(yield_dcr, rupture_dcr)
    
    # Compression Capacity
    Fe: float                     # MPa
    Fcr: float                    # MPa
    phi_c: float                  # 0.90
    phi_Pn_comp: float            # kN (0.90 * Fcr * Ag)
    comp_dcr: float               # Pu / phi_Pn_comp
    
    # Overall
    max_dcr: float
    is_safe: bool
    summary: str


def design_steel_brace(inp: SteelBraceInput) -> SteelBraceResult:
    """Evaluate KDS 14 31 10 tensile and compressive capacity for a steel brace."""
    Fy = inp.material.Fy_design if hasattr(inp.material, 'Fy_design') else inp.material.Fy
    Fu = inp.material.Fu
    E = inp.material.E
    
    phi_t_yield = 0.90
    phi_t_rupture = 0.75
    phi_c = 0.90
    
    # 1. Section Geometric Properties & Minimum Radius of Gyration
    sec_type = inp.section_type.upper()
    
    if sec_type in ["ANGLE", "L"]:
        B = inp.B
        t = inp.t
        Ag = (2.0 * B - t) * t
        # r_min approximation for equal leg angle: rz ~ 0.195 * B
        r_min = 0.195 * B
        An = max(Ag - inp.num_bolt_holes * inp.bolt_hole_diameter * t, 0.5 * Ag)
        
    elif sec_type in ["2ANGLE", "DOUBLE_ANGLE"]:
        B = inp.B
        t = inp.t
        Ag = 2.0 * (2.0 * B - t) * t
        r_min = 0.24 * B
        An = max(Ag - 2.0 * inp.num_bolt_holes * inp.bolt_hole_diameter * t, 0.5 * Ag)
        
    elif sec_type == "PIPE":
        D = inp.H if inp.H > 0 else inp.B
        t = inp.t
        Ro = D / 2.0
        Ri = Ro - t
        Ag = math.pi * (Ro**2 - Ri**2)
        r_min = math.sqrt((Ro**2 + Ri**2) / 4.0)
        An = Ag
        
    elif sec_type == "BOX":
        B = inp.B
        H = inp.H
        t = inp.t
        Ag = 2.0 * t * (B + H - 2.0 * t)
        Ix = (B * (H**3) - (B - 2.0 * t) * ((H - 2.0 * t)**3)) / 12.0
        Iy = (H * (B**3) - (H - 2.0 * t) * ((B - 2.0 * t)**3)) / 12.0
        r_min = math.sqrt(min(Ix, Iy) / Ag)
        An = Ag
        
    else:
        # Default H-shape
        H = inp.H
        B = inp.B
        tw = inp.tw
        tf = inp.tf if inp.tf > 0 else inp.t
        h_web = max(H - 2.0 * tf, 1.0)
        Ag = 2.0 * (B * tf) + h_web * tw
        Iy = 2.0 * (tf * (B**3)) / 12.0 + (h_web * (tw**3)) / 12.0
        r_min = math.sqrt(Iy / Ag) if Ag > 0 else 1.0
        An = max(Ag - inp.num_bolt_holes * inp.bolt_hole_diameter * tf * 2.0, 0.6 * Ag)
        
    # 2. Shear Lag Factor U (KDS 14 31 10 Table 4.4-1: U = 1 - x_bar / L)
    if inp.connection_length_L > 0 and inp.eccentricity_x_bar > 0:
        U = max(0.60, min(1.0 - (inp.eccentricity_x_bar / inp.connection_length_L), 0.90))
    else:
        U = 0.85 if sec_type in ["ANGLE", "CHANNEL"] else 1.0
        
    Ae = U * An
    
    # 3. Slenderness Evaluation
    slenderness = (inp.K * inp.L) / r_min if r_min > 0 else 999.0
    is_slenderness_tension_ok = (slenderness <= 300.0)
    is_slenderness_comp_ok = (slenderness <= 200.0)
    
    # 4. Tension Capacity
    # Gross Yielding
    Pn_yield = (Fy * Ag) / 1e3
    phi_Pn_yield = phi_t_yield * Pn_yield
    yield_dcr = inp.Tu / phi_Pn_yield if phi_Pn_yield > 0 else 999.0
    
    # Net Rupture
    Pn_rupture = (Fu * Ae) / 1e3
    phi_Pn_rupture = phi_t_rupture * Pn_rupture
    rupture_dcr = inp.Tu / phi_Pn_rupture if phi_Pn_rupture > 0 else 999.0
    
    tension_dcr = max(yield_dcr, rupture_dcr)
    
    # 5. Compression Capacity (Buckling)
    Fe = (math.pi ** 2 * E) / (slenderness ** 2) if slenderness > 0 else 0.001
    slender_limit = 4.71 * math.sqrt(E / Fy)
    
    if slenderness <= slender_limit:
        Fcr = (0.658 ** (Fy / Fe)) * Fy
    else:
        Fcr = 0.877 * Fe
        
    Pn_comp = (Fcr * Ag) / 1e3
    phi_Pn_comp = phi_c * Pn_comp
    comp_dcr = inp.Pu / phi_Pn_comp if phi_Pn_comp > 0 else 0.0
    
    max_dcr = max(tension_dcr, comp_dcr)
    is_safe = (max_dcr <= 1.0) and is_slenderness_tension_ok and is_slenderness_comp_ok
    
    status = "OK" if is_safe else "NG"
    summary = (f"[{status}] Steel Brace DCR={max_dcr:.3f} "
               f"(Tension={tension_dcr:.3f}, Comp={comp_dcr:.3f}, L/r={slenderness:.1f}, U={U:.2f})")
    
    return SteelBraceResult(
        Ag=Ag,
        An=An,
        Ae=Ae,
        U=U,
        r_min=r_min,
        slenderness=slenderness,
        is_slenderness_tension_ok=is_slenderness_tension_ok,
        is_slenderness_comp_ok=is_slenderness_comp_ok,
        phi_t_yield=phi_t_yield,
        phi_Pn_yield=phi_Pn_yield,
        yield_dcr=yield_dcr,
        phi_t_rupture=phi_t_rupture,
        phi_Pn_rupture=phi_Pn_rupture,
        rupture_dcr=rupture_dcr,
        tension_dcr=tension_dcr,
        Fe=Fe,
        Fcr=Fcr,
        phi_c=phi_c,
        phi_Pn_comp=phi_Pn_comp,
        comp_dcr=comp_dcr,
        max_dcr=max_dcr,
        is_safe=is_safe,
        summary=summary
    )
