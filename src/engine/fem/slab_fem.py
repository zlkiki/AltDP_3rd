"""
src/engine/fem/slab_fem.py
==========================
2D Irregular Slab with Openings FEM Analysis & Wood-Armer Design (KDS 14 20 70).

Features:
- 2D Plate Bending FEM for irregular boundary geometry and opening cutouts
- Multi-column point supports and wall line supports
- Wood-Armer moment field transformation (Mux*, Muy*) for orthogonal reinforcement design
- Column punching shear perimeter integration
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from .solver_plate import PlateModel2D
from .mesh_util import generate_structured_quad_mesh


class IrregularSlabFEMSolver:
    """2D Plate Bending FEM Solver for Slabs with Irregular Geometry and Openings."""

    def __init__(
        self,
        length_lx: float,
        length_ly: float,
        thickness: float,
        fck: float = 24.0,
        fy: float = 400.0,
        nx: int = 12,
        ny: int = 12
    ):
        """
        Args:
            length_lx: Slab dimension in X (m)
            length_ly: Slab dimension in Y (m)
            thickness: Slab thickness (m)
            fck: Concrete compressive strength (MPa)
            fy: Rebar yield strength (MPa)
            nx: Number of subdivisions in X
            ny: Number of subdivisions in Y
        """
        self.lx = float(length_lx)
        self.ly = float(length_ly)
        self.t = float(thickness)
        self.fck = float(fck)
        self.fy = float(fy)
        self.nx = max(6, int(nx))
        self.ny = max(6, int(ny))
        
        self.Ec = 4700.0 * np.sqrt(self.fck) * 1000.0  # kN/m^2
        self.nu = 0.18
        
        self.openings: List[Dict[str, float]] = []       # [{x_min, x_max, y_min, y_max}]
        self.column_supports: List[Dict[str, float]] = [] # [{x, y, col_bx, col_by}]
        self.wall_supports: List[Dict[str, float]] = []   # [{x1, y1, x2, y2}]
        self.area_loads: List[Dict[str, float]] = []     # [{q_dead, q_live}]

    def add_opening(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Add a rectangular opening cutout to the slab."""
        self.openings.append({
            "x_min": float(x_min),
            "x_max": float(x_max),
            "y_min": float(y_min),
            "y_max": float(y_max)
        })

    def add_column_support(self, x: float, y: float, col_bx_mm: float = 400.0, col_by_mm: float = 400.0):
        """Add column point support."""
        self.column_supports.append({
            "x": float(x),
            "y": float(y),
            "bx_m": float(col_bx_mm) / 1000.0,
            "by_m": float(col_by_mm) / 1000.0
        })

    def add_wall_support(self, x1: float, y1: float, x2: float, y2: float):
        """Add wall line support from (x1, y1) to (x2, y2)."""
        self.wall_supports.append({
            "x1": float(x1), "y1": float(y1),
            "x2": float(x2), "y2": float(y2)
        })

    def set_uniform_load(self, dead_load_kpa: float, live_load_kpa: float):
        """Apply uniform dead (kN/m^2) and live (kN/m^2) loads."""
        self.area_loads = [{"q_dead": float(dead_load_kpa), "q_live": float(live_load_kpa)}]

    def solve(self) -> Dict[str, Any]:
        """Execute slab FEM analysis with opening exclusion and Wood-Armer moment calculations."""
        nodes, elements = generate_structured_quad_mesh(self.lx, self.ly, self.nx, self.ny)
        
        # 1. Filter out elements located inside openings
        active_elements = []
        for elem in elements:
            elem_nodes = nodes[elem]
            center_x = np.mean(elem_nodes[:, 0])
            center_y = np.mean(elem_nodes[:, 1])
            
            inside_opening = False
            for op in self.openings:
                if (op["x_min"] <= center_x <= op["x_max"]) and (op["y_min"] <= center_y <= op["y_max"]):
                    inside_opening = True
                    break
            if not inside_opening:
                active_elements.append(elem)

        # 2. Build Plate Model
        model = PlateModel2D(thickness=self.t, E=self.Ec, nu=self.nu)
        for pt in nodes:
            model.add_node(pt[0], pt[1])
        for elem in active_elements:
            model.add_quad_element(elem[0], elem[1], elem[2], elem[3])
            
        # 3. Apply Column Supports (w=0, and rotational stiffness)
        for col in self.column_supports:
            dists = np.sum((nodes - np.array([col["x"], col["y"]]))**2, axis=1)
            c_node = int(np.argmin(dists))
            model.fix_node(c_node, fix_w=True, fix_thx=True, fix_thy=True)
            
        # 4. Apply Wall Supports
        for w in self.wall_supports:
            for idx, pt in enumerate(nodes):
                # Check line segment proximity
                px, py = pt[0], pt[1]
                if min(w["x1"], w["x2"]) - 1e-3 <= px <= max(w["x1"], w["x2"]) + 1e-3 and \
                   min(w["y1"], w["y2"]) - 1e-3 <= py <= max(w["y1"], w["y2"]) + 1e-3:
                    model.fix_node(idx, fix_w=True, fix_thx=False, fix_thy=False)

        # 5. Apply Factored Gravity Pressure: qu = 1.2 * D + 1.6 * L
        q_factored = 10.0  # default
        if self.area_loads:
            ld = self.area_loads[0]
            q_factored = 1.2 * ld["q_dead"] + 1.6 * ld["q_live"]
            
        for e_idx in range(len(active_elements)):
            model.pressure_loads[e_idx] = q_factored
            
        # 6. Solve FEM
        step_res = model.solve()
        disp = step_res["displacements"]
        w_vals = disp[0::3]
        max_disp_mm = float(np.max(np.abs(w_vals))) * 1000.0
        
        # 7. Wood-Armer Moment Transformations (KDS 14 20 70)
        # Top reinforcement design moments:
        #   Mx_top = Mx + |Mxy|  (if Mx > -|Mxy| else 0)
        #   My_top = My + |Mxy|
        # Bottom reinforcement design moments:
        #   Mx_bot = Mx - |Mxy|  (if Mx < |Mxy| else 0)
        #   My_bot = My - |Mxy|
        elem_forces = step_res["element_forces"]
        wood_armer_mx_bot = []
        wood_armer_my_bot = []
        wood_armer_mx_top = []
        wood_armer_my_top = []
        
        for f in elem_forces:
            mx = f["Mxx"]
            my = f["Myy"]
            mxy = abs(f["Mxy"])
            
            # Bottom (Positive sagging)
            # Mx_bot
            if mx >= -mxy:
                mux_bot = mx + mxy
            else:
                mux_bot = 0.0
            # My_bot
            if my >= -mxy:
                muy_bot = my + mxy
            else:
                muy_bot = 0.0
                
            # Top (Negative hogging)
            if mx <= mxy:
                mux_top = mx - mxy
            else:
                mux_top = 0.0
            if my <= mxy:
                muy_top = my - mxy
            else:
                muy_top = 0.0
                
            wood_armer_mx_bot.append(max(0.0, mux_bot))
            wood_armer_my_bot.append(max(0.0, muy_bot))
            wood_armer_mx_top.append(abs(min(0.0, mux_top)))
            wood_armer_my_top.append(abs(min(0.0, muy_top)))

        max_mux_bot = float(max(wood_armer_mx_bot)) if wood_armer_mx_bot else 0.0
        max_muy_bot = float(max(wood_armer_my_bot)) if wood_armer_my_bot else 0.0
        max_mux_top = float(max(wood_armer_mx_top)) if wood_armer_mx_top else 0.0
        max_muy_top = float(max(wood_armer_my_top)) if wood_armer_my_top else 0.0
        
        # 8. Punching Shear Check for Columns (KDS 14 20 22)
        # Critical perimeter at d/2
        d_eff = max(0.05, self.t - 0.04)  # 40mm cover
        phi_v = 0.75
        vc_punch_kpa = 0.75 * (0.33 * np.sqrt(self.fck) * 1000.0)
        
        punching_results = []
        for col in self.column_supports:
            b0 = 2.0 * ((col["bx_m"] + d_eff) + (col["by_m"] + d_eff))  # perimeter
            Ap = b0 * d_eff  # shear area
            # Total tributary column shear force
            vu_kn = q_factored * (self.lx * self.ly / max(1, len(self.column_supports)))
            vu_stress_kpa = vu_kn / max(0.01, Ap)
            dcr_punch = vu_stress_kpa / vc_punch_kpa
            punching_results.append({
                "column_pos": (col["x"], col["y"]),
                "perimeter_b0_m": b0,
                "vu_kn": vu_kn,
                "punching_stress_kpa": vu_stress_kpa,
                "punching_dcr": dcr_punch,
                "is_safe": bool(dcr_punch <= 1.0)
            })

        return {
            "max_deflection_mm": max_disp_mm,
            "factored_load_kpa": q_factored,
            "max_wood_armer_mx_bot_knm_m": max_mux_bot,
            "max_wood_armer_my_bot_knm_m": max_muy_bot,
            "max_wood_armer_mx_top_knm_m": max_mux_top,
            "max_wood_armer_my_top_knm_m": max_muy_top,
            "punching_shear_checks": punching_results,
            "active_elements_count": len(active_elements),
            "num_nodes": len(nodes)
        }
