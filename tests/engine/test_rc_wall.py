"""Unit tests for RC Shear Wall Design Engine (Phase 05-1).

Verifies KDS 14 20 22 / KDS 14 20 70 in-plane shear, rebar limits,
and Special Boundary Element (SBE) checks.
"""

import math
import pytest
from src.engine.rc.wall import (
    RCShearWall,
    RCWallInput,
    BoundaryElementConfig,
    WallShearResult,
    WallRebarRatioResult,
    BoundaryElementCheckResult,
    RCWallDesignResult
)
from src.engine.materials import ConcreteMaterial, RebarMaterial


def test_shear_capacity_aspect_ratio_interpolation():
    """Test alpha_c interpolation based on hw / lw ratio."""
    # Case 1: Squat wall (hw / lw <= 1.5) -> alpha_c = 0.25
    inp_squat = RCWallInput(lw=3000.0, tw=200.0, hw=3000.0) # hw/lw = 1.0
    wall_squat = RCShearWall(inp_squat)
    res_squat = wall_squat.calc_shear_capacity()
    assert res_squat.alpha_c == 0.25
    assert res_squat.aspect_ratio == 1.0
    
    # Case 2: Slender wall (hw / lw >= 2.0) -> alpha_c = 0.17
    inp_slender = RCWallInput(lw=2000.0, tw=200.0, hw=5000.0) # hw/lw = 2.5
    wall_slender = RCShearWall(inp_slender)
    res_slender = wall_slender.calc_shear_capacity()
    assert res_slender.alpha_c == 0.17
    assert res_slender.aspect_ratio == 2.5
    
    # Case 3: Intermediate wall (hw / lw = 1.75) -> alpha_c = 0.21
    inp_mid = RCWallInput(lw=2000.0, tw=200.0, hw=3500.0) # hw/lw = 1.75
    wall_mid = RCShearWall(inp_mid)
    res_mid = wall_mid.calc_shear_capacity()
    assert math.isclose(res_mid.alpha_c, 0.21, abs_tol=1e-3)


def test_axial_load_effect_on_vc():
    """Test that compressive axial load increases Vc."""
    inp_no_axial = RCWallInput(lw=3000.0, tw=250.0, hw=3000.0, Pu=0.0, Vu=300.0)
    wall_no_axial = RCShearWall(inp_no_axial)
    res1 = wall_no_axial.calc_shear_capacity()
    
    inp_with_axial = RCWallInput(lw=3000.0, tw=250.0, hw=3000.0, Pu=2000.0, Vu=300.0)
    wall_with_axial = RCShearWall(inp_with_axial)
    res2 = wall_with_axial.calc_shear_capacity()
    
    assert res2.Vc > res1.Vc
    # Check theoretical difference: Nu / (4 * lw * tw) * tw * d
    # Pu = 2000 kN = 2e6 N, d = 0.8 * 3000 = 2400 mm
    # delta_Vc = (2e6 / (4 * 3000 * 250)) * 250 * 2400 = (2e6 / 3e6) * 600000 = 400,000 N = 400 kN
    diff_kN = res2.Vc - res1.Vc
    assert math.isclose(diff_kN, 400.0, rel_tol=1e-2)


def test_upper_limit_vn_max():
    """Test shear upper limit Vn <= 0.83 * sqrt(fck) * tw * d."""
    # Huge rebar to cause Vs overshoot
    inp = RCWallInput(
        lw=3000.0, tw=300.0, hw=3000.0,
        horiz_bar_diam=32.0, horiz_spacing=50.0, horiz_layers=4,
        concrete=ConcreteMaterial(fck=25.0)
    )
    wall = RCShearWall(inp)
    res = wall.calc_shear_capacity()
    # Vn_max = 0.83 * sqrt(25) * 300 * (0.8 * 3000) = 0.83 * 5 * 300 * 2400 = 2,988,000 N = 2988 kN
    assert math.isclose(res.Vn_max, 2988.0, rel_tol=1e-2)
    assert res.Vn == res.Vn_max


def test_rebar_ratios_and_double_curtain():
    """Test minimum rebar ratio rules and double-curtain trigger."""
    # tw = 300 mm (>= 250 mm -> double curtain required)
    inp = RCWallInput(
        lw=4000.0, tw=300.0, hw=3000.0,
        vert_bar_diam=13.0, vert_spacing=200.0, vert_layers=2,
        horiz_bar_diam=13.0, horiz_spacing=200.0, horiz_layers=2,
        Vu=200.0
    )
    wall = RCShearWall(inp)
    rebar_res = wall.check_reinforcement_ratios()
    
    assert rebar_res.is_double_curtain_required is True
    assert rebar_res.is_double_curtain_provided is True
    assert rebar_res.is_vert_ok is True
    assert rebar_res.is_horiz_ok is True
    assert rebar_res.is_spacing_ok is True


def test_special_boundary_element_displacement_based():
    """Test displacement-based boundary element requirement."""
    # High inelastic drift delta_u / hw = 45 / 3000 = 0.015
    # c_limit = lw / (600 * 0.015) = lw / 9.0 = 4000 / 9 = 444.4 mm
    inp = RCWallInput(
        lw=4000.0, tw=300.0, hw=3000.0,
        Pu=3000.0, Mu=4000.0, delta_u=45.0,
        left_boundary=BoundaryElementConfig(length=500.0, width=300.0, bar_diam=25.0, total_bars=8)
    )
    wall = RCShearWall(inp)
    be_res = wall.check_boundary_elements()
    
    assert be_res.is_sbe_required is True
    assert be_res.trigger_method in ["Displacement-based", "Both"]
    assert be_res.required_be_length > 0


def test_special_boundary_element_stress_based():
    """Test stress-based boundary element requirement when sigma_max >= 0.2 * fck."""
    # fck = 20 MPa -> 0.2 * fck = 4.0 MPa
    # Ag = 4000 * 300 = 1.2e6 mm2, Z = 300 * 4000^2 / 6 = 8.0e8 mm3
    # Pu = 3000 kN -> Pu/Ag = 2.5 MPa
    # Mu = 2000 kN*m -> Mu/Z = 2.5 MPa
    # sigma_max = 5.0 MPa >= 4.0 MPa -> SBE Required
    inp = RCWallInput(
        lw=4000.0, tw=300.0, hw=3000.0,
        Pu=3000.0, Mu=2000.0,
        concrete=ConcreteMaterial(fck=20.0),
        delta_u=5.0 # Low drift to isolate stress check
    )
    wall = RCShearWall(inp)
    be_res = wall.check_boundary_elements()
    
    assert be_res.sigma_max >= be_res.sigma_limit
    assert be_res.is_sbe_required is True


def test_wall_comprehensive_design_check():
    """Test full design check pipeline and 2D geometry generation."""
    inp = RCWallInput(
        name="W101",
        lw=3500.0, tw=300.0, hw=3200.0,
        Pu=1200.0, Vu=500.0, Mu=1500.0,
        left_boundary=BoundaryElementConfig(length=450.0, width=300.0),
        right_boundary=BoundaryElementConfig(length=450.0, width=300.0)
    )
    wall = RCShearWall(inp)
    res = wall.design_check()
    assert isinstance(res, RCWallDesignResult)
    assert res.wall_name == "W101"
    
    geom = wall.get_section_geometry_dict()
    assert len(geom["polygon"]) == 4
    assert len(geom["rebars"]) > 0
    assert len(geom["boundary_zones"]) == 2
