"""
Tests for Phase 21-5: Original App 1:1 KDS Standard Structural Calculation Report Pane 4 Engine.
Conforms to Requirements 21-5 & DOCS 07 & DOCS 14 Specifications.
"""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_index_html_pane4_and_report_toolbar_elements():
    """Verify index.html contains #report-control-toolbar with radios, checkboxes, and actions."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # 1. Pane 4 and Toolbar Container
    assert 'id="right-pane"' in html or 'pane-right-report' in html
    assert 'id="report-control-toolbar"' in html
    assert 'class="report-toolbar"' in html

    # 2. Report Mode Radios (Detail / Summary)
    assert 'name="report-mode"' in html
    assert 'value="detail"' in html
    assert 'value="summary"' in html
    assert "상세 보고서 (Detail)" in html
    assert "요약 보고서 (Summary)" in html

    # 3. Output Option Checkboxes
    assert 'id="chk-report-include-input"' in html
    assert "사용자 입력 데이터 상세 포함" in html
    assert 'id="chk-report-include-graphics"' in html
    assert "그래픽 임베딩" in html

    # 4. Custom Header & Action Buttons
    assert 'id="btn-report-header-settings"' in html
    assert 'id="btn-report-print"' in html
    assert 'id="btn-report-pdf"' in html
    assert 'id="btn-report-excel"' in html

    # 5. Script Inclusion
    assert "/static/js/core/report_engine.js" in html


def test_report_engine_js_specifications():
    """Verify report_engine.js implements ReportEngine singleton with 8-step KaTeX and OK/NG verdicts."""
    res = client.get("/static/js/core/report_engine.js")
    assert res.status_code == 200
    js = res.text

    # 1. Class and Singleton
    assert "class ReportEngine" in js
    assert "window.ReportEngine = new ReportEngine()" in js

    # 2. State and Mode Methods
    assert "setReportMode" in js
    assert "setIncludeInput" in js
    assert "setIncludeGraphics" in js
    assert "updateHeaderConfig" in js

    # 3. KaTeX 8-Step Formula Pipeline
    assert "_renderDetailFormulas" in js
    assert "등가 직사각형 응력블록 깊이" in js
    assert "KDS 14 20 20" in js
    assert "중립축 깊이" in js
    assert "강도감소계수" in js
    assert "휨모멘트 안전성 판정" in js
    assert "콘크리트 분담 전단강도" in js
    assert "전단철근 분담 전단강도" in js
    assert "KDS 14 20 22" in js

    # 4. Original App Verdict Badges (  →  O.K /   →  N.G)
    assert "  →  O.K" in js
    assert "  →  N.G" in js
    assert "verdict-ok" in js
    assert "verdict-ng" in js

    # 5. Header / Approval Configuration (IDD_REPORT_HEADER_DLG)
    assert "IDD_REPORT_HEADER_DLG" in js
    assert "openHeaderDialog" in js
    assert "headerConfig" in js


def test_report_css_and_print_css_specifications():
    """Verify report.css and print.css provide constant pure white A4 and print isolation."""
    # 1. report.css
    res_css = client.get("/static/css/report.css")
    assert res_css.status_code == 200
    css = res_css.text

    assert "#report-control-toolbar" in css or ".report-toolbar" in css
    assert "pure-white-sheet" in css
    assert "#ffffff !important" in css  # Constant pure white A4 guarantee
    assert ".report-print-banner" in css
    assert ".header-approval-table" in css
    assert ".katex-formula-step" in css
    assert ".verdict-ok" in css
    assert ".verdict-ng" in css
    assert ".user-input-section.hidden" in css

    # 2. print.css
    res_print = client.get("/static/css/print.css")
    assert res_print.status_code == 200
    pcss = res_print.text

    assert "@media print" in pcss
    assert "#report-control-toolbar" in pcss or ".report-toolbar" in pcss
    assert "display: none !important" in pcss


def test_common_dialogs_report_header_dialog():
    """Verify common_dialogs.js implements openReportHeaderDialog modal."""
    res = client.get("/static/js/core/common_dialogs.js")
    assert res.status_code == 200
    js = res.text

    assert "openReportHeaderDialog" in js
    assert "IDD_REPORT_HEADER_DLG" in js
    assert "dlg-hdr-project" in js
    assert "dlg-hdr-company" in js
    assert "dlg-hdr-tag" in js
    assert "dlg-hdr-engineer" in js
    assert "dlg-hdr-checker" in js
    assert "dlg-hdr-approver" in js
