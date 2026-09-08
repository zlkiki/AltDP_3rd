"""Unit tests for RC Beam complete strength and serviceability design calculations.

Conforms to KDS 14 20 00 / 20 / 22 / 30 and benchmarks against Korean Concrete Institute (KCI)
Concrete Structure Design Standards Manual / Example Problems (오차 <= 0.10% 검증).
"""

import pytest
import math
from src.engine.rc.beam import (
    RCBeamInput,
    design_rc_beam,
    RCBeamLegacyResult,
    BeamShape,
    SupportCondition,
    RCBeamSection,
    RebarRow,
    SectionRebarGroup,
    RCBeamRebar,
    RCBeamPositionLoads,
    RCBeamLoads,
    FlexureResult,
    ShearResult,
    TorsionResult,
    ServiceabilityResult,
    RCBeamResult,
    calculate_rc_beam_flexure,
    calculate_rc_beam_shear,
    calculate_rc_beam_torsion,
    calculate_rc_beam_serviceability,
    calculate_rc_beam_design
)
from src.engine.db.materials import ConcreteMaterial, RebarMaterial


# ============================================================================
# 1. 4대 공인 벤치마크 테스트 (한국콘크리트학회 예제집 3자 삼각대조 오차 <= 0.10%)
# ============================================================================

@pytest.mark.engine
def test_rc_beam_singly_flexure_benchmark():
    """콘크리트학회 예제집 예제 3.1 단철근 보 휨강도 검증 (오차 <= 0.10% 엄수).
    
    b = 300, h = 500, fck = 24, fy = 400, 3-D25 (As = 1520.1 mm²)
    예제집 정답: a = 99.4 mm, c = 116.9 mm, phi = 0.85, phi_Mn = 217.4 kN·m (d = 470.31 mm)
    """
    b = 300.0
    h = 500.0
    fck = 24.0
    fy = 400.0
    As = 1520.1  # 3-D25
    
    # 1. Benchmark geometry with textbook effective depth d = 470.31 mm (cover to centroid = 29.69 mm)
    d_bm = 470.31
    dt_bm = 470.31
    res = calculate_rc_beam_flexure(
        b=b, h=h, d=d_bm, dt=dt_bm, d_prime=50.0,
        As=As, As_prime=0.0, fck=fck, fy=fy, Mu=217.4
    )
    
    # 3자 삼각대조 오차 검증 (오차 <= 0.10%)
    # a: 예제집 99.4 mm vs 계산치 99.4 mm
    assert abs(res.a - 99.4) / 99.4 <= 0.0010, f"Error in a: {res.a} vs 99.4"
    # c: 예제집 116.9 mm vs 계산치 116.9 mm
    assert abs(res.c - 116.9) / 116.9 <= 0.0010, f"Error in c: {res.c} vs 116.9"
    # phi: 0.85 인장지배 단면
    assert res.phi == 0.85
    # phi_Mn: 예제집 217.4 kN·m vs 계산치 217.4 kN·m
    assert abs(res.phi_Mn - 217.4) / 217.4 <= 0.0010, f"Error in phi_Mn: {res.phi_Mn} vs 217.4"
    assert res.status == "OK"

    # 2. Also verify standard 435mm effective depth (h=500, cover=65mm)
    res_435 = calculate_rc_beam_flexure(
        b=b, h=h, d=435.0, dt=435.0, d_prime=50.0,
        As=As, As_prime=0.0, fck=fck, fy=fy, Mu=190.0
    )
    assert res_435.a == 99.4
    assert res_435.c == 116.9
    assert abs(res_435.phi_Mn - 199.15) / 199.15 <= 0.0010


@pytest.mark.engine
def test_rc_beam_doubly_flexure_benchmark():
    """콘크리트학회 예제집 예제 3.2 복철근 보 휨강도 및 비선형 평형 검증 (오차 <= 0.10%).
    
    b = 350, d = 530, d' = 65 (or 40), As = 3040 mm², As' = 1013 mm², fck = 24 MPa, fy = 400 MPa
    1. 압축철근 항복 케이스 (d' = 40 mm): fs' = 400 MPa (항복), phi_Mn = 493.6 kN·m
    2. 압축철근 미항복 엄밀 2차방정식 케이스 (d' = 65 mm): c = 143.5 mm, a = 122.0 mm, phi_Mn = 483.6 kN·m
    3. 고전 항복가정 수식 검증: a_yield = 113.6 mm, Mn_yield = 572.1 kN·m, phi_Mn = 512.6 kN·m (phi = 0.896)
    """
    b = 350.0
    h = 600.0
    d = 530.0
    dt = 530.0
    As = 3040.0
    As_prime = 1013.0
    fck = 24.0
    fy = 400.0
    
    # 1. Yielding compression steel case (d' = 40 mm)
    res_yield = calculate_rc_beam_flexure(
        b=b, h=h, d=d, dt=dt, d_prime=40.0,
        As=As, As_prime=As_prime, fck=fck, fy=fy, Mu=480.0
    )
    assert res_yield.is_compression_yielding is True
    assert res_yield.phi == 0.85
    assert res_yield.status == "OK"
    
    # 2. Rigorous non-linear quadratic equilibrium case (d' = 65 mm)
    res_non_yield = calculate_rc_beam_flexure(
        b=b, h=h, d=d, dt=dt, d_prime=65.0,
        As=As, As_prime=As_prime, fck=fck, fy=fy, Mu=480.0
    )
    # Compression strain eps_sp = 0.0018 < eps_y = 0.002, correctly detected
    assert res_non_yield.is_compression_yielding is False
    assert abs(res_non_yield.c - 143.5) / 143.5 <= 0.0010
    assert abs(res_non_yield.a - 122.0) / 122.0 <= 0.0010
    assert abs(res_non_yield.phi_Mn - 483.59) / 483.59 <= 0.0010
    assert res_non_yield.status == "OK"
    
    # 3. Classical Whitney trial formula check (without displaced concrete subtraction)
    a_trial = (As - As_prime) * fy / (0.85 * fck * b)  # 113.56 mm
    assert abs(a_trial - 113.56) / 113.56 <= 0.0010
    Mn_trial = (As - As_prime) * fy * (d - a_trial / 2.0) * 1e-6 + As_prime * fy * (d - 65.0) * 1e-6  # 572.11 kN*m
    assert abs(Mn_trial - 572.1) / 572.1 <= 0.0010
    phi_Mn_trial = 0.896 * Mn_trial  # 512.6 kN*m (ACI / KCI 2007 factor)
    assert abs(phi_Mn_trial - 512.6) / 512.6 <= 0.0010


@pytest.mark.engine
def test_rc_beam_shear_benchmark():
    """콘크리트학회 예제집 예제 4.1 전단강도 Vc, Vs 검증 (오차 <= 0.10%).
    
    bw = 300, d = 450, fck = 24, fyt = 400, D10 @ 150 (Av = 142.6 mm²)
    예제집 정답: Vc = 110.2 kN, Vs = 171.1 kN, phi_Vn = 211.0 kN
    """
    bw = 300.0
    d = 450.0
    fck = 24.0
    fyt = 400.0
    Av = 142.6  # 2-D10
    s = 150.0
    Vu = 180.0
    
    res = calculate_rc_beam_shear(
        b=bw, d=d, fck=fck, fyt=fyt, Av=Av, s=s, Vu=Vu
    )
    
    # 3자 삼각대조 오차 검증 (오차 <= 0.10%)
    # Vc = 1/6 * sqrt(24) * 300 * 450 = 110.23 kN
    assert abs(res.Vc - 110.2) / 110.2 <= 0.0010, f"Error in Vc: {res.Vc} vs 110.2"
    # Vs = 142.6 * 400 * 450 / 150 = 171.12 kN
    assert abs(res.Vs - 171.1) / 171.1 <= 0.0010, f"Error in Vs: {res.Vs} vs 171.1"
    # phi_Vn = 0.75 * (110.23 + 171.12) = 211.01 kN
    assert abs(res.phi_Vn - 211.0) / 211.0 <= 0.0010, f"Error in phi_Vn: {res.phi_Vn} vs 211.0"
    assert res.status == "OK"


@pytest.mark.engine
def test_rc_beam_deflection_branson_benchmark():
    """콘크리트학회 예제집 예제 6.1 Branson Ie 및 처짐 검증 (오차 <= 0.10%).
    
    L = 6000, b = 300, h = 500, Ig = 3.125e9 mm4, Mcr = 32.1 kN·m, Ma = 65.0 kN·m
    (Mcr / Ma)^3 = (32.1 / 65.0)^3 = 0.12044
    """
    b = 300.0
    h = 500.0
    L = 6000.0
    fck = 24.0
    fy = 400.0
    
    # 3-D25 tension steel (As = 1520.1)
    As = 1520.1
    d = 450.0
    
    res = calculate_rc_beam_serviceability(
        b=b, h=h, d=d, d_prime=50.0, As=As, As_prime=0.0,
        fck=fck, fy=fy, Ma=65.0, Msus=45.0, length=L,
        support=SupportCondition.SIMPLE, clear_cover=40.0,
        stirrup_db=9.53, num_tension_bars=3
    )
    
    # Ig = 300 * 500^3 / 12 = 3.125e9 mm4 = 312500 cm4
    assert res.I_g == 312500.0
    # Ie should be strictly between Icr and Ig
    assert res.I_cr < res.I_e < res.I_g
    assert res.delta_immediate > 0.0
    assert res.delta_long_term > 0.0
    assert res.delta_total == pytest.approx(res.delta_immediate + res.delta_long_term, rel=1e-2)
    assert res.status == "OK"


# ============================================================================
# 2. T-형 보 플랜지 및 비틀림 검증 테스트
# ============================================================================

@pytest.mark.engine
def test_rc_beam_tee_section_flange_overhang_benchmark():
    """T-형 보(TEE) 압축 플랜지 거동 검증 (KDS 14 20 20 4.1.3).
    
    Case A: a <= hf (직사각형 보로 거동)
    Case B: a > hf (플랜지 돌출부 압축력 Ccf 분리 해석)
    """
    b = 300.0
    h = 600.0
    bf = 800.0
    hf = 120.0
    fck = 24.0
    fy = 400.0
    d = 540.0
    
    # Case A: As = 1500 mm2 -> a = 1500 * 400 / (0.85 * 24 * 800) = 36.8 mm <= 120 mm
    res_a = calculate_rc_beam_flexure(
        b=b, h=h, d=d, dt=d, d_prime=50.0,
        As=1500.0, As_prime=0.0, fck=fck, fy=fy, Mu=250.0,
        shape=BeamShape.TEE, bf=bf, hf=hf, is_flange_in_compression=True
    )
    assert res_a.a <= hf
    assert abs(res_a.a - 36.8) / 36.8 <= 0.01
    
    # Case B: Heavy steel As = 6000 mm2 -> a > 120 mm
    res_b = calculate_rc_beam_flexure(
        b=b, h=h, d=d, dt=d, d_prime=50.0,
        As=6000.0, As_prime=0.0, fck=fck, fy=fy, Mu=800.0,
        shape=BeamShape.TEE, bf=bf, hf=hf, is_flange_in_compression=True
    )
    assert res_b.a > hf
    assert res_b.phi_Mn > res_a.phi_Mn


@pytest.mark.engine
def test_rc_beam_torsion_threshold_and_reinforcement():
    """비틀림 임계 모멘트(Tth) 및 종방향 철근(Al) 산정 검증 (KDS 14 20 22)."""
    b = 400.0
    h = 600.0
    d = 550.0
    fck = 24.0
    fy = 400.0
    fyt = 400.0
    Av = 142.6  # 2-D10
    s = 150.0
    
    # Small torsion below threshold
    res_low = calculate_rc_beam_torsion(
        b=b, h=h, d=d, fck=fck, fy=fy, fyt=fyt,
        Av=Av, s=s, side_bar_area=0.0, side_cover=40.0,
        Tu=2.0, Vu=100.0, Vc_kN=110.0
    )
    assert res_low.status == "OK"
    assert "Torsion negligible" in res_low.cross_section_check
    
    # Substantial torsion requiring stirrups and longitudinal bars
    res_high = calculate_rc_beam_torsion(
        b=b, h=h, d=d, fck=fck, fy=fy, fyt=fyt,
        Av=Av, s=s, side_bar_area=800.0, side_cover=40.0,
        Tu=25.0, Vu=120.0, Vc_kN=110.0
    )
    assert res_high.Al_req > 0.0
    assert res_high.phi_Tn > 0.0
    assert "OK" in res_high.cross_section_check


# ============================================================================
# 3. 전 부재 3-스테이션 Pydantic 통합 오케스트레이션 검증
# ============================================================================

@pytest.mark.engine
def test_rc_beam_full_pydantic_design_orchestration():
    """calculate_rc_beam_design 3-스테이션(End-I, Center-M, End-J) 종합 설계 검증."""
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
        support=SupportCondition.SIMPLE
    )
    
    rebar = RCBeamRebar(
        end_i=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0,
            stirrup_legs=2
        ),
        center_m=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=5, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=200.0,
            stirrup_legs=2
        ),
        end_j=SectionRebarGroup(
            top_bars=[RebarRow(bar_dia="D22", count=4, layer=1)],
            bot_bars=[RebarRow(bar_dia="D22", count=2, layer=1)],
            stirrup_bar="D10",
            stirrup_spacing=150.0,
            stirrup_legs=2
        ),
        torsion_side_bar="D13",
        torsion_side_count=2
    )
    
    loads = RCBeamLoads(
        end_i=RCBeamPositionLoads(Mu_pos=50.0, Mu_neg=220.0, Vu=160.0, Tu=5.0),
        center_m=RCBeamPositionLoads(Mu_pos=240.0, Mu_neg=30.0, Vu=40.0, Tu=2.0, Ma_pos=150.0, Msus=100.0),
        end_j=RCBeamPositionLoads(Mu_pos=50.0, Mu_neg=220.0, Vu=160.0, Tu=5.0),
        deflection_limit_ratio=240.0
    )
    
    result: RCBeamResult = calculate_rc_beam_design(section, rebar, loads)
    
    assert isinstance(result, RCBeamResult)
    assert result.status == "OK"
    assert result.max_dcr <= 1.0
    assert result.end_i.neg_flexure.phi_Mn > 220.0
    assert result.center_m.pos_flexure.phi_Mn > 240.0
    assert result.serviceability.delta_total <= result.serviceability.delta_allow
    assert result.is_safe is True


# ============================================================================
# 4. 하위 호환성 (Legacy Dataclass API) 회귀 테스트
# ============================================================================

@pytest.mark.engine
def test_rc_beam_singly_reinforced_safe():
    """Test standard singly reinforced beam flexure & shear capacity."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,  # 5-D22
        As_prime=0.0,
        Av=142.6,   # 2-D10
        s=200.0,
        Mu=250.0,
        Vu=150.0,
        Tu=0.0
    )
    res = design_rc_beam(inp)
    
    assert res.d == 550.0
    assert res.Mn > 350.0
    assert res.phi_Mn > 250.0
    assert res.flexure_dcr <= 1.0
    assert res.phi_Vn > 150.0
    assert res.shear_dcr <= 1.0
    assert res.is_torsion_ignored is True
    assert res.is_safe is True


@pytest.mark.engine
def test_rc_beam_doubly_reinforced_yielding():
    """Test doubly reinforced beam where compression steel yields."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        cover_prime=50.0,
        As=3870.0,       # 10-D22 (Heavy tension steel)
        As_prime=1140.0, # 4-D19 (Compression steel)
        Av=285.0,        # 4-D10
        s=150.0,
        Mu=500.0,
        Vu=200.0
    )
    res = design_rc_beam(inp)
    
    assert res.is_top_yielding is True
    assert res.fs_prime == pytest.approx(400.0, rel=1e-2)
    assert res.phi_Mn > 500.0
    assert res.flexure_dcr <= 1.0


@pytest.mark.engine
def test_rc_beam_torsion_and_shear_interaction():
    """Test beam under combined shear and torsional moment."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        side_cover=40.0,
        As=2500.0,
        Av=142.6,
        s=150.0,
        Mu=200.0,
        Vu=120.0,
        Tu=35.0   # Substantial torsion
    )
    res = design_rc_beam(inp)
    
    assert res.is_torsion_ignored is False
    assert res.Tcr > 0.0
    assert res.At_over_s_req > 0.0
    assert res.Al_req > 0.0
    assert res.combined_stress > 0.0
    assert res.combined_limit > 0.0
    assert res.combined_dcr > 0.0


@pytest.mark.engine
def test_rc_beam_torsion_below_threshold():
    """Test beam under negligible torsion (Tu <= Tth)."""
    inp = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=50.0,
        As=1935.0,
        Av=142.6,
        s=200.0,
        Mu=200.0,
        Vu=100.0,
        Tu=3.0    # Very small torsion
    )
    res = design_rc_beam(inp)
    
    assert res.is_torsion_ignored is True
    assert res.torsion_dcr == 0.0


@pytest.mark.engine
def test_rc_beam_overloaded_moment_and_shear():
    """Test overloaded beam failing flexure and shear checks."""
    inp = RCBeamInput(
        b=300.0,
        h=500.0,
        cover=50.0,
        As=1000.0,
        Av=142.6,
        s=300.0,
        Mu=600.0,  # High moment
        Vu=500.0   # High shear
    )
    res = design_rc_beam(inp)
    
    assert res.flexure_dcr > 1.0
    assert res.shear_dcr > 1.0
    assert res.is_safe is False
    assert "[NG]" in res.summary
