"""Tests for Web UI Templates and HTML Layout."""

import os
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_serving():
    """Test serving index.html dashboard and basic structural elements."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    
    # Platform branding & metadata
    assert "AltDP_3rd" in html
    assert "KDS 14 20" in html
    
    # Design tokens & stylesheets
    assert "/static/css/design_tokens.css" in html
    assert "/static/css/style.css" in html
    
    # Essential member tabs
    assert 'data-type="rc_beam"' in html
    assert 'data-type="rc_column"' in html
    assert 'data-type="rc_wall"' in html
    assert 'data-type="steel_beam"' in html
    assert 'data-type="cft_column"' in html
    assert 'data-type="retrofit"' in html
    assert 'data-type="section_db"' in html
    
    # Essential DOM containers
    assert 'id="sectionCanvas"' in html
    assert 'id="dcrCard"' in html
    assert 'id="dcrValue"' in html
    assert 'id="dcrBar"' in html
    assert 'id="resultTable"' in html
    assert 'id="pmChartCanvas"' in html
    assert 'id="btnThemeToggle"' in html


def test_static_css_serving():
    """Test static CSS file routing."""
    response_tokens = client.get("/static/css/design_tokens.css")
    assert response_tokens.status_code == 200
    assert "--bg-primary" in response_tokens.text
    assert "--status-safe" in response_tokens.text
    
    response_style = client.get("/static/css/style.css")
    assert response_style.status_code == 200
    assert ".canvas-panel" in response_style.text
