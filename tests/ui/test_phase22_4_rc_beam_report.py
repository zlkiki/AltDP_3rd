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
