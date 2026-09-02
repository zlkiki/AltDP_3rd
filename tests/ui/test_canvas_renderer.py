"""Tests for 2D Section Canvas Renderer and Static Assets."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_renderer2d_js_serving():
    """Verify renderer2d.js static script serving and essential drawing functions."""
    response = client.get("/static/js/renderer2d.js")
    assert response.status_code == 200
    js = response.text
    
    # Check all key member drawing function signatures
    assert "drawRCBeamSection" in js
    assert "drawRCColumnSection" in js
    assert "drawRCWallSection" in js
    assert "drawSteelSection" in js
    assert "drawCFTSection" in js
    assert "drawRetrofitSection" in js
    assert "drawDimension" in js
    assert "drawRebar" in js


def test_pm_chart_js_serving():
    """Verify pm_chart.js static script serving and P-M curve rendering methods."""
    response = client.get("/static/js/pm_chart.js")
    assert response.status_code == 200
    js = response.text
    
    assert "class PMChartRenderer" in js
    assert "render(data)" in js
    assert "phi_Pn" in js
    assert "phi_Mn" in js


def test_app_js_serving():
    """Verify app.js frontend client controller."""
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    js = response.text
    
    assert "calculateRcBeam" in js
    assert "calculateRcColumn" in js
    assert "calculateRcWall" in js
    assert "calculateSteelBeam" in js
    assert "calculateCftColumn" in js
    assert "calculateRetrofit" in js
    assert "btnThemeToggle" in js
