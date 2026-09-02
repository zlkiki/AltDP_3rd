"""Tests for Moment End-Plate Yield Line & Local Bending FEM Solver."""

import pytest
import numpy as np
from src.engine.fem.endplate_fem import EndPlateFEMSolver


def test_4bolt_extended_endplate_standard_design():
    """Verify standard 4-bolt extended end-plate under factored moment."""
    solver = EndPlateFEMSolver(
        plate_width_bp=250.0,
        plate_height_hp=650.0,
        plate_thickness_tp=28.0,
        beam_depth_d=500.0,
        flange_width_bf=200.0,
        flange_thickness_tf=16.0,
        web_thickness_tw=10.0,
        steel_fy=355.0,
        bolt_grade_fub=1000.0,
        bolt_dia_db=24.0,
        nx=8,
        ny=12
    )
    solver.set_4bolt_extended_layout(pitch_p_ext_mm=50.0, pitch_p_in_mm=50.0, gage_g_mm=100.0)
    
    # Apply 200 kNm moment
    res = solver.solve(moment_mu_knm=200.0, axial_pu_kn=0.0)
    
    assert res["flange_tension_tf_kn"] > 350.0
    assert res["max_bolt_tension_tb_kn"] > 0.0
    assert res["bolt_tensile_capacity_phi_rn_kn"] > 200.0
    assert "prying_force_q_kn" in res
    assert res["governing_dcr"] > 0.0


def test_thin_vs_thick_endplate_prying_action():
    """Thinner end-plate should exhibit larger prying force due to greater flexibility."""
    # Thin plate (16mm)
    thin_solver = EndPlateFEMSolver(
        plate_width_bp=250.0,
        plate_height_hp=600.0,
        plate_thickness_tp=16.0,
        beam_depth_d=450.0,
        flange_width_bf=200.0,
        flange_thickness_tf=14.0,
        web_thickness_tw=9.0,
        nx=8,
        ny=10
    )
    thin_res = thin_solver.solve(moment_mu_knm=120.0)
    
    # Thick plate (32mm)
    thick_solver = EndPlateFEMSolver(
        plate_width_bp=250.0,
        plate_height_hp=600.0,
        plate_thickness_tp=32.0,
        beam_depth_d=450.0,
        flange_width_bf=200.0,
        flange_thickness_tf=14.0,
        web_thickness_tw=9.0,
        nx=8,
        ny=10
    )
    thick_res = thick_solver.solve(moment_mu_knm=120.0)
    
    # Thin plate has higher bending stress and higher prying force
    assert thin_res["max_plate_stress_mpa"] > thick_res["max_plate_stress_mpa"]
    assert thin_res["prying_force_q_kn"] >= thick_res["prying_force_q_kn"]
