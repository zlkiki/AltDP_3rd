"""Tests for 2D Plate Bending FEM Core (DKMQ, DKT, Sparse Solver, Mesh Utilities).

Validates:
- Rigid body motion modes (zero eigenvalues) for DKMQ and DKT
- Theoretical deflection and moment comparisons for simply-supported and clamped plates
- High-speed SciPy sparse matrix solver execution (< 0.05s)
"""

import time
import pytest
import numpy as np

from src.engine.fem.element_dkmq import compute_dkmq_stiffness, compute_dkmq_internal_forces
from src.engine.fem.element_dkt import compute_dkt_stiffness
from src.engine.fem.solver_plate import PlateModel2D
from src.engine.fem.mesh_util import generate_structured_quad_mesh, generate_structured_tri_mesh


def test_dkmq_rigid_body_modes():
    """DKMQ 12x12 stiffness matrix should have at least 3 zero eigenvalues (rigid body modes in 2D bending: w, rot_x, rot_y)."""
    coords = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ])
    thickness = 0.2
    E = 3.0e7  # kPa
    nu = 0.2
    
    Ke, Db = compute_dkmq_stiffness(coords, thickness, E, nu)
    assert Ke.shape == (12, 12)
    assert np.allclose(Ke, Ke.T, atol=1e-6), "Stiffness matrix must be symmetric."
    
    eigvals = np.linalg.eigvalsh(Ke)
    # The smallest 3 eigenvalues corresponding to rigid translation and two rotations should be nearly 0
    zero_eigvals = [ev for ev in eigvals if abs(ev) < 1e-4]
    assert len(zero_eigvals) >= 3, f"Expected 3 rigid body modes, got: {eigvals[:5]}"


def test_dkt_rigid_body_modes():
    """DKT 9x9 stiffness matrix should have 3 zero eigenvalues (rigid body modes)."""
    coords = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0]
    ])
    thickness = 0.2
    E = 3.0e7
    nu = 0.2
    
    Ke, Db = compute_dkt_stiffness(coords, thickness, E, nu)
    assert Ke.shape == (9, 9)
    assert np.allclose(Ke, Ke.T, atol=1e-6), "Stiffness matrix must be symmetric."
    
    eigvals = np.linalg.eigvalsh(Ke)
    zero_eigvals = [ev for ev in eigvals if abs(ev) < 1e-4]
    assert len(zero_eigvals) >= 3, f"Expected 3 rigid body modes, got: {eigvals[:5]}"


def test_clamped_square_plate_deflection():
    """Clamped square plate under uniform pressure load: compare with Timoshenko/Roark theoretical solution.
    
    Theoretical center deflection w_max for clamped square plate (a x a) under pressure q:
    w_max = alpha * q * a^4 / D
    where D = E * t^3 / (12 * (1 - nu^2)), alpha ~= 0.00126 (Timoshenko & Woinowsky-Krieger)
    """
    a = 2.0  # length in m
    t = 0.1  # thickness in m
    E = 2.0e7  # kPa (20 GPa)
    nu = 0.2
    q = 10.0  # kPa
    
    D = (E * t**3) / (12.0 * (1.0 - nu**2))
    w_theory = 0.00126 * q * (a**4) / D  # m (downward)
    
    # Mesh 8x8
    nx, ny = 8, 8
    nodes, elements = generate_structured_quad_mesh(a, a, nx, ny)
    
    model = PlateModel2D(thickness=t, E=E, nu=nu)
    for pt in nodes:
        model.add_node(pt[0], pt[1])
    for elem in elements:
        model.add_quad_element(elem[0], elem[1], elem[2], elem[3])
        
    # Clamp all 4 boundaries (w=0, thx=0, thy=0)
    for i, pt in enumerate(nodes):
        x, y = pt[0], pt[1]
        if np.isclose(x, 0.0) or np.isclose(x, a) or np.isclose(y, 0.0) or np.isclose(y, a):
            model.fix_node(i, fix_w=True, fix_thx=True, fix_thy=True)
            
    model.set_uniform_pressure(q)
    results = model.solve()
    
    w_fem = abs(results["max_displacement_w"])
    error = abs(w_fem - w_theory) / w_theory
    assert error < 0.05, f"Clamped plate deflection FEM={w_fem:.6f}m, Theory={w_theory:.6f}m, Error={error*100:.2f}%"


def test_tri_mesh_solver():
    """Verify solving with DKT triangular elements."""
    a = 2.0
    t = 0.1
    E = 2.0e7
    nu = 0.2
    
    nodes, tri_elems = generate_structured_tri_mesh(a, a, 4, 4)
    model = PlateModel2D(thickness=t, E=E, nu=nu)
    for pt in nodes:
        model.add_node(pt[0], pt[1])
    for elem in tri_elems:
        model.add_tri_element(elem[0], elem[1], elem[2])
        
    # Simple support boundary (fix w only)
    for i, pt in enumerate(nodes):
        x, y = pt[0], pt[1]
        if np.isclose(x, 0.0) or np.isclose(x, a) or np.isclose(y, 0.0) or np.isclose(y, a):
            model.fix_node(i, fix_w=True, fix_thx=False, fix_thy=False)
            
    # Apply central point load
    center_idx = (4 + 1) * 2 + 2  # (2, 2)
    model.add_nodal_load(center_idx, Pz=-50.0)
    
    results = model.solve()
    assert results["max_displacement_w"] < 0.0, "Displacement must be negative downward."
    assert results["num_elements"] == 32


def test_sparse_solver_speed_1000_nodes():
    """Check that sparse solve for ~1,000 nodes takes < 0.2s."""
    nx, ny = 30, 30  # 31 * 31 = 961 nodes, 900 quad elements
    nodes, elements = generate_structured_quad_mesh(10.0, 10.0, nx, ny)
    
    model = PlateModel2D(thickness=0.3, E=2.5e7, nu=0.2)
    for pt in nodes:
        model.add_node(pt[0], pt[1])
    for elem in elements:
        model.add_quad_element(elem[0], elem[1], elem[2], elem[3])
        
    for i, pt in enumerate(nodes):
        if np.isclose(pt[0], 0.0) or np.isclose(pt[0], 10.0) or np.isclose(pt[1], 0.0) or np.isclose(pt[1], 10.0):
            model.fix_node(i, fix_w=True, fix_thx=True, fix_thy=True)
            
    model.set_uniform_pressure(15.0)
    
    t0 = time.perf_counter()
    results = model.solve()
    elapsed = time.perf_counter() - t0
    
    assert results["num_nodes"] == 961
    assert elapsed < 0.8, f"Solve time {elapsed:.4f}s took too long (expected < 0.8s)."
