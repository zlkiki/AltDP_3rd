"""Unit tests for PMDiagramSolver 2D/3D interaction engine (Phase 04-2)."""

import math
import pytest

from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.solver.fiber_section import FiberSection
from src.engine.solver.pm_diagram import PMDiagramSolver, PMDiagramResult


@pytest.fixture
def sample_column_section():
    """600x600 column with 12-D25 rebars."""
    b, h = 600.0, 600.0
    concrete = ConcreteMaterial(fck=30.0)
    rebar_mat = RebarMaterial(fy=400.0)
    bar_area = math.pi * 25.0**2 / 4.0
    
    # 4 on top, 4 on bottom, 2 on left, 2 on right (12 total)
    rebars = [
        # Top line (y = 230)
        (-230.0, 230.0, bar_area), (-76.7, 230.0, bar_area), (76.7, 230.0, bar_area), (230.0, 230.0, bar_area),
        # Middle sides (y = 76.7, y = -76.7)
        (-230.0, 76.7, bar_area), (230.0, 76.7, bar_area),
        (-230.0, -76.7, bar_area), (230.0, -76.7, bar_area),
        # Bottom line (y = -230)
        (-230.0, -230.0, bar_area), (-76.7, -230.0, bar_area), (76.7, -230.0, bar_area), (230.0, -230.0, bar_area),
    ]
    return FiberSection.from_rect(b, h, rebars, nx=20, ny=20, concrete=concrete, rebar_mat=rebar_mat)


def test_2d_pm_diagram_generation(sample_column_section):
    """Verify 2D P-M interaction diagram generation and KDS limit checks."""
    diag = PMDiagramSolver.generate_2d_diagram(sample_column_section, theta=0.0, num_points=40)
    
    assert isinstance(diag, PMDiagramResult)
    assert len(diag.points) >= 40
    
    # Check max design axial compression upper limit (0.80 * 0.65 * Po for tied)
    expected_phi_Pn_max = 0.80 * 0.65 * diag.Po
    assert math.isclose(diag.phi_Pn_max, expected_phi_Pn_max, rel_tol=1e-3)
    
    # Check max point in list equals phi_Pn_max
    assert math.isclose(diag.points[0].phi_Pn, diag.phi_Pn_max, rel_tol=1e-3)
    
    # Check pure tension at the bottom
    expected_phi_Pt = 0.85 * diag.Pt
    assert math.isclose(diag.points[-1].phi_Pn, expected_phi_Pt, rel_tol=1e-3)


def test_phi_transition_on_pm_curve(sample_column_section):
    """Verify phi transition from 0.65 to 0.85 along the curve."""
    diag = PMDiagramSolver.generate_2d_diagram(sample_column_section, theta=0.0, num_points=50)
    
    phi_values = [p.phi for p in diag.points]
    # Pure compression has phi = 0.65
    assert phi_values[0] == 0.65
    # Bottom pure tension has phi = 0.85
    assert phi_values[-1] == 0.85
    # All phi values in [0.65, 0.85]
    assert all(0.65 <= phi <= 0.85 for phi in phi_values)


def test_3d_pm_surface_mesh(sample_column_section):
    """Verify 3D surface mesh generation structure."""
    surface = PMDiagramSolver.generate_3d_surface(sample_column_section, num_theta=8, num_points_per_ray=20)
    
    assert len(surface) == 8
    assert "theta_deg" in surface[0]
    assert len(surface[0]["points"]) >= 20
    assert "phi_Mux" in surface[0]["points"][0]
    assert "phi_Muy" in surface[0]["points"][0]


def test_dcr_evaluation_safe_and_unsafe(sample_column_section):
    """Verify DCR calculation for safe, marginal, and unsafe load points."""
    # 1. Moderate safe load: Pu = 2000 kN, Mux = 300 kNm, Muy = 0
    res_safe = PMDiagramSolver.calculate_dcr(sample_column_section, Pu=2000.0, Mux=300.0, Muy=0.0)
    assert res_safe["is_safe"] is True
    assert 0.0 < res_safe["dcr"] < 1.0
    assert res_safe["status"] == "OK"
    
    # 2. Overloaded moment: Pu = 2000 kN, Mux = 1500 kNm, Muy = 0
    res_over = PMDiagramSolver.calculate_dcr(sample_column_section, Pu=2000.0, Mux=1500.0, Muy=0.0)
    assert res_over["is_safe"] is False
    assert res_over["dcr"] > 1.0
    assert res_over["status"] == "NG"
    
    # 3. Axial force exceeding phi_Pn_max
    res_axial_ng = PMDiagramSolver.calculate_dcr(sample_column_section, Pu=10000.0, Mux=50.0, Muy=0.0)
    assert res_axial_ng["is_safe"] is False
    assert res_axial_ng["status"] == "NG_AXIAL_EXCEEDED"
    
    # 4. Biaxial load: Pu = 2000 kN, Mux = 250 kNm, Muy = 250 kNm
    res_biaxial = PMDiagramSolver.calculate_dcr(sample_column_section, Pu=2000.0, Mux=250.0, Muy=250.0)
    assert "dcr" in res_biaxial
    assert res_biaxial["theta_deg"] == pytest.approx(45.0, abs=1.0)
