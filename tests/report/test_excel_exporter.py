"""Tests for Multi-sheet Excel Calculation Report Exporter (Phase 09-3)."""

import io
import openpyxl
import pytest
from src.report.excel_exporter import ExcelReportExporter


def test_excel_exporter_workbook_structure():
    """Test multi-sheet Excel generation and cell values."""
    exporter = ExcelReportExporter()

    project_info = {
        "title": "엑셀 계산서 테스트 프로젝트",
        "code": "KDS 14 20 00",
        "author": "홍길동",
        "checker": "이순신",
        "date": "2026-09-02",
    }
    member_info = {
        "id": "2B-101",
        "type": "RC Beam",
    }
    material_info = {
        "fck (Concrete)": "24.0 MPa",
        "fy (Main Rebar)": "400.0 MPa",
        "fys (Stirrups)": "400.0 MPa",
    }
    section_info = {
        "Width (b)": "400 mm",
        "Height (h)": "600 mm",
        "Effective Depth (d)": "540 mm",
    }
    loads_info = {
        "Mu (Flexure)": "210.0 kN·m",
        "Vu (Shear)": "150.0 kN",
        "Load Combination": "1.2D + 1.6L",
    }
    checks = [
        {"title": "휨모멘트 검토", "demand": "210.0 kN·m", "capacity": "260.27 kN·m", "dcr": 0.807},
        {"title": "전단강도 검토", "demand": "150.0 kN", "capacity": "229.35 kN", "dcr": 0.654},
    ]

    xlsx_bytes = exporter.export_workbook_bytes(
        project_info=project_info,
        member_info=member_info,
        material_info=material_info,
        section_info=section_info,
        loads_info=loads_info,
        checks=checks,
        summary_dcr=0.807,
        is_safe=True,
    )

    assert len(xlsx_bytes) > 1000

    # Read workbook back from bytes
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    sheet_names = wb.sheetnames
    assert "Summary & Overview" in sheet_names
    assert "Material & Section" in sheet_names
    assert "Detailed Checks" in sheet_names
    assert "Design Loads" in sheet_names

    ws_sum = wb["Summary & Overview"]
    assert "2B-101" in str(ws_sum["C4"].value)
    assert "0.807" in str(ws_sum["C9"].value)

    ws_chk = wb["Detailed Checks"]
    assert "휨모멘트 검토" in str(ws_chk["C5"].value)
    assert "OK" in str(ws_chk["G5"].value)
