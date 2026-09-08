"""
Tests for Requirement 22-3 (Phase V1-1 Step 3):
RC Beam 2D VDraw Canvas Detailing & Force Envelopes (vector_rc_beam.js)
"""
import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_vector_rc_beam_js_serving():
    """Verify that vector_rc_beam.js is served with HTTP 200 OK."""
    response = client.get("/static/js/visual/vector_rc_beam.js")
    assert response.status_code == 200
    content = response.text
    assert "VectorRCBeam" in content
    assert "renderLongitudinalView" in content
    assert "renderCrossSections" in content


def test_index_html_contains_vector_rc_beam():
    """Verify that index.html contains script tag for vector_rc_beam.js."""
    response = client.get("/")
    assert response.status_code == 200
    assert "vector_rc_beam.js" in response.text


def test_vector_rc_beam_specifications():
    """Verify implementation details in vector_rc_beam.js."""
    response = client.get("/static/js/visual/vector_rc_beam.js")
    assert response.status_code == 200
    content = response.text

    # 1. Dual Viewport methods
    assert "renderLongitudinalView" in content
    assert "renderCrossSections" in content

    # 2. Viewport A features: Hinge/Roller, L/4 & L/2 partition, hooks, BMD, SFD
    assert "End-I (L/4" in content
    assert "Center-M (L/2" in content
    assert "End-J (L/4" in content
    assert "Mu_pos" in content
    assert "Mu_neg" in content
    assert "Vu" in content
    assert "BMD" in content
    assert "SFD" in content

    # 3. Viewport B features: 3 stations, 135-deg hook, multi-layer, torsion side
    assert "slotKeys" in content or "end_i" in content
    assert "135" in content
    assert "rebar_top1" in content or "Top Layer 1" in content
    assert "interactiveElements" in content


def test_renderer2d_dispatches_to_vector_rc_beam():
    """Verify that renderer2d.js dispatches rc_beam to VectorRCBeam."""
    response = client.get("/static/js/renderer2d.js")
    assert response.status_code == 200
    content = response.text
    assert "VectorRCBeam" in content
    assert "renderLongitudinalView" in content
    assert "renderCrossSections" in content


def test_rc_beam_module_uses_vector_rc_beam_or_graphic_viewport():
    """Verify that rc_beam_module.js integrates with GraphicViewport and VectorRCBeam."""
    response = client.get("/static/js/modules/rc_beam/rc_beam_module.js")
    assert response.status_code == 200
    content = response.text
    assert "GraphicViewport" in content
    assert "VectorRCBeam" in content
