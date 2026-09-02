"""Aluminium Alloy Structural Design Engine (KDS 14 31 40).

Implements:
1. Aluminium Alloy Material Database (6061-T6, 6063-T6, 6082-T6, 5083-O/H112)
2. Heat-Affected Zone (HAZ) Strength Reduction (25mm from weld line)
3. Tension Member Design Strength (phi_t * Pn)
4. Column Buckling and Compression Member Design Strength (phi_c * Pn)
5. Beam Flexural Design Strength (phi_b * Mn) with Lateral Torsional Buckling (LTB)
6. Web Shear Design Strength (phi_v * Vn)
7. Combined Force (P-M) Interaction DCR
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional, Dict, Any


class AluAlloyType(str, Enum):
    A6061_T6 = "6061-T6"
    A6063_T6 = "6063-T6"
    A6082_T6 = "6082-T6"
    A5083_H112 = "5083-H112"
    A5083_O = "5083-O"


class AluSectionShape(str, Enum):
    I_SHAPE = "I_SHAPE"
    RECT_TUBE = "RECT_TUBE"
    CIRC_TUBE = "CIRC_TUBE"
    CHANNEL = "CHANNEL"
    ANGLE = "ANGLE"


@dataclass
class AluMaterialProp:
    """Mechanical properties of aluminium alloys (MPa)."""
    name: str
    Fty: float      # Tensile yield strength (MPa)
    Ftu: float      # Tensile ultimate strength (MPa)
    Fcy: float      # Compressive yield strength (MPa)
    Fsu: float      # Shear ultimate strength (MPa)
    E: float = 70000.0  # Modulus of elasticity (MPa)
    G: float = 26000.0  # Shear modulus (MPa)
    
    # HAZ (Heat-Affected Zone) properties
    Fty_haz: float = 0.0
    Ftu_haz: float = 0.0
    Fcy_haz: float = 0.0
    
    def __post_init__(self):
        if self.Fty_haz <= 0.0:
            self.Fty_haz = self.Fty * 0.65
        if self.Ftu_haz <= 0.0:
            self.Ftu_haz = self.Ftu * 0.65
        if self.Fcy_haz <= 0.0:
            self.Fcy_haz = self.Fcy * 0.65


ALU_MATERIAL_DB: Dict[AluAlloyType, AluMaterialProp] = {
    AluAlloyType.A6061_T6: AluMaterialProp(
        name="6061-T6",
        Fty=240.0,
        Ftu=260.0,
        Fcy=240.0,
        Fsu=150.0,
        Fty_haz=140.0,
        Ftu_haz=165.0,
        Fcy_haz=140.0,
    ),
    AluAlloyType.A6063_T6: AluMaterialProp(
        name="6063-T6",
        Fty=170.0,
        Ftu=205.0,
        Fcy=170.0,
        Fsu=110.0,
        Fty_haz=90.0,
        Ftu_haz=115.0,
        Fcy_haz=90.0,
    ),
    AluAlloyType.A6082_T6: AluMaterialProp(
        name="6082-T6",
        Fty=260.0,
        Ftu=310.0,
        Fcy=260.0,
        Fsu=170.0,
        Fty_haz=150.0,
        Ftu_haz=185.0,
        Fcy_haz=150.0,
    ),
    AluAlloyType.A5083_H112: AluMaterialProp(
        name="5083-H112",
        Fty=190.0,
        Ftu=290.0,
        Fcy=190.0,
        Fsu=170.0,
        Fty_haz=125.0,
        Ftu_haz=275.0,
        Fcy_haz=125.0,
    ),
    AluAlloyType.A5083_O: AluMaterialProp(
        name="5083-O",
        Fty=125.0,
        Ftu=275.0,
        Fcy=125.0,
        Fsu=160.0,
        Fty_haz=125.0,
        Ftu_haz=275.0,
        Fcy_haz=125.0,
    ),
}


@dataclass
class AluSectionInput:
    """Input parameters for aluminium member design."""
    alloy: AluAlloyType = AluAlloyType.A6061_T6
    shape: AluSectionShape = AluSectionShape.I_SHAPE
    
    # Section geometric properties
    Ag: float = 4500.0         # Gross cross-sectional area (mm2)
    An: Optional[float] = None # Net cross-sectional area (mm2) (defaults to Ag)
    Aw: float = 1800.0         # Web shear area (mm2)
    
    # Inertia & Section moduli
    Ix: float = 35000000.0     # Moment of inertia X (mm4)
    Iy: float = 12000000.0     # Moment of inertia Y (mm4)
    Sx: float = 350000.0       # Elastic section modulus X (mm3)
    Sy: float = 120000.0       # Elastic section modulus Y (mm3)
    Zx: float = 400000.0       # Plastic section modulus X (mm3)
    Zy: float = 160000.0       # Plastic section modulus Y (mm3)
    rx: float = 88.0           # Radius of gyration X (mm)
    ry: float = 51.6           # Radius of gyration Y (mm)
    J: float = 85000.0         # Torsional constant (mm4)
    Cw: float = 1500000000.0   # Warping constant (mm6)
    
    # Member length and boundary conditions
    Lx: float = 3000.0         # Unbraced length X (mm)
    Ly: float = 3000.0         # Unbraced length Y (mm)
    Lb: float = 3000.0         # Lateral unbraced length for LTB (mm)
    Kx: float = 1.0            # Effective length factor X
    Ky: float = 1.0            # Effective length factor Y
    
    # Welding & HAZ
    is_welded_in_haz: bool = False  # If True, HAZ strength reduction is applied
    
    # Factored design loads
    Pu: float = 150.0          # Factored axial tension (+) or compression (-) (kN)
    Mux: float = 25.0          # Factored moment X (kN·m)
    Muy: float = 0.0           # Factored moment Y (kN·m)
    Vu: float = 35.0           # Factored shear force (kN)


@dataclass
class AluDesignResult:
    """Comprehensive design results for aluminium member."""
    is_safe: bool
    max_dcr: float
    dcr_axial: float
    dcr_flexure_x: float
    dcr_flexure_y: float
    dcr_shear: float
    dcr_combined: float
    
    # Capacities (kN, kN·m)
    phi_Pt: float              # Design tensile strength (kN)
    phi_Pc: float              # Design compressive strength (kN)
    phi_Mnx: float             # Design flexural strength X (kN·m)
    phi_Mny: float             # Design flexural strength Y (kN·m)
    phi_Vn: float              # Design shear strength (kN)
    
    # Material applied
    Fty_used: float            # Applied tensile yield strength (MPa)
    Ftu_used: float            # Applied tensile ultimate strength (MPa)
    Fcy_used: float            # Applied compressive yield strength (MPa)
    khaz: float                # HAZ strength reduction factor
    
    # Buckling properties
    slenderness_max: float
    details: Dict[str, Any] = field(default_factory=dict)


def check_alu_member(input_data: AluSectionInput) -> AluDesignResult:
    """Check Aluminium Alloy Structural Member according to KDS 14 31 40."""
    mat = ALU_MATERIAL_DB[input_data.alloy]
    
    # 1. HAZ Strength Reduction Factor
    if input_data.is_welded_in_haz:
        Fty = mat.Fty_haz
        Ftu = mat.Ftu_haz
        Fcy = mat.Fcy_haz
        khaz = mat.Fty_haz / mat.Fty
    else:
        Fty = mat.Fty
        Ftu = mat.Ftu
        Fcy = mat.Fcy
        khaz = 1.0
        
    E = mat.E
    Ag = input_data.Ag
    An = input_data.An if input_data.An is not None else Ag
    Aw = input_data.Aw
    
    # 2. Tension Member Design Strength (phi_t * Pn)
    # phi_t = 0.95 for yielding, 0.85 for rupture (KDS 14 31 40)
    phi_ty = 0.95
    phi_tu = 0.85
    Pt_yield_N = phi_ty * Fty * Ag
    Pt_rupt_N = phi_tu * Ftu * An
    phi_Pt_N = min(Pt_yield_N, Pt_rupt_N)
    phi_Pt = phi_Pt_N / 1000.0
    
    # 3. Compression Member Design Strength (phi_c * Pc)
    # Slenderness ratios
    KL_r_x = (input_data.Kx * input_data.Lx) / input_data.rx if input_data.rx > 0 else 0.0
    KL_r_y = (input_data.Ky * input_data.Ly) / input_data.ry if input_data.ry > 0 else 0.0
    lambda_max = max(KL_r_x, KL_r_y)
    
    # Column buckling constants (KDS 14 31 40)
    # Bc = Fcy * (1 + (Fcy / 1000.0))
    # Dc = (Bc / 10.0) * sqrt(Bc / E)
    # Elastic buckling limit: lambda_2 = pi * sqrt(E / (1.2 * Fcy))
    Bc = Fcy * (1.0 + (Fcy / 1500.0))
    Dc = (Bc / 10.0) * math.sqrt(Bc / E)
    lambda_1 = (Bc - Fcy) / Dc if Dc > 0 else 0.0
    lambda_2 = math.pi * math.sqrt(E / (1.2 * Fcy)) if Fcy > 0 else 100.0
    
    if lambda_max <= lambda_1:
        Fcr = Fcy
    elif lambda_max < lambda_2:
        Fcr = max(0.0, Bc - Dc * lambda_max)
    else:
        Fcr = (math.pi ** 2) * E / (lambda_max ** 2) if lambda_max > 0 else Fcy
        
    phi_c = 0.85
    phi_Pc_N = phi_c * Fcr * Ag
    phi_Pc = phi_Pc_N / 1000.0
    
    # 4. Beam Flexural Strength (phi_b * Mn)
    # Strong axis (X)
    My_x_Nmm = Fty * input_data.Sx
    Mp_x_Nmm = min(Fty * input_data.Zx, 1.5 * My_x_Nmm)
    
    # Lateral-Torsional Buckling (LTB)
    Lb = input_data.Lb
    if Lb > 0 and input_data.Iy > 0 and input_data.J > 0:
        G = mat.G
        t1 = E * input_data.Iy * G * input_data.J
        t2 = ((math.pi * E / Lb) ** 2) * input_data.Iy * input_data.Cw
        Mcr_Nmm = (math.pi / Lb) * math.sqrt(max(0.0, t1 + t2))
        
        # Inelastic LTB transition when Mcr > My
        if Mcr_Nmm >= Mp_x_Nmm:
            Mn_x_Nmm = Mp_x_Nmm
        elif Mcr_Nmm > 0.5 * My_x_Nmm:
            # Inelastic buckling zone
            Mn_x_Nmm = min(Mp_x_Nmm, Mp_x_Nmm - (Mp_x_Nmm - 0.5 * My_x_Nmm) * (1.0 - Mcr_Nmm / Mp_x_Nmm))
        else:
            Mn_x_Nmm = Mcr_Nmm
    else:
        Mn_x_Nmm = Mp_x_Nmm
        
    phi_b = 0.85
    phi_Mnx = (phi_b * Mn_x_Nmm) / 1e6
    
    # Weak axis (Y)
    My_y_Nmm = Fty * input_data.Sy
    Mp_y_Nmm = min(Fty * input_data.Zy, 1.5 * My_y_Nmm)
    phi_Mny = (phi_b * Mp_y_Nmm) / 1e6
    
    # 5. Web Shear Strength (phi_v * Vn)
    phi_v = 0.85
    Vn_N = 0.60 * Fty * Aw
    phi_Vn = (phi_v * Vn_N) / 1000.0
    
    # 6. Demand-Capacity Ratios (DCR)
    Pu = input_data.Pu
    if Pu >= 0.0:  # Tension
        dcr_axial = Pu / phi_Pt if phi_Pt > 0 else 0.0
    else:          # Compression
        dcr_axial = abs(Pu) / phi_Pc if phi_Pc > 0 else 0.0
        
    dcr_flexure_x = input_data.Mux / phi_Mnx if phi_Mnx > 0 else 0.0
    dcr_flexure_y = input_data.Muy / phi_Mny if phi_Mny > 0 else 0.0
    dcr_shear = input_data.Vu / phi_Vn if phi_Vn > 0 else 0.0
    
    # Combined P-M interaction (KDS 14 31 40)
    dcr_combined = dcr_axial + dcr_flexure_x + dcr_flexure_y
    max_dcr = max(dcr_axial, dcr_flexure_x, dcr_flexure_y, dcr_shear, dcr_combined)
    is_safe = max_dcr <= 1.0
    
    return AluDesignResult(
        is_safe=is_safe,
        max_dcr=round(max_dcr, 4),
        dcr_axial=round(dcr_axial, 4),
        dcr_flexure_x=round(dcr_flexure_x, 4),
        dcr_flexure_y=round(dcr_flexure_y, 4),
        dcr_shear=round(dcr_shear, 4),
        dcr_combined=round(dcr_combined, 4),
        phi_Pt=round(phi_Pt, 2),
        phi_Pc=round(phi_Pc, 2),
        phi_Mnx=round(phi_Mnx, 2),
        phi_Mny=round(phi_Mny, 2),
        phi_Vn=round(phi_Vn, 2),
        Fty_used=Fty,
        Ftu_used=Ftu,
        Fcy_used=Fcy,
        khaz=round(khaz, 3),
        slenderness_max=round(lambda_max, 2),
        details={
            "Bc": round(Bc, 2),
            "Dc": round(Dc, 4),
            "lambda_1": round(lambda_1, 2),
            "lambda_2": round(lambda_2, 2),
            "Fcr": round(Fcr, 2),
        }
    )
