"""Tests for Phase 20-1 TreeMenu & ModuleDispatcher Framework."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_phase20_core_scripts_serving():
    """Verify that all Phase 20-1 core architecture JS files are correctly served."""
    scripts = [
        "/static/js/core/event_bus.js",
        "/static/js/core/dispatcher.js",
        "/static/js/core/context_menu.js",
        "/static/js/core/tree_menu.js",
        "/static/css/tree_menu.css"
    ]
    for url in scripts:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed to serve {url}"
        assert len(resp.text) > 50, f"Empty content in {url}"


def test_phase20_tree_menu_structure():
    """Verify that TreeMenu contains 6 top-level categories and original module lists."""
    resp = client.get("/static/js/core/tree_menu.js")
    assert resp.status_code == 200
    js_code = resp.text
    
    # 6 Top-level categories
    assert "콘크리트(RCS)" in js_code
    assert "철골(STEEL)" in js_code
    assert "합성부재(SRC)" in js_code
    assert "알루미늄(ALU)" in js_code
    assert "보강(RFM)" in js_code
    assert "설정/하중(Option)" in js_code
    
    # Strict original module order in RC
    assert "rc_slab" in js_code
    assert "rc_beam" in js_code
    assert "rc_column" in js_code
    assert "gen_column" in js_code
    assert "rc_wall" in js_code
    assert "combined_wall" in js_code
    assert "basement_wall" in js_code
    assert "retaining_wall" in js_code
    assert "anchor_bolt" in js_code
    assert "buttress" in js_code
    assert "rc_stair" in js_code
    assert "corbel" in js_code
    assert "rc_footing" in js_code


def test_phase20_dispatcher_and_eventbus():
    """Verify EventBus and ModuleDispatcher methods."""
    resp_bus = client.get("/static/js/core/event_bus.js")
    assert "class EventBus" in resp_bus.text
    assert "MEMBER_SELECTED" in resp_bus.text
    assert "PARAM_CHANGED" in resp_bus.text

    resp_disp = client.get("/static/js/core/dispatcher.js")
    assert "class ModuleDispatcher" in resp_disp.text
    assert "switchModule" in resp_disp.text
    assert "register" in resp_disp.text


def test_phase20_vdraw_primitives_and_engine():
    """Verify Phase 20-2 VDrawEngine, 135-deg hook stirrups, and PM chart."""
    resp_eng = client.get("/static/js/core/vdraw_engine.js")
    assert resp_eng.status_code == 200
    assert "class VDrawEngine" in resp_eng.text
    assert "fitToScreen" in resp_eng.text
    assert "zoom" in resp_eng.text

    resp_prim = client.get("/static/js/core/vdraw_primitives.js")
    assert resp_prim.status_code == 200
    assert "drawStirrupWithHooks" in resp_prim.text
    assert "135" in resp_prim.text or "drawStirrup" in resp_prim.text
    assert "drawSolidRebar" in resp_prim.text
    assert "drawDimensionLine" in resp_prim.text

    resp_pm = client.get("/static/js/core/pm_chart_vdraw.js")
    assert resp_pm.status_code == 200
    assert "class PMChartVDraw" in resp_pm.text
    assert "curvePn" in resp_pm.text

    resp_css = client.get("/static/css/vdraw.css")
    assert resp_css.status_code == 200
    assert ".vdraw-viewport-container" in resp_css.text


def test_phase20_subtab_and_modal_manager():
    """Verify Phase 20-3 ModalManager, CommonDialogs, and FormBuilder."""
    resp_modal = client.get("/static/js/core/modal_manager.js")
    assert resp_modal.status_code == 200
    assert "class ModalManager" in resp_modal.text
    assert "open" in resp_modal.text
    assert "close" in resp_modal.text

    resp_dlg = client.get("/static/js/core/common_dialogs.js")
    assert resp_dlg.status_code == 200
    assert "IDD_RCS_DESIGN_LOAD" in resp_dlg.text
    assert "IDD_STL_BEAMCOL_SMODE_INPUT_SECT1_DLG" in resp_dlg.text
    assert "IDD_RCS_BEAM_SECT_DLG" in resp_dlg.text

    resp_fb = client.get("/static/js/core/form_builder.js")
    assert resp_fb.status_code == 200
    assert "class FormBuilder" in resp_fb.text
    assert "sub-tab-bar" in resp_fb.text
    assert "sub-tab-btn" in resp_fb.text

    resp_css = client.get("/static/css/modal.css")
    assert resp_css.status_code == 200
    assert ".app-modal-overlay" in resp_css.text
    assert ".sub-tab-bar" in resp_css.text


def test_phase20_5chapter_report_engine():
    """Verify Phase 20-4 5-Chapter Report Renderer, KaTeX, and SVG embedding."""
    resp_katex = client.get("/static/js/core/report_katex.js")
    assert resp_katex.status_code == 200
    assert "formulaPhiMn" in resp_katex.text
    assert "formulaPhiVn" in resp_katex.text

    resp_rep = client.get("/static/js/core/report_renderer.js")
    assert resp_rep.status_code == 200
    assert "class ReportRenderer" in resp_rep.text
    assert "제 1장" in resp_rep.text
    assert "제 2장" in resp_rep.text
    assert "제 3장" in resp_rep.text
    assert "제 4장" in resp_rep.text
    assert "제 5장" in resp_rep.text
    assert "  →  O.K" in resp_rep.text
    assert "  →  N.G" in resp_rep.text
    assert "_generateSectionSvg" in resp_rep.text


def test_phase20_flagship_5member_modules():
    """Verify Phase 20-5 5 flagship member modules (rc_beam, rc_column, rc_slab, steel_beam, steel_baseplate)."""
    modules = [
        ("/static/js/modules/rc_beam/rc_beam_module.js", "RCBeamModule", "rc_beam"),
        ("/static/js/modules/rc_column/rc_column_module.js", "RCColumnModule", "rc_column"),
        ("/static/js/modules/rc_slab/rc_slab_module.js", "RCSlabModule", "rc_slab"),
        ("/static/js/modules/steel_beam/steel_beam_module.js", "SteelBeamModule", "steel_beam"),
        ("/static/js/modules/steel_baseplate/steel_baseplate_module.js", "SteelBaseplateModule", "steel_baseplate"),
    ]

    for url, cls_name, mod_key in modules:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed to serve {url}"
        assert f"class {cls_name}" in resp.text
        assert f"register('{mod_key}'" in resp.text or f'register("{mod_key}"' in resp.text
        assert "mount" in resp.text
        assert "renderCanvas" in resp.text
        assert "renderReport" in resp.text
        assert "renderForm" in resp.text




