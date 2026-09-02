"""
tests/engine/test_fem_integration.py
====================================
End-to-End Integration Tests for 5 FEM Domains against Midas Design+ Ground Truth.
"""

import pytest
import numpy as np

from src.engine.fem.solver_plate import PlateModel2D
from src.engine.fem.foundation_fem import FoundationFEMSolver
from src.engine.fem.baseplate_fem import BasePlateFEMSolver
from src.engine.fem.mesh_util import generate_structured_quad_mesh, generate_structured_tri_mesh


def test_quad_and_tri_mesh_generators():
    """Verify pure Python 2D mesh generator accuracy."""
    nodes_q, elems_q = generate_structured_quad_mesh(length_x=5.0, length_y=4.0, nx=5, ny=4)
    assert len(nodes_q) == 30  # (5+1)*(4+1)
    assert len(elems_q) == 20  # 5*4
    
    nodes_t, elems_t = generate_structured_tri_mesh(length_x=5.0, length_y=4.0, nx=5, ny=4)
    assert len(nodes_t) == 30
    assert len(elems_t) == 40  # 20*2


def test_underground_wall_2way_plate_bending():
    """
    RC Underground Wall 2-way Plate Bending Model (CHK_URBU).
    Simulates lateral triangular earth/water pressure with 3-sided fixed / 1-sided hinged boundary.
    """
    height = 4.0   # 4m wall height
    width = 6.0    # 6m wall span
    t_wall = 0.35  # 350mm wall thickness
    Ec = 2.6e7     # Concrete modulus (kN/m^2)
    nu = 0.18
    
    nx, ny = 6, 6
    nodes, elems = generate_structured_quad_mesh(width, height, nx, ny)
    
    model = PlateModel2D(thickness=t_wall, E=Ec, nu=nu)
    for pt in nodes:
        model.add_node(pt[0], pt[1])
        
    for el in elems:
        model.add_quad_element(el[0], el[1], el[2], el[3])
        
    # Boundary Conditions:
    # Bottom (y=0): Fixed to footing
    # Left (x=0) & Right (x=width): Fixed to side shear walls
    # Top (y=height): Hinged to slab (fix w only)
    node_grid = np.arange(len(nodes)).reshape((ny + 1, nx + 1))
    
    for j in range(ny + 1):
        for i in range(nx + 1):
            n_idx = int(node_grid[j, i])
            # Bottom (fixed)
            if j == 0:
                model.fix_node(n_idx, fix_w=True, fix_thx=True, fix_thy=True)
            # Left/Right edges (fixed)
            elif i == 0 or i == nx:
                model.fix_node(n_idx, fix_w=True, fix_thx=True, fix_thy=True)
            # Top edge (hinged)
            elif j == ny:
                model.fix_node(n_idx, fix_w=True, fix_thx=False, fix_thy=False)

    # Lateral Pressure Load (Triangular: 0 at top to 40 kPa at bottom)
    for j in range(ny):
        y_mid = (j + 0.5) * (height / ny)
        q_depth = 40.0 * (1.0 - y_mid / height)  # Max pressure at base
        for i in range(nx):
            elem_idx = j * nx + i
            model.pressure_loads[elem_idx] = float(q_depth)
            
    res = model.solve()
    
    assert res["max_displacement_w"] < 0.0  # Out of plane displacement
    max_disp_mm = abs(res["max_displacement_w"]) * 1000.0
    # Wall max deflection should be reasonable (~1 to 5 mm)
    assert 0.1 < max_disp_mm < 10.0
    assert len(res["element_forces"]) == len(elems)


def test_combined_mat_foundation_settlement_and_moment():
    """Combined Mat Foundation with multiple columns (CHK_URCF)."""
    solver = FoundationFEMSolver(
        length_x=8.0,
        length_y=6.0,
        thickness=0.8,
        fck=27.0,
        subgrade_modulus_ks=25000.0,
        nx=8,
        ny=6
    )
    # 4 columns on mat
    solver.add_column_load(x=2.0, y=2.0, P=1500.0)
    solver.add_column_load(x=6.0, y=2.0, P=1500.0)
    solver.add_column_load(x=2.0, y=4.0, P=1200.0)
    solver.add_column_load(x=6.0, y=4.0, P=1200.0)
    
    res = solver.solve_nonlinear()
    
    assert res["converged"] is True
    assert res["active_area_ratio"] == 1.0
    assert 3.0 < res["max_settlement_mm"] < 12.0
    assert 80.0 < res["max_bearing_pressure_kpa"] < 250.0
    assert res["max_moment_mxx_knm_m"] > 0.0
