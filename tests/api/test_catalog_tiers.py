"""Test Suite for 61 Original App Member Modules and 3-Tier Classification (Phase 20-2).

Verifies Requirements 20-2 acceptance criteria:
1. Exact 61 unique member design modules with 0 omissions.
2. 3-tier distribution: Tier 1 (9), Tier 2 (26), Tier 3 (26).
3. Engine status: VERIFIED (35), WIP (26).
4. Mandatory fields (key, name, midas_dlg, category, tier, standard, engine_status) present and valid across all 61 modules.
5. GET /api/modules endpoint and summary statistics fidelity.
6. Frontend catalog.js parity with backend SSOT.
"""

import os
import re
import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from src.api.models.wip import MODULE_CATALOG_61, get_catalog_stats, get_wip_module_detail
from app.engines import get_all_modules_meta, get_module

client = TestClient(app)


def test_catalog_61_modules_count_and_tier_distribution():
    """Verify exact count of 61 modules and 3-tier distribution per Requirements 20-2."""
    assert len(MODULE_CATALOG_61) == 61, f"Expected 61 modules, found {len(MODULE_CATALOG_61)}"
    
    stats = get_catalog_stats()
    assert stats["total"] == 61
    assert stats["tier1"] == 9
    assert stats["tier2"] == 26
    assert stats["tier3"] == 26
    assert stats["verified"] == 35
    assert stats["wip"] == 26
    assert stats["tier1"] + stats["tier2"] + stats["tier3"] == 61
    assert stats["verified"] + stats["wip"] == 61


def test_catalog_mandatory_metadata_fields():
    """Verify all 61 modules have complete, non-empty mandatory metadata fields."""
    mandatory_fields = [
        "key", "name", "midas_dlg", "category", "group", "id",
        "tier", "standard", "engine_status"
    ]
    
    valid_tiers = {"Tier 1", "Tier 2", "Tier 3"}
    valid_statuses = {"VERIFIED", "WIP"}
    valid_categories = {"rc", "steel", "src", "alu", "fem", "rfm", "pbd", "report", "interop", "intl"}

    for mod_id, meta in MODULE_CATALOG_61.items():
        for field in mandatory_fields:
            assert field in meta, f"Module '{mod_id}' missing required field '{field}'"
            val = meta[field]
            assert isinstance(val, str) and len(val.strip()) > 0, (
                f"Module '{mod_id}' field '{field}' must be a non-empty string, got '{val}'"
            )
        
        # Validate tier
        assert meta["tier"] in valid_tiers, f"Module '{mod_id}' invalid tier '{meta['tier']}'"
        
        # Validate engine status
        assert meta["engine_status"] in valid_statuses, (
            f"Module '{mod_id}' invalid engine_status '{meta['engine_status']}'"
        )
        
        # Validate category
        assert meta["category"] in valid_categories, (
            f"Module '{mod_id}' category '{meta['category']}' not recognized"
        )

        # Tier 1 and Tier 2 must be VERIFIED
        if meta["tier"] in ["Tier 1", "Tier 2"]:
            assert meta["engine_status"] == "VERIFIED", (
                f"{meta['tier']} module '{mod_id}' must have engine_status VERIFIED"
            )
        # Tier 3 must be WIP
        elif meta["tier"] == "Tier 3":
            assert meta["engine_status"] == "WIP", (
                f"Tier 3 module '{mod_id}' must have engine_status WIP"
            )


def test_get_modules_api_endpoint():
    """Verify GET /api/modules returns 61 modules with summary stats."""
    res = client.get("/api/modules")
    assert res.status_code == 200
    data = res.json()
    
    assert "modules" in data
    assert "total_count" in data
    assert "summary" in data
    
    assert data["total_count"] == 61
    assert len(data["modules"]) == 61
    
    summary = data["summary"]
    assert summary["total"] == 61
    assert summary["tier1"] == 9
    assert summary["tier2"] == 26
    assert summary["tier3"] == 26
    assert summary["verified"] == 35
    assert summary["wip"] == 26

    # Verify each module in response
    keys_seen = set()
    for mod in data["modules"]:
        assert "key" in mod
        assert "name" in mod
        assert "midas_dlg" in mod
        assert "tier" in mod
        assert "standard" in mod
        assert "engine_status" in mod
        
        # Key must be unique
        assert mod["key"] not in keys_seen, f"Duplicate module key '{mod['key']}' found"
        keys_seen.add(mod["key"])
        
    assert len(keys_seen) == 61


def test_catalog_tier1_flagship_modules():
    """Verify the 9 Tier 1 flagship modules specifically match Requirements 20-2 Section 2.2.A."""
    tier1_expected = [
        ("rc/beam/rc_beam", "IDD_RCS_BEAM_PMODE_DLG", "VERIFIED"),
        ("rc/column/rc_column", "IDD_RCS_COLUMN_PMODE_DLG", "VERIFIED"),
        ("rc/wall/rc_shear_wall", "IDD_RCS_WALL_PMODE_DLG", "VERIFIED"),
        ("rc/retaining_wall/rc_retaining_wall", "IDD_RCS_RETAINING_WALL_INPUT_DLG", "VERIFIED"),
        ("rc/slab/rc_slab", "IDD_RCS_SLAB_PMODE_DLG", "VERIFIED"),
        ("rc/footing/rc_iso_footing", "IDD_RCS_FOOT_PMODE_DLG", "VERIFIED"),
        ("steel/beam/steel_beam_column", "IDD_STL_BEAMCOLUMN_INPUT_DLG", "VERIFIED"),
        ("steel/baseplate/steel_baseplate", "IDD_STL_USBP_PMODE_DLG", "VERIFIED"),
        ("steel/conn/steel_bolt_conn", "IDD_STL_BOLTCONNECTION_INPUT_DLG", "VERIFIED")
    ]
    
    tier1_map = {m["key"]: m for m in MODULE_CATALOG_61.values() if m["tier"] == "Tier 1"}
    assert len(tier1_map) == 9
    
    for key, expected_dlg, expected_status in tier1_expected:
        assert key in tier1_map, f"Missing expected Tier 1 module '{key}'"
        mod = tier1_map[key]
        assert mod["midas_dlg"] == expected_dlg
        assert mod["engine_status"] == expected_status


def test_catalog_frontend_parity():
    """Verify frontend src/web/static/js/catalog.js exists and matches backend SSOT."""
    catalog_js_path = os.path.join(os.path.dirname(__file__), "../../src/web/static/js/catalog.js")
    assert os.path.isfile(catalog_js_path), f"catalog.js file not found at {catalog_js_path}"
    
    with open(catalog_js_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check that all 61 keys appear in catalog.js
    for mod_id, meta in MODULE_CATALOG_61.items():
        assert meta["key"] in content, f"Module key '{meta['key']}' missing from catalog.js"
        assert meta["midas_dlg"] in content, f"Dialog ID '{meta['midas_dlg']}' missing from catalog.js"


def test_module_schema_resolution_all_61():
    """Verify get_module can resolve all 61 modules without crashing."""
    for mod_id, meta in MODULE_CATALOG_61.items():
        cat = meta["category"]
        grp = meta["group"]
        mid = meta["id"]
        mod = get_module(cat, grp, mid)
        assert mod is not None, f"get_module failed to resolve '{cat}/{grp}/{mid}'"
        assert "key" in mod
        assert "info" in mod
        assert "schema_json" in mod
