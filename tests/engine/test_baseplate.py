"""강구조 주각부 베이스플레이트 및 앵커볼트 엔진 테스트 (KDS 14 31 25 / KDS 14 20 54)"""

import pytest
from src.engine.steel.baseplate import (
    AnchorType,
    AnchorBoltInput,
    BasePlateInput,
    SteelBasePlateEngine,
)


def test_concentric_and_small_eccentricity_baseplate():
    """소편심(전단면 압축) 상태 베이스플레이트 지압응력 및 두께 산정 검증"""
    inp = BasePlateInput(
        col_d=400.0,
        col_bf=400.0,
        col_tf=20.0,
        col_tw=13.0,
        col_fy=275.0,
        B=600.0,
        N=600.0,
        tp=35.0,
        plate_fy=275.0,
        fck=27.0,
        pedestal_B=800.0,
        pedestal_N=800.0,
        Pu=600.0,   # 600 kN
        Mu=30.0,    # 30 kN*m -> e = 50 mm <= N/6 (100 mm) -> 소편심
        Vu=50.0
    )
    res = SteelBasePlateEngine.check_base_plate(inp)
    
    assert res.eccentricity_case == "소편심(전단면압축)"
    assert res.Tu_anchor_total == 0.0 # 앵커 인장력 없음
    
    # A1 = 360,000, A2 = 640,000, sqrt(A2/A1) = sqrt(640/360) = 1.333
    # fp_max_allow = 0.65 * 0.85 * 27 * 1.333 = 19.89 MPa
    assert res.fp_max_allow == pytest.approx(19.89, rel=1e-2)
    assert res.dcr_bearing < 1.0
    
    # 캔틸레버 m = (600 - 0.95*400)/2 = 110 mm, n = (600 - 0.80*400)/2 = 140 mm
    assert res.cantilever_l >= 140.0
    assert res.req_plate_tp > 0.0
    assert res.is_safe is True


def test_large_eccentricity_anchor_tension():
    """대편심(휨모멘트 지배) 상태 앵커볼트 인장력 및 콘파칭 검증"""
    inp = BasePlateInput(
        B=500.0,
        N=500.0,
        tp=40.0,
        Pu=200.0,   # 200 kN
        Mu=150.0,   # 150 kN*m -> e = 750 mm > N/2 -> 대편심
        anchor=AnchorBoltInput(
            anchor_type=AnchorType.CAST_IN_HEADED,
            diameter=24.0,
            num_anchors=4,
            num_tension_anchors=2,
            hef=300.0,
            futa=400.0
        )
    )
    res = SteelBasePlateEngine.check_base_plate(inp)
    
    assert res.eccentricity_case == "대편심(앵커인장)"
    assert res.Tu_anchor_total > 0.0 # 앵커 인장력 발생
    assert res.phi_Nsa > 0.0         # 앵커 강재 인장강도
    assert res.phi_Ncb > 0.0         # 콘크리트 콘파칭 강도
    assert res.phi_Vcp > 0.0         # 프라이아웃 강도
    assert res.is_safe is True


def test_thin_plate_thickness_warning():
    """베이스플레이트 두께 부족 시 경고 및 불합격 판정 검증"""
    inp = BasePlateInput(
        tp=15.0, # 15mm 얇은 플레이트
        Pu=1000.0,
        Mu=100.0
    )
    res = SteelBasePlateEngine.check_base_plate(inp)
    assert res.req_plate_tp > 15.0
    assert res.dcr_plate > 1.0
    assert len(res.messages) >= 1
    assert "소요두께" in res.messages[0]
    assert res.is_safe is False


def test_concrete_bearing_geometry_factor_upper_bound():
    """콘크리트 기초 지압 증대계수 sqrt(A2/A1) 2.0 상한 검증"""
    inp = BasePlateInput(
        B=400.0,
        N=400.0,
        pedestal_B=2000.0, # A2 / A1 = 25 -> sqrt = 5.0 -> 2.0으로 클램핑되어야 함
        pedestal_N=2000.0,
        fck=30.0
    )
    res = SteelBasePlateEngine.check_base_plate(inp)
    
    # fp_max_allow = 0.65 * (0.85 * 30.0) * 2.0 = 33.15 MPa
    assert res.fp_max_allow == pytest.approx(0.65 * 0.85 * 30.0 * 2.0, rel=1e-3)
