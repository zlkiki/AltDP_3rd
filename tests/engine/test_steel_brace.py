"""Unit Tests for Steel Brace and Web Opening Design Engine (KDS 14 31 10)."""

import math
import pytest

from src.engine.materials import SteelMaterial
from src.engine.steel.brace import (
    SteelBraceInput,
    SteelBraceResult,
    design_steel_brace,
    BraceConnection
)
from src.engine.steel.web_opening import (
    WebOpeningInput,
    WebOpeningResult,
    check_web_opening,
    OpeningShape
)


def test_steel_brace_tension_yielding_and_rupture():
    """Verify brace tension yield (Ag) and net section rupture (Ae with shear lag U)."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0)
    
    # Single Angle L-100x100x10, L=3000mm, 2-M20 bolts (d_hole=22mm)
    inp = SteelBraceInput(
        section_type="ANGLE",
        B=100.0, H=100.0, t=10.0,
        L=3000.0, K=1.0,
        connection_type=BraceConnection.BOLTED,
        bolt_hole_diameter=22.0,
        num_bolt_holes=2,
        connection_length_L=150.0,
        eccentricity_x_bar=28.2,
        Tu=300.0, Pu=100.0,
        material=mat
    )
    res = design_steel_brace(inp)
    
    # Ag = (200 - 10)*10 = 1900 mm2
    assert pytest.approx(res.Ag, rel=1e-3) == 1900.0
    # Expected Gross Yield: 0.90 * 355 * 1900 / 1000 = 607.05 kN
    assert pytest.approx(res.phi_Pn_yield, rel=1e-3) == 607.05
    
    # Net area An = 1900 - 2*22*10 = 1460 mm2
    assert pytest.approx(res.An, rel=1e-3) == 1460.0
    
    # Shear lag U = 1 - 28.2 / 150 = 0.812
    assert pytest.approx(res.U, rel=1e-3) == 0.812
    
    # Rupture strength: 0.75 * 490 * (0.812 * 1460) / 1000 = 435.63 kN
    assert pytest.approx(res.phi_Pn_rupture, rel=1e-2) == 435.63
    
    assert res.is_slenderness_tension_ok is True
    assert res.phi_Pn_comp > 0.0


def test_steel_web_opening_check():
    """Verify beam web opening shear and Vierendeel interaction."""
    mat = SteelMaterial(name="SM355", Fy=355.0, Fu=490.0)
    
    # Unreinforced rectangular opening
    inp_unreinf = WebOpeningInput(
        H=500.0, B=200.0, tw=9.0, tf=14.0,
        ao=300.0, ho=200.0, e=0.0,
        has_reinforcement=False,
        Mu=150.0, Vu=80.0,
        material=mat
    )
    res_unreinf = check_web_opening(inp_unreinf)
    assert res_unreinf.phi_Vn > 0.0
    assert res_unreinf.phi_Mn > 0.0
    assert res_unreinf.vierendeel_dcr > 0.0
    
    # Reinforced opening should have higher capacities
    inp_reinf = WebOpeningInput(
        H=500.0, B=200.0, tw=9.0, tf=14.0,
        ao=300.0, ho=200.0, e=0.0,
        has_reinforcement=True, br=80.0, tr=10.0,
        Mu=150.0, Vu=80.0,
        material=mat
    )
    res_reinf = check_web_opening(inp_reinf)
    assert res_reinf.phi_Mn > res_unreinf.phi_Mn
    assert res_reinf.max_dcr < res_unreinf.max_dcr
