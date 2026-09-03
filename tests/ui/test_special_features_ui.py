"""Tests for Phase 19-5 Special Features Integration in Web UI."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_special_feature_buttons_in_index_html():
    """Verify presence of CAD DXF, Quantity Takeoff, 3D P-M, and Gen Import in index.html."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Check button IDs
    assert 'id="btn-open-dxf"' in html
    assert 'id="btn-open-quantity"' in html
    assert 'id="btn-toggle-pm"' in html
    assert 'id="btn-import-gen"' in html
    assert 'id="gen-file-importer"' in html
    assert 'id="pmChartCanvas"' in html


def test_cad_dxf_export_endpoint():
    """Verify CAD DXF export API endpoint works."""
    resp = client.post("/api/v1/project/cad/export-dxf?member_type=BEAM&name=B1&b=400&h=600")
    assert resp.status_code == 200
    assert "attachment; filename=B1_Rebar_Detail.dxf" in resp.headers.get("content-disposition", "")
    assert len(resp.content) > 100


def test_quantity_excel_export_endpoint():
    """Verify Quantity Takeoff Excel export API endpoint works."""
    resp = client.get("/api/v1/project/quantity/export-excel")
    assert resp.status_code == 200
    assert "attachment; filename=Project_Quantity_Summary.xlsx" in resp.headers.get("content-disposition", "")
    assert len(resp.content) > 100


def test_app_js_special_features_handlers():
    """Verify app.js includes event handlers for all advanced Phase 19-5 features."""
    resp = client.get("/static/js/app.js")
    assert resp.status_code == 200
    js = resp.text

    assert "btn-open-dxf" in js
    assert "btn-open-quantity" in js
    assert "btn-toggle-pm" in js
    assert "btn-import-gen" in js
    assert "PMChartRenderer" in js
