"""
tests/engine/test_extract_group5.py
===================================
Verification tests for Phase 01-5: Group 5 (Section Properties DB & Overall Index).
"""

import json
from pathlib import Path


def test_group5_db_and_overall_index():
    """Verify that Group 5 DB C files exist and core_routines/README.md is created."""
    db_dir = Path("decompiled_src/core_routines/db")
    assert db_dir.exists(), "DB directory must exist."

    readme_path = Path("decompiled_src/core_routines/README.md")
    assert readme_path.exists(), "Global index README.md must exist."

    readme_content = readme_path.read_text(encoding="utf-8")
    assert "# AltDP_3rd Decompiled Core Routines Index" in readme_content
    assert "CHK_BCCO" in readme_content
    assert "CHK_BBBE" in readme_content
    assert "CHK_USMC" in readme_content
