"""Unit tests for RC column comprehensive design engine (Phase 04-3)."""

import math
import pytest

from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.column import (
    RCColumnInput,
    evaluate_slenderness,
    design_rc_column,
    RCColumnDesignResult
)


def test_rc_column_slenderness_short_column():
    """Short column (k*Lu/r <= limit) should have delta_ns = 1.0."""
    inp = RCColumnInput(
        b=600.0,
        h=600.0,
        Lu=2000.0,  # Short length
        k=1.0,
        is_braced=True,
        Pu=2000.0,
        Mux=300.0,
        M2x=300.0
    )
    res = evaluate_slenderness(inp)
    
    # r = 0.3 * 600 = 180mm -> slenderness = 2000 / 180 = 11.1 <= 22
    assert res.slenderness_x < 22.0
    assert not res.is_slender_x
    assert res.delta_ns_x == 1.0
    assert res.Mc_x >= inp.M2x


def test_rc_column_slenderness_long_column_magnification():
    """Slender column should magnify moment delta_ns > 1.0 for uniform single curvature bending."""
    inp = RCColumnInput(
        b=400.0,
        h=400.0,
        Lu=6000.0,  # Slender column
        k=1.0,
        is_braced=True,
        Pu=2000.0,
        Mux=150.0,
        M2x=150.0,
        M1x=150.0   # M1/M2 = 1.0 -> Cm = 1.0
    )
    res = evaluate_slenderness(inp)
    
    # r = 0.3 * 400 = 120mm -> slenderness = 6000 / 120 = 50.0 > 22
    assert res.is_slender_x
    assert res.delta_ns_x > 1.0
    assert res.Mc_x > inp.M2x


def test_rc_column_min_eccentricity():
    """Verify minimum eccentricity moment emin = 15 + 0.03*h."""
    inp = RCColumnInput(
        b=500.0,
        h=500.0,
        Lu=2000.0,
        Pu=2000.0,
        Mux=10.0,  # Very small moment
        M2x=10.0
    )
    res = evaluate_slenderness(inp)
    
    # emin = 15 + 0.03 * 500 = 30mm -> M2_min = 2000 * 0.03 = 60 kNm
    assert res.min_eccentricity_x == 30.0
    assert res.Mc_x >= 60.0


def test_rc_column_comprehensive_design_safe():
    """Verify safe column design output structure and KDS compliance."""
    inp = RCColumnInput(
        name="C-Main",
        b=600.0,
        h=600.0,
        cover=60.0,
        bar_diam=25.0,
        total_bars=12,
        tie_diam=10.0,
        tie_spacing=300.0,
        Pu=2200.0,
        Mux=300.0,
        Muy=0.0,
        Vuy=150.0,
        concrete=ConcreteMaterial(fck=30.0),
        rebar=RebarMaterial(fy=400.0)
    )
    result = design_rc_column(inp)
    
    assert isinstance(result, RCColumnDesignResult)
    assert result.is_rho_ok is True
    assert result.is_tie_ok is True
    assert result.is_safe is True
    assert result.pm_dcr < 1.0
    assert result.shear_dcr_y < 1.0
    assert len(result.pm_curve_x) > 0
    assert len(result.pm_curve_y) > 0
