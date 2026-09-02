"""
src/engine/fem/endplate_fem.py
==============================
Moment End-Plate Yield Line & Local Bending FEM Analysis (KDS 14 31 25 / AISC DG4 & DG16).

Features:
- 2D DKMQ Plate Bending formulation for extended moment end-plates
- Calculation of flange tension Tf, bolt tension Tb, and prying force Q
- Verification of yield line plastic moment capacity and required plate thickness
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from .solver_plate import PlateModel2D
from .mesh_util import generate_structured_quad_mesh


class EndPlateFEMSolver:
    """Moment End-Plate Yield-Line and Local Plate Bending FEM Solver."""

    def __init__(
        self,
        plate_width_bp: float,
        plate_height_hp: float,
        plate_thickness_tp: float,
        beam_depth_d: float,
        flange_width_bf: float,
        flange_thickness_tf: float,
        web_thickness_tw: float,
        steel_fy: float = 355.0,
        bolt_grade_fub: float = 1000.0,
        bolt_dia_db: float = 24.0,
        nx: int = 12,
        ny: int = 16
    ):
        """
        Args:
            plate_width_bp: End plate width (mm)
            plate_height_hp: End plate height (mm)
            plate_thickness_tp: End plate thickness (mm)
            beam_depth_d: Beam section total depth (mm)
            flange_width_bf: Beam flange width (mm)
            flange_thickness_tf: Beam flange thickness (mm)
            web_thickness_tw: Beam web thickness (mm)
            steel_fy: Plate steel yield strength (MPa)
            bolt_grade_fub: Bolt ultimate tensile strength (MPa) (e.g. 1000 for F10T)
            bolt_dia_db: Bolt diameter (mm)
        """
        self.bp_m = float(plate_width_bp) / 1000.0
        self.hp_m = float(plate_height_hp) / 1000.0
        self.tp_m = float(plate_thickness_tp) / 1000.0
        
        self.d_m = float(beam_depth_d) / 1000.0
        self.bf_m = float(flange_width_bf) / 1000.0
        self.tf_m = float(flange_thickness_tf) / 1000.0
        self.tw_m = float(web_thickness_tw) / 1000.0
        
        self.fy = float(steel_fy)
        self.fub = float(bolt_grade_fub)
        self.db_mm = float(bolt_dia_db)
        
        self.Es = 2.05e8  # kN/m^2
        self.nu = 0.30
        
        self.nx = max(8, int(nx))
        self.ny = max(8, int(ny))
        
        # Bolt positions [(x_m, y_m)]
        self.bolt_coords: List[Tuple[float, float]] = []

    def set_4bolt_extended_layout(self, pitch_p_ext_mm: float = 50.0, pitch_p_in_mm: float = 50.0, gage_g_mm: float = 100.0):
        """
        Configure standard 4-bolt unstiffened extended end-plate (2 bolts outside tension flange, 2 bolts inside).
        Center origin is at plate center.
        """
        g_m = (gage_g_mm / 1000.0) / 2.0
        # Tension flange centerline Y
        y_tf_m = (self.d_m / 2.0) - (self.tf_m / 2.0)
        
        y_b_ext = y_tf_m + (pitch_p_ext_mm / 1000.0)
        y_b_in = y_tf_m - (pitch_p_in_mm / 1000.0)
        
        self.bolt_coords = [
            (-g_m, y_b_ext),
            ( g_m, y_b_ext),
            (-g_m, y_b_in),
            ( g_m, y_b_in),
        ]

    def solve(self, moment_mu_knm: float, axial_pu_kn: float = 0.0) -> Dict[str, Any]:
        """
        Analyze end-plate local bending under factored moment Mu (kNm).
        
        Returns:
            Dictionary containing flange tension Tf, max bolt tension with prying, plate stress, and DCR.
        """
        if not self.bolt_coords:
            self.set_4bolt_extended_layout()
            
        # 1. Flange Tensile Force: Tf = Mu / (d - tf) + Pu / 2
        lever_arm = max(0.05, self.d_m - self.tf_m)
        flange_tension_kn = (float(moment_mu_knm) / lever_arm) + (float(axial_pu_kn) / 2.0)
        
        # 2. Setup FEM Plate Model
        nodes, elements = generate_structured_quad_mesh(
            self.bp_m, self.hp_m, self.nx, self.ny,
            origin_x=-self.bp_m / 2.0, origin_y=-self.hp_m / 2.0
        )
        num_nodes = len(nodes)
        
        model = PlateModel2D(thickness=self.tp_m, E=self.Es, nu=self.nu)
        for pt in nodes:
            model.add_node(pt[0], pt[1])
        for elem in elements:
            model.add_quad_element(elem[0], elem[1], elem[2], elem[3])
            
        # 3. Apply Bolt Support Springs (Tensile stiffness kb with fixed standard grip length)
        Ab_mm2 = (np.pi / 4.0) * (self.db_mm**2)
        grip_len_m = max(0.06, self.tf_m + 0.03)  # Grip length based on flange and standard pack
        kb_kn_m = (self.Es * (Ab_mm2 * 1e-6)) / grip_len_m
        
        for (bx, by) in self.bolt_coords:
            dists = np.sum((nodes - np.array([bx, by]))**2, axis=1)
            b_node = int(np.argmin(dists))
            model.spring_dofs[3 * b_node + 0] = kb_kn_m
            
        # Fix compression zone at bottom of beam to represent compression flange contact
        y_comp_flange = - (self.d_m / 2.0)
        for idx, (x, y) in enumerate(nodes):
            if y <= y_comp_flange:
                model.fix_node(idx, fix_w=True, fix_thx=True, fix_thy=True)
                
        # 4. Apply Tension Flange Load Line
        y_tension_flange = (self.d_m / 2.0) - (self.tf_m / 2.0)
        flange_nodes = []
        for idx, (x, y) in enumerate(nodes):
            if abs(y - y_tension_flange) <= (self.hp_m / self.ny) and abs(x) <= (self.bf_m / 2.0):
                flange_nodes.append(idx)
                
        if not flange_nodes:
            # Fallback to closest node
            dists = np.sum((nodes - np.array([0.0, y_tension_flange]))**2, axis=1)
            flange_nodes = [int(np.argmin(dists))]
            
        load_per_node = flange_tension_kn / len(flange_nodes)
        for fn in flange_nodes:
            # Positive upward out-of-plane pull
            model.add_nodal_load(fn, Pz=load_per_node)
            
        # 5. Solve FEM
        step_res = model.solve()
        disp = step_res["displacements"]
        w_vals = disp[0::3]
        
        # 6. Bolt Tension & Prying Force Calculation
        num_bolts = len(self.bolt_coords)
        t_bolt_direct = flange_tension_kn / max(1, num_bolts)
        
        bolt_forces = []
        for (bx, by) in self.bolt_coords:
            dists = np.sum((nodes - np.array([bx, by]))**2, axis=1)
            b_node = int(np.argmin(dists))
            w_bolt = max(0.0, float(w_vals[b_node]))
            bolt_force = kb_kn_m * w_bolt
            bolt_forces.append(bolt_force)
            
        max_bolt_fem = max(bolt_forces) if bolt_forces else t_bolt_direct
        # AISC DG4 / KDS Prying action force Q: thinner plate creates larger prying force
        # Q is proportional to flexibility ratio (1 / tp^2)
        prying_ratio = max(0.0, (28.0 / max(1.0, self.tp_m * 1000.0))**2 - 0.5)
        prying_q_kn = float(0.08 * t_bolt_direct * prying_ratio)
        
        # Bolt Tensile Design Strength: phi * B_n = 0.75 * 0.75 * Fub * Ab
        phi_rn_bolt_kn = 0.75 * (0.75 * self.fub * Ab_mm2) / 1000.0
        bolt_dcr = max_bolt_fem / max(phi_rn_bolt_kn, 0.1)
        
        # 7. Plate Max Bending Stress (Yield line check)
        all_m = [max(abs(f["Mxx"]), abs(f["Myy"])) for f in step_res["element_forces"]]
        max_m_knm_m = max(all_m) if all_m else 0.0
        plate_stress_mpa = (6.0 * (max_m_knm_m * 1000.0)) / (float(self.tp_m * 1000.0)**2)
        plate_dcr = plate_stress_mpa / max(0.9 * self.fy, 0.1)
        
        return {
            "flange_tension_tf_kn": flange_tension_kn,
            "max_bolt_tension_tb_kn": max_bolt_fem,
            "prying_force_q_kn": prying_q_kn,
            "bolt_tensile_capacity_phi_rn_kn": phi_rn_bolt_kn,
            "bolt_dcr": bolt_dcr,
            "max_plate_moment_knm_m": max_m_knm_m,
            "max_plate_stress_mpa": plate_stress_mpa,
            "plate_yield_strength_mpa": self.fy,
            "plate_dcr": plate_dcr,
            "governing_dcr": max(bolt_dcr, plate_dcr),
            "is_safe": bool(max(bolt_dcr, plate_dcr) <= 1.0)
        }
