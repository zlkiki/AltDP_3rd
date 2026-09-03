"""FastAPI Routes for Quantity Takeoff and CAD DXF Exports (Phase 17-2)."""

from typing import List, Optional
from io import BytesIO
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse

from src.engine.project.quantity_engine import (
    QuantityEngine,
    MemberQuantityInput,
    ProjectQuantitySummary,
)
from src.report.excel_quantity_exporter import ExcelQuantityExporter
from src.report.cad_exporter import (
    CADExporter,
    BeamSectionCADInput,
    ColumnSectionCADInput,
    RebarDetail,
)
from src.report.cad_schedule import CADScheduleTable


router = APIRouter(prefix="/api/v1/project", tags=["Quantity Takeoff & CAD"])

# In-memory store for project quantities
_CURRENT_QUANTITY_SUMMARY: Optional[ProjectQuantitySummary] = None


@router.post("/quantity/calculate", response_model=ProjectQuantitySummary)
def calculate_quantities(members: List[MemberQuantityInput]):
    """Calculate exact concrete volume, formwork, and rebar tonnage per KDS standards."""
    global _CURRENT_QUANTITY_SUMMARY
    if not members:
        raise HTTPException(status_code=400, detail="Member list cannot be empty.")
    
    summary = QuantityEngine.aggregate_project_quantities(members)
    _CURRENT_QUANTITY_SUMMARY = summary
    return summary


@router.get("/quantity/export-excel")
def export_quantity_excel():
    """Download multi-sheet Excel (.xlsx) file containing BOQ summaries and breakdowns."""
    global _CURRENT_QUANTITY_SUMMARY
    if _CURRENT_QUANTITY_SUMMARY is None:
        # Generate default sample summary if none calculated yet
        sample_members = [
            MemberQuantityInput(member_id=1, story="2F", member_type="BEAM", b=400.0, h=600.0, length=6000.0),
            MemberQuantityInput(member_id=2, story="1F", member_type="COLUMN", b=600.0, h=600.0, length=3500.0),
        ]
        _CURRENT_QUANTITY_SUMMARY = QuantityEngine.aggregate_project_quantities(sample_members)

    stream = ExcelQuantityExporter.export_to_bytes(_CURRENT_QUANTITY_SUMMARY)
    headers = {
        "Content-Disposition": "attachment; filename=Project_Quantity_Summary.xlsx"
    }
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


@router.post("/cad/export-dxf")
def export_cad_dxf(
    member_type: str = "BEAM",
    name: str = "B1",
    b: float = 400.0,
    h: float = 600.0
):
    """Generate and download 2D CAD reinforcement detail (.dxf) file."""
    doc = CADExporter.create_document()

    if member_type.upper() == "COLUMN":
        col_inp = ColumnSectionCADInput(name=name, b=b, h=h)
        CADExporter.draw_rc_column_section(doc, col_inp, origin=(0.0, 0.0))
    else:
        beam_inp = BeamSectionCADInput(
            name=name,
            b=b,
            h=h,
            top_rebars=[RebarDetail(bar_size="D19", count=3, diameter_mm=19.1)],
            bot_rebars=[RebarDetail(bar_size="D22", count=4, diameter_mm=22.2)]
        )
        CADExporter.draw_rc_beam_section(doc, beam_inp, origin=(0.0, 0.0))

    # Add sample schedule table alongside section
    CADScheduleTable.draw_sample_beam_schedule(doc, origin=(b + 400.0, h + 200.0))

    from io import StringIO
    text_stream = StringIO()
    doc.write(text_stream)
    stream = BytesIO(text_stream.getvalue().encode("utf-8"))

    headers = {
        "Content-Disposition": f"attachment; filename={name}_Rebar_Detail.dxf"
    }
    return StreamingResponse(
        stream,
        media_type="application/dxf",
        headers=headers
    )
