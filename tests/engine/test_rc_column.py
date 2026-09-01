"""Unit tests for RC Column and P-M diagram generation."""

import pytest
from src.engine.rc.column import RCColumnInput, design_rc_column


@pytest.mark.engine
def test_rc_column_pm_curve():
    inp = RCColumnInput(
        b=600.0,
        h=600.0,
        cover=60.0,
        bar_diam=25.0,
        total_bars=12,
        Pu=2500.0,
        Mu=350.0
    )
    res = design_rc_column(inp)
    
    assert res.Ag == 360000.0
    assert res.Ast > 5000.0
    assert 0.01 <= res.rho_g <= 0.08
    assert res.Pn_max > 5000.0
    assert len(res.pm_curve) >= 20
    assert res.dcr > 0.0
    assert res.is_safe is True
