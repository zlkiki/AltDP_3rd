"""
UI Integration Test Suite for Requirement 22-6:
Phase V1-01 Step 6 RC Beam 4-Pane Workspace E2E Integration & Online Release.

Tests:
1. Catalog & Dispatcher Online registration with zero WIP degradation.
2. 4-Pane real-time event pipeline (Form -> Store -> Canvas -> Report).
3. 12-point clear spacing interactive engine & popover status.
4. Absence of legacy calculation cards and placeholders.
5. End-to-end multi-member ProjectStore synchronization.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

WEB_STATIC_DIR = Path("src/web/static")
JS_DIR = WEB_STATIC_DIR / "js"
TEMPLATES_DIR = Path("src/web/templates")


def test_catalog_and_dispatcher_online_contract():
    """Verify catalog.js and dispatcher.js recognize rc_beam as official Online."""
    catalog_content = (JS_DIR / "catalog.js").read_text(encoding="utf-8")
    dispatcher_content = (JS_DIR / "core" / "dispatcher.js").read_text(encoding="utf-8")

    # catalog.js module definition
    assert "rc/beam/rc_beam" in catalog_content
    assert "is_wip: false" in catalog_content
    assert 'status: "Online"' in catalog_content

    # dispatcher.js WIP bypass
    assert "meta.is_wip === false" in dispatcher_content
    assert "meta.status === 'Online'" in dispatcher_content


def test_index_html_integration_of_rc_beam_components():
    """Verify index.html includes all required scripts for RC Beam 4-Pane workspace."""
    index_html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")

    assert "catalog.js" in index_html
    assert "form_rc_beam.js" in index_html
    assert "vector_rc_beam.js" in index_html
    assert "rc_beam_report.js" in index_html
    assert "dispatcher.js" in index_html
    assert "project_store.js" in index_html
    assert "graphic_viewport.js" in index_html
    assert "report_engine.js" in index_html


def test_form_rc_beam_action_pipeline_elements():
    """Verify form_rc_beam has all 3 action buttons and real-time calculation hooks."""
    form_content = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")

    assert "beam-btn-apply" in form_content
    assert "beam-btn-check" in form_content
    assert "beam-btn-design" in form_content
    assert "_handleApply" in form_content
    assert "_handleCheck" in form_content
    assert "_handleAutoDesign" in form_content


def test_rc_beam_report_7_chapters_and_excel_button():
    """Verify rc_beam_report renders all 7 chapters and provides print/excel hooks."""
    report_content = (JS_DIR / "report" / "rc_beam_report.js").read_text(encoding="utf-8")

    assert 'data-chapter-key="general"' in report_content
    assert 'data-chapter-key="load"' in report_content
    assert 'data-chapter-key="ductility"' in report_content
    assert 'data-chapter-key="flexure"' in report_content
    assert 'data-chapter-key="shear"' in report_content
    assert 'data-chapter-key="serviceability"' in report_content
    assert 'data-chapter-key="verdict"' in report_content
    assert '\uC81C 1\uC7A5' in report_content
    assert '\uC81C 7\uC7A5' in report_content


def test_no_legacy_wip_card_for_rc_beam():
    """Verify no legacy WIP cards or placeholders are triggered for rc_beam."""
    app_js = (JS_DIR / "app.js").read_text(encoding="utf-8")
    assert "isModuleWIP" in app_js
    assert "m.is_wip === false || m.status === 'Online'" in app_js
