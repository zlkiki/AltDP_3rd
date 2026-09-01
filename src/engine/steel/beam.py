"""Steel Beam Design Module (KDS 14 31 10 / AISC 360 LRFD) for AltDP_3rd.

Calculates section compactness, lateral-torsional buckling (LTB), flexural capacity (phi*Mn),
and shear capacity (phi*Vn) for I- and H-shaped steel members.
"""

from dataclasses import dataclass, field
import math

from src.engine.db.materials import SteelMaterial


@dataclass
class SteelBeamInput:
    """Steel Beam Geometry and Design Loading Parameters."""
    name: str = "SB1"
    
    # H-Section Dimensions (mm)
    H: float = 400.0           # Total height
    B: float = 200.0           # Flange width
    tw: float = 8.0            # Web thickness
    tf: float = 13.0           # Flange thickness
    r: float = 16.0            # Fillet radius
    
    # Member Length & Unbraced Length (mm)
    L: float = 6000.0          # Total span length
    Lb: float = 3000.0         # Lateral unbraced length
    Cb: float = 1.0            # Moment gradient factor
    
    # Factored Design Forces
    Mu: float = 180.0          # kN*m (Design flexural moment)
    Vu: float = 120.0          # kN (Design shear force)
    
    material: SteelMaterial = field(default_factory=lambda: SteelMaterial(name="SS275", Fy=275.0, Fu=410.0, E=205000.0))


@dataclass
class SteelBeamResult:
    """Steel Beam Design Verification Output."""
    is_flange_compact: bool
    is_web_compact: bool
    
    Mp: float                  # kN*m (Plastic moment capacity)
    Lp: float                  # mm (Limiting unbraced length for plastic flexure)
    Lr: float                  # mm (Limiting unbraced length for inelastic LTB)
    Mn: float                  # kN*m (Nominal flexural capacity)
    phi_b: float               # 0.90
    phi_Mn: float              # kN*m (Design flexural capacity)
    flexure_dcr: float         # Mu / phi_Mn
    
    Vn: float                  # kN (Nominal shear capacity)
    phi_v: float               # 0.90 (or 1.0 for specific KDS limits)
    phi_Vn: float              # kN (Design shear capacity)
    shear_dcr: float           # Vu / phi_Vn
    
    is_safe: bool
    summary: str


def design_steel_beam(inp: SteelBeamInput) -> SteelBeamResult:
    """Evaluate KDS 14 31 10 structural capacity for a steel H-beam."""
    Fy = inp.material.Fy
    E = inp.material.E
    G = inp.material.G
    
    H = inp.H
    B = inp.B
    tw = inp.tw
    tf = inp.tf
    h_web = H - 2.0 * tf
    
    # 1. Section Compactness (KDS 14 31 10 Table 4.1-1)
    # Flange slenderness: lambda_f = (B/2) / tf
    lambda_f = (B / 2.0) / tf
    lambda_pf = 0.38 * math.sqrt(E / Fy)
    is_flange_compact = (lambda_f <= lambda_pf)
    
    # Web slenderness: lambda_w = h_web / tw
    lambda_w = h_web / tw
    lambda_pw = 3.76 * math.sqrt(E / Fy)
    is_web_compact = (lambda_w <= lambda_pw)
    
    # Section Moduli Calculation (Approximation)
    # Area
    Af = B * tf
    Aw = h_web * tw
    Ag = 2.0 * Af + Aw
    
    # Ix & Iy
    Ix = (B * (H**3) - (B - tw) * (h_web**3)) / 12.0
    Iy = 2.0 * (tf * (B**3)) / 12.0 + (h_web * (tw**3)) / 12.0
    
    Sx = Ix / (H / 2.0)
    # Plastic Section Modulus Zx
    Zx = 2.0 * (B * tf * (H / 2.0 - tf / 2.0)) + tw * (h_web / 2.0) ** 2
    
    ry = math.sqrt(Iy / Ag) if Ag > 0 else 1.0
    ho = H - tf
    # Effective radius of gyration for LTB: rts = sqrt(Iy * ho / (2 * Sx))
    rts = math.sqrt((Iy * ho) / (2.0 * Sx)) if Sx > 0 else ry
    
    # Torsional constant J & Warping constant Cw
    J = (2.0 * B * (tf**3) + h_web * (tw**3)) / 3.0
    Cw = (Iy * (ho**2)) / 4.0
    
    # 2. Flexural Strength (Mn) & Lateral-Torsional Buckling (LTB)
    Mp_Nmm = Fy * Zx
    Mp = Mp_Nmm / 1e6  # kN*m
    
    # Lp = 1.76 * ry * sqrt(E / Fy)
    Lp = 1.76 * ry * math.sqrt(E / Fy)
    
    # Lr = 1.95 * rts * (E / (0.7*Fy)) * sqrt(J/(Sx*ho) + sqrt((J/(Sx*ho))^2 + 6.76*(0.7*Fy/E)^2))
    factor = 0.7 * Fy / E
    term1 = J / (Sx * ho) if (Sx * ho) > 0 else 0.001
    Lr = 1.95 * rts * (1.0 / factor) * math.sqrt(term1 + math.sqrt(term1**2 + 6.76 * (factor**2)))
    
    Lb = inp.Lb
    Cb = inp.Cb
    
    if Lb <= Lp:
        Mn = Mp
    elif Lb <= Lr:
        Mn = Cb * (Mp - (Mp - 0.7 * Fy * Sx / 1e6) * ((Lb - Lp) / (Lr - Lp)))
        Mn = min(Mn, Mp)
    else:
        # Elastic LTB: Fcr = Cb * pi^2 * E / (Lb/rts)^2 * sqrt(1 + 0.078 * J/(Sx*ho) * (Lb/rts)^2)
        slenderness = Lb / rts
        Fcr = (Cb * (math.pi ** 2) * E) / (slenderness ** 2) * math.sqrt(1.0 + 0.078 * (J / (Sx * ho)) * (slenderness ** 2))
        Mn = min((Fcr * Sx) / 1e6, Mp)
        
    phi_b = 0.90
    phi_Mn = phi_b * Mn
    flexure_dcr = inp.Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 3. Shear Strength (Vn)
    # Aw = d * tw
    Cv = 1.0  # Compact web under KDS limits
    Vn_N = 0.60 * Fy * H * tw * Cv
    Vn = Vn_N / 1e3  # kN
    phi_v = 0.90
    phi_Vn = phi_v * Vn
    shear_dcr = inp.Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    max_dcr = max(flexure_dcr, shear_dcr)
    is_safe = (max_dcr <= 1.0) and is_flange_compact and is_web_compact
    
    status = "OK" if is_safe else "NG"
    summary = f"[{status}] Steel Beam DCR: {flexure_dcr:.3f} (phi_Mn={phi_Mn:.1f} kN*m, phi_Vn={phi_Vn:.1f} kN, Lb={Lb:.0f}mm)"
    
    return SteelBeamResult(
        is_flange_compact=is_flange_compact,
        is_web_compact=is_web_compact,
        Mp=Mp,
        Lp=Lp,
        Lr=Lr,
        Mn=Mn,
        phi_b=phi_b,
        phi_Mn=phi_Mn,
        flexure_dcr=flexure_dcr,
        Vn=Vn,
        phi_v=phi_v,
        phi_Vn=phi_Vn,
        shear_dcr=shear_dcr,
        is_safe=is_safe,
        summary=summary
    )
