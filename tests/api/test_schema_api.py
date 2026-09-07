"""Tests for Schema API Endpoints (/api/modules and /api/schema)."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_get_all_modules():
    """Verify listing all 61 member design modules."""
    response = client.get("/api/modules")
    assert response.status_code == 200
    data = response.json()
    
    assert "modules" in data
    assert "total_count" in data
    assert "summary" in data
    assert data["total_count"] == 61
    assert len(data["modules"]) == 61
    
    # Check sample modules across tiers
    keys = [m["key"] for m in data["modules"]]
    assert "rc/beam/rc_beam" in keys
    assert "rc/column/rc_column" in keys
    assert "rc/footing/rc_iso_footing" in keys
    assert "rc/slab/rc_slab" in keys
    assert "rc/wall/rc_shear_wall" in keys
    assert "steel/beam/steel_beam_column" in keys
    assert "steel/baseplate/steel_baseplate" in keys
    assert "steel/conn/steel_bolt_conn" in keys
    assert "fem/foundation/foundation_fem" in keys
    assert "rc/special/rc_stair" in keys


def test_get_module_schema():
    """Verify retrieving Pydantic JSON schema for dynamic form."""
    # 1. RC Beam Schema
    resp_rc = client.get("/api/schema/rc/beam/base")
    assert resp_rc.status_code == 200
    data_rc = resp_rc.json()
    assert data_rc["key"] == "rc/beam/base"
    assert "properties" in data_rc["schema"]
    assert "b" in data_rc["schema"]["properties"]
    assert "h" in data_rc["schema"]["properties"]
    assert "rebar_grade" in data_rc["schema"]["properties"]

    # 2. Steel Member Beam Schema
    resp_steel = client.get("/api/schema/steel/member/beam")
    assert resp_steel.status_code == 200
    data_steel = resp_steel.json()
    assert data_steel["key"] == "steel/member/beam"
    assert "properties" in data_steel["schema"]

    # 3. Non-existent module 404
    resp_404 = client.get("/api/schema/rc/unknown/invalid")
    assert resp_404.status_code == 404
