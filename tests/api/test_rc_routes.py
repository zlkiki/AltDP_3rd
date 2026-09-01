"""API endpoint tests for RC design."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


@pytest.mark.api
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.api
def test_rc_beam_api_check():
    payload = {
        "name": "B1",
        "b": 400.0,
        "h": 600.0,
        "cover": 50.0,
        "As": 1935.0,
        "Av": 142.6,
        "s": 200.0,
        "Mu": 250.0,
        "Vu": 150.0,
        "fck": 24.0,
        "fy": 400.0
    }
    response = client.post("/api/rc/beam/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "phi_Mn" in data["data"]
    assert "flexure_dcr" in data["data"]


@pytest.mark.api
def test_rc_column_api_check():
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
        "fy": 500.0
    }
    response = client.post("/api/rc/column/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["pm_curve"]) > 0
