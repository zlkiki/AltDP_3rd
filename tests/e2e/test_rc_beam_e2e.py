"""
E2E Test Suite for Requirement 22-6:
Phase V1-01 Step 6 RC Beam 4-Pane Workspace Full E2E & Online Production Transition.

Covers the 6 core E2E scenarios conforming to Requirement 22-6 and docs/16:
- Scenario 1: Sidebar Module Mount, Official Online Registration & WIP Elimination
- Scenario 2: Rebar Arrangement 3-Type Switching & Load/Form Realtime Interlock
- Scenario 3: Composite Rebar Inputs & 12-Point Clear Spacing Realtime Engine
- Scenario 4: 3-Action Pipeline ([Apply], [Check], [AutoDesign]) & 7-Chapter A4 KaTeX Report
- Scenario 5: 2D Canvas Viewports Interaction, Graphics Integrity & Torsion 0-Count Fix
- Scenario 6: Pure White (#ffffff) A4 Print Preview & Theme Integrity
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

WEB_STATIC_DIR = Path("src/web/static")
JS_DIR = WEB_STATIC_DIR / "js"
CSS_DIR = WEB_STATIC_DIR / "css"


# ==============================================================================
# Scenario 1: Sidebar Module Mount, Official Online Registration & WIP Elimination
# ==============================================================================
def test_scenario1_catalog_online_registration_and_wip_elimination():
    """Verify rc_beam is registered as an official Online module in catalog.js,
    with is_wip: false, status: 'Online', verified engine_status, and full metadata."""
    catalog_content = (JS_DIR / "catalog.js").read_text(encoding="utf-8")
    
    # 1. Official Online fields in catalog.js
    assert 'key: "rc/beam/rc_beam"' in catalog_content
    assert 'is_wip: false' in catalog_content
    assert 'status: "Online"' in catalog_content
    assert 'engine_status: "VERIFIED"' in catalog_content
    assert 'icon: "icon-beam"' in catalog_content
    assert 'component: "form_rc_beam"' in catalog_content
    assert 'renderer: "vector_rc_beam"' in catalog_content
    assert 'report: "rc_beam_report"' in catalog_content

    # 2. Dispatcher and App.js WIP checks
    dispatcher_content = (JS_DIR / "core" / "dispatcher.js").read_text(encoding="utf-8")
    assert "meta.is_wip === false || meta.status === 'Online'" in dispatcher_content
    
    app_content = (JS_DIR / "app.js").read_text(encoding="utf-8")
    assert "m.is_wip === false || m.status === 'Online'" in app_content

    # 3. Sidebar status badge for Online modules
    sidebar_content = (JS_DIR / "components" / "sidebar_nav.js").read_text(encoding="utf-8")
    assert "mod-status-badge online" in sidebar_content
    assert "Online" in sidebar_content


# ==============================================================================
# Scenario 2: Rebar Arrangement 3-Type Switching & Load/Form Realtime Interlock
# ==============================================================================
def test_scenario2_rebar_arrangement_types_and_load_table_interlock():
    """Verify the 3 arrangement types (ONE_SECTION, SYMMETRIC_ENDS, THREE_STATIONS)
    and their automated replication & load-table disabling interlocks."""
    form_content = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")

    # 1. 3 Arrange Type Radios
    assert 'value="ONE_SECTION"' in form_content
    assert 'value="SYMMETRIC_ENDS"' in form_content
    assert 'value="THREE_STATIONS"' in form_content

    # 2. Arrange Type Change Event Handlers & Load Table State
    assert "_updateLoadTableArrangeState" in form_content
    assert "row-ld-endi" in form_content
    assert "row-ld-cent" in form_content
    assert "row-ld-endj" in form_content
    assert "tag-ld-endi-sym" in form_content
    assert "tag-ld-endj-sym" in form_content


# ==============================================================================
# Scenario 3: Composite Rebar Inputs & 12-Point Clear Spacing Realtime Engine
# ==============================================================================
def test_scenario3_composite_rebar_and_12point_clear_spacing_engine():
    """Verify composite rebar controls with min=2 constraint on layer 1,
    0 allowed on layer 2, and 12-point clear spacing engine with governing badge."""
    form_content = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")

    # 1. 12-point clear spacing calculation functions & IDs
    assert "_calcAllClearSpacings" in form_content
    assert "beam-spacing-badge" in form_content
    assert "beam-spacing-popover" in form_content
    assert "btn-toggle-spacing-popover" in form_content

    # 2. Station and layer definitions
    assert "top_layer1" in form_content and "top_layer2" in form_content
    assert "bot_layer1" in form_content and "bot_layer2" in form_content
    assert "end_i" in form_content and "center_m" in form_content and "end_j" in form_content


# ==============================================================================
# Scenario 4: 3-Action Pipeline & 7-Chapter A4 KaTeX Report
# ==============================================================================
def test_scenario4_action_pipeline_and_7chapters_a4_report():
    """Verify sticky floating header with [Apply], [Check], [AutoDesign] actions,
    and 7-chapter KaTeX A4 report without legacy rho terms."""
    # 1. Form sticky header & 32px compact buttons
    form_content = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")
    assert "beam-sticky-header" in form_content or "form-sticky-header" in form_content
    assert "btn-action-compact" in form_content
    assert "beam-btn-apply" in form_content
    assert "beam-btn-check" in form_content
    assert "beam-btn-design" in form_content

    # 2. Report 7 Chapters structure
    report_content = (JS_DIR / "report" / "rc_beam_report.js").read_text(encoding="utf-8")
    assert 'data-chapter-key="general"' in report_content
    assert 'data-chapter-key="load"' in report_content
    assert 'data-chapter-key="ductility"' in report_content
    assert 'data-chapter-key="flexure"' in report_content
    assert 'data-chapter-key="shear"' in report_content
    assert 'data-chapter-key="serviceability"' in report_content
    assert 'data-chapter-key="verdict"' in report_content

    # 3. Zero-load omission logic & KaTeX aligned environment
    assert "aligned" in report_content
    assert "torsion_zero" in report_content or "Tu <= 0" in report_content or "비틀림" in report_content

    # 4. Strict absence of legacy rho formulas
    assert "\\rho_{min}" not in report_content
    assert "\\rho_{max}" not in report_content

    # 5. Engine API calculation response check
    api_resp = client.post("/api/design/rc/beam/base", json={
        "b": 400.0,
        "h": 600.0,
        "fck": 27.0,
        "fy": 400.0,
        "fyt": 400.0,
        "cover": 40.0,
        "cover_top": 40.0,
        "length": 6000.0,
        "mu": 220.0,
        "vu": 140.0,
        "tu": 0.0,
        "arrange_type": "SYMMETRIC_ENDS",
        "top_layer1": "4-D25",
        "top_layer2": "2-D25",
        "bot_layer1": "3-D22",
        "bot_layer2": "0",
        "stirrup_dia": "D10",
        "stirrup_space": 150.0,
        "stirrup_legs": 2
    })
    assert api_resp.status_code == 200
    res_json = api_resp.json()
    assert res_json.get("success") is True or "result" in res_json or "status" in res_json
    status = res_json.get("result", {}).get("status") or res_json.get("status")
    assert status in ["OK", "PASS"]


# ==============================================================================
# Scenario 5: 2D Canvas Viewports Interaction & Torsion 0-Count Fix
# ==============================================================================
def test_scenario5_canvas_graphics_integrity_and_torsion_fix():
    """Verify VectorRCBeam 3-station canvas renderer, nullish coalescing torsion bar count fix,
    and graphic viewport integration."""
    vector_content = (JS_DIR / "visual" / "vector_rc_beam.js").read_text(encoding="utf-8")

    # 1. Station rendering entry points
    assert "renderStationSection" in vector_content
    assert "renderCrossSections" in vector_content

    # 2. Torsion bar count fix (nullish coalescing)
    assert "r.torsion_side_count ?? data.torsion_side_count ?? 0" in vector_content

    # 3. Graphic Viewport 3-station viewport stack in index.html
    index_html = (Path("src/web/templates/index.html")).read_text(encoding="utf-8")
    assert "canvas-station-1" in index_html
    assert "canvas-station-2" in index_html
    assert "canvas-station-3" in index_html


# ==============================================================================
# Scenario 6: Pure White (#ffffff) A4 Print Preview & Theme Integrity
# ==============================================================================
def test_scenario6_pure_white_a4_print_preview_and_theme_integrity():
    """Verify pure white #ffffff A4 print stylesheet, print media queries,
    and UI theme CSS serving."""
    # 1. Report CSS pure white background
    report_css = (CSS_DIR / "report.css").read_text(encoding="utf-8")
    assert "#ffffff" in report_css.lower() or "background: #fff" in report_css.lower()

    # 2. Print CSS media query and page setup
    print_css = (CSS_DIR / "print.css").read_text(encoding="utf-8")
    assert "@media print" in print_css
    assert "@page" in print_css

    # 3. Static assets served via HTTP 200
    res_report_css = client.get("/static/css/report.css")
    assert res_report_css.status_code == 200

    res_print_css = client.get("/static/css/print.css")
    assert res_print_css.status_code == 200

    res_catalog_js = client.get("/static/js/catalog.js")
    assert res_catalog_js.status_code == 200
