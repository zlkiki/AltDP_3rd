"""Tests for Phase 20-4: 2D VDraw Canvas WIP and Pure White A4 Report Hardcoding Cleanup."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_renderer2d_render_wip_canvas():
    """Verify Renderer2D.renderWIPCanvas is implemented with dark grid & geometry symbol."""
    res = client.get("/static/js/renderer2d.js")
    assert res.status_code == 200
    text = res.text

    assert "renderWIPCanvas" in text
    assert "2D VDraw 단면 및 배근도 그래픽 준비 중 (WIP)" in text
    assert "setupDPI" in text
    assert "rgba(148, 163, 184" in text  # Grid lines
    assert "roundRect" in text or "rect" in text


def test_result_renderer_a4_wip_sheet():
    """Verify ResultRenderer has renderA4WIPSheet conforming to docs/14 5-chapter standard."""
    res = client.get("/static/js/report/result_renderer.js")
    assert res.status_code == 200
    text = res.text

    assert "renderA4WIPSheet" in text
    assert "pure-white-sheet" in text
    assert "제 1장. 일반 설계 조건" in text
    assert "제 2장. 재질 및 단면 제원" in text
    assert "제 3장. 소요 설계 하중" in text
    assert "제 4장. 단면 안전성 정밀 검토" in text
    assert "제 5장. 종합 안전성 판정" in text
    assert "KDS 공식 수식 전개식 작성 예정 (WIP)" in text
    assert "[미구현 (WIP)]" in text


def test_redcr_common_renderer_legacy_cleanup():
    """Verify legacy 4-pillar cards are eliminated and pure white A4 is guaranteed."""
    res = client.get("/static/js/report/redcr_common_renderer.js")
    assert res.status_code == 200
    text = res.text

    # Legacy 4-pillar cards eliminated
    assert "four-pillar-container" not in text
    assert "pillar-card" not in text
    assert "pillar-section-canvas" not in text

    # Standard A4 sheet guaranteed
    assert "pure-white-sheet" in text
    assert "renderA4Sheet" in text
    assert "KDS STRUCTURAL CALCULATION REPORT" in text
    assert "제 1장. 일반 설계 조건" in text
    assert "제 5장. 종합 안전성 판정" in text


def test_core_report_renderer_no_hardcoded_values():
    """Verify core/report_renderer.js has no fake hardcoded numbers like 8.4mm or 335.2kNm."""
    res = client.get("/static/js/core/report_renderer.js")
    assert res.status_code == 200
    text = res.text

    assert "8.4 mm" not in text
    assert "335.2 kN" not in text
    assert "232.8 kN" not in text
    assert "0.18 mm" not in text
    assert "pure-white-sheet" in text


def test_app_js_wip_canvas_and_pm_guard():
    """Verify app.js wires renderWIPCanvas and guards 3D P-M toggle on WIP modules."""
    res = client.get("/static/js/app.js")
    assert res.status_code == 200
    text = res.text

    assert "renderWIPCanvas" in text
    assert "3D P-M 상관곡선 그래픽 준비 중 (WIP)" in text
    assert "pmChartCanvas" in text
