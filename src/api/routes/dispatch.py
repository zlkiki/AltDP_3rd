"""Dynamic Calculation Dispatcher API Route for AltDP_3rd.

Endpoints:
    POST /api/design/{category}/{group}/{module_id}
Dispatches calculation requests dynamically to member design engines (RC, Steel, PC, Misc)
and formats results according to the KDS Standard Result Schema.
When unintegrated or WIP modules are requested, returns standard WIPResponse (NOT_YET_IMPLEMENTED)
instead of mock values or 500 errors.
"""

import traceback
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.engines import get_module
from src.api.models.wip import (
    WIPModuleDetail,
    WIPResponse,
    get_wip_module_detail,
    is_wip_module,
    MODULE_CATALOG_61
)

router = APIRouter(tags=["dispatch"])


@router.post("/api/design/{category}/{group}/{module_id}")
def run_design(category: str, group: str, module_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamic universal endpoint for member structural calculation."""
    # 1. Check registered calculation module
    mod = get_module(category, group, module_id)
    
    # 2. Check 61-module catalog metadata for WIP detection
    wip_meta = get_wip_module_detail(category, group, module_id)

    # Case A: Module is not registered in dynamic engines
    if not mod:
        # If it belongs to the 61-module catalog, return transparent WIPResponse
        if wip_meta:
            return WIPResponse(
                success=False,
                status="NOT_YET_IMPLEMENTED",
                code="WIP_MODULE",
                message=f"'{wip_meta.name}' 부재는 원본앱 1:1 서브탭 및 KDS 전개식 연동 준비 중(WIP)입니다.",
                module=wip_meta
            ).model_dump()
            
        # If completely unknown/invalid route, return 404 Not Found
        raise HTTPException(
            status_code=404,
            detail=f"Module '{category}/{group}/{module_id}' not found."
        )

    # Case B: Module is registered, but flagged as WIP
    if wip_meta and wip_meta.engine_status == "WIP":
        return WIPResponse(
            success=False,
            status="NOT_YET_IMPLEMENTED",
            code="WIP_MODULE",
            message=f"'{wip_meta.name}' 부재는 원본앱 1:1 서브탭 및 KDS 전개식 연동 준비 중(WIP)입니다.",
            module=wip_meta
        ).model_dump()

    # Case C: Execute calculation routine
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
        except NotImplementedError:
            # Handle explicit WIP stub exceptions honestly
            if not wip_meta:
                wip_meta = WIPModuleDetail(
                    key=mod["key"],
                    name=mod.get("info", {}).get("name", module_id),
                    midas_dlg="IDD_WIP_DLG",
                    category=category,
                    group=group,
                    domain="RC" if category == "rc" else "STEEL",
                    tier="Tier 3",
                    standard="KDS 14 00 00",
                    engine_status="WIP"
                )
            return WIPResponse(
                success=False,
                status="NOT_YET_IMPLEMENTED",
                code="WIP_MODULE",
                message=f"'{wip_meta.name}' 엔진 연산 루틴이 준비 중(WIP)입니다.",
                module=wip_meta
            ).model_dump()
        except (AttributeError, TypeError):
            if isinstance(input_data, dict) and schema_cls:
                result = calc_func(schema_cls(**payload))
            elif hasattr(input_data, "model_dump"):
                result = calc_func(input_data.model_dump())
            elif hasattr(input_data, "dict"):
                result = calc_func(input_data.dict())
            else:
                result = calc_func(payload)

        # Standardize result schema without injecting fake default values
        if isinstance(result, dict):
            dcr_val = result.get("dcr", result.get("governing_dcr", result.get("max_ratio")))
            if dcr_val is not None:
                try:
                    dcr_float = float(dcr_val)
                    if "dcr" not in result:
                        result["dcr"] = dcr_float
                    if "governing_dcr" not in result:
                        result["governing_dcr"] = dcr_float
                    if "verdict" not in result:
                        result["verdict"] = "OK" if dcr_float <= 1.0 else "NG"
                except (ValueError, TypeError):
                    pass

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


@router.get("/api/design/{category}/{group}/{module_id}/status")
def get_design_status(category: str, group: str, module_id: str) -> Dict[str, Any]:
    """Returns the operational status (VERIFIED or WIP) of a design module."""
    mod = get_module(category, group, module_id)
    wip_meta = get_wip_module_detail(category, group, module_id)
    
    if not mod and not wip_meta:
        raise HTTPException(
            status_code=404,
            detail=f"Module '{category}/{group}/{module_id}' not found."
        )

    is_wip = False
    if not mod or (wip_meta and wip_meta.engine_status == "WIP"):
        is_wip = True

    return {
        "key": f"{category}/{group}/{module_id}",
        "is_wip": is_wip,
        "engine_status": "WIP" if is_wip else "VERIFIED",
        "module": wip_meta.model_dump() if wip_meta else None
    }

