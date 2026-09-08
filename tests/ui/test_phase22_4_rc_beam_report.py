"""Test Phase 22-4: RC Beam Pure White A4 5-Chapter 8-Step KaTeX Calculation Report."""

import os
import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_redcr_rc_beam_js_serving():
    """Verify redcr_rc_beam.js is served properly via static files."""
    response = client.get("/static/js/report/redcr_rc_beam.js")
    assert response.status_code == 200
    content = response.text
    assert "RedcrRcBeamReport" in content
    assert "window.RedcrRcBeamReport" in content
    # Verify 5 chapters
    assert "제 1장" in content or "설계 기본 정보 및 단면 제원" in content
    assert "제 2장" in content or "설계 부재력 및 하중조합" in content
    assert "제 3장" in content or "휨모멘트 강도 검토" in content
    assert "제 4장" in content or "전단 및 비틀림 강도 검토" in content
    assert "제 5장" in content or "사용성 한계상태 검토" in content
    assert "제 6장" in content or "종합 안전성 판정" in content
    # Verify 8-step KaTeX key formulas
    assert r"\rho_{\min}" in content or "rhoMin" in content
    assert r"\beta_1" in content or "beta1" in content
    assert r"\epsilon_t" in content or "epsT" in content
    assert r"\phi M_n" in content or "phiMn" in content
    assert "V_c" in content
    assert "V_s" in content
    assert "T_{th}" in content
    assert "I_e" in content


def test_index_html_contains_redcr_rc_beam():
    """Verify index.html contains script tag for redcr_rc_beam.js."""
    response = client.get("/")
    assert response.status_code == 200
    assert "redcr_rc_beam.js" in response.text


def test_report_engine_delegates_to_redcr_rc_beam():
    """Verify report_engine.js dispatches to RedcrRcBeamReport for rc_beam."""
    response = client.get("/static/js/core/report_engine.js")
    assert response.status_code == 200
    assert "RedcrRcBeamReport" in response.text


def test_redcr_rc_beam_formula_substitution_steps():
    """Verify KaTeX formulas contain numerical substitution steps (기준식 -> 대입식 -> 결과값)."""
    response = client.get("/static/js/report/redcr_rc_beam.js")
    assert response.status_code == 200
    content = response.text
    # 3-step formula derivation structure checks
    assert "formula-row" in content
    assert "formula-subst" in content
    assert "formula-eval" in content
    assert "rhoMax" in content or "rho" in content
    assert "V_{s," in content or "VsMax" in content or "V_{s" in content
    assert "Vc" in content or "V_c" in content
    assert "Tth" in content or "T_{th}" in content
    assert "phi" in content
    assert "lambdaDelta" in content or "rhoPrime" in content
    assert "deltaTotal" in content or "Delta" in content
    assert "crackWidth" in content or "w =" in content


def test_report_excel_button_disabled():
    """Verify Excel export button is disabled with guidance tooltip."""
    # Check index.html
    resp_index = client.get("/")
    assert resp_index.status_code == 200
    assert 'id="btn-report-excel"' in resp_index.text
    assert "disabled" in resp_index.text

    # Check report_engine.js toolbar template
    resp_engine = client.get("/static/js/core/report_engine.js")
    assert resp_engine.status_code == 200
    assert 'id="btn-report-excel" class="btn-tool" disabled' in resp_engine.text


def test_report_table_layout_and_column_widths():
    """Verify report.css removes .inp-label 60% rule and enforces fixed layout with colgroup."""
    # Check report.css
    resp_css = client.get("/static/css/report.css")
    assert resp_css.status_code == 200
    css = resp_css.text
    assert "width: 60% !important;" not in css
    assert "table-layout: fixed !important;" in css

    # Check redcr_rc_beam.js colgroup tags
    resp_beam = client.get("/static/js/report/redcr_rc_beam.js")
    assert resp_beam.status_code == 200
    assert "<colgroup>" in resp_beam.text
    assert "table-layout:fixed" in resp_beam.text


def test_report_zoom_fit_width_on_init():
    """Verify zoom controller implements fitToWidth on initialization."""
    resp_zoom = client.get("/static/js/components/zoom_controller.js")
    assert resp_zoom.status_code == 200
    assert "fitToWidth()" in resp_zoom.text
    assert "isFitMode" in resp_zoom.text

    resp_engine = client.get("/static/js/core/report_engine.js")
    assert resp_engine.status_code == 200
    assert "hasInitialFitted" in resp_engine.text
    assert "window.ZoomController.fitToWidth()" in resp_engine.text

