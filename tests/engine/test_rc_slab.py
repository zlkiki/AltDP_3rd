"""Unit tests for RC Slab and Punching Shear Engine (Phase 05-2).

Verifies 1-way slab deflection & flexure, 2-way slab Direct Design Method (DDM),
and 2-way punching shear 3 KDS capacity formulas with unbalanced moments.
"""

import math
import pytest
from src.engine.rc.slab import (
    RCOneWaySlab,
    OneWaySlabInput,
    SlabSupportCondition,
    RCTwoWaySlabDDM,
    TwoWaySlabDDMInput,
    PunchingShearEngine,
    PunchingShearInput,
    ColumnLocation
)
from src.engine.materials import ConcreteMaterial, RebarMaterial


def test_one_way_slab_min_thickness():
    """Test KDS 14 20 20 minimum slab thickness for deflection."""
    # L = 4000 mm, Both ends continuous -> L / 28 = 4000 / 28 = 142.86 mm
    inp_cont = OneWaySlabInput(span_L=4000.0, support_type=SlabSupportCondition.BOTH_ENDS_CONTINUOUS)
    slab_cont = RCOneWaySlab(inp_cont)
    assert math.isclose(slab_cont.calc_min_thickness(), 4000.0 / 28.0, rel_tol=1e-3)
    
    # Cantilever L = 2000 mm -> L / 10 = 200 mm
    inp_cant = OneWaySlabInput(span_L=2000.0, support_type=SlabSupportCondition.CANTILEVER)
    slab_cant = RCOneWaySlab(inp_cant)
    assert math.isclose(slab_cant.calc_min_thickness(), 200.0, rel_tol=1e-3)
    
    # Simply supported with fy = 500 MPa -> (L / 20) * (0.43 + 500/700)
    inp_fy500 = OneWaySlabInput(
        span_L=3000.0,
        support_type=SlabSupportCondition.SIMPLY_SUPPORTED,
        rebar=RebarMaterial(fy=500.0)
    )
    slab_fy500 = RCOneWaySlab(inp_fy500)
    expected = (3000.0 / 20.0) * (0.43 + 500.0 / 700.0)
    assert math.isclose(slab_fy500.calc_min_thickness(), expected, rel_tol=1e-3)


def test_one_way_slab_flexure_and_temp():
    """Test 1-way slab flexure design check and temperature rebar."""
    inp = OneWaySlabInput(
        name="S101",
        span_L=3500.0,
        thickness_h=160.0,
        cover=20.0,
        main_bar_diam=13.0, # As = 126.7 mm2
        main_spacing=150.0, # As_prov = 1000/150 * 126.7 = 844.7 mm2/m
        temp_bar_diam=10.0,
        temp_spacing=200.0,
        Mu=30.0,
        Vu=25.0
    )
    slab = RCOneWaySlab(inp)
    res = slab.design_check()
    
    assert res.is_safe is True
    assert res.dcr_flexure < 1.0
    assert res.is_temp_ok is True
    assert res.phi_Mn > 30.0


def test_two_way_slab_ddm_moments():
    """Test 2-way slab Direct Design Method static moment M0 and strip distribution."""
    # l1 = 6.0 m, l2 = 6.0 m, c1 = 0.5 m -> ln = 5.5 m
    # qu = 10.0 kN/m2
    # M0 = (10.0 * 6.0 * (5.5^2)) / 8 = 60 * 30.25 / 8 = 226.875 kN*m
    inp = TwoWaySlabDDMInput(
        l1=6000.0,
        l2=6000.0,
        c1=500.0,
        c2=500.0,
        qu=10.0,
        is_interior_span=True
    )
    ddm_solver = RCTwoWaySlabDDM(inp)
    moments = ddm_solver.calculate_ddm_moments()
    
    assert math.isclose(moments.M0, 226.88, abs_tol=0.1)
    # Interior span: neg = 0.65 * M0, pos = 0.35 * M0
    assert math.isclose(moments.neg_interior_Mu, 0.65 * moments.M0, rel_tol=1e-3)
    assert math.isclose(moments.pos_Mu, 0.35 * moments.M0, rel_tol=1e-3)
    
    # Column Strip (75% neg, 60% pos)
    assert math.isclose(moments.col_strip_neg_interior, 0.75 * moments.neg_interior_Mu, rel_tol=1e-3)
    assert math.isclose(moments.col_strip_pos, 0.60 * moments.pos_Mu, rel_tol=1e-3)


def test_punching_shear_interior_3_formulas():
    """Test 2-way punching shear 3 KDS formulas for interior square column."""
    # c1 = 500 mm, c2 = 500 mm, d = 200 mm
    # b1 = 700 mm, b2 = 700 mm -> b0 = 4 * 700 = 2800 mm
    # fck = 25 MPa -> sqrt(fck) = 5.0 MPa
    # vc1 = (1 + 2/1) * (1/6) * 5 = 2.500 MPa
    # vc2 = (40 * 200 / 2800 + 2) * (1/12) * 5 = (2.857 + 2) * 5 / 12 = 2.024 MPa
    # vc3 = (1/3) * 5 = 1.667 MPa
    # min is vc3 = 1.667 MPa
    inp = PunchingShearInput(
        location=ColumnLocation.INTERIOR,
        c1=500.0,
        c2=500.0,
        eff_depth_d=200.0,
        Vu=400.0,
        Munb=0.0,
        concrete=ConcreteMaterial(fck=25.0)
    )
    engine = PunchingShearEngine(inp)
    res = engine.check_punching_shear()
    
    assert res.b0 == 2800.0
    assert math.isclose(res.vc1, 2.500, rel_tol=1e-2)
    assert math.isclose(res.vc3, 1.667, rel_tol=1e-2)
    assert res.vc_nominal == res.vc3 # 1.667 MPa is lowest
    assert math.isclose(res.phi_vc, 0.75 * 1.667, rel_tol=1e-2)


def test_punching_shear_unbalanced_moment():
    """Test eccentric shear stress addition due to unbalanced moment."""
    inp_pure = PunchingShearInput(
        location=ColumnLocation.INTERIOR,
        c1=500.0,
        c2=500.0,
        eff_depth_d=200.0,
        Vu=350.0,
        Munb=0.0,
        concrete=ConcreteMaterial(fck=25.0)
    )
    res_pure = PunchingShearEngine(inp_pure).check_punching_shear()
    
    inp_moment = PunchingShearInput(
        location=ColumnLocation.INTERIOR,
        c1=500.0,
        c2=500.0,
        eff_depth_d=200.0,
        Vu=350.0,
        Munb=50.0, # 50 kN*m unbalanced moment
        concrete=ConcreteMaterial(fck=25.0)
    )
    res_moment = PunchingShearEngine(inp_moment).check_punching_shear()
    
    assert res_moment.gamma_v > 0.0
    assert res_moment.vu_moment > 0.0
    assert res_moment.vu_total > res_pure.vu_total
    assert res_moment.dcr > res_pure.dcr


def test_punching_shear_edge_and_corner():
    """Test edge and corner column perimeter and alpha_s values."""
    # Edge column (alpha_s = 30)
    inp_edge = PunchingShearInput(
        location=ColumnLocation.EDGE,
        c1=400.0,
        c2=400.0,
        eff_depth_d=200.0
    )
    res_edge = PunchingShearEngine(inp_edge).check_punching_shear()
    assert res_edge.alpha_s == 30.0
    # b0 = 2 * (400 + 100) + (400 + 200) = 1000 + 600 = 1600 mm
    assert res_edge.b0 == 1600.0
    
    # Corner column (alpha_s = 20)
    inp_corner = PunchingShearInput(
        location=ColumnLocation.CORNER,
        c1=400.0,
        c2=400.0,
        eff_depth_d=200.0
    )
    res_corner = PunchingShearEngine(inp_corner).check_punching_shear()
    assert res_corner.alpha_s == 20.0
    # b0 = (400 + 100) + (400 + 100) = 1000 mm
    assert res_corner.b0 == 1000.0
