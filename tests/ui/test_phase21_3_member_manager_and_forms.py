"""Tests for Phase 21-3: Multi-Member Manager Pane 1 & Parametric Input Form Pane 2.

Validates:
1. Pane 1 (#pane-member-list) & Pane 2 (#pane-input-form) elements in index.html.
2. member_manager.js: 6-column spreadsheet summary table, rebar/force summaries, 2-stage font-color DCR text.
3. form_generator.js: 4 high-access subtabs (geom_mat, reinf, force, option), 3-button toolbar, sub-dialog triggers (...).
4. common_dialogs.js: 4 original app 1:1 sub-dialogs (IDD_RCS_BEAM_BEFF_DLG, IDD_RCS_COLUMN_SWAY_DLG, IDD_STEEL_SECTION_DB_DLG, IDD_LOAD_COMBINATION_DLG).
5. CSS styling: components.css, modal.css subtabs, buttons, and font-color DCR texts.
"""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_pane1_and_pane2_structure():
    """Verify presence of Pane 1 and Pane 2 core DOM structures and scripts."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Pane 1: Member Manager
    assert 'id="pane-member-list"' in html
    assert 'id="member-list-container"' in html
    assert 'id="member-count-badge"' in html
    assert 'id="btn-add-member"' in html
    assert 'id="btn-dup-member"' in html
    assert 'id="btn-del-member"' in html

    # Pane 2: Input Form & 2-Tier Header
    assert 'id="pane-input-form"' in html
    assert 'id="active-member-tag"' in html
    assert 'id="stage-breadcrumb-banner"' in html
    assert 'id="dynamic-form"' in html

    # Scripts
    assert "/static/js/components/member_manager.js" in html
    assert "/static/js/components/form_generator.js" in html
    assert "/static/js/components/form_combobox.js" in html
    assert "/static/js/core/common_dialogs.js" in html
    assert "/static/js/core/modal_manager.js" in html


def test_member_manager_js_specifications():
    """Verify member_manager.js implementation matches Req 21-3 specifications."""
    res = client.get("/static/js/components/member_manager.js")
    assert res.status_code == 200
    js = res.text

    # Table columns (부재명, 단면 치수, 주요 배근/형강, 소요력, DCR 상태)
    assert "member-table" in js
    assert "단면 치수" in js
    assert "주요 배근 / 형강" in js
    assert "소요력" in js
    assert "DCR 상태" in js

    # Summary extractors
    assert "_extractSectionSummary" in js
    assert "_extractRebarSummary" in js
    assert "_extractForceSummary" in js

    # 2-stage Font-color DCR text (chips/background removed)
    assert "dcr-status-text" in js
    assert "dcr-text-ok" in js
    assert "dcr-text-ng" in js
    assert "dcr-text-ready" in js
    assert "OK" in js
    assert "NG" in js


def test_form_generator_js_4_subtabs_and_actions():
    """Verify form_generator.js implementation for 4 subtabs and 3-button pipeline."""
    res = client.get("/static/js/components/form_generator.js")
    assert res.status_code == 200
    js = res.text

    # 4 SubTabs
    assert "sub-tab-bar" in js
    assert "sub-tab-btn" in js
    assert "sub-tab-pane" in js
    assert "geom_mat" in js
    assert "reinf" in js
    assert "force" in js
    assert "option" in js

    # 3-button toolbar
    assert "btn-run-apply" in js
    assert "btn-run-check" in js
    assert "btn-run-design" in js

    # Sub-dialog button (...)
    assert "btn-more-dlg" in js
    assert "_attachSubDialogButton" in js
    assert "_openBeffDialog" in js
    assert "_openColumnSwayDialog" in js
    assert "_openSectionDbDialog" in js
    assert "_openLoadCombinationDialog" in js


def test_common_dialogs_4_core_sub_modals():
    """Verify common_dialogs.js provides 4 core KDS engineering modals."""
    res = client.get("/static/js/core/common_dialogs.js")
    assert res.status_code == 200
    js = res.text

    # 1. Beam beff modal
    assert "openBeamBeffDialog" in js
    assert "IDD_RCS_BEAM_BEFF_DLG" in js

    # 2. Column Sway modal
    assert "openColumnSwayDialog" in js
    assert "IDD_RCS_COLUMN_SWAY_DLG" in js

    # 3. Steel Section DB modal
    assert "openSectionDb" in js
    assert "IDD_STEEL_SECTION_DB_DLG" in js

    # 4. Load Combination modal
    assert "openLoadCombination" in js
    assert "IDD_LOAD_COMBINATION_DLG" in js


def test_css_styles_for_phase21_3():
    """Verify styling in components.css and modal.css."""
    res_comp = client.get("/static/css/components.css")
    assert res_comp.status_code == 200
    assert ".dcr-status-text" in res_comp.text
    assert ".dcr-text-ok" in res_comp.text
    assert ".dcr-text-ng" in res_comp.text

    res_modal = client.get("/static/css/modal.css")
    assert res_modal.status_code == 200
    assert ".sub-tab-bar" in res_modal.text
    assert ".sub-tab-btn" in res_modal.text
    assert ".sub-tab-pane" in res_modal.text
    assert ".btn-more-dlg" in res_modal.text
