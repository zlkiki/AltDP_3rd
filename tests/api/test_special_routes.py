"""Tests for Special Structures REST API Routes."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_cft_column_check_api():
    """Test CFT column check endpoint."""
    payload = {
        "cft_type": "RECTANGULAR",
        "B": 400.0,
        "H": 400.0,
        "t": 12.0,
        "fck": 30.0,
        "Fy": 355.0,
        "L": 4000.0,
        "K": 1.0,
        "Pu": 3000.0
    }
    response = client.post("/api/v1/special/cft-column/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_safe"] is True
    assert data["dcr_axial"] < 1.0
    assert data["phi_Pn"] > 3000.0


def test_src_column_check_api():
    """Test Encased SRC column check endpoint."""
    payload = {
        "B": 600.0,
        "H": 600.0,
        "cover": 50.0,
        "As": 11980.0,
        "Is_x": 204000000.0,
        "Is_y": 67500000.0,
        "Fy": 355.0,
        "num_rebars": 8,
        "rebar_dia": 22.0,
        "fck": 30.0,
        "L": 4000.0,
        "K": 1.0,
        "Pu": 4000.0
    }
    response = client.post("/api/v1/special/src-column/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_safe"] is True
    assert data["dcr_axial"] < 1.0
    assert data["phi_Pn"] > 4000.0


def test_composite_beam_check_api():
    """Test Composite Beam check endpoint."""
    payload = {
        "L": 8000.0,
        "beam_spacing": 3000.0,
        "d_s": 400.0,
        "b_f": 200.0,
        "t_f": 13.0,
        "t_w": 8.0,
        "Fy": 355.0,
        "h_f": 120.0,
        "fck": 27.0,
        "stud_dia": 19.0,
        "num_studs_half_span": 20,
        "Mu": 350.0,
        "Vu": 150.0
    }
    response = client.post("/api/v1/special/composite-beam/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_safe"] is True
    assert data["dcr_flexure"] < 1.0
    assert data["phi_Mn"] > 350.0


def test_aluminum_check_api():
    """Test Aluminium structural check endpoint."""
    payload = {
        "alloy": "6061-T6",
        "shape": "I_SHAPE",
        "Ag": 4500.0,
        "Aw": 1800.0,
        "Sx": 350000.0,
        "Sy": 120000.0,
        "Zx": 400000.0,
        "Zy": 160000.0,
        "rx": 88.0,
        "ry": 51.6,
        "Lx": 3000.0,
        "Ly": 3000.0,
        "Lb": 3000.0,
        "is_welded_in_haz": False,
        "Pu": 150.0,
        "Mux": 25.0,
        "Muy": 0.0,
        "Vu": 35.0
    }
    response = client.post("/api/v1/special/aluminum/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_safe"] is True
    assert data["max_dcr"] < 1.0


def test_retrofit_check_api():
    """Test Retrofit check endpoint."""
    payload = {
        "retrofit_type": "FLEXURE",
        "method": "CFRP_PLATE",
        "b": 300.0,
        "h": 600.0,
        "d": 540.0,
        "fck": 24.0,
        "As": 1520.0,
        "fy": 400.0,
        "Av": 142.6,
        "s": 200.0,
        "cfrp_tf": 1.2,
        "cfrp_bf": 200.0,
        "num_plies": 1,
        "Mu": 350.0,
        "Vu": 180.0
    }
    response = client.post("/api/v1/special/retrofit/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["flexure_gain_ratio"] > 1.0
