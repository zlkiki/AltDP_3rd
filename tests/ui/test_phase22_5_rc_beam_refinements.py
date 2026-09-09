"""
Integration Test Suite for Requirement 22-5 & 22-5-4:
Phase V1-01 Step 5-4 RC Beam 12-Refinements Full E2E & Regression Test.

Verifies all 12 refinement items implemented across Steps 5-1, 5-2, and 5-3:
1. Ductility Limit & Min Rebar relocated to Chapter 3
2. Branching by arrangement type (ONE_SECTION, SYMMETRIC_ENDS, THREE_STATIONS)
3. KaTeX aligned multiline environment to prevent overflow
4. Branson weighted average I_e and long-term deflection
5. Elimination of messy bracket tags & clean 'O.K' verdicts
6. Universal DCR notation across all design checks
7. Dynamic omission & 1-line summary on zero loads (Tu <= 0, Mu <= 0)
8. Crack control s <= s_max with elastic stress fs per station
9. Canvas torsion side bar 0 count fix (nullish coalescing)
10. 12-point clear spacing full calculation & governing badge
11. Dynamic load table disabled & symmetric replication
12. Sticky floating header & 32px compact engineering action buttons
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.server import app
from src.engine.rc.beam import (
    calculate_rc_beam_design,
    RCBeamSection,
    RCBeamRebar,
    RCBeamLoads,
    RCBeamPositionLoads,
    RCBeamResult,
    SectionRebarGroup,
    RebarRow,
    BeamShape,
    SupportCondition,
    BeamArrangeType
)

client = TestClient(app)

WEB_STATIC_DIR = Path("src/web/static")
JS_DIR = WEB_STATIC_DIR / "js"
CSS_DIR = WEB_STATIC_DIR / "css"


# ==============================================================================
# Test 1: Serviceability Engine & Zero-Load Response (Items 4, 7, 8)
# ==============================================================================
def test_12_refinements_engine_serviceability_and_zero_load():
    """Verify calculate_rc_beam_design calculates serviceability (I_e, deflection, crack s_max)
    and populates zero-load flags and universal DCRs properly."""
    section = RCBeamSection(
        shape=BeamShape.RECTANGULAR,
        b=400.0,
        h=650.0,
        length=6000.0,
        cover=40.0,
        cover_top=40.0,
        fck=27.0,
        fy=400.0,
        fyt=400.0,
        support=SupportCondition.CONTINUOUS_BOTH
    )

    rebar = RCBeamRebar(
        arrange_type=BeamArrangeType.SYMMETRIC_ENDS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0,
            stirrup_legs=2
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=250.0,
            stirrup_legs=2
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0,
            stirrup_legs=2
        )
    )

    # 0 하중 (Tu = 0) 및 일반 휨/전단 하중
    loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=280.0, Vu=180.0, Tu=0.0, Ma_neg=170.0),
        center_m=RCBeamPositionLoads(Mu_pos=210.0, Mu_neg=0.0, Vu=80.0, Tu=0.0, Ma_pos=130.0, Msus=80.0),
        end_j=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=280.0, Vu=180.0, Tu=0.0, Ma_neg=170.0),
        deflection_limit_ratio=240.0
    )

    result: RCBeamResult = calculate_rc_beam_design(section, rebar, loads)

    # 1. Branson weighted average & deflection checks (Item 4)
    svc = result.serviceability
    assert svc.Ie_avg > 0.0
    assert svc.delta_immediate > 0.0
    assert svc.delta_long_term > 0.0
    assert svc.delta_total == pytest.approx(svc.delta_immediate + svc.delta_long_term, rel=1e-3)
    assert svc.dcr_defl > 0.0
    assert svc.dcr_defl == pytest.approx(svc.delta_total / svc.delta_allow, abs=1e-3)

    # 2. Crack control 3-station s <= s_max and elastic fs (Item 8)
    crack_checks = svc.crack_spacing_checks
    assert "end_i" in crack_checks
    assert "center_m" in crack_checks
    assert "end_j" in crack_checks
    center_crack = crack_checks["center_m"]
    assert center_crack.s_max > 0.0
    assert center_crack.fs > 0.0
    assert center_crack.dcr == pytest.approx(center_crack.s_actual / center_crack.s_max, abs=1e-3)

    # 3. Zero torsion flags & summary (Item 7)
    for st in [result.end_i, result.center_m, result.end_j]:
        assert st.is_zero_torsion is True
        assert st.torsion.is_zero_torsion is True
        assert st.torsion.dcr == 0.0

    # 4. API Endpoint verification
    api_payload = {
        "name": "B1", "b": 400.0, "h": 650.0, "cover": 40.0, "cover_prime": 40.0,
        "As": 2026.8, "As_prime": 1013.4, "Av": 142.6, "s": 150.0,
        "Mu": 280.0, "Vu": 180.0, "Tu": 0.0, "Ma": 170.0, "span_length": 6000.0,
        "fck": 27.0, "fy": 400.0
    }
    api_res = client.post("/api/rc/beam/check", json=api_payload)
    assert api_res.status_code == 200
    api_data = api_res.json()["data"]
    assert api_data["is_torsion_ignored"] is True
    assert api_data["deflection_dcr"] > 0.0


# ==============================================================================
# Test 2: Calculation Report 7 Chapters, KaTeX aligned, Clean Tags (Items 1, 3, 5, 6)
# ==============================================================================
def test_12_refinements_report_structure_and_katex():
    """Verify rc_beam_report.js implements 7 chapters, Chapter 3 Ductility,
    KaTeX aligned multiline environments, clean verdict texts, and universal DCR."""
    report_js = (JS_DIR / "report" / "rc_beam_report.js").read_text(encoding="utf-8")

    # Item 1: Chapter 3 Ductility Limit & Min Rebar
    assert 'data-chapter-key="ductility"' in report_js
    assert "Ductility Limit & Minimum Reinforcement Check" in report_js
    assert "1.2 M_{cr}" in report_js
    assert "dcrMin" in report_js
    assert "dcrEps" in report_js

    # Item 3: KaTeX aligned environment across chapters
    aligned_count = report_js.count("\\begin{aligned}")
    assert aligned_count >= 5, f"Expected >= 5 aligned blocks, got {aligned_count}"
    assert "\\end{aligned}" in report_js

    # Item 5: Clean verdict and absence of messy legacy bracket tags
    assert "[최소철근량 부족]" not in report_js
    assert "[연성확보 불가]" not in report_js
    assert "[최대철근비 초과]" not in report_js
    assert "O.K" in report_js

    # Item 6: Universal DCR notation in report logic
    assert "dcrMin" in report_js
    assert "dcrEps" in report_js
    assert "dcrDefl" in report_js
    assert "dcrCrack" in report_js
    assert "governingDcr" in report_js


# ==============================================================================
# Test 3: Zero Load Dynamic Omission in Report (Item 7)
# ==============================================================================
def test_12_refinements_zero_load_report_omission():
    """Verify rc_beam_report.js dynamically omits detailed formulas for zero loads
    and renders concise engineering 1-line summary cards."""
    report_js = (JS_DIR / "report" / "rc_beam_report.js").read_text(encoding="utf-8")

    # Torsion zero omission
    assert "isZeroTorsion" in report_js
    assert "비틀림 설계 생략" in report_js or "설계 비틀림 모멘트 없음" in report_js

    # Flexure zero moment omission
    assert "강도 검토 생략" in report_js or "작용 부모멘트 없음" in report_js or "작용 정모멘트 없음" in report_js


# ==============================================================================
# Test 4: Form & UI 12-Point Spacing, Disabled Rows, Sticky Header, Canvas (Items 2, 9, 10, 11, 12)
# ==============================================================================
def test_12_refinements_ui_components_form_and_canvas():
    """Verify form_rc_beam.js, vector_rc_beam.js and style.css implement:
    - Arrangement type branching (Item 2)
    - Canvas nullish coalescing for torsion side bar (Item 9)
    - 12-point clear spacing engine & governing badge (Item 10)
    - Load table dynamic disabled & sync (Item 11)
    - Sticky floating header & 32px compact buttons (Item 12)"""
    form_js = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")
    vector_js = (JS_DIR / "visual" / "vector_rc_beam.js").read_text(encoding="utf-8")
    style_css = (CSS_DIR / "style.css").read_text(encoding="utf-8")

    # Item 2: Arrangement type branching
    assert "ONE_SECTION" in form_js
    assert "SYMMETRIC_ENDS" in form_js
    assert "THREE_STATIONS" in form_js

    # Item 9: Canvas nullish coalescing (0 count handled properly)
    assert "r.torsion_side_count ?? data.torsion_side_count ?? 0" in vector_js

    # Item 10: 12-point clear spacing engine
    assert "_calcAllClearSpacings" in form_js
    assert "beam-spacing-popover" in form_js
    assert "btn-toggle-spacing-popover" in form_js
    assert ".spacing-badge-governing" in style_css

    # Item 11: Dynamic disabled load table & symmetric sync
    assert "_updateLoadTableArrangeState" in form_js
    assert "row-ld-endi" in form_js
    assert "row-ld-endj" in form_js
    assert ".row-disabled-load" in style_css
    assert ".badge-load-sym" in style_css

    # Item 12: Sticky floating header & 32px compact engineering buttons
    assert "btn-action-compact" in form_js
    assert "btn-action-compact" in style_css
    assert "height: 32px" in style_css
    assert "form-sticky-header" in form_js or "beam-sticky-header" in form_js
