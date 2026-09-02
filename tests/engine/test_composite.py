"""Unit tests for SRC/CFT Composite Columns and Composite Beams (KDS 14 31 30)."""

import pytest
import math
from src.engine.src_composite.composite_column import (
    CFTColumnInput,
    SRCColumnInput,
    CFTType,
    check_cft_column,
    check_src_column,
)
from src.engine.src_composite.composite_beam import (
    CompositeBeamInput,
    StudBoltInput,
    check_composite_beam,
)


class TestCompositeColumn:
    """Test suite for CFT and SRC column design."""

    def test_cft_rectangular_column_basic(self):
        """Test rectangular CFT column axial compressive strength."""
        cft_input = CFTColumnInput(
            cft_type=CFTType.RECTANGULAR,
            B=400.0,
            H=400.0,
            t=12.0,
            fck=30.0,
            Fy=355.0,
            L=3500.0,
            K=1.0,
            Pu=4500.0,
        )
        res = check_cft_column(cft_input)
        
        assert res.Ag == 160000.0
        assert res.steel_ratio > 1.0  # As / Ag >= 1%
        assert res.Pno > 0.0
        assert res.EI_eff_x > 0.0
        assert res.Pe_x > 0.0
        assert res.phi_Pn > 0.0
        assert res.phi_Pn < res.Pno  # Buckling reduces strength
        assert res.dcr_axial > 0.0
        assert res.details["C2"] == 0.85

    def test_cft_circular_column_confinement(self):
        """Test circular CFT column with 0.95 confinement factor."""
        cft_input = CFTColumnInput(
            cft_type=CFTType.CIRCULAR,
            D=450.0,
            t=10.0,
            fck=35.0,
            Fy=355.0,
            L=4000.0,
            K=1.0,
            Pu=4000.0,
        )
        res = check_cft_column(cft_input)
        
        assert res.details["C2"] == 0.95
        assert res.is_compact is True
        assert res.Pno > 0.0
        assert res.phi_Pn > 0.0
        # Expected Pno = Fy * As + 0.95 * fck * Ac
        Di = 450.0 - 20.0
        Ac_expected = math.pi * (Di ** 2) / 4.0
        As_expected = math.pi * (450.0 ** 2) / 4.0 - Ac_expected
        Pno_expected = (355.0 * As_expected + 0.95 * 35.0 * Ac_expected) / 1000.0
        assert pytest.approx(res.Pno, rel=1e-3) == Pno_expected

    def test_src_encased_column(self):
        """Test Encased SRC column with H-beam and rebar cage."""
        src_input = SRCColumnInput(
            B=600.0,
            H=600.0,
            As=11980.0,
            Is_x=204000000.0,
            Is_y=67500000.0,
            Fy=355.0,
            num_rebars=8,
            rebar_dia=22.0,
            rebar_dist_x=480.0,
            rebar_dist_y=480.0,
            Fysr=400.0,
            fck=30.0,
            L=4500.0,
            K=1.0,
            Pu=5000.0,
        )
        res = check_src_column(src_input)
        
        assert res.Ag == 360000.0
        assert res.steel_ratio_ok is True
        assert res.details["rebar_ratio_ok"] is True
        assert res.Pno > 0.0
        assert res.phi_Pn > 0.0
        assert res.dcr_axial <= 1.0
        assert res.is_safe is True


class TestCompositeBeam:
    """Test suite for Composite Beam and Stud Connectors."""

    def test_full_composite_beam(self):
        """Test full composite beam with concrete slab and studs."""
        beam_input = CompositeBeamInput(
            L=9000.0,
            beam_spacing=3000.0,
            d_s=450.0,
            b_f=200.0,
            t_f=14.0,
            t_w=9.0,
            Fy=355.0,
            h_f=150.0,
            h_deck=0.0,
            fck=27.0,
            stud=StudBoltInput(
                diameter=19.0,
                Fu=400.0,
                num_studs_half_span=42,
            ),
            Mu=450.0,
            Vu=200.0,
        )
        res = check_composite_beam(beam_input)
        
        assert res.b_eff == min(9000.0 / 4.0, 3000.0, 200.0 + 16.0 * 150.0)  # 2250.0
        assert res.Qn_single > 0.0
        assert res.sum_Qn > 0.0
        assert res.is_full_composite is True
        assert res.plastic_neutral_axis == "SLAB"
        assert res.phi_Mn > 0.0
        assert res.dcr_flexure <= 1.0
        assert res.dcr_shear <= 1.0
        assert res.is_safe is True

    def test_partial_composite_beam(self):
        """Test partial composite beam when stud count is limited."""
        beam_input = CompositeBeamInput(
            L=8000.0,
            beam_spacing=2500.0,
            d_s=400.0,
            b_f=200.0,
            t_f=13.0,
            t_w=8.0,
            Fy=355.0,
            h_f=120.0,
            fck=24.0,
            stud=StudBoltInput(
                diameter=16.0,
                Fu=400.0,
                num_studs_half_span=8,  # Limited stud count
            ),
            Mu=300.0,
            Vu=100.0,
        )
        res = check_composite_beam(beam_input)
        
        assert res.is_full_composite is False
        assert res.composite_ratio < 100.0
        assert res.plastic_neutral_axis in ["FLANGE", "WEB"]
        assert res.phi_Mn > 0.0
