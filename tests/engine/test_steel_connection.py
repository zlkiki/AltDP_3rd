"""강구조 볼트/용접 접합부 및 블록전단 엔진 테스트 (KDS 14 31 25)"""

import pytest
from src.engine.steel.connection import (
    BoltGrade,
    JointType,
    HoleType,
    WeldType,
    BoltGroupInput,
    BlockShearInput,
    WeldJointInput,
    SteelConnectionEngine,
    BOLT_DB,
)


def test_bolt_properties():
    """볼트 기본 직경 및 강도 속성 검증"""
    d, ab, fnt, fnv_inc, fnv_exc, fu = SteelConnectionEngine.get_bolt_props("M20", BoltGrade.F10T)
    assert d == 20.0
    assert ab == pytest.approx(314.2, rel=1e-2)
    assert fu == 1000.0
    assert fnt == 750.0
    assert fnv_inc == 450.0
    assert fnv_exc == 563.0


def test_bearing_bolt_shear_and_tension():
    """지압접합 볼트 전단 및 인장 강도 검증"""
    inp = BoltGroupInput(
        bolt_size="M20",
        grade=BoltGrade.F10T,
        joint_type=JointType.BEARING,
        num_bolts=4,
        num_shear_planes=1,
        threads_included=True,
        plate_thickness=12.0,
        plate_fu=400.0,
        plate_fy=275.0,
        edge_distance=40.0,
        pitch=60.0,
        gauge=70.0,
        rows=2,
        cols=2,
        Vu=200.0,
        Tu=150.0
    )
    res = SteelConnectionEngine.check_bolt_group(inp)
    
    # 단일 볼트 전단: phi * Fnv * Ab = 0.75 * 450 * 314.2 = 106.04 kN
    assert res.phi_Rn_shear_single == pytest.approx(106.04, rel=1e-2)
    # 4개 볼트 전단: 4 * 106.04 = 424.16 kN
    assert res.phi_Rn_shear_total == pytest.approx(424.16, rel=1e-2)
    # 단일 볼트 인장: phi * Fnt * Ab = 0.75 * 750 * 314.2 = 176.74 kN
    assert res.phi_Rn_tension_single == pytest.approx(176.74, rel=1e-2)
    # 4개 볼트 인장: 4 * 176.74 = 706.95 kN
    assert res.phi_Rn_tension_total == pytest.approx(706.95, rel=1e-2)
    assert res.is_safe is True


def test_slip_critical_connection():
    """마찰접합(Slip-Critical) 미끄럼 강도 및 인장 저감 검증"""
    inp = BoltGroupInput(
        bolt_size="M20",
        grade=BoltGrade.F10T,
        joint_type=JointType.SLIP_CRITICAL,
        hole_type=HoleType.STANDARD,
        num_bolts=4,
        num_shear_planes=2, # 2면 마찰
        slip_coefficient=0.33,
        du=1.13,
        Vu=150.0,
        Tu=50.0 # 인장력 작용
    )
    res = SteelConnectionEngine.check_bolt_group(inp)
    
    # T0 = 157 kN, Du = 1.13, mu = 0.33, Ns = 2, n = 4, phi = 1.0
    # k_sc = 1 - Tu / (Du * T0 * n) = 1 - 50 / (1.13 * 157 * 4) = 1 - 50/709.64 = 0.9295
    # Rn = 0.33 * 1.13 * 1.0 * 157 * 2 * 4 * 0.9295 = 434.6 kN
    assert res.phi_Rn_slip_total == pytest.approx(434.6, rel=1e-2)
    assert res.is_safe is True


def test_bearing_strength_and_spacing_warnings():
    """볼트 구멍 지압강도 및 최소 간격 미달 경고 검증"""
    inp = BoltGroupInput(
        bolt_size="M20",
        grade=BoltGrade.F10T,
        edge_distance=20.0, # 1.25d = 25mm 미달
        pitch=40.0,         # 2.67d = 53.4mm 미달
        plate_thickness=8.0,
        plate_fu=400.0,
        Vu=100.0
    )
    res = SteelConnectionEngine.check_bolt_group(inp)
    assert len(res.messages) >= 2
    assert "연단거리" in res.messages[0]
    assert "볼트피치" in res.messages[1]
    assert res.is_safe is False # 경고 메시지로 인해 False


def test_block_shear_rupture():
    """블록전단 파단강도 검증 (KDS 14 31 25 4.1.3)"""
    # L자형 전단단면: Agv=3000 mm², Anv=2400 mm², Ant=800 mm²
    inp = BlockShearInput(
        Agv=3000.0,
        Anv=2400.0,
        Ant=800.0,
        Fu=400.0,
        Fy=275.0,
        Ubs=1.0,
        Pu=450.0
    )
    res = SteelConnectionEngine.check_block_shear(inp)
    
    # Rn_rupture = 0.60 * 400 * 2400 + 1.0 * 400 * 800 = 576000 + 320000 = 896 kN
    # Rn_yield = 0.60 * 275 * 3000 + 1.0 * 400 * 800 = 495000 + 320000 = 815 kN (지배)
    # phi_Rn = 0.75 * 815 = 611.25 kN
    assert res.Rn_rupture == pytest.approx(896.0, rel=1e-3)
    assert res.Rn_yield == pytest.approx(815.0, rel=1e-3)
    assert res.phi_Rn == pytest.approx(611.25, rel=1e-3)
    assert res.governing_mode == "전단항복+인장파단"
    assert res.dcr == pytest.approx(450.0 / 611.25, rel=1e-3)
    assert res.is_safe is True


def test_welded_joint_fillet_and_cjp():
    """필릿 및 완전용입 그루브 용접 강도 검증"""
    # 필릿용접 s=6mm, L=200mm, Fexx=490 MPa
    inp_fillet = WeldJointInput(
        weld_type=WeldType.FILLET,
        leg_size=6.0,
        length=200.0,
        Fexx=490.0,
        base_fu=400.0,
        base_thickness=10.0,
        Vu=150.0
    )
    res_fillet = SteelConnectionEngine.check_weld_joint(inp_fillet)
    assert res_fillet.throat == pytest.approx(4.24, rel=1e-2) # 0.707 * 6
    assert res_fillet.effective_length == pytest.approx(188.0, rel=1e-2) # 200 - 2*6
    assert res_fillet.phi_Rn > 0.0
    assert res_fillet.is_safe is True

    # CJP 그루브용접
    inp_cjp = WeldJointInput(
        weld_type=WeldType.CJP,
        length=200.0,
        base_fu=400.0,
        base_thickness=10.0,
        Vu=300.0
    )
    res_cjp = SteelConnectionEngine.check_weld_joint(inp_cjp)
    assert res_cjp.throat == 10.0
    assert res_cjp.phi_Rn == pytest.approx(0.90 * 400 * 10 * 200 / 1000.0, rel=1e-3) # 720 kN
    assert res_cjp.is_safe is True
