"""Section Database API Routes for AltDP_3rd."""

import os
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from src.engine.db.sdb_parser import SDBParser, SectionRecord

router = APIRouter(prefix="/api/db", tags=["Section Database"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SDB_DIR = os.path.join(BASE_DIR, "original_src", "Midas Design+", "Dbase")
_CACHED_PARSERS = {}


def get_parser(country_code: str = "KS") -> SDBParser:
    """Get or cache SDB parser for specific country/standard database."""
    if country_code not in _CACHED_PARSERS:
        filename = f"{country_code}.sdb"
        filepath = os.path.join(SDB_DIR, filename)
        if not os.path.exists(filepath):
            # Fallback to KS.sdb
            filepath = os.path.join(SDB_DIR, "KS.sdb")
        parser = SDBParser(filepath)
        parser.parse()
        _CACHED_PARSERS[country_code] = parser
    return _CACHED_PARSERS[country_code]


@router.get("/sections")
async def list_sections(
    db: str = Query(default="KS", description="Database standard code (KS, AISC, JIS, etc.)"),
    query: Optional[str] = Query(default="", description="Search query string"),
    limit: int = Query(default=50, ge=1, le=200)
):
    """Search sections from Midas .sdb databases."""
    try:
        parser = get_parser(db)
        results = parser.search(query) if query else parser.sections
        sliced = results[:limit]
        return {
            "success": True,
            "total_count": len(results),
            "db": db,
            "data": [
                {
                    "name": s.name,
                    "H": s.H,
                    "B": s.B,
                    "tw": s.tw,
                    "tf": s.tf,
                    "A": s.A,
                    "Ix": s.Ix,
                    "Iy": s.Iy,
                    "weight": s.weight
                }
                for s in sliced
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
