"""Steel Beam Design Module (KDS 14 31 10 / AISC 360 LRFD) for AltDP_3rd.

Calculates section compactness, lateral-torsional buckling (LTB), major/minor flexural capacity,
shear capacity (with web shear buckling Cv), and serviceability deflections for steel flexural members.
"""

from dataclasses import dataclass, field
import math
from typing import Optional, List, Dict, Any

from src.engine.materials import SteelMaterial
from src.engine.steel.compactness import (
    check_h_section_compactness,
    check_box_section_compactness,
    check_pipe_section_compactness,
    SectionCompactnessResult,
    SectionClassification
)


def calculate_cb(Mmax: float, MA: float, MB: float, MC: float, Rm: float = 1.0) -> float:
    """Calculate moment gradient factor Cb (KDS 14 31 10 4.2.1.2.2).
    
    Cb = 12.5 * |Mmax| / (2.5*|Mmax| + 3*|MA| + 4*|MB| + 3*|MC|) * Rm <= 3.0
    """
    abs_max = abs(Mmax)
    abs_A = abs(MA)
    abs_B = abs(MB)
    abs_C = abs(MC)
    
    denom = 2.5 * abs_max + 3.0 * abs_A + 4.0 * abs_B + 3.0 * abs_C
    if denom <= 0.0:
        return 1.0
    
    cb = (12.5 * abs_max / denom) * Rm
    return min(max(cb, 1.0), 3.0)


@dataclass
class SteelBeamInput:
    """Steel Beam Geometry and Design Loading Parameters."""
    name: str = "SB1"
    section_type: str = "H"     # "H", "BOX", "PIPE"
    
    # H-Section Dimensions (mm)
    H: float = 400.0           # Total height
    B: float = 200.0           # Flange width
    tw: float = 8.0            # Web thickness
    tf: float = 13.0           # Flange thickness
    r: float = 16.0            # Fillet radius
    
    # Box / Pipe Dimensions (if applicable)
    D: float = 0.0             # Outer diameter (mm)
    t_wall: float = 0.0        # Wall thickness (mm)
    
    # Member Length & Unbraced Length (mm)
    L: float = 6000.0          # Total span length
    Lb: float = 3000.0         # Lateral unbraced length
    Cb: float = 1.0            # Moment gradient factor (or specify quarter moments)
    MA: float = 0.0            # Quarter-point moment (kN*m)
    MB: float = 0.0            # Mid-point moment (kN*m)
    MC: float = 0.0            # Three-quarter-point moment (kN*m)
    
    # Factored Design Forces
    Mux: float = 180.0         # kN*m (Major axis flexural moment)
    Muy: float = 0.0           # kN*m (Minor axis flexural moment)
    Vu: float = 120.0          # kN (Factored shear force)
    
    # Unfactored Service Load for Deflection (kN/m or kN)
    service_w: float = 15.0    # kN/m (Uniform service load)
    allowable_deflection_ratio: float = 300.0  # L / 300
    
    material: SteelMaterial = field(default_factory=lambda: SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0))


@dataclass
class SteelBeamResult:
    """Steel Beam Design Verification Output."""
    compactness: SectionCompactnessResult
    
    # Major-Axis Flexure (X-axis)
    Mp_x: float                # kN*m (Plastic moment capacity)
    Lp: float                  # mm (Limiting unbraced length for plastic flexure)
    Lr: float                  # mm (Limiting unbraced length for inelastic LTB)
    Mn_x: float                # kN*m (Nominal major flexural capacity)
    phi_b: float               # 0.90
    phi_Mn_x: float            # kN*m (Design major flexural capacity)
    flexure_dcr_x: float       # Mux / phi_Mn_x
    
    # Minor-Axis Flexure (Y-axis)
    Mp_y: float                # kN*m (Plastic minor moment)
    Mn_y: float                # kN*m (Nominal minor flexural capacity)
    phi_Mn_y: float            # kN*m (Design minor flexural capacity)
    flexure_dcr_y: float       # Muy / phi_Mn_y
    total_flexure_dcr: float   # Mux / phi_Mn_x + Muy / phi_Mn_y
    
    # Shear
    Cv: float                  # Web shear buckling coefficient
    Vn: float                  # kN (Nominal shear capacity)
    phi_v: float               # 0.90 (or 1.0)
    phi_Vn: float              # kN (Design shear capacity)
    shear_dcr: float           # Vu / phi_Vn
    
    # Serviceability (Deflection)
    delta_act: float           # mm (Calculated midspan deflection)
    delta_allow: float         # mm (Allowable deflection limit L / ratio)
    deflection_dcr: float      # delta_act / delta_allow
    
    # Overall Status
    max_dcr: float
    is_safe: bool
    summary: str


def design_steel_beam(inp: SteelBeamInput) -> SteelBeamResult:
    """Evaluate KDS 14 31 10 structural capacity for a steel beam."""
    Fy = inp.material.Fy_design if hasattr(inp.material, 'Fy_design') else inp.material.Fy
    E = inp.material.E
    G = inp.material.G if hasattr(inp.material, 'G') else E / (2.0 * 1.3)
    
    # Compute Cb if quarter moments are supplied
    Cb = inp.Cb
    if any([inp.MA != 0.0, inp.MB != 0.0, inp.MC != 0.0]):
        Cb = calculate_cb(inp.Mux, inp.MA, inp.MB, inp.MC)
        
    phi_b = 0.90
    phi_v = 0.90
    
    if inp.section_type.upper() == "BOX":
        # Box Section
        B = inp.B
        H = inp.H
        t = inp.tw if inp.tw > 0 else (inp.t_wall if inp.t_wall > 0 else 9.0)
        compactness = check_box_section_compactness(B, H, t, Fy, E, "flexure")
        
        Ag = 2.0 * t * (B + H - 2.0 * t)
        Ix = (B * (H**3) - (B - 2.0 * t) * ((H - 2.0 * t)**3)) / 12.0
        Iy = (H * (B**3) - (H - 2.0 * t) * ((B - 2.0 * t)**3)) / 12.0
        Sx = Ix / (H / 2.0)
        Sy = Iy / (B / 2.0)
        Zx = (B * (H**2) / 4.0) - ((B - 2.0 * t) * ((H - 2.0 * t)**2) / 4.0)
        Zy = (H * (B**2) / 4.0) - ((H - 2.0 * t) * ((B - 2.0 * t)**2) / 4.0)
        
        Mp_x = (Fy * Zx) / 1e6
        Mp_y = (Fy * Zy) / 1e6
        Lp = 0.13 * E * math.sqrt(Iy * 0.5) / (Fy * Sx) if Sx > 0 else 99999.0
        Lr = Lp * 2.5
        
        if compactness.is_compact:
            Mn_x = Mp_x
            Mn_y = Mp_y
        else:
            Mn_x = (Fy * Sx) / 1e6
            Mn_y = (Fy * Sy) / 1e6
            
        Cv = 1.0
        Aw = 2.0 * (H - 2.0 * t) * t
        Vn = (0.60 * Fy * Aw * Cv) / 1e3
        
    elif inp.section_type.upper() == "PIPE":
        # Pipe Section
        D = inp.D if inp.D > 0 else inp.H
        t = inp.tw if inp.tw > 0 else (inp.t_wall if inp.t_wall > 0 else 9.0)
        compactness = check_pipe_section_compactness(D, t, Fy, E, "flexure")
        
        Ro = D / 2.0
        Ri = Ro - t
        Ix = math.pi * (Ro**4 - Ri**4) / 4.0
        Iy = Ix
        Sx = Ix / Ro
        Sy = Sx
        Zx = 4.0 * (Ro**3 - Ri**3) / 3.0
        Zy = Zx
        
        Mp_x = (Fy * Zx) / 1e6
        Mp_y = Mp_x
        Lp = 99999.0
        Lr = 99999.0
        
        if compactness.is_compact:
            Mn_x = min(Mp_x, 1.6 * Fy * Sx / 1e6)
        elif compactness.is_non_compact:
            Mn_x = ((0.021 * E / (D / t) + Fy) * Sx) / 1e6
        else:
            Mn_x = ((0.33 * E / (D / t)) * Sx) / 1e6
        Mn_y = Mn_x
        
        Cv = 1.0
        Ag = math.pi * (Ro**2 - Ri**2)
        Aw = Ag / 2.0
        Vn = (0.60 * Fy * Aw * Cv) / 1e3
        
    else:
        # Standard H-Shape (Default)
        H = inp.H
        B = inp.B
        tw = inp.tw
        tf = inp.tf
        h_web = max(H - 2.0 * tf, 1.0)
        
        compactness = check_h_section_compactness(B, tf, H, tw, Fy, E, "flexure")
        
        # Section properties
        Af = B * tf
        Aw = h_web * tw
        Ag = 2.0 * Af + Aw
        
        Ix = (B * (H**3) - (B - tw) * (h_web**3)) / 12.0
        Iy = 2.0 * (tf * (B**3)) / 12.0 + (h_web * (tw**3)) / 12.0
        
        Sx = Ix / (H / 2.0)
        Sy = Iy / (B / 2.0)
        
        Zx = 2.0 * (B * tf * (H / 2.0 - tf / 2.0)) + tw * (h_web / 2.0) ** 2
        Zy = 2.0 * (tf * (B**2) / 4.0) + h_web * (tw**2) / 4.0
        
        ry = math.sqrt(Iy / Ag) if Ag > 0 else 1.0
        ho = H - tf
        rts = math.sqrt((Iy * ho) / (2.0 * Sx)) if Sx > 0 else ry
        
        J = (2.0 * B * (tf**3) + h_web * (tw**3)) / 3.0
        
        # 1. Major Flexural Strength (Mn_x) & LTB
        Mp_x = (Fy * Zx) / 1e6
        Mp_y = min((Fy * Zy) / 1e6, 1.6 * (Fy * Sy) / 1e6)
        
        Lp = 1.76 * ry * math.sqrt(E / Fy)
        factor = 0.7 * Fy / E
        term1 = J / (Sx * ho) if (Sx * ho) > 0 else 0.001
        Lr = 1.95 * rts * (1.0 / factor) * math.sqrt(term1 + math.sqrt(term1**2 + 6.76 * (factor**2)))
        
        Lb = inp.Lb
        if Lb <= Lp:
            Mn_x = Mp_x
        elif Lb <= Lr:
            Mn_x = Cb * (Mp_x - (Mp_x - 0.7 * Fy * Sx / 1e6) * ((Lb - Lp) / (Lr - Lp)))
            Mn_x = min(Mn_x, Mp_x)
        else:
            slenderness = Lb / rts
            Fcr = (Cb * (math.pi ** 2) * E) / (slenderness ** 2) * math.sqrt(1.0 + 0.078 * (J / (Sx * ho)) * (slenderness ** 2))
            Mn_x = min((Fcr * Sx) / 1e6, Mp_x)
            
        # Flange/Web local buckling reduction if non-compact
        if compactness.flange.is_non_compact:
            lambda_f = compactness.flange.lambda_val
            lambda_pf = compactness.flange.lambda_p
            lambda_rf = compactness.flange.lambda_r
            Mn_flb = Mp_x - (Mp_x - 0.7 * Fy * Sx / 1e6) * ((lambda_f - lambda_pf) / (lambda_rf - lambda_pf))
            Mn_x = min(Mn_x, Mn_flb)
            
        Mn_y = Mp_y
        
        # 2. Shear Strength (Vn) with web shear buckling Cv (KDS 14 31 10 4.2.3)
        lambda_w = h_web / tw
        kv = 5.0  # Unstiffened web
        limit1 = 1.10 * math.sqrt(kv * E / Fy)
        limit2 = 1.37 * math.sqrt(kv * E / Fy)
        
        if lambda_w <= limit1:
            Cv = 1.0
            phi_v = 1.0 if (lambda_w <= 2.24 * math.sqrt(E / Fy)) else 0.90
        elif lambda_w <= limit2:
            Cv = 1.10 * math.sqrt(kv * E / Fy) / lambda_w
            phi_v = 0.90
        else:
            Cv = 1.51 * kv * E / ((lambda_w**2) * Fy)
            phi_v = 0.90
            
        Vn = (0.60 * Fy * (H * tw) * Cv) / 1e3
        
    phi_Mn_x = phi_b * Mn_x
    phi_Mn_y = phi_b * Mn_y
    phi_Vn = phi_v * Vn
    
    flexure_dcr_x = inp.Mux / phi_Mn_x if phi_Mn_x > 0 else 999.0
    flexure_dcr_y = inp.Muy / phi_Mn_y if phi_Mn_y > 0 else 0.0
    total_flexure_dcr = flexure_dcr_x + flexure_dcr_y
    shear_dcr = inp.Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    # 3. Deflection calculation: delta = 5 * w * L^4 / (384 * E * Ix)
    w_N_per_mm = inp.service_w  # kN/m = N/mm
    delta_act = (5.0 * w_N_per_mm * (inp.L ** 4)) / (384.0 * E * Ix) if Ix > 0 else 0.0
    delta_allow = inp.L / inp.allowable_deflection_ratio if inp.allowable_deflection_ratio > 0 else 999.0
    deflection_dcr = delta_act / delta_allow if delta_allow > 0 else 0.0
    
    max_dcr = max(total_flexure_dcr, shear_dcr, deflection_dcr)
    is_safe = (max_dcr <= 1.0) and not compactness.is_slender
    
    status = "OK" if is_safe else "NG"
    summary = (f"[{status}] Steel Beam DCR={max_dcr:.3f} "
               f"(Flexure={total_flexure_dcr:.3f}, Shear={shear_dcr:.3f}, Deflection={deflection_dcr:.3f})")
    
    return SteelBeamResult(
        compactness=compactness,
        Mp_x=Mp_x,
        Lp=Lp,
        Lr=Lr,
        Mn_x=Mn_x,
        phi_b=phi_b,
        phi_Mn_x=phi_Mn_x,
        flexure_dcr_x=flexure_dcr_x,
        Mp_y=Mp_y,
        Mn_y=Mn_y,
        phi_Mn_y=phi_Mn_y,
        flexure_dcr_y=flexure_dcr_y,
        total_flexure_dcr=total_flexure_dcr,
        Cv=Cv,
        Vn=Vn,
        phi_v=phi_v,
        phi_Vn=phi_Vn,
        shear_dcr=shear_dcr,
        delta_act=delta_act,
        delta_allow=delta_allow,
        deflection_dcr=deflection_dcr,
        max_dcr=max_dcr,
        is_safe=is_safe,
        summary=summary
    )
