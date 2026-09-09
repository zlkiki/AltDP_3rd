"""Test Phase 22-7-2: RC Beam Pure White A4 Report Zero-Shear Dynamic Omission, Minimum Shear/Torsion KaTeX Checks.

Conforms to Requirement 22-7-2 & DOCS 07/14/16:
- Chapter 3: KDS 14 20 20 : 2022 phi_Mn >= 1.2 Mcr always rendered even with zero loads
- Chapter 5 Section 5.1.B: 3-Station minimum shear reinforcement and spacing summary table
- Chapter 5 Section 5.2: Dynamic 1-line simplification when factored shear Vu <= 0
- Chapter 5 Section 5.3: Mandatory independent KaTeX block for Av,min and s,max (never omitted)
- Chapter 5 Section 5.4: Minimum transverse (Av + 2At)min and longitudinal Al,min KaTeX derivation
- Chapter 7: Comprehensive final verdict table with Av,min, s,max, and Al,req DCR rows
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_chapter3_kds2022_min_flexure_always_rendered():
    """Verify Chapter 3 maintains KDS 14 20 20: 2022 phi_Mn >= 1.2 Mcr and is always rendered."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Verify Chapter 3 presence
    assert 'data-chapter-key="ductility"' in content
    assert 'Ductility Limit & Minimum Reinforcement Check' in content

    # Verify KDS 14 20 20 : 2022 4.2.2 standard formula
    assert r'\phi M_n \ge 1.2 M_{cr}' in content.replace('\\\\', '\\') or '1.2 M_{cr}' in content
    assert 'phiMnMin' in content
    assert 'dcrMin' in content

    # Ensure no legacy equation regression (0.25*sqrt(fck)/fy)
    assert '0.25 \\sqrt{f_{ck}} / f_y' not in content

    # Verify Section 3.4 End-J symmetry formula syntax (no quadruple backslash escaping bug)
    assert r'($\\\\phi M_n =' not in content
    assert '3.4 단부-J (End-J) 최소철근량 만족 및 연성파괴 유도 검토:' in content
    assert r'($\\phi M_n =' in content


def test_chapter5_zero_shear_dynamic_omission():
    """Verify Chapter 5.2 dynamically simplifies to 1-line summary when Vu <= 0."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Verify Vu <= 0 branch exists in Chapter 5.2
    assert 'governingShear.VuDemand <= 0' in content
    assert 'V_u = 0.0' in content or 'Vu = 0.0' in content
    assert '5.2' in content


def test_chapter5_min_shear_rebar_and_spacing_always_rendered():
    """Verify Section 5.1.B table and Section 5.3 KaTeX block for Av,min and s,max are mandatory."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Section 5.1.B summary table
    assert '5.1.B' in content
    assert 'AvMin' in content
    assert 'dcrAvMin' in content
    assert 'sMax' in content
    assert 'dcrSpacing' in content

    # Section 5.3 independent KaTeX block (mandatory, never omitted)
    assert '5.3' in content
    assert 'KDS 14 20 22 (4.3.3 & 4.3.4)' in content

    # KDS formulas in KaTeX
    assert '0.0625' in content
    assert '0.35' in content
    assert 'dcrAvMin' in content
    assert 'dcrSpacing' in content


def test_chapter5_torsion_min_rebar_katex():
    """Verify Section 5.4 contains minimum torsion rebar KaTeX formulas for (Av + 2At)min and Al,min."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Section 5.4 Torsion
    assert '5.4' in content
    assert 'isZeroTorsion' in content
    assert 'Av2AtMin' in content
    assert 'AlMin' in content
    assert 'AlReq' in content
    assert 'sMaxTorsion' in content

    # KaTeX formula terms
    assert 'Av2AtMin' in content
    assert 'AlMin' in content
    assert 'AlReq' in content


def test_chapter7_min_shear_and_torsion_rows_in_verdict():
    """Verify Chapter 7 executive summary table contains Av,min, s,max, and Al rows, and updates governingDcr."""
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # Rows in Chapter 7
    assert 'KDS 14 20 22 (4.3.3)' in content
    assert 'KDS 14 20 22 (4.3.4)' in content
    assert 'dcrAvMin' in content
    assert 'dcrSpacing' in content

    # Verification that governingDcr takes Av,min and s,max into account
    assert 'governingShear.dcrAvMin' in content
    assert 'governingShear.dcrSpacing' in content
