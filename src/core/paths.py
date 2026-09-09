"""Application Path Abstraction Layer for AltDP_3rd.

Centralizes all filesystem paths for standalone execution without external dependencies.
"""

import os
from pathlib import Path

# Base Directories
SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SRC_DIR.parent

# Internal Data Asset Directories
DATA_DIR = SRC_DIR / "data"
DBASE_DIR = DATA_DIR / "dbase"

# Static & Template Directories
WEB_DIR = SRC_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

# Tests & Benchmarks Directories
TESTS_DIR = PROJECT_ROOT / "tests"
BENCHMARKS_DIR = TESTS_DIR / "benchmarks"
