"""Comprehensive tests for Member Calculation Reports and SVG graphics (Phase 09-2)."""

import pytest
from src.report.generator import ReportGenerator
from src.report.svg_drawer import (
    draw_rc_beam_section_svg,
    draw_rc_column_section_svg,
    draw_steel_h_section_svg,
    draw_pm_diagram_svg,
)


def test_svg_drawing_functions():
    """Test pure Python SVG drawing functions."""
    # 1. RC Beam SVG
    svg_beam = draw_rc_beam_section_svg(b=400, h=600, top_rebars=3, bot_rebars=4)
    assert "<svg" in svg_beam
    assert "b=400" in svg_beam
    assert "h=600" in svg_beam
    assert "circle" in svg_beam  # rebars

    # 2. RC Column SVG
    svg_col = draw_rc_column_section_svg(b=600, h=600, nx=4, ny=4)
    assert "<svg" in svg_col
    assert "600×600" in svg_col

    # 3. Steel H-Section SVG
    svg_steel = draw_steel_h_section_svg(h=400, b=200, tw=8, tf=13)
    assert "<svg" in svg_steel
    assert "polygon" in svg_steel
    assert "H=400" in svg_steel

    # 4. P-M Curve SVG
    nom_pts = [(0, 4000), (300, 3000), (450, 1500), (300, 0), (0, -800)]
    des_pts = [(0, 3400), (255, 2550), (382, 1275), (255, 0), (0, -680)]
    svg_pm = draw_pm_diagram_svg(nom_pts, des_pts, action_point=(2000, 200))
    assert "<svg" in svg_pm
    assert "polyline" in svg_pm
    assert "Bending Moment" in svg_pm


def test_rc_beam_report_rendering():
    """Test RC Beam detailed calculation report rendering."""
    gen = ReportGenerator()
    svg = draw_rc_beam_section_svg(b=400, h=600)

    html = gen.render_rc_beam(
        project_info={"title": "RC보 계산서 테스트", "date": "2026-09-02"},
        member_info={"id": "2B-101", "type": "RC 직사각형 보"},
        material_info={"fck": 24.0, "fy": 400.0, "fys": 400.0},
        section_info={"b": 400.0, "h": 600.0, "d": 540.0, "dc": 40.0},
        loads_info={"Mu": 210.0, "Vu": 150.0, "comb_name": "1.2D + 1.6L"},
        flexure_check={"As": 1520.0, "a": 71.5, "phi": 0.85, "phi_Mn": 260.27, "dcr": 0.807},
        shear_check={"Av": 142.6, "s": 150.0, "phi_Vc": 110.23, "phi_Vs": 119.12, "phi_Vn": 229.35, "dcr": 0.654},
        service_check={"Ie": 52000.0, "deflection": 12.4, "allow_deflection": 20.0, "deflection_dcr": 0.62, "crack_width": 0.18, "allow_crack_width": 0.3, "crack_dcr": 0.60},
        summary_dcr=0.807,
        is_safe=True,
        svg_diagram=svg,
    )

    assert "RC보 계산서 테스트" in html
    assert "2B-101" in html
    assert "260.27" in html
    assert "229.35" in html
    assert "<svg" in html


def test_rc_column_report_rendering():
    """Test RC Column detailed report with P-M diagram."""
    gen = ReportGenerator()
    svg_col = draw_rc_column_section_svg(600, 600)
    svg_pm = draw_pm_diagram_svg([(0, 4000), (450, 1500), (0, -800)], [(0, 3400), (380, 1275), (0, -680)], (1500, 250))

    html = gen.render_rc_column(
        project_info={"title": "RC기둥 계산서 테스트"},
        member_info={"id": "C-101"},
        material_info={"fck": 30.0, "fy": 400.0, "fys": 400.0},
        section_info={"b": 600.0, "h": 600.0, "Lu": 3600.0, "Ast": 6079.0},
        loads_info={"Pu": 1500.0, "Mux": 250.0, "comb_name": "1.2D + 1.6L"},
        pm_check={"phi_Pn_max": 3800.0, "phi_Mnx": 380.0, "Mcx": 262.5, "dcr": 0.691, "delta_ns_x": 1.05},
        summary_dcr=0.691,
        is_safe=True,
        svg_diagram=svg_col,
        pm_chart_svg=svg_pm,
    )

    assert "C-101" in html
    assert "P-M 축휨 상관비 검토" in html
    assert "0.691" in html


def test_other_member_reports():
    """Test Wall/Slab, Foundation, Steel Member, and Connection reports."""
    gen = ReportGenerator()

    # Steel Member
    html_steel = gen.render_steel_member(
        project_info={"title": "철골보 계산서"},
        member_info={"id": "SB-101"},
        material_info={"steel_grade": "SM355", "Fy": 355.0, "Fu": 490.0},
        section_info={"name": "H-400x200x8x13", "H": 400, "B": 200, "tw": 8, "tf": 13, "A": 8410, "Zx": 1340},
        loads_info={"Mu": 280.0, "Vu": 140.0},
        checks=[{"title": "휨강도 검토", "demand": "Mu=280", "capacity": "phi*Mn=428", "dcr": 0.654, "steps": []}],
        summary_dcr=0.654,
        is_safe=True,
        svg_diagram=draw_steel_h_section_svg(400, 200, 8, 13),
    )
    assert "SB-101" in html_steel
    assert "SM355" in html_steel

    # Steel Connection
    html_conn = gen.render_steel_connection(
        project_info={"title": "접합부 계산서"},
        member_info={"id": "CONN-101"},
        material_info={"bolt_grade": "F10T M22"},
        section_info={"tp": 16.0},
        loads_info={"Vu": 180.0, "Tu": 0.0},
        checks=[{"title": "볼트 전단강도", "demand": "Vu=180", "capacity": "phi*Rn=280", "dcr": 0.643, "steps": []}],
        summary_dcr=0.643,
        is_safe=True,
    )
    assert "CONN-101" in html_conn
    assert "F10T M22" in html_conn
