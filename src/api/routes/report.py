"""FastAPI REST Router for Structural Calculation Reports.

Provides endpoints for HTML calculation preview, A4 printing,
Excel spreadsheet download, and PDF document generation.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.report.generator import ReportGenerator
from src.report.excel_exporter import ExcelReportExporter
from src.report.pdf_exporter import PDFReportExporter
from src.report.svg_drawer import (
    draw_rc_beam_section_svg,
    draw_rc_column_section_svg,
    draw_steel_h_section_svg,
    draw_pm_diagram_svg,
)

router = APIRouter(prefix="/api/v1/report", tags=["Calculation Report"])

report_gen = ReportGenerator()
excel_exp = ExcelReportExporter()
pdf_exp = PDFReportExporter()


class ReportRequest(BaseModel):
    """General calculation report generation request payload."""
    member_type: str = Field(default="rc_beam", description="Member type: rc_beam, rc_column, rc_wall_slab, rc_foundation, steel_member, steel_connection")
    project_info: Dict[str, Any] = Field(default_factory=lambda: {"title": "AltDP_3rd 구조계산서", "code": "KDS 14 20 00", "date": "2026-09-02", "author": "AltDP Engineer"})
    member_info: Dict[str, Any] = Field(default_factory=lambda: {"id": "M-101", "type": "RC 부재"})
    material_info: Dict[str, Any] = Field(default_factory=lambda: {"fck": 24.0, "fy": 400.0})
    section_info: Dict[str, Any] = Field(default_factory=lambda: {"b": 400.0, "h": 600.0, "d": 540.0})
    loads_info: Dict[str, Any] = Field(default_factory=lambda: {"Mu": 210.0, "Vu": 150.0, "comb_name": "1.2D + 1.6L"})
    checks: List[Dict[str, Any]] = Field(default_factory=list)
    summary_dcr: float = Field(default=0.807)
    is_safe: bool = Field(default=True)
    custom_context: Optional[Dict[str, Any]] = None


def _render_report_html(req: ReportRequest) -> str:
    """Internal helper to render appropriate member HTML report."""
    mtype = req.member_type.lower()
    
    if mtype == "rc_beam":
        svg = draw_rc_beam_section_svg(
            b=float(req.section_info.get("b", 400)),
            h=float(req.section_info.get("h", 600)),
        )
        flex_chk = req.custom_context.get("flexure_check") if req.custom_context else {
            "As": 1520.0, "a": 71.5, "phi": 0.85, "phi_Mn": 260.27, "dcr": 0.807
        }
        shear_chk = req.custom_context.get("shear_check") if req.custom_context else {
            "Av": 142.6, "s": 150.0, "phi_Vc": 110.23, "phi_Vs": 119.12, "phi_Vn": 229.35, "dcr": 0.654
        }
        serv_chk = req.custom_context.get("service_check") if req.custom_context else {
            "Ie": 52000.0, "deflection": 12.4, "allow_deflection": 20.0, "deflection_dcr": 0.62, "crack_width": 0.18, "crack_dcr": 0.60
        }
        return report_gen.render_rc_beam(
            project_info=req.project_info,
            member_info=req.member_info,
            material_info=req.material_info,
            section_info=req.section_info,
            loads_info=req.loads_info,
            flexure_check=flex_chk,
            shear_check=shear_chk,
            service_check=serv_chk,
            summary_dcr=req.summary_dcr,
            is_safe=req.is_safe,
            svg_diagram=svg,
        )
    elif mtype == "rc_column":
        svg_col = draw_rc_column_section_svg(
            b=float(req.section_info.get("b", 600)),
            h=float(req.section_info.get("h", 600)),
        )
        svg_pm = draw_pm_diagram_svg(
            [(0, 4000), (450, 1500), (0, -800)],
            [(0, 3400), (380, 1275), (0, -680)],
            (float(req.loads_info.get("Pu", 1500)), float(req.loads_info.get("Mu", req.loads_info.get("Mux", 250)))),
        )
        pm_chk = req.custom_context.get("pm_check") if req.custom_context else {
            "phi_Pn_max": 3800.0, "phi_Mnx": 380.0, "Mcx": 262.5, "dcr": req.summary_dcr, "delta_ns_x": 1.05
        }
        return report_gen.render_rc_column(
            project_info=req.project_info,
            member_info=req.member_info,
            material_info=req.material_info,
            section_info=req.section_info,
            loads_info=req.loads_info,
            pm_check=pm_chk,
            summary_dcr=req.summary_dcr,
            is_safe=req.is_safe,
            svg_diagram=svg_col,
            pm_chart_svg=svg_pm,
        )
    elif mtype == "steel_member":
        svg_steel = draw_steel_h_section_svg(
            h=float(req.section_info.get("H", 400)),
            b=float(req.section_info.get("B", 200)),
            tw=float(req.section_info.get("tw", 8)),
            tf=float(req.section_info.get("tf", 13)),
        )
        return report_gen.render_steel_member(
            project_info=req.project_info,
            member_info=req.member_info,
            material_info=req.material_info,
            section_info=req.section_info,
            loads_info=req.loads_info,
            checks=req.checks,
            summary_dcr=req.summary_dcr,
            is_safe=req.is_safe,
            svg_diagram=svg_steel,
        )
    else:
        return report_gen.render_generic_report(
            project_info=req.project_info,
            member_info=req.member_info,
            material_info=req.material_info,
            section_info=req.section_info,
            loads_info=req.loads_info,
            checks=req.checks,
            summary_dcr=req.summary_dcr,
            is_safe=req.is_safe,
        )


@router.post("/html", response_class=HTMLResponse)
async def generate_report_html(req: ReportRequest):
    """Generate and return full A4 calculation report in HTML."""
    try:
        html = _render_report_html(req)
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report rendering error: {str(e)}")


@router.post("/excel")
async def generate_report_excel(req: ReportRequest):
    """Generate and export calculation report as multi-sheet Excel file."""
    try:
        checks = req.checks or [
            {"title": "주요 한계상태 검토", "demand": "Mu", "capacity": "phi*Mn", "dcr": req.summary_dcr}
        ]
        excel_bytes = excel_exp.export_workbook_bytes(
            project_info=req.project_info,
            member_info=req.member_info,
            material_info=req.material_info,
            section_info=req.section_info,
            loads_info=req.loads_info,
            checks=checks,
            summary_dcr=req.summary_dcr,
            is_safe=req.is_safe,
        )
        filename = f"Calculation_Report_{req.member_info.get('id', 'MEMBER')}.xlsx"
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation error: {str(e)}")


@router.post("/pdf")
async def generate_report_pdf(req: ReportRequest):
    """Generate and export calculation report as PDF file."""
    try:
        html = _render_report_html(req)
        pdf_bytes = pdf_exp.export_pdf_bytes(html)
        media_type = "application/pdf" if pdf_exp.is_weasyprint_available else "text/html; charset=utf-8"
        ext = "pdf" if pdf_exp.is_weasyprint_available else "html"
        filename = f"Calculation_Report_{req.member_info.get('id', 'MEMBER')}.{ext}"
        return Response(
            content=pdf_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@router.get("/sample/{member_type}", response_class=HTMLResponse)
async def sample_report(member_type: str = "rc_beam"):
    """Quick preview sample calculation report for specific member type."""
    sample_req = ReportRequest(
        member_type=member_type,
        project_info={"title": f"AltDP_3rd {member_type.upper()} 표준 계산서", "code": "KDS 14 20 00 / 14 31 00"},
        member_info={"id": f"SMPL-{member_type.upper()}-1", "type": member_type},
        summary_dcr=0.785,
        is_safe=True,
    )
    html = _render_report_html(sample_req)
    return HTMLResponse(content=html, status_code=200)
