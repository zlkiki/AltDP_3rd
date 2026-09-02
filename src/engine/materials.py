"""KDS Standard Material Specifications for AltDP_3rd.

Follows KDS 14 20 10 (Concrete), KDS 14 31 10 (Structural Steel), and KDS 14 20 00.
"""

from dataclasses import dataclass, field
import math
from typing import Optional, Dict


@dataclass
class ConcreteMaterial:
    """KDS 14 20 10 Concrete Material Specification."""
    name: str = "C24"
    fck: float = 24.0          # MPa (Specified compressive strength)
    unit_weight: float = 23.5   # kN/m3
    ecu: float = 0.0033        # Ultimate compressive strain
    is_lightweight: bool = False
    lambda_factor: float = 1.0  # Lightweight concrete factor (1.0 for normal weight)

    @property
    def Ec(self) -> float:
        """Modulus of elasticity (KDS 14 20 10: Ec = 8500 * (fcu)^(1/3)).
        
        fcu = fck + 4.0 if fck <= 40 else fck + 6.0
        """
        fcu = self.fck + 4.0 if self.fck <= 40.0 else self.fck + 6.0
        return 8500.0 * (fcu ** (1.0 / 3.0))

    @property
    def alpha1(self) -> float:
        """Equivalent rectangular stress block intensity factor (alpha1).
        
        alpha1 = 0.85 (fck <= 40 MPa)
        alpha1 = max(0.65, 0.85 - 0.0015 * (fck - 40)) (fck > 40 MPa)
        """
        if self.fck <= 40.0:
            return 0.85
        return max(0.65, 0.85 - 0.0015 * (self.fck - 40.0))

    @property
    def beta1(self) -> float:
        """Equivalent rectangular stress block depth factor (beta1).
        
        beta1 = 0.80 (or 0.85 for standard) with reduction for high strength.
        KDS 14 20 20: beta1 = max(0.65, 0.80 - 0.0025 * (fck - 40)) for fck > 40 MPa
        or traditional 0.85 - 0.007 * (fck - 28)
        """
        if self.fck <= 28.0:
            return 0.85
        return max(0.65, 0.85 - 0.007 * (self.fck - 28.0))

    @property
    def f_cr(self) -> float:
        """Modulus of rupture for cracking moment fr = 0.63 * lambda * sqrt(fck) (MPa)."""
        return 0.63 * self.lambda_factor * math.sqrt(self.fck)


@dataclass
class RebarMaterial:
    """KDS 14 20 00 Reinforcing Steel Material Specification."""
    name: str = "SD400"
    fy: float = 400.0          # MPa (Yield strength)
    fu: float = 560.0          # MPa (Tensile strength)
    Es: float = 200000.0       # MPa (Modulus of elasticity)

    @property
    def ey(self) -> float:
        """Yield strain ey = fy / Es."""
        return self.fy / self.Es


# Korean Structural Steel Standard Strengths (KDS 14 31 10 Table)
STEEL_STANDARDS_DB: Dict[str, Dict[str, float]] = {
    "SS275": {"Fy_base": 275.0, "Fu": 410.0},
    "SM355": {"Fy_base": 355.0, "Fu": 490.0},
    "SM460": {"Fy_base": 460.0, "Fu": 550.0},
    "SHN275": {"Fy_base": 275.0, "Fu": 410.0},
    "SHN355": {"Fy_base": 355.0, "Fu": 490.0},
    "SHN460": {"Fy_base": 460.0, "Fu": 550.0},
    "SN275": {"Fy_base": 275.0, "Fu": 410.0},
    "SN355": {"Fy_base": 355.0, "Fu": 490.0},
    "SS400": {"Fy_base": 235.0, "Fu": 400.0},
    "SM490": {"Fy_base": 315.0, "Fu": 490.0},
}


@dataclass
class SteelMaterial:
    """KDS 14 31 10 Structural Steel Material Specification."""
    name: str = "SM355"
    Fy: float = 355.0          # MPa (Yield strength)
    Fu: float = 490.0          # MPa (Tensile strength)
    E: float = 205000.0        # MPa (Modulus of elasticity)
    nu: float = 0.30           # Poisson's ratio
    thickness: float = 12.0    # mm (Element thickness for strength reduction)

    def __post_init__(self):
        # Auto-lookup standard grade if name matches DB
        if self.name.upper() in STEEL_STANDARDS_DB and self.Fy == 355.0 and self.name.upper() != "SM355":
            entry = STEEL_STANDARDS_DB[self.name.upper()]
            self.Fy = entry["Fy_base"]
            self.Fu = entry["Fu"]

    @property
    def Fy_design(self) -> float:
        """Design yield strength considering element thickness reduction (KDS 14 31 10).
        
        For t <= 16mm: Fy
        For 16 < t <= 40mm: Fy - 10 MPa (for higher grades)
        For 40 < t <= 100mm: Fy - 20 MPa
        """
        if self.thickness <= 16.0:
            return self.Fy
        elif self.thickness <= 40.0:
            return max(self.Fy - 10.0, 0.0)
        else:
            return max(self.Fy - 25.0, 0.0)

    @property
    def G(self) -> float:
        """Shear modulus G = E / (2 * (1 + nu)) (MPa)."""
        return self.E / (2.0 * (1.0 + self.nu))


def get_phi_flexure(et: float, ey: float = 0.002, is_spiral: bool = False) -> float:
    """Calculate KDS strength reduction factor (phi) for flexure and axial tension/compression.
    
    Args:
        et: Net tensile strain in extreme tension steel.
        ey: Yield strain of steel (fy / Es).
        is_spiral: True if member has spiral reinforcement (phi_c = 0.70 instead of 0.65).
        
    Returns:
        phi: Strength reduction factor between 0.65 (or 0.70) and 0.85.
    """
    phi_c = 0.70 if is_spiral else 0.65
    phi_t = 0.85
    et_limit = max(0.005, 2.5 * ey)
    
    if et >= et_limit:
        return phi_t
    elif et <= ey:
        return phi_c
    else:
        return phi_c + (et - ey) * (phi_t - phi_c) / (et_limit - ey)


def get_phi_shear(is_seismic: bool = False) -> float:
    """KDS strength reduction factor for shear and torsion (phi = 0.75 or 0.60 for seismic walls)."""
    return 0.60 if is_seismic else 0.75
