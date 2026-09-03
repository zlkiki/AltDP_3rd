"""Tests for PBD (Performance-Based Design) Plastic Hinge Engine.

Validates ASCE 41-17 / KDS 41 17 00 hinge parameter formulations,
backbone curve geometry, IO/LS/CP performance levels, and member response.
"""

import pytest
import math
from src.engine.pbd import (
    BackbonePoint,
    HingeParameters,
    HingePerformance,
    MemberType,
    PerformanceLevel,
    generate_backbone_curve,
    evaluate_performance_level,
    create_hinge_performance_summary,
    calculate_rc_beam_hinge_parameters,
    calculate_rc_column_hinge_parameters,
    calculate_rc_wall_hinge_parameters,
    create_rc_beam_hinge,
    calculate_steel_beam_hinge_parameters,
    calculate_steel_column_hinge_parameters,
    calculate_steel_brace_hinge_parameters,
    create_steel_beam_hinge,
)


class TestBackboneCurveAndPerformanceEvaluation:
    """Test backbone curve generation and acceptance criteria evaluations."""

    def test_backbone_curve_points_generation(self):
        params = HingeParameters(
            a=0.020,
            b=0.030,
            c=0.20,
            io_limit=0.005,
            ls_limit=0.020,
            cp_limit=0.030,
            alpha=0.05,
        )
        theta_y = 0.005
        my = 200.0

        # Positive quadrant only
        curve_pos = generate_backbone_curve(theta_y, my, params, symmetric=False)
        assert len(curve_pos) == 5
        assert curve_pos[0].theta_rad == 0.0
        assert curve_pos[0].moment_knm == 0.0
        # Yield point
        assert curve_pos[1].theta_rad == pytest.approx(0.005, rel=1e-5)
        assert curve_pos[1].moment_knm == pytest.approx(200.0, rel=1e-5)
        # Capping point: theta_y + a = 0.025, My*(1+alpha) = 210.0
        assert curve_pos[2].theta_rad == pytest.approx(0.025, rel=1e-5)
        assert curve_pos[2].moment_knm == pytest.approx(210.0, rel=1e-5)
        # Residual point: theta_y + b = 0.035, My*c = 40.0
        assert curve_pos[3].theta_rad == pytest.approx(0.035, rel=1e-5)
        assert curve_pos[3].moment_knm == pytest.approx(40.0, rel=1e-5)
        # Failure point: theta > 0.035, M = 0.0
        assert curve_pos[4].theta_rad > 0.035
        assert curve_pos[4].moment_knm == 0.0

        # Symmetric curve includes negative mirrored coordinates
        curve_sym = generate_backbone_curve(theta_y, my, params, symmetric=True)
        assert len(curve_sym) == 9
        assert curve_sym[0].moment_knm == 0.0
        assert curve_sym[0].theta_rad < 0.0
        assert curve_sym[4].theta_rad == 0.0  # Center origin

    def test_performance_level_classification(self):
        params = HingeParameters(
            a=0.025,
            b=0.040,
            c=0.20,
            io_limit=0.005,
            ls_limit=0.020,
            cp_limit=0.035,
            alpha=0.03,
        )
        theta_y = 0.005

        # Limits: IO <= 0.010, LS <= 0.025, CP <= 0.040, COLLAPSE > 0.040
        level_io, dcr_io = evaluate_performance_level(0.008, theta_y, params)
        assert level_io == PerformanceLevel.IO.value
        assert dcr_io < 1.0

        level_ls, dcr_ls = evaluate_performance_level(0.018, theta_y, params)
        assert level_ls == PerformanceLevel.LS.value
        assert dcr_ls < 1.0

        level_cp, dcr_cp = evaluate_performance_level(0.032, theta_y, params)
        assert level_cp == PerformanceLevel.CP.value
        assert dcr_cp <= 1.0

        level_coll, dcr_coll = evaluate_performance_level(0.055, theta_y, params)
        assert level_coll == PerformanceLevel.COLLAPSE.value
        assert dcr_coll > 1.0


class TestRCHingeFormulation:
    """Test ASCE 41-17 RC beam, column, and wall formulations."""

    def test_rc_beam_hinge_parameters_conforming_vs_nonconforming(self):
        # Conforming beam
        params_conf = calculate_rc_beam_hinge_parameters(
            b=300.0, h=500.0, d=450.0, fck=24.0, fy=400.0,
            As=1200.0, As_prime=600.0, V_design=50.0, conforming=True
        )
        # Non-conforming beam
        params_nonconf = calculate_rc_beam_hinge_parameters(
            b=300.0, h=500.0, d=450.0, fck=24.0, fy=400.0,
            As=1200.0, As_prime=600.0, V_design=50.0, conforming=False
        )
        # Conforming beam must exhibit larger plastic rotation capacity
        assert params_conf.a > params_nonconf.a
        assert params_conf.b > params_nonconf.b
        assert params_conf.cp_limit > params_nonconf.cp_limit
        assert params_conf.c == 0.20

    def test_rc_column_hinge_axial_and_shear_branching(self):
        # Low axial load, flexure-controlled (Condition i)
        params_low_axial = calculate_rc_column_hinge_parameters(
            b=500.0, h=500.0, fck=30.0, P_axial=500.0,  # nu = 500 / 7500 = 0.067
            V_plastic=100.0, V_nominal=300.0, conforming=True  # Vp/Vn = 0.33 <= 0.6
        )
        # High axial load, flexure-controlled (Condition i)
        params_high_axial = calculate_rc_column_hinge_parameters(
            b=500.0, h=500.0, fck=30.0, P_axial=4500.0,  # nu = 4500 / 7500 = 0.60
            V_plastic=100.0, V_nominal=300.0, conforming=True
        )
        # Shear controlled (Condition iii: Vp/Vn >= 1.0)
        params_shear_ctrl = calculate_rc_column_hinge_parameters(
            b=500.0, h=500.0, fck=30.0, P_axial=1500.0,
            V_plastic=350.0, V_nominal=300.0, conforming=True  # Vp/Vn > 1.0
        )

        assert params_low_axial.a > params_high_axial.a
        assert params_low_axial.cp_limit > params_high_axial.cp_limit
        # Shear controlled must be brittle
        assert params_shear_ctrl.a == 0.002
        assert params_shear_ctrl.c == 0.0

    def test_rc_shear_wall_hinge(self):
        wall_flex = calculate_rc_wall_hinge_parameters(is_flexure=True, has_boundary_elements=True, nu=0.1)
        wall_shear = calculate_rc_wall_hinge_parameters(is_flexure=False)
        assert wall_flex.a > wall_shear.a
        assert wall_shear.c == 0.40

    def test_create_rc_beam_hinge_performance_summary(self):
        summary = create_rc_beam_hinge(
            member_id=101, b=400.0, h=600.0, d=540.0, fck=27.0, fy=400.0,
            As=1800.0, As_prime=400.0, span_len=6000.0, V_design=80.0,
            demand_theta=0.012,
        )
        assert summary.member_id == 101
        assert summary.member_type == MemberType.RC_BEAM.value
        assert summary.my_knm > 100.0
        assert summary.theta_y_rad > 0.0
        assert summary.performance_level in ["IO", "LS", "CP"]
        assert len(summary.backbone_curve) == 9


class TestSteelHingeFormulation:
    """Test ASCE 41-17 / AISC 341 steel member plastic hinge engines."""

    def test_steel_beam_compactness_and_bracing(self):
        # High ductility compact beam with frequent bracing
        params_hd = calculate_steel_beam_hinge_parameters(
            bf=200.0, tf=16.0, h=400.0, tw=9.0, fy=275.0, lb=1500.0, ry=48.0
        )
        # Slender / non-compact or long unbraced length beam
        params_ld = calculate_steel_beam_hinge_parameters(
            bf=200.0, tf=8.0, h=400.0, tw=5.0, fy=355.0, lb=8000.0, ry=30.0
        )
        assert params_hd.a > params_ld.a
        assert params_hd.cp_limit > params_ld.cp_limit
        assert params_hd.c == 0.60
        assert params_ld.c == 0.20

    def test_steel_column_axial_effect(self):
        params_col_low_p = calculate_steel_column_hinge_parameters(P_axial=200.0, P_cl=2000.0, is_compact=True)
        params_col_high_p = calculate_steel_column_hinge_parameters(P_axial=1500.0, P_cl=2000.0, is_compact=True)
        assert params_col_low_p.a > params_col_high_p.a
        assert params_col_low_p.cp_limit > params_col_high_p.cp_limit

    def test_steel_brace_tension_vs_compression(self):
        params_ten = calculate_steel_brace_hinge_parameters(is_tension=True)
        params_comp = calculate_steel_brace_hinge_parameters(is_tension=False, kl_over_r=90.0)
        # Tension brace has large ductile deformation
        assert params_ten.a > params_comp.a
        assert params_ten.c > params_comp.c
        assert params_ten.cp_limit > params_comp.cp_limit

    def test_create_steel_beam_hinge_performance_summary(self):
        summary = create_steel_beam_hinge(
            member_id=202, zx=1500e3, fy=275.0,
            bf=200.0, tf=16.0, h=400.0, tw=9.0, span_len=7000.0, ix=30000e4,
            demand_theta=0.015,
        )
        assert summary.member_id == 202
        assert summary.member_type == MemberType.STEEL_BEAM.value
        assert summary.my_knm == pytest.approx(412.5, rel=1e-3)
        assert summary.theta_y_rad > 0.0
        assert summary.performance_level in ["IO", "LS"]
