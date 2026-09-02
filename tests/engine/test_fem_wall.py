"""Tests for 2-Way Basement Wall FEM Solver (Earth/Water lateral pressure)."""

import pytest
import numpy as np
from src.engine.fem.wall_2way_fem import Wall2WayFEMSolver


def test_2way_basement_wall_dry_earth_pressure():
    """Basement wall under dry earth pressure with fixed bottom and pinned edges."""
    wall = Wall2WayFEMSolver(
        length_b=6.0,
        height_h=3.5,
        thickness=0.35,
        fck=24.0,
        fy=400.0,
        nx=8,
        ny=8,
        boundary_bottom="FIXED",
        boundary_top="PINNED",
        boundary_left="PINNED",
        boundary_right="PINNED"
    )
    
    res = wall.solve(
        soil_gamma=19.0,
        water_table_depth=None,
        surcharge_q=10.0,
        k0=0.5
    )
    
    assert res["max_displacement_mm"] > 0.0
    assert res["max_displacement_mm"] < 10.0, "Lateral displacement should be reasonably small."
    assert res["max_moment_my_knm_m"] > 0.0
    assert res["max_moment_mx_knm_m"] > 0.0
    assert res["as_req_vertical_mm2_m"] >= res["as_min_mm2_m"]
    assert res["as_req_horizontal_mm2_m"] >= res["as_min_mm2_m"]


def test_2way_basement_wall_with_water_table():
    """Water table presence should increase lateral moments and required rebar."""
    wall_dry = Wall2WayFEMSolver(length_b=5.0, height_h=4.0, thickness=0.4, nx=6, ny=6)
    res_dry = wall_dry.solve(soil_gamma=18.0, water_table_depth=None, surcharge_q=5.0)
    
    wall_wet = Wall2WayFEMSolver(length_b=5.0, height_h=4.0, thickness=0.4, nx=6, ny=6)
    res_wet = wall_wet.solve(soil_gamma=18.0, water_table_depth=1.5, surcharge_q=5.0)
    
    assert res_wet["max_moment_my_knm_m"] > res_dry["max_moment_my_knm_m"]
    assert res_wet["max_displacement_mm"] > res_dry["max_displacement_mm"]
