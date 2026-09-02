"""Unit tests for Concrete Structure Retrofit & Strengthening Engine (KDS 14 20 90 / ACI 440.2R)."""

import pytest
from src.engine.rfm.retrofit_design import (
    RetrofitType,
    RetrofitMethod,
    ExposureCondition,
    CFRPProp,
    SteelPlateProp,
    ExistingBeamProp,
    RetrofitDesignInput,
    check_retrofit_member,
)


class TestRetrofitDesign:
    """Test suite for CFRP and Steel Plate Retrofit."""

    def test_cfrp_plate_flexural_strengthening(self):
        """Test CFRP plate flexural strengthening and debonding strain limit."""
        input_data = RetrofitDesignInput(
            retrofit_type=RetrofitType.FLEXURE,
            method=RetrofitMethod.CFRP_PLATE,
            existing=ExistingBeamProp(
                b=300.0,
                h=600.0,
                d=540.0,
                fck=24.0,
                As=1520.0,
                fy=400.0,
                M_DL=40.0,
            ),
            cfrp=CFRPProp(
                tf=1.2,
                bf=200.0,
                num_plies=1,
                ffu=2800.0,
                Ef=165000.0,
                eps_fu=0.017,
                exposure=ExposureCondition.INTERIOR,
            ),
            Mu=300.0,
            Vu=0.0,
        )
        res = check_retrofit_member(input_data)

        assert res.phi_Mn_orig > 0.0
        assert res.phi_Mn_ret > res.phi_Mn_orig
        assert res.flexure_gain_ratio > 1.0
        assert res.eps_fe <= 0.004  # Debonding strain limit
        assert res.f_fe == pytest.approx(res.eps_fe * 165000.0, rel=1e-3)
        assert res.dcr_flexure <= 1.0
        assert res.is_safe is True

    def test_steel_plate_flexural_strengthening(self):
        """Test Steel Plate flexural strengthening."""
        input_data = RetrofitDesignInput(
            retrofit_type=RetrofitType.FLEXURE,
            method=RetrofitMethod.STEEL_PLATE,
            existing=ExistingBeamProp(
                b=300.0,
                h=500.0,
                d=450.0,
                fck=21.0,
                As=1200.0,
                fy=400.0,
                M_DL=30.0,
            ),
            steel_plate=SteelPlateProp(
                tsp=4.5,
                bsp=200.0,
                fys=275.0,
            ),
            Mu=240.0,
            Vu=0.0,
        )
        res = check_retrofit_member(input_data)

        assert res.phi_Mn_ret > res.phi_Mn_orig
        assert res.flexure_gain_ratio > 1.15
        assert res.is_safe is True

    def test_cfrp_shear_strengthening_u_wrap_and_full_wrap(self):
        """Test CFRP shear strengthening with U-wrap vs Full-wrap."""
        # U-wrap
        u_wrap_input = RetrofitDesignInput(
            retrofit_type=RetrofitType.SHEAR,
            method=RetrofitMethod.CFRP_SHEET,
            existing=ExistingBeamProp(
                b=300.0,
                h=600.0,
                d=540.0,
                fck=24.0,
                Av=142.6,
                fyt=400.0,
                s=200.0,
            ),
            cfrp=CFRPProp(
                tf=0.3,
                bf=100.0,
                sf=200.0,
                is_full_wrap=False,
            ),
            Mu=0.0,
            Vu=220.0,
        )
        res_u = check_retrofit_member(u_wrap_input)

        # Full-wrap
        full_wrap_input = RetrofitDesignInput(
            retrofit_type=RetrofitType.SHEAR,
            method=RetrofitMethod.CFRP_SHEET,
            existing=ExistingBeamProp(
                b=300.0,
                h=600.0,
                d=540.0,
                fck=24.0,
                Av=142.6,
                fyt=400.0,
                s=200.0,
            ),
            cfrp=CFRPProp(
                tf=0.3,
                bf=100.0,
                sf=200.0,
                is_full_wrap=True,
            ),
            Mu=0.0,
            Vu=220.0,
        )
        res_full = check_retrofit_member(full_wrap_input)

        assert res_u.phi_Vn_ret > res_u.phi_Vn_orig
        assert res_full.phi_Vn_ret >= res_u.phi_Vn_ret
        assert res_u.shear_gain_ratio > 1.0

    def test_combined_flexure_shear_retrofit(self):
        """Test combined flexure and shear retrofit check."""
        input_data = RetrofitDesignInput(
            retrofit_type=RetrofitType.COMBINED,
            method=RetrofitMethod.CFRP_PLATE,
            existing=ExistingBeamProp(
                b=300.0,
                h=600.0,
                d=540.0,
                fck=24.0,
                As=1520.0,
                fy=400.0,
                Av=142.6,
                fyt=400.0,
                s=200.0,
                M_DL=40.0,
            ),
            cfrp=CFRPProp(
                tf=1.2,
                bf=200.0,
                num_plies=1,
            ),
            Mu=330.0,
            Vu=200.0,
        )
        res = check_retrofit_member(input_data)

        assert res.phi_Mn_ret > res.phi_Mn_orig
        assert res.phi_Vn_ret > res.phi_Vn_orig
        assert res.details["unstrengthened_safe"] is True
