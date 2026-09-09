"""Unit tests for RC Beam Serviceability (Deflection, Crack) and Auto-Design Rebar Layout."""

import pytest
import math
from src.engine.rc.beam import (
    RCBeamInput,
    design_rc_beam,
    RCBeamSection,
    RCBeamRebar,
    RCBeamLoads,
    RCBeamPositionLoads,
    RCBeamResult,
    SectionRebarGroup,
    RebarRow,
    BeamShape,
    SupportCondition,
    BeamArrangeType,
    calculate_rc_beam_design,
    calculate_rc_beam_serviceability,
    check_crack_bar_spacing,
    calculate_cracked_section_properties,
    calculate_effective_moment_of_inertia
)
from src.engine.rc.rebar_layout import (
    REBAR_DB,
    calculate_bar_spacing_capacity,
    create_rebar_arrangement,
    auto_design_beam_rebar
)


@pytest.mark.engine
def test_rc_beam_branson_effective_inertia_and_deflection():
    """Verify Branson Ie, elastic deflection, and long-term deflection."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,  # 5-D22
        As_prime=0.0,
        Mu=250.0,
        Vu=120.0,
        Ma=140.0,   # Service moment > Mcr
        span_length=6000.0, # 6m span
        sustained_ratio=0.7,
        time_duration_months=60
    )
    res = design_rc_beam(inp)
    
    assert res.Ig > res.Icr
    assert res.Icr <= res.Ie <= res.Ig
    assert res.Mcr > 0.0
    assert res.delta_elastic > 0.0
    assert res.lambda_delta == pytest.approx(2.0, rel=1e-2)  # xi = 2.0 for 5 years, rho_prime = 0
    assert res.delta_long > 0.0
    assert res.delta_total == pytest.approx(res.delta_elastic + res.delta_long, rel=1e-3)
    assert res.delta_allowable == 6000.0 / 240.0  # 25.0 mm
    assert res.deflection_dcr < 1.0


@pytest.mark.engine
def test_rc_beam_crack_width():
    """Verify crack width calculation."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=40.0,
        As=1935.0,
        Ma=160.0,
        w_lim=0.3
    )
    res = design_rc_beam(inp)
    
    assert res.fs_service > 0.0
    assert 0.02 <= res.crack_width <= 0.35
    assert res.crack_dcr > 0.0


@pytest.mark.engine
def test_rebar_layout_single_layer():
    """Test 1-layer rebar spacing and arrangement."""
    max_bars, clear_spacing = calculate_bar_spacing_capacity(
        b=400.0,
        bar_size="D22",
        cover=40.0,
        stirrup_db=9.53,
        max_aggregate=25.0
    )
    # Clear width = 400 - 2*(40+9.53) = 300.94mm
    # Min clear spacing = max(25, 22.2, 33.25) = 33.25mm
    # max_bars = floor((300.94 + 33.25) / (22.2 + 33.25)) = floor(334.19 / 55.45) = 6
    assert max_bars >= 4
    
    arr = create_rebar_arrangement(
        b=400.0,
        h=600.0,
        bar_size="D22",
        num_bars=4,
        cover=40.0
    )
    assert arr.is_valid is True
    assert arr.num_layers == 1
    assert len(arr.layers[0].x_coords) == 4
    assert arr.layers[0].clear_spacing >= 33.0


@pytest.mark.engine
def test_rebar_layout_two_layers():
    """Test 2-layer rebar division when bar count exceeds single layer capacity."""
    arr = create_rebar_arrangement(
        b=300.0,
        h=600.0,
        bar_size="D25",
        num_bars=6,  # 6-D25 in b=300 requires 2 layers
        cover=40.0
    )
    assert arr.num_layers == 2
    assert len(arr.layers) == 2
    assert arr.layers[0].num_bars + arr.layers[1].num_bars == 6
    assert arr.effective_d < 600.0 - 50.0  # Centroid raised due to 2 layers


@pytest.mark.engine
def test_auto_design_beam_rebar():
    """Test automatic optimal rebar design selection."""
    As_req = 1800.0  # mm2
    result = auto_design_beam_rebar(
        b=400.0,
        h=600.0,
        As_req=As_req,
        cover=40.0,
        stirrup_size="D10"
    )
    assert result.selected_arrangement is not None
    assert result.selected_arrangement.total_area >= As_req
    assert result.selected_arrangement.is_valid is True
    assert len(result.all_candidates) > 0


# ============================================================================
# KDS 14 20 30 사용성 확장 및 공인 예제집 벤치마크 테스트 (요구사항 22-5-1)
# ============================================================================

@pytest.mark.engine
def test_kci2020_pdf_benchmark_crack_spacing_ex3_2():
    """콘크리트구조 학회기준 예제집(2020) 제3장 예제 3.2 벤치마크 검증 (PDF p.44-45).
    
    설계 조건:
    - 폭 b = 500 mm, fy = 400 MPa, 피복 cc = 50 mm, 건조환경 (k_cr = 280)
    - 스터럽: D10, 주근: 2-D35 또는 4-D25
    - fs 근사식: fs = (2/3) * fy = 266.67 MPa
    
    예제집 원문 정답:
    - 허용 최대 간격:
      s_max = 375 * (280 / 266.67) - 2.5 * 50 = 393.75 - 125 = 268.75 mm -> 269 mm
      (상한 300 * (280 / 266.67) = 315 mm > 269 mm 이므로 269 mm 지배)
    - 2-D35 사용 시 (n=2, db=35.8 mm):
      실제 중심간격 s_actual = 500 - 2 * (50 + 35.8 / 2) = 364.2 mm > 269 mm -> 부적합 (NG)
    - 4-D25 사용 시 (n=4, db=25.4 mm):
      실제 중심간격 s_actual = (500 - 2 * (50 + 25.4 / 2)) / 3 = 124.87 mm -> 125 mm < 269 mm -> 적합 (OK)
    """
    # 1. 2-D35 배근 검토 (NG 케이스)
    bars_2d35 = [RebarRow(bar_dia="D35", count=2, layer=1)]
    check_2d35 = check_crack_bar_spacing(
        station_name="center_m",
        rebar_pos="BOTTOM",
        b=500.0,
        d=540.0,
        kd=173.0,
        As=1913.0,
        fy=400.0,
        Ma_kNm=0.0,  # 0 입력 시 폴백 (2/3) * fy 적용
        clear_cover=40.0,
        stirrup_db=10.0,  # cc = clear_cover + stirrup_db = 50.0 mm
        bars=bars_2d35,
        k_cr=280.0
    )
    
    # s_max: 268.8 mm vs 269 mm (오차 <= 0.10%)
    assert abs(check_2d35.s_max - 268.8) <= 0.5
    assert check_2d35.cc == 50.0
    assert abs(check_2d35.fs - 266.7) <= 0.5
    # s_actual: 364.2 mm vs 365 mm
    assert abs(check_2d35.s_actual - 364.2) <= 0.5
    assert check_2d35.is_ok is False
    assert check_2d35.dcr > 1.0
    
    # 2. 4-D25 배근 검토 (OK 케이스)
    bars_4d25 = [RebarRow(bar_dia="D25", count=4, layer=1)]
    check_4d25 = check_crack_bar_spacing(
        station_name="center_m",
        rebar_pos="BOTTOM",
        b=500.0,
        d=540.0,
        kd=173.0,
        As=2027.0,
        fy=400.0,
        Ma_kNm=0.0,
        clear_cover=40.0,
        stirrup_db=10.0,
        bars=bars_4d25,
        k_cr=280.0
    )
    
    # s_max: 268.8 mm
    assert abs(check_4d25.s_max - 268.8) <= 0.5
    # s_actual: 124.9 mm vs 125 mm (오차 <= 0.10%)
    assert abs(check_4d25.s_actual - 124.9) <= 0.5
    assert check_4d25.is_ok is True
    assert check_4d25.dcr < 1.0
    
    # 3. 기타 환경 (k_cr = 210) 검증
    # s_max = 375 * (210 / 266.67) - 2.5 * 50 = 295.31 - 125 = 170.3 mm
    check_wet = check_crack_bar_spacing(
        station_name="center_m",
        rebar_pos="BOTTOM",
        b=500.0,
        d=540.0,
        kd=173.0,
        As=2027.0,
        fy=400.0,
        Ma_kNm=0.0,
        clear_cover=40.0,
        stirrup_db=10.0,
        bars=bars_4d25,
        k_cr=210.0
    )
    assert abs(check_wet.s_max - 170.3) <= 0.5
    assert check_wet.is_ok is True  # 124.9 mm < 170.3 mm


@pytest.mark.engine
def test_kci2020_pdf_benchmark_deflection_ex3_1_weighted_average():
    """KCI 2020 예제집 제3장 예제 3.1 기반 지점조건별 Branson Ie 가중평균 검증 (KDS 14 20 30 4.2.1).
    
    보 경간 L = 8000 mm, b = 400 mm, h = 600 mm, d = 535 mm, d' = 65 mm
    fck = 28 MPa, fy = 400 MPa, As = 1521 mm² (3-D25), As' = 1521 mm² (3-D25)
    
    단면 특성:
    - Ig = 7.20e9 mm4 = 720000 cm4
    - Mcr = 80.0 kN·m
    - Icr = 2.18e9 mm4 = 218000 cm4 (단면해석치 217901 cm4)
    - 중앙부 정모멘트 Ma = 120 kN·m:
      Ie_m = (80/120)^3 * 7.2e9 + [1 - (80/120)^3] * 2.179e9 = 3.667e9 mm4 = 366700 cm4
    - 단부 부모멘트 Ma = 140 kN·m:
      Ie_end = (80/140)^3 * 7.2e9 + [1 - (80/140)^3] * 2.179e9 = 3.115e9 mm4 = 311500 cm4
    """
    Ig, Icr, Mcr, kd, n = calculate_cracked_section_properties(
        b=400.0, h=600.0, d=535.0, d_prime=65.0,
        As=1521.0, As_prime=1521.0, fck=28.0
    )
    
    # 3자 삼각대조 1: 단면 기본값 오차 <= 0.10%
    assert abs(Ig / 1e4 - 720000.0) / 720000.0 <= 0.0010
    assert abs(Mcr - 80.0) / 80.0 <= 0.0010
    assert abs(Icr / 1e4 - 218000.0) / 218000.0 <= 0.0010
    
    # Ie 계산
    Ie_m = calculate_effective_moment_of_inertia(Ig, Icr, Mcr, 120.0)
    Ie_end = calculate_effective_moment_of_inertia(Ig, Icr, Mcr, 140.0)
    
    assert abs(Ie_m / 1e4 - 366741.0) / 366741.0 <= 0.0010
    assert abs(Ie_end / 1e4 - 311504.0) / 311504.0 <= 0.0010
    
    # 3자 삼각대조 2: 지점조건별 가중평균 Ie_avg 검증 (KDS 14 20 30 4.2.1(4))
    # 1) 단순지지: Ie_avg = Ie_m
    Ie_avg_simple = Ie_m
    assert abs(Ie_avg_simple / 1e4 - 366741.0) / 366741.0 <= 0.0010
    
    # 2) 양단연속: Ie_avg = 0.50 * Ie_m + 0.25 * (Ie_1 + Ie_2)
    #    0.50 * 366741 + 0.25 * (311504 + 311504) = 183370.5 + 155752 = 339122.5 cm4
    Ie_avg_both = 0.50 * Ie_m + 0.25 * (Ie_end + Ie_end)
    assert abs(Ie_avg_both / 1e4 - 339122.5) / 339122.5 <= 0.0010
    
    # 3) 1단연속: Ie_avg = 0.85 * Ie_m + 0.15 * Ie_cont
    #    0.85 * 366741 + 0.15 * 311504 = 311729.85 + 46725.6 = 358455.45 cm4
    Ie_avg_one = 0.85 * Ie_m + 0.15 * Ie_end
    assert abs(Ie_avg_one / 1e4 - 358455.5) / 358455.5 <= 0.0010
    
    # 4) 캔틸레버: Ie_avg = Ie_fixed = Ie_end
    Ie_avg_cant = Ie_end
    assert abs(Ie_avg_cant / 1e4 - 311504.0) / 311504.0 <= 0.0010


@pytest.mark.engine
def test_rc_beam_3station_crack_spacing_checks_and_elastic_fs():
    """탄성 균열단면해석 기반 fs 직접 산출 및 3-Station 각 단면별 균열방지 간격 전수 검증."""
    section = RCBeamSection(
        shape=BeamShape.RECTANGULAR,
        b=400.0,
        h=600.0,
        length=8000.0,
        cover=40.0,
        cover_top=40.0,
        fck=28.0,
        fy=400.0,
        fyt=400.0,
        support=SupportCondition.CONTINUOUS_BOTH
    )
    
    rebar = RCBeamRebar(
        arrange_type=BeamArrangeType.THREE_STATIONS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0,
            stirrup_legs=2
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=200.0,
            stirrup_legs=2
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D25", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D25", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0,
            stirrup_legs=2
        ),
        torsion_side_bar="D13",
        torsion_side_count=2
    )
    
    loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=30.0, Mu_neg=200.0, Vu=150.0, Tu=0.0, Ma_neg=120.0),
        center_m=RCBeamPositionLoads(Mu_pos=220.0, Mu_neg=20.0, Vu=40.0, Tu=0.0, Ma_pos=130.0, Msus=90.0),
        end_j=RCBeamPositionLoads(Mu_pos=30.0, Mu_neg=190.0, Vu=140.0, Tu=0.0, Ma_neg=110.0),
        deflection_limit_ratio=240.0
    )
    
    result: RCBeamResult = calculate_rc_beam_design(section, rebar, loads)
    
    assert isinstance(result, RCBeamResult)
    checks = result.serviceability.crack_spacing_checks
    assert "end_i" in checks
    assert "center_m" in checks
    assert "end_j" in checks
    
    # End-I (상부인장): Ma = 120 kN·m
    chk_i = checks["end_i"]
    assert chk_i.rebar_pos == "TOP"
    assert 0.0 < chk_i.fs <= 400.0
    assert chk_i.s_actual > 0.0
    assert chk_i.s_max > 0.0
    assert chk_i.dcr == pytest.approx(chk_i.s_actual / chk_i.s_max, rel=1e-2)
    
    # Center-M (하부인장): Ma = 130 kN·m
    chk_m = checks["center_m"]
    assert chk_m.rebar_pos == "BOTTOM"
    assert 0.0 < chk_m.fs <= 400.0
    assert chk_m.s_actual > 0.0
    assert chk_m.s_max > 0.0
    assert chk_m.dcr == pytest.approx(chk_m.s_actual / chk_m.s_max, rel=1e-2)
    
    # End-J (상부인장): Ma = 110 kN·m
    chk_j = checks["end_j"]
    assert chk_j.rebar_pos == "TOP"
    assert 0.0 < chk_j.fs <= 400.0
    
    # 가중평균 Ie_avg가 ServiceabilityResult에 포함되었는지 확인
    assert result.serviceability.Ie_avg > 0.0
    assert result.serviceability.Ie_mid > 0.0
    assert result.serviceability.Ie_end_i > 0.0
    assert result.serviceability.Ie_end_j > 0.0
    assert result.serviceability.support_condition == "CONT_BOTH"


@pytest.mark.engine
def test_rc_beam_zero_load_flags_and_schema():
    """계수하중 0(Tu=0, Mu=0, Vu=0) 입력 시 0하중 플래그 및 모델 반환 무결성 검증."""
    section = RCBeamSection(
        shape=BeamShape.RECTANGULAR,
        b=400.0,
        h=600.0,
        length=6000.0,
        cover=40.0,
        cover_top=40.0,
        fck=24.0,
        fy=400.0,
        fyt=400.0,
        support=SupportCondition.SIMPLE
    )
    
    rebar = RCBeamRebar(
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=3, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=3, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=200.0,
            stirrup_legs=2
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=200.0,
            stirrup_legs=2
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=3, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=3, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=200.0,
            stirrup_legs=2
        )
    )
    
    # 모든 계수하중 0 입력
    zero_loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=0.0, Vu=0.0, Tu=0.0),
        center_m=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=0.0, Vu=0.0, Tu=0.0),
        end_j=RCBeamPositionLoads(Mu_pos=0.0, Mu_neg=0.0, Vu=0.0, Tu=0.0),
        deflection_limit_ratio=240.0
    )
    
    result: RCBeamResult = calculate_rc_beam_design(section, rebar, zero_loads)
    
    assert isinstance(result, RCBeamResult)
    assert result.status == "OK"
    assert result.max_dcr == 0.0
    
    # 0하중 플래그 무결성 확인
    for st_name, st_res in [("end_i", result.end_i), ("center_m", result.center_m), ("end_j", result.end_j)]:
        assert st_res.is_zero_flexure is True
        assert st_res.is_zero_shear is True
        assert st_res.is_zero_torsion is True
        assert st_res.pos_flexure.is_zero_flexure is True
        assert st_res.neg_flexure.is_zero_flexure is True
        assert st_res.shear.is_zero_shear is True
        assert st_res.torsion.is_zero_torsion is True
        assert st_res.pos_flexure.dcr == 0.0
        assert st_res.neg_flexure.dcr == 0.0
        assert st_res.shear.dcr == 0.0
        assert st_res.torsion.dcr == 0.0


@pytest.mark.engine
def test_rc_beam_arrange_type_linkage():
    """배근 유형(ONE_SECTION, SYMMETRIC_ENDS, THREE_STATIONS)별 사용성 및 간격검토 연동 검증."""
    section = RCBeamSection(
        shape=BeamShape.RECTANGULAR,
        b=400.0,
        h=600.0,
        length=6000.0,
        cover=40.0,
        cover_top=40.0,
        fck=27.0,
        fy=400.0,
        fyt=400.0,
        support=SupportCondition.CONTINUOUS_BOTH
    )
    
    loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_neg=150.0, Vu=100.0, Ma_neg=90.0),
        center_m=RCBeamPositionLoads(Mu_pos=180.0, Vu=30.0, Ma_pos=110.0, Msus=70.0),
        end_j=RCBeamPositionLoads(Mu_neg=150.0, Vu=100.0, Ma_neg=90.0)
    )
    
    # 1. ONE_SECTION 배근
    rebar_one = RCBeamRebar(
        arrange_type=BeamArrangeType.ONE_SECTION,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=4, layer=1)]
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=4, layer=1)]
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=4, layer=1)]
        )
    )
    res_one = calculate_rc_beam_design(section, rebar_one, loads)
    assert "center_m" in res_one.serviceability.crack_spacing_checks
    assert res_one.serviceability.Ie_end_i == res_one.serviceability.Ie_mid
    assert res_one.serviceability.Ie_end_j == res_one.serviceability.Ie_mid
    
    # 2. SYMMETRIC_ENDS 배근
    rebar_sym = RCBeamRebar(
        arrange_type=BeamArrangeType.SYMMETRIC_ENDS,
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)]
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=4, layer=1)]
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)]
        )
    )
    res_sym = calculate_rc_beam_design(section, rebar_sym, loads)
    assert "end_i" in res_sym.serviceability.crack_spacing_checks
    assert "center_m" in res_sym.serviceability.crack_spacing_checks
    assert "end_j" in res_sym.serviceability.crack_spacing_checks
    # End-J mirrors End-I
    assert res_sym.serviceability.Ie_end_j == res_sym.serviceability.Ie_end_i
    assert res_sym.serviceability.crack_spacing_checks["end_j"].s_max == res_sym.serviceability.crack_spacing_checks["end_i"].s_max

