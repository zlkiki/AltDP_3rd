"""Tests for Mat/Footing Foundation FEM Solver with Winkler Springs & Tension Cut-off."""

import pytest
import numpy as np
from src.engine.fem.foundation_fem import FoundationFEMSolver


def test_concentric_mat_foundation_bearing_pressure():
    """Concentric column load on a mat foundation should yield nearly uniform pressure."""
    solver = FoundationFEMSolver(
        length_x=4.0,
        length_y=4.0,
        thickness=0.5,
        fck=24.0,
        subgrade_modulus_ks=20000.0,
        nx=8,
        ny=8
    )
    # 1000 kN centered load at (2.0, 2.0)
    solver.add_column_load(2.0, 2.0, P=1600.0, Mx=0.0, My=0.0)
    
    res = solver.solve_nonlinear(max_iter=15)
    assert res["converged"] is True
    assert res["active_area_ratio"] == 1.0, "All springs should remain active for concentric load."
    
    # Average pressure = P / Area = 1600 / 16 = 100 kPa
    assert res["max_bearing_pressure_kpa"] > 90.0
    assert res["max_bearing_pressure_kpa"] < 250.0  # Slightly peaked under column due to plate bending
    assert res["max_settlement_mm"] > 0.0


def test_eccentric_tension_separation_uplift():
    """Heavy eccentric moment should cause partial uplift (tension cut-off separation)."""
    solver = FoundationFEMSolver(
        length_x=5.0,
        length_y=5.0,
        thickness=0.6,
        fck=27.0,
        subgrade_modulus_ks=15000.0,
        nx=10,
        ny=10
    )
    # Axial 500 kN + High Overturning Moment My = 1000 kNm
    solver.add_column_load(2.5, 2.5, P=500.0, Mx=0.0, My=1000.0)
    
    res = solver.solve_nonlinear(max_iter=20)
    assert res["converged"] is True
    # Due to overturning, uplift occurs on one side
    assert res["active_area_ratio"] < 1.0, f"Expected uplift separation, but active ratio was {res['active_area_ratio']}"
    assert res["active_area_ratio"] >= 0.3
    assert res["iterations"] <= 15
    assert res["max_moment_mxx_knm_m"] > 0.0
