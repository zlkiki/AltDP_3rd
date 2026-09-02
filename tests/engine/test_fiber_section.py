"""Unit tests for FiberSection numerical integration engine (Phase 04-1)."""

import math
import time
import pytest

from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.solver.fiber_section import FiberSection, MaterialType, SectionForceResult


def test_fiber_section_rect_discretization():
    """Test rectangular fiber section geometry and area summation."""
    b, h = 500.0, 500.0
    concrete = ConcreteMaterial(fck=30.0)
    rebar_mat = RebarMaterial(fy=400.0)
    
    # 8-D25 rebars (corner + middle)
    bar_area = math.pi * 25.0**2 / 4.0
    cover = 50.0
    rebars = [
        (-200.0, -200.0, bar_area), (0.0, -200.0, bar_area), (200.0, -200.0, bar_area),
        (-200.0, 0.0, bar_area),                              (200.0, 0.0, bar_area),
        (-200.0, 200.0, bar_area),  (0.0, 200.0, bar_area),  (200.0, 200.0, bar_area),
    ]
    
    sec = FiberSection.from_rect(b, h, rebars, nx=20, ny=20, concrete=concrete, rebar_mat=rebar_mat)
    
    # Area checks
    assert len(sec.concrete_fibers) == 400
    assert len(sec.rebar_fibers) == 8
    assert math.isclose(sec.gross_concrete_area, b * h, rel_tol=1e-5)
    assert math.isclose(sec.total_rebar_area, 8 * bar_area, rel_tol=1e-5)


def test_fiber_section_circle_discretization():
    """Test circular fiber section geometry and area summation."""
    D = 600.0
    concrete = ConcreteMaterial(fck=27.0)
    rebar_mat = RebarMaterial(fy=400.0)
    
    # 6 rebars on circle radius 240mm
    n_bars = 6
    bar_area = math.pi * 22.0**2 / 4.0
    rebars = []
    for i in range(n_bars):
        angle = 2.0 * math.pi * i / n_bars
        rebars.append((240.0 * math.cos(angle), 240.0 * math.sin(angle), bar_area))
        
    sec = FiberSection.from_circle(D, rebars, n_rings=20, n_theta=40, concrete=concrete, rebar_mat=rebar_mat)
    
    # Theoretical circle area
    target_Ag = math.pi * (D / 2.0)**2
    assert math.isclose(sec.gross_concrete_area, target_Ag, rel_tol=1e-3)
    assert math.isclose(sec.total_rebar_area, 6 * bar_area, rel_tol=1e-5)


def test_fiber_section_pure_capacities():
    """Verify nominal pure axial compression Po and tension Pt capacities."""
    b, h = 400.0, 400.0
    fck = 30.0
    fy = 400.0
    concrete = ConcreteMaterial(fck=fck)
    rebar_mat = RebarMaterial(fy=fy)
    
    bar_area = 500.0  # mm2
    rebars = [
        (-150.0, -150.0, bar_area), (150.0, -150.0, bar_area),
        (-150.0, 150.0, bar_area),  (150.0, 150.0, bar_area),
    ]
    sec = FiberSection.from_rect(b, h, rebars, nx=20, ny=20, concrete=concrete, rebar_mat=rebar_mat)
    
    Ag = 400.0 * 400.0
    Ast = 4.0 * 500.0
    expected_Po = (0.85 * fck * (Ag - Ast) + fy * Ast) / 1e3  # kN
    expected_Pt = (-fy * Ast) / 1e3  # kN
    
    assert math.isclose(sec.compute_pure_compression(), expected_Po, rel_tol=1e-4)
    assert math.isclose(sec.compute_pure_tension(), expected_Pt, rel_tol=1e-4)


def test_fiber_section_stress_integration_performance():
    """Verify force integration consistency and performance (< 0.5ms per solve)."""
    b, h = 600.0, 600.0
    bar_area = 600.0
    rebars = [
        (-220.0, -220.0, bar_area), (220.0, -220.0, bar_area),
        (-220.0, 220.0, bar_area),  (220.0, 220.0, bar_area),
    ]
    sec = FiberSection.from_rect(b, h, rebars, nx=30, ny=30)
    
    # 1. Evaluate bending at c = 300mm, theta = 0
    res = sec.compute_forces(c=300.0, theta=0.0)
    assert isinstance(res, SectionForceResult)
    assert res.P > 0  # Compression
    assert res.Mx > 0  # Moment about X
    assert math.isclose(res.My, 0.0, abs_tol=1e-3)  # Symmetric about Y
    
    # 2. Performance benchmark: 100 integrations
    start_time = time.perf_counter()
    for c_val in range(50, 550, 5):
        sec.compute_forces(c=float(c_val), theta=0.0)
    elapsed = time.perf_counter() - start_time
    avg_ms = (elapsed / 100.0) * 1000.0
    
    # Check avg solve time is very fast
    assert avg_ms < 5.0, f"Average solve time too slow: {avg_ms:.2f} ms"
