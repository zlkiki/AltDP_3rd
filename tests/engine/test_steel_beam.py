"""Unit tests for Steel Beam design calculations."""

import pytest
from src.engine.steel.beam import SteelBeamInput, design_steel_beam


@pytest.mark.engine
def test_steel_beam_compact_safe():
    inp = SteelBeamInput(
        H=400.0,
        B=200.0,
        tw=8.0,
        tf=13.0,
        Lb=3000.0,
        Mu=180.0,
        Vu=120.0
    )
    res = design_steel_beam(inp)
    
    assert res.is_flange_compact is True
    assert res.is_web_compact is True
    assert res.Mp > 250.0
    assert res.phi_Mn > 180.0
    assert res.flexure_dcr <= 1.0
    assert res.is_safe is True
