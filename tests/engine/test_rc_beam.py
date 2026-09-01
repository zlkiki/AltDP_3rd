"""Unit tests for RC Beam design calculations."""

import pytest
from src.engine.rc.beam import RCBeamInput, design_rc_beam


@pytest.mark.engine
def test_rc_beam_safe_design():
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,  # 5-D22
        Av=142.6,   # 2-D10
        s=200.0,
        Mu=250.0,
        Vu=150.0
    )
    res = design_rc_beam(inp)
    
    assert res.d == 550.0
    assert res.Mn > 300.0
    assert res.phi_Mn > 250.0
    assert res.flexure_dcr <= 1.0
    assert res.phi_Vn > 150.0
    assert res.shear_dcr <= 1.0
    assert res.is_safe is True


@pytest.mark.engine
def test_rc_beam_overloaded_moment():
    inp = RCBeamInput(
        b=300.0,
        h=500.0,
        cover=50.0,
        As=1000.0,
        Mu=500.0,  # Extremely large moment
        Vu=50.0
    )
    res = design_rc_beam(inp)
    assert res.flexure_dcr > 1.0
    assert res.is_safe is False
