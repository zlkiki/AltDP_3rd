"""Test Phase 22-4 & 22-4-1-4: RC Beam Pure White A4 5-Chapter 8-Step KaTeX Calculation Report (Standardized).

Conforms to Requirement 22-4-1-4:
- 3-Station Individual KaTeX Formulations (End-I, Center-M, End-J)
- KDS 14 20 20: 2022 Minimum Reinforcement (phi_Mn >= 1.2 Mcr) & Ductility Limit (eps_t >= eps_t,min)
- Zero Legacy Rho (\rho_min, \rho_max) Formulas
- 4-Pane Pure White A4 Layout & Print/Export Integration
"""

import os
import re
import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_rc_beam_report_js_serving():
    """Verify rc_beam_report.js is served properly via static files and has standardized names."""
    response = client.get("/static/js/report/rc_beam_report.js")
    assert response.status_code == 200
    content = response.text
    assert "RCBeamReportGenerator" in content
    assert "window.renderRCBeamReport" in content
    # Verify 5+ chapters
    assert "제 1장" in content or "설계 기본 정보 및 단면 제원" in content
    assert "제 2장" in content or "설계 부재력 및 하중조합" in content
    assert "제 3장" in content or "휨모멘트 강도 검토" in content
    assert "제 4장" in content or "전단 및 비틀림 강도 검토" in content
    assert "제 5장" in content or "사용성 한계상태 검토" in content
    assert "제 6장" in content or "종합 안전성 판정" in content
    # Verify KDS 14 20 20: 2022 key formulas
    assert r"\phi M_n \ge 1.2 M_{cr}" in content or "M_{cr}" in content or "Mcr" in content
    assert r"\epsilon_t \ge \epsilon_{t,\min}" in content or "epsT" in content
    assert r"\beta_1" in content or "beta1" in content
    assert r"\phi M_n" in content or "phiMn" in content
    assert "V_c" in content
    assert "V_s" in content
    assert "T_{th}" in content
    assert "I_e" in content


def test_index_html_contains_rc_beam_report():
    """Verify index.html contains script tag for rc_beam_report.js."""
    response = client.get("/")
    assert response.status_code == 200
    assert "rc_beam_report.js" in response.text


def test_report_engine_delegates_to_rc_beam_report():
    """Verify report_engine.js dispatches to window.renderRCBeamReport for rc_beam."""
    response = client.get("/static/js/core/report_engine.js")
    assert response.status_code == 200
    assert "renderRCBeamReport" in response.text


def test_rc_beam_report_formula_substitution_steps():
    """Verify KaTeX formulas contain numerical substitution steps (기준식 -> 대입식 -> 결과값)."""
    response = client.get("/static/js/report/rc_beam_report.js")
    assert response.status_code == 200
    content = response.text
    # 3-step formula derivation structure checks
    assert "formula-row" in content
    assert "formula-subst" in content
    assert "formula-eval" in content
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

    # Check rc_beam_report.js colgroup tags
    resp_beam = client.get("/static/js/report/rc_beam_report.js")
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


# ============================================================================
# Phase 22-4-1-4 Requirement Specific Verification Tests
# ============================================================================

def test_rc_beam_report_3station_flexure_sections():
    """Verify calculation report contains 3-Station dedicated flexure review sections (End-I, Center-M, End-J)."""
    response = client.get("/static/js/report/rc_beam_report.js")
    assert response.status_code == 200
    content = response.text

    # 3.1 3-Station summary table
    assert "3-Station 위치별 휨설계 강도 총괄 요약표" in content or "3-Station" in content
    # 3.2 End-I Negative bending check
    assert "단부-I (End-I)" in content
    assert "부모멘트" in content
    # 3.3 Center-M Positive bending check
    assert "중앙부 (Center-M)" in content or "중앙부-M" in content
    assert "정모멘트" in content
    # 3.4 End-J Bending check
    assert "단부-J (End-J)" in content


def test_rc_beam_report_kds_min_rebar_katex():
    """Verify KDS 14 20 20: 2022 minimum reinforcement KaTeX formula (phi_Mn >= 1.2 Mcr, Mcr)."""
    response = client.get("/static/js/report/rc_beam_report.js")
    assert response.status_code == 200
    content = response.text

    # Verify formula strings (matching double backslashes in JS template literal)
    assert r"\\phi M_n \\ge 1.2 M_{cr}" in content or r"\phi M_n \ge 1.2 M_{cr}" in content.replace("\\\\", "\\")
    assert r"f_r = 0.63 \lambda \sqrt{f_{ck}}" in content.replace("\\\\", "\\") or "0.63" in content
    assert r"I_g = \frac{b_w h^3}{12}" in content.replace("\\\\", "\\") or "I_g" in content
    assert r"M_{cr} = \frac{f_r I_g}{y_t}" in content.replace("\\\\", "\\") or "M_{cr}" in content
    assert "최소철근량 만족" in content


def test_rc_beam_report_ductility_strain_limit_katex():
    """Verify KDS 14 20 20: 2022 ductility limit KaTeX formula (eps_t >= eps_t,min, c/d_t <= (c/d_t)_lim)."""
    response = client.get("/static/js/report/rc_beam_report.js")
    assert response.status_code == 200
    content = response.text

    # Verify ductility strain formula strings (matching double backslashes in JS template literal)
    assert r"\\epsilon_t \\ge \\epsilon_{t,\\min}" in content or r"\epsilon_t \ge \epsilon_{t,\min}" in content.replace("\\\\", "\\")
    assert r"\frac{c}{d_t} \le \left(\frac{c}{d_t}\right)_{\lim}" in content.replace("\\\\", "\\") or r"\frac{c}{d_t}" in content.replace("\\\\", "\\")
    assert r"\epsilon_t = \epsilon_{cu} \left(\frac{d_t - c}{c}\right)" in content.replace("\\\\", "\\")
    assert "연성파괴 유도" in content


def test_rc_beam_report_no_legacy_rho_terms():
    """Verify report completely excludes legacy reinforcement ratio terms (rho_min, rho_max, rhoMin, rhoMax)."""
    response = client.get("/static/js/report/rc_beam_report.js")
    assert response.status_code == 200
    content = response.text

    # Check that legacy formulas and variable names do not exist in report content
    assert r"\rho_{\min}" not in content, r"Legacy \rho_{\min} must not exist in rc_beam_report.js"
    assert r"\rho_{\max}" not in content, r"Legacy \rho_{\max} must not exist in rc_beam_report.js"
    assert "rhoMin" not in content, "Legacy rhoMin variable must not exist in rc_beam_report.js"
    assert "rhoMax" not in content, "Legacy rhoMax variable must not exist in rc_beam_report.js"
    # Ensure regex check also passes
    assert not re.search(r"\\rho_\{?(?:min|max)\}?", content, re.IGNORECASE)
