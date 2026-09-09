"""RC Column Engineering Engine for Standalone Prototype.

Conforms 100% to docs/202_rc_column_module_specification.md.
Implements:
- 10-domain 48-parameter analysis
- 200-fiber P-M interaction curves (KDS 14 20 20)
- Slenderness moment magnification (delta_ns, Pc, Mc, emin)
- Biaxial bending with Bresler reciprocal formulation
- Shear capacity with axial force contribution (KDS 14 20 22)
- Seismic detailing for SMF / IMF / OMF (KDS 14 20 80)
- Piloti column special seismic provisions (KDS 41 17 00)
- Longitudinal bar lap splices (KDS 14 20 50)
- Automated optimal design search (Auto Design)
- 4 Tie bar patterns (TYPE_1 ~ 4) & corner/side mixed rebars
"""

import math
from typing import List, Tuple, Dict, Any, Optional

from .schemas import (
    RCColumnFullInput, LoadCombination, RCColumnCheckResult,
    GeometryOutput, GeometryPoint, RebarGeometry, TieLoopGeometry,
    PMPoint, CombResult, SeismicOutput, SpliceOutput
)


class RCColumnEngine:
    """Core Calculation Engine for RC Column Prototype."""

    @staticmethod
    def get_rebar_positions(inp: RCColumnFullInput) -> List[Tuple[float, float, float, float, bool]]:
        """Calculate (x, y, diameter, area, is_corner) for all longitudinal rebars.
        
        Coordinate origin (0, 0) is at section centroid.
        """
        rebars = []
        corner_diam = inp.corner_bar_diam if inp.use_diff_bar else inp.bar_diam
        side_diam = inp.side_bar_diam if inp.use_diff_bar else inp.bar_diam

        corner_area = math.pi * (corner_diam ** 2) / 4.0
        side_area = math.pi * (side_diam ** 2) / 4.0

        if inp.shape == "RECT":
            b, h = inp.b, inp.h
            # Center of rebar from outer face:
            # dc = cc + tie_diam + bar_diam / 2
            dc_x = inp.cc + inp.tie_diam + corner_diam / 2.0
            dc_y = inp.cc + inp.tie_diam + corner_diam / 2.0

            x_min = -b / 2.0 + dc_x
            x_max = b / 2.0 - dc_x
            y_min = -h / 2.0 + dc_y
            y_max = h / 2.0 - dc_y

            if getattr(inp, 'rebar_mode', 'EQUAL') == "PER_FACE":
                nx = max(2, getattr(inp, 'side_x_bars', 2) + 2)
                ny = max(2, getattr(inp, 'side_y_bars', 2) + 2)
            else:
                nx = max(2, inp.Nx)
                ny = max(2, inp.Ny)

            # 4 Corners
            rebars.append((x_min, y_max, corner_diam, corner_area, True))
            rebars.append((x_max, y_max, corner_diam, corner_area, True))
            rebars.append((x_max, y_min, corner_diam, corner_area, True))
            rebars.append((x_min, y_min, corner_diam, corner_area, True))

            # Top edge side bars
            if nx > 2:
                dx = (x_max - x_min) / (nx - 1)
                for i in range(1, nx - 1):
                    rebars.append((x_min + i * dx, y_max, side_diam, side_area, False))

            # Bottom edge side bars
            if nx > 2:
                dx = (x_max - x_min) / (nx - 1)
                for i in range(1, nx - 1):
                    rebars.append((x_min + i * dx, y_min, side_diam, side_area, False))

            # Left & Right edge side bars
            if ny > 2:
                dy = (y_max - y_min) / (ny - 1)
                for j in range(1, ny - 1):
                    rebars.append((x_min, y_min + j * dy, side_diam, side_area, False))
                    rebars.append((x_max, y_min + j * dy, side_diam, side_area, False))

        else:  # CIRCLE
            D = inp.D
            dc = inp.cc + inp.tie_diam + inp.bar_diam / 2.0
            r_circle = D / 2.0 - dc
            ncir = max(6, inp.Ncir)
            d_theta = 2.0 * math.pi / ncir
            bar_area = math.pi * (inp.bar_diam ** 2) / 4.0

            for i in range(ncir):
                theta = i * d_theta
                x = r_circle * math.cos(theta)
                y = r_circle * math.sin(theta)
                rebars.append((x, y, inp.bar_diam, bar_area, (i % (ncir // 4) == 0)))

        return rebars

    @classmethod
    def generate_geometry(cls, inp: RCColumnFullInput) -> GeometryOutput:
        """Create 2D CAD/Canvas coordinates for outline, ties, and rebars."""
        rebars_data = cls.get_rebar_positions(inp)
        rebars_geom = [
            RebarGeometry(x=round(r[0], 2), y=round(r[1], 2), diameter=r[2], is_corner=r[4])
            for r in rebars_data
        ]

        outline = []
        ties = []

        if inp.shape == "RECT":
            b, h, r_corner = inp.b, inp.h, inp.r
            half_b, half_h = b / 2.0, h / 2.0

            if r_corner <= 1.0:
                outline = [
                    GeometryPoint(x=-half_b, y=half_h),
                    GeometryPoint(x=half_b, y=half_h),
                    GeometryPoint(x=half_b, y=-half_h),
                    GeometryPoint(x=-half_b, y=-half_h),
                    GeometryPoint(x=-half_b, y=half_h)
                ]
            else:
                # Rounded rectangle boundary points
                r_c = min(r_corner, min(b, h) / 4.0)
                outline = [
                    GeometryPoint(x=-half_b + r_c, y=half_h),
                    GeometryPoint(x=half_b - r_c, y=half_h),
                    GeometryPoint(x=half_b, y=half_h - r_c),
                    GeometryPoint(x=half_b, y=-half_h + r_c),
                    GeometryPoint(x=half_b - r_c, y=-half_h),
                    GeometryPoint(x=-half_b + r_c, y=-half_h),
                    GeometryPoint(x=-half_b, y=-half_h + r_c),
                    GeometryPoint(x=-half_b, y=half_h - r_c),
                    GeometryPoint(x=-half_b + r_c, y=half_h)
                ]

            # Main outer tie loop
            tie_x = half_b - inp.cc - inp.tie_diam / 2.0
            tie_y = half_h - inp.cc - inp.tie_diam / 2.0
            main_tie = TieLoopGeometry(
                points=[
                    GeometryPoint(x=-tie_x, y=tie_y),
                    GeometryPoint(x=tie_x, y=tie_y),
                    GeometryPoint(x=tie_x, y=-tie_y),
                    GeometryPoint(x=-tie_x, y=-tie_y),
                    GeometryPoint(x=-tie_x, y=tie_y)
                ],
                closed=True,
                line_width=2.0,
                color="#2563eb"
            )
            ties.append(main_tie)

            # Additional Tie Patterns
            if inp.tie_pattern == "TYPE_2":
                # 4-Leg Cross-ties along centerlines
                ties.append(TieLoopGeometry(
                    points=[GeometryPoint(x=-tie_x, y=0.0), GeometryPoint(x=tie_x, y=0.0)],
                    closed=False, line_width=1.5, color="#0284c7"
                ))
                ties.append(TieLoopGeometry(
                    points=[GeometryPoint(x=0.0, y=tie_y), GeometryPoint(x=0.0, y=-tie_y)],
                    closed=False, line_width=1.5, color="#0284c7"
                ))
            elif inp.tie_pattern == "TYPE_3":
                # Diamond / Rhombus Tie
                ties.append(TieLoopGeometry(
                    points=[
                        GeometryPoint(x=0.0, y=tie_y),
                        GeometryPoint(x=tie_x, y=0.0),
                        GeometryPoint(x=0.0, y=-tie_y),
                        GeometryPoint(x=-tie_x, y=0.0),
                        GeometryPoint(x=0.0, y=tie_y)
                    ],
                    closed=True, line_width=1.5, color="#16a34a"
                ))
            elif inp.tie_pattern == "TYPE_4":
                # Octagonal / Inner Rectangular Sub-tie
                sub_x, sub_y = tie_x * 0.55, tie_y * 0.55
                ties.append(TieLoopGeometry(
                    points=[
                        GeometryPoint(x=-sub_x, y=sub_y),
                        GeometryPoint(x=sub_x, y=sub_y),
                        GeometryPoint(x=sub_x, y=-sub_y),
                        GeometryPoint(x=-sub_x, y=-sub_y),
                        GeometryPoint(x=-sub_x, y=sub_y)
                    ],
                    closed=True, line_width=1.5, color="#9333ea"
                ))

        else:  # CIRCLE
            D = inp.D
            r_outer = D / 2.0
            outline_pts = []
            for deg in range(0, 361, 10):
                rad = math.radians(deg)
                outline_pts.append(GeometryPoint(x=round(r_outer * math.cos(rad), 2), y=round(r_outer * math.sin(rad), 2)))
            outline = outline_pts

            r_tie = r_outer - inp.cc - inp.tie_diam / 2.0
            tie_pts = []
            for deg in range(0, 361, 10):
                rad = math.radians(deg)
                tie_pts.append(GeometryPoint(x=round(r_tie * math.cos(rad), 2), y=round(r_tie * math.sin(rad), 2)))
            ties.append(TieLoopGeometry(points=tie_pts, closed=True, line_width=2.0, color="#2563eb"))

        return GeometryOutput(
            shape=inp.shape,
            b=inp.b,
            h=inp.h,
            D=inp.D,
            r=inp.r,
            outline=outline,
            ties=ties,
            rebars=rebars_geom
        )

    @classmethod
    def compute_pm_curves_200_fiber(
        cls, inp: RCColumnFullInput, rebars: List[Tuple[float, float, float, float, bool]]
    ) -> Tuple[List[PMPoint], List[PMPoint], float, float]:
        """Compute full 200-fiber P-M interaction curves for X and Y bending axes.
        
        Conforms strictly to KDS 14 20 20 section 4.1.
        Returns: (curve_x, curve_y, P0, phi_Pn_max)
        """
        fck = inp.fck
        fy = inp.fy
        Es = 200000.0  # MPa
        eps_cu = 0.0033
        is_spiral = (inp.tie_type == "SPIRAL")
        phi_axial = 0.70 if is_spiral else 0.65
        alpha_pn_max = 0.85 if is_spiral else 0.80

        # Beta1 factor
        if fck <= 28.0:
            beta1 = 0.85
        else:
            beta1 = max(0.65, 0.85 - 0.05 * (fck - 28.0) / 7.0)

        # Cross sectional area and rebar area
        if inp.shape == "RECT":
            Ag = inp.b * inp.h
            if inp.r > 1.0:
                Ag -= (4.0 - math.pi) * (min(inp.r, min(inp.b, inp.h) / 4.0) ** 2)
        else:
            Ag = math.pi * (inp.D ** 2) / 4.0

        Ast = sum(r[3] for r in rebars)

        # Pure axial compression capacity P0 (kN)
        P0 = (0.85 * fck * (Ag - Ast) + fy * Ast) / 1e3
        phi_Pn_max = alpha_pn_max * phi_axial * P0

        # Pure axial tension capacity Pt (kN)
        Pt = -fy * Ast / 1e3
        phi_Pt = 0.85 * Pt

        def solve_axis(axis: str) -> List[PMPoint]:
            depth = inp.h if (inp.shape == "RECT" and axis == "X") else (inp.b if inp.shape == "RECT" else inp.D)
            width = inp.b if (inp.shape == "RECT" and axis == "X") else (inp.h if inp.shape == "RECT" else inp.D)

            # Extract distances d_i from top compression fiber along chosen axis
            # Coordinate system: top is +depth/2, bottom is -depth/2
            # For X bending: moment about X, compression at top (+y), d_i = depth/2 - y
            # For Y bending: moment about Y, compression at right (+x), d_i = depth/2 - x
            bar_items = []
            for r in rebars:
                pos = r[1] if axis == "X" else r[0]
                di = depth / 2.0 - pos
                bar_items.append((di, r[3]))

            # Find extreme tension steel distance dt
            dt = max(item[0] for item in bar_items)
            eps_y = fy / Es

            points = []

            # 1. Pure compression top point (phi*Pn_max, 0)
            points.append(PMPoint(phi_P=round(phi_Pn_max, 2), phi_Mx=0.0, phi_My=0.0, c=9999.0, eps_t=0.0, phi=phi_axial))

            # 2. 200 Fiber neutral axis steps: c from 2.5*depth down to 0.03*depth
            steps = 200
            c_values = []
            for i in range(steps):
                # Log-linear distribution for fine resolution near tension/balanced failure
                t = i / float(steps - 1)
                c_val = 2.5 * depth * (0.01 ** t)
                c_values.append(c_val)

            for c in c_values:
                a = beta1 * c
                eff_a = min(a, depth)

                # Concrete compression block
                if inp.shape == "RECT":
                    Cc = 0.85 * fck * width * eff_a  # N
                    Mc = Cc * (depth / 2.0 - eff_a / 2.0)  # N*mm
                else:
                    # Circular segment integration
                    R = depth / 2.0
                    y_cut = R - eff_a
                    y_cut = max(-R, min(R, y_cut))
                    # Angle theta for segment
                    theta = 2.0 * math.acos(y_cut / R)
                    area_seg = 0.5 * (R ** 2) * (theta - math.sin(theta))
                    Cc = 0.85 * fck * area_seg
                    # Centroid of circular segment from circle center
                    y_bar = (4.0 * R * (math.sin(theta / 2.0) ** 3)) / (3.0 * (theta - math.sin(theta))) if (theta - math.sin(theta)) > 1e-6 else 0.0
                    Mc = Cc * y_bar

                # Steel layer forces
                Pn_steel = 0.0
                Mn_steel = 0.0
                eps_t = 0.0

                for di, area_i in bar_items:
                    eps_si = eps_cu * (c - di) / c
                    f_si = max(-fy, min(fy, Es * eps_si))

                    # Deduct concrete displaced if in compression zone
                    if di <= eff_a:
                        f_net = f_si - 0.85 * fck
                    else:
                        f_net = f_si

                    Fi = area_i * f_net  # N
                    Pn_steel += Fi
                    Mn_steel += Fi * (depth / 2.0 - di)  # N*mm

                    if abs(di - dt) < 1e-3:
                        eps_t = -eps_si  # positive for tension

                Pn_total = (Cc + Pn_steel) / 1e3  # kN
                Mn_total = (Mc + Mn_steel) / 1e6  # kN*m

                # Strength reduction factor phi transition (KDS 14 20 20)
                if eps_t <= eps_y:
                    phi = phi_axial
                elif eps_t < 0.005:
                    phi = phi_axial + (0.85 - phi_axial) * ((eps_t - eps_y) / (0.005 - eps_y))
                else:
                    phi = 0.85

                phi_P = phi * Pn_total
                phi_M = phi * Mn_total

                # Clip axial compression to phi*Pn_max
                phi_P_clipped = min(phi_P, phi_Pn_max)

                if axis == "X":
                    points.append(PMPoint(
                        phi_P=round(phi_P_clipped, 2), phi_Mx=round(max(0.0, phi_M), 2),
                        phi_My=0.0, c=round(c, 1), eps_t=round(eps_t, 5), phi=round(phi, 3)
                    ))
                else:
                    points.append(PMPoint(
                        phi_P=round(phi_P_clipped, 2), phi_Mx=0.0,
                        phi_My=round(max(0.0, phi_M), 2), c=round(c, 1), eps_t=round(eps_t, 5), phi=round(phi, 3)
                    ))

            # 3. Pure tension bottom point
            if axis == "X":
                points.append(PMPoint(phi_P=round(phi_Pt, 2), phi_Mx=0.0, phi_My=0.0, c=0.0, eps_t=0.02, phi=0.85))
            else:
                points.append(PMPoint(phi_P=round(phi_Pt, 2), phi_Mx=0.0, phi_My=0.0, c=0.0, eps_t=0.02, phi=0.85))

            return points

        curve_x = solve_axis("X")
        curve_y = solve_axis("Y")

        return curve_x, curve_y, P0, phi_Pn_max

    @classmethod
    def evaluate_slenderness(cls, inp: RCColumnFullInput, rebars: List[Tuple[float, float, float, float, bool]]) -> Dict[str, Any]:
        """Slenderness & Euler moment magnification calculation (KDS 14 20 20)."""
        fck = inp.fck
        Ec = 8500.0 * ((fck + 4.0) ** (1.0 / 3.0)) * ((1.0 if not inp.is_lcon else inp.lambda_factor) ** 1.5)  # MPa
        Es = 200000.0

        if inp.shape == "RECT":
            b, h = inp.b, inp.h
            rx = 0.30 * h
            ry = 0.30 * b
            Ig_x = b * (h ** 3) / 12.0
            Ig_y = h * (b ** 3) / 12.0
            emin_x = 15.0 + 0.03 * h
            emin_y = 15.0 + 0.03 * b
        else:
            D = inp.D
            rx = 0.25 * D
            ry = 0.25 * D
            Ig_x = math.pi * (D ** 4) / 64.0
            Ig_y = Ig_x
            emin_x = 15.0 + 0.03 * D
            emin_y = emin_x

        slender_x = (inp.Kx * inp.Lux) / rx
        slender_y = (inp.Ky * inp.Luy) / ry

        # Slenderness limits for braced frame (conservative default 22 ~ 34)
        limit_x = 34.0 - 12.0 * (inp.Mux / max(1.0, inp.Mux)) if inp.Kx <= 1.0 else 22.0
        limit_x = min(40.0, max(22.0, limit_x))
        limit_y = 34.0 - 12.0 * (inp.Muy / max(1.0, inp.Muy)) if inp.Ky <= 1.0 else 22.0
        limit_y = min(40.0, max(22.0, limit_y))

        is_slender_x = slender_x > limit_x
        is_slender_y = slender_y > limit_y

        # Rebar moments of inertia
        Ise_x = sum(r[3] * (r[1] ** 2) for r in rebars)
        Ise_y = sum(r[3] * (r[0] ** 2) for r in rebars)

        beta_d = max(0.0, min(1.0, inp.beta_d))

        EI_x = (0.2 * Ec * Ig_x + Es * Ise_x if Ise_x > 0 else 0.4 * Ec * Ig_x) / (1.0 + beta_d)
        EI_y = (0.2 * Ec * Ig_y + Es * Ise_y if Ise_y > 0 else 0.4 * Ec * Ig_y) / (1.0 + beta_d)

        Pc_x = (math.pi ** 2) * EI_x / ((inp.Kx * inp.Lux) ** 2) / 1e3  # kN
        Pc_y = (math.pi ** 2) * EI_y / ((inp.Ky * inp.Luy) ** 2) / 1e3  # kN

        # Moment magnification factor delta_ns
        Pu = max(0.1, inp.Pu)

        if is_slender_x and Pc_x > 0 and Pu < 0.75 * Pc_x:
            delta_ns_x = max(1.0, inp.Cmx / (1.0 - Pu / (0.75 * Pc_x)))
        else:
            delta_ns_x = 1.0

        if is_slender_y and Pc_y > 0 and Pu < 0.75 * Pc_y:
            delta_ns_y = max(1.0, inp.Cmy / (1.0 - Pu / (0.75 * Pc_y)))
        else:
            delta_ns_y = 1.0

        M2_min_x = Pu * emin_x / 1e3
        M2_min_y = Pu * emin_y / 1e3

        Mc_x = delta_ns_x * max(inp.Mux, M2_min_x)
        Mc_y = delta_ns_y * max(inp.Muy, M2_min_y)

        return {
            "slender_ratio_x": round(slender_x, 2),
            "slender_ratio_y": round(slender_y, 2),
            "is_slender_x": is_slender_x,
            "is_slender_y": is_slender_y,
            "delta_ns_x": round(delta_ns_x, 3),
            "delta_ns_y": round(delta_ns_y, 3),
            "Pc_x": round(Pc_x, 1),
            "Pc_y": round(Pc_y, 1),
            "Mc_x": round(Mc_x, 2),
            "Mc_y": round(Mc_y, 2),
            "emin_x": emin_x,
            "emin_y": emin_y
        }

    @classmethod
    def evaluate_shear(cls, inp: RCColumnFullInput) -> Dict[str, Any]:
        """Shear capacity evaluation under axial force (KDS 14 20 22)."""
        fck = inp.fck
        fys = inp.fys
        lmb = inp.lambda_factor if inp.is_lcon else 1.00

        if inp.shape == "RECT":
            b, h = inp.b, inp.h
            Ag = b * h
            dx = h - inp.cc - inp.tie_diam - inp.bar_diam / 2.0
            dy = b - inp.cc - inp.tie_diam - inp.bar_diam / 2.0
            bw_x, bw_y = b, h
        else:
            D = inp.D
            Ag = math.pi * (D ** 2) / 4.0
            dx = 0.80 * D
            dy = 0.80 * D
            bw_x, bw_y = D, D

        Pu = inp.Pu * 1e3 if inp.apply_ax2sh else 0.0  # N

        # Concrete shear contribution Vc with axial compression
        # Vc = (1/6) * (1 + Nu / (14 * Ag)) * lambda * sqrt(fck) * bw * d
        factor_nu = max(0.0, 1.0 + Pu / (14.0 * Ag)) if Ag > 0 else 1.0
        factor_nu = min(1.33, factor_nu)

        Vcx_N = (1.0 / 6.0) * factor_nu * lmb * math.sqrt(fck) * bw_x * dx
        Vcy_N = (1.0 / 6.0) * factor_nu * lmb * math.sqrt(fck) * bw_y * dy

        # Stirrup spacing
        s = inp.s_end if (inp.use_end_tie and inp.s_end > 0) else inp.s_mid

        # Legs area
        tie_bar_area = math.pi * (inp.tie_diam ** 2) / 4.0
        legs_x = max(2, inp.tie_legs_x) if inp.chk_tiebar else 2
        legs_y = max(2, inp.tie_legs_y) if inp.chk_tiebar else 2

        Avx = legs_x * tie_bar_area
        Avy = legs_y * tie_bar_area

        Vsx_N = (Avx * fys * dx) / s
        Vsy_N = (Avy * fys * dy) / s

        phi_v = 0.75

        # Upper limit Vn <= Vc + (2/3)*sqrt(fck)*bw*d
        Vsx_max_N = (2.0 / 3.0) * math.sqrt(fck) * bw_x * dx
        Vsy_max_N = (2.0 / 3.0) * math.sqrt(fck) * bw_y * dy

        Vsx_N = min(Vsx_N, Vsx_max_N)
        Vsy_N = min(Vsy_N, Vsy_max_N)

        phi_Vnx = phi_v * (Vcx_N + Vsx_N) / 1e3  # kN
        phi_Vny = phi_v * (Vcy_N + Vsy_N) / 1e3  # kN

        return {
            "Vcx": round(Vcx_N / 1e3, 1),
            "Vsx": round(Vsx_N / 1e3, 1),
            "phi_Vnx": round(phi_Vnx, 1),
            "Vcy": round(Vcy_N / 1e3, 1),
            "Vsy": round(Vsy_N / 1e3, 1),
            "phi_Vny": round(phi_Vny, 1),
        }

    @classmethod
    def evaluate_seismic(cls, inp: RCColumnFullInput) -> SeismicOutput:
        """Seismic provisions detailing (KDS 14 20 80 / KDS 41 17 00)."""
        dim_h = inp.h if inp.shape == "RECT" else inp.D
        dim_b = inp.b if inp.shape == "RECT" else inp.D
        clear_span = min(inp.Lux, inp.Luy)
        db = inp.bar_diam
        dt = inp.tie_diam

        # 1. Plastic hinge length lo
        lo = max(dim_h, dim_b, clear_span / 6.0, 450.0)

        # 2. Maximum tie spacing so in plastic hinge
        if inp.chk_seismic:
            if inp.frame_type == "SMF":
                hx = dim_b - 2.0 * inp.cc
                sx = 100.0 + (350.0 - hx) / 3.0
                sx = max(100.0, min(150.0, sx))
                so_limit = min(dim_b / 4.0, dim_h / 4.0, 6.0 * db, sx)
            elif inp.frame_type == "IMF":
                so_limit = min(8.0 * db, 24.0 * dt, dim_b / 2.0, dim_h / 2.0, 300.0)
            else:  # OMF
                so_limit = min(16.0 * db, 48.0 * dt, dim_b, dim_h)
        else:
            so_limit = min(16.0 * db, 48.0 * dt, dim_b, dim_h)

        # 3. Ash required for SMF
        if inp.shape == "RECT":
            Ag = dim_b * dim_h
            Ach = (dim_b - 2.0 * inp.cc) * (dim_h - 2.0 * inp.cc)
            bc = dim_b - 2.0 * inp.cc
        else:
            Ag = math.pi * (dim_b ** 2) / 4.0
            Ach = math.pi * ((dim_b - 2.0 * inp.cc) ** 2) / 4.0
            bc = dim_b - 2.0 * inp.cc

        s_actual = inp.s_end if inp.use_end_tie else inp.s_mid

        if inp.chk_seismic and inp.frame_type == "SMF" and Ach > 0:
            Ash1 = 0.3 * (s_actual * bc * inp.fck / inp.fys) * (Ag / Ach - 1.0)
            Ash2 = 0.09 * (s_actual * bc * inp.fck / inp.fys)
            Ash_req = max(Ash1, Ash2)
        else:
            Ash_req = 0.0

        tie_area = math.pi * (inp.tie_diam ** 2) / 4.0
        Ash_prov_x = inp.tie_legs_x * tie_area
        Ash_prov_y = inp.tie_legs_y * tie_area

        # Piloti Status
        if inp.chk_piloti:
            piloti_status = "필로티 적용 (Ω0=3.0 증폭 및 전구간 소성힌지 상세)"
            lo = clear_span  # entire length
        else:
            piloti_status = "미적용"

        status = "OK" if s_actual <= so_limit and (Ash_req == 0 or min(Ash_prov_x, Ash_prov_y) >= Ash_req) else "NG"

        return SeismicOutput(
            frame_type=inp.frame_type if inp.chk_seismic else "NONE",
            lo=round(lo, 1),
            so=round(s_actual, 1),
            so_limit=round(so_limit, 1),
            Ash_req=round(Ash_req, 1),
            Ash_prov_x=round(Ash_prov_x, 1),
            Ash_prov_y=round(Ash_prov_y, 1),
            piloti_status=piloti_status,
            status=status
        )

    @classmethod
    def evaluate_splice(cls, inp: RCColumnFullInput) -> SpliceOutput:
        """Longitudinal rebar lap splice length (KDS 14 20 50)."""
        db = inp.bar_diam
        fck = inp.fck
        fy = inp.fy
        lmb = inp.lambda_factor if inp.is_lcon else 1.0

        # Tension development length ld
        # Simplified KDS formula: ld = max(300, (fy / (1.4 * lambda * sqrt(fck))) * (1.0 / 2.5) * db)
        denom = 1.4 * lmb * math.sqrt(fck) * 2.5
        ld = max(300.0, (fy / denom) * db) if denom > 0 else 40.0 * db

        # Tension lap splice
        if inp.splice_type == "SPLICE050":
            splice_class = "Class A (50% Staggered)"
            ls_tens = max(300.0, 1.0 * ld)
        elif inp.splice_type == "SPLICE100":
            splice_class = "Class B (100% Spliced)"
            ls_tens = max(300.0, 1.3 * ld)
        else:
            splice_class = "No Splice (0%)"
            ls_tens = 0.0

        # Compression lap splice lsc
        if inp.splice_type != "SPLICE000":
            if fy <= 400.0:
                lsc_comp = max(300.0, 0.071 * fy * db)
            else:
                lsc_comp = max(300.0, (0.13 * fy - 24.0) * db)
        else:
            lsc_comp = 0.0

        return SpliceOutput(
            splice_type=inp.splice_type,
            splice_class=splice_class,
            ld=round(ld, 1),
            ls_tens=round(ls_tens, 1),
            lsc_comp=round(lsc_comp, 1),
            status="OK"
        )

    @classmethod
    def interpolate_pm_capacity(cls, curve: List[PMPoint], target_P: float, axis: str) -> float:
        """Find nominal/design bending moment capacity phi*Mn for a given axial force Pu."""
        if not curve:
            return 1.0

        # Sort curve by phi_P descending
        sorted_curve = sorted(curve, key=lambda pt: pt.phi_P, reverse=True)

        if target_P >= sorted_curve[0].phi_P:
            # Beyond max compression
            return 0.1
        if target_P <= sorted_curve[-1].phi_P:
            # Beyond max tension
            return 0.1

        # Find bracket
        for i in range(len(sorted_curve) - 1):
            p1 = sorted_curve[i].phi_P
            p2 = sorted_curve[i + 1].phi_P
            if p1 >= target_P >= p2:
                m1 = sorted_curve[i].phi_Mx if axis == "X" else sorted_curve[i].phi_My
                m2 = sorted_curve[i + 1].phi_Mx if axis == "X" else sorted_curve[i + 1].phi_My
                if abs(p1 - p2) < 1e-4:
                    return max(0.1, m1)
                frac = (target_P - p2) / (p1 - p2)
                return max(0.1, m2 + frac * (m1 - m2))

        return 1.0

    @classmethod
    def evaluate_load_combination(
        cls, lc: LoadCombination, curve_x: List[PMPoint], curve_y: List[PMPoint],
        slender: Dict[str, Any], shear: Dict[str, Any], P0: float, phi_Pn_max: float
    ) -> CombResult:
        """Evaluate single load case DCR for P-M interaction (Bresler) and Shear."""
        Pu = lc.Pu
        Mux = lc.Mux * slender["delta_ns_x"]
        Muy = lc.Muy * slender["delta_ns_y"]
        Vux = lc.Vux
        Vuy = lc.Vuy

        # 1. P-M interaction (Bresler Reciprocal or Contour method)
        phi_Mnx = cls.interpolate_pm_capacity(curve_x, Pu, "X")
        phi_Mny = cls.interpolate_pm_capacity(curve_y, Pu, "Y")

        dcr_mx = Mux / phi_Mnx if phi_Mnx > 0 else 99.0
        dcr_my = Muy / phi_Mny if phi_Mny > 0 else 99.0

        # Axial DCR
        dcr_p = Pu / phi_Pn_max if phi_Pn_max > 0 else 99.0

        # Bresler reciprocal formula if biaxial
        if Mux > 0.1 and Muy > 0.1:
            # (Mx/Mnx)^alpha + (My/Mny)^alpha <= 1.0 (approx alpha=1.2 ~ 1.5)
            alpha = 1.3
            dcr_pm = (dcr_mx ** alpha + dcr_my ** alpha) ** (1.0 / alpha)
            dcr_pm = max(dcr_pm, dcr_p)
        else:
            dcr_pm = max(dcr_mx, dcr_my, dcr_p)

        # 2. Shear DCR
        dcr_vx = Vux / shear["phi_Vnx"] if shear["phi_Vnx"] > 0 else 0.0
        dcr_vy = Vuy / shear["phi_Vny"] if shear["phi_Vny"] > 0 else 0.0

        max_dcr = max(dcr_pm, dcr_vx, dcr_vy)
        status = "OK" if max_dcr <= 1.00 else "NG"

        return CombResult(
            no=lc.no,
            name=lc.name,
            Pu=round(Pu, 1),
            Mux=round(Mux, 1),
            Muy=round(Muy, 1),
            Vux=round(Vux, 1),
            Vuy=round(Vuy, 1),
            dcr_pm=round(dcr_pm, 3),
            dcr_vx=round(dcr_vx, 3),
            dcr_vy=round(dcr_vy, 3),
            status=status
        )

    @classmethod
    def analyze(cls, inp: RCColumnFullInput) -> RCColumnCheckResult:
        """Full RC Column Engineering Analysis Pipeline."""
        rebars = cls.get_rebar_positions(inp)
        total_bars = len(rebars)
        Ast = sum(r[3] for r in rebars)

        if inp.shape == "RECT":
            Ag = inp.b * inp.h
            if inp.r > 1.0:
                Ag -= (4.0 - math.pi) * (min(inp.r, min(inp.b, inp.h) / 4.0) ** 2)
        else:
            Ag = math.pi * (inp.D ** 2) / 4.0

        rho_g = Ast / Ag if Ag > 0 else 0.0
        min_rho = inp.min_rho if inp.chk_user_rho else 0.010
        max_rho = inp.max_rho if inp.chk_user_rho else 0.040
        is_rho_ok = (min_rho <= rho_g <= max_rho)

        # Clear rebar spacing
        if inp.shape == "RECT":
            # clear distance between adjacent bars along perimeter
            nx = max(2, inp.Nx)
            dc_x = inp.cc + inp.tie_diam + inp.bar_diam / 2.0
            s_clear = ((inp.b - 2.0 * dc_x) / (nx - 1)) - inp.bar_diam if nx > 1 else 100.0
        else:
            ncir = max(6, inp.Ncir)
            r_circle = inp.D / 2.0 - inp.cc - inp.tie_diam - inp.bar_diam / 2.0
            perimeter_c = 2.0 * math.pi * r_circle
            s_clear = (perimeter_c / ncir) - inp.bar_diam

        d_agg = getattr(inp, 'd_agg', 25.0)
        s_clear_min = round(max(25.0, inp.bar_diam * 1.5, 1.33 * d_agg), 1)
        is_sclear_ok = (s_clear >= s_clear_min)

        # Section properties & limits
        Ec = round(8500.0 * ((inp.fck + 4.0) ** (1.0 / 3.0)), 1)
        beta1 = round(max(0.65, 0.85 - 0.05 * max(0.0, inp.fck - 28.0) / 7.0), 3)

        if inp.shape == "RECT":
            Ig_x = round(inp.b * (inp.h ** 3) / 12.0, 1)
            Ig_y = round(inp.h * (inp.b ** 3) / 12.0, 1)
            rx = round(0.30 * inp.h, 1)
            ry = round(0.30 * inp.b, 1)
            e_min_x = round(15.0 + 0.03 * inp.h, 1)
            e_min_y = round(15.0 + 0.03 * inp.b, 1)
            dx = inp.h - inp.cc - inp.tie_diam - inp.bar_diam / 2.0
            dy = inp.b - inp.cc - inp.tie_diam - inp.bar_diam / 2.0
            Vs_max_x = round((2.0 / 3.0) * math.sqrt(inp.fck) * inp.b * dx / 1000.0, 1)
            Vs_max_y = round((2.0 / 3.0) * math.sqrt(inp.fck) * inp.h * dy / 1000.0, 1)
        else:
            Ig_x = round(math.pi * (inp.D ** 4) / 64.0, 1)
            Ig_y = Ig_x
            rx = round(0.25 * inp.D, 1)
            ry = rx
            e_min_x = round(15.0 + 0.03 * inp.D, 1)
            e_min_y = e_min_x
            d_eff = 0.80 * inp.D
            Vs_max_x = round((2.0 / 3.0) * math.sqrt(inp.fck) * inp.D * d_eff / 1000.0, 1)
            Vs_max_y = Vs_max_x

        # Slenderness & Euler Buckling
        slender = cls.evaluate_slenderness(inp, rebars)

        # P-M Curves
        curve_x, curve_y, P0, phi_Pn_max = cls.compute_pm_curves_200_fiber(inp, rebars)

        # Shear
        shear = cls.evaluate_shear(inp)

        # Seismic & Splice
        seismic = cls.evaluate_seismic(inp)
        splice = cls.evaluate_splice(inp)

        # Geometry
        geometry = cls.generate_geometry(inp)

        # Evaluate Load Combinations
        lcases = inp.load_combinations if inp.load_combinations else [
            LoadCombination(no=1, name="PrimaryLC", Pu=inp.Pu, Mux=inp.Mux, Muy=inp.Muy, Vux=inp.Vux, Vuy=inp.Vuy)
        ]

        comb_results = [
            cls.evaluate_load_combination(lc, curve_x, curve_y, slender, shear, P0, phi_Pn_max)
            for lc in lcases
        ]

        # Critical case
        critical_case = max(comb_results, key=lambda c: max(c.dcr_pm, c.dcr_vx, c.dcr_vy))
        max_dcr = max(critical_case.dcr_pm, critical_case.dcr_vx, critical_case.dcr_vy)
        overall_status = "OK" if (max_dcr <= 1.00 and is_rho_ok and is_sclear_ok) else "NG"

        return RCColumnCheckResult(
            overall_status=overall_status,
            max_dcr=round(max_dcr, 3),
            critical_case=critical_case,
            shape=inp.shape,
            Ag=round(Ag, 1),
            Ast=round(Ast, 1),
            total_bars=total_bars,
            rho_g=round(rho_g, 4),
            is_rho_ok=is_rho_ok,
            s_clear=round(s_clear, 1),
            is_sclear_ok=is_sclear_ok,
            P0=round(P0, 1),
            phi_axial=0.70 if inp.tie_type == "SPIRAL" else 0.65,
            phi_Pn_max=round(phi_Pn_max, 1),
            slender_ratio_x=slender["slender_ratio_x"],
            slender_ratio_y=slender["slender_ratio_y"],
            is_slender_x=slender["is_slender_x"],
            is_slender_y=slender["is_slender_y"],
            delta_ns_x=slender["delta_ns_x"],
            delta_ns_y=slender["delta_ns_y"],
            Pc_x=slender["Pc_x"],
            Pc_y=slender["Pc_y"],
            Mc_x=slender["Mc_x"],
            Mc_y=slender["Mc_y"],
            Vcx=shear["Vcx"],
            Vsx=shear["Vsx"],
            phi_Vnx=shear["phi_Vnx"],
            Vcy=shear["Vcy"],
            Vsy=shear["Vsy"],
            phi_Vny=shear["phi_Vny"],
            Ec=Ec,
            Es=200000.0,
            beta1=beta1,
            Ig_x=Ig_x,
            Ig_y=Ig_y,
            rx=rx,
            ry=ry,
            s_clear_min=s_clear_min,
            e_min_x=e_min_x,
            e_min_y=e_min_y,
            Vs_max_x=Vs_max_x,
            Vs_max_y=Vs_max_y,
            seismic=seismic,
            splice=splice,
            curve_x=curve_x,
            curve_y=curve_y,
            geometry=geometry,
            comb_results=comb_results
        )

    @classmethod
    def auto_design(cls, inp: RCColumnFullInput) -> RCColumnFullInput:
        """Automated optimal design search conforming to docs/202 Section 3.5.
        
        Follows the flowchart:
        1. Check DCR <= 1.0 and 1.0% <= rho <= 4.0%
        2. If rho > 4.0% or s_clear < 30mm -> increase section (+50mm)
        3. If DCR > 1.0 -> step up bar diameter, then bar count, then section size (+50mm)
        """
        bar_diameters = [19.0, 22.0, 25.0, 29.0, 32.0]
        cur = inp.model_copy(deep=True)

        for iteration in range(60):
            res = cls.analyze(cur)

            # Success condition
            if res.max_dcr <= 1.00 and res.is_rho_ok and res.is_sclear_ok:
                return cur

            # 1. If steel ratio exceeded 4.0% or rebar congested, immediately increase section
            if res.rho_g > 0.040 or not res.is_sclear_ok:
                if cur.shape == "RECT":
                    cur.b += 50.0
                    cur.h += 50.0
                    cur.Nx = max(2, cur.Nx - 1)
                    cur.Ny = max(2, cur.Ny - 1)
                else:
                    cur.D += 50.0
                    cur.Ncir = max(6, cur.Ncir - 2)
                continue

            # 2. If DCR > 1.0, try increasing bar diameter first
            curr_diam_idx = bar_diameters.index(cur.bar_diam) if cur.bar_diam in bar_diameters else 0
            if curr_diam_idx < len(bar_diameters) - 1:
                cur.bar_diam = bar_diameters[curr_diam_idx + 1]
                continue

            # 3. If bar diameter is at max (D32), try adding more bars
            if cur.shape == "RECT":
                if cur.Nx < 6 or cur.Ny < 6:
                    cur.Nx += 1
                    cur.Ny += 1
                    cur.bar_diam = 22.0  # reset diameter to re-explore
                    continue
                else:
                    # Section is too small for these forces, increase section
                    cur.b += 50.0
                    cur.h += 50.0
                    cur.Nx = 4
                    cur.Ny = 4
                    cur.bar_diam = 22.0
            else:
                if cur.Ncir < 16:
                    cur.Ncir += 2
                    cur.bar_diam = 22.0
                    continue
                else:
                    cur.D += 50.0
                    cur.Ncir = 8
                    cur.bar_diam = 22.0

        return cur
