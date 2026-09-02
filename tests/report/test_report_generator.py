"""Tests for Report Generator and Base Report Template (Phase 09-1)."""

import pytest
from src.report.generator import (
    ReportGenerator,
    fmt_num,
    fmt_force,
    fmt_moment,
    fmt_stress,
    fmt_dcr,
    dcr_badge,
    katex_inline,
    katex_block,
)


def test_custom_filters():
    """Test custom formatting and badge filters."""
    assert fmt_num(1234.5678, 2) == "1,234.57"
    assert fmt_num(None) == "-"
    assert fmt_force(250.5) == "250.50 kN"
    assert fmt_moment(180.2) == "180.20 kN·m"
    assert fmt_stress(24.0) == "24.00 MPa"
    assert fmt_dcr(0.8567) == "0.857"
    
    # DCR badge checks
    assert "badge-pass" in dcr_badge(0.80)
    assert "badge-warn" in dcr_badge(1.03)
    assert "badge-fail" in dcr_badge(1.15)
    
    # LaTeX wrappers
    assert katex_inline("a+b") == "$a+b$"
    assert katex_block("c+d") == "$$c+d$$"


def test_report_generator_base_rendering():
    """Test rendering of standard calculation report via ReportGenerator."""
    gen = ReportGenerator()
    
    project_info = {
        "title": "테스트 오피스 빌딩 RC보 설계계산서",
        "code": "KDS 14 20 00",
        "date": "2026-09-02",
        "author": "김구조",
        "checker": "이검토",
    }
    member_info = {
        "id": "2B-101",
        "type": "RC 직사각형 보 (Beam)",
    }
    material_info = {
        "fck": 24.0,
        "fy": 400.0,
        "fys": 400.0,
    }
    section_info = {
        "b": 400.0,
        "h": 600.0,
        "d": 540.0,
    }
    loads_info = {
        "Mu": 210.0,
        "Vu": 150.0,
        "Pu": 0.0,
        "Tu": 15.0,
        "comb_name": "1.2D + 1.6L",
    }
    checks = [
        {
            "title": "휨모멘트 설계검토 (Flexural Strength)",
            "dcr": 0.807,
            "demand": "Mu = 210.00 kN·m",
            "capacity": "phi*Mn = 260.27 kN·m",
            "steps": [
                {"label": "기호식", "formula": r"$\phi M_n = \phi [A_s f_y (d - a/2)]$"},
                {"label": "대입식", "formula": r"$= 0.85 \times [1520 \times 400 \times (540 - 71.5/2)] \times 10^{-6}$"},
                {"label": "결과치", "formula": r"$= 260.27 \text{ kN}\cdot\text{m} \ge M_u = 210.0 \text{ kN}\cdot\text{m}$ (DCR = 0.807)"},
            ],
        },
        {
            "title": "전단강도 설계검토 (Shear Strength)",
            "dcr": 0.654,
            "demand": "Vu = 150.00 kN",
            "capacity": "phi*Vn = 229.35 kN",
            "steps": [
                {"label": "콘크리트 전단강도", "formula": r"$\phi V_c = 0.75 \times \frac{1}{6} \sqrt{f_{ck}} b_w d = 110.23 \text{ kN}$"},
                {"label": "스터럽 전단강도", "formula": r"$\phi V_s = 0.75 \times \frac{A_v f_{yt} d}{s} = 119.12 \text{ kN}$"},
                {"label": "설계 전단강도", "formula": r"$\phi V_n = \phi V_c + \phi V_s = 229.35 \text{ kN} \ge V_u = 150.0 \text{ kN}$ (DCR = 0.654)"},
            ],
        },
    ]

    html = gen.render_generic_report(
        project_info=project_info,
        member_info=member_info,
        material_info=material_info,
        section_info=section_info,
        loads_info=loads_info,
        checks=checks,
        summary_dcr=0.807,
        is_safe=True,
    )

    # Verify HTML contents
    assert "테스트 오피스 빌딩 RC보 설계계산서" in html
    assert "2B-101" in html
    assert "KDS 14 20 00" in html
    assert "ALL SAFE" in html
    assert "0.807" in html
    assert "katex.min.js" in html
    assert "@page" in html
