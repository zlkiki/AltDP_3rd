"""Tests for 2D Irregular Slab FEM with Openings & Wood-Armer Transformation."""

import pytest
import numpy as np
from src.engine.fem.slab_fem import IrregularSlabFEMSolver


def test_slab_with_opening_and_wood_armer():
    """Verify irregular slab with a central opening cutout and 4 column supports."""
    slab = IrregularSlabFEMSolver(
        length_lx=8.0,
        length_ly=6.0,
        thickness=0.20,
        fck=24.0,
        fy=400.0,
        nx=10,
        ny=10
    )
    # Add opening in middle (from x=3 to 5, y=2 to 4)
    slab.add_opening(x_min=3.0, x_max=5.0, y_min=2.0, y_max=4.0)
    
    # 4 corner column supports
    slab.add_column_support(1.0, 1.0)
    slab.add_column_support(7.0, 1.0)
    slab.add_column_support(1.0, 5.0)
    slab.add_column_support(7.0, 5.0)
    
    slab.set_uniform_load(dead_load_kpa=4.5, live_load_kpa=2.5)
    
    res = slab.solve()
    
    assert res["active_elements_count"] < 100, "Elements inside opening must be excluded."
    assert res["max_deflection_mm"] > 0.0
    assert res["max_wood_armer_mx_bot_knm_m"] > 0.0
    assert res["max_wood_armer_my_bot_knm_m"] > 0.0
    assert len(res["punching_shear_checks"]) == 4
    for pchk in res["punching_shear_checks"]:
        assert pchk["punching_stress_kpa"] > 0.0
