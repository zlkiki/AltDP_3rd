"""Tests for Universal Dynamic Design Dispatcher API (/api/design/{cat}/{grp}/{mod})."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_dispatch_rc_beam_base():
    """Test dynamic calculation for RC Beam Base module."""
    payload = {
        "b": 400.0,
        "h": 600.0,
        "fck": 24.0,
        "rebar_grade": "SD400",
        "cover": 40.0,
        "Mu": 250.0,
        "Vu": 120.0,
        "top_dia": 22,
        "top_num": 4,
        "bot_dia": 22,
        "bot_num": 4,
        "stirrup_dia": 10,
        "stirrup_spacing": 200.0,
        "stirrup_legs": 2
    }
    resp = client.post("/api/design/rc/beam/base", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["key"] == "rc/beam/base"
    res = data["result"]
    assert "dcr" in res
    assert "verdict" in res
    assert res["verdict"] in ["OK", "NG"]
    assert "phiMn" in res or "flexure" in res or "summary" in res


def test_dispatch_rc_column_base():
    """Test dynamic calculation for RC Column Base module."""
    payload = {
        "b": 500.0,
        "h": 500.0,
        "fck": 27.0,
        "rebar_grade": "SD400",
        "cover": 40.0,
        "Pu": 1500.0,
        "Mux": 200.0,
        "Muy": 100.0,
        "main_bar_dia": 25,
        "nx": 4,
        "ny": 4,
        "tie_dia": 10,
        "tie_spacing": 300.0
    }
    resp = client.post("/api/design/rc/column/base", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["key"] == "rc/column/base"
    res = data["result"]
    assert "dcr" in res
    assert "verdict" in res


def test_dispatch_steel_member_beam():
    """Test dynamic calculation for Steel Member Beam module."""
    payload = {
        "section_name": "H-400x200x8x13",
        "steel_grade": "SM355",
        "Lb": 3000.0,
        "Mu": 180.0,
        "Vu": 90.0,
        "Cb": 1.0
    }
    resp = client.post("/api/design/steel/member/beam", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["key"] == "steel/member/beam"
    res = data["result"]
    assert "dcr" in res
    assert "verdict" in res


def test_dispatch_steel_connection_baseplate():
    """Test dynamic calculation for Steel Baseplate Connection module."""
    payload = {
        "section_name": "H-300x300x10x15",
        "Pu": 500.0,
        "Mu": 50.0,
        "Vu": 30.0,
        "plate_b": 500.0,
        "plate_h": 500.0,
        "plate_t": 30.0,
        "fck": 24.0,
        "anchor_dia": 24,
        "anchor_num": 4
    }
    resp = client.post("/api/design/steel/connection/baseplate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["key"] == "steel/connection/baseplate"
    res = data["result"]
    assert "dcr" in res


def test_dispatch_404_not_found():
    """Test 404 handling for invalid module route."""
    resp = client.post("/api/design/rc/invalid/nonexistent", json={})
    assert resp.status_code == 404
