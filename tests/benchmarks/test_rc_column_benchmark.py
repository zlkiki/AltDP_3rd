"""Executable Benchmark Specification & 3-Way Triangulation Tests for RC Column.

Conforms to Requirement 23 Step 3 and AGENTS.md Invariant 2 (Error <= 0.10%).
Directly verifies calculation engine outputs against Korea Concrete Institute (KCI 2020)
academic benchmark examples:
- Ex 5.1: Uniaxial flexure-compression short column (b=500, h=500, 8-D22)
- Ex 5.2/5.4: Slender column moment magnification (b=600, h=600, delta_ns, Pc, Mc)
- Ex 5.3: Biaxial bending with Bresler reciprocal method (Pu=5300, Mux=404, Muy=168)
"""

import os
import json
import math
import pytest
from typing import Dict, Any

from src.core.paths import BENCHMARKS_DIR
from src.engine.materials import ConcreteMaterial, RebarMaterial
from src.engine.rc.column import RCColumnInput, design_rc_column, evaluate_slenderness


BENCHMARK_FILE = os.path.join(os.path.dirname(__file__), "rc_column_benchmark.json")


def load_benchmark_data() -> Dict[str, Any]:
    """Load official KCI 2020 benchmark fixture data."""
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def benchmark_suite():
    return load_benchmark_data()


def test_rc_column_benchmark_triangulation(benchmark_suite):
    """Assert all benchmark targets achieve relative error <= 0.10% against KCI 2020 standards."""
    cases = benchmark_suite.get("cases", [])
    assert len(cases) >= 3, "Must contain at least 3 KCI 2020 column benchmarks"

    print("\n" + "=" * 92)
    print(f"{'CASE ID':<26} | {'PARAMETER':<18} | {'TARGET':<10} | {'ACTUAL':<10} | {'ERROR %':<8} | {'VERDICT'}")
    print("-" * 92)

    total_checks = 0
    passed_checks = 0

    for case in cases:
        case_id = case["case_id"]
        inp_data = case["input"]
        targets = case["targets"]

        concrete_mat = ConcreteMaterial(fck=inp_data.get("fck", 27.0))
        rebar_mat = RebarMaterial(fy=inp_data.get("fy", 400.0))

        col_inp = RCColumnInput(
            name=inp_data.get("name", case_id),
            b=inp_data["b"],
            h=inp_data["h"],
            cover=inp_data.get("cover", 60.0),
            bar_diam=inp_data.get("bar_diam", 25.0),
            total_bars=inp_data.get("total_bars", 12),
            tie_diam=inp_data.get("tie_diam", 10.0),
            tie_spacing=inp_data.get("tie_spacing", 300.0),
            Pu=inp_data.get("Pu", 1000.0),
            Mux=inp_data.get("Mux", 0.0),
            Muy=inp_data.get("Muy", 0.0),
            Vux=inp_data.get("Vux", 0.0),
            Vuy=inp_data.get("Vuy", 0.0),
            Lu=inp_data.get("Lu", 3000.0),
            k=inp_data.get("k", 1.0),
            is_braced=inp_data.get("is_braced", True),
            M1x=inp_data.get("M1x", 0.0),
            M2x=inp_data.get("M2x", inp_data.get("Mux", 0.0)),
            M1y=inp_data.get("M1y", 0.0),
            M2y=inp_data.get("M2y", inp_data.get("Muy", 0.0)),
            beta_dns=inp_data.get("beta_dns", 0.2),
            concrete=concrete_mat,
            rebar=rebar_mat
        )

        res = design_rc_column(col_inp)

        for param_key, target_meta in targets.items():
            total_checks += 1
            target_val = target_meta["val"]
            tol_pct = target_meta.get("tol_percent", 0.10)

            if hasattr(res, param_key):
                actual_val = getattr(res, param_key)
            elif hasattr(res.slenderness, param_key):
                actual_val = getattr(res.slenderness, param_key)
            else:
                pytest.fail(f"Attribute '{param_key}' not found on RCColumnDesignResult or SlendernessResult")

            error_pct = abs(float(actual_val) - float(target_val)) / abs(float(target_val)) * 100.0
            verdict = "PASS" if error_pct <= (tol_pct + 1e-4) else "FAIL"

            print(f"{case_id:<26} | {param_key:<18} | {target_val:<10.2f} | {actual_val:<10.2f} | {error_pct:<8.4f} | {verdict}")

            assert error_pct <= (tol_pct + 1e-4), (
                f"[{case_id}] {param_key}: actual={actual_val} vs target={target_val}, "
                f"error={error_pct:.4f}% exceeds tolerance {tol_pct:.2f}%"
            )
            passed_checks += 1

    print("=" * 92)
    print(f"Benchmark Summary: {passed_checks}/{total_checks} checks PASSED within <= 0.10% tolerance.")


def test_rc_column_tracer_ast_integrity(benchmark_suite):
    """Verify Tracer AST captures 5 KDS chapters, KaTeX formulas, substitutions, and evaluations."""
    case = benchmark_suite["cases"][0]
    inp_data = case["input"]

    col_inp = RCColumnInput(
        name="TracerCheck",
        b=inp_data["b"],
        h=inp_data["h"],
        cover=inp_data["cover"],
        bar_diam=inp_data["bar_diam"],
        total_bars=inp_data["total_bars"],
        Pu=inp_data["Pu"],
        Mux=inp_data["Mux"],
        concrete=ConcreteMaterial(fck=inp_data["fck"]),
        rebar=RebarMaterial(fy=inp_data["fy"])
    )

    res = design_rc_column(col_inp)

    # 1. Tracer AST existence
    assert res.tracer is not None
    tracer = res.tracer
    assert "chapters" in tracer
    assert len(tracer["chapters"]) >= 5, "Tracer must contain 5 KDS structural calculation chapters"

    # 2. All 8 key calculation steps check
    all_steps = tracer.get("all_steps", [])
    assert len(all_steps) >= 8, f"Expected at least 8 derivation steps, got {len(all_steps)}"

    for step in all_steps:
        assert step["formula"], "Formula cannot be empty"
        assert "\\" in step["formula"] or "=" in step["formula"], "Formula must contain LaTeX/KaTeX symbols"
        assert step["standard_ref"], "KDS standard reference must be present"
        assert step["result"], "Result cannot be empty"

    # 3. Evaluations check
    all_evals = tracer.get("all_evaluations", [])
    assert len(all_evals) >= 4, "Must contain at least 4 safety evaluations (rho, axial, pm, shear, tie)"
    for ev in all_evals:
        assert ev["status"] in ("OK", "NG")
        assert "dcr" in ev
        assert isinstance(ev["dcr"], (int, float))


def test_rc_column_parametric_geometry_integrity(benchmark_suite):
    """Verify SectionGeometry standard DTO conforms to core/geometry.py CAD specifications."""
    case = benchmark_suite["cases"][0]
    inp_data = case["input"]

    col_inp = RCColumnInput(
        name="GeomCheck",
        b=inp_data["b"],
        h=inp_data["h"],
        cover=inp_data["cover"],
        bar_diam=inp_data["bar_diam"],
        total_bars=inp_data["total_bars"],
        Pu=inp_data["Pu"],
        Mux=inp_data["Mux"],
        concrete=ConcreteMaterial(fck=inp_data["fck"]),
        rebar=RebarMaterial(fy=inp_data["fy"])
    )

    res = design_rc_column(col_inp)

    assert res.geometry is not None
    geom = res.geometry

    # 1. Boundary
    assert len(geom["boundary"]) == 4, "Boundary must be a 4-vertex closed polygon"

    # 2. Rebars
    assert len(geom["rebars"]) == inp_data["total_bars"], f"Rebar count must equal {inp_data['total_bars']}"

    # 3. Stirrups
    assert len(geom["stirrups"]) >= 1
    assert geom["stirrups"][0]["is_closed"] is True
    assert geom["stirrups"][0]["hook_angle"] == 135.0

    # 4. Dimensions
    assert len(geom["dimensions"]) >= 2

    # 5. P-M Curves
    assert geom["pm_curve_x"] is not None
    assert len(geom["pm_curve_x"]["nominal_curve"]) >= 100
    assert len(geom["pm_curve_x"]["design_curve"]) >= 100
    assert "demand_point" in geom["pm_curve_x"]
