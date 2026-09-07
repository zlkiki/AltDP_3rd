"""Tests for Phase 21-1: DOCS 07 4-Pane Workspace Layout & 4 Independent Resizers Engine.

Validates:
1. 4-Pane Workspace DOM hierarchy in index.html (app-container, top-toolbar, main-workspace, 4 panes).
2. 4 Independent Resizers DOM definitions (resizer-sidebar-h, resizer-left-h, resizer-left-v, resizer-main-h).
3. 4-Pane CSS Grid/Flex tokens and pointer-lock resizing styles in layout.css.
4. layout_resizer.js engine serving, standard bounding constraints, and AltDP_layout_ratios persistence.
5. One-click layout reset and save buttons in top toolbar.
"""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_4pane_workspace_hierarchy():
    """Verify 4-Pane workspace DOM hierarchy in index.html."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Top Toolbar and Action buttons
    assert 'id="app-container"' in html
    assert 'id="top-toolbar"' in html
    assert 'id="btn-save-layout"' in html
    assert 'id="btn-reset-layout"' in html

    # Main 4-Pane Workspace container
    assert 'id="main-workspace"' in html
    assert "workspace-4pane" in html

    # 4 Main Panes
    assert 'id="sidebar-nav"' in html
    assert "pane-sidebar" in html

    assert 'id="left-sub-pane"' in html
    assert "pane-left-sub" in html

    assert 'id="pane-member-list"' in html
    assert "subpane-member-list" in html

    assert 'id="pane-input-form"' in html
    assert "subpane-input-form" in html

    assert 'id="center-pane"' in html
    assert "pane-center-graphic" in html

    assert 'id="right-pane"' in html
    assert "pane-right-report" in html


def test_index_html_4_independent_resizers_present():
    """Verify presence of all 4 independent resizers with proper data-direction attributes."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # 1. Sidebar-Horizontal
    assert 'id="resizer-sidebar-h"' in html
    # 2. Left-Vertical
    assert 'id="resizer-left-v"' in html
    # 3. Left-Horizontal
    assert 'id="resizer-left-h"' in html
    # 4. Main-Horizontal
    assert 'id="resizer-main-h"' in html


def test_layout_css_4pane_styles():
    """Verify layout.css defines 4-pane flex styles, resizer handles, and pointerlock guards."""
    res = client.get("/static/css/layout.css")
    assert res.status_code == 200
    css = res.text

    assert ".workspace-4pane" in css
    assert ".pane-sidebar" in css
    assert ".pane-left-sub" in css
    assert ".subpane-member-list" in css
    assert ".subpane-input-form" in css
    assert ".pane-center-graphic" in css
    assert ".pane-right-report" in css

    # Resizers and global dragging guards
    assert ".resizer-h" in css
    assert ".resizer-v" in css
    assert "cursor: col-resize" in css
    assert "cursor: row-resize" in css
    assert "body.resizing-col" in css
    assert "body.resizing-row" in css
    assert "user-select: none" in css


def test_layout_resizer_js_serving_and_specifications():
    """Verify layout_resizer.js serves with standard bounding limits and persistence logic."""
    res = client.get("/static/js/components/layout_resizer.js")
    assert res.status_code == 200
    js = res.text

    # Bounding constraints and defaults per Requirement 21-1 Sec 2.2
    assert "sidebarWidth: 280" in js
    assert "leftSubWidth: 380" in js
    assert "memberHeight: 160" in js
    assert "centerRightRatio: 0.5" in js

    # Bounding checks
    assert "480" in js  # Sidebar max width
    assert "200" in js  # Sidebar min width
    assert "400" in js  # Member list max height
    assert "80" in js   # Member list min height

    # Storage Key
    assert "AltDP_layout_ratios" in js

    # Event handlers & Controls
    assert "btn-reset-layout" in js
    assert "btn-save-layout" in js
    assert "btn-toggle-sidebar" in js
    assert "pointermove" in js
    assert "pointerup" in js
    assert "window.LayoutResizer" in js
