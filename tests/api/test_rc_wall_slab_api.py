"""Integration tests for RC Shear Wall and Slab/Punching API Endpoints (Phase 05-3)."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_rc_wall_check_api_endpoint():
    """Verify POST /api/rc/wall/check returns full engineering results & 2D geometry."""
    payload = {
        "name": "W-E1",
        "lw": 3500.0,
        "tw": 300.0,
        "hw": 3000.0,
        "cover": 40.0,
        "vert_bar_diam": 13.0,
        "vert_spacing": 200.0,
        "vert_layers": 2,
        "horiz_bar_diam": 13.0,
        "horiz_spacing": 200.0,
        "horiz_layers": 2,
        "left_boundary": {
            "length": 450.0,
            "width": 300.0,
            "bar_diam": 22.0,
            "total_bars": 8,
            "tie_diam": 10.0,
            "tie_spacing": 100.0,
            "tie_legs_x": 2,
            "tie_legs_y": 2
        },
        "fck": 27.0,
        "fy": 400.0,
        "fys": 400.0,
        "Pu": 1200.0,
        "Vu": 450.0,
        "Mu": 1600.0,
        "delta_u": 25.0
    }
    
    response = client.post("/api/rc/wall/check", json=payload)
    assert response.status_code == 200
    
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    
    # Assert shear results
    assert "shear" in data
    assert data["shear"]["phi_Vn"] > 0
    assert data["shear"]["dcr"] > 0
    
    # Assert rebar ratio results
    assert "rebar_ratio" in data
    assert data["rebar_ratio"]["is_double_curtain_provided"] is True
    assert data["rebar_ratio"]["is_spacing_ok"] is True
    
    # Assert boundary element results
    assert "boundary_element" in data
    assert "is_sbe_required" in data["boundary_element"]
    
    # Assert 2D geometry
    assert "geometry_2d" in data
    assert len(data["geometry_2d"]["polygon"]) == 4
    assert len(data["geometry_2d"]["rebars"]) > 0


def test_one_way_slab_check_api_endpoint():
    """Verify POST /api/rc/slab/one-way/check endpoint."""
    payload = {
        "name": "S101",
        "span_L": 4000.0,
        "thickness_h": 180.0,
        "cover": 25.0,
        "support_type": "both_ends_continuous",
        "main_bar_diam": 13.0,
        "main_spacing": 150.0,
        "temp_bar_diam": 10.0,
        "temp_spacing": 200.0,
        "fck": 24.0,
        "fy": 400.0,
        "Mu": 25.0,
        "Vu": 30.0
    }
    
    response = client.post("/api/rc/slab/one-way/check", json=payload)
    assert response.status_code == 200
    
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["is_thickness_ok"] is True
    assert data["is_flexure_ok"] is True
    assert data["phi_Mn"] > 25.0
    assert data["is_temp_ok"] is True


def test_two_way_slab_ddm_api_endpoint():
    """Verify POST /api/rc/slab/two-way/ddm endpoint."""
    payload = {
        "name": "S201",
        "l1": 6000.0,
        "l2": 6000.0,
        "c1": 500.0,
        "c2": 500.0,
        "thickness_h": 200.0,
        "qu": 12.0,
        "is_interior_span": True,
        "has_edge_beam": False,
        "fck": 27.0,
        "fy": 400.0
    }
    
    response = client.post("/api/rc/slab/two-way/ddm", json=payload)
    assert response.status_code == 200
    
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["M0"] > 0
    assert "longitudinal_moments" in data
    assert "column_strip" in data
    assert "middle_strip" in data


def test_punching_shear_check_api_endpoint():
    """Verify POST /api/rc/slab/punching endpoint."""
    payload = {
        "column_name": "C101",
        "location": "interior",
        "c1": 500.0,
        "c2": 500.0,
        "slab_h": 250.0,
        "eff_depth_d": 200.0,
        "Vu": 420.0,
        "Munb": 45.0,
        "fck": 27.0
    }
    
    response = client.post("/api/rc/slab/punching", json=payload)
    assert response.status_code == 200
    
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["b0"] == 2800.0
    assert data["capacity"]["phi_vc"] > 0
    assert data["stress"]["vu_total"] > 0
    assert data["dcr"] > 0
    assert len(data["perimeter_points"]) == 4
