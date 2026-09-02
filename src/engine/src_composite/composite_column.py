"""Composite Column Design Engine (KDS 14 31 30).

Implements:
1. Encased SRC (Steel Reinforced Concrete) Columns
2. Filled CFT (Concrete Filled Tube - Rectangular & Circular) Columns
3. Plastic Compressive Strength (Pno)
4. Effective Flexural Stiffness (EIeff)
5. Elastic Euler Buckling & Inelastic Column Buckling Design Strength (phi_c * Pn)
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional, Dict, Any


class SRCSectionType(str, Enum):
    ENCASED = "ENCASED"  # 매입형 SRC
    FILLED = "FILLED"    # 충전형 CFT


class CFTType(str, Enum):
    RECTANGULAR = "RECTANGULAR"  # 각형강관
    CIRCULAR = "CIRCULAR"        # 원형강관


@dataclass
class CFTColumnInput:
    """Input parameters for CFT (Concrete Filled Tube) column."""
    cft_type: CFTType = CFTType.RECTANGULAR
    
    # Dimensions (mm)
    # For Rectangular: B (width), H (height), t (wall thickness)
    # For Circular: D (outer diameter), t (wall thickness)
    B: float = 400.0
    H: float = 400.0
    D: float = 400.0
    t: float = 12.0
    
    # Material properties (MPa)
    fck: float = 30.0     # Concrete compressive strength
    Fy: float = 355.0     # Steel yield strength
    Es: float = 205000.0  # Steel elastic modulus
    Ec: Optional[float] = None  # Concrete elastic modulus (auto-calculated if None)
    
    # Reinforcing steel inside tube (optional)
    Asr: float = 0.0      # Area of longitudinal rebars (mm2)
    Fysr: float = 400.0   # Yield strength of rebars (MPa)
    Isr: float = 0.0      # Moment of inertia of rebars (mm4)
    
    # Unbraced length and effective length factor
    L: float = 4000.0     # Column length (mm)
    K: float = 1.0        # Effective length factor
    
    # Factored design loads
    Pu: float = 3000.0    # Factored axial compressive load (kN)
    Mux: float = 0.0      # Factored moment about X (kN·m)
    Muy: float = 0.0      # Factored moment about Y (kN·m)


@dataclass
class SRCColumnInput:
    """Input parameters for Encased SRC (Steel Reinforced Concrete) column."""
    # Concrete section dimensions (mm)
    B: float = 600.0      # Concrete section width
    H: float = 600.0      # Concrete section height
    cover: float = 50.0   # Clear concrete cover to rebars (mm)
    
    # Structural steel core (H-Beam / Built-up)
    As: float = 11980.0   # Steel section area (mm2) (e.g. H-300x300x10x15)
    Is_x: float = 204000000.0  # Steel moment of inertia X (mm4)
    Is_y: float = 67500000.0   # Steel moment of inertia Y (mm4)
    Fy: float = 355.0     # Steel yield strength (MPa)
    Es: float = 205000.0  # Steel elastic modulus (MPa)
    
    # Rebar cage
    num_rebars: int = 8
    rebar_dia: float = 22.0  # mm (D22)
    rebar_dist_x: float = 500.0  # Outer rebar distance X (mm)
    rebar_dist_y: float = 500.0  # Outer rebar distance Y (mm)
    Fysr: float = 400.0   # Rebar yield strength (MPa)
    
    # Concrete material
    fck: float = 30.0     # Concrete compressive strength (MPa)
    Ec: Optional[float] = None
    
    # Column unbraced length
    L: float = 4000.0     # mm
    K: float = 1.0
    
    # Factored design loads
    Pu: float = 4000.0    # kN
    Mux: float = 0.0      # kN·m
    Muy: float = 0.0      # kN·m


@dataclass
class CompositeColumnResult:
    """Design check results for composite column."""
    is_safe: bool
    dcr_axial: float
    Pno: float            # Plastic compression strength (kN)
    EI_eff_x: float       # Effective flexural stiffness X (N·mm2)
    EI_eff_y: float       # Effective flexural stiffness Y (N·mm2)
    Pe_x: float           # Elastic buckling load X (kN)
    Pe_y: float           # Elastic buckling load Y (kN)
    Pn: float             # Nominal compressive strength (kN)
    phi_Pn: float         # Design compressive strength (kN) (phi_c = 0.75)
    
    # Section properties
    Ag: float             # Total gross area (mm2)
    As: float             # Steel area (mm2)
    Ac: float             # Net concrete area (mm2)
    Asr: float            # Rebar area (mm2)
    steel_ratio: float    # As / Ag (%)
    steel_ratio_ok: bool = True
    
    # Slenderness & Limits
    is_compact: bool = True
    slenderness_ok: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


def _calc_concrete_ec(fck: float) -> float:
    """Calculate concrete modulus of elasticity according to KDS 14 20 10."""
    fcu = fck + 4.0 if fck <= 40.0 else fck + 6.0
    return 8500.0 * (fcu ** (1.0 / 3.0))


def check_cft_column(input_data: CFTColumnInput) -> CompositeColumnResult:
    """Check CFT (Concrete Filled Tube) column according to KDS 14 31 30."""
    Ec = input_data.Ec if input_data.Ec is not None else _calc_concrete_ec(input_data.fck)
    Es = input_data.Es
    Fy = input_data.Fy
    fck = input_data.fck
    t = input_data.t
    
    if input_data.cft_type == CFTType.RECTANGULAR:
        B = input_data.B
        H = input_data.H
        Ag = B * H
        
        # Inner concrete dimensions
        Bi = max(0.0, B - 2.0 * t)
        Hi = max(0.0, H - 2.0 * t)
        Ac = Bi * Hi - input_data.Asr
        As = Ag - (Bi * Hi)
        
        # Moment of inertias
        Is_x = (B * (H ** 3) - Bi * (Hi ** 3)) / 12.0
        Is_y = (H * (B ** 3) - Hi * (Bi ** 3)) / 12.0
        Ic_x = (Bi * (Hi ** 3)) / 12.0
        Ic_y = (Hi * (Bi ** 3)) / 12.0
        
        # Slenderness limits (KDS 14 31 30)
        # Compact limit: b/t <= 2.26 * sqrt(E/Fy)
        b_clear = max(Bi, Hi)
        limit_compact = 2.26 * math.sqrt(Es / Fy)
        actual_bt = b_clear / t
        is_compact = actual_bt <= limit_compact
        slenderness_ok = actual_bt <= 5.00 * math.sqrt(Es / Fy)
        
        # Strength coefficient C2 = 0.85 for rectangular
        C2 = 0.85
    else:  # CIRCULAR
        D = input_data.D
        Ag = math.pi * (D ** 2) / 4.0
        Di = max(0.0, D - 2.0 * t)
        Ac = math.pi * (Di ** 2) / 4.0 - input_data.Asr
        As = Ag - (math.pi * (Di ** 2) / 4.0)
        
        Is_x = math.pi * (D ** 4 - Di ** 4) / 64.0
        Is_y = Is_x
        Ic_x = math.pi * (Di ** 4) / 64.0
        Ic_y = Ic_x
        
        # Circular limit: D/t <= 0.15 * E / Fy
        limit_compact = 0.15 * (Es / Fy)
        actual_dt = D / t
        is_compact = actual_dt <= limit_compact
        slenderness_ok = actual_dt <= 0.31 * (Es / Fy)
        
        # Strength coefficient C2 = 0.95 for circular (confinement effect)
        C2 = 0.95

    Asr = input_data.Asr
    Fysr = input_data.Fysr
    
    # 1. Steel ratio check (As / Ag >= 1%)
    steel_ratio = (As / Ag) * 100.0
    steel_ratio_ok = steel_ratio >= 1.0
    
    # 2. Plastic Compressive Strength Pno (N -> kN)
    # Pno = Fy * As + Fysr * Asr + C2 * fck * Ac
    Pno_N = Fy * As + Fysr * Asr + C2 * fck * Ac
    Pno = Pno_N / 1000.0
    
    # 3. Effective Flexural Stiffness EI_eff
    # C1 = 0.1 + 2 * (As / (As + Ac)) <= 0.3
    C1 = min(0.30, 0.10 + 2.0 * (As / (As + Ac)))
    
    EI_eff_x = Es * Is_x + Es * input_data.Isr + C1 * Ec * Ic_x
    EI_eff_y = Es * Is_y + Es * input_data.Isr + C1 * Ec * Ic_y
    
    # 4. Elastic Euler Buckling Load Pe
    KL = input_data.K * input_data.L
    Pe_x_N = (math.pi ** 2) * EI_eff_x / (KL ** 2) if KL > 0 else float('inf')
    Pe_y_N = (math.pi ** 2) * EI_eff_y / (KL ** 2) if KL > 0 else float('inf')
    Pe_x = Pe_x_N / 1000.0
    Pe_y = Pe_y_N / 1000.0
    Pe_min_N = min(Pe_x_N, Pe_y_N)
    
    # 5. Nominal Compressive Strength Pn (KDS 14 31 30)
    lambda_c_sq = Pno_N / Pe_min_N if Pe_min_N > 0 else 0.0
    if lambda_c_sq <= 2.25:
        Pn_N = Pno_N * (0.658 ** lambda_c_sq)
    else:
        Pn_N = 0.877 * Pe_min_N
        
    Pn = Pn_N / 1000.0
    phi_c = 0.75
    phi_Pn = phi_c * Pn
    
    # DCR
    dcr_axial = input_data.Pu / phi_Pn if phi_Pn > 0 else 999.0
    is_safe = dcr_axial <= 1.0 and steel_ratio_ok and slenderness_ok
    
    return CompositeColumnResult(
        is_safe=is_safe,
        dcr_axial=round(dcr_axial, 4),
        Pno=round(Pno, 2),
        EI_eff_x=round(EI_eff_x, 2),
        EI_eff_y=round(EI_eff_y, 2),
        Pe_x=round(Pe_x, 2),
        Pe_y=round(Pe_y, 2),
        Pn=round(Pn, 2),
        phi_Pn=round(phi_Pn, 2),
        Ag=round(Ag, 2),
        As=round(As, 2),
        Ac=round(Ac, 2),
        Asr=round(Asr, 2),
        steel_ratio=round(steel_ratio, 2),
        steel_ratio_ok=steel_ratio_ok,
        is_compact=is_compact,
        slenderness_ok=slenderness_ok,
        details={
            "C1": round(C1, 4),
            "C2": C2,
            "Ec": round(Ec, 1),
            "steel_ratio_ok": steel_ratio_ok,
            "lambda_c_sq": round(lambda_c_sq, 4),
        }
    )


def check_src_column(input_data: SRCColumnInput) -> CompositeColumnResult:
    """Check Encased SRC (Steel Reinforced Concrete) column according to KDS 14 31 30."""
    Ec = input_data.Ec if input_data.Ec is not None else _calc_concrete_ec(input_data.fck)
    Es = input_data.Es
    Fy = input_data.Fy
    fck = input_data.fck
    
    B = input_data.B
    H = input_data.H
    Ag = B * H
    
    # Rebars
    single_bar_area = math.pi * (input_data.rebar_dia ** 2) / 4.0
    Asr = input_data.num_rebars * single_bar_area
    Fysr = input_data.Fysr
    
    # Rebar moment of inertia
    # Simplified rebar centroid placement at half distances
    dx = input_data.rebar_dist_x / 2.0
    dy = input_data.rebar_dist_y / 2.0
    Isr_x = Asr * (dy ** 2) / 2.0
    Isr_y = Asr * (dx ** 2) / 2.0
    
    As = input_data.As
    Ac = Ag - As - Asr
    
    # Gross concrete inertia
    Ig_x = (B * (H ** 3)) / 12.0
    Ig_y = (H * (B ** 3)) / 12.0
    Ic_x = Ig_x - input_data.Is_x - Isr_x
    Ic_y = Ig_y - input_data.Is_y - Isr_y
    
    # 1. Steel ratio & Rebar ratio limits
    steel_ratio = (As / Ag) * 100.0
    rebar_ratio = (Asr / Ag) * 100.0
    steel_ratio_ok = steel_ratio >= 1.0
    rebar_ratio_ok = rebar_ratio >= 0.4
    
    # 2. Plastic compressive strength Pno
    # Pno = Fy * As + Fysr * Asr + 0.85 * fck * Ac
    Pno_N = Fy * As + Fysr * Asr + 0.85 * fck * Ac
    Pno = Pno_N / 1000.0
    
    # 3. Effective Flexural Stiffness EI_eff
    C1 = min(0.30, 0.10 + 2.0 * (As / (As + Ac)))
    EI_eff_x = Es * input_data.Is_x + Es * Isr_x + C1 * Ec * Ic_x
    EI_eff_y = Es * input_data.Is_y + Es * Isr_y + C1 * Ec * Ic_y
    
    # 4. Elastic Euler Buckling Load Pe
    KL = input_data.K * input_data.L
    Pe_x_N = (math.pi ** 2) * EI_eff_x / (KL ** 2) if KL > 0 else float('inf')
    Pe_y_N = (math.pi ** 2) * EI_eff_y / (KL ** 2) if KL > 0 else float('inf')
    Pe_x = Pe_x_N / 1000.0
    Pe_y = Pe_y_N / 1000.0
    Pe_min_N = min(Pe_x_N, Pe_y_N)
    
    # 5. Nominal Compressive Strength Pn
    lambda_c_sq = Pno_N / Pe_min_N if Pe_min_N > 0 else 0.0
    if lambda_c_sq <= 2.25:
        Pn_N = Pno_N * (0.658 ** lambda_c_sq)
    else:
        Pn_N = 0.877 * Pe_min_N
        
    Pn = Pn_N / 1000.0
    phi_c = 0.75
    phi_Pn = phi_c * Pn
    
    dcr_axial = input_data.Pu / phi_Pn if phi_Pn > 0 else 999.0
    is_safe = dcr_axial <= 1.0 and steel_ratio_ok and rebar_ratio_ok
    
    return CompositeColumnResult(
        is_safe=is_safe,
        dcr_axial=round(dcr_axial, 4),
        Pno=round(Pno, 2),
        EI_eff_x=round(EI_eff_x, 2),
        EI_eff_y=round(EI_eff_y, 2),
        Pe_x=round(Pe_x, 2),
        Pe_y=round(Pe_y, 2),
        Pn=round(Pn, 2),
        phi_Pn=round(phi_Pn, 2),
        Ag=round(Ag, 2),
        As=round(As, 2),
        Ac=round(Ac, 2),
        Asr=round(Asr, 2),
        steel_ratio=round(steel_ratio, 2),
        steel_ratio_ok=steel_ratio_ok,
        is_compact=True,
        slenderness_ok=True,
        details={
            "C1": round(C1, 4),
            "Ec": round(Ec, 1),
            "rebar_ratio": round(rebar_ratio, 2),
            "steel_ratio_ok": steel_ratio_ok,
            "rebar_ratio_ok": rebar_ratio_ok,
            "lambda_c_sq": round(lambda_c_sq, 4),
        }
    )
