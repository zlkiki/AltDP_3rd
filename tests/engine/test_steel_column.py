"""Unit Tests for Steel Column & Beam-Column Design Engine (KDS 14 31 10)."""

import math
import pytest

from src.engine.materials import SteelMaterial
from src.engine.steel.column import (
    SteelColumnInput,
    SteelColumnResult,
    design_steel_column
)


def test_steel_column_buckling_stress():
    """Verify Euler elastic and inelastic buckling stress calculations."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0)
    
    # 1. Short Column (Inelastic Buckling: KL/r <= 4.71*sqrt(E/Fy) = 113.2)
    # H-300x300x10x15, L=3000mm
    inp_short = SteelColumnInput(
        H=300.0, B=300.0, tw=10.0, tf=15.0,
        Lx=3000.0, Ly=3000.0, Kx=1.0, Ky=1.0,
        Pu=1500.0, Mux=50.0, Muy=20.0, material=mat
    )
    res_short = design_steel_column(inp_short)
    
    assert res_short.max_slenderness <= 113.2
    assert res_short.Fcr < 355.0
    # Inelastic Fcr = 0.658^(Fy/Fe) * Fy
    expected_fcr = (0.658 ** (355.0 / res_short.Fe)) * 355.0
    assert pytest.approx(res_short.Fcr, rel=1e-3) == expected_fcr
    
    # 2. Slender Column (Elastic Buckling: KL/r > 113.2)
    inp_slender = SteelColumnInput(
        H=300.0, B=300.0, tw=10.0, tf=15.0,
        Lx=10000.0, Ly=10000.0, Kx=1.0, Ky=1.0,
        Pu=200.0, Mux=10.0, Muy=5.0, material=mat
    )
    res_slender = design_steel_column(inp_slender)
    assert res_slender.max_slenderness > 113.2
    expected_elastic_fcr = 0.877 * res_slender.Fe
    assert pytest.approx(res_slender.Fcr, rel=1e-3) == expected_elastic_fcr


def test_steel_column_pm_interaction_branches():
    """Verify KDS 14 31 10 Eq 4.5-1 (Pu/phiPn >= 0.2) and Eq 4.5-2 (Pu/phiPn < 0.2)."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0)
    
    # 1. High axial compression: Pu / phiPn >= 0.2
    inp_high_p = SteelColumnInput(
        H=350.0, B=350.0, tw=12.0, tf=19.0,
        Lx=3500.0, Ly=3500.0,
        Pu=2000.0, Mux=100.0, Muy=30.0, material=mat
    )
    res_high_p = design_steel_column(inp_high_p)
    assert res_high_p.axial_dcr >= 0.20
    assert "Eq 4.5-1" in res_high_p.pm_formula
    expected_dcr_high = res_high_p.axial_dcr + (8.0 / 9.0) * (res_high_p.flexure_dcr_x + res_high_p.flexure_dcr_y)
    assert pytest.approx(res_high_p.pm_dcr, rel=1e-4) == expected_dcr_high
    
    # 2. Low axial compression: Pu / phiPn < 0.2
    inp_low_p = SteelColumnInput(
        H=350.0, B=350.0, tw=12.0, tf=19.0,
        Lx=3500.0, Ly=3500.0,
        Pu=200.0, Mux=150.0, Muy=50.0, material=mat
    )
    res_low_p = design_steel_column(inp_low_p)
    assert res_low_p.axial_dcr < 0.20
    assert "Eq 4.5-2" in res_low_p.pm_formula
    expected_dcr_low = (res_low_p.axial_dcr / 2.0) + (res_low_p.flexure_dcr_x + res_low_p.flexure_dcr_y)
    assert pytest.approx(res_low_p.pm_dcr, rel=1e-4) == expected_dcr_low


def test_box_and_pipe_column():
    """Verify box and pipe section column design under combined compression and bending."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0)
    
    # Box Column
    inp_box = SteelColumnInput(
        section_type="BOX",
        B=300.0, H=300.0, tw=12.0,
        Lx=4000.0, Ly=4000.0,
        Pu=1800.0, Mux=80.0, Muy=40.0, material=mat
    )
    res_box = design_steel_column(inp_box)
    assert res_box.phi_Pn > 0.0
    assert res_box.pm_dcr > 0.0
    assert res_box.is_slenderness_ok is True
    
    # Pipe Column
    inp_pipe = SteelColumnInput(
        section_type="PIPE",
        D=318.5, tw=10.3,
        Lx=3500.0, Ly=3500.0,
        Pu=1200.0, Mux=60.0, Muy=0.0, material=mat
    )
    res_pipe = design_steel_column(inp_pipe)
    assert res_pipe.phi_Pn > 0.0
    assert res_pipe.pm_dcr > 0.0
