"""Tests for 2D Canvas Visualizers and A4 KDS Report Generators."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_visual_canvas_and_vector_serving():
    """Verify 2D Canvas modules and Vector SVG scripts are served properly."""
    # 1. Canvas Core & Renderer
    res_canvas = client.get("/static/js/visual/canvas_renderer.js")
    assert res_canvas.status_code == 200
    assert "CanvasRenderer" in res_canvas.text

    # 2. Draw RC & Steel
    res_rc = client.get("/static/js/visual/draw_rc.js")
    assert res_rc.status_code == 200
    assert "DrawRc" in res_rc.text

    res_steel = client.get("/static/js/visual/draw_steel.js")
    assert res_steel.status_code == 200
    assert "DrawSteel" in res_steel.text

    # 3. Vector Core & RC Sec
    res_vec_core = client.get("/static/js/visual/vector/vector_core.js")
    assert res_vec_core.status_code == 200
    assert "VectorCore" in res_vec_core.text

    res_vec_rc = client.get("/static/js/visual/vector/vector_rc_sec.js")
    assert res_vec_rc.status_code == 200
    assert "VectorRcSec" in res_vec_rc.text

    # 4. Legend Bar
    res_legend = client.get("/static/js/visual/legend_bar.js")
    assert res_legend.status_code == 200
    assert "LegendBar" in res_legend.text

    # 5. Native Renderer2D & WIP Canvas Placeholder
    res_r2d = client.get("/static/js/renderer2d.js")
    assert res_r2d.status_code == 200
    assert "Renderer2D" in res_r2d.text
    assert "renderWIPCanvas" in res_r2d.text


def test_kds_report_renderers_serving():
    """Verify A4 KDS Calculation Report generators and Zoom Controller are served."""
    # 1. Result Renderer (A4 Standard & WIP Sheet)
    res_result = client.get("/static/js/report/result_renderer.js")
    assert res_result.status_code == 200
    assert "ResultRenderer" in res_result.text
    assert "renderA4WIPSheet" in res_result.text

    # 2. Common KDS A4 Calculation Sheet Generator (Legacy 4-pillar eliminated)
    res_report = client.get("/static/js/report/report_common_renderer.js")
    assert res_report.status_code == 200
    assert "ReportCommonRenderer" in res_report.text
    assert "four-pillar-container" not in res_report.text
    assert "pure-white-sheet" in res_report.text

    # 3. Dedicated Member Report Generators
    res_beam_rep = client.get("/static/js/report/redcr/BeamReportGenerator.js")
    assert res_beam_rep.status_code == 200
    assert "RedcrBeamReport" in res_beam_rep.text

    res_col_rep = client.get("/static/js/report/redcr/ColumnCheckReportGenerator.js")
    assert res_col_rep.status_code == 200
    assert "RedcrColumnReport" in res_col_rep.text

    res_steel_rep = client.get("/static/js/report/redcr/SteelReportGenerator.js")
    assert res_steel_rep.status_code == 200
    assert "RedcrSteelReport" in res_steel_rep.text

    # 4. Zoom Controller
    res_zoom = client.get("/static/js/components/zoom_controller.js")
    assert res_zoom.status_code == 200
    assert "ZoomController" in res_zoom.text
