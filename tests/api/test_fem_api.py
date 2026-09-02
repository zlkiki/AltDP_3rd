"""Tests for 2D FEM FastAPI REST API Endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_api_fem_foundation():
    """Test Foundation 2D FEM endpoint."""
    payload = {
        "length_x": 4.0,
        "length_y": 4.0,
        "thickness": 0.5,
        "fck": 24.0,
        "subgrade_modulus_ks": 20000.0,
        "nx": 6,
        "ny": 6,
        "column_loads": [
            {"x": 2.0, "y": 2.0, "P": 800.0, "Mx": 0.0, "My": 0.0}
        ]
    }
    response = client.post("/api/v1/fem/foundation/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["converged"] is True
    assert data["data"]["max_bearing_pressure_kpa"] > 0.0


def test_api_fem_wall_2way():
    """Test 2-Way Basement Wall FEM endpoint."""
    payload = {
        "length_b": 5.0,
        "height_h": 3.5,
        "thickness": 0.35,
        "fck": 24.0,
        "fy": 400.0,
        "soil_gamma": 18.0,
        "surcharge_q": 10.0,
        "boundary_bottom": "FIXED",
        "boundary_top": "PINNED"
    }
    response = client.post("/api/v1/fem/wall-2way/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["max_moment_my_knm_m"] > 0.0


def test_api_fem_baseplate():
    """Test Column Baseplate Contact FEM endpoint."""
    payload = {
        "plate_bx": 500.0,
        "plate_by": 500.0,
        "plate_thickness": 30.0,
        "steel_fy": 275.0,
        "concrete_fck": 24.0,
        "axial_p_kn": 500.0,
        "moment_mx_knm": 50.0,
        "moment_my_knm": 0.0
    }
    response = client.post("/api/v1/fem/baseplate/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["converged"] is True


def test_api_fem_endplate():
    """Test Moment Endplate FEM endpoint."""
    payload = {
        "plate_width_bp": 250.0,
        "plate_height_hp": 650.0,
        "plate_thickness_tp": 28.0,
        "beam_depth_d": 500.0,
        "flange_width_bf": 200.0,
        "flange_thickness_tf": 16.0,
        "web_thickness_tw": 10.0,
        "steel_fy": 355.0,
        "bolt_grade_fub": 1000.0,
        "bolt_dia_db": 24.0,
        "moment_mu_knm": 150.0,
        "axial_pu_kn": 0.0
    }
    response = client.post("/api/v1/fem/endplate/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["flange_tension_tf_kn"] > 0.0


def test_api_fem_slab():
    """Test Irregular Slab FEM endpoint."""
    payload = {
        "length_lx": 6.0,
        "length_ly": 6.0,
        "thickness": 0.20,
        "fck": 24.0,
        "fy": 400.0,
        "dead_load_kpa": 4.0,
        "live_load_kpa": 2.0,
        "openings": [
            {"x_min": 2.5, "x_max": 3.5, "y_min": 2.5, "y_max": 3.5}
        ]
    }
    response = client.post("/api/v1/fem/slab/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["max_wood_armer_mx_bot_knm_m"] > 0.0
