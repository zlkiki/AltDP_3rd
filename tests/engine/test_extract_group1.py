"""
tests/engine/test_extract_group1.py
===================================
Verification tests for Phase 01-2: Group 1 (P-M Interaction & Solver).
"""

import json
from pathlib import Path


def test_group1_solver_files_exist():
    """Verify that Group 1 decompiled C files and metadata JSON exist."""
    solver_dir = Path("decompiled_src/core_routines/solver")
    assert solver_dir.exists(), "Solver directory must exist."

    meta_json = solver_dir / "solver_meta.json"
    assert meta_json.exists(), "solver_meta.json must exist."

    with open(meta_json, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["matched_count"] > 0, "At least one solver function must be extracted."

    c_files = list(solver_dir.glob("*.c"))
    assert len(c_files) >= 1, "At least one .c file must be exported in solver/."

    # Verify content in C files
    has_bcco = any("CHK_BCCO" in f.name for f in c_files)
    assert has_bcco, "CHK_BCCO C source must be present."
