"""
src/engine/fem/baseplate_fem.py
===============================
Nonlinear Contact FEM Solver for Steel Base Plates on Concrete Pedestals with Anchor Bolts.

Ground Truth: DPLUS_STEEL.dll (CUSBPPModeDlg, CESBPPModeDlg) / KDS 14 31 00
Features:
- 2D Thick/Thin Plate Bending for Steel Base Plate
- One-way Compression-only Concrete Bearing Springs
- Tension-only Anchor Bolt Springs with effective embedment stiffness
- Nonlinear Newton-Raphson contact iteration
- Exact calculation of peak concrete bearing stress fc, anchor bolt tension Tu, and plate bending stress fb
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from .solver_plate import PlateModel2D


class BasePlateFEMSolver:
    """Nonlinear Contact FEM Solver for Column Base Plates."""

    def __init__(
        self,
        plate_bx: float,
        plate_by: float,
        plate_thickness: float,
        steel_fy: float = 275.0,
        concrete_fck: float = 24.0,
        pedestal_bx: Optional[float] = None,
        pedestal_by: Optional[float] = None,
        nx: int = 12,
        ny: int = 12
    ):
        """
        Args:
            plate_bx: Base plate dimension in X (mm)
            plate_by: Base plate dimension in Y (mm)
            plate_thickness: Base plate thickness (mm)
            steel_fy: Steel yield strength (MPa)
            concrete_fck: Concrete design strength (MPa)
            pedestal_bx: Concrete pedestal dimension in X (mm)
            pedestal_by: Concrete pedestal dimension in Y (mm)
        """
        # Convert mm to m for internal SI FEM calculations
        self.bx_m = float(plate_bx) / 1000.0
        self.by_m = float(plate_by) / 1000.0
        self.tp_m = float(plate_thickness) / 1000.0
        
        self.fy_mpa = float(steel_fy)
        self.fck_mpa = float(concrete_fck)
        
        self.Es_kn_m2 = 2.05e8   # Steel Young's Modulus (205 GPa = 2.05e8 kN/m^2)
        self.nu_steel = 0.30
        
        # Concrete Modulus: Ec = 4700 * sqrt(fck) MPa
        self.Ec_mpa = 4700.0 * np.sqrt(self.fck_mpa)
        self.Ec_kn_m2 = self.Ec_mpa * 1000.0
        
        # Confinement factor sqrt(A2/A1) <= 2.0
        ped_bx = pedestal_bx / 1000.0 if pedestal_bx else self.bx_m
        ped_by = pedestal_by / 1000.0 if pedestal_by else self.by_m
        A1 = self.bx_m * self.by_m
        A2 = ped_bx * ped_by
        self.confinement_ratio = min(2.0, np.sqrt(A2 / A1))
        
        # Allowable concrete bearing stress: f_c_max = 0.85 * phi_c * fck * sqrt(A2/A1)
        self.fc_allowable_mpa = 0.85 * 0.65 * self.fck_mpa * self.confinement_ratio
        
        # Concrete equivalent compressive spring stiffness (kN/m^3)
        # Effective foundation depth ~ 2.0 * plate_thickness
        eff_depth = max(0.1, 2.0 * self.tp_m)
        self.k_concrete_kn_m3 = self.Ec_kn_m2 / eff_depth
        
        self.nx = max(6, int(nx))
        self.ny = max(6, int(ny))
        
        self.anchor_bolts: List[Dict[str, float]] = []  # [{x_m, y_m, d_bolt_mm, L_embed_mm}]
        self.profile_loads: List[Dict[str, float]] = []  # Column footprint loads

    def add_anchor_bolt(self, x_mm: float, y_mm: float, bolt_dia_mm: float = 24.0, embed_len_mm: float = 400.0):
        """Add an anchor bolt at (x_mm, y_mm) relative to plate center."""
        # Shift coordinate to corner origin (0, 0)
        x_from_origin = (self.bx_m / 2.0) + (x_mm / 1000.0)
        y_from_origin = (self.by_m / 2.0) + (y_mm / 1000.0)
        
        Ab_mm2 = (np.pi / 4.0) * (bolt_dia_mm**2)
        Ab_m2 = Ab_mm2 * 1e-6
        Le_m = embed_len_mm / 1000.0
        
        # Anchor Bolt Tension Stiffness: k_bolt = (Es * Ab) / Le (kN/m)
        k_bolt_kn_m = (self.Es_kn_m2 * Ab_m2) / max(Le_m, 0.05)
        
        self.anchor_bolts.append({
            "x": x_from_origin,
            "y": y_from_origin,
            "k_bolt": k_bolt_kn_m,
            "dia_mm": bolt_dia_mm
        })

    def set_column_load(self, P_kn: float, Mx_knm: float = 0.0, My_knm: float = 0.0):
        """Apply total column axial load P (kN, positive compression) and moments Mx, My at plate center."""
        self.profile_loads = [{
            "x": self.bx_m / 2.0,
            "y": self.by_m / 2.0,
            "P": float(P_kn),
            "Mx": float(Mx_knm),
            "My": float(My_knm)
        }]

    def solve_contact(self, max_iter: int = 25) -> Dict[str, Any]:
        """Execute nonlinear contact iteration for base plate."""
        dx = self.bx_m / self.nx
        dy = self.by_m / self.ny
        
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

        trib_areas = np.zeros(num_nodes)
        for j in range(self.ny + 1):
            factor_y = 0.5 if (j == 0 or j == self.ny) else 1.0
            for i in range(self.nx + 1):
                factor_x = 0.5 if (i == 0 or i == self.nx) else 1.0
                idx = node_grid[j, i]
                trib_areas[idx] = (factor_x * dx) * (factor_y * dy)

        # Map anchor bolts to nearest nodes
        bolt_nodes = []
        for ab in self.anchor_bolts:
            dists = np.sum((nodes_arr - np.array([ab["x"], ab["y"]]))**2, axis=1)
            b_node = int(np.argmin(dists))
            bolt_nodes.append((b_node, ab["k_bolt"]))

        # Nonlinear Contact Loop
        active_conc = np.ones(num_nodes, dtype=bool)
        active_bolts = np.ones(len(bolt_nodes), dtype=bool)
        converged = False
        final_result = None

        for iter_idx in range(max_iter):
            model = PlateModel2D(self.tp_m, self.Es_kn_m2, self.nu_steel)
            for pt in nodes:
                model.add_node(pt[0], pt[1])
                
            for j in range(self.ny):
                for i in range(self.nx):
                    n1 = node_grid[j, i]
                    n2 = node_grid[j, i + 1]
                    n3 = node_grid[j + 1, i + 1]
                    n4 = node_grid[j + 1, i]
                    model.add_quad_element(n1, n2, n3, n4)

            # 1. Concrete Compressive Springs (Active when settlement w < 0)
            for idx in range(num_nodes):
                if active_conc[idx]:
                    k_conc = self.k_concrete_kn_m3 * trib_areas[idx]
                    model.spring_dofs[3 * idx + 0] = model.spring_dofs.get(3 * idx + 0, 0.0) + k_conc

            # 2. Anchor Bolt Tensile Springs (Active when uplift w > 0)
            for b_idx, (b_node, k_b) in enumerate(bolt_nodes):
                if active_bolts[b_idx]:
                    model.spring_dofs[3 * b_node + 0] = model.spring_dofs.get(3 * b_node + 0, 0.0) + k_b

            # Apply Column Loads
            for cl in self.profile_loads:
                dists = np.sum((nodes_arr - np.array([cl["x"], cl["y"]]))**2, axis=1)
                c_node = int(np.argmin(dists))
                # P > 0 is downward compression -> in FEM Pz is negative
                model.add_nodal_load(c_node, Pz=-cl["P"], Mx=cl["Mx"], My=cl["My"])

            step_res = model.solve()
            w_settle = step_res["displacements"][0::3]

            # Contact update:
            # Concrete: active if w < 0 (downward compression)
            # Bolt: active if w > 0 (upward tension)
            new_active_conc = w_settle < 0.0
            new_active_bolts = np.array([w_settle[bn] > 0.0 for bn, _ in bolt_nodes], dtype=bool) if bolt_nodes else np.array([])

            changed_conc = np.sum(new_active_conc != active_conc)
            changed_bolts = np.sum(new_active_bolts != active_bolts) if len(active_bolts) > 0 else 0

            active_conc = new_active_conc
            active_bolts = new_active_bolts
            final_result = step_res

            if changed_conc == 0 and changed_bolts == 0:
                converged = True
                break

        # Output Results
        w_final = final_result["displacements"][0::3]
        conc_pressure_kpa = np.zeros(num_nodes)
        for idx in range(num_nodes):
            if active_conc[idx] and w_final[idx] < 0.0:
                conc_pressure_kpa[idx] = self.k_concrete_kn_m3 * abs(w_final[idx])

        # Max Bearing Stress (MPa = kPa / 1000)
        max_fc_mpa = float(np.max(conc_pressure_kpa)) / 1000.0
        
        # Max Bolt Tension (kN)
        bolt_tensions = []
        for b_idx, (b_node, k_b) in enumerate(bolt_nodes):
            if active_bolts[b_idx] and w_final[b_node] > 0.0:
                T_kn = float(k_b * w_final[b_node])
            else:
                T_kn = 0.0
            bolt_tensions.append(T_kn)
            
        max_tu_kn = max(bolt_tensions) if bolt_tensions else 0.0
        
        # Plate Max Bending Stress: sigma_b = 6 * M_max / (tp^2) (in MPa)
        all_m = [max(abs(f["Mxx"]), abs(f["Myy"])) for f in final_result["element_forces"]]
        max_m_knm_m = max(all_m) if all_m else 0.0
        # M in kNm/m = Nmm/mm. sigma = 6 * M / tp^2 (MPa)
        max_fb_mpa = (6.0 * (max_m_knm_m * 1000.0)) / (float(self.tp_m * 1000.0)**2)

        return {
            "converged": converged,
            "iterations": iter_idx + 1,
            "max_concrete_stress_mpa": max_fc_mpa,
            "allowable_concrete_stress_mpa": float(self.fc_allowable_mpa),
            "bearing_ratio": float(max_fc_mpa / max(self.fc_allowable_mpa, 0.1)),
            "max_bolt_tension_kn": max_tu_kn,
            "max_plate_stress_mpa": max_fb_mpa,
            "steel_yield_strength_mpa": self.fy_mpa,
            "plate_stress_ratio": float(max_fb_mpa / max(0.9 * self.fy_mpa, 0.1)),
            "active_bearing_ratio": float(np.sum(active_conc) / num_nodes)
        }
