"""Unit Tests for Steel Beam Design Engine and Section Compactness (KDS 14 31 10)."""

import math
import pytest

from src.engine.materials import SteelMaterial
from src.engine.steel.compactness import (
    check_h_section_compactness,
    check_box_section_compactness,
    check_pipe_section_compactness,
    check_angle_section_compactness,
    SectionClassification,
    SectionType
)
from src.engine.steel.beam import (
    SteelBeamInput,
    design_steel_beam,
    calculate_cb
)


def test_h_section_compactness_classification():
    """Verify flange and web slenderness checks for standard H-shapes."""
    Fy = 355.0  # SM355
    E = 205000.0
    
    # 1. Compact H-beam (H-400x200x8x13)
    res1 = check_h_section_compactness(B=200.0, tf=13.0, H=400.0, tw=8.0, Fy=Fy, E=E, stress_state="flexure")
    assert res1.is_compact is True
    assert res1.flange.is_compact is True
    assert res1.web.is_compact is True
    assert res1.Q == 1.0
    
    # 2. Slender Flange H-beam (B=400, tf=6, H=400, tw=12)
    # lambda_f = 200 / 6 = 33.3 > 1.0 * sqrt(205000/355) = 24.03 -> Slender
    res2 = check_h_section_compactness(B=400.0, tf=6.0, H=400.0, tw=12.0, Fy=Fy, E=E, stress_state="flexure")
    assert res2.is_slender is True
    assert res2.flange.is_slender is True
    assert res2.Q < 1.0


def test_box_and_pipe_compactness():
    """Verify compactness for hollow sections."""
    Fy = 275.0
    E = 205000.0
    
    # Box-200x200x9 (Compact)
    box_res = check_box_section_compactness(B=200.0, H=200.0, t=9.0, Fy=Fy, E=E)
    assert box_res.is_compact is True
    
    # Pipe-219.1x6.0
    pipe_res = check_pipe_section_compactness(D=219.1, t=6.0, Fy=Fy, E=E)
    assert pipe_res.section_type == SectionType.PIPE
    assert pipe_res.overall_classification in [SectionClassification.COMPACT, SectionClassification.NON_COMPACT]


def test_moment_gradient_factor_cb():
    """Verify Cb formula against known standard loading cases."""
    # 1. Uniform moment: Mmax = MA = MB = MC = 100 -> Cb = 1.0
    cb_uniform = calculate_cb(Mmax=100.0, MA=100.0, MB=100.0, MC=100.0)
    assert pytest.approx(cb_uniform, abs=1e-3) == 1.0
    
    # 2. Center concentrated load simply supported beam (triangle moment)
    # Mmax = 100, MA = 50, MB = 100, MC = 50
    # Cb = 12.5*100 / (2.5*100 + 3*50 + 4*100 + 3*50) = 1250 / (250 + 150 + 400 + 150) = 1250 / 950 = 1.316
    cb_center = calculate_cb(Mmax=100.0, MA=50.0, MB=100.0, MC=50.0)
    assert pytest.approx(cb_center, abs=1e-3) == 1.316


def test_steel_beam_ltb_zones():
    """Verify flexural capacity in plastic (Lb <= Lp), inelastic LTB, and elastic LTB zones."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0)
    
    # 1. Fully braced (Lb = 500 mm <= Lp) -> Mn = Mp
    inp_braced = SteelBeamInput(
        H=400.0, B=200.0, tw=8.0, tf=13.0,
        L=6000.0, Lb=500.0, Cb=1.0,
        Mux=150.0, Vu=80.0, material=mat
    )
    res_braced = design_steel_beam(inp_braced)
    assert res_braced.Mn_x == res_braced.Mp_x
    assert res_braced.phi_Mn_x == pytest.approx(0.90 * res_braced.Mp_x, rel=1e-3)
    
    # 2. Inelastic LTB zone (Lp < Lb = 3000 mm < Lr)
    inp_inelastic = SteelBeamInput(
        H=400.0, B=200.0, tw=8.0, tf=13.0,
        L=6000.0, Lb=3000.0, Cb=1.0,
        Mux=150.0, Vu=80.0, material=mat
    )
    res_inelastic = design_steel_beam(inp_inelastic)
    assert res_inelastic.Lp < 3000.0 < res_inelastic.Lr
    assert res_inelastic.Mn_x < res_braced.Mp_x
    
    # 3. Elastic LTB zone (Lb = 10000 mm > Lr)
    inp_elastic = SteelBeamInput(
        H=400.0, B=200.0, tw=8.0, tf=13.0,
        L=12000.0, Lb=10000.0, Cb=1.0,
        Mux=50.0, Vu=30.0, material=mat
    )
    res_elastic = design_steel_beam(inp_elastic)
    assert 10000.0 > res_elastic.Lr
    assert res_elastic.Mn_x < res_inelastic.Mn_x


def test_steel_beam_box_and_serviceability():
    """Verify box section beam design and deflection checking."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0)
    inp_box = SteelBeamInput(
        section_type="BOX",
        B=200.0, H=300.0, tw=9.0,
        L=6000.0, Lb=6000.0,
        Mux=120.0, Muy=20.0, Vu=90.0,
        service_w=12.0, allowable_deflection_ratio=300.0,
        material=mat
    )
    res = design_steel_beam(inp_box)
    assert res.compactness.section_type == SectionType.BOX
    assert res.delta_allow == 6000.0 / 300.0  # 20 mm
    assert res.delta_act > 0.0
    assert res.phi_Mn_x > 0.0
    assert res.phi_Mn_y > 0.0
