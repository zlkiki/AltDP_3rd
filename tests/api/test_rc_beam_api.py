"""Unit and integration tests for RC Beam API Endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


@pytest.mark.api
def test_rc_beam_api_check_endpoint():
    """Verify POST /api/rc/beam/check returns complete KDS results."""
    payload = {
        "name": "B101",
        "b": 400.0,
        "h": 600.0,
        "cover": 50.0,
        "cover_prime": 50.0,
        "side_cover": 40.0,
        "As": 1935.0,
        "As_prime": 0.0,
        "Av": 142.6,
        "s": 200.0,
        "Mu": 250.0,
        "Vu": 150.0,
        "Tu": 15.0,
        "Ma": 160.0,
        "span_length": 6000.0,
        "fck": 24.0,
        "fy": 400.0,
        "num_tension_bars": 5
    }
    
    response = client.post("/api/rc/beam/check", json=payload)
    assert response.status_code == 200
    
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    
    # Check key engineering outputs
    assert "phi_Mn" in data
    assert data["phi_Mn"] > 250.0
    assert "flexure_dcr" in data
    assert "phi_Vn" in data
    assert "shear_dcr" in data
    assert "Tcr" in data
    assert "is_torsion_ignored" in data
    assert "delta_total" in data
    assert "deflection_dcr" in data
    assert "crack_width" in data
    assert "is_safe" in data


@pytest.mark.api
def test_rc_beam_api_auto_design_endpoint():
    """Verify POST /api/rc/beam/auto-design returns optimal arrangement."""
    payload = {
        "b": 400.0,
        "h": 600.0,
        "As_req": 1850.0,
        "cover": 40.0,
        "stirrup_size": "D10",
        "max_aggregate": 25.0
    }
    
    response = client.post("/api/rc/beam/auto-design", json=payload)
    assert response.status_code == 200
    
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    
    assert "selected" in data
    assert data["selected"] is not None
    assert data["selected"]["total_area"] >= 1850.0
    assert len(data["selected"]["layers"]) >= 1
    assert "candidates" in data
    assert len(data["candidates"]) > 0


@pytest.mark.api
def test_rc_beam_api_validation_error():
    """Verify API handles invalid dimensions gracefully with 422."""
    payload = {
        "b": 10.0,  # Invalid: below minimum ge=50.0
        "h": 600.0,
        "As": 1935.0
    }
    response = client.post("/api/rc/beam/check", json=payload)
    assert response.status_code == 422
