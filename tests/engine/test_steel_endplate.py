"""강구조 엔드플레이트 모멘트 접합부 엔진 테스트 (KDS 14 31 25)"""

import pytest
from src.engine.steel.connection import BoltGrade
from src.engine.steel.endplate import (
    EndPlateType,
    EndPlateInput,
    SteelEndPlateEngine,
)


def test_extended_4bolt_design_and_flange_tension():
    """확장형 4볼트 엔드플레이트 플랜지 인장력 및 볼트 DCR 검증"""
    inp = EndPlateInput(
        plate_type=EndPlateType.EXTENDED_4BOLT_UNSTIFFENED,
        beam_d=500.0,
        beam_bf=200.0,
        beam_tf=16.0,
        beam_tw=10.0,
        beam_fy=275.0,
        col_d=350.0,
        col_bf=350.0,
        col_tf=19.0,
        col_tw=12.0,
        col_k=32.0,
        col_fy=275.0,
        bp=220.0,
        tp=28.0,
        plate_fy=275.0,
        bolt_size="M24",
        bolt_grade=BoltGrade.F10T,
        num_tension_bolts=4,
        Mu=200.0,  # 200 kN*m
        Vu=100.0,
        Pu=0.0
    )
    res = SteelEndPlateEngine.check_end_plate(inp)
    
    # debar = 500 - 16 = 484 mm
    # Tf = 200 * 1000 / 484 = 413.22 kN
    assert res.Tf == pytest.approx(413.22, rel=1e-2)
    # T_bolt_req = 413.22 / 4 = 103.31 kN
    assert res.T_bolt_req == pytest.approx(103.31, rel=1e-2)
    
    # 단일 M24 F10T 인장강도: 0.75 * 750 * 452.4 / 1000 = 254.48 kN
    assert res.phi_Rn_bolt == pytest.approx(254.48, rel=1e-2)
    assert res.dcr_bolt_tension == pytest.approx(103.31 / 254.48, rel=1e-2)
    assert res.yield_line_Y > 0.0
    assert res.req_plate_tp > 0.0
    assert res.is_safe is True


def test_plate_thickness_insufficient_warning():
    """엔드플레이트 두께 부족 시 경고 및 불합격 판정 검증"""
    inp = EndPlateInput(
        tp=12.0, # 매우 얇은 두께
        Mu=300.0, # 큰 모멘트
        bolt_size="M24",
        bolt_grade=BoltGrade.F10T
    )
    res = SteelEndPlateEngine.check_end_plate(inp)
    assert res.req_plate_tp > 12.0
    assert res.dcr_plate_bending > 1.0
    assert len(res.messages) >= 1
    assert "소요두께" in res.messages[0]
    assert res.is_safe is False


def test_column_limit_states():
    """기둥 플랜지 휨, 웨브 국부항복, 패널존 전단 한계상태 검증"""
    inp = EndPlateInput(
        col_d=300.0,
        col_bf=300.0,
        col_tf=15.0,
        col_tw=10.0,
        col_k=28.0,
        col_fy=275.0,
        tp=30.0,
        Mu=150.0
    )
    res = SteelEndPlateEngine.check_end_plate(inp)
    
    # 기둥 플랜지 휨강도: 0.90 * 6.25 * 275 * 15^2 / 1000 = 348.05 kN
    assert res.phi_Rn_col_flange_bending == pytest.approx(348.05, rel=1e-2)
    # 기둥 웨브 항복강도: 1.0 * 275 * 10 * (5*28 + 16 + 2*30) / 1000 = 594.0 kN
    assert res.phi_Rn_col_web_yielding == pytest.approx(594.0, rel=1e-2)
    assert res.phi_Vn_col_panel_zone > 0.0


def test_yield_line_types():
    """접합부 형식(Flush, Ext 4-Bolt, Ext 8-Bolt)별 항복선 Y 크기 비교"""
    inp_flush = EndPlateInput(plate_type=EndPlateType.FLUSH)
    inp_4b = EndPlateInput(plate_type=EndPlateType.EXTENDED_4BOLT_UNSTIFFENED)
    inp_8b = EndPlateInput(plate_type=EndPlateType.EXTENDED_8BOLT_STIFFENED)
    
    Y_flush = SteelEndPlateEngine.calculate_yield_line_Y(inp_flush)
    Y_4b = SteelEndPlateEngine.calculate_yield_line_Y(inp_4b)
    Y_8b = SteelEndPlateEngine.calculate_yield_line_Y(inp_8b)
    
    # 확장형 4볼트 및 8볼트의 항복선 Y가 Flush보다 커야 함
    assert Y_8b > Y_4b > Y_flush
