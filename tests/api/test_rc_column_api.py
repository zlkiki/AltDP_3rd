"""E2E Integration tests for RC Column FastAPI endpoints (Phase 04-3)."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)


def test_api_rc_column_design_endpoint():
    """Test POST /api/rc/column/design."""
    payload = {
        "name": "C101",
        "b": 600.0,
        "h": 600.0,
        "cover": 60.0,
        "bar_diam": 25.0,
        "total_bars": 12,
        "tie_diam": 10.0,
        "tie_spacing": 300.0,
        "tie_legs_x": 2,
        "tie_legs_y": 2,
        "is_spiral": False,
        "Lu": 3600.0,
        "k": 1.0,
        "is_braced": True,
        "M1x": 0.0,
        "M2x": 350.0,
        "M1y": 0.0,
        "M2y": 0.0,
        "Pu": 2500.0,
        "Mux": 350.0,
        "Muy": 0.0,
        "Vux": 0.0,
        "Vuy": 120.0,
        "fck": 30.0,
        "fy": 400.0
    }
    
    response = client.post("/api/rc/column/design", json=payload)
    assert response.status_code == 200
    
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "Ag" in data
    assert "Ast" in data
    assert "slenderness" in data
    assert "design_forces" in data
    assert "shear" in data
    assert "pm_curve_x" in data
    assert len(data["pm_curve_x"]) > 0


def test_api_rc_column_pm_curve_endpoint():
    """Test POST /api/rc/column/pm-curve."""
    payload = {
        "b": 500.0,
        "h": 500.0,
        "cover": 50.0,
        "bar_diam": 22.0,
        "total_bars": 8,
        "is_spiral": False,
        "fck": 24.0,
        "fy": 400.0,
        "theta_deg": 45.0,
        "num_points": 30
    }
    
    response = client.post("/api/rc/column/pm-curve", json=payload)
    assert response.status_code == 200
    
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["theta_deg"] == 45.0
    assert "points" in data
    assert len(data["points"]) >= 30


def test_api_rc_column_legacy_check_endpoint():
    """Test backward compatibility of POST /api/rc/column/check."""
    payload = {
        "name": "C1",
        "b": 600.0,
        "h": 600.0,
        "cover": 60.0,
        "bar_diam": 25.0,
        "total_bars": 12,
        "Pu": 2500.0,
        "Mu": 350.0,
        "Vu": 120.0,
        "fck": 30.0,
        "fy": 400.0
    }
    
    response = client.post("/api/rc/column/check", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "dcr" in body["data"]
    assert "pm_curve" in body["data"]
