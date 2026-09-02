"""Unit tests for KDS Material Models and Load Combination Envelope Engine (Phase 02-3)."""

import pytest
import math
from src.engine.materials import (
    ConcreteMaterial,
    RebarMaterial,
    SteelMaterial,
    get_phi_flexure,
    get_phi_shear,
    STEEL_STANDARDS_DB
)
from src.engine.load_comb import (
    MemberForces,
    LoadCase,
    LoadCombination,
    LoadCombinator,
    EnvelopeResult
)


@pytest.mark.engine
def test_high_strength_concrete_kds14():
    """Verify KDS 14 20 10 high strength concrete alpha1, beta1, and Ec."""
    # Normal strength fck = 24
    c24 = ConcreteMaterial(name="C24", fck=24.0)
    assert c24.alpha1 == 0.85
    assert c24.beta1 == 0.85
    assert c24.Ec == pytest.approx(8500.0 * (28.0 ** (1.0 / 3.0)), rel=1e-3)
    assert c24.f_cr == pytest.approx(0.63 * math.sqrt(24.0), rel=1e-3)

    # High strength fck = 60
    c60 = ConcreteMaterial(name="C60", fck=60.0)
    # alpha1 = 0.85 - 0.0015 * (60 - 40) = 0.82
    assert c60.alpha1 == pytest.approx(0.82, abs=1e-3)
    # beta1 <= 0.80
    assert c60.beta1 <= 0.80
    assert c60.beta1 >= 0.65


@pytest.mark.engine
def test_structural_steel_thickness_reduction():
    """Verify KDS 14 31 10 structural steel standard database and thickness reduction."""
    # SM355 with t = 12mm
    sm355_thin = SteelMaterial(name="SM355", thickness=12.0)
    assert sm355_thin.Fy == 355.0
    assert sm355_thin.Fy_design == 355.0

    # SM355 with t = 25mm -> Fy reduction of 10 MPa
    sm355_med = SteelMaterial(name="SM355", thickness=25.0)
    assert sm355_med.Fy_design == 345.0

    # SM355 with t = 50mm -> Fy reduction of 25 MPa
    sm355_thick = SteelMaterial(name="SM355", thickness=50.0)
    assert sm355_thick.Fy_design == 330.0

    # SHN460 lookup
    shn460 = SteelMaterial(name="SHN460", thickness=10.0)
    assert shn460.Fy == 460.0
    assert shn460.Fu == 550.0


@pytest.mark.engine
def test_load_combination_generation():
    """Test KDS 41 10 15 automated load combination generator."""
    combinator = LoadCombinator()
    
    # Add Dead, Live, Wind, Seismic cases
    combinator.add_load_case("D", MemberForces(P=-100.0, Vy=20.0, Mx=150.0), case_type="D")
    combinator.add_load_case("L", MemberForces(P=-50.0, Vy=10.0, Mx=80.0), case_type="L")
    combinator.add_load_case("W", MemberForces(P=-10.0, Vy=40.0, Mx=120.0), case_type="W")
    combinator.add_load_case("E", MemberForces(P=-5.0, Vy=60.0, Mx=200.0), case_type="E")

    combos = combinator.generate_kds41_combinations(
        d_name="D", l_name="L", w_names=["W"], e_names=["E"], include_sls=True
    )

    # Must contain 1.4D, 1.2D+1.6L, 1.2D+1.0L±1.0W, 1.2D+1.0L±1.0E, 0.9D±1.0W, 0.9D±1.0E, SLS
    assert len(combos) >= 8

    # Evaluate 1.4D: P = 1.4 * -100 = -140, Mx = 1.4 * 150 = 210
    c_14d = [c for c in combos if c.name == "1.4D"][0]
    f_14d = c_14d.evaluate(combinator.load_cases)
    assert f_14d.P == -140.0
    assert f_14d.Mx == 210.0

    # Evaluate 1.2D + 1.6L: P = -120 + -80 = -200, Mx = 1.2*150 + 1.6*80 = 180 + 128 = 308
    c_12d_16l = [c for c in combos if c.name == "1.2D + 1.6L"][0]
    f_12d_16l = c_12d_16l.evaluate(combinator.load_cases)
    assert f_12d_16l.P == -200.0
    assert f_12d_16l.Mx == 308.0


@pytest.mark.engine
def test_envelope_extraction():
    """Test governing envelope and critical load combination extraction."""
    combinator = LoadCombinator()
    combinator.add_load_case("D", MemberForces(P=-100.0, Vy=20.0, Mx=150.0))
    combinator.add_load_case("L", MemberForces(P=-50.0, Vy=10.0, Mx=80.0))
    combinator.add_load_case("W", MemberForces(P=30.0, Vy=50.0, Mx=-250.0))
    combinator.add_load_case("E", MemberForces(P=-20.0, Vy=80.0, Mx=350.0))

    combinator.generate_kds41_combinations(
        d_name="D", l_name="L", w_names=["W"], e_names=["E"]
    )

    env = combinator.extract_envelope(combo_type="ULS")

    # Max moment Mx should govern from seismic combo 1.2D + 1.0L + 1.0E
    # Mx = 1.2*150 + 1.0*80 + 1.0*350 = 180 + 80 + 350 = 610 kN*m
    assert env.max_Mx[0] == pytest.approx(610.0)
    assert "1.0E" in env.max_Mx[1]

    # Max Shear Vy should also be governed by seismic combo (Vy = 1.2*20 + 1.0*10 + 1.0*80 = 24+10+80 = 114)
    assert env.max_Vy[0] == pytest.approx(114.0)
