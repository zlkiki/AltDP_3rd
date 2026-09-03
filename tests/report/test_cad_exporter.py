"""Unit and Integration tests for ezdxf-based 2D CAD Exporter and Schedule Generator (Phase 17-1)."""

import os
import ezdxf
import pytest

from src.report.cad_exporter import (
    CADExporter,
    BeamSectionCADInput,
    ColumnSectionCADInput,
    RebarDetail,
)
from src.report.cad_schedule import CADScheduleTable


def test_cad_exporter_layers_and_beam_section(tmp_path):
    """Test standard structural layer setup and RC beam section drawing."""
    doc = CADExporter.create_document()
    
    # 1. Verify standard layers
    assert "S-CONC" in doc.layers
    assert "S-REBAR-MAIN" in doc.layers
    assert "S-REBAR-SUB" in doc.layers
    assert "S-DIM" in doc.layers
    assert "S-TEXT" in doc.layers

    # 2. Draw RC Beam section
    inp = BeamSectionCADInput(
        name="B1_Test",
        b=400.0,
        h=600.0,
        cover=50.0,
        top_rebars=[RebarDetail(bar_size="D19", count=2, diameter_mm=19.1)],
        bot_rebars=[RebarDetail(bar_size="D22", count=4, diameter_mm=22.2)]
    )
    CADExporter.draw_rc_beam_section(doc, inp, origin=(0.0, 0.0))

    msp = doc.modelspace()
    entities = list(msp)
    assert len(entities) > 5

    # Check that circles exist on S-REBAR-MAIN
    rebar_circles = [e for e in entities if e.dxftype() == "CIRCLE" and e.dxf.layer == "S-REBAR-MAIN"]
    assert len(rebar_circles) == 6  # 2 top + 4 bot

    # 3. Save to file and re-read for CAD compatibility
    output_dxf = tmp_path / "beam_detail.dxf"
    doc.saveas(str(output_dxf))
    assert os.path.exists(str(output_dxf))

    reloaded = ezdxf.readfile(str(output_dxf))
    assert "S-CONC" in reloaded.layers
    assert len(list(reloaded.modelspace())) == len(entities)


def test_cad_exporter_column_section(tmp_path):
    """Test RC column cross section drawing with perimeter rebars."""
    doc = CADExporter.create_document()
    inp = ColumnSectionCADInput(
        name="C1_Test",
        b=600.0,
        h=600.0,
        total_bars=12,
        bar_dia=25.4
    )
    CADExporter.draw_rc_column_section(doc, inp, origin=(1000.0, 0.0))

    msp = doc.modelspace()
    rebar_circles = [e for e in msp if e.dxftype() == "CIRCLE" and e.dxf.layer == "S-REBAR-MAIN"]
    assert len(rebar_circles) == 12

    output_dxf = tmp_path / "column_detail.dxf"
    doc.saveas(str(output_dxf))
    assert os.path.exists(str(output_dxf))


def test_cad_schedule_table(tmp_path):
    """Test generating structural schedule grid table."""
    doc = CADExporter.create_document()
    CADScheduleTable.draw_sample_beam_schedule(doc, origin=(0.0, 1000.0))

    msp = doc.modelspace()
    texts = [e for e in msp if e.dxftype() == "TEXT"]
    assert len(texts) >= 15

    output_dxf = tmp_path / "schedule.dxf"
    doc.saveas(str(output_dxf))
    assert os.path.exists(str(output_dxf))
