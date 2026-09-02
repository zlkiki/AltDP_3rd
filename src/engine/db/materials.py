"""Material properties and KDS standard definitions for AltDP_3rd.

Re-exports core material models from src.engine.materials for backwards compatibility.
"""

from src.engine.materials import (
    ConcreteMaterial,
    RebarMaterial,
    SteelMaterial,
    get_phi_flexure,
    get_phi_shear,
    STEEL_STANDARDS_DB
)

__all__ = [
    "ConcreteMaterial",
    "RebarMaterial",
    "SteelMaterial",
    "get_phi_flexure",
    "get_phi_shear",
    "STEEL_STANDARDS_DB"
]
