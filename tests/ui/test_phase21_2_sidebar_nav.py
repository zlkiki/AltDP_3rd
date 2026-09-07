"""Tests for Phase 21-2: Smart Hierarchical Module Navigator Sidebar & Favorites System.

Validates:
1. 8 Category Pills in index.html (all, fav, rc, steel, src_pc, alu, rfm, found_special).
2. sidebar_nav.js static serving, SidebarNav class, and key methods.
3. tree_menu.css 8-tab styles, 2-stage DCR text, pin button, and auto-hide transition.
4. Pin button (#btn-pin-sidebar) and tree level buttons (#btn-tree-lv1, #btn-tree-lv2, #btn-tree-lv3).
5. Quick search input (#quick-search) and shortcut integration.
"""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_8_category_pills_present():
    """Verify presence of all 8 category pills tabs in index.html as per Req 21-2."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # 8 Category Pills
    assert 'id="sidebar-cat-pills"' in html
    assert 'data-cat="all"' in html
    assert 'data-cat="fav"' in html
    assert 'data-cat="rc"' in html
    assert 'data-cat="steel"' in html
    assert 'data-cat="src_pc"' in html
    assert 'data-cat="alu"' in html
    assert 'data-cat="rfm"' in html
    assert 'data-cat="found_special"' in html

    # Pin button and tree levels
    assert 'id="btn-pin-sidebar"' in html
    assert 'id="btn-tree-lv1"' in html
    assert 'id="btn-tree-lv2"' in html
    assert 'id="btn-tree-lv3"' in html
    assert 'id="quick-search"' in html

    # Script tag for sidebar_nav.js
    assert "/static/js/components/sidebar_nav.js" in html


def test_sidebar_nav_js_serving_and_specifications():
    """Verify sidebar_nav.js serving and required functionality."""
    res = client.get("/static/js/components/sidebar_nav.js")
    assert res.status_code == 200
    js = res.text

    # Class and core methods
    assert "class SidebarNav" in js
    assert "window.SidebarNav = new SidebarNav();" in js
    assert "AltDP_favorites" in js
    assert "matchesCategory" in js
    assert "toggleFavorite" in js
    assert "setTreeLevel" in js
    assert "scrollToReportNG" in js
    assert "autoHideTimer" in js
    assert "togglePin" in js


def test_tree_menu_css_styles():
    """Verify tree_menu.css contains styles for 8 pills, favorites, DCR text, and auto-hide."""
    res = client.get("/static/css/tree_menu.css")
    assert res.status_code == 200
    css = res.text

    assert ".sidebar-category-pills" in css
    assert ".pill-btn" in css
    assert ".pinned-section" in css
    assert ".fav-star-btn" in css
    assert ".tree-dcr-text" in css
    assert ".tree-dcr-text.pass" in css
    assert ".tree-dcr-text.fail" in css
    assert ".sidebar.auto-hidden" in css
    assert ".pin-header-btn.pinned" in css
    assert ".pin-header-btn.unpinned" in css


def test_app_js_sidebar_nav_integration():
    """Verify app.js integrates SidebarNav properly."""
    res = client.get("/static/js/app.js")
    assert res.status_code == 200
    js = res.text

    assert "window.SidebarNav" in js
    assert "window.selectMemberInModule" in js
    assert "window.selectModule" in js
