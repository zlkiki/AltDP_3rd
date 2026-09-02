"""
tests/engine/test_fem_baseplate.py
==================================
Verification of Base Plate Nonlinear Contact FEM Solver.
"""

import pytest
from src.engine.fem.baseplate_fem import BasePlateFEMSolver


def test_concentric_baseplate_bearing():
    """Concentric axial compression on a steel base plate."""
    # 500mm x 500mm x 30mm base plate with P = 1200 kN
    solver = BasePlateFEMSolver(
        plate_bx=500.0,
        plate_by=500.0,
        plate_thickness=30.0,
        steel_fy=275.0,
        concrete_fck=24.0,
        pedestal_bx=700.0,
        pedestal_by=700.0,
        nx=8,
        ny=8
    )
    # Add 4 corner anchor bolts (d=24mm)
    solver.add_anchor_bolt(x_mm=-180.0, y_mm=-180.0, bolt_dia_mm=24.0)
    solver.add_anchor_bolt(x_mm=180.0, y_mm=-180.0, bolt_dia_mm=24.0)
    solver.add_anchor_bolt(x_mm=180.0, y_mm=180.0, bolt_dia_mm=24.0)
    solver.add_anchor_bolt(x_mm=-180.0, y_mm=180.0, bolt_dia_mm=24.0)

    solver.set_column_load(P_kn=400.0, Mx_knm=0.0, My_knm=0.0)
    res = solver.solve_contact()

    assert res["converged"] is True
    assert res["active_bearing_ratio"] > 0.0  # Compressive contact active under column
    assert res["max_concrete_stress_mpa"] > 0.0
    assert res["bearing_ratio"] > 0.0


def test_eccentric_baseplate_with_anchor_tension():
    """Large eccentric bending moment inducing anchor bolt tension."""
    solver = BasePlateFEMSolver(
        plate_bx=600.0,
        plate_by=600.0,
        plate_thickness=35.0,
        steel_fy=355.0,
        concrete_fck=27.0,
        nx=10,
        ny=10
    )
    # 4 Anchor bolts
    solver.add_anchor_bolt(x_mm=-220.0, y_mm=-220.0, bolt_dia_mm=30.0)
    solver.add_anchor_bolt(x_mm=220.0, y_mm=-220.0, bolt_dia_mm=30.0)
    solver.add_anchor_bolt(x_mm=220.0, y_mm=220.0, bolt_dia_mm=30.0)
    solver.add_anchor_bolt(x_mm=-220.0, y_mm=220.0, bolt_dia_mm=30.0)

    # High moment causing partial separation & bolt tension
    solver.set_column_load(P_kn=400.0, Mx_knm=180.0, My_knm=0.0)
    res = solver.solve_contact()

    assert res["converged"] is True
    # Contact separation should occur
    assert res["active_bearing_ratio"] < 1.0
    # Anchor bolts should engage in tension
    assert res["max_bolt_tension_kn"] > 0.0
    assert res["max_concrete_stress_mpa"] > 0.0
    assert res["max_plate_stress_mpa"] > 0.0
