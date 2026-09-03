"""Schema API Route for AltDP_3rd.

Provides member module metadata and Pydantic JSON schema endpoints for dynamic form generation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.engines import REGISTRY, get_module, get_all_modules_meta

router = APIRouter(tags=["schema"])


@router.get("/api/modules")
def list_modules() -> Dict[str, Any]:
    """Returns metadata for all auto-discovered member design modules (54 modules)."""
    modules = get_all_modules_meta()
    return {
        "modules": modules,
        "total_count": len(modules)
    }


@router.get("/api/schema/{category}/{group}/{module_id}")
def get_module_schema(category: str, group: str, module_id: str) -> Dict[str, Any]:
    """Returns Pydantic JSON schema and UI metadata for dynamic form rendering."""
    mod = get_module(category, group, module_id)
    if not mod:
        raise HTTPException(
            status_code=404,
            detail=f"Module '{category}/{group}/{module_id}' not found."
        )
    return {
        "key": mod["key"],
        "info": mod["info"],
        "schema": mod["schema_json"]
    }
