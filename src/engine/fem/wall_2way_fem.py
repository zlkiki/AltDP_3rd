"""
src/engine/fem/wall_2way_fem.py
===============================
2-Way Basement Wall Finite Element Analysis Engine (KDS 14 20 00).

Features:
- 2D DKMQ Plate Bending formulation for basement retaining walls
- Multi-span / multi-level boundary condition supports (Fixed, Pinned, or Elastic)
- Trapezoidal lateral earth pressure, hydrostatic water pressure, and surcharge load distribution
- Calculation of horizontal moment (Mx), vertical moment (My), out-of-plane shear forces (Vxz, Vyz)
"""

import numpy as np
from typing import Dict, Any, List, Optional

from .solver_plate import PlateModel2D
from .mesh_util import generate_structured_quad_mesh


class Wall2WayFEMSolver:
    """2-Way Basement Wall Plate Bending FEM Solver."""

    def __init__(
        self,
        length_b: float,
        height_h: float,
        thickness: float,
        fck: float = 24.0,
        fy: float = 400.0,
        nx: int = 10,
        ny: int = 10,
        boundary_bottom: str = "FIXED",
        boundary_top: str = "PINNED",
        boundary_left: str = "PINNED",
        boundary_right: str = "PINNED"
    ):
        """
        Args:
            length_b: Wall span width (m)
            height_h: Wall story height (m)
            thickness: Wall thickness (m)
            fck: Concrete compressive strength (MPa)
            fy: Rebar yield strength (MPa)
            nx: Number of horizontal divisions
            ny: Number of vertical divisions
            boundary_*: Support condition: 'FIXED', 'PINNED', or 'FREE'
        """
        self.b = float(length_b)
        self.h = float(height_h)
        self.t = float(thickness)
        self.fck = float(fck)
        self.fy = float(fy)
        self.nx = max(4, int(nx))
        self.ny = max(4, int(ny))
        
        self.bound_bottom = boundary_bottom.upper()
        self.bound_top = boundary_top.upper()
        self.bound_left = boundary_left.upper()
        self.bound_right = boundary_right.upper()
        
        # Concrete Elastic Modulus (kN/m^2)
        self.Ec = 4700.0 * np.sqrt(self.fck) * 1000.0
        self.nu = 0.18

    def solve(
        self,
        soil_gamma: float = 18.0,
        water_table_depth: Optional[float] = None,
        surcharge_q: float = 10.0,
        k0: float = 0.5
    ) -> Dict[str, Any]:
        """
        Solve 2-way basement wall under lateral earth & water pressure.
        
        Args:
            soil_gamma: Soil unit weight (kN/m^3)
            water_table_depth: Depth from top of wall to water level (m). If None, dry.
            surcharge_q: Surface surcharge load (kN/m^2)
            k0: Lateral earth pressure coefficient at rest
            
        Returns:
            Dictionary containing max moments (Mx, My), shears, displacements, and rebar demands.
        """
        nodes, elements = generate_structured_quad_mesh(self.b, self.h, self.nx, self.ny)
        num_nodes = len(nodes)
        
        model = PlateModel2D(thickness=self.t, E=self.Ec, nu=self.nu)
        for pt in nodes:
            model.add_node(pt[0], pt[1])
        for elem in elements:
            model.add_quad_element(elem[0], elem[1], elem[2], elem[3])
            
        # 1. Apply Boundary Conditions
        # Node y = 0: Bottom
        # Node y = h: Top
        # Node x = 0: Left
        # Node x = b: Right
        for idx, (x, y) in enumerate(nodes):
            is_bottom = np.isclose(y, 0.0)
            is_top = np.isclose(y, self.h)
            is_left = np.isclose(x, 0.0)
            is_right = np.isclose(x, self.b)
            
            # Bottom
            if is_bottom:
                if self.bound_bottom == "FIXED":
                    model.fix_node(idx, fix_w=True, fix_thx=True, fix_thy=True)
                elif self.bound_bottom == "PINNED":
                    model.fix_node(idx, fix_w=True, fix_thx=False, fix_thy=False)
            # Top
            elif is_top:
                if self.bound_top == "FIXED":
                    model.fix_node(idx, fix_w=True, fix_thx=True, fix_thy=True)
                elif self.bound_top == "PINNED":
                    model.fix_node(idx, fix_w=True, fix_thx=False, fix_thy=False)
            # Left
            elif is_left:
                if self.bound_left == "FIXED":
                    model.fix_node(idx, fix_w=True, fix_thx=True, fix_thy=True)
                elif self.bound_left == "PINNED":
                    model.fix_node(idx, fix_w=True, fix_thx=False, fix_thy=False)
            # Right
            elif is_right:
                if self.bound_right == "FIXED":
                    model.fix_node(idx, fix_w=True, fix_thx=True, fix_thy=True)
                elif self.bound_right == "PINNED":
                    model.fix_node(idx, fix_w=True, fix_thx=False, fix_thy=False)

        # 2. Calculate Lateral Pressure Profile at each node
        # Depth z from top of wall: z = h - y
        dx = self.b / self.nx
        dy = self.h / self.ny
        
        for idx, (x, y) in enumerate(nodes):
            depth_z = max(0.0, self.h - y)
            
            # Earth pressure: p_earth = k0 * (q_surcharge + gamma * depth_z)
            p_lateral = k0 * (surcharge_q + soil_gamma * depth_z)
            
            # Water pressure if depth is below water table
            if water_table_depth is not None and depth_z > water_table_depth:
                water_head = depth_z - water_table_depth
                p_lateral += 9.81 * water_head
                
            # Tributary area for node
            factor_x = 0.5 if (np.isclose(x, 0.0) or np.isclose(x, self.b)) else 1.0
            factor_y = 0.5 if (np.isclose(y, 0.0) or np.isclose(y, self.h)) else 1.0
            node_area = (factor_x * dx) * (factor_y * dy)
            
            # Downward / Out-of-plane nodal force Pz = - p_lateral * Area
            model.add_nodal_load(idx, Pz=-p_lateral * node_area)

        # 3. Solve FEM Model
        step_res = model.solve()
        disp = step_res["displacements"]
        w_vals = disp[0::3]
        max_disp_mm = float(np.max(np.abs(w_vals))) * 1000.0
        
        # 4. Extract Element Moments & Out-of-plane Shears
        elem_forces = step_res["element_forces"]
        all_mx = [abs(f["Mxx"]) for f in elem_forces]  # Horizontal bending moment
        all_my = [abs(f["Myy"]) for f in elem_forces]  # Vertical bending moment
        all_vxz = [f["Vxz"] for f in elem_forces]
        all_vyz = [f["Vyz"] for f in elem_forces]
        
        max_mx = float(max(all_mx)) if all_mx else 0.0
        max_my = float(max(all_my)) if all_my else 0.0
        max_vx = float(max(all_vxz)) if all_vxz else 0.0
        max_vy = float(max(all_vyz)) if all_vyz else 0.0
        
        # Required rebar calculations (As = Mu / (0.9 * fy * 0.9 * d))
        eff_d = self.t - 0.05  # 50mm cover assumed
        as_req_horiz_mm2_m = (max_mx * 1e6) / (0.9 * self.fy * (0.9 * eff_d * 1000.0)) if eff_d > 0 else 0.0
        as_req_vert_mm2_m = (max_my * 1e6) / (0.9 * self.fy * (0.9 * eff_d * 1000.0)) if eff_d > 0 else 0.0
        
        # Minimum temperature & shrinkage rebar (KDS 14 20 20: 0.0020 * b * t)
        as_min_mm2_m = 0.0020 * 1000.0 * (self.t * 1000.0)
        
        return {
            "max_displacement_mm": max_disp_mm,
            "max_moment_mx_knm_m": max_mx,
            "max_moment_my_knm_m": max_my,
            "max_shear_vx_kn_m": max_vx,
            "max_shear_vy_kn_m": max_vy,
            "as_req_horizontal_mm2_m": max(as_req_horiz_mm2_m, as_min_mm2_m),
            "as_req_vertical_mm2_m": max(as_req_vert_mm2_m, as_min_mm2_m),
            "as_min_mm2_m": as_min_mm2_m,
            "num_elements": len(elements),
            "num_nodes": num_nodes
        }
