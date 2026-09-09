"""Test Phase 22-5-3: RC Beam Pure White A4 7-Chapter KaTeX Structural Calculation Report.

Conforms to Requirement 22-5-3 & DOCS 07/14/16:
- 7-Chapter Structure (Chapter 1 to Chapter 7)
- Independent Chapter 3: Ductility Limit & Minimum Reinforcement Check (KDS 14 20 20: 2022)
- KaTeX aligned environments for multiline overflow prevention
- Universal DCR notation on all design checks
- Dynamic simplification/omission on zero loads (Mu <= 0, Tu <= 0)
- Chapter 6 Serviceability: Branson weighted average I_e, long-term deflection, and 3-station s <= s_max crack control
- Comprehensive summary table in Chapter 7 with all governing DCRs
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_rc_beam_report_7_chapters_structure():
    """Verify standard 7-chapter structure and chapter keys."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Verify 7 standard chapters exist with exact chapter keys
    assert 'data-chapter-key="general"' in content
    assert 'data-chapter-key="load"' in content
    assert 'data-chapter-key="ductility"' in content
    assert 'data-chapter-key="flexure"' in content
    assert 'data-chapter-key="shear"' in content
    assert 'data-chapter-key="serviceability"' in content
    assert 'data-chapter-key="verdict"' in content

    # Verify chapter numbering (using unicode escapes for cross-platform safety)
    # \uC81C = '제', \uC7A5 = '장'
    assert '\uC81C 1\uC7A5' in content
    assert '\uC81C 2\uC7A5' in content
    assert '\uC81C 3\uC7A5' in content
    assert '\uC81C 4\uC7A5' in content
    assert '\uC81C 5\uC7A5' in content
    assert '\uC81C 6\uC7A5' in content
    assert '\uC81C 7\uC7A5' in content

    # Chapter titles
    assert 'Design Information & Section Geometry' in content
    assert 'Design Factored Loads & Combinations' in content
    assert 'Ductility Limit & Minimum Reinforcement Check' in content
    assert 'Flexural Strength Check' in content
    assert 'Shear & Torsion Strength Check' in content
    assert 'Serviceability Check' in content
    assert 'Executive Summary & Final Verdict' in content

    # Verify user input section is isolated as appendix to preserve 7 chapters
    assert 'user-input-section' in content
    assert 'report-appendix' in content


def test_rc_beam_report_chapter3_ductility_content():
    """Verify Chapter 3 has 3-Station summary table and reinforcement arrangement branching."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # 3-Station Summary Table
    assert '3.1 3-Station' in content
    assert 'KDS 14 20 20' in content
    assert 'DCR' in content
    assert r'\phi M_n \ge 1.2 M_{cr}' in content.replace('\\\\', '\\') or '1.2 M_{cr}' in content

    # Check arrangement type branching
    assert 'ONE_SECTION' in content
    assert 'SYMMETRIC_ENDS' in content
    assert 'THREE_STATIONS' in content

    # Check ductility formula and limits
    assert r'\epsilon_t \ge \epsilon_{t,\min}' in content.replace('\\\\', '\\') or 'epsT' in content
    assert r'\frac{c}{d_t}' in content.replace('\\\\', '\\')
    assert 'dcrEps' in content


def test_rc_beam_report_katex_aligned_environment():
    """Verify KaTeX \\begin{aligned} is used for formulas to prevent overflow."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Verify aligned blocks exist across multiple chapters
    assert r'\begin{aligned}' in content
    assert r'\end{aligned}' in content

    # Check aligned count
    count_aligned = content.count(r'\begin{aligned}')
    assert count_aligned >= 5, f'Expected at least 5 aligned blocks, got {count_aligned}'


def test_rc_beam_report_zero_load_omission():
    """Verify dynamic omission / summary handling for zero loads (Mu <= 0, Tu <= 0)."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Zero moment omission logic
    assert 'isZeroMoment' in content or 'isZero' in content
    # Zero torsion simplification notice
    assert 'isZeroTorsion' in content
    assert 'dcrTorsion' in content


def test_rc_beam_report_chapter6_serviceability_formulas():
    """Verify Chapter 6 includes Branson weighted average I_e and crack spacing s <= s_max."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Branson I_e weighted average formulas
    assert 'Branson' in content or 'I_{e' in content
    assert '0.50' in content or '0.5' in content
    assert '0.85' in content

    # Long-term deflection multiplier lambda_Delta
    assert r'\lambda_\Delta' in content.replace('\\\\', '\\') or 'lambda' in content

    # Crack spacing limit s <= s_max (KDS 14 20 30)
    assert 's_{\\max}' in content or 's_{max}' in content or 's_max' in content
    assert '375' in content
    assert '210' in content
    assert '300' in content


def test_rc_beam_report_chapter7_universal_dcr_summary():
    """Verify Chapter 7 includes universal DCR summary table covering all limit states."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Chapter 7 heading
    assert '\uC81C 7\uC7A5' in content
    assert 'Executive Summary & Final Verdict' in content

    # Review categories in Chapter 7
    assert 'dcrMin' in content
    assert 'dcrEps' in content
    assert 'dcrDefl' in content
    assert 'dcrCrack' in content

    # Governing DCR and verdict banner
    assert 'governingDcr' in content
    assert 'overallVerdict' in content
