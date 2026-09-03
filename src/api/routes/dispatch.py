"""Dynamic Calculation Dispatcher API Route for AltDP_3rd.

Endpoints:
    POST /api/design/{category}/{group}/{module_id}
Dispatches calculation requests dynamically to member design engines (RC, Steel, PC, Misc)
and formats results according to the KDS Standard Result Schema.
"""

import traceback
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.engines import get_module

router = APIRouter(tags=["dispatch"])


@router.post("/api/design/{category}/{group}/{module_id}")
def run_design(category: str, group: str, module_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamic universal endpoint for member structural calculation."""
    mod = get_module(category, group, module_id)
    if not mod:
        raise HTTPException(
            status_code=404,
            detail=f"Module '{category}/{group}/{module_id}' not found."
        )

    calc_func = mod["calculate"]
    schema_cls = mod.get("schema_cls")

    try:
        # Convert dictionary to Pydantic model if calculate expects a BaseModel instance
        input_data = payload
        if schema_cls and isinstance(payload, dict):
            try:
                input_data = schema_cls(**payload)
            except Exception:
                input_data = payload

        # Execute calculation routine
        try:
            result = calc_func(input_data)
        except (AttributeError, TypeError):
            if isinstance(input_data, dict) and schema_cls:
                result = calc_func(schema_cls(**payload))
            elif hasattr(input_data, "model_dump"):
                result = calc_func(input_data.model_dump())
            elif hasattr(input_data, "dict"):
                result = calc_func(input_data.dict())
            else:
                result = calc_func(payload)

        # Standardize result schema if required
        if isinstance(result, dict):
            dcr = result.get("dcr", result.get("governing_dcr", result.get("max_ratio", 0.0)))
            if "dcr" not in result:
                result["dcr"] = float(dcr)
            if "governing_dcr" not in result:
                result["governing_dcr"] = float(dcr)
            if "verdict" not in result:
                result["verdict"] = "OK" if float(dcr) <= 1.0 else "NG"

        return {
            "success": True,
            "key": mod["key"],
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Calculation Error in {mod['key']}: {str(e)}"
        )
