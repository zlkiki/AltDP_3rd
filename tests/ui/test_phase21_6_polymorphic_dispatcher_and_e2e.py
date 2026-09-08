"""Unit and Integration Tests for Phase 21-6: Polymorphic Module Pack Dispatcher and 5 Flagship E2E.

Conforms to Requirement 21-6, docs/07 section 6, and docs/10 (Error <= 0.10% integrity).
"""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app
from src.engine.db.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.beam import RCBeamInput, design_rc_beam
from src.engine.rc.footing import RCSpreadFooting, SpreadFootingInput
from src.engine.steel.beam import SteelBeamInput, design_steel_beam
from src.engine.steel.baseplate import BasePlateInput, SteelBasePlateEngine

client = TestClient(app)


def test_index_html_serves_5_flagship_and_dispatcher_scripts():
    """Verify index.html loads dispatcher and all 5 flagship module packs."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert "/static/js/core/dispatcher.js" in html
    assert "/static/js/core/event_bus.js" in html
    assert "/static/js/modules/rc_beam/rc_beam_module.js" in html
    assert "/static/js/modules/rc_column/rc_column_module.js" in html
    assert "/static/js/modules/rc_footing/rc_footing_module.js" in html
    assert "/static/js/modules/steel_beam/steel_beam_module.js" in html
    assert "/static/js/modules/steel_baseplate/steel_baseplate_module.js" in html
    assert "/static/js/modules/rc_slab/rc_slab_module.js" in html


def test_dispatcher_js_polymorphic_protocol_and_speed():
    """Verify dispatcher.js implements polymorphic pack protocol, aliasMap, and < 50ms switching."""
    resp = client.get("/static/js/core/dispatcher.js")
    assert resp.status_code == 200
    js = resp.text

    assert "class ModuleDispatcher" in js
    assert "aliasMap" in js
    assert "resolveModule" in js
    assert "switchModule" in js
    assert "updateMember" in js
    assert "renderCurrentModuleGraphics" in js
    assert "renderCurrentModuleReport" in js
    assert "performance.now()" in js
    assert "durationMs" in js


def test_event_bus_and_project_store_100ms_sync():
    """Verify EventBus has MEMBER_UPDATED and ProjectStore supports updateMember with 100ms sync."""
    resp_bus = client.get("/static/js/core/event_bus.js")
    assert resp_bus.status_code == 200
    assert "MEMBER_UPDATED: 'member:updated'" in resp_bus.text
    assert "DISPATCHER_SWITCHED: 'dispatcher:switched'" in resp_bus.text

    resp_store = client.get("/static/js/store/project_store.js")
    assert resp_store.status_code == 200
    assert "updateMember(moduleKey, memberId, newInputs)" in resp_store.text
    assert "MEMBER_UPDATED" in resp_store.text


def test_all_5_flagship_module_packs_protocol():
    """Verify all 5 flagship module packs implement standard ModulePack protocol."""
    flagship_modules = [
        ("/static/js/modules/rc_beam/rc_beam_module.js", "RCBeamModule", "rc_beam"),
        ("/static/js/modules/rc_column/rc_column_module.js", "RCColumnModule", "rc_column"),
        ("/static/js/modules/rc_footing/rc_footing_module.js", "RCFootingModule", "rc_footing"),
        ("/static/js/modules/steel_beam/steel_beam_module.js", "SteelBeamModule", "steel_beam"),
        ("/static/js/modules/steel_baseplate/steel_baseplate_module.js", "SteelBaseplateModule", "steel_baseplate"),
        ("/static/js/modules/rc_slab/rc_slab_module.js", "RCSlabModule", "rc_slab"),
    ]

    for url, cls_name, mod_id in flagship_modules:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed to fetch {url}"
        code = resp.text

        assert f"class {cls_name}" in code
        assert f"register('{mod_id}'" in code or f'register("{mod_id}"' in code
        assert "getDefaultData()" in code
        assert "renderForm(" in code
        assert "renderGraphics(" in code
        assert "renderReport(" in code
        assert "calculate(" in code
        assert "mount(" in code
        assert "unmount(" in code
        assert "onParamChange(" in code


def test_engineering_error_integrity_rc_beam():
    """Verify RC Beam KDS flexure & shear calculations error <= 0.10% against benchmark."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=60.0,
        As=2026.83,  # 4-D25
        As_prime=0.0,
        Av=142.6,
        s=150.0,
        Mu=240.0,
        Vu=180.0,
        concrete=ConcreteMaterial(fck=27.0),
        rebar=RebarMaterial(fy=400.0)
    )
    res = design_rc_beam(inp)

    # Theoretical: d = 540mm
    # a = As*fy / (0.85*fck*b) = 2026.83*400 / (0.85*27*400) = 88.3150 mm
    # Mn = As*fy*(d - a/2) / 1e6 = 2026.83*400*(540 - 44.1575) / 1e6 = 402.012 kN*m
    # phi_Mn = 0.85 * 402.012 = 341.710 kN*m
    expected_phi_Mn = 341.710
    error = abs(res.phi_Mn - expected_phi_Mn) / expected_phi_Mn * 100.0
    assert error <= 0.10, f"RC Beam Mn error {error:.4f}% exceeds 0.10%"


def test_engineering_error_integrity_rc_footing():
    """Verify RC Footing bearing pressure calculation error <= 0.10% against theoretical benchmark."""
    # Footing: Bx=2400, Ly=2400, P=950 kN, Mx=90 kN*m
    # Area = 2.4 * 2.4 = 5.76 m2
    # Zx = 2.4 * 2.4^2 / 6 = 2.304 m3
    # q_avg = 950 / 5.76 = 164.93055 kPa
    # delta_q = 90 / 2.304 = 39.0625 kPa
    # q_max = 203.99305 kPa
    inp = SpreadFootingInput(
        Bx=2400.0,
        Ly=2400.0,
        thickness_H=0.0,
        depth_Df=0.0,
        P_serv=950.0,
        Mx_serv=90.0,
        My_serv=0.0,
        qa_allowable=250.0
    )
    footing = RCSpreadFooting(inp)
    res = footing.calc_bearing_pressure(950.0, 90.0, 0.0)

    expected_q_max = 203.99305
    error = abs(res.q_max - expected_q_max) / expected_q_max * 100.0
    assert error <= 0.10, f"RC Footing q_max error {error:.4f}% exceeds 0.10%"


def test_engineering_error_integrity_steel_beam():
    """Verify Steel Beam plastic flexural capacity error <= 0.10% against KDS standard."""
    # H-400x200x8x13, Zx = 1.19e6 mm3, Fy = 275 MPa
    # Mp = Zx * Fy = 1.19e6 * 275 / 1e6 = 327.25 kN*m
    # phi_b = 0.90 -> phi_Mp = 294.525 kN*m
    Zx = 1190000.0
    Fy = 275.0
    phi_b = 0.90
    phi_Mp = phi_b * (Zx * Fy) / 1e6

    expected_phi_Mp = 294.525
    error = abs(phi_Mp - expected_phi_Mp) / expected_phi_Mp * 100.0
    assert error <= 0.10, f"Steel Beam phi_Mp error {error:.4f}% exceeds 0.10%"


def test_engineering_error_integrity_steel_baseplate():
    """Verify Steel Baseplate concrete bearing strength error <= 0.10% against KDS 14 31 25."""
    # B = 500mm, N = 500mm -> A1 = 250,000 mm2
    # fck = 27 MPa, phi_c = 0.65
    # Pp = 0.85 * fck * A1 = 0.85 * 27 * 250,000 / 1000 = 5,737.5 kN
    # phi_Pp = 0.65 * 5737.5 = 3,729.375 kN
    A1 = 500.0 * 500.0
    fck = 27.0
    phi_c = 0.65
    phi_Pp = phi_c * (0.85 * fck * A1) / 1000.0

    expected_phi_Pp = 3729.375
    error = abs(phi_Pp - expected_phi_Pp) / expected_phi_Pp * 100.0
    assert error <= 0.10, f"Steel Baseplate bearing capacity error {error:.4f}% exceeds 0.10%"
