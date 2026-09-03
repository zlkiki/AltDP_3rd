"""Tests for International Design Codes (Eurocode, US, Indian Standards).

Validates calculation precision, code compliance, and safety criteria against
standard textbook and code benchmark solutions.
"""

import pytest
import math

from src.engine.international.eurocode import (
    check_ec2_rc_beam,
    check_ec3_steel_beam,
)
from src.engine.international.us_code import (
    check_aci318_rc_beam,
    check_aisc360_steel_beam,
)
from src.engine.international.is_code import (
    check_is456_rc_beam,
    check_is800_steel_beam,
)


class TestEurocodeAdapters:
    """Test Eurocode 2 (EN 1992-1-1) and Eurocode 3 (EN 1993-1-1)."""

    def test_ec2_rc_beam_design_and_partial_factors(self):
        # b=300, h=600, d=550, fck=30, fyk=500, As=1500 (3-D25)
        res = check_ec2_rc_beam(
            b=300.0, h=600.0, d=550.0, fck=30.0, fyk=500.0,
            As=1500.0, Mu=250.0, Vu=100.0,
        )
        # Material strengths: fcd = 0.85 * 30 / 1.5 = 17.0 MPa, fyd = 500 / 1.15 = 434.78 MPa
        assert res.fcd == pytest.approx(17.0, rel=1e-3)
        assert res.fyd == pytest.approx(434.783, rel=1e-3)
        assert res.M_Rd > 280.0
        assert res.V_Rd > 100.0
        assert res.is_safe is True
        assert res.dcr_flexure < 1.0

    def test_ec3_steel_beam_classification_and_ltb(self):
        # Standard compact European section (e.g. HEA 300 / IPE 400)
        res_short = check_ec3_steel_beam(
            h=400.0, b=180.0, tw=8.6, tf=13.5, r=21.0,
            A=8450.0, Wpl_y=1307e3, Wel_y=1156e3,
            Iz=1318e4, It=51.1e4, Iw=490e9,
            fy=275.0, Lcr=2000.0, Mu=250.0, Vu=120.0,
        )
        res_long = check_ec3_steel_beam(
            h=400.0, b=180.0, tw=8.6, tf=13.5, r=21.0,
            A=8450.0, Wpl_y=1307e3, Wel_y=1156e3,
            Iz=1318e4, It=51.1e4, Iw=490e9,
            fy=275.0, Lcr=8000.0, Mu=250.0, Vu=120.0,
        )
        assert res_short.section_class in (1, 2)
        assert res_short.chi_LT > res_long.chi_LT
        assert res_short.M_b_Rd > res_long.M_b_Rd
        assert res_short.V_pl_Rd > 200.0


class TestUSStandardsAdapters:
    """Test US ACI 318-19 and AISC 360-16 LRFD."""

    def test_aci318_rc_beam_beta1_and_phi_transition(self):
        # f'c = 28 MPa (4000 psi) => beta1 = 0.85
        res_28 = check_aci318_rc_beam(
            b=300.0, h=600.0, d=540.0, fc_prime=28.0, fy=420.0,
            As=1200.0, Mu=200.0, Vu=80.0
        )
        assert res_28.beta1 == 0.85
        # Under-reinforced: eps_t >= 0.005 => phi = 0.90
        assert res_28.epsilon_t > 0.005
        assert res_28.phi_flexure == 0.90
        assert res_28.phi_M_n > res_28.M_n * 0.89

        # High strength concrete f'c = 42 MPa => beta1 = 0.85 - 0.05*(42-28)/7 = 0.75
        res_42 = check_aci318_rc_beam(
            b=300.0, h=600.0, d=540.0, fc_prime=42.0, fy=420.0,
            As=1200.0
        )
        assert res_42.beta1 == pytest.approx(0.75, rel=1e-3)

    def test_aisc360_steel_beam_ltb_zones_and_compression(self):
        # Doubly symmetric I-beam W16x50 approx (d=413, bf=180, tf=16, tw=9.7, Zx=1500e3, Sx=1320e3)
        # Short unbraced length => Zone 1 (Mn = Mp)
        res_zone1 = check_aisc360_steel_beam(
            d_depth=413.0, bf=180.0, tf=16.0, tw=9.7, Ag=9500.0,
            Zx=1500e3, Sx=1320e3, ry=40.0, J_torsion=50e4, Cw=500e9,
            Fy=345.0, Lb=1500.0, Mu=300.0, Vu=100.0
        )
        assert res_zone1.ltb_zone == 1
        assert res_zone1.M_n == res_zone1.M_p
        assert res_zone1.phi_M_n == pytest.approx(0.90 * res_zone1.M_p, rel=1e-3)

        # Longer unbraced length => Zone 2 or 3
        res_zone23 = check_aisc360_steel_beam(
            d_depth=413.0, bf=180.0, tf=16.0, tw=9.7, Ag=9500.0,
            Zx=1500e3, Sx=1320e3, ry=40.0, J_torsion=50e4, Cw=500e9,
            Fy=345.0, Lb=6000.0
        )
        assert res_zone23.ltb_zone in (2, 3)
        assert res_zone23.M_n < res_zone23.M_p


class TestIndianStandardsAdapters:
    """Test Indian Standards IS 456:2000 and IS 800:2007."""

    def test_is456_rc_beam_limiting_moment(self):
        # b=250, d=450, fck=20 (M20), fy=415 (Fe 415)
        # IS 456: xu_max / d = 0.48 => xu_max = 216 mm
        # Mu_lim = 0.36 * 0.48 * (1 - 0.42 * 0.48) * 250 * 450^2 * 20 / 1e6 = 139.9 kN*m
        res = check_is456_rc_beam(
            b=250.0, h=500.0, d=450.0, fck=20.0, fy=415.0,
            Ast=1000.0, Mu_applied=100.0, Vu_applied=50.0
        )
        assert res.xu_max == pytest.approx(0.48 * 450.0, rel=1e-3)
        assert res.M_u_lim == pytest.approx(139.9, rel=1e-2)
        assert res.is_under_reinforced is True
        assert res.M_u < res.M_u_lim
        assert res.is_safe is True

    def test_is800_steel_beam_plastic_capacity(self):
        res = check_is800_steel_beam(
            d_total=400.0, b_flange=200.0, tf=14.0, tw=8.0, r=16.0,
            Ag=8410.0, Zp=1307e3, Ze=1156e3, ry=45.0,
            fy=250.0, KL=2000.0, Mu=200.0, Vu=80.0
        )
        assert res.section_class in ("Plastic", "Compact")
        # Md = Zp * fy / 1.10 = 1307e3 * 250 / 1.10 / 1e6 = 297.04 kN*m
        assert res.M_d == pytest.approx(297.045, rel=1e-2)
        assert res.V_d > 100.0
        assert res.is_safe is True
