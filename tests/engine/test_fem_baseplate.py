"""Tests for Steel Baseplate Nonlinear Contact FEM Solver (Concrete Bearing & Anchor Tension)."""

import pytest
import numpy as np
from src.engine.fem.baseplate_fem import BasePlateFEMSolver


def test_baseplate_concentric_compression():
    """Concentric axial compression should engage full concrete bearing with zero bolt tension."""
    solver = BasePlateFEMSolver(
        plate_bx=500.0,
        plate_by=500.0,
        plate_thickness=30.0,
        steel_fy=275.0,
        concrete_fck=24.0,
        nx=8,
        ny=8
    )
    # Add 4 corner anchor bolts
    solver.add_anchor_bolt(-180.0, -180.0, bolt_dia_mm=24.0)
    solver.add_anchor_bolt( 180.0, -180.0, bolt_dia_mm=24.0)
    solver.add_anchor_bolt(-180.0,  180.0, bolt_dia_mm=24.0)
    solver.add_anchor_bolt( 180.0,  180.0, bolt_dia_mm=24.0)
    
    # Concentric 800 kN compression
    solver.set_column_load(P_kn=800.0, Mx_knm=0.0, My_knm=0.0)
    
    res = solver.solve_contact(max_iter=15)
    assert res["converged"] is True
    # Under concentric compression, bolt tension is near zero or very small (< 20 kN) due to minor corner curl
    assert res["max_bolt_tension_kn"] < 20.0
    assert res["max_concrete_stress_mpa"] > 0.0
    assert res["max_concrete_stress_mpa"] <= res["allowable_concrete_stress_mpa"] * 1.5


def test_baseplate_large_moment_with_anchor_tension():
    """High bending moment should cause tension in anchor bolts and uplift on one side."""
    solver = BasePlateFEMSolver(
        plate_bx=600.0,
        plate_by=600.0,
        plate_thickness=35.0,
        steel_fy=355.0,
        concrete_fck=27.0,
        nx=10,
        ny=10
    )
    solver.add_anchor_bolt(-220.0, -220.0, bolt_dia_mm=30.0)
    solver.add_anchor_bolt( 220.0, -220.0, bolt_dia_mm=30.0)
    solver.add_anchor_bolt(-220.0,  220.0, bolt_dia_mm=30.0)
    solver.add_anchor_bolt( 220.0,  220.0, bolt_dia_mm=30.0)
    
    # 200 kN axial + 150 kNm moment
    solver.set_column_load(P_kn=200.0, Mx_knm=150.0, My_knm=0.0)
    
    res = solver.solve_contact(max_iter=20)
    assert res["converged"] is True
    assert res["max_bolt_tension_kn"] > 0.0, "High moment must engage anchor bolt tension."
    assert res["active_bearing_ratio"] < 1.0, "Partial uplift expected on tension side."
