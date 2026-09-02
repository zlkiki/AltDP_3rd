"""RC Beam Complete Design Engine (KDS 14 20 00 / 20 / 22 / 30).

Provides full flexural (singly/doubly reinforced), shear, torsion,
shear-torsion interaction verification, Branson deflection, crack width evaluation,
and DCR evaluation for reinforced concrete beams.
"""

from dataclasses import dataclass, field
import math
from typing import Optional, Dict, Any

from src.engine.db.materials import (
    ConcreteMaterial,
    RebarMaterial,
    get_phi_flexure,
    get_phi_shear
)


@dataclass
class RCBeamInput:
    """RC Beam Geometry, Materials, Loading, and Serviceability Input Parameters."""
    name: str = "B1"
    b: float = 400.0           # mm (Section width bw)
    h: float = 600.0           # mm (Section total depth)
    cover: float = 50.0        # mm (Clear cover to tension rebar centroid)
    cover_prime: float = 50.0  # mm (Clear cover to compression rebar centroid)
    side_cover: float = 40.0   # mm (Clear cover to stirrup edge for torsion)
    
    # Tension Reinforcement (Bottom for positive moment, Top for negative)
    As: float = 1935.0         # mm2 (e.g., 5-D22 = 5 * 387 mm2)
    # Compression Reinforcement
    As_prime: float = 0.0      # mm2 (e.g., 2-D19 = 2 * 287 mm2)
    
    # Shear Stirrups (2 legs)
    Av: float = 142.6          # mm2 (e.g., 2-D10 = 2 * 71.3 mm2)
    s: float = 200.0           # mm (Stirrup spacing)
    
    # Factored Design Forces (Ultimate Limit State)
    Mu: float = 250.0          # kN*m (Design flexural moment)
    Vu: float = 150.0          # kN (Design shear force)
    Tu: float = 0.0            # kN*m (Design torsional moment)
    
    # Serviceability Forces & Parameters (KDS 14 20 30)
    Ma: float = 160.0          # kN*m (Service load maximum moment)
    span_length: float = 6000.0# mm (Beam clear span length L)
    sustained_ratio: float = 0.70 # Ratio of sustained load to Ma
    time_duration_months: int = 60 # Load duration (>= 60 months => xi = 2.0)
    allowable_deflection_ratio: float = 240.0 # L / 240
    w_lim: float = 0.3         # mm (Allowable crack width limit)
    num_tension_bars: int = 5  # Number of tension bars in outer layer
    
    # Materials
    concrete: ConcreteMaterial = field(default_factory=ConcreteMaterial)
    rebar: RebarMaterial = field(default_factory=RebarMaterial)
    rebar_stirrup: Optional[RebarMaterial] = None
    is_seismic: bool = False


@dataclass
class RCBeamResult:
    """RC Beam Design & Verification Output (Strength + Serviceability)."""
    # 1. Flexure (KDS 14 20 20)
    d: float                   # mm (Effective tension depth)
    d_prime: float             # mm (Effective compression depth)
    a: float                   # mm (Equivalent stress block depth)
    c: float                   # mm (Neutral axis depth)
    fs_prime: float            # MPa (Compression steel stress)
    is_top_yielding: bool      # True if compression steel yields
    et: float                  # Net tensile strain in extreme tension steel
    phi_b: float               # Flexural strength reduction factor
    Mn: float                  # kN*m (Nominal flexural capacity)
    phi_Mn: float              # kN*m (Design flexural capacity)
    flexure_dcr: float         # Mu / phi_Mn
    rho: float                 # As / (b * d)
    rho_min: float             # Minimum flexural rebar ratio
    rho_max: float             # Maximum rebar ratio limit (et >= 0.004)
    
    # 2. Shear (KDS 14 20 22)
    Vc: float                  # kN (Concrete nominal shear capacity)
    Vs: float                  # kN (Stirrup nominal shear capacity)
    Vs_max: float              # kN (Upper limit of Vs = 2/3 * sqrt(fck) * b * d)
    Vn: float                  # kN (Total nominal shear capacity)
    phi_v: float               # Shear reduction factor (0.75)
    phi_Vn: float              # kN (Design shear capacity)
    shear_dcr: float           # Vu / phi_Vn
    s_max: float               # mm (Maximum allowable stirrup spacing)
    Av_min: float              # mm2 (Minimum stirrup area per spacing s)
    
    # 3. Torsion & Interaction (KDS 14 20 22)
    Tcr: float                 # kN*m (Cracking torsional moment)
    Tth: float                 # kN*m (Threshold torsion limit = phi * Tcr / 4)
    is_torsion_ignored: bool   # True if Tu <= Tth
    Aoh: float                 # mm2 (Area enclosed by centerline of outermost closed stirrup)
    ph: float                  # mm (Perimeter of centerline of outermost closed stirrup)
    Ao: float                  # mm2 (Gross area enclosed by shear flow path = 0.85 * Aoh)
    At_over_s_req: float       # mm2/mm (Required single-leg torsion stirrup per unit length)
    Al_req: float              # mm2 (Required longitudinal torsional steel)
    Al_min: float              # mm2 (Minimum longitudinal torsional steel)
    Tn: float                  # kN*m (Nominal torsional capacity based on At/s)
    phi_Tn: float              # kN*m (Design torsional capacity)
    torsion_dcr: float         # Tu / phi_Tn
    combined_stress: float     # MPa (Combined shear-torsion shear stress)
    combined_limit: float      # MPa (Allowable upper limit on combined shear stress)
    combined_dcr: float        # Combined stress ratio
    
    # 4. Serviceability - Deflection & Cracking (KDS 14 20 30)
    Ig: float                  # cm4 (Gross moment of inertia)
    Mcr: float                 # kN*m (Cracking moment)
    Icr: float                 # cm4 (Cracked moment of inertia)
    Ie: float                  # cm4 (Branson effective moment of inertia)
    delta_elastic: float       # mm (Immediate elastic deflection)
    xi_factor: float           # Long-term multiplier time factor xi
    lambda_delta: float        # Long-term deflection multiplier
    delta_long: float          # mm (Long-term deflection)
    delta_total: float         # mm (Total deflection)
    delta_allowable: float     # mm (Allowable deflection limit)
    deflection_dcr: float      # delta_total / delta_allowable
    
    fs_service: float          # MPa (Service steel stress)
    crack_width: float         # mm (Estimated surface crack width)
    crack_dcr: float           # crack_width / w_lim
    
    # Overall Status
    is_safe: bool              # True if all DCR <= 1.0 and detailing limits satisfied
    summary: str


def design_rc_beam(inp: RCBeamInput) -> RCBeamResult:
    """Perform full KDS 14 20 00 structural capacity and serviceability check for an RC beam."""
    b = inp.b
    h = inp.h
    d = max(h - inp.cover, 1.0)
    d_prime = min(inp.cover_prime, d - 1.0)
    
    fck = inp.concrete.fck
    fy = inp.rebar.fy
    Es = inp.rebar.Es
    Ec = inp.concrete.Ec
    ecu = inp.concrete.ecu
    ey = inp.rebar.ey
    alpha1 = inp.concrete.alpha1
    beta1 = inp.concrete.beta1
    
    rebar_stirrup = inp.rebar_stirrup if inp.rebar_stirrup is not None else inp.rebar
    fyt = rebar_stirrup.fy
    
    # -------------------------------------------------------------
    # 1. Flexural Strength (Mn) - Singly & Doubly Reinforced
    # -------------------------------------------------------------
    As = max(inp.As, 0.0)
    As_prime = max(inp.As_prime, 0.0)
    
    if As_prime > 0.0 and As > 0.0:
        a_yield = (As * fy - As_prime * fy) / (alpha1 * fck * b)
        c_yield = a_yield / beta1 if beta1 > 0 else a_yield / 0.85
        eps_s_prime_yield = ecu * (c_yield - d_prime) / c_yield if c_yield > 0 else 0.0
        
        if eps_s_prime_yield >= ey and a_yield > 0:
            a = a_yield
            c = c_yield
            fs_prime = fy
            is_top_yielding = True
        else:
            A_quad = alpha1 * fck * beta1 * b
            B_quad = As_prime * Es * ecu - As * fy
            C_quad = - As_prime * Es * ecu * d_prime
            discriminant = max(B_quad ** 2 - 4.0 * A_quad * C_quad, 0.0)
            c = (-B_quad + math.sqrt(discriminant)) / (2.0 * A_quad) if A_quad > 0 else 1.0
            a = beta1 * c
            fs_prime = min(max(Es * ecu * (c - d_prime) / c, -fy), fy) if c > 0 else 0.0
            is_top_yielding = (abs(fs_prime) >= fy * 0.999)
    else:
        a = (As * fy) / (alpha1 * fck * b) if (alpha1 * fck * b) > 0 else 0.0
        c = a / beta1 if beta1 > 0 else a / 0.85
        fs_prime = 0.0
        is_top_yielding = False
        
    et = ecu * (d - c) / c if c > 0 else 0.05
    phi_b = get_phi_flexure(et, ey)
    
    if As_prime > 0.0 and c > 0:
        Cc = alpha1 * fck * a * b
        Cs = As_prime * fs_prime
        Mn_Nmm = (As * fy - Cs) * (d - 0.5 * a) + Cs * (d - d_prime)
    else:
        Mn_Nmm = As * fy * (d - 0.5 * a)
        
    Mn = max(Mn_Nmm / 1e6, 0.0)  # kN*m
    phi_Mn = phi_b * Mn
    flexure_dcr = inp.Mu / phi_Mn if phi_Mn > 0 else (0.0 if inp.Mu == 0 else 999.0)
    
    rho = As / (b * d) if (b * d) > 0 else 0.0
    rho_min = max(0.25 * math.sqrt(fck) / fy, 1.4 / fy)
    rho_max = 0.85 * beta1 * (fck / fy) * (ecu / (ecu + 0.004))
    
    # -------------------------------------------------------------
    # 2. Shear Strength (Vn) - KDS 14 20 22
    # -------------------------------------------------------------
    lambda_factor = inp.concrete.lambda_factor
    Vc_N = (1.0 / 6.0) * lambda_factor * math.sqrt(fck) * b * d
    Vc = Vc_N / 1e3  # kN
    
    Vs_N = (inp.Av * fyt * d) / inp.s if inp.s > 0 else 0.0
    Vs_max_N = (2.0 / 3.0) * math.sqrt(fck) * b * d
    Vs_N = min(Vs_N, Vs_max_N)
    Vs = Vs_N / 1e3
    Vs_max = Vs_max_N / 1e3
    
    Vn = Vc + Vs
    phi_v = get_phi_shear(inp.is_seismic)
    phi_Vn = phi_v * Vn
    shear_dcr = inp.Vu / phi_Vn if phi_Vn > 0 else (0.0 if inp.Vu == 0 else 999.0)
    
    if Vs > (1.0 / 3.0) * math.sqrt(fck) * b * d / 1e3:
        s_max = min(d / 4.0, 300.0)
    else:
        s_max = min(d / 2.0, 600.0)
        
    Av_min = max(0.0625 * math.sqrt(fck) * (b * inp.s) / fyt, 0.35 * (b * inp.s) / fyt) if inp.s > 0 else 0.0
    
    # -------------------------------------------------------------
    # 3. Torsion & Interaction (KDS 14 20 22)
    # -------------------------------------------------------------
    Acp = b * h
    pcp = 2.0 * (b + h)
    Tcr_Nmm = (1.0 / 3.0) * lambda_factor * math.sqrt(fck) * (Acp ** 2) / pcp
    Tcr = Tcr_Nmm / 1e6
    phi_t = 0.75
    Tth = phi_t * (Tcr / 4.0)
    is_torsion_ignored = (abs(inp.Tu) <= Tth)
    
    boh = max(b - 2.0 * inp.side_cover, 10.0)
    hoh = max(h - 2.0 * inp.side_cover, 10.0)
    Aoh = boh * hoh
    ph = 2.0 * (boh + hoh)
    Ao = 0.85 * Aoh
    
    if not is_torsion_ignored and abs(inp.Tu) > 0:
        Tu_abs = abs(inp.Tu)
        Tn_req_Nmm = (Tu_abs / phi_t) * 1e6
        At_over_s_req = Tn_req_Nmm / (2.0 * Ao * fyt * 1.0)
        Al_req = At_over_s_req * ph * (fyt / fy) * 1.0
        Al_min = max((0.42 * math.sqrt(fck) * Acp / fy) - (At_over_s_req * ph * (fyt / fy)), 0.0)
        
        At_prov = inp.Av / 2.0
        Tn_prov_Nmm = (2.0 * Ao * At_prov * fyt * 1.0) / inp.s if inp.s > 0 else 0.0
        Tn = Tn_prov_Nmm / 1e6
        phi_Tn = phi_t * Tn
        torsion_dcr = Tu_abs / phi_Tn if phi_Tn > 0 else 999.0
        
        vu = (inp.Vu * 1e3) / (b * d)
        tu = (Tu_abs * 1e6 * ph) / (1.7 * (Aoh ** 2))
        combined_stress = math.sqrt(vu ** 2 + tu ** 2)
        combined_limit = phi_v * ((Vc_N / (b * d)) + (2.0 / 3.0) * math.sqrt(fck))
        combined_dcr = combined_stress / combined_limit if combined_limit > 0 else 999.0
    else:
        At_over_s_req = 0.0
        Al_req = 0.0
        Al_min = 0.0
        Tn = 0.0
        phi_Tn = 0.0
        torsion_dcr = 0.0
        vu = (inp.Vu * 1e3) / (b * d)
        combined_stress = vu
        combined_limit = phi_v * ((Vc_N / (b * d)) + (2.0 / 3.0) * math.sqrt(fck))
        combined_dcr = shear_dcr
        
    # -------------------------------------------------------------
    # 4. Serviceability - Deflection & Crack (KDS 14 20 30)
    # -------------------------------------------------------------
    # 4.1 Branson Effective Moment of Inertia (Ie)
    Ig_mm4 = (b * (h ** 3)) / 12.0
    Ig = Ig_mm4 / 1e4  # cm4
    yt = h / 2.0
    fr = inp.concrete.f_cr  # MPa = 0.63 * lambda * sqrt(fck)
    Mcr_Nmm = (fr * Ig_mm4) / yt
    Mcr = Mcr_Nmm / 1e6  # kN*m
    
    # Cracked transformed section: kd
    n_ratio = Es / Ec
    # Solve 0.5 * b * (kd)^2 + (n-1)*As'* (kd - d') = n * As * (d - kd)
    # 0.5 * b * kd^2 + [n*As + (n-1)*As'] * kd - [n*As*d + (n-1)*As'*d'] = 0
    A_kd = 0.5 * b
    B_kd = n_ratio * As + max((n_ratio - 1.0) * As_prime, 0.0)
    C_kd = - (n_ratio * As * d + max((n_ratio - 1.0) * As_prime * d_prime, 0.0))
    disc_kd = max(B_kd ** 2 - 4.0 * A_kd * C_kd, 0.0)
    kd = (-B_kd + math.sqrt(disc_kd)) / (2.0 * A_kd) if A_kd > 0 else 0.3 * d
    
    # Cracked moment of inertia Icr
    Icr_mm4 = (b * (kd ** 3)) / 3.0 + n_ratio * As * ((d - kd) ** 2)
    if As_prime > 0 and kd > d_prime:
        Icr_mm4 += (n_ratio - 1.0) * As_prime * ((kd - d_prime) ** 2)
    Icr = Icr_mm4 / 1e4  # cm4
    
    Ma_abs = abs(inp.Ma)
    if Ma_abs <= Mcr or Mcr == 0:
        Ie_mm4 = Ig_mm4
    else:
        m_ratio = (Mcr / Ma_abs) ** 3
        Ie_mm4 = m_ratio * Ig_mm4 + (1.0 - m_ratio) * Icr_mm4
        Ie_mm4 = min(Ie_mm4, Ig_mm4)
        
    Ie = Ie_mm4 / 1e4  # cm4
    
    # 4.2 Immediate and Long-term Deflection
    L = inp.span_length
    # Elastic deflection: delta_i = 5 * Ma * L^2 / (48 * Ec * Ie) for simply supported beam
    delta_elastic = (5.0 * (Ma_abs * 1e6) * (L ** 2)) / (48.0 * Ec * Ie_mm4) if (Ec * Ie_mm4) > 0 else 0.0
    
    # Time factor xi for sustained load
    if inp.time_duration_months >= 60:
        xi_factor = 2.0
    elif inp.time_duration_months >= 12:
        xi_factor = 1.4
    elif inp.time_duration_months >= 6:
        xi_factor = 1.2
    elif inp.time_duration_months >= 3:
        xi_factor = 1.0
    else:
        xi_factor = 0.0
        
    rho_prime = As_prime / (b * d) if (b * d) > 0 else 0.0
    lambda_delta = xi_factor / (1.0 + 50.0 * rho_prime)
    
    delta_sustained_elastic = delta_elastic * inp.sustained_ratio
    delta_long = lambda_delta * delta_sustained_elastic
    delta_total = delta_elastic + delta_long
    
    delta_allowable = L / inp.allowable_deflection_ratio if inp.allowable_deflection_ratio > 0 else 25.0
    deflection_dcr = delta_total / delta_allowable if delta_allowable > 0 else 0.0
    
    # 4.3 Direct Crack Width Check (KDS 14 20 30)
    # Service steel stress fs = Ma / (As * (d - kd / 3))
    jd = d - kd / 3.0
    fs_service = (Ma_abs * 1e6) / (As * jd) if (As * jd) > 0 else 0.0
    fs_service = min(fs_service, 0.6 * fy)
    
    # dc: distance from extreme tension fiber to center of closest bar
    dc = inp.cover
    n_bars = max(inp.num_tension_bars, 2)
    A_eff = (2.0 * dc * b) / n_bars
    beta_crack = (h - kd) / (d - kd) if (d - kd) > 0 else 1.2
    
    # Gergely-Lutz / Frosch crack width equation (mm)
    # w = 1.08 * beta * (fs / Es) * (dc * A_eff)^(1/3)
    eps_s_service = fs_service / Es
    crack_width = 1.08 * beta_crack * eps_s_service * ((dc * A_eff) ** (1.0 / 3.0)) if (dc * A_eff) > 0 else 0.0
    crack_dcr = crack_width / inp.w_lim if inp.w_lim > 0 else 0.0
    
    # -------------------------------------------------------------
    # 5. Overall Safety & Summary
    # -------------------------------------------------------------
    max_dcr = max(flexure_dcr, shear_dcr, torsion_dcr, combined_dcr, deflection_dcr, crack_dcr)
    rebar_limits_ok = (rho >= rho_min) and (et >= 0.004) and (inp.s <= s_max * 1.001)
    
    is_safe = (max_dcr <= 1.0) and rebar_limits_ok
    status = "OK" if is_safe else "NG"
    
    summary = (
        f"[{status}] DCR_max: {max_dcr:.3f} | Flexure: {flexure_dcr:.3f}, Shear: {shear_dcr:.3f}, "
        f"Deflection: {deflection_dcr:.3f} (delta={delta_total:.1f}mm), Crack: {crack_dcr:.3f} (w={crack_width:.2f}mm)"
    )
    
    return RCBeamResult(
        d=d,
        d_prime=d_prime,
        a=a,
        c=c,
        fs_prime=fs_prime,
        is_top_yielding=is_top_yielding,
        et=et,
        phi_b=phi_b,
        Mn=Mn,
        phi_Mn=phi_Mn,
        flexure_dcr=flexure_dcr,
        rho=rho,
        rho_min=rho_min,
        rho_max=rho_max,
        Vc=Vc,
        Vs=Vs,
        Vs_max=Vs_max,
        Vn=Vn,
        phi_v=phi_v,
        phi_Vn=phi_Vn,
        shear_dcr=shear_dcr,
        s_max=s_max,
        Av_min=Av_min,
        Tcr=Tcr,
        Tth=Tth,
        is_torsion_ignored=is_torsion_ignored,
        Aoh=Aoh,
        ph=ph,
        Ao=Ao,
        At_over_s_req=At_over_s_req,
        Al_req=Al_req,
        Al_min=Al_min,
        Tn=Tn,
        phi_Tn=phi_Tn,
        torsion_dcr=torsion_dcr,
        combined_stress=combined_stress,
        combined_limit=combined_limit,
        combined_dcr=combined_dcr,
        Ig=Ig,
        Mcr=Mcr,
        Icr=Icr,
        Ie=Ie,
        delta_elastic=delta_elastic,
        xi_factor=xi_factor,
        lambda_delta=lambda_delta,
        delta_long=delta_long,
        delta_total=delta_total,
        delta_allowable=delta_allowable,
        deflection_dcr=deflection_dcr,
        fs_service=fs_service,
        crack_width=crack_width,
        crack_dcr=crack_dcr,
        is_safe=is_safe,
        summary=summary
    )
