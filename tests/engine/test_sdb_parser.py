"""Unit tests for SDB section database parser and SectionDBManager."""

import os
import pytest
from pathlib import Path
from src.engine.db.sdb_parser import SDBParser
from src.engine.db.section_db import SectionDBManager, get_section_db_manager

DB_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "original_src", "Midas Design+", "Dbase")
)
KS_SDB_PATH = os.path.join(DB_DIR, "KS.sdb")


@pytest.mark.engine
def test_sdb_parser_ks():
    """Test parsing KS.sdb file."""
    if not os.path.exists(KS_SDB_PATH):
        pytest.skip(f"KS.sdb file not found at {KS_SDB_PATH}")

    parser = SDBParser(KS_SDB_PATH)
    sections = parser.parse()

    assert len(sections) > 0
    # Search for H-beam
    results = parser.search("400")
    assert len(results) > 0
    
    # Check first section attributes
    sec = results[0]
    assert sec.H > 0
    assert sec.B > 0
    assert sec.A > 0
    assert sec.Ix > 0
    assert sec.Zx > 0


@pytest.mark.engine
def test_sdb_parser_aisc():
    """Test parsing AISC.sdb file."""
    aisc_path = os.path.join(DB_DIR, "AISC.sdb")
    if not os.path.exists(aisc_path):
        pytest.skip(f"AISC.sdb file not found at {aisc_path}")

    parser = SDBParser(aisc_path)
    sections = parser.parse()
    assert len(sections) > 0


@pytest.mark.engine
def test_section_db_manager_sqlite():
    """Test SectionDBManager SQLite caching and queries."""
    if not os.path.exists(DB_DIR):
        pytest.skip(f"DB directory not found at {DB_DIR}")

    mgr = SectionDBManager(DB_DIR)
    available_dbs = mgr.get_available_databases()
    assert len(available_dbs) >= 10
    assert "KS" in available_dbs or "KS21" in available_dbs

    # Load KS database
    count = mgr.load_database("KS")
    assert count > 0

    # Search section
    results = mgr.search_sections(keyword="400", db_name="KS")
    assert len(results) > 0
    first = results[0]
    assert first.H > 0

    # Direct retrieval
    sec_exact = mgr.get_section(name=first.name, db_name="KS")
    assert sec_exact is not None
    assert sec_exact.name == first.name
