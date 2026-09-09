"""Standalone FastAPI Server for RC Column Prototype.

Ports Midas Design+ IDD_RCS_COLUMN_PMODE_DLG into an interactive web testbed.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .schemas import RCColumnFullInput
from .engine import RCColumnEngine

# 앱 생성
app = FastAPI(title="Midas Design+ RC Column Standalone Prototype")

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=FileResponse)
async def get_index():
    """Render the 1:1 Midas Design+ RC Column Dialog Page."""
    return FileResponse(os.path.join(templates_dir, "index.html"))


@app.post("/api/check")
async def post_check(inp: RCColumnFullInput):
    """Run full RC Column engineering check and return 10-domain results."""
    try:
        res = RCColumnEngine.analyze(inp)
        return res
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/api/auto-design")
async def post_auto_design(inp: RCColumnFullInput):
    """Run automated optimal design search."""
    try:
        opt_inp = RCColumnEngine.auto_design(inp)
        res = RCColumnEngine.analyze(opt_inp)
        return {
            "optimized_input": opt_inp,
            "result": res
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
