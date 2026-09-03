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


def test_kds_report_renderers_serving():
    """Verify A4 KDS Calculation Report generators and Zoom Controller are served."""
    # 1. Result Renderer
    res_result = client.get("/static/js/report/result_renderer.js")
    assert res_result.status_code == 200
    assert "ResultRenderer" in res_result.text

    # 2. re-DCR Common Renderer
    res_redcr = client.get("/static/js/report/redcr_common_renderer.js")
    assert res_redcr.status_code == 200
    assert "RedcrCommonRenderer" in res_redcr.text

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
