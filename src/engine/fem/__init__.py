"""
src/engine/fem/__init__.py
==========================
AltDP_3rd High-Performance 2D Finite Element Analysis & Foundation Solver Package.
Zero-Dependency Pure Python (NumPy/SciPy) Engine.
"""

from .element_dkmq import compute_dkmq_stiffness, compute_dkmq_internal_forces
from .element_dkt import compute_dkt_stiffness
from .solver_plate import PlateModel2D
from .foundation_fem import FoundationFEMSolver
from .baseplate_fem import BasePlateFEMSolver
from .mesh_util import generate_structured_quad_mesh, generate_structured_tri_mesh

__all__ = [
    "compute_dkmq_stiffness",
    "compute_dkmq_internal_forces",
    "compute_dkt_stiffness",
    "PlateModel2D",
    "FoundationFEMSolver",
    "BasePlateFEMSolver",
    "generate_structured_quad_mesh",
    "generate_structured_tri_mesh"
]
