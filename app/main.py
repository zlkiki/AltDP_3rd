# app/main.py
"""AltDP Member Designer - Universal Dynamic Dispatcher API Server."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any

from app.engines import REGISTRY, get_module, get_all_modules_meta, auto_discover_modules

app = FastAPI(
    title="AltDP Member Designer API",
    description="Zero-Build Auto-Discovery Dynamic API for KDS 54 Member Design Engines",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/modules")
def list_modules():
    """Returns metadata for all auto-discovered member design modules."""
    return {"modules": get_all_modules_meta(), "total_count": len(REGISTRY)}


@app.get("/api/schema/{category}/{group}/{module_id}")
def get_module_schema(category: str, group: str, module_id: str):
    """Returns Pydantic JSON schema and UI metadata for dynamic form rendering."""
    mod = get_module(category, group, module_id)
    if not mod:
        raise HTTPException(status_code=404, detail=f"Module '{category}/{group}/{module_id}' not found.")
    return {
        "key": mod["key"],
        "info": mod["info"],
        "schema": mod["schema_json"]
    }


@app.post("/api/design/{category}/{group}/{module_id}")
def run_design(category: str, group: str, module_id: str, payload: Dict[str, Any]):
    """Dynamic universal endpoint for member structural calculation."""
    mod = get_module(category, group, module_id)
    if not mod:
        raise HTTPException(status_code=404, detail=f"Module '{category}/{group}/{module_id}' not found.")
        
    calc_func = mod["calculate"]
    schema_cls = mod.get("schema_cls")
    
    try:
        # Convert dict to Pydantic model if calculate expects a BaseModel instance
        input_data = payload
        if schema_cls and isinstance(payload, dict):
            try:
                input_data = schema_cls(**payload)
            except Exception:
                input_data = payload
                
        try:
            result = calc_func(input_data)
        except (AttributeError, TypeError):
            # Fallback: try raw payload dict or model
            if isinstance(input_data, dict) and schema_cls:
                result = calc_func(schema_cls(**payload))
            elif hasattr(input_data, "model_dump"):
                result = calc_func(input_data.model_dump())
            elif hasattr(input_data, "dict"):
                result = calc_func(input_data.dict())
            else:
                result = calc_func(payload)
                
        return {"success": True, "key": mod["key"], "result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Calculation Error in {mod['key']}: {str(e)}")


# Static file serving for No-Build Vanilla Web UI (Mount at the bottom)
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
