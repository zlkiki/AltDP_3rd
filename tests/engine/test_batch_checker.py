"""Unit tests for BatchDesignChecker engine (Phase 16-3)."""

import pytest
from src.engine.interop.model_schema import MidasModel3D, MidasNode, MidasElement, MidasSection, MemberForce
from src.engine.project.batch_checker import BatchDesignChecker


def test_batch_checker_rc_members():
    """Test batch design checking for mixed RC beams and columns."""
    model = MidasModel3D()
    # Add sections
    model.sections[1] = MidasSection(sec_id=1, sec_name="B400x600", b=400.0, h=600.0)
    model.sections[2] = MidasSection(sec_id=2, sec_name="C600x600", b=600.0, h=600.0)

    forces_by_elem = {}
    # Create 50 beams and 50 columns
    for i in range(1, 51):
        # Beam
        model.elements[i] = MidasElement(elem_id=i, elem_type="BEAM", mat_id=1, sec_id=1, nodes=[1, 2], story="2F")
        forces_by_elem[i] = [
            MemberForce(elem_id=i, lcb_name="1.2D+1.6L", position="I", vy=40.0, mz=-90.0),
            MemberForce(elem_id=i, lcb_name="1.2D+1.6L", position="M", vy=5.0, mz=120.0),
            MemberForce(elem_id=i, lcb_name="1.2D+1.0E", position="I", vy=60.0, mz=-160.0),
        ]
        # Column
        col_id = i + 100
        model.elements[col_id] = MidasElement(elem_id=col_id, elem_type="COLUMN", mat_id=1, sec_id=2, nodes=[3, 4], story="1F")
        forces_by_elem[col_id] = [
            MemberForce(elem_id=col_id, lcb_name="1.2D+1.6L", position="I", p=-1200.0, my=30.0, mz=50.0),
            MemberForce(elem_id=col_id, lcb_name="1.2D+1.0E", position="I", p=-800.0, my=80.0, mz=150.0),
        ]

    summary = BatchDesignChecker.run_batch_check(model, forces_by_elem)

    assert summary.total_members == 100
    assert summary.safe_count > 0
    assert summary.max_dcr > 0.0
    assert "1F" in summary.story_summaries
    assert "2F" in summary.story_summaries
    assert summary.story_summaries["1F"]["total"] == 50
    assert summary.story_summaries["2F"]["total"] == 50
    # Performance check: 100 members must take < 0.5s
    assert summary.elapsed_seconds < 0.5


def test_batch_checker_story_filter():
    """Test batch design check with story filtering."""
    model = MidasModel3D()
    model.sections[1] = MidasSection(sec_id=1, sec_name="B400x600", b=400.0, h=600.0)

    model.elements[1] = MidasElement(elem_id=1, elem_type="BEAM", mat_id=1, sec_id=1, nodes=[1, 2], story="1F")
    model.elements[2] = MidasElement(elem_id=2, elem_type="BEAM", mat_id=1, sec_id=1, nodes=[2, 3], story="2F")

    forces = {
        1: [MemberForce(elem_id=1, lcb_name="LCB1", mz=80.0)],
        2: [MemberForce(elem_id=2, lcb_name="LCB1", mz=80.0)],
    }

    summary_1f = BatchDesignChecker.run_batch_check(model, forces, story_filter="1F")
    assert summary_1f.total_members == 1
    assert summary_1f.results[0].elem_id == 1
