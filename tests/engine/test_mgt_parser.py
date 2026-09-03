"""Tests for MIDAS Gen MGT parser and 3D model construction (Phase 16-1)."""

import time
import pytest
from src.engine.interop.mgt_parser import MGTParser


SAMPLE_MGT = """
; MIDAS Gen MGT Script Test Sample
*NODE
1, 0.0, 0.0, 0.0
2, 6000.0, 0.0, 0.0
3, 0.0, 0.0, 3500.0
4, 6000.0, 0.0, 3500.0
5, 0.0, 0.0, 7000.0
6, 6000.0, 0.0, 7000.0

*MATERIAL
1, CONC, C24
27386.0, 0.2, 1.0e-5, 24.5
2, STEEL, SM355
205000.0, 0.3, 1.2e-5, 78.5

*SECTION
1, DBUSER, H-SECTION, H 400x200x8/13
400, 200, 8, 13, 16
2, RECT, B600x600
600, 600

*STORY
1F, 3500.0, 3500.0
2F, 3500.0, 7000.0

*ELEMENT
; 1-2: Columns (1->3, 2->4)
1, BEAM, 1, 2, 1, 3
2, BEAM, 1, 2, 2, 4
; 3: Beam (3->4)
3, BEAM, 1, 2, 3, 4
; 4: Brace (1->4)
4, TRUSS, 2, 1, 1, 4
; 5: 2nd Story Columns (3->5, 4->6)
5, BEAM, 1, 2, 3, 5
6, BEAM, 1, 2, 4, 6
; 7: 2nd Story Beam (5->6)
7, BEAM, 1, 2, 5, 6
"""


def test_mgt_parsing_nodes_and_elements():
    parser = MGTParser()
    model = parser.parse_string(SAMPLE_MGT)

    assert len(model.nodes) == 6
    assert model.nodes[1].x == 0.0
    assert model.nodes[1].z == 0.0
    assert model.nodes[4].x == 6000.0
    assert model.nodes[4].z == 3500.0

    assert len(model.elements) == 7
    assert len(model.materials) == 2
    assert len(model.sections) == 2
    assert len(model.stories) == 2


def test_mgt_element_classification():
    parser = MGTParser()
    model = parser.parse_string(SAMPLE_MGT)

    # Elem 1 & 2 are vertical columns (Z: 0 -> 3500)
    assert model.elements[1].elem_type == "COLUMN"
    assert model.elements[2].elem_type == "COLUMN"

    # Elem 3 is horizontal beam (Z: 3500 -> 3500)
    assert model.elements[3].elem_type == "BEAM"

    # Elem 4 is diagonal brace (X: 0->6000, Z: 0->3500)
    assert model.elements[4].elem_type == "BRACE"

    # Elem 5 & 6 are columns on 2nd floor
    assert model.elements[5].elem_type == "COLUMN"
    assert model.elements[6].elem_type == "COLUMN"

    # Elem 7 is beam on 2nd floor
    assert model.elements[7].elem_type == "BEAM"


def test_mgt_story_assignment():
    parser = MGTParser()
    model = parser.parse_string(SAMPLE_MGT)

    # 1st floor elements (Z up to 3500)
    assert model.elements[1].story == "1F"
    assert model.elements[2].story == "1F"
    assert model.elements[3].story == "1F"

    # 2nd floor elements (Z up to 7000)
    assert model.elements[5].story == "2F"
    assert model.elements[6].story == "2F"
    assert model.elements[7].story == "2F"


def test_mgt_section_dimensions():
    parser = MGTParser()
    model = parser.parse_string(SAMPLE_MGT)

    sec1 = model.sections[1]
    assert sec1.h == 400
    assert sec1.b == 200
    assert sec1.tw == 8
    assert sec1.tf == 13

    sec2 = model.sections[2]
    assert sec2.h == 600
    assert sec2.b == 600


def test_large_mgt_parsing_performance():
    # Generate 1000 nodes and 1000 elements
    lines = ["*NODE"]
    for i in range(1, 1001):
        lines.append(f"{i}, {i*10.0}, {i*5.0}, {i*3.0}")
    lines.append("*ELEMENT")
    for i in range(1, 1000):
        lines.append(f"{i}, BEAM, 1, 1, {i}, {i+1}")

    big_mgt = "\n".join(lines)
    parser = MGTParser()

    start_t = time.perf_counter()
    model = parser.parse_string(big_mgt)
    elapsed = time.perf_counter() - start_t

    assert len(model.nodes) == 1000
    assert len(model.elements) == 999
    assert elapsed < 0.2  # 0.2s performance threshold
