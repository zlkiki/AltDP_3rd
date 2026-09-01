"""Unit tests for material models and KDS reduction factors."""

import pytest
from src.engine.db.materials import ConcreteMaterial, RebarMaterial, SteelMaterial, get_phi_flexure


@pytest.mark.engine
def test_concrete_properties(default_concrete):
    assert default_concrete.fck == 24.0
    assert default_concrete.alpha1 == 0.85
    assert default_concrete.beta1 == 0.85
    assert default_concrete.Ec > 20000.0


@pytest.mark.engine
def test_concrete_high_strength():
    c40 = ConcreteMaterial(fck=40.0)
    assert c40.beta1 < 0.85
    assert c40.beta1 >= 0.65


@pytest.mark.engine
def test_rebar_properties(default_rebar):
    assert default_rebar.fy == 400.0
    assert default_rebar.ey == 400.0 / 200000.0


@pytest.mark.engine
def test_phi_reduction_factor():
    # Tension-controlled (et >= 0.005)
    assert get_phi_flexure(0.006, 0.002) == 0.85
    # Compression-controlled (et <= ey)
    assert get_phi_flexure(0.001, 0.002) == 0.65
    # Transition zone
    phi_mid = get_phi_flexure(0.0035, 0.002)
    assert 0.65 < phi_mid < 0.85
