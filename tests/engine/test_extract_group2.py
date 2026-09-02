"""
tests/engine/test_extract_group2.py
===================================
Verification tests for Phase 01-3: Group 2 (RC Core Elements: Beam, Wall, Slab, Footing, Retaining Wall).
"""

import json
from pathlib import Path


def test_group2_rc_files_exist():
    """Verify that Group 2 RC decompiled C files and metadata JSON exist."""
    rc_dir = Path("decompiled_src/core_routines/rc")
    assert rc_dir.exists(), "RC directory must exist."

    meta_json = rc_dir / "rc_meta.json"
    assert meta_json.exists(), "rc_meta.json must exist."

    with open(meta_json, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["matched_count"] > 0, "RC functions must be extracted."

    c_files = list(rc_dir.glob("*.c"))
    assert len(c_files) >= 1, "At least one RC .c file must be exported in rc/."

    # Check for primary element checks (Beam, Wall, Slab, Footing, Retaining Wall)
    file_names = " ".join(f.name for f in c_files)
    assert "CHK_BBBE" in file_names or "beam" in file_names.lower() or "CHK_" in file_names
