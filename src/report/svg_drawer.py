"""Pure Python SVG Vector Graphics Engine for Structural Member Reports.

Generates 2D cross-section rebar layouts, steel cross sections,
and 2D P-M interaction diagram curves without external graphics libraries.
"""

from typing import List, Tuple, Optional


def draw_rc_beam_section_svg(
    b: float,
    h: float,
    top_rebars: int = 3,
    bot_rebars: int = 4,
    rebar_dia: float = 22.0,
    stirrup_dia: float = 10.0,
    cover: float = 40.0,
    width_px: int = 240,
    height_px: int = 220,
) -> str:
    """Generate SVG for rectangular RC beam section with rebars and stirrup."""
    pad_x = 40
    pad_y = 30
    draw_w = width_px - 2 * pad_x
    draw_h = height_px - 2 * pad_y

    scale = min(draw_w / max(b, 1.0), draw_h / max(h, 1.0))
    sx = b * scale
    sy = h * scale

    x0 = pad_x + (draw_w - sx) / 2
    y0 = pad_y + (draw_h - sy) / 2

    # Concrete Rect
    svg = [
        f'<svg viewBox="0 0 {width_px} {height_px}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="{x0:.1f}" y="{y0:.1f}" width="{sx:.1f}" height="{sy:.1f}" fill="#e2e8f0" stroke="#1e293b" stroke-width="2" />',
    ]

    # Stirrup
    st_off = cover * scale
    st_x = x0 + st_off
    st_y = y0 + st_off
    st_w = sx - 2 * st_off
    st_h = sy - 2 * st_off
    if st_w > 0 and st_h > 0:
        svg.append(
            f'  <rect x="{st_x:.1f}" y="{st_y:.1f}" width="{st_w:.1f}" height="{st_h:.1f}" '
            f'fill="none" stroke="#2563eb" stroke-width="1.8" rx="4" ry="4" />'
        )

    # Top Rebars
    r_px = max(2.5, (rebar_dia / 2) * scale)
    if top_rebars > 1 and st_w > 0:
        dx_top = (st_w - 2 * r_px) / (top_rebars - 1)
        for i in range(top_rebars):
            rx = st_x + r_px + i * dx_top
            ry = st_y + r_px + 2
            svg.append(f'  <circle cx="{rx:.1f}" cy="{ry:.1f}" r="{r_px:.1f}" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" />')
    elif top_rebars == 1:
        rx = st_x + st_w / 2
        ry = st_y + r_px + 2
        svg.append(f'  <circle cx="{rx:.1f}" cy="{ry:.1f}" r="{r_px:.1f}" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" />')

    # Bottom Rebars
    if bot_rebars > 1 and st_w > 0:
        dx_bot = (st_w - 2 * r_px) / (bot_rebars - 1)
        for i in range(bot_rebars):
            rx = st_x + r_px + i * dx_bot
            ry = st_y + st_h - r_px - 2
            svg.append(f'  <circle cx="{rx:.1f}" cy="{ry:.1f}" r="{r_px:.1f}" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" />')
    elif bot_rebars == 1:
        rx = st_x + st_w / 2
        ry = st_y + st_h - r_px - 2
        svg.append(f'  <circle cx="{rx:.1f}" cy="{ry:.1f}" r="{r_px:.1f}" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" />')

    # Dimension text
    svg.append(f'  <text x="{x0 + sx/2:.1f}" y="{y0 - 8:.1f}" font-size="10" fill="#334155" text-anchor="middle" font-family="sans-serif">b={b:.0f}</text>')
    svg.append(f'  <text x="{x0 + sx + 8:.1f}" y="{y0 + sy/2:.1f}" font-size="10" fill="#334155" text-anchor="start" dominant-baseline="middle" font-family="sans-serif">h={h:.0f}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


def draw_rc_column_section_svg(
    b: float,
    h: float,
    nx: int = 4,
    ny: int = 4,
    rebar_dia: float = 25.0,
    cover: float = 40.0,
    width_px: int = 240,
    height_px: int = 220,
) -> str:
    """Generate SVG for rectangular RC column section with perimeter ties and rebars."""
    pad_x = 40
    pad_y = 30
    draw_w = width_px - 2 * pad_x
    draw_h = height_px - 2 * pad_y

    scale = min(draw_w / max(b, 1.0), draw_h / max(h, 1.0))
    sx = b * scale
    sy = h * scale

    x0 = pad_x + (draw_w - sx) / 2
    y0 = pad_y + (draw_h - sy) / 2

    svg = [
        f'<svg viewBox="0 0 {width_px} {height_px}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="{x0:.1f}" y="{y0:.1f}" width="{sx:.1f}" height="{sy:.1f}" fill="#e2e8f0" stroke="#1e293b" stroke-width="2" />',
    ]

    st_off = cover * scale
    st_x = x0 + st_off
    st_y = y0 + st_off
    st_w = sx - 2 * st_off
    st_h = sy - 2 * st_off
    if st_w > 0 and st_h > 0:
        svg.append(
            f'  <rect x="{st_x:.1f}" y="{st_y:.1f}" width="{st_w:.1f}" height="{st_h:.1f}" '
            f'fill="none" stroke="#2563eb" stroke-width="1.8" rx="4" ry="4" />'
        )

    r_px = max(2.5, (rebar_dia / 2) * scale)

    # Perimeter rebars
    points = set()
    # Top & Bottom rows
    for i in range(nx):
        x = st_x + r_px + i * ((st_w - 2 * r_px) / max(nx - 1, 1))
        points.add((x, st_y + r_px + 2))
        points.add((x, st_y + st_h - r_px - 2))
    # Left & Right columns
    for j in range(ny):
        y = st_y + r_px + j * ((st_h - 2 * r_px) / max(ny - 1, 1))
        points.add((st_x + r_px + 2, y))
        points.add((st_x + st_w - r_px - 2, y))

    for px, py in points:
        svg.append(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{r_px:.1f}" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" />')

    svg.append(f'  <text x="{x0 + sx/2:.1f}" y="{y0 - 8:.1f}" font-size="10" fill="#334155" text-anchor="middle" font-family="sans-serif">{b:.0f}×{h:.0f}</text>')
    svg.append('</svg>')
    return '\n'.join(svg)


def draw_steel_h_section_svg(
    h: float,
    b: float,
    tw: float,
    tf: float,
    width_px: int = 240,
    height_px: int = 220,
) -> str:
    """Generate SVG for structural steel H-section."""
    pad_x = 40
    pad_y = 30
    draw_w = width_px - 2 * pad_x
    draw_h = height_px - 2 * pad_y

    scale = min(draw_w / max(b, 1.0), draw_h / max(h, 1.0))
    sh = h * scale
    sb = b * scale
    stw = max(2.0, tw * scale)
    stf = max(2.0, tf * scale)

    x0 = pad_x + (draw_w - sb) / 2
    y0 = pad_y + (draw_h - sh) / 2

    # Coordinates for I/H polygon
    xc = x0 + sb / 2
    x_w_l = xc - stw / 2
    x_w_r = xc + stw / 2

    pts = [
        (x0, y0), (x0 + sb, y0), (x0 + sb, y0 + stf),
        (x_w_r, y0 + stf), (x_w_r, y0 + sh - stf),
        (x0 + sb, y0 + sh - stf), (x0 + sb, y0 + sh),
        (x0, y0 + sh), (x0, y0 + sh - stf),
        (x_w_l, y0 + sh - stf), (x_w_l, y0 + stf),
        (x0, y0 + stf)
    ]
    pt_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    svg = [
        f'<svg viewBox="0 0 {width_px} {height_px}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
        f'  <polygon points="{pt_str}" fill="#94a3b8" stroke="#1e293b" stroke-width="1.8" />',
        f'  <text x="{x0 + sb/2:.1f}" y="{y0 - 8:.1f}" font-size="10" fill="#334155" text-anchor="middle" font-family="sans-serif">B={b:.0f}</text>',
        f'  <text x="{x0 + sb + 8:.1f}" y="{y0 + sh/2:.1f}" font-size="10" fill="#334155" text-anchor="start" dominant-baseline="middle" font-family="sans-serif">H={h:.0f}</text>',
        '</svg>'
    ]
    return '\n'.join(svg)


def draw_pm_diagram_svg(
    pm_nominal: List[Tuple[float, float]],
    pm_design: List[Tuple[float, float]],
    action_point: Optional[Tuple[float, float]] = None,
    width_px: int = 320,
    height_px: int = 240,
) -> str:
    """Generate SVG for 2D P-M interaction diagram curve."""
    pad_left = 55
    pad_right = 25
    pad_top = 25
    pad_bottom = 35

    draw_w = width_px - pad_left - pad_right
    draw_h = height_px - pad_top - pad_bottom

    all_p = [p for m, p in pm_nominal + pm_design]
    all_m = [m for m, p in pm_nominal + pm_design]

    if action_point:
        all_m.append(action_point[1])
        all_p.append(action_point[0])

    min_p, max_p = min(min(all_p, default=0.0), 0.0), max(max(all_p, default=100.0), 10.0)
    min_m, max_m = 0.0, max(max(all_m, default=100.0), 10.0)

    range_p = max_p - min_p if (max_p - min_p) > 0 else 1.0
    range_m = max_m - min_m if (max_m - min_m) > 0 else 1.0

    def to_svg(m_val: float, p_val: float) -> Tuple[float, float]:
        x = pad_left + ((m_val - min_m) / range_m) * draw_w
        y = pad_top + ((max_p - p_val) / range_p) * draw_h
        return x, y

    svg = [
        f'<svg viewBox="0 0 {width_px} {height_px}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
        # Background & Grid
        f'  <rect x="{pad_left}" y="{pad_top}" width="{draw_w}" height="{draw_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" />',
    ]

    # Axes
    y_axis_x = pad_left
    x_axis_y = pad_top + ((max_p - 0.0) / range_p) * draw_h
    if pad_top <= x_axis_y <= pad_top + draw_h:
        svg.append(f'  <line x1="{pad_left}" y1="{x_axis_y:.1f}" x2="{pad_left + draw_w}" y2="{x_axis_y:.1f}" stroke="#94a3b8" stroke-dasharray="3,3" />')

    # Nominal Curve (Gray Dashed)
    if pm_nominal:
        nom_pts = " ".join(f"{to_svg(m, p)[0]:.1f},{to_svg(m, p)[1]:.1f}" for m, p in pm_nominal)
        svg.append(f'  <polyline points="{nom_pts}" fill="none" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="4,4" />')

    # Design Curve (Blue Solid)
    if pm_design:
        des_pts = " ".join(f"{to_svg(m, p)[0]:.1f},{to_svg(m, p)[1]:.1f}" for m, p in pm_design)
        svg.append(f'  <polyline points="{des_pts}" fill="rgba(37, 99, 235, 0.08)" stroke="#2563eb" stroke-width="2.2" />')

    # Action Point (Mu, Pu)
    if action_point:
        pu, mu = action_point
        ax, ay = to_svg(mu, pu)
        svg.append(f'  <circle cx="{ax:.1f}" cy="{ay:.1f}" r="4.5" fill="#dc2626" stroke="#ffffff" stroke-width="1.5" />')
        svg.append(f'  <text x="{ax + 6:.1f}" y="{ay - 4:.1f}" font-size="8.5" font-weight="bold" fill="#dc2626" font-family="sans-serif">({mu:.1f}, {pu:.1f})</text>')

    # Axis Labels
    svg.append(f'  <text x="{pad_left + draw_w/2:.1f}" y="{height_px - 8:.1f}" font-size="9" fill="#475569" text-anchor="middle" font-family="sans-serif">Bending Moment M (kN·m)</text>')
    svg.append(f'  <text x="14" y="{pad_top + draw_h/2:.1f}" font-size="9" fill="#475569" text-anchor="middle" font-family="sans-serif" transform="rotate(-90 14 {pad_top + draw_h/2})">Axial Load P (kN)</text>')

    # Legend
    svg.append(f'  <text x="{pad_left + 8:.1f}" y="{pad_top + 16:.1f}" font-size="8" fill="#2563eb" font-family="sans-serif">― φPn-φMn (설계)</text>')
    svg.append(f'  <text x="{pad_left + 8:.1f}" y="{pad_top + 28:.1f}" font-size="8" fill="#94a3b8" font-family="sans-serif">--- Pn-Mn (공칭)</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


def draw_fem_contour_svg(
    nx: int = 5,
    ny: int = 5,
    title: str = "FEM Bending Moment Contour (Mx)",
    width_px: int = 280,
    height_px: int = 220,
) -> str:
    """Generate SVG for 2D FEM plate stress / moment contour map."""
    pad = 30
    draw_w = width_px - 2 * pad
    draw_h = height_px - 2 * pad - 20

    dx = draw_w / nx
    dy = draw_h / ny

    # Color palette for contour (Blue -> Green -> Yellow -> Red)
    colors = ["#3b82f6", "#10b981", "#fbbf24", "#f97316", "#ef4444"]

    svg = [
        f'<svg viewBox="0 0 {width_px} {height_px}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
        f'  <text x="{width_px/2:.1f}" y="18" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">{title}</text>',
    ]

    for i in range(nx):
        for j in range(ny):
            x = pad + i * dx
            y = pad + 15 + j * dy
            # Pseudo-stress distribution (higher at center)
            dist_center = 1.0 - (((i - nx / 2) ** 2 + (j - ny / 2) ** 2) / ((nx / 2) ** 2 + (ny / 2) ** 2))
            c_idx = min(len(colors) - 1, max(0, int(dist_center * len(colors))))
            color = colors[c_idx]

            svg.append(
                f'  <rect x="{x:.1f}" y="{y:.1f}" width="{dx:.1f}" height="{dy:.1f}" '
                f'fill="{color}" fill-opacity="0.85" stroke="#ffffff" stroke-width="0.5" />'
            )

    # Border outline
    svg.append(f'  <rect x="{pad}" y="{pad + 15}" width="{draw_w}" height="{draw_h}" fill="none" stroke="#334155" stroke-width="1.5" />')

    # Color Legend bar at bottom
    leg_y = height_px - 14
    leg_w = draw_w / len(colors)
    for k, c in enumerate(colors):
        lx = pad + k * leg_w
        svg.append(f'  <rect x="{lx:.1f}" y="{leg_y}" width="{leg_w:.1f}" height="6" fill="{c}" />')
    svg.append(f'  <text x="{pad}" y="{leg_y - 3}" font-size="8" fill="#64748b">Min (Safe)</text>')
    svg.append(f'  <text x="{pad + draw_w}" y="{leg_y - 3}" font-size="8" fill="#64748b" text-anchor="end">Max (Critical)</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

