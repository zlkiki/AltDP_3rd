"""Tests for KDS 3 Report Modes (Summary, Detail, Input Data) and Pipeline.

Conforms to Requirement 15-1.
"""

import pytest
from src.report.generator import ReportGenerator
from src.report.options import ReportOptions

gen = ReportGenerator()

SAMPLE_CONTEXT = {
    "project": {"name": "Test Building", "code": "KDS 14 20 00", "date": "2026-09-03"},
    "member": {"name": "B1", "type": "RC Beam"},
    "material": {"fck": 27.0, "fy": 400.0},
    "section": {"b": 400.0, "h": 600.0, "rebar": "4-D25", "cover": 40.0},
    "loads": {"Mu": 180.0, "Vu": 140.0},
    "checks": [
        {"title": "휨모멘트 (Flexure)", "demand": 180.0, "capacity": 236.8, "dcr": 0.76, "code_clause": "KDS 14 20 20"},
        {"title": "전단력 (Shear)", "demand": 140.0, "capacity": 220.0, "dcr": 0.636, "code_clause": "KDS 14 20 22"},
    ],
    "summary_dcr": 0.760,
    "is_safe": True,
}


def test_summary_report_mode():
    """Verify that summary report renders compact layout with key limit states."""
    opts = ReportOptions(report_mode="summary")
    html = gen.render_summary_report(SAMPLE_CONTEXT, opts)

    assert "KDS 구조계산서 요약" in html
    assert "설계 기본 제원" in html
    assert "0.760" in html
    assert "종합 판정: KDS 기준 구조 안전성 만족" in html


def test_detail_report_mode():
    """Verify that detail report renders step-by-step formula derivations."""
    opts = ReportOptions(report_mode="detail")
    html = gen.render_detail_report(SAMPLE_CONTEXT, opts)

    assert "KDS 표준 구조계산서" in html
    assert "단계별 상세 수식 전개 과정" in html
    assert "등가 직사각형 응력블록 깊이" in html
    assert "콘크리트 부담 전단강도" in html
    assert "종합 한계상태 검토표" in html


def test_input_data_report_mode():
    """Verify that input data report renders raw variables and load combinations."""
    opts = ReportOptions(report_mode="input_data")
    html = gen.render_input_data_report(SAMPLE_CONTEXT, opts)

    assert "사용자 입력 원시 데이터 시트" in html
    assert "단면 형상 및 배근 입력 데이터" in html
    assert "설계 하중조합" in html
    assert "400" in html
    assert "600" in html


def test_render_with_options_dispatch():
    """Verify dynamic dispatch based on report_mode."""
    for mode, expected in [
        ("summary", "KDS 구조계산서 요약"),
        ("detail", "KDS 표준 구조계산서"),
        ("input_data", "사용자 입력 원시 데이터 시트"),
    ]:
        opts = ReportOptions(report_mode=mode)
        html = gen.render_with_options(SAMPLE_CONTEXT, opts)
        assert expected in html
