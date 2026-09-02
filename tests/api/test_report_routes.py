"""Tests for Structural Calculation Report API Endpoints (Phase 09-3)."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_api_report_sample():
    """Test sample calculation report GET endpoint."""
    resp = client.get("/api/v1/report/sample/rc_beam")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "SMPL-RC_BEAM-1" in resp.text
    assert "ALL SAFE" in resp.text


def test_api_report_html_post():
    """Test custom report generation POST endpoint."""
    payload = {
        "member_type": "rc_beam",
        "project_info": {"title": "API 테스트 프로젝트", "code": "KDS 14 20 00"},
        "member_info": {"id": "B-201", "type": "RC Beam"},
        "material_info": {"fck": 24.0, "fy": 400.0, "fys": 400.0},
        "section_info": {"b": 400.0, "h": 600.0, "d": 540.0},
        "loads_info": {"Mu": 200.0, "Vu": 120.0},
        "summary_dcr": 0.75,
        "is_safe": True,
    }
    resp = client.post("/api/v1/report/html", json=payload)
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "B-201" in resp.text
    assert "API 테스트 프로젝트" in resp.text


def test_api_report_excel_post():
    """Test Excel download POST endpoint."""
    payload = {
        "member_type": "rc_column",
        "project_info": {"title": "기둥 엑셀 계산서"},
        "member_info": {"id": "C-301"},
        "summary_dcr": 0.68,
        "is_safe": True,
    }
    resp = client.post("/api/v1/report/excel", json=payload)
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in resp.headers["content-type"]
    assert len(resp.content) > 1000


def test_api_report_pdf_post():
    """Test PDF / Print HTML download POST endpoint."""
    payload = {
        "member_type": "steel_member",
        "project_info": {"title": "철골보 PDF 계산서"},
        "member_info": {"id": "SB-401"},
        "summary_dcr": 0.82,
        "is_safe": True,
    }
    resp = client.post("/api/v1/report/pdf", json=payload)
    assert resp.status_code == 200
    assert len(resp.content) > 500
