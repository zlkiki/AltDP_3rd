"""
Tests for Requirement 22-5-2: Phase V1-01 Step 5-2 RC Beam UI Patches
- 12-point clear spacing full check & popover
- Load table dynamic disabled & symmetric replication
- Sticky floating header & 32px compact engineering action buttons
- Canvas torsion side bar 0 count nullish coalescing fix
"""

import pytest
from pathlib import Path

WEB_STATIC_DIR = Path("src/web/static")
JS_DIR = WEB_STATIC_DIR / "js"
CSS_DIR = WEB_STATIC_DIR / "css"


def test_vector_rc_beam_torsion_nullish_coalescing():
    """Verify vector_rc_beam.js uses nullish coalescing (?? 0) for torsionSideCount."""
    vector_js = (JS_DIR / "visual" / "vector_rc_beam.js").read_text(encoding="utf-8")
    assert "r.torsion_side_count ?? data.torsion_side_count ?? 0" in vector_js, \
        "vector_rc_beam.js must use nullish coalescing ?? 0 so that 0 count is not overridden by default 2"


def test_form_rc_beam_12point_clear_spacing_engine():
    """Verify form_rc_beam.js implements 12-point clear spacing full calculation & popover."""
    form_js = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")
    assert "_calcAllClearSpacings" in form_js, "form_rc_beam.js must have _calcAllClearSpacings method"
    assert "top_layer1" in form_js and "top_layer2" in form_js
    assert "bot_layer1" in form_js and "bot_layer2" in form_js
    assert "end_i" in form_js and "center_m" in form_js and "end_j" in form_js
    assert "beam-spacing-popover" in form_js, "Popover container must be present in form_rc_beam.js"
    assert "btn-toggle-spacing-popover" in form_js, "Popover toggle button must be present"


def test_form_rc_beam_load_table_arrange_state():
    """Verify form_rc_beam.js dynamically manages load table disabled and symmetric sync."""
    form_js = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")
    assert "_updateLoadTableArrangeState" in form_js, "form_rc_beam.js must have _updateLoadTableArrangeState method"
    assert "row-ld-endi" in form_js, "Load table must have row-ld-endi ID"
    assert "row-ld-cent" in form_js, "Load table must have row-ld-cent ID"
    assert "row-ld-endj" in form_js, "Load table must have row-ld-endj ID"
    assert "tag-ld-endi-sym" in form_js and "tag-ld-endj-sym" in form_js
    assert "SYMMETRIC_ENDS" in form_js


def test_form_rc_beam_sticky_header_and_compact_buttons():
    """Verify form_rc_beam.js wraps toolbar and tabs in sticky header and applies 32px compact buttons."""
    form_js = (JS_DIR / "components" / "form_rc_beam.js").read_text(encoding="utf-8")
    assert "form-sticky-header" in form_js or "beam-sticky-header" in form_js, \
        "form_rc_beam.js must have sticky header container"
    assert "btn-action-compact" in form_js, "Action buttons must have btn-action-compact class"
    assert "btn-apply-action" in form_js
    assert "btn-check-action" in form_js
    assert "btn-design-action" in form_js


def test_style_css_requirement_22_5_2_classes():
    """Verify style.css contains all required classes for Req 22-5-2."""
    style_css = (CSS_DIR / "style.css").read_text(encoding="utf-8")
    assert ".form-sticky-header" in style_css or ".beam-sticky-header" in style_css
    assert ".btn-action-compact" in style_css
    assert "height: 32px" in style_css
    assert ".spacing-badge-governing" in style_css
    assert ".spacing-popover" in style_css
    assert ".row-disabled-load" in style_css
    assert ".badge-load-sym" in style_css
