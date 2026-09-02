"""Unit tests for Aluminium Alloy Structural Design (KDS 14 31 40)."""

import pytest
from src.engine.alu.alu_design import (
    AluAlloyType,
    AluSectionShape,
    AluSectionInput,
    ALU_MATERIAL_DB,
    check_alu_member,
)


class TestAluDesign:
    """Test suite for Aluminium alloy member design."""

    def test_material_database(self):
        """Verify mechanical properties in material DB."""
        mat_6061 = ALU_MATERIAL_DB[AluAlloyType.A6061_T6]
        assert mat_6061.Fty == 240.0
        assert mat_6061.Ftu == 260.0
        assert mat_6061.E == 70000.0
        assert mat_6061.Fty_haz == 140.0

        mat_6063 = ALU_MATERIAL_DB[AluAlloyType.A6063_T6]
        assert mat_6063.Fty == 170.0
        assert mat_6063.Ftu == 205.0

    def test_alu_tension_member(self):
        """Test tension member without welding."""
        sec_input = AluSectionInput(
            alloy=AluAlloyType.A6061_T6,
            Ag=4000.0,
            An=3600.0,
            Pu=300.0,
            Mux=0.0,
            Muy=0.0,
            Vu=0.0,
            is_welded_in_haz=False,
        )
        res = check_alu_member(sec_input)
        
        assert res.khaz == 1.0
        assert res.Fty_used == 240.0
        # Yielding: 0.95 * 240 * 4000 / 1000 = 912 kN
        # Rupture: 0.85 * 260 * 3600 / 1000 = 795.6 kN
        assert pytest.approx(res.phi_Pt, rel=1e-3) == 795.6
        assert res.dcr_axial < 1.0
        assert res.is_safe is True

    def test_alu_haz_reduction(self):
        """Test HAZ strength reduction when welded."""
        sec_unwelded = AluSectionInput(
            alloy=AluAlloyType.A6061_T6,
            Ag=4000.0,
            An=4000.0,
            Pu=500.0,
            is_welded_in_haz=False,
        )
        res_unwelded = check_alu_member(sec_unwelded)

        sec_welded = AluSectionInput(
            alloy=AluAlloyType.A6061_T6,
            Ag=4000.0,
            An=4000.0,
            Pu=500.0,
            is_welded_in_haz=True,
        )
        res_welded = check_alu_member(sec_welded)

        assert res_welded.khaz < 1.0
        assert res_welded.Fty_used == 140.0
        assert res_welded.phi_Pt < res_unwelded.phi_Pt
        assert res_welded.phi_Pc < res_unwelded.phi_Pc
        assert res_welded.phi_Mnx < res_unwelded.phi_Mnx

    def test_alu_column_buckling(self):
        """Test compression column buckling with different slenderness."""
        # Short column
        short_col = AluSectionInput(
            alloy=AluAlloyType.A6061_T6,
            Ag=4000.0,
            rx=80.0,
            ry=80.0,
            Lx=500.0,
            Ly=500.0,
            Pu=-200.0,  # Compression
            Mux=0.0,
            Muy=0.0,
            Vu=0.0,
        )
        res_short = check_alu_member(short_col)

        # Slender column
        slender_col = AluSectionInput(
            alloy=AluAlloyType.A6061_T6,
            Ag=4000.0,
            rx=80.0,
            ry=80.0,
            Lx=5000.0,
            Ly=5000.0,
            Pu=-200.0,
            Mux=0.0,
            Muy=0.0,
            Vu=0.0,
        )
        res_slender = check_alu_member(slender_col)

        assert res_short.phi_Pc > res_slender.phi_Pc
        assert res_short.slenderness_max < res_slender.slenderness_max

    def test_alu_beam_flexure_and_shear(self):
        """Test flexural strength and web shear strength."""
        beam_input = AluSectionInput(
            alloy=AluAlloyType.A6061_T6,
            Ag=5000.0,
            Aw=2000.0,
            Sx=400000.0,
            Zx=450000.0,
            Iy=15000000.0,
            J=100000.0,
            Cw=2000000000.0,
            Lb=2000.0,
            Pu=0.0,
            Mux=60.0,
            Muy=0.0,
            Vu=50.0,
        )
        res = check_alu_member(beam_input)

        assert res.phi_Mnx > 0.0
        assert res.phi_Vn > 0.0
        assert res.dcr_flexure_x <= 1.0
        assert res.dcr_shear <= 1.0
        assert res.is_safe is True
