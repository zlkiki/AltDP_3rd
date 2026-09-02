"""Integration Tests for Foundation and Retaining Wall FastAPI Endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_spread_footing_design_endpoint():
    payload = {
        "name": "F1_API",
        "Bx": 2400.0,
        "Ly": 2400.0,
        "thickness_H": 600.0,
        "depth_Df": 1500.0,
        "col_cx": 500.0,
        "col_cy": 500.0,
        "col_type": "interior",
        "fck": 24.0,
        "fy": 400.0,
        "qa_allowable": 250.0,
        "P_serv": 1000.0,
        "Mx_serv": 50.0,
        "My_serv": 40.0,
        "Pu": 1400.0,
        "Mux": 70.0,
        "Muy": 55.0
    }
    response = client.post("/api/rc/foundation/spread-footing/design", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["name"] == "F1_API"
    assert "bearing" in data
    assert "shear" in data
    assert "flexure" in data
    assert "visualization" in data
    assert data["bearing"]["is_ok"] is True


def test_combined_footing_design_endpoint():
    payload = {
        "name": "CF1_API",
        "Bx": 2000.0,
        "Ly": 6500.0,
        "thickness_H": 800.0,
        "col1_P_serv": 800.0,
        "col1_Pu": 1100.0,
        "col2_P_serv": 1400.0,
        "col2_Pu": 1900.0,
        "qa_allowable": 300.0
    }
    response = client.post("/api/rc/foundation/combined-footing/design", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "bearing" in data
    assert "longitudinal_flexure" in data


def test_tie_beam_design_endpoint():
    payload = {
        "name": "TB1_API",
        "b": 400.0,
        "h": 600.0,
        "connected_col_Pu": 2000.0,
        "Pu_tension": 200.0,
        "Mu": 80.0,
        "Vu": 60.0
    }
    response = client.post("/api/rc/foundation/tie-beam/design", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["axial_tension"]["is_ok"] is True


def test_retaining_wall_design_endpoint():
    payload = {
        "name": "RW1_API",
        "wall_type": "cantilever_t",
        "H_total": 4500.0,
        "stem_t_top": 300.0,
        "stem_t_bot": 450.0,
        "base_width_B": 3200.0,
        "base_t": 500.0,
        "toe_length": 1000.0,
        "heel_length": 1750.0,
        "front_embedment_Df": 800.0,
        "soil_unit_weight": 19.0,
        "phi_deg": 30.0,
        "surcharge_q": 10.0,
        "qa_allowable": 300.0
    }
    response = client.post("/api/rc/foundation/retaining-wall/design", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "earth_pressure" in data
    assert "stability" in data
    assert "stem" in data
    assert "visualization" in data
    assert data["stability"]["is_overturning_ok"] is True
    assert data["stability"]["is_sliding_ok"] is True
