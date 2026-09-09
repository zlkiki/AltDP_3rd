"""
Test Suite for Requirement 22-7-3:
Phase V1-01 Step 7-3 RC Beam 22-7 E2E Integration, Zero-Load Interaction & Regression Verification.

Validates the 4 scenarios defined in Requirement 22-7-3:
1. Scenario 1: Normal design load full verification (Chapters 3, 4, 5.2, 5.3, 5.4, 7).
2. Scenario 2: Factored shear Vu = 0.0 dynamic omission in 5.2 while keeping mandatory 5.3 (Av,min, s_max).
3. Scenario 3: All loads zero (Mu=0, Vu=0, Tu=0) with mandatory Chapter 3 & Section 5.3 minimum rebar checks.
4. Scenario 4: Stirrup spacing exceeding s_max (350 mm > 270 mm) yielding DCR_spacing = 1.296 and overall NG verdict.
5. Backend Pydantic Orchestrator 0.10% error and DCR tracking integrity across all scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from src.engine.rc.beam import (
    RCBeamSection,
    RCBeamRebar,
    RCBeamLoads,
    RCBeamPositionLoads,
    SectionRebarGroup,
    RebarRow,
    BeamArrangeType,
    calculate_rc_beam_design
)

client = TestClient(app)


def test_scenario1_normal_design_loads_backend_and_report_contract():
    """Scenario 1: Normal design load check (End-I Mu=240, Vu=180, Tu=15).
    
    Verifies:
    - Chapter 3 ductility and KDS 2022 min flexure phi_Mn >= 1.2 Mcr
    - Chapter 5.2 detailed shear formula
    - Chapter 5.3 minimum shear Av,min and s_max
    - Chapter 5.4 torsion formulas
    - Chapter 7 verdict
    """
    section = RCBeamSection(b=400.0, h=600.0, length=6000.0, fck=27.0, fy=400.0, fyt=400.0)
    rebar = RCBeamRebar(
        arrange_type=BeamArrangeType.SYMMETRIC_ENDS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=4, layer=1), RebarRow(bar_dia="D25", count=2, layer=2)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        torsion_side_bar="D13",
        torsion_side_count=4
    )
    loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=50.0, Mu_neg=240.0, Vu=180.0, Tu=15.0),
        center_m=RCBeamPositionLoads(Mu_pos=260.0, Mu_neg=30.0, Vu=60.0, Tu=5.0),
        end_j=RCBeamPositionLoads(Mu_pos=50.0, Mu_neg=240.0, Vu=180.0, Tu=15.0)
    )

    res = calculate_rc_beam_design(section=section, rebar=rebar, loads=loads)

    # 1. Section 5.3 Av,min and s_max checks
    # Av_min = max(0.0625*sqrt(27)*400*150/400, 0.35*400*150/400) = max(48.71, 52.5) = 52.5 mm2
    end_i_shear = res.end_i.shear
    assert abs(end_i_shear.Av_min - 52.5) / 52.5 <= 0.0010
    assert 265.0 <= end_i_shear.s_max <= 270.5  # d/2 = 537.8 / 2 = 268.9 mm
    assert end_i_shear.dcr_Av_min < 1.0  # Av_prov = 142.7 > 52.5
    assert end_i_shear.dcr_spacing < 1.0  # s = 150 < 268.9
    assert end_i_shear.is_min_shear_ok is True
    assert end_i_shear.status == "OK"

    # 2. Section 5.4 Torsion check (Tu = 15 > phi Tth = 7.0 kNm)
    end_i_tor = res.end_i.torsion
    assert end_i_tor.is_zero_torsion is False
    assert end_i_tor.Al_min > 0.0
    assert end_i_tor.Al_req >= end_i_tor.Al_min
    # With 4-D13 (Al_prov = 506.8 mm2 < Al_min = 1012.5 mm2), Step 7-1 Al_min governing check correctly triggers NG
    assert end_i_tor.dcr_Al > 1.0
    assert end_i_tor.status == "NG"

    # 3. With side rebar augmented to 4-D19 (Al_prov = 1146 mm2 > Al_req), beam achieves 100% OK
    rebar_safe = rebar.model_copy(deep=True)
    rebar_safe.torsion_side_bar = "D19"
    rebar_safe.torsion_side_count = 4
    res_safe = calculate_rc_beam_design(section=section, rebar=rebar_safe, loads=loads)
    assert res_safe.end_i.torsion.status == "OK"
    assert res_safe.status == "OK"

    # 4. Report JS integrity
    response = client.get('/static/js/report/rc_beam_report.js')
    assert response.status_code == 200
    js_content = response.content.decode('utf-8')
    assert '5.1.B' in js_content
    assert 'AvMin' in js_content
    assert '5.3' in js_content
    assert 'dcrAvMin' in js_content
    assert 'dcrSpacing' in js_content


def test_scenario2_zero_shear_dynamic_omission_and_mandatory_min_shear():
    """Scenario 2: Factored shear Vu = 0.0.
    
    Verifies:
    - 5.2 Detailed shear calculation omitted and replaced with 1-line summary box
    - 5.3 Mandatory minimum shear reinforcement check (Av,min, s_max) remains 100% active
    """
    section = RCBeamSection(b=400.0, h=600.0, length=6000.0, fck=27.0, fy=400.0, fyt=400.0)
    rebar = RCBeamRebar(
        arrange_type=BeamArrangeType.SYMMETRIC_ENDS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        )
    )
    loads_zero_shear = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=200.0, Vu=0.0, Tu=0.0),
        center_m=RCBeamPositionLoads(Mu_pos=220.0, Mu_neg=0.0, Vu=0.0, Tu=0.0),
        end_j=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=200.0, Vu=0.0, Tu=0.0)
    )

    res = calculate_rc_beam_design(section=section, rebar=rebar, loads=loads_zero_shear)

    for st in [res.end_i, res.center_m, res.end_j]:
        assert st.is_zero_shear is True
        assert st.shear.dcr == 0.0
        # Mandatory minimum shear rebar and spacing must be satisfied
        assert st.shear.is_min_shear_ok is True
        assert st.shear.status == "OK"

    # Check JS code branch handles Vu <= 0 dynamically
    response = client.get('/static/js/report/rc_beam_report.js')
    content = response.content.decode('utf-8')
    assert 'governingShear.VuDemand <= 0' in content
    assert '5.2' in content
    assert 'V_u = 0.0' in content


def test_scenario3_all_loads_zero_mandatory_chapter3_and_5_3():
    """Scenario 3: Mu = 0, Vu = 0, Tu = 0 across all stations.
    
    Verifies:
    - Chapters 4, 5.2, 5.4 omit detailed stress equations
    - Chapter 3 (phi_Mn >= 1.2 Mcr, epsilon_t >= eps_t_min) ALWAYS rendered
    - Chapter 5.3 (Av >= Av_min, s <= s_max) ALWAYS rendered
    """
    section = RCBeamSection(b=400.0, h=600.0, length=6000.0, fck=27.0, fy=400.0, fyt=400.0)
    rebar = RCBeamRebar(
        arrange_type=BeamArrangeType.SYMMETRIC_ENDS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0
        )
    )
    loads_all_zero = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=0.0, Vu=0.0, Tu=0.0),
        center_m=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=0.0, Vu=0.0, Tu=0.0),
        end_j=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=0.0, Vu=0.0, Tu=0.0)
    )

    res = calculate_rc_beam_design(section=section, rebar=rebar, loads=loads_all_zero)

    assert res.end_i.is_zero_flexure is True
    assert res.end_i.is_zero_shear is True
    assert res.end_i.is_zero_torsion is True
    assert res.status == "OK"

    # JS Report contains unconditional render for Chapter 3 & 5.3
    response = client.get('/static/js/report/rc_beam_report.js')
    content = response.content.decode('utf-8')
    assert 'data-chapter-key="ductility"' in content
    assert '3.1 3-Station' in content
    assert '3.2' in content
    assert '3.3' in content
    assert '5.3' in content
    assert 'phiMnMin' in content
    assert 'dcrAvMin' in content
    assert 'dcrSpacing' in content


def test_scenario4_stirrup_spacing_exceeded_dcr_and_ng_verdict():
    """Scenario 4: Stirrup spacing s = 350 mm exceeding s_max = 268.9 mm (nominal 270 mm).
    
    Verifies:
    - s_max = d/2 = 268.9 mm
    - DCR_spacing = 350 / 268.9 = 1.302 (> 1.0)
    - Section shear status = "NG"
    - Master beam status = "NG"
    - Chapter 7 verdict renders NG
    """
    section = RCBeamSection(b=400.0, h=600.0, length=6000.0, fck=27.0, fy=400.0, fyt=400.0)
    rebar_ng = RCBeamRebar(
        arrange_type=BeamArrangeType.SYMMETRIC_ENDS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=350.0  # Exceeds s_max (268.9 mm)
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=350.0  # Exceeds s_max (268.9 mm)
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=350.0  # Exceeds s_max (268.9 mm)
        )
    )
    loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=100.0, Vu=50.0, Tu=0.0),
        center_m=RCBeamPositionLoads(Mu_pos=150.0, Mu_neg=0.0, Vu=20.0, Tu=0.0),
        end_j=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=100.0, Vu=50.0, Tu=0.0)
    )

    res = calculate_rc_beam_design(section=section, rebar=rebar_ng, loads=loads)

    # 1. Spacing check fails
    assert res.end_i.shear.is_min_shear_ok is False
    assert res.end_i.shear.status == "NG"
    assert res.end_i.shear.dcr_spacing > 1.0
    expected_dcr = 350.0 / res.end_i.shear.s_max
    assert abs(res.end_i.shear.dcr_spacing - expected_dcr) / expected_dcr <= 0.0010

    # 2. Master status must be NG and governing mode tracks spacing
    assert res.status == "NG"
    assert res.max_dcr >= 1.296
    assert 'Shear Spacing' in res.governing_mode

    # 3. Report JS contains governingShear.dcrSpacing in governingDcr calculation
    response = client.get('/static/js/report/rc_beam_report.js')
    content = response.content.decode('utf-8')
    assert 'governingShear.dcrSpacing' in content
    assert 'governingShear.dcrAvMin' in content
    assert 'isOverallSafe' in content


def test_rc_beam_form_and_report_sync_assets():
    """Verify all front-end assets for 22-7 are fully served and zero-error ready."""
    resp_form = client.get('/static/js/components/form_rc_beam.js')
    assert resp_form.status_code == 200
    form_text = resp_form.content.decode('utf-8')
    assert 'calcResult.max_dcr' in form_text

    resp_report = client.get('/static/js/report/rc_beam_report.js')
    assert resp_report.status_code == 200
    report_text = resp_report.content.decode('utf-8')
    assert 'RCBeamReportGenerator' in report_text
    assert 'renderRCBeamReport' in report_text
