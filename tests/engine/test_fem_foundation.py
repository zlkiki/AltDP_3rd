"""
tests/engine/test_fem_foundation.py
===================================
Verification of Foundation FEM with Winkler Springs and Tension Cut-off.
"""

import pytest
import numpy as np
from src.engine.fem.foundation_fem import FoundationFEMSolver


def test_uniform_concentric_mat_foundation():
    """Concentric vertical column load on a square footing."""
    P_total = 1000.0  # kN
    lx, ly = 4.0, 4.0  # 4m x 4m = 16 m^2
    ks = 20000.0       # kN/m^3
    thickness = 0.5    # m
    
    # Theoretical Uniform Settlement: w = P / (ks * Area) = 1000 / (20000 * 16) = 0.003125 m = 3.125 mm
    # Theoretical Bearing Pressure: q = P / Area = 1000 / 16 = 62.5 kPa
    q_avg_exact = P_total / (lx * ly)
    
    solver = FoundationFEMSolver(
        length_x=lx,
        length_y=ly,
        thickness=thickness,
        fck=27.0,
        subgrade_modulus_ks=ks,
        nx=8,
        ny=8
    )
    solver.add_column_load(x=2.0, y=2.0, P=P_total)
    
    res = solver.solve_nonlinear()
    
    assert res["converged"] is True
    assert res["active_area_ratio"] == 1.0  # Fully compressive
    
    # Peak bearing pressure near column should be higher than average due to plate flexibility, but close in order
    assert 50.0 < res["max_bearing_pressure_kpa"] < 150.0
    assert 2.0 < res["max_settlement_mm"] < 6.0
    assert res["max_moment_mxx_knm_m"] > 0.0


def test_eccentric_load_tension_cutoff():
    """Large eccentric moment causing partial uplift separation."""
    P_col = 500.0
    M_col = 600.0  # High moment causing uplift
    lx, ly = 4.0, 4.0
    
    solver = FoundationFEMSolver(
        length_x=lx,
        length_y=ly,
        thickness=0.4,
        fck=24.0,
        subgrade_modulus_ks=15000.0,
        nx=8,
        ny=8
    )
    solver.add_column_load(x=2.0, y=2.0, P=P_col, Mx=M_col)
    
    res = solver.solve_nonlinear()
    
    assert res["converged"] is True
    assert res["iterations"] >= 1
    # Uplift separation should reduce active contact area
    assert res["active_area_ratio"] < 1.0
    assert res["max_bearing_pressure_kpa"] > 0.0
