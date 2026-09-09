"""UI Integration Test Suite for Requirement 23:
Phase V1-02 RC Column (rc_column) AltDP-Core Platform Vertical Slice & Online Release.

Tests:
1. Catalog & Dispatcher Online registration with zero WIP degradation.
2. 4-Pane workspace integration (4-subtab form, dual stacked canvas, Tracer KaTeX A4 report).
3. 3 action buttons binding (Apply, Check, AutoDesign).
4. Tracer AST report renderer pure white A4 output.
5. End-to-end API design calculation, schema, and P-M curve integrity.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)

WEB_STATIC_DIR = Path("src/web/static")
JS_DIR = WEB_STATIC_DIR / "js"
TEMPLATES_DIR = Path("src/web/templates")


def test_catalog_rc_column_online_contract():
    """Verify catalog.js registers rc_column as official Online with is_wip: false."""
    catalog_content = (JS_DIR / "catalog.js").read_text(encoding="utf-8")

    assert "rc/column/rc_column" in catalog_content
    assert "is_wip: false" in catalog_content
    assert 'status: "Online"' in catalog_content
    assert "KDS 14 20 20" in catalog_content
    assert "tracer_report_renderer" in catalog_content


def test_index_html_integration_of_rc_column_and_tracer():
    """Verify index.html includes tracer_report_renderer.js and rc_column_module.js."""
    index_html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")

    assert "tracer_report_renderer.js" in index_html
    assert "rc_column_module.js" in index_html
    assert "catalog.js" in index_html
    assert "dispatcher.js" in index_html
    assert "graphic_viewport.js" in index_html


def test_rc_column_module_4_subtabs_and_actions():
    """Verify rc_column_module has 4 subtabs and all 3 action buttons."""
    mod_content = (JS_DIR / "modules" / "rc_column" / "rc_column_module.js").read_text(encoding="utf-8")

    # 4 Subtabs
    assert 'data-tab="section"' in mod_content
    assert 'data-tab="rebar"' in mod_content
    assert 'data-tab="load"' in mod_content
    assert 'data-tab="option"' in mod_content

    # 3 Action Buttons
    assert "btn-col-apply" in mod_content
    assert "btn-col-check" in mod_content
    assert "btn-col-autodesign" in mod_content
    assert "calculateAndRender" in mod_content


def test_tracer_report_renderer_a4_sheet_structure():
    """Verify tracer_report_renderer.js renders pure white A4 sheet with 5-chapter structure."""
    renderer_content = (JS_DIR / "report" / "tracer_report_renderer.js").read_text(encoding="utf-8")

    assert "pure-white-sheet" in renderer_content
    assert "altdp-tracer-report" in renderer_content
    assert "TracerReportRenderer" in renderer_content
    assert "katex-formula-step" in renderer_content
    assert "window.print()" in renderer_content


def test_api_rc_column_design_and_tracer_ast_e2e():
    """Verify /api/rc/column/design returns calculation results, Tracer AST, and parametric CAD geometry."""
    payload = {
        "name": "C-E2E",
        "b": 500.0,
        "h": 500.0,
        "cover": 60.0,
        "bar_diam": 22.0,
        "total_bars": 8,
        "tie_diam": 10.0,
        "tie_spacing": 300.0,
        "fck": 27.0,
        "fy": 400.0,
        "Pu": 1250.0,
        "Mux": 375.0,
        "Muy": 0.0,
        "Vux": 0.0,
        "Vuy": 100.0,
        "Lu": 3000.0,
        "k": 1.0,
        "is_braced": True
    }

    res = client.post("/api/rc/column/design", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True

    data = body["data"]
    # Structural integrity
    assert "pm_dcr" in data["design_forces"]
    assert "shear_dcr_y" in data["shear"]
    assert "tie_check" in data

    # Tracer AST
    assert "tracer" in data
    tracer = data["tracer"]
    assert "chapters" in tracer
    assert len(tracer["chapters"]) >= 5
    assert "summary" in tracer
    assert tracer["summary"]["status"] in ("OK", "NG")

    # Parametric CAD Geometry
    assert "geometry" in data
    geom = data["geometry"]
    assert "boundary" in geom
    assert len(geom["boundary"]) == 4
    assert "rebars" in geom
    assert len(geom["rebars"]) == 8
    assert "stirrups" in geom
    assert "pm_curve_x" in geom
    assert len(geom["pm_curve_x"]["nominal_curve"]) >= 150


def test_api_rc_column_schema_e2e():
    """Verify /api/rc/column/schema returns dynamic form definition with 4 subtabs."""
    res = client.get("/api/rc/column/schema")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert "tabs" in data
    assert "section" in data["tabs"]
    assert "rebar" in data["tabs"]
    assert "load" in data["tabs"]
    assert "option" in data["tabs"]
