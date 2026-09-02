"""Steel Column & Beam-Column Design Module (KDS 14 31 10 / AISC 360 LRFD) for AltDP_3rd.

Evaluates flexural buckling, torsional buckling, flexural-torsional buckling, and combined
axial compression + biaxial bending interaction (P-M DCR) for structural steel members.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional, Dict, Any

from src.engine.materials import SteelMaterial
from src.engine.steel.compactness import (
    check_h_section_compactness,
    check_box_section_compactness,
    check_pipe_section_compactness,
    check_angle_section_compactness,
    SectionCompactnessResult,
    SectionClassification,
    SectionType
)
from src.engine.steel.beam import design_steel_beam, SteelBeamInput


@dataclass
class SteelColumnInput:
    """Steel Column Geometry and Combined Loading Parameters."""
    name: str = "SC1"
    section_type: str = "H"       # "H", "BOX", "PIPE", "ANGLE"
    
    # H-Section Dimensions (mm)
    H: float = 350.0             # Total depth
    B: float = 350.0             # Width
    tw: float = 12.0             # Web thickness
    tf: float = 19.0             # Flange thickness
    r: float = 16.0              # Fillet radius
    
    # Box / Pipe / Angle dimensions (if applicable)
    D: float = 0.0               # Outer diameter (mm)
    t_wall: float = 0.0          # Wall thickness (mm)
    
    # Unbraced Lengths (mm)
    Lx: float = 4000.0           # Length for X-axis buckling
    Ly: float = 4000.0           # Length for Y-axis buckling
    Lz: float = 4000.0           # Length for torsional buckling
    
    # Effective Length Factors (K-factors)
    Kx: float = 1.0              # Effective length factor for X-axis
    Ky: float = 1.0              # Effective length factor for Y-axis
    Kz: float = 1.0              # Effective length factor for torsion
    
    # Lateral-Torsional Buckling unbraced length
    Lb: float = 4000.0           # mm
    Cb: float = 1.0
    
    # Factored Design Forces
    Pu: float = 1200.0           # kN (Factored axial compression)
    Mux: float = 150.0           # kN*m (Factored major-axis moment)
    Muy: float = 50.0            # kN*m (Factored minor-axis moment)
    Vux: float = 40.0            # kN (Shear along major axis)
    Vuy: float = 30.0            # kN (Shear along minor axis)
    
    # Moment Amplification Factor Cm
    Cmx: float = 1.0
    Cmy: float = 1.0
    
    material: SteelMaterial = field(default_factory=lambda: SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0))


@dataclass
class SteelColumnResult:
    """Steel Column Design & P-M Interaction Verification Output."""
    compactness: SectionCompactnessResult
    
    # Geometric Properties
    Ag: float                    # mm2 (Gross area)
    Ae: float                    # mm2 (Effective area considering slenderness)
    rx: float                    # mm (Radius of gyration X)
    ry: float                    # mm (Radius of gyration Y)
    
    # Slenderness & Buckling
    slenderness_x: float         # Kx * Lx / rx
    slenderness_y: float         # Ky * Ly / ry
    max_slenderness: float       # max(KL/r)
    is_slenderness_ok: bool      # max(KL/r) <= 200
    
    # Axial Compressive Capacities
    Fe: float                    # MPa (Euler elastic buckling stress)
    Fcr: float                   # MPa (Critical buckling stress)
    Pn: float                    # kN (Nominal compressive capacity)
    phi_c: float                 # 0.90
    phi_Pn: float                # kN (Design compressive capacity)
    axial_dcr: float             # Pu / phi_Pn
    
    # Flexural Capacities
    phi_Mn_x: float              # kN*m (Design major flexural capacity)
    phi_Mn_y: float              # kN*m (Design minor flexural capacity)
    flexure_dcr_x: float         # Mux / phi_Mn_x
    flexure_dcr_y: float         # Muy / phi_Mn_y
    
    # P-M Combined Interaction
    pm_formula: str              # "H1-1a (Pu/phiPn >= 0.2)" or "H1-1b (Pu/phiPn < 0.2)"
    pm_dcr: float                # Combined P-M interaction ratio
    
    # Overall Status
    max_dcr: float
    is_safe: bool
    summary: str


def design_steel_column(inp: SteelColumnInput) -> SteelColumnResult:
    """Evaluate KDS 14 31 10 compressive strength and 3D P-M interaction for steel columns."""
    Fy = inp.material.Fy_design if hasattr(inp.material, 'Fy_design') else inp.material.Fy
    Fu = inp.material.Fu
    E = inp.material.E
    G = inp.material.G if hasattr(inp.material, 'G') else E / (2.0 * 1.3)
    
    phi_c = 0.90
    phi_b = 0.90
    
    # 1. Section Properties & Compactness under uniform compression
    if inp.section_type.upper() == "BOX":
        B = inp.B
        H = inp.H
        t = inp.tw if inp.tw > 0 else (inp.t_wall if inp.t_wall > 0 else 12.0)
        compactness = check_box_section_compactness(B, H, t, Fy, E, "compression")
        
        Ag = 2.0 * t * (B + H - 2.0 * t)
        Ix = (B * (H**3) - (B - 2.0 * t) * ((H - 2.0 * t)**3)) / 12.0
        Iy = (H * (B**3) - (H - 2.0 * t) * ((B - 2.0 * t)**3)) / 12.0
        Sx = Ix / (H / 2.0)
        Sy = Iy / (B / 2.0)
        Zx = (B * (H**2) / 4.0) - ((B - 2.0 * t) * ((H - 2.0 * t)**2) / 4.0)
        Zy = (H * (B**2) / 4.0) - ((H - 2.0 * t) * ((B - 2.0 * t)**2) / 4.0)
        
        rx = math.sqrt(Ix / Ag) if Ag > 0 else 1.0
        ry = math.sqrt(Iy / Ag) if Ag > 0 else 1.0
        
        # Major and minor flexural capacity
        Mn_x = (Fy * Zx) / 1e6 if compactness.is_compact else (Fy * Sx) / 1e6
        Mn_y = (Fy * Zy) / 1e6 if compactness.is_compact else (Fy * Sy) / 1e6
        
    elif inp.section_type.upper() == "PIPE":
        D = inp.D if inp.D > 0 else inp.H
        t = inp.tw if inp.tw > 0 else (inp.t_wall if inp.t_wall > 0 else 12.0)
        compactness = check_pipe_section_compactness(D, t, Fy, E, "compression")
        
        Ro = D / 2.0
        Ri = Ro - t
        Ag = math.pi * (Ro**2 - Ri**2)
        Ix = math.pi * (Ro**4 - Ri**4) / 4.0
        Iy = Ix
        Sx = Ix / Ro
        Sy = Sx
        Zx = 4.0 * (Ro**3 - Ri**3) / 3.0
        Zy = Zx
        
        rx = math.sqrt(Ix / Ag) if Ag > 0 else 1.0
        ry = rx
        
        Mn_x = min((Fy * Zx) / 1e6, 1.6 * (Fy * Sx) / 1e6)
        Mn_y = Mn_x
        
    else:
        # Standard H-Shape Column (Default)
        H = inp.H
        B = inp.B
        tw = inp.tw
        tf = inp.tf
        h_web = max(H - 2.0 * tf, 1.0)
        
        compactness = check_h_section_compactness(B, tf, H, tw, Fy, E, "compression")
        
        Af = B * tf
        Aw = h_web * tw
        Ag = 2.0 * Af + Aw
        
        Ix = (B * (H**3) - (B - tw) * (h_web**3)) / 12.0
        Iy = 2.0 * (tf * (B**3)) / 12.0 + (h_web * (tw**3)) / 12.0
        
        Sx = Ix / (H / 2.0)
        Sy = Iy / (B / 2.0)
        
        Zx = 2.0 * (B * tf * (H / 2.0 - tf / 2.0)) + tw * (h_web / 2.0) ** 2
        Zy = 2.0 * (tf * (B**2) / 4.0) + h_web * (tw**2) / 4.0
        
        rx = math.sqrt(Ix / Ag) if Ag > 0 else 1.0
        ry = math.sqrt(Iy / Ag) if Ag > 0 else 1.0
        
        # Compute flexural capacity from beam engine logic
        beam_in = SteelBeamInput(
            H=H, B=B, tw=tw, tf=tf,
            L=inp.Lx, Lb=inp.Lb, Cb=inp.Cb,
            Mux=inp.Mux, Muy=inp.Muy, material=inp.material
        )
        beam_res = design_steel_beam(beam_in)
        Mn_x = beam_res.Mn_x
        Mn_y = beam_res.Mn_y
        
    # 2. Slenderness & Euler Elastic Buckling Stress (KDS 14 31 10 4.3.2)
    slenderness_x = (inp.Kx * inp.Lx) / rx if rx > 0 else 999.0
    slenderness_y = (inp.Ky * inp.Ly) / ry if ry > 0 else 999.0
    max_slenderness = max(slenderness_x, slenderness_y)
    is_slenderness_ok = (max_slenderness <= 200.0)
    
    Fe = (math.pi ** 2 * E) / (max_slenderness ** 2) if max_slenderness > 0 else 0.001
    
    # 3. Critical Buckling Stress (Fcr) considering slenderness factor Q
    Q = compactness.Q
    Ae = Ag * compactness.Ae_ratio
    
    slender_limit = 4.71 * math.sqrt(E / (Q * Fy))
    
    if max_slenderness <= slender_limit:
        # Inelastic buckling
        exp_power = (Q * Fy) / Fe
        Fcr = Q * (0.658 ** exp_power) * Fy
    else:
        # Elastic buckling
        Fcr = 0.877 * Fe
        
    Pn = (Fcr * Ag) / 1e3  # kN
    phi_Pn = phi_c * Pn
    axial_dcr = inp.Pu / phi_Pn if phi_Pn > 0 else 999.0
    
    # 4. Moment Amplification Factors B1 (KDS 14 31 10 4.5.2)
    Pe1_x = (math.pi ** 2 * E * Ix / ((inp.Kx * inp.Lx)**2)) / 1e3 if (inp.Kx * inp.Lx) > 0 else 999999.0
    Pe1_y = (math.pi ** 2 * E * Iy / ((inp.Ky * inp.Ly)**2)) / 1e3 if (inp.Ky * inp.Ly) > 0 else 999999.0
    
    B1_x = inp.Cmx / (1.0 - inp.Pu / Pe1_x) if (Pe1_x > inp.Pu) else 1.0
    B1_x = max(B1_x, 1.0)
    
    B1_y = inp.Cmy / (1.0 - inp.Pu / Pe1_y) if (Pe1_y > inp.Pu) else 1.0
    B1_y = max(B1_y, 1.0)
    
    Mrx = B1_x * inp.Mux
    Mry = B1_y * inp.Muy
    
    phi_Mn_x = phi_b * Mn_x
    phi_Mn_y = phi_b * Mn_y
    
    flexure_dcr_x = Mrx / phi_Mn_x if phi_Mn_x > 0 else 999.0
    flexure_dcr_y = Mry / phi_Mn_y if phi_Mn_y > 0 else 0.0
    
    # 5. Combined Axial-Biaxial Flexure P-M Interaction (KDS 14 31 10 4.5.1 Eq 4.5-1 & 4.5-2)
    if axial_dcr >= 0.20:
        pm_formula = "KDS Eq 4.5-1 (Pu/phiPn >= 0.2)"
        pm_dcr = axial_dcr + (8.0 / 9.0) * (flexure_dcr_x + flexure_dcr_y)
    else:
        pm_formula = "KDS Eq 4.5-2 (Pu/phiPn < 0.2)"
        pm_dcr = (axial_dcr / 2.0) + (flexure_dcr_x + flexure_dcr_y)
        
    max_dcr = max(axial_dcr, flexure_dcr_x, flexure_dcr_y, pm_dcr)
    is_safe = (pm_dcr <= 1.0) and is_slenderness_ok
    
    status = "OK" if is_safe else "NG"
    summary = (f"[{status}] Steel Column P-M DCR={pm_dcr:.3f} "
               f"(Axial={axial_dcr:.3f}, Mux={flexure_dcr_x:.3f}, Muy={flexure_dcr_y:.3f}, KL/r={max_slenderness:.1f})")
    
    return SteelColumnResult(
        compactness=compactness,
        Ag=Ag,
        Ae=Ae,
        rx=rx,
        ry=ry,
        slenderness_x=slenderness_x,
        slenderness_y=slenderness_y,
        max_slenderness=max_slenderness,
        is_slenderness_ok=is_slenderness_ok,
        Fe=Fe,
        Fcr=Fcr,
        Pn=Pn,
        phi_c=phi_c,
        phi_Pn=phi_Pn,
        axial_dcr=axial_dcr,
        phi_Mn_x=phi_Mn_x,
        phi_Mn_y=phi_Mn_y,
        flexure_dcr_x=flexure_dcr_x,
        flexure_dcr_y=flexure_dcr_y,
        pm_formula=pm_formula,
        pm_dcr=pm_dcr,
        max_dcr=max_dcr,
        is_safe=is_safe,
        summary=summary
    )
