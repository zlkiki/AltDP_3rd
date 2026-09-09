"""Tests for Phase 20-5: 4-Pane Integrated E2E Verification and Zero Console Errors Baseline.

Validates:
1. Zero 404s on all static assets (CSS, JS) referenced in index.html.
2. Complete 61-module catalog integrity via /api/modules.
3. Resilience of schema endpoint across all 61 modules without 500 errors.
4. Safeguards and error-handling in dispatcher.js and app.js.
5. Verified vs WIP distinction and pure white A4 WIP sheet single-source guarantee.
"""

import re
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_assets_all_200_ok():
    """Verify all CSS and JS assets referenced in index.html return HTTP 200 OK (0 404 errors)."""
    res = client.get("/")
    assert res.status_code == 200
    html_content = res.text

    # Extract all local CSS links
    css_links = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html_content)
    local_css = [c.split("?")[0] for c in css_links if not c.startswith("http")]

    # Extract all local JS scripts
    js_scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html_content)
    local_js = [j.split("?")[0] for j in js_scripts if not j.startswith("http")]

    assert len(local_css) >= 10, f"Expected at least 10 CSS files, found {len(local_css)}"
    assert len(local_js) >= 50, f"Expected at least 50 JS files, found {len(local_js)}"

    for css in local_css:
        css_res = client.get(css)
        assert css_res.status_code == 200, f"CSS 404 error: {css}"
        assert len(css_res.text) > 0, f"Empty CSS: {css}"

    for js in local_js:
        js_res = client.get(js)
        assert js_res.status_code == 200, f"JS 404 error: {js}"
        assert len(js_res.text) > 0, f"Empty JS: {js}"


def test_all_61_modules_catalog_integrity():
    """Verify that /api/modules returns the full 61-module catalog with valid 3-tier metadata."""
    res = client.get("/api/modules")
    assert res.status_code == 200
    data = res.json()
    modules = data.get("modules", [])

    assert len(modules) >= 61, f"Expected at least 61 modules, got {len(modules)}"

    for mod in modules:
        assert "key" in mod, f"Module missing key: {mod}"
        assert "name" in mod, f"Module missing name: {mod}"
        assert "category" in mod, f"Module missing category: {mod}"
        assert "group" in mod, f"Module missing group: {mod}"
        assert "tier" in mod, f"Module missing tier: {mod}"
        assert "engine_status" in mod, f"Module missing engine_status: {mod}"
        assert mod["tier"] in ["Tier 1", "Tier 2", "Tier 3"], f"Invalid tier for {mod['key']}: {mod['tier']}"
        assert mod["engine_status"] in ["VERIFIED", "WIP"], f"Invalid engine_status for {mod['key']}: {mod['engine_status']}"


def test_all_61_modules_schema_endpoint_resilience():
    """Verify that iterating through all 61 modules' schema endpoints never triggers a 500 Server Error."""
    res = client.get("/api/modules")
    assert res.status_code == 200
    modules = res.json().get("modules", [])

    for mod in modules:
        key = mod["key"]
        parts = key.split("/")
        cat = parts[0]
        grp = parts[1] if len(parts) > 1 else "base"
        mod_id = parts[2] if len(parts) > 2 else "base"

        schema_res = client.get(f"/api/schema/{cat}/{grp}/{mod_id}")
        # Must be either 200 (schema found) or 404 (not implemented yet), never 500
        assert schema_res.status_code in [200, 404], (
            f"Schema endpoint crashed with {schema_res.status_code} for module {key}"
        )
        if schema_res.status_code == 200:
            data = schema_res.json()
            assert "schema" in data or "info" in data


def test_dispatcher_and_app_js_error_free_guards():
    """Verify that dispatcher.js and app.js have robust guards against runtime exceptions."""
    # 1. Dispatcher syntax & structure
    disp_res = client.get("/static/js/core/dispatcher.js")
    assert disp_res.status_code == 200
    disp_text = disp_res.text
    assert "class ModuleDispatcher" in disp_text
    assert "cleanupForm" in disp_text
    assert "isWIP" in disp_text
    assert "switchModule" in disp_text
    # Ensure no illegal commas after class methods
    assert "isWIP(moduleKey) {" in disp_text
    assert "cleanupForm(container = null) {" in disp_text

    # 2. App.js safeguards
    app_res = client.get("/static/js/app.js")
    assert app_res.status_code == 200
    app_text = app_res.text
    assert "selectModule" in app_text
    assert "isModuleWIP" in app_text
    assert "WIPCardRenderer.render" in app_text
    assert "Renderer2D.renderWIPCanvas" in app_text
    assert "ResultRenderer.render" in app_text
    assert "catch (fetchErr)" in app_text or "catch (err)" in app_text


def test_flagship_vs_wip_handling():
    """Verify flagship members (Tier 1 VERIFIED) vs WIP members (Tier 2/3) distinction."""
    res = client.get("/api/modules")
    assert res.status_code == 200
    modules = res.json().get("modules", [])

    flagship_keys = ["rc/beam/base", "rc/column/base", "rc/slab/base", "steel/member/beam", "steel/connection/baseplate"]
    wip_keys = ["rc/wall/basement", "rc/wall/retaining", "steel/brace/base"]

    for mod in modules:
        if mod["key"] in flagship_keys:
            assert mod["tier"] == "Tier 1", f"Flagship {mod['key']} should be Tier 1"
        if mod["key"] in wip_keys:
            assert mod["engine_status"] == "WIP", f"WIP module {mod['key']} should be engine_status WIP"


def test_wip_a4_report_no_legacy_card():
    """Verify legacy 4-pillar card renderer is decommissioned and A4 sheet standard is enforced."""
    rep_res = client.get("/static/js/report/report_common_renderer.js")
    assert rep_res.status_code == 200
    assert "four-pillar-container" not in rep_res.text

    result_res = client.get("/static/js/report/result_renderer.js")
    assert result_res.status_code == 200
    assert "renderA4WIPSheet" in result_res.text
    assert "pure-white-sheet" in result_res.text
