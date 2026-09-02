"""
src/engine/fem/foundation_fem.py
================================
Winkler Soil-Structure Interaction & Nonlinear Tension Cut-off Foundation FEM Solver.

Ground Truth: DgnSolver/Iterative.exe & DPLUS_DB.dll (CDBSolverTool)
Features:
- 2D Thick/Thin Plate Bending with Winkler Elastic Soil Springs (ks in kN/m^3)
- Nonlinear Tension Cut-off iteration for uplift separation
- Computes settlement w, subgrade soil reaction pressure q, and plate moments (Mxx, Myy)
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from .solver_plate import PlateModel2D


class FoundationFEMSolver:
    """Nonlinear Soil-Foundation Interaction FEM Solver."""

    def __init__(
        self,
        length_x: float,
        length_y: float,
        thickness: float,
        fck: float = 24.0,
        subgrade_modulus_ks: float = 20000.0,
        nx: int = 10,
        ny: int = 10
    ):
        """
        Args:
            length_x: Foundation width in X (m)
            length_y: Foundation length in Y (m)
            thickness: Mat/Footing thickness (m)
            fck: Concrete compressive strength (MPa)
            subgrade_modulus_ks: Modulus of subgrade reaction (kN/m^3)
            nx: Number of mesh subdivisions in X
            ny: Number of mesh subdivisions in Y
        """
        self.lx = float(length_x)
        self.ly = float(length_y)
        self.thickness = float(thickness)
        self.fck = float(fck)
        self.ks = float(subgrade_modulus_ks)
        self.nx = max(4, int(nx))
        self.ny = max(4, int(ny))
        
        # Concrete Elastic Modulus (KDS 14 20 00: Ec = 8500 * (fcu)^(1/3) MPa -> converted to kN/m^2)
        # Standard: Ec = 4700 * sqrt(fck) MPa = 4700 * sqrt(fck) * 1000 kN/m^2
        self.Ec = 4700.0 * np.sqrt(self.fck) * 1000.0
        self.nu = 0.18  # Concrete Poisson's ratio
        
        self.loads_column: List[Dict[str, float]] = []  # [{x, y, P, Mx, My}]

    def add_column_load(self, x: float, y: float, P: float, Mx: float = 0.0, My: float = 0.0):
        """Add column load P (kN, positive downward compression), Mx, My (kNm)."""
        self.loads_column.append({
            "x": float(x),
            "y": float(y),
            "P": float(P),
            "Mx": float(Mx),
            "My": float(My)
        })

    def solve_nonlinear(self, max_iter: int = 30, tol: float = 1e-4) -> Dict[str, Any]:
        """
        Execute nonlinear tension cut-off iterative analysis.
        
        Returns:
            Dict containing max_settlement, max_bearing_pressure, moment envelopes, and convergence status.
        """
        dx = self.lx / self.nx
        dy = self.ly / self.ny
        
        # 1. Generate Regular Grid Nodes
        nodes = []
        node_grid = np.zeros((self.ny + 1, self.nx + 1), dtype=int)
        for j in range(self.ny + 1):
            y = j * dy
            for i in range(self.nx + 1):
                x = i * dx
                node_grid[j, i] = len(nodes)
                nodes.append([x, y])
        nodes_arr = np.array(nodes)
        num_nodes = len(nodes)

        # 2. Calculate Tributary Area for each node
        trib_areas = np.zeros(num_nodes)
        for j in range(self.ny + 1):
            factor_y = 0.5 if (j == 0 or j == self.ny) else 1.0
            for i in range(self.nx + 1):
                factor_x = 0.5 if (i == 0 or i == self.nx) else 1.0
                idx = node_grid[j, i]
                trib_areas[idx] = (factor_x * dx) * (factor_y * dy)

        # 3. Initial active spring mask (all active)
        active_springs = np.ones(num_nodes, dtype=bool)
        converged = False
        final_result = None

        for iter_count in range(max_iter):
            model = PlateModel2D(self.thickness, self.Ec, self.nu)
            for pt in nodes:
                model.add_node(pt[0], pt[1])
                
            # Add Quad Elements (CCW: (i,j) -> (i+1,j) -> (i+1,j+1) -> (i,j+1))
            for j in range(self.ny):
                for i in range(self.nx):
                    n1 = node_grid[j, i]
                    n2 = node_grid[j, i + 1]
                    n3 = node_grid[j + 1, i + 1]
                    n4 = node_grid[j + 1, i]
                    model.add_quad_element(n1, n2, n3, n4)
                    
            # Apply active Winkler springs
            for idx in range(num_nodes):
                if active_springs[idx]:
                    k_spring = self.ks * trib_areas[idx]
                    model.spring_dofs[3 * idx + 0] = k_spring

            # Apply column loads to nearest grid node (or distributed)
            for cl in self.loads_column:
                # Find closest node
                dists = np.sum((nodes_arr - np.array([cl["x"], cl["y"]]))**2, axis=1)
                best_node = int(np.argmin(dists))
                # P > 0 is downward compression -> in FEM Pz is negative (downward)
                model.add_nodal_load(best_node, Pz=-cl["P"], Mx=cl["Mx"], My=cl["My"])

            # Solve linear step
            step_res = model.solve()
            disp = step_res["displacements"]
            w_settle = disp[0::3]  # Negative w is downward settlement

            # Tension separation check: w < 0 means downward compression (Soil engaged)
            # w > 0 means uplift tension (Soil separates -> ks = 0)
            new_active = w_settle < 0.0
            
            # Ensure at least 3 non-collinear springs remain active to prevent rigid body singularity
            if np.sum(new_active) < 3:
                new_active = np.ones(num_nodes, dtype=bool)

            changed = np.sum(new_active != active_springs)
            active_springs = new_active
            final_result = step_res

            if changed == 0:
                converged = True
                break

        # Post-Processing
        w_final = final_result["displacements"][0::3]
        # Soil Reaction Pressure: q_i = ks * |w_i| where active, else 0
        soil_pressure = np.zeros(num_nodes)
        for idx in range(num_nodes):
            if active_springs[idx] and w_final[idx] < 0.0:
                soil_pressure[idx] = self.ks * abs(w_final[idx])

        max_settlement_mm = float(np.max(np.abs(w_final))) * 1000.0  # mm
        max_pressure_kpa = float(np.max(soil_pressure))             # kN/m^2 (kPa)
        
        # Max Bending Moments
        all_mxx = [abs(f["Mxx"]) for f in final_result["element_forces"]]
        all_myy = [abs(f["Myy"]) for f in final_result["element_forces"]]
        max_mxx = float(max(all_mxx)) if all_mxx else 0.0
        max_myy = float(max(all_myy)) if all_myy else 0.0

        return {
            "converged": converged,
            "iterations": iter_count + 1,
            "max_settlement_mm": max_settlement_mm,
            "max_bearing_pressure_kpa": max_pressure_kpa,
            "max_moment_mxx_knm_m": max_mxx,
            "max_moment_myy_knm_m": max_myy,
            "soil_pressures": soil_pressure.tolist(),
            "settlements_m": w_final.tolist(),
            "active_area_ratio": float(np.sum(active_springs) / num_nodes)
        }
