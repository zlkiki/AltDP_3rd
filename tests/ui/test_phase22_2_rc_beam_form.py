"""Tests for Phase 22-2: RC Beam Original App 1:1 Subtab Form & Modals.
Conforms to Requirement 22-2, docs/07 PART 4, and docs/16.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_form_rc_beam_js_serving():
    """Verify that form_rc_beam.js is served correctly with HTTP 200."""
    response = client.get("/static/js/components/form_rc_beam.js")
    assert response.status_code == 200
    content = response.text
    assert "RCBeamFormComponent" in content
    assert "window.RCBeamForm" in content
    assert "IDD_RCS_BEAM_PMODE_DLG" in content


def test_index_html_contains_form_rc_beam():
    """Verify that index.html includes form_rc_beam.js."""
    response = client.get("/")
    assert response.status_code == 200
    assert "/static/js/components/form_rc_beam.js" in response.text


def test_common_dialogs_has_beam_rebar_dialog():
    """Verify that common_dialogs.js contains openBeamRebarDialog and IDD_RCS_BEAM_REBAR_DLG."""
    response = client.get("/static/js/core/common_dialogs.js")
    assert response.status_code == 200
    content = response.text
    assert "openBeamRebarDialog" in content
    assert "IDD_RCS_BEAM_REBAR_DLG" in content
    assert "dlg-rebar-main-hook" in content
    assert "dlg-rebar-stirrup-hook" in content
    assert "dlg-rebar-stirrup-legs" in content
    assert "dlg-rebar-splice" in content


def test_common_dialogs_has_beam_beff_dialog():
    """Verify that common_dialogs.js contains openBeamBeffDialog and IDD_RCS_BEAM_BEFF_DLG."""
    response = client.get("/static/js/core/common_dialogs.js")
    assert response.status_code == 200
    content = response.text
    assert "openBeamBeffDialog" in content
    assert "IDD_RCS_BEAM_BEFF_DLG" in content
    assert "dlg-beff-bw" in content
    assert "dlg-beff-hf" in content


def test_form_rc_beam_subtabs_and_structure():
    """Verify that form_rc_beam.js includes all 4 subtabs and critical engineering elements."""
    response = client.get("/static/js/components/form_rc_beam.js")
    assert response.status_code == 200
    content = response.text

    # 4 Subtabs
    assert "단면 / 재료" in content
    assert "철근 배근" in content
    assert "부재력 / 하중" in content
    assert "사용성 / 처짐" in content

    # Tab 1: Section & Material
    assert "RECTANGULAR" in content
    assert "TEE" in content
    assert "beam-input-bw" in content
    assert "beam-input-h" in content
    assert "beam-input-span" in content
    assert "beam-select-fck" in content
    assert "beam-select-fy" in content
    assert "beam-select-fyt" in content
    assert "openBeamBeffDialog" in content

    # Tab 2: Reinforcement Detailing
    assert "rb-endi-t1" in content
    assert "rb-cent-b1" in content
    assert "rb-endj-t1" in content
    assert "openBeamRebarDialog" in content
    assert "beam-spacing-badge" in content
    assert "beam-input-torsion-bar" in content
    assert "beam-input-torsion-count" in content

    # Tab 3: Design Factored Loads
    assert "ld-endi-mup" in content
    assert "ld-cent-mup" in content
    assert "ld-endj-vu" in content
    assert "openLoadCombination" in content

    # Tab 4: Serviceability & Deflection
    assert "beam-input-mapos" in content
    assert "beam-input-maneg" in content
    assert "beam-input-msus" in content
    assert "beam-input-defl-limit" in content
    assert "beam-select-exposure" in content
    assert "beam-select-seismic" in content


def test_rc_beam_module_uses_rc_beam_form():
    """Verify that rc_beam_module.js mounts RCBeamForm and has complete KDS schema defaults."""
    response = client.get("/static/js/modules/rc_beam/rc_beam_module.js")
    assert response.status_code == 200
    content = response.text

    assert "window.RCBeamForm" in content
    assert "RCBeamForm.render" in content
    assert "rebar" in content
    assert "loads" in content
    assert "serviceability" in content
