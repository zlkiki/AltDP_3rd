"""Unit tests for RC Beam Serviceability (Deflection, Crack) and Auto-Design Rebar Layout."""

import pytest
import math
from src.engine.rc.beam import RCBeamInput, design_rc_beam
from src.engine.rc.rebar_layout import (
    REBAR_DB,
    calculate_bar_spacing_capacity,
    create_rebar_arrangement,
    auto_design_beam_rebar
)


@pytest.mark.engine
def test_rc_beam_branson_effective_inertia_and_deflection():
    """Verify Branson Ie, elastic deflection, and long-term deflection."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,  # 5-D22
        As_prime=0.0,
        Mu=250.0,
        Vu=120.0,
        Ma=140.0,   # Service moment > Mcr
        span_length=6000.0, # 6m span
        sustained_ratio=0.7,
        time_duration_months=60
    )
    res = design_rc_beam(inp)
    
    assert res.Ig > res.Icr
    assert res.Icr <= res.Ie <= res.Ig
    assert res.Mcr > 0.0
    assert res.delta_elastic > 0.0
    assert res.lambda_delta == pytest.approx(2.0, rel=1e-2)  # xi = 2.0 for 5 years, rho_prime = 0
    assert res.delta_long > 0.0
    assert res.delta_total == pytest.approx(res.delta_elastic + res.delta_long, rel=1e-3)
    assert res.delta_allowable == 6000.0 / 240.0  # 25.0 mm
    assert res.deflection_dcr < 1.0


@pytest.mark.engine
def test_rc_beam_crack_width():
    """Verify crack width calculation."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=40.0,
        As=1935.0,
        Ma=160.0,
        w_lim=0.3
    )
    res = design_rc_beam(inp)
    
    assert res.fs_service > 0.0
    assert 0.02 <= res.crack_width <= 0.35
    assert res.crack_dcr > 0.0


@pytest.mark.engine
def test_rebar_layout_single_layer():
    """Test 1-layer rebar spacing and arrangement."""
    max_bars, clear_spacing = calculate_bar_spacing_capacity(
        b=400.0,
        bar_size="D22",
        cover=40.0,
        stirrup_db=9.53,
        max_aggregate=25.0
    )
    # Clear width = 400 - 2*(40+9.53) = 300.94mm
    # Min clear spacing = max(25, 22.2, 33.25) = 33.25mm
    # max_bars = floor((300.94 + 33.25) / (22.2 + 33.25)) = floor(334.19 / 55.45) = 6
    assert max_bars >= 4
    
    arr = create_rebar_arrangement(
        b=400.0,
        h=600.0,
        bar_size="D22",
        num_bars=4,
        cover=40.0
    )
    assert arr.is_valid is True
    assert arr.num_layers == 1
    assert len(arr.layers[0].x_coords) == 4
    assert arr.layers[0].clear_spacing >= 33.0


@pytest.mark.engine
def test_rebar_layout_two_layers():
    """Test 2-layer rebar division when bar count exceeds single layer capacity."""
    arr = create_rebar_arrangement(
        b=300.0,
        h=600.0,
        bar_size="D25",
        num_bars=6,  # 6-D25 in b=300 requires 2 layers
        cover=40.0
    )
    assert arr.num_layers == 2
    assert len(arr.layers) == 2
    assert arr.layers[0].num_bars + arr.layers[1].num_bars == 6
    assert arr.effective_d < 600.0 - 50.0  # Centroid raised due to 2 layers


@pytest.mark.engine
def test_auto_design_beam_rebar():
    """Test automatic optimal rebar design selection."""
    As_req = 1800.0  # mm2
    result = auto_design_beam_rebar(
        b=400.0,
        h=600.0,
        As_req=As_req,
        cover=40.0,
        stirrup_size="D10"
    )
    assert result.selected_arrangement is not None
    assert result.selected_arrangement.total_area >= As_req
    assert result.selected_arrangement.is_valid is True
    assert len(result.all_candidates) > 0
