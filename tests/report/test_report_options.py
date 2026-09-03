"""Tests for SVG Vector Graphics Embedding and Unit Converter Precision.

Conforms to Requirement 15-2.
"""

import pytest
from src.report.unit_converter import UnitConverter
from src.report.svg_drawer import (
    draw_rc_beam_section_svg,
    draw_rc_column_section_svg,
    draw_pm_diagram_svg,
    draw_fem_contour_svg,
)


def test_unit_converter_force():
    """Verify bidirectional force conversion between SI, MKS, and US."""
    # 100 kN to MKS (tonf)
    mks_val, mks_unit = UnitConverter.convert_force(100.0, "MKS")
    assert abs(mks_val - 10.197) < 0.01
    assert mks_unit == "tonf"

    # 100 kN to US (kip)
    us_val, us_unit = UnitConverter.convert_force(100.0, "US")
    assert abs(us_val - 22.48) < 0.05
    assert us_unit == "kip"

    # Formatting string
    fmt = UnitConverter.format_force(150.0, "MKS")
    assert "tonf" in fmt


def test_unit_converter_moment():
    """Verify moment conversion between SI, MKS, and US."""
    # 200 kN*m to MKS (tonf*m)
    mks_val, mks_unit = UnitConverter.convert_moment(200.0, "MKS")
    assert abs(mks_val - 20.39) < 0.05
    assert mks_unit == "tonf·m"

    # 200 kN*m to US (ft*kip)
    us_val, us_unit = UnitConverter.convert_moment(200.0, "US")
    assert abs(us_val - 147.51) < 0.1
    assert us_unit == "ft·kip"


def test_unit_converter_stress():
    """Verify stress conversion between MPa, kgf/cm², and ksi."""
    # 24 MPa to MKS (kgf/cm²)
    mks_val, mks_unit = UnitConverter.convert_stress(24.0, "MKS")
    assert abs(mks_val - 244.73) < 0.1
    assert mks_unit == "kgf/cm²"

    # 24 MPa to US (ksi)
    us_val, us_unit = UnitConverter.convert_stress(24.0, "US")
    assert abs(us_val - 3.48) < 0.05
    assert us_unit == "ksi"


def test_svg_fem_contour_generation():
    """Verify FEM plate stress/moment contour SVG generation."""
    svg = draw_fem_contour_svg(nx=4, ny=4, title="Slab Bending Moment Contour")
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Slab Bending Moment Contour" in svg
    assert "Min (Safe)" in svg
    assert "Max (Critical)" in svg


def test_svg_rebar_and_pm_generation():
    """Verify RC beam and P-M diagram SVG generation."""
    svg_beam = draw_rc_beam_section_svg(b=400, h=600, top_rebars=3, bot_rebars=4)
    assert "<svg" in svg_beam
    assert "b=400" in svg_beam
    assert "h=600" in svg_beam

    svg_pm = draw_pm_diagram_svg([(0, 4000), (300, 1500)], [(0, 3200), (250, 1200)], (1500, 200))
    assert "<svg" in svg_pm
    assert "Bending Moment" in svg_pm
    assert "Axial Load" in svg_pm
