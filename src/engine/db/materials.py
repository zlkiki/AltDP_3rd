"""Material properties and KDS standard definitions for AltDP_3rd.

Provides concrete, reinforcing steel, and structural steel material models
following KDS 14 20 00 and KDS 14 31 00 standards.
"""

from dataclasses import dataclass
import math


@dataclass
class ConcreteMaterial:
    """KDS 14 20 00 Concrete Material Specification."""
    name: str = "C24"
    fck: float = 24.0          # MPa (Specified compressive strength)
    unit_weight: float = 23.5   # kN/m3
    ecu: float = 0.0033        # Ultimate strain
    
    @property
    def Ec(self) -> float:
        """Modulus of elasticity (KDS 14 20 10: Ec = 8500 * (fcu)^(1/3))."""
        fcu = self.fck + 4.0 if self.fck < 40 else self.fck + 6.0
        return 8500.0 * (fcu ** (1.0 / 3.0))

    @property
    def alpha1(self) -> float:
        """Equivalent stress block intensity factor (alpha1 = 0.85)."""
        return 0.85

    @property
    def beta1(self) -> float:
        """Equivalent stress block depth factor (beta1)."""
        if self.fck <= 28.0:
            return 0.85
        return max(0.85 - 0.007 * (self.fck - 28.0), 0.65)

    @property
    def f_cr(self) -> float:
        """Modulus of rupture for cracking moment (0.63 * sqrt(fck))."""
        return 0.63 * math.sqrt(self.fck)


@dataclass
class RebarMaterial:
    """KDS 14 20 00 Reinforcing Steel Material Specification."""
    name: str = "SD400"
    fy: float = 400.0          # MPa (Yield strength)
    fu: float = 560.0          # MPa (Tensile strength)
    Es: float = 200000.0       # MPa (Modulus of elasticity)

    @property
    def ey(self) -> float:
        """Yield strain."""
        return self.fy / self.Es


@dataclass
class SteelMaterial:
    """KDS 14 31 00 Structural Steel Material Specification."""
    name: str = "SS275"
    Fy: float = 275.0          # MPa (Yield strength)
    Fu: float = 410.0          # MPa (Tensile strength)
    E: float = 205000.0        # MPa (Modulus of elasticity)
    nu: float = 0.3            # Poisson's ratio
    
    @property
    def G(self) -> float:
        """Shear modulus."""
        return self.E / (2.0 * (1.0 + self.nu))


def get_phi_flexure(et: float, ey: float = 0.002) -> float:
    """Calculate KDS strength reduction factor (phi) for flexure and axial.
    
    Args:
        et: Net tensile strain in extreme tension steel.
        ey: Yield strain of steel (fy / Es).
        
    Returns:
        phi: Strength reduction factor between 0.65 (compression-controlled)
             and 0.85 (tension-controlled).
    """
    et_limit = max(0.005, 2.5 * ey)
    if et >= et_limit:
        return 0.85
    elif et <= ey:
        return 0.65
    else:
        return 0.65 + (et - ey) * (0.85 - 0.65) / (et_limit - ey)
