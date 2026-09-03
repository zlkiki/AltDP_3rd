"""Tests for Web UI/UX routes and template serving.

Validates the 4-Main Form Views (MembView, ListView, DrawView, QnttView),
Ribbon navigation, and static assets loading conforming to Requirement 14.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_main_index_page():
    """Verify that the main engineering dashboard serves properly with 4-Main Form Views."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Verify Brand & Codes
    assert "AltDP_3rd" in html
    assert "KDS 14 20 00" in html

    # Verify 4-Main Form Views Containers
    assert 'id="view-memb"' in html
    assert 'id="view-list"' in html
    assert 'id="view-draw"' in html
    assert 'id="view-qntt"' in html

    # Verify Ribbon Tabs
    assert 'data-tab="tab-home"' in html
    assert 'data-tab="tab-rc"' in html
    assert 'data-tab="tab-steel"' in html

    # Verify P/S/M Mode Switcher
    assert 'data-mode="P"' in html
    assert 'data-mode="S"' in html
    assert 'data-mode="M"' in html


def test_static_css_assets():
    """Verify that all CSS stylesheets are properly mounted and served."""
    css_files = [
        "/static/css/design_tokens.css",
        "/static/css/ribbon.css",
        "/static/css/views.css",
        "/static/css/style.css"
    ]
    for path in css_files:
        resp = client.get(path)
        assert resp.status_code == 200, f"Failed to serve {path}"
        assert len(resp.text) > 50


def test_static_js_assets():
    """Verify that all JavaScript controllers are properly mounted and served."""
    js_files = [
        "/static/js/renderer2d.js",
        "/static/js/pm_chart.js",
        "/static/js/member_forms.js",
        "/static/js/batch_grid.js",
        "/static/js/draw_cad.js",
        "/static/js/qntt_summary.js",
        "/static/js/app.js"
    ]
    for path in js_files:
        resp = client.get(path)
        assert resp.status_code == 200, f"Failed to serve {path}"
        assert len(resp.text) > 50


def test_health_check():
    """Verify health endpoint."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["platform"] == "AltDP_3rd"
