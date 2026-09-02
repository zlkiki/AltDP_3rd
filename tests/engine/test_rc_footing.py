"""Unit Tests for RC Footing and Underground Beam Engine (KDS 14 20 20 / KDS 14 20 60)."""

import pytest
import math

from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.footing import (
    ColumnType,
    SpreadFootingInput,
    RCSpreadFooting,
    CombinedFootingInput,
    RCCombinedFooting,
    UndergroundBeamInput,
    RCUndergroundBeam,
)


class TestSpreadFooting:
    """Test Isolated/Spread Footing Bearing, Shear, and Flexure Calculations."""

    def test_concentric_bearing_pressure(self):
        """Uniform bearing pressure under zero eccentricity."""
        inp = SpreadFootingInput(
            Bx=2000.0,
            Ly=2000.0,
            thickness_H=500.0,
            depth_Df=1000.0,
            P_serv=1000.0,
            Mx_serv=0.0,
            My_serv=0.0,
            qa_allowable=300.0
        )
        footing = RCSpreadFooting(inp)
        res = footing.calc_bearing_pressure(inp.P_serv, inp.Mx_serv, inp.My_serv)
        
        # Self weight = 2*2*0.5*23.5 = 47 kN, Soil = 2*2*0.5*18 = 36 kN -> Total = 1083 kN
        # Area = 4.0 m2 -> q_avg = 1083 / 4 = 270.75 kPa
        assert res.is_bearing_ok is True
        assert res.is_tension_separated is False
        assert pytest.approx(res.q_max, rel=1e-2) == res.q_min
        assert res.q_max < 300.0

    def test_eccentric_tension_separation(self):
        """Large moment causing eccentricity exceeding kern (ex > B/6)."""
        inp = SpreadFootingInput(
            Bx=2400.0,
            Ly=2400.0,
            thickness_H=600.0,
            P_serv=500.0,
            Mx_serv=0.0,
            My_serv=350.0,  # ex = 350 / ~580 = 0.60m > B/6 = 0.40m
            qa_allowable=500.0
        )
        footing = RCSpreadFooting(inp)
        res = footing.calc_bearing_pressure(inp.P_serv, inp.Mx_serv, inp.My_serv)
        
        assert res.is_tension_separated is True
        assert res.q_min == 0.0
        assert res.q_max > 0.0

    def test_punching_shear_and_flexure(self):
        """Check two-way punching shear and flexural capacity."""
        inp = SpreadFootingInput(
            Bx=2500.0,
            Ly=2500.0,
            thickness_H=650.0,
            col_cx=500.0,
            col_cy=500.0,
            Pu=1500.0,
            rebar_x_diam=19.0,
            rebar_x_spacing=150.0,
            rebar_y_diam=19.0,
            rebar_y_spacing=150.0
        )
        footing = RCSpreadFooting(inp)
        res = footing.solve()
        
        assert res.shear.is_2way_ok is True
        assert res.shear.Vu_2way < res.shear.phi_Vc_2way
        assert res.shear.b0 == pytest.approx(2.0 * (500 + res.shear.d_avg) * 2, rel=1e-3)
        assert res.flexure.is_flexure_x_ok is True
        assert res.flexure.is_flexure_y_ok is True
        assert res.is_safe is True


class TestCombinedFooting:
    """Test 2-Column Combined Footing."""

    def test_combined_footing_resultant_and_bending(self):
        inp = CombinedFootingInput(
            Bx=2200.0,
            Ly=7000.0,
            thickness_H=900.0,
            col1_dist_from_left=500.0,
            col1_P_serv=900.0,
            col1_Pu=1200.0,
            col2_dist_from_left=5500.0,
            col2_P_serv=1500.0,
            col2_Pu=2000.0,
            qa_allowable=350.0
        )
        combined = RCCombinedFooting(inp)
        res = combined.solve()
        
        assert res.is_bearing_ok is True
        assert res.Mu_top_max > 0.0
        assert res.is_top_ok is True
        assert res.is_bot_ok is True


class TestUndergroundBeam:
    """Test Tie Beam under 10% column axial force and bending."""

    def test_tie_beam_tension_and_shear(self):
        inp = UndergroundBeamInput(
            b=400.0,
            h=600.0,
            connected_col_Pu=2500.0,  # 10% = 250 kN
            Pu_tension=150.0,         # Should be governed by 250 kN
            Mu=60.0,
            Vu=50.0
        )
        beam = RCUndergroundBeam(inp)
        res = beam.solve()
        
        assert res.min_required_axial_kN == 250.0
        assert res.is_axial_ok is True
        assert res.is_flexure_ok is True
        assert res.is_shear_ok is True
        assert res.is_safe is True
