"""API Integration Tests for Steel Member Design Routes (/api/steel/*)."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)


def test_api_steel_beam_design():
    """Test POST /api/steel/beam/design endpoint."""
    payload = {
        "name": "B1",
        "section_type": "H",
        "H": 400.0,
        "B": 200.0,
        "tw": 8.0,
        "tf": 13.0,
        "L": 6000.0,
        "Lb": 3000.0,
        "Cb": 1.0,
        "Mux": 180.0,
        "Muy": 0.0,
        "Vu": 120.0,
        "service_w": 15.0,
        "Fy": 355.0,
        "Fu": 490.0
    }
    response = client.post("/api/steel/beam/design", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "phi_Mn_x" in json_data["data"]
    assert "shear_dcr" in json_data["data"]
    assert "deflection_dcr" in json_data["data"]


def test_api_steel_column_design():
    """Test POST /api/steel/column/design endpoint."""
    payload = {
        "name": "C1",
        "section_type": "H",
        "H": 350.0,
        "B": 350.0,
        "tw": 12.0,
        "tf": 19.0,
        "Lx": 4000.0,
        "Ly": 4000.0,
        "Kx": 1.0,
        "Ky": 1.0,
        "Pu": 1500.0,
        "Mux": 120.0,
        "Muy": 40.0,
        "Fy": 355.0,
        "Fu": 490.0
    }
    response = client.post("/api/steel/column/design", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "pm_dcr" in json_data["data"]
    assert "axial_dcr" in json_data["data"]
    assert "phi_Pn" in json_data["data"]


def test_api_steel_brace_design():
    """Test POST /api/steel/brace/design endpoint."""
    payload = {
        "name": "BR1",
        "section_type": "ANGLE",
        "B": 100.0,
        "H": 100.0,
        "t": 10.0,
        "L": 3500.0,
        "K": 1.0,
        "connection_type": "BOLTED",
        "bolt_hole_diameter": 22.0,
        "num_bolt_holes": 2,
        "connection_length_L": 150.0,
        "eccentricity_x_bar": 28.2,
        "Tu": 200.0,
        "Pu": 100.0,
        "Fy": 355.0,
        "Fu": 490.0
    }
    response = client.post("/api/steel/brace/design", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "tension_dcr" in json_data["data"]
    assert "phi_Pn_yield" in json_data["data"]


def test_api_web_opening_check():
    """Test POST /api/steel/web-opening/check endpoint."""
    payload = {
        "name": "WO1",
        "shape": "RECTANGULAR",
        "H": 500.0,
        "B": 200.0,
        "tw": 9.0,
        "tf": 14.0,
        "ao": 300.0,
        "ho": 200.0,
        "e": 0.0,
        "has_reinforcement": True,
        "br": 80.0,
        "tr": 10.0,
        "Mu": 180.0,
        "Vu": 90.0,
        "Fy": 355.0,
        "Fu": 490.0
    }
    response = client.post("/api/steel/web-opening/check", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "vierendeel_dcr" in json_data["data"]
    assert "phi_Vn" in json_data["data"]
