"""Unit and Integration Tests for WIP Dispatcher (Phase 20-1).

Verifies standard WIPResponse (NOT_YET_IMPLEMENTED) handling for unintegrated modules,
protection of verified KDS engines, and prevention of fake mock values.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from src.api.models.wip import WIPModuleDetail, WIPResponse, get_wip_module_detail, MODULE_CATALOG_61

client = TestClient(app)


def test_wip_pydantic_schema_serialization():
    """Test WIPModuleDetail and WIPResponse Pydantic serialization."""
    detail = WIPModuleDetail(
        key="rc/wall/rc_basement_wall",
        name="RC 지하외벽 (Basement Wall)",
        midas_dlg="IDD_RCS_BASEWALL_INPUT_DLG",
        category="rc",
        group="wall",
        domain="RC",
        tier="Tier 2",
        standard="KDS 14 20 40 : 2022",
        engine_status="WIP"
    )
    resp = WIPResponse(
        success=False,
        status="NOT_YET_IMPLEMENTED",
        code="WIP_MODULE",
        message="Test WIP message",
        module=detail
    )
    dumped = resp.model_dump()
    assert dumped["success"] is False
    assert dumped["status"] == "NOT_YET_IMPLEMENTED"
    assert dumped["code"] == "WIP_MODULE"
    assert dumped["module"]["key"] == "rc/wall/rc_basement_wall"
    assert dumped["module"]["tier"] == "Tier 2"
    assert dumped["module"]["engine_status"] == "WIP"


def test_wip_dispatch_unintegrated_modules():
    """Test calling unintegrated catalog modules returns HTTP 200 with WIPResponse."""
    wip_targets = [
        ("rc", "special", "rc_stair"),
        ("steel", "special", "steel_stair"),
        ("rc", "special", "rc_buttress"),
        ("rfm", "beam", "rfm_beam"),
        ("pbd", "rc", "pbd_rc_beam")
    ]
    
    for cat, grp, mod in wip_targets:
        res = client.post(f"/api/design/{cat}/{grp}/{mod}", json={})
        assert res.status_code == 200, f"Expected 200 for WIP module {cat}/{grp}/{mod}, got {res.status_code}"
        data = res.json()
        assert data["success"] is False
        assert data["status"] == "NOT_YET_IMPLEMENTED"
        assert data["code"] == "WIP_MODULE"
        assert "module" in data
        assert data["module"]["engine_status"] == "WIP"
        assert len(data["message"]) > 0


def test_wip_dispatch_verified_engine_protection():
    """Verify that verified KDS engines (docs/12) continue calculating with full fidelity."""
    # 1. RC Beam
    payload_beam = {
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
    resp_beam = client.post("/api/design/rc/beam/base", json=payload_beam)
    assert resp_beam.status_code == 200
    data_beam = resp_beam.json()
    assert data_beam["success"] is True
    assert "result" in data_beam
    res = data_beam["result"]
    assert "dcr" in res
    assert "verdict" in res
    assert res["verdict"] in ["OK", "NG"]

    # 2. RC Column
    payload_col = {
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
    resp_col = client.post("/api/design/rc/column/base", json=payload_col)
    assert resp_col.status_code == 200
    data_col = resp_col.json()
    assert data_col["success"] is True
    assert data_col["result"]["verdict"] in ["OK", "NG"]


def test_wip_dispatch_invalid_route_404():
    """Test that completely invalid/unknown routes continue to return 404."""
    resp = client.post("/api/design/rc/invalid/nonexistent", json={})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_get_design_status_endpoint():
    """Test GET status inspection endpoint for verified vs WIP modules."""
    # Verified module
    resp_verified = client.get("/api/design/rc/beam/base/status")
    assert resp_verified.status_code == 200
    data_v = resp_verified.json()
    assert data_v["engine_status"] == "VERIFIED"
    assert data_v["is_wip"] is False

    # WIP module
    resp_wip = client.get("/api/design/rc/special/rc_stair/status")
    assert resp_wip.status_code == 200
    data_w = resp_wip.json()
    assert data_w["engine_status"] == "WIP"
    assert data_w["is_wip"] is True

    # 404 for unknown
    resp_unknown = client.get("/api/design/rc/nonexistent/xyz/status")
    assert resp_unknown.status_code == 404


def test_catalog_integrity_61_modules():
    """Test that the catalog contains 61 unique module specifications."""
    assert len(MODULE_CATALOG_61) == 61
    tiers = {m["tier"] for m in MODULE_CATALOG_61.values()}
    assert tiers == {"Tier 1", "Tier 2", "Tier 3"}
    tier1_count = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 1")
    tier2_count = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 2")
    tier3_count = sum(1 for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 3")
    assert tier1_count == 9
    assert tier2_count == 26
    assert tier3_count == 26
