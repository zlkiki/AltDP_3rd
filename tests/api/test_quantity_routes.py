"""API Integration tests for Quantity Takeoff and CAD Export Routes (Phase 17-2)."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_api_calculate_quantities():
    """Test quantity calculation endpoint."""
    payload = [
        {
            "member_id": 1,
            "story": "2F",
            "member_type": "BEAM",
            "b": 400.0,
            "h": 600.0,
            "length": 6000.0,
            "main_bar_size": "D22",
            "main_bar_count": 6,
            "sub_bar_size": "D10",
            "sub_bar_spacing": 200.0
        },
        {
            "member_id": 2,
            "story": "1F",
            "member_type": "COLUMN",
            "b": 500.0,
            "h": 500.0,
            "length": 3500.0,
            "main_bar_size": "D25",
            "main_bar_count": 8,
            "sub_bar_size": "D10",
            "sub_bar_spacing": 300.0
        }
    ]

    resp = client.post("/api/v1/project/quantity/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_concrete_vol_m3"] > 0
    assert data["total_formwork_area_m2"] > 0
    assert data["total_rebar_weight_ton"] > 0
    assert len(data["member_details"]) == 2
    assert "1F" in data["story_breakdowns"]
    assert "2F" in data["story_breakdowns"]


def test_api_export_quantity_excel():
    """Test downloading multi-sheet Excel file."""
    resp = client.get("/api/v1/project/quantity/export-excel")
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in resp.headers["content-type"]
    assert "filename=Project_Quantity_Summary.xlsx" in resp.headers["content-disposition"]
    # Verify non-empty binary content
    assert len(resp.content) > 1000


def test_api_export_cad_dxf():
    """Test downloading 2D CAD DXF detail."""
    resp = client.post("/api/v1/project/cad/export-dxf?member_type=BEAM&name=2G1&b=400&h=600")
    assert resp.status_code == 200
    assert "application/dxf" in resp.headers["content-type"]
    assert "filename=2G1_Rebar_Detail.dxf" in resp.headers["content-disposition"]
    assert len(resp.content) > 500
