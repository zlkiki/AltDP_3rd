"""Unit tests for Section Properties Calculation Engine (Phase 02-2)."""

import pytest
import math
from src.engine.db.section_properties import (
    SectionPropertiesCalculator,
    CalculatedSectionProperties
)


@pytest.mark.engine
def test_h_section_properties_h400x200():
    """Test H-400x200x8x13 properties against standard structural tables."""
    # H = 400, B = 200, tw = 8, tf = 13, r = 16
    props = SectionPropertiesCalculator.calc_h_section(
        H=400.0, B=200.0, tw=8.0, tf=13.0, r=16.0, name="H-400x200x8x13"
    )

    # Standard values for H-400x200x8x13:
    # Area ~ 84.12 cm2 (without fillet ~ 81.92)
    assert 80.0 <= props.A <= 90.0

    # Ix ~ 23,700 cm4
    assert 22000.0 <= props.Ix <= 25000.0

    # Iy ~ 1,740 cm4
    assert 1600.0 <= props.Iy <= 1900.0

    # Sx ~ 1,190 cm3
    assert 1100.0 <= props.Sx <= 1300.0

    # Zx ~ 1,320 cm3
    assert 1250.0 <= props.Zx <= 1450.0

    # rx ~ 16.8 cm, ry ~ 4.54 cm
    assert 15.0 <= props.rx <= 18.0
    assert 4.0 <= props.ry <= 5.5

    # J, Cw must be positive
    assert props.J > 0
    assert props.Cw > 0
    assert props.weight > 0


@pytest.mark.engine
def test_box_section_properties():
    """Test RHS 200x200x9 properties."""
    props = SectionPropertiesCalculator.calc_box_section(
        H=200.0, B=200.0, t=9.0, r_out=18.0, name="RHS-200x200x9"
    )

    # Area: ~ 68.76 cm2 (exact approx)
    assert 60.0 <= props.A <= 75.0

    # For symmetric box, Ix == Iy
    assert math.isclose(props.Ix, props.Iy, rel_tol=1e-3)
    assert math.isclose(props.Sx, props.Sy, rel_tol=1e-3)
    assert math.isclose(props.Zx, props.Zy, rel_tol=1e-3)
    assert props.J > 0


@pytest.mark.engine
def test_pipe_section_properties():
    """Test CHS 216.3x5.8 properties."""
    D = 216.3
    t = 5.8
    props = SectionPropertiesCalculator.calc_pipe_section(D=D, t=t, name="PIPE-216.3x5.8")

    # A = pi/4 * (216.3^2 - 204.7^2) / 100 = ~ 38.35 cm2
    assert 35.0 <= props.A <= 42.0
    assert props.Ix == props.Iy
    assert props.Sx == props.Sy
    assert props.J == pytest.approx(2.0 * props.Ix, rel=1e-3)


@pytest.mark.engine
def test_channel_section_properties():
    """Test Channel 200x80x7.5x11 properties."""
    props = SectionPropertiesCalculator.calc_channel_section(
        H=200.0, B=80.0, tw=7.5, tf=11.0, name="Channel-200x80"
    )

    assert props.A > 0
    assert props.Ix > props.Iy
    assert props.xc > 0
    assert props.xs > 0
    assert props.Cw > 0


@pytest.mark.engine
def test_angle_section_properties():
    """Test L-Angle 100x100x10 properties."""
    props = SectionPropertiesCalculator.calc_angle_section(
        H=100.0, B=100.0, t=10.0, name="L-100x100x10"
    )

    assert props.A > 0
    # Equal leg angle: Ix == Iy
    assert math.isclose(props.Ix, props.Iy, rel_tol=1e-2)
    assert props.xc == props.yc
    assert props.theta != 0.0
