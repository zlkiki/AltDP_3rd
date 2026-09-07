"""Tests for Phase 21-4: Vertical Multi-Card Viewport Graphic Information Center Pane 3.

Validates:
1. index.html: Dual vertical viewport stack (#center-pane-container, #viewport-card-geometry, #viewport-card-mechanics, #canvas-geometry, #canvas-mechanics).
2. index.html: Viewport toolbars and action buttons (Fit, Zoom In/Out, Dim, 3D, DCR).
3. graphic_viewport.js: Independent zoom/pan matrices, hover tooltip hit-testing, EventBus integration, legacy canvas bridging.
4. canvas.css: Vertical stack styling, cards, toolbars, buttons, tooltips, dark/light theme support.
5. renderer2d.js & pm_chart.js: renderTopViewportGeometry, renderBottomViewportMechanics, PMChartRenderer multi-canvas bindings.
"""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_pane3_vertical_viewport_stack():
    """Verify presence of 2-tier vertical stacked viewport in index.html."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Container
    assert 'id="center-pane-container"' in html
    assert 'class="center-viewport-stack"' in html

    # Top Viewport: Geometry & Detailing
    assert 'id="viewport-card-geometry"' in html
    assert 'id="canvas-geometry"' in html
    assert 'id="btn-fit-geom"' in html
    assert 'id="btn-zoom-in-geom"' in html
    assert 'id="btn-zoom-out-geom"' in html
    assert 'id="btn-toggle-dim"' in html

    # Bottom Viewport: Mechanics & P-M Diagram
    assert 'id="viewport-card-mechanics"' in html
    assert 'id="canvas-mechanics"' in html
    assert 'id="btn-fit-mech"' in html
    assert 'id="btn-toggle-3d"' in html
    assert 'id="btn-toggle-dcr-bar"' in html
    assert 'id="dcrCard"' in html
    assert 'id="dcrValue"' in html
    assert 'id="dcrBar"' in html

    # Script tag
    assert "/static/js/components/graphic_viewport.js" in html


def test_graphic_viewport_js_specifications():
    """Verify graphic_viewport.js implementation matches Req 21-4 specifications."""
    res = client.get("/static/js/components/graphic_viewport.js")
    assert res.status_code == 200
    js = res.text

    # Core class and global export
    assert "class GraphicViewport" in js
    assert "global.GraphicViewport = instance;" in js

    # Independent Viewport States
    assert "this.geomState" in js
    assert "this.mechState" in js
    assert "showDimensions" in js
    assert "is3DMode" in js
    assert "interactiveElements" in js

    # Methods
    assert "zoomAt(" in js
    assert "zoomStep(" in js
    assert "fitViewport(" in js
    assert "_handleHoverTooltip(" in js
    assert "renderGeometry(" in js
    assert "renderMechanics(" in js
    assert "setMember(" in js
    assert "setCalculationResult(" in js

    # Tooltip and DOM IDs
    assert "viewport-canvas-tooltip" in js
    assert "canvas-geometry" in js
    assert "canvas-mechanics" in js


def test_canvas_css_phase21_4_styles():
    """Verify canvas.css contains styles for 2-tier vertical stack and toolbars."""
    res = client.get("/static/css/canvas.css")
    assert res.status_code == 200
    css = res.text

    assert ".center-viewport-stack" in css
    assert ".viewport-card" in css
    assert ".viewport-toolbar" in css
    assert ".viewport-title" in css
    assert ".viewport-actions" in css
    assert ".btn-tool" in css
    assert ".btn-tool.active" in css
    assert ".canvas-wrapper" in css
    assert ".canvas-tooltip" in css
    assert ".dcr-summary-card" in css
    assert ".dcr-gauge-bar" in css
    assert 'body[data-theme="light"] .viewport-card' in css


def test_renderer2d_top_and_bottom_viewports():
    """Verify renderer2d.js exports functions for top geometry and bottom mechanics."""
    res = client.get("/static/js/renderer2d.js")
    assert res.status_code == 200
    js = res.text

    assert "Renderer2D.renderTopViewportGeometry" in js
    assert "Renderer2D.renderBottomViewportMechanics" in js
    assert "showDimensions" in js
    assert "interactiveElements" in js
    assert "is3DMode" in js


def test_pm_chart_js_canvas_bindings():
    """Verify pm_chart.js supports canvas-mechanics and fallback."""
    res = client.get("/static/js/pm_chart.js")
    assert res.status_code == 200
    js = res.text

    assert "canvas-mechanics" in js
    assert "PMChartRenderer" in js
