"""Unit tests for SDB section database parser."""

import os
import pytest
from src.engine.db.sdb_parser import SDBParser

SDB_PATH = r"f:\PyProject\re-DP\original_src\Midas Design+\Dbase\KS.sdb"


@pytest.mark.engine
def test_sdb_parser_ks():
    if not os.path.exists(SDB_PATH):
        pytest.skip("KS.sdb file not available")
        
    parser = SDBParser(SDB_PATH)
    sections = parser.parse()
    
    assert len(sections) > 0
    # Search for H-beam
    results = parser.search("400")
    assert len(results) > 0
