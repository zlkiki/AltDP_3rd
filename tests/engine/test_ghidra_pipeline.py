"""
tests/engine/test_ghidra_pipeline.py
====================================
Unit and integration tests for the Ghidra Headless extraction pipeline.
"""

import subprocess
import sys
from pathlib import Path
from scripts.ghidra_extract import detect_environment, DEFAULT_GHIDRA_PATH, DEFAULT_JAVA_HOME


def test_detect_environment():
    """Verify that Ghidra Analyzer and Java JDK paths are correctly detected."""
    env_info = detect_environment()
    assert env_info["ghidra_bin"] is not None
    assert env_info["ghidra_bin"].exists()
    assert env_info["java_home"] is not None
    assert env_info["java_home"].exists()


def test_ghidra_script_exists():
    """Verify that ExportTargetFunctions.java exists in scripts/."""
    script_path = Path("scripts/ExportTargetFunctions.java")
    assert script_path.exists()
    content = script_path.read_text(encoding="utf-8")
    assert "class ExportTargetFunctions extends GhidraScript" in content
    assert "DecompInterface" in content


def test_ghidra_extract_cli_help():
    """Verify that ghidra_extract.py CLI can be invoked with --help."""
    result = subprocess.run(
        [sys.executable, "scripts/ghidra_extract.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "--dll" in result.stdout
    assert "--symbols" in result.stdout
    assert "--out" in result.stdout
