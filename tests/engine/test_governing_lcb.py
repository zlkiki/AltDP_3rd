"""Tests for MIDAS Gen Internal Forces Parser and Governing LCB Selector (Phase 16-2)."""

import sqlite3
import pytest
from src.engine.interop.model_schema import MemberForce
from src.engine.interop.mgb_parser import MidasForceParser
from src.engine.interop.governing_lcb import GoverningLCBSelector


SAMPLE_FORCE_MGT = """
*FORCE-BEAM
; ELEM, LCB, PART, P, Vy, Vz, T, My, Mz
1, 1.2D+1.6L, I, -120.5, 45.2, 0.0, 0.0, 0.0, -85.6
1, 1.2D+1.6L, M, -110.0, 5.1, 0.0, 0.0, 0.0, 115.4
1, 1.2D+1.6L, J, -100.2, -48.3, 0.0, 0.0, 0.0, -92.1
1, 1.2D+1.0E_X, I, -80.0, 62.0, 0.0, 0.0, 0.0, -145.0
1, 1.2D+1.0E_X, M, -75.0, 10.0, 0.0, 0.0, 0.0, 65.0
1, 1.2D+1.0E_X, J, -70.0, -65.5, 0.0, 0.0, 0.0, -150.2
*FORCE-COLUMN
2, 1.2D+1.6L, I, -1500.0, 25.0, 15.0, 0.0, 35.0, 50.0
2, 1.2D+1.6L, J, -1480.0, 25.0, 15.0, 0.0, -30.0, -45.0
2, 1.2D+1.0E_X, I, -950.0, 85.0, 20.0, 0.0, 120.0, 180.0
2, 0.9D-1.0E_X, I, 250.0, -80.0, -18.0, 0.0, -115.0, -175.0
"""


def test_mgt_force_parsing():
    """Test parsing 6-DOF internal forces from MGT text."""
    forces = MidasForceParser.parse_mgt_forces(SAMPLE_FORCE_MGT)
    assert 1 in forces
    assert 2 in forces
    assert len(forces[1]) == 6
    assert len(forces[2]) == 4

    beam_f = forces[1][0]
    assert beam_f.elem_id == 1
    assert beam_f.lcb_name == "1.2D+1.6L"
    assert beam_f.position == "I"
    assert beam_f.p == -120.5
    assert beam_f.vy == 45.2
    assert beam_f.mz == -85.6


def test_sqlite_force_parsing(tmp_path):
    """Test parsing internal forces from SQLite/MGB database."""
    db_file = tmp_path / "test_midas.db"
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE BeamForce (
            ElemID INTEGER,
            LCB TEXT,
            Part TEXT,
            P REAL,
            Vy REAL,
            Vz REAL,
            My REAL,
            Mz REAL,
            T REAL
        )
    """)
    cursor.execute("INSERT INTO BeamForce VALUES (10, '1.2D+1.6L', 'I', -50.0, 30.0, 0.0, 0.0, -60.0, 0.0)")
    cursor.execute("INSERT INTO BeamForce VALUES (10, '1.2D+1.6L', 'M', -50.0, 2.0, 0.0, 0.0, 75.0, 0.0)")
    conn.commit()
    conn.close()

    forces = MidasForceParser.parse_sqlite_forces(str(db_file))
    assert 10 in forces
    assert len(forces[10]) == 2
    assert forces[10][1].mz == 75.0


def test_beam_governing_lcb_selection():
    """Test governing LCB selection for beam (max pos/neg moment and shear)."""
    # Create 30 synthetic LCBs for a beam
    forces = []
    for i in range(30):
        lcb = f"LCB_{i+1}"
        forces.append(MemberForce(elem_id=1, lcb_name=lcb, position="I", p=-10.0, vy=10.0 + i, mz=-50.0 - i * 2))
        forces.append(MemberForce(elem_id=1, lcb_name=lcb, position="M", p=-10.0, vy=2.0, mz=30.0 + i * 3))
        forces.append(MemberForce(elem_id=1, lcb_name=lcb, position="J", p=-10.0, vy=-10.0 - i, mz=-50.0 - i * 2))

    summary = GoverningLCBSelector.select_governing_forces(
        elem_id=1, elem_type="BEAM", forces=forces, max_cases=10
    )

    assert summary.member_id == 1
    assert summary.total_lcb_count == 30
    # Governing LCB list must be compressed to <= 10 cases
    assert len(summary.governing_lcb_list) <= 10
    assert len(summary.critical_forces) > 0
    # LCB_30 should be captured as critical due to maximum moment and shear
    assert "LCB_30" in summary.governing_lcb_list


def test_column_governing_lcb_selection():
    """Test governing LCB selection for column (P-M extreme envelope)."""
    forces = []
    # 20 regular cases
    for i in range(20):
        forces.append(MemberForce(
            elem_id=2, lcb_name=f"LCB_{i}", position="I",
            p=-1000.0 - i * 10, vy=10.0, vz=5.0, my=20.0, mz=30.0
        ))
    # Extreme tension case
    forces.append(MemberForce(elem_id=2, lcb_name="LCB_TENSION", position="I", p=500.0, my=10.0, mz=15.0))
    # Extreme moment case
    forces.append(MemberForce(elem_id=2, lcb_name="LCB_MOMENT", position="I", p=-800.0, my=250.0, mz=350.0))

    summary = GoverningLCBSelector.select_governing_forces(
        elem_id=2, elem_type="COLUMN", forces=forces, max_cases=8
    )

    assert summary.member_id == 2
    assert "LCB_TENSION" in summary.governing_lcb_list
    assert "LCB_MOMENT" in summary.governing_lcb_list
    assert len(summary.governing_lcb_list) <= 8
    assert summary.max_dcr_estimated > 0.0
