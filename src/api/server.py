"""FastAPI Server Application for AltDP_3rd.

Provides web application serving, static asset routing, and engineering API endpoints.
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.rc import router as rc_router
from src.api.routes.rc_wall_slab import router as rc_wall_slab_router
from src.api.routes.rc_foundation import router as rc_foundation_router
from src.api.routes.steel import router as steel_router
from src.api.routes.db import router as db_router
from src.api.routes.report import router as report_router

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")

app = FastAPI(
    title="AltDP_3rd Engineering API",
    description="Web-based Structural Member Design Platform (KDS 14 20 00 / KDS 14 31 00)",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates or Direct HTML loader
try:
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
except Exception:
    templates = None

# Include API routers
app.include_router(rc_router)
app.include_router(rc_wall_slab_router)
app.include_router(rc_foundation_router)
app.include_router(steel_router)
app.include_router(db_router)
app.include_router(report_router)


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Serve main AltDP_3rd web application dashboard."""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request, "app_name": "AltDP_3rd"})
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>AltDP_3rd Web Engineering Platform</h1>")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "platform": "AltDP_3rd", "version": "1.0.0"}
