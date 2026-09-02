"""
tests/engine/test_fem_analytical.py
===================================
Verification of 2D Plate Bending Element against Timoshenko Analytical Exact Solutions.
"""

import pytest
import numpy as np
from src.engine.fem.solver_plate import PlateModel2D


def test_timoshenko_simply_supported_square_plate():
    """
    Test simply supported square plate (a x a) under uniform pressure q.
    Timoshenko Exact Solution (Navier Series):
        D = E * t^3 / (12 * (1 - nu^2))
        w_max = 0.004062 * q * a^4 / D
        M_max = 0.0479 * q * a^2
    """
    a = 10.0      # length (m)
    t = 0.2       # thickness (m)
    E = 3.0e7     # Young's modulus (kN/m^2)
    nu = 0.3      # Poisson's ratio
    q = 10.0      # uniform pressure (kN/m^2)

    D = (E * t**3) / (12.0 * (1.0 - nu**2))
    w_exact = 0.004062 * q * (a**4) / D
    M_exact = 0.0479 * q * (a**2)

    # FEM Mesh: 16x16 quad mesh
    nx, ny = 16, 16
    dx = a / nx
    dy = a / ny

    model = PlateModel2D(thickness=t, E=E, nu=nu)
    nodes = []
    node_grid = np.zeros((ny + 1, nx + 1), dtype=int)

    for j in range(ny + 1):
        y = j * dy
        for i in range(nx + 1):
            x = i * dx
            node_grid[j, i] = len(nodes)
            nodes.append([x, y])
            model.add_node(x, y)

    # Add Elements
    for j in range(ny):
        for i in range(nx):
            n1 = node_grid[j, i]
            n2 = node_grid[j, i + 1]
            n3 = node_grid[j + 1, i + 1]
            n4 = node_grid[j + 1, i]
            model.add_quad_element(n1, n2, n3, n4)

    # Simply Supported Boundary Conditions: fix w = 0 on all 4 edges
    for j in range(ny + 1):
        for i in range(nx + 1):
            if i == 0 or i == nx or j == 0 or j == ny:
                idx = node_grid[j, i]
                model.fix_node(idx, fix_w=True, fix_thx=False, fix_thy=False)

    model.set_uniform_pressure(q)
    results = model.solve()

    w_fem = abs(results["max_displacement_w"])
    error_w = abs(w_fem - w_exact) / w_exact

    # Check accuracy within 1.0% for 16x16 mesh (Mindlin shear deformation effect included)
    assert error_w < 0.01, f"Center deflection error {error_w*100:.3f}% exceeds 1.0% (FEM={w_fem}, Exact={w_exact})"



def test_clamped_square_plate():
    """
    Test clamped (fixed on all 4 edges) square plate under uniform pressure q.
    Timoshenko Exact Solution:
        w_max = 0.00126 * q * a^4 / D
    """
    a = 6.0
    t = 0.15
    E = 2.5e7
    nu = 0.2
    q = 5.0

    D = (E * t**3) / (12.0 * (1.0 - nu**2))
    w_exact = 0.00126 * q * (a**4) / D

    nx, ny = 12, 12
    dx = a / nx
    dy = a / ny

    model = PlateModel2D(thickness=t, E=E, nu=nu)
    node_grid = np.zeros((ny + 1, nx + 1), dtype=int)
    nodes = []

    for j in range(ny + 1):
        y = j * dy
        for i in range(nx + 1):
            x = i * dx
            node_grid[j, i] = len(nodes)
            nodes.append([x, y])
            model.add_node(x, y)

    for j in range(ny):
        for i in range(nx):
            n1 = node_grid[j, i]
            n2 = node_grid[j, i + 1]
            n3 = node_grid[j + 1, i + 1]
            n4 = node_grid[j + 1, i]
            model.add_quad_element(n1, n2, n3, n4)

    # Clamped on all 4 edges (fix w, thx, thy)
    for j in range(ny + 1):
        for i in range(nx + 1):
            if i == 0 or i == nx or j == 0 or j == ny:
                idx = node_grid[j, i]
                model.fix_node(idx, fix_w=True, fix_thx=True, fix_thy=True)

    model.set_uniform_pressure(q)
    results = model.solve()

    w_fem = abs(results["max_displacement_w"])
    error_w = abs(w_fem - w_exact) / w_exact

    assert error_w < 0.01, f"Clamped deflection error {error_w*100:.3f}% exceeds 1.0%"
