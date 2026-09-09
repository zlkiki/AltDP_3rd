"""Tests for Phase 22-4-1-3: RC Beam Original App 1:1 Arrange Type Radios & Rebar Composite UI.
Conforms to Requirement 22-4-1-3, docs/07 PART 4, and docs/16.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_form_rc_beam_arrange_type_radios():
    """Verify that form_rc_beam.js includes arrange type radio group and 3 types."""
    response = client.get("/static/js/components/form_rc_beam.js")
    assert response.status_code == 200
    content = response.text

    # Radio group name & Arrange type titles
    assert "beam_arrange_type" in content
    assert "배근 유형 (Reinforcement Arrange Type)" in content
    assert "ONE_SECTION" in content
    assert "SYMMETRIC_ENDS" in content
    assert "THREE_STATIONS" in content

    # Ground Truth labels from DLG_DPLUS_RCS.ini
    assert "배근 유형-1 (전단면)" in content
    assert "배근 유형-2 (양단부와 중앙부)" in content
    assert "배근 유형-3 (각단부와 중앙부)" in content

    # Default arrange_type in _normalizeData
    assert "arrange_type: raw.rebar?.arrange_type || 'SYMMETRIC_ENDS'" in content


def test_form_rc_beam_composite_controls():
    """Verify that form_rc_beam.js renders composite inline rebar controls (count + '-' + dia)."""
    response = client.get("/static/js/components/form_rc_beam.js")
    assert response.status_code == 200
    content = response.text

    # Composite element structure
    assert "rebar-cell-composite" in content
    assert "rebar-count-input" in content
    assert "rebar-sep" in content
    assert "rebar-dia-select" in content

    # 9 Core Rebar Diameters
    for dia in ["D10", "D13", "D16", "D19", "D22", "D25", "D29", "D32", "D35"]:
        assert f"'{dia}'" in content or f'"{dia}"' in content

    # Min count constraints (Layer 1: 2, Layer 2: 0)
    assert 'min="${isLayer2 ? 0 : 2}"' in content or 'min="${minCount}"' in content


def test_form_rc_beam_interlock_and_sync_logic():
    """Verify that form_rc_beam.js contains synchronization and visual tag logic."""
    response = client.get("/static/js/components/form_rc_beam.js")
    assert response.status_code == 200
    content = response.text

    # _parseRebarStr method
    assert "_parseRebarStr(" in content

    # Arrange Type UI tags
    assert "tag-endj-sym" in content
    assert "[단부-I 대칭 연동]" in content
    assert "[전단면 연동]" in content

    # UI update & DOM state management
    assert "_updateArrangeTypeUI(" in content
    assert "badge-sym-tag" in content


def test_modal_css_rebar_composite_styles():
    """Verify that modal.css serves composite rebar control and responsive styles."""
    response = client.get("/static/css/modal.css")
    assert response.status_code == 200
    content = response.text

    assert ".rebar-cell-composite" in content
    assert ".rebar-count-input" in content
    assert ".rebar-sep" in content
    assert ".rebar-dia-select" in content
    assert "min-width: 110px;" in content
    assert ".beam-rebar-table-wrap" in content
    assert ".badge-sym-tag" in content
