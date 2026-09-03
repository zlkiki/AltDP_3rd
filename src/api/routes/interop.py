"""FastAPI Routes for MIDAS Gen Interoperability and Batch Design (Phase 16-3)."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

from src.engine.interop.model_schema import MidasModel3D, MemberForce
from src.engine.interop.mgt_parser import MGTParser
from src.engine.interop.mgb_parser import MidasForceParser
from src.engine.project.batch_checker import BatchDesignChecker, BatchDesignSummary


router = APIRouter(prefix="/api/v1/interop", tags=["MIDAS Gen Interoperability"])

# In-memory session store for uploaded models and forces
_ACTIVE_MODEL: Optional[MidasModel3D] = None
_ACTIVE_FORCES: Dict[int, List[MemberForce]] = {}
_LAST_BATCH_SUMMARY: Optional[BatchDesignSummary] = None


class MgtUploadResponse(BaseModel):
    success: bool
    message: str
    total_nodes: int
    total_elements: int
    total_stories: int
    elements_by_type: Dict[str, int]


class BatchDesignRequest(BaseModel):
    story_filter: Optional[str] = None


@router.post("/mgt/upload", response_model=MgtUploadResponse)
async def upload_mgt_file(
    file: Optional[UploadFile] = File(None),
    mgt_text: Optional[str] = Form(None)
):
    """Upload and parse MIDAS Gen .mgt script file or raw text."""
    global _ACTIVE_MODEL, _ACTIVE_FORCES
    content = ""
    if file:
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("cp949", errors="ignore")
    elif mgt_text:
        content = mgt_text
    else:
        raise HTTPException(status_code=400, detail="Either file or mgt_text must be provided.")

    if not content.strip():
        raise HTTPException(status_code=400, detail="MGT content cannot be empty.")

    try:
        parser = MGTParser()
        model = parser.parse_string(content)
        forces = MidasForceParser.parse_mgt_forces(content)
        _ACTIVE_MODEL = model
        _ACTIVE_FORCES = forces

        counts = {}
        for el in model.elements.values():
            counts[el.elem_type] = counts.get(el.elem_type, 0) + 1

        return MgtUploadResponse(
            success=True,
            message="MGT model successfully parsed and loaded.",
            total_nodes=len(model.nodes),
            total_elements=len(model.elements),
            total_stories=len(model.stories),
            elements_by_type=counts
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse MGT file: {str(e)}")


@router.post("/batch-design", response_model=BatchDesignSummary)
def run_batch_design(request: Optional[BatchDesignRequest] = None):
    """Execute batch member design for loaded model and forces."""
    global _ACTIVE_MODEL, _ACTIVE_FORCES, _LAST_BATCH_SUMMARY
    if _ACTIVE_MODEL is None or len(_ACTIVE_MODEL.elements) == 0:
        raise HTTPException(status_code=400, detail="No active MIDAS model loaded. Upload an MGT file first.")

    story = request.story_filter if request else None
    summary = BatchDesignChecker.run_batch_check(
        model=_ACTIVE_MODEL,
        forces_by_elem=_ACTIVE_FORCES,
        story_filter=story
    )
    _LAST_BATCH_SUMMARY = summary
    return summary


@router.get("/batch-summary", response_model=Dict[str, Any])
def get_batch_summary():
    """Retrieve the latest batch design summary."""
    global _LAST_BATCH_SUMMARY
    if _LAST_BATCH_SUMMARY is None:
        raise HTTPException(status_code=404, detail="No batch design has been executed yet.")
    return _LAST_BATCH_SUMMARY.model_dump()


@router.get("/batch-status/{task_id}")
def get_batch_status(task_id: str):
    """Retrieve the progress and execution status of a batch design job."""
    # Synchronous pipeline completes immediately (100%)
    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "progress_percent": 100.0,
        "has_result": _LAST_BATCH_SUMMARY is not None
    }
