"""Unit Tests for RC Retaining Wall Design Engine (KDS 14 20 60 / KDS 14 20 20)."""

import pytest
import math

from src.engine.rc.retaining_wall import (
    RetainingWallType,
    SoilProperties,
    RetainingWallGeometry,
    RetainingWallInput,
    RCRetainingWall
)


class TestRCRetainingWall:
    """Test Retaining Wall Earth Pressure, 3-Stability Checks, and RC Sections."""

    def test_rankine_active_pressure_and_moment(self):
        """Test active lateral thrust and overturning moment on 4.5m wall."""
        inp = RetainingWallInput(
            geometry=RetainingWallGeometry(H_total=4500.0, base_t=500.0),
            soil=SoilProperties(
                unit_weight=19.0,
                phi_deg=30.0,
                surcharge_q=10.0,
                water_table_depth=6000.0  # Dry backfill
            )
        )
        wall = RCRetainingWall(inp)
        ep = wall.calc_earth_pressure()
        
        # Ka = tan^2(45 - 15) = tan^2(30) = 1/3 = 0.33333
        assert pytest.approx(ep.Ka, rel=1e-3) == 1.0 / 3.0
        assert ep.Pa_soil > 0.0
        assert ep.Pa_surch > 0.0
        assert ep.total_H == pytest.approx(ep.Pa_soil + ep.Pa_surch, rel=1e-3)
        assert ep.total_overturning_moment_Mo > 0.0

    def test_overturning_and_sliding_stability(self):
        """Check 3 external stability conditions (Fs_ot >= 2.0, Fs_sl >= 1.5, Bearing)."""
        inp = RetainingWallInput(
            geometry=RetainingWallGeometry(
                H_total=4500.0,
                stem_t_top=300.0,
                stem_t_bot=450.0,
                base_width_B=3200.0,
                base_t=500.0,
                toe_length=1000.0,
                heel_length=1750.0,
                front_embedment_Df=800.0
            ),
            soil=SoilProperties(
                unit_weight=19.0,
                phi_deg=30.0,
                base_friction_coef=0.55,
                surcharge_q=10.0,
                qa_allowable=300.0
            )
        )
        wall = RCRetainingWall(inp)
        res = wall.solve()
        
        assert res.stability.Fs_ot >= 2.0
        assert res.stability.is_overturning_ok is True
        assert res.stability.Fs_sl >= 1.5
        assert res.stability.is_sliding_ok is True
        assert res.stability.is_bearing_ok is True
        assert res.stability.q_max <= inp.soil.qa_allowable

    def test_stem_and_base_section_design(self):
        """Check internal RC structural capacities of Stem, Toe, and Heel."""
        inp = RetainingWallInput(
            geometry=RetainingWallGeometry(
                H_total=4000.0,
                stem_t_top=300.0,
                stem_t_bot=450.0,
                base_width_B=3000.0,
                base_t=500.0,
                toe_length=900.0,
                heel_length=1650.0
            ),
            stem_main_bar_diam=19.0,
            stem_main_bar_spacing=150.0,
            toe_main_bar_diam=16.0,
            toe_main_bar_spacing=150.0,
            heel_main_bar_diam=19.0,
            heel_main_bar_spacing=150.0
        )
        wall = RCRetainingWall(inp)
        res = wall.solve()
        
        assert res.stem.is_flexure_ok is True
        assert res.stem.is_shear_ok is True
        assert res.toe.is_flexure_ok is True
        assert res.toe.is_shear_ok is True
        assert res.heel.is_flexure_ok is True
        assert res.heel.is_shear_ok is True
        assert res.is_safe is True
