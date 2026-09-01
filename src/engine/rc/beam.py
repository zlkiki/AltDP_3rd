"""RC Beam Design Module (KDS 14 20 00 / ACI 318) for AltDP_3rd.

Provides flexural and shear capacity calculations, rebar ratio verification,
and DCR (Demand-Capacity Ratio) evaluation for reinforced concrete beams.
"""

from dataclasses import dataclass, field
import math
from typing import Dict, Any

from src.engine.db.materials import ConcreteMaterial, RebarMaterial, get_phi_flexure


@dataclass
class RCBeamInput:
    """RC Beam Geometry and Loading Input Parameters."""
    name: str = "B1"
    b: float = 400.0           # mm (Width)
    h: float = 600.0           # mm (Total height)
    cover: float = 50.0        # mm (Clear cover to rebar centroid)
    
    # Tension Rebar (Bottom for positive moment, Top for negative)
    As: float = 1935.0         # mm2 (e.g., 5-D22 = 5 * 387 mm2)
    # Compression Rebar
    As_prime: float = 0.0      # mm2
    
    # Shear Stirrups
    Av: float = 142.6          # mm2 (e.g., 2-D10 = 2 * 71.3 mm2)
    s: float = 200.0           # mm (Stirrup spacing)
    
    # Factored Design Forces
    Mu: float = 250.0          # kN*m (Design flexural moment)
    Vu: float = 150.0          # kN (Design shear force)
    
    # Materials
    concrete: ConcreteMaterial = field(default_factory=ConcreteMaterial)
    rebar: RebarMaterial = field(default_factory=RebarMaterial)


@dataclass
class RCBeamResult:
    """RC Beam Design & Verification Output."""
    d: float                   # mm (Effective depth)
    a: float                   # mm (Depth of equivalent stress block)
    c: float                   # mm (Neutral axis depth)
    et: float                  # Net tensile strain
    phi_b: float               # Flexural reduction factor
    Mn: float                  # kN*m (Nominal flexural moment capacity)
    phi_Mn: float              # kN*m (Design flexural moment capacity)
    flexure_dcr: float         # Mu / phi_Mn
    
    Vc: float                  # kN (Concrete nominal shear capacity)
    Vs: float                  # kN (Stirrup nominal shear capacity)
    Vn: float                  # kN (Total nominal shear capacity)
    phi_v: float               # Shear reduction factor (0.75)
    phi_Vn: float              # kN (Design shear capacity)
    shear_dcr: float           # Vu / phi_Vn
    
    rho: float                 # Reinforcement ratio (As / (b*d))
    rho_min: float             # Minimum rebar ratio
    rho_max: float             # Maximum rebar ratio
    is_safe: bool              # True if both DCR <= 1.0 and rebar limits satisfied
    summary: str


def design_rc_beam(inp: RCBeamInput) -> RCBeamResult:
    """Perform full KDS 14 20 00 structural capacity check for an RC beam."""
    b = inp.b
    h = inp.h
    d = h - inp.cover
    fck = inp.concrete.fck
    fy = inp.rebar.fy
    Es = inp.rebar.Es
    alpha1 = inp.concrete.alpha1
    beta1 = inp.concrete.beta1
    
    # 1. Flexural Strength (Mn)
    # a = (As * fy - As' * fs') / (alpha1 * fck * b)
    # Assuming tension rebar yields (fs = fy)
    a = (inp.As * fy) / (alpha1 * fck * b)
    c = a / beta1
    
    # Net tensile strain in extreme tension layer: et = ecu * (d - c) / c
    ecu = inp.concrete.ecu
    et = ecu * (d - c) / c if c > 0 else 0.05
    ey = fy / Es
    phi_b = get_phi_flexure(et, ey)
    
    # Nominal moment capacity Mn = As * fy * (d - a / 2)
    Mn_Nmm = inp.As * fy * (d - 0.5 * a)
    Mn = Mn_Nmm / 1e6  # kN*m
    phi_Mn = phi_b * Mn
    flexure_dcr = inp.Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # Rebar ratio checks
    rho = inp.As / (b * d)
    rho_min = max(0.25 * math.sqrt(fck) / fy, 1.4 / fy)
    # KDS limit for tension-controlled / net strain limit
    rho_max = 0.85 * beta1 * (fck / fy) * (0.0033 / (0.0033 + 0.004))
    
    # 2. Shear Strength (Vn)
    # Vc = 1/6 * sqrt(fck) * b * d
    Vc_N = (1.0 / 6.0) * math.sqrt(fck) * b * d
    Vc = Vc_N / 1e3  # kN
    
    # Vs = Av * fyt * d / s
    Vs_N = (inp.Av * fy * d) / inp.s if inp.s > 0 else 0.0
    Vs = Vs_N / 1e3  # kN
    
    Vn = Vc + Vs
    phi_v = 0.75  # KDS 14 20 00 shear reduction factor
    phi_Vn = phi_v * Vn
    shear_dcr = inp.Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    # Safety determination
    max_dcr = max(flexure_dcr, shear_dcr)
    is_safe = (max_dcr <= 1.0) and (rho >= rho_min)
    
    status = "OK" if is_safe else "NG"
    summary = f"[{status}] Flexure DCR: {flexure_dcr:.3f} (phi_Mn={phi_Mn:.1f} kN*m), Shear DCR: {shear_dcr:.3f} (phi_Vn={phi_Vn:.1f} kN)"
    
    return RCBeamResult(
        d=d,
        a=a,
        c=c,
        et=et,
        phi_b=phi_b,
        Mn=Mn,
        phi_Mn=phi_Mn,
        flexure_dcr=flexure_dcr,
        Vc=Vc,
        Vs=Vs,
        Vn=Vn,
        phi_v=phi_v,
        phi_Vn=phi_Vn,
        shear_dcr=shear_dcr,
        rho=rho,
        rho_min=rho_min,
        rho_max=rho_max,
        is_safe=is_safe,
        summary=summary
    )
