"""Unit tests for RC Beam complete strength design calculations (KDS 14 20 20 / KDS 14 20 22)."""

import pytest
import math
from src.engine.rc.beam import RCBeamInput, design_rc_beam
from src.engine.db.materials import ConcreteMaterial, RebarMaterial


@pytest.mark.engine
def test_rc_beam_singly_reinforced_safe():
    """Test standard singly reinforced beam flexure & shear capacity."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,  # 5-D22
        As_prime=0.0,
        Av=142.6,   # 2-D10
        s=200.0,
        Mu=250.0,
        Vu=150.0,
        Tu=0.0
    )
    res = design_rc_beam(inp)
    
    assert res.d == 550.0
    assert res.Mn > 350.0
    assert res.phi_Mn > 250.0
    assert res.flexure_dcr <= 1.0
    assert res.phi_Vn > 150.0
    assert res.shear_dcr <= 1.0
    assert res.is_torsion_ignored is True
    assert res.is_safe is True


@pytest.mark.engine
def test_rc_beam_doubly_reinforced_yielding():
    """Test doubly reinforced beam where compression steel yields."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        cover_prime=50.0,
        As=3870.0,       # 10-D22 (Heavy tension steel)
        As_prime=1140.0, # 4-D19 (Compression steel)
        Av=285.0,        # 4-D10
        s=150.0,
        Mu=500.0,
        Vu=200.0
    )
    res = design_rc_beam(inp)
    
    # Compression steel should contribute to higher flexural capacity
    assert res.is_top_yielding is True
    assert res.fs_prime == pytest.approx(400.0, rel=1e-2)
    assert res.phi_Mn > 500.0
    assert res.flexure_dcr <= 1.0


@pytest.mark.engine
def test_rc_beam_torsion_and_shear_interaction():
    """Test beam under combined shear and torsional moment."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        side_cover=40.0,
        As=2500.0,
        Av=142.6,
        s=150.0,
        Mu=200.0,
        Vu=120.0,
        Tu=35.0   # Substantial torsion
    )
    res = design_rc_beam(inp)
    
    # Torsion should NOT be ignored
    assert res.is_torsion_ignored is False
    assert res.Tcr > 0.0
    assert res.At_over_s_req > 0.0
    assert res.Al_req > 0.0
    assert res.combined_stress > 0.0
    assert res.combined_limit > 0.0
    assert res.combined_dcr > 0.0


@pytest.mark.engine
def test_rc_beam_torsion_below_threshold():
    """Test beam under negligible torsion (Tu <= Tth)."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,
        Av=142.6,
        s=200.0,
        Mu=200.0,
        Vu=100.0,
        Tu=3.0    # Very small torsion
    )
    res = design_rc_beam(inp)
    
    assert res.is_torsion_ignored is True
    assert res.torsion_dcr == 0.0


@pytest.mark.engine
def test_rc_beam_overloaded_moment_and_shear():
    """Test overloaded beam failing flexure and shear checks."""
    inp = RCBeamInput(
        b=300.0,
        h=500.0,
        cover=50.0,
        As=1000.0,
        Av=142.6,
        s=300.0,
        Mu=600.0,  # Unrealistic high moment
        Vu=500.0   # Unrealistic high shear
    )
    res = design_rc_beam(inp)
    
    assert res.flexure_dcr > 1.0
    assert res.shear_dcr > 1.0
    assert res.is_safe is False
    assert "[NG]" in res.summary
