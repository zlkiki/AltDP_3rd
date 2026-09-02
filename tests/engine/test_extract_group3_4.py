"""
tests/engine/test_extract_group3_4.py
=====================================
Verification tests for Phase 01-4: Group 3 & 4 (Steel Members, Connections & BasePlate).
"""

import json
from pathlib import Path


def test_group3_4_steel_files_exist():
    """Verify that Group 3 & 4 Steel decompiled C files and metadata JSON exist."""
    steel_dir = Path("decompiled_src/core_routines/steel")
    assert steel_dir.exists(), "Steel directory must exist."

    meta_json = steel_dir / "steel_meta.json"
    assert meta_json.exists(), "steel_meta.json must exist."

    with open(meta_json, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["matched_count"] > 0, "Steel functions must be extracted."

    c_files = list(steel_dir.glob("*.c"))
    assert len(c_files) >= 1, "At least one Steel .c file must be exported."
