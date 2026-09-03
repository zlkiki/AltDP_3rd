"""ezdxf-based 2D Reinforcement Detail CAD (DXF) Generator (Phase 17-1).

Generates AutoCAD-compatible DXF drawings with standard structural layers:
S-CONC, S-REBAR-MAIN, S-REBAR-SUB, S-DIM, S-TEXT, S-BORDER.
"""

from typing import List, Dict, Any, Optional, Tuple
import ezdxf
from ezdxf.document import Drawing
from pydantic import BaseModel, Field


class RebarDetail(BaseModel):
    """Reinforcement bar specification for CAD drawing."""
    bar_size: str = "D22"      # "D19", "D22", "D25"
    count: int = 4
    layer: int = 1             # 1 = outer, 2 = inner
    diameter_mm: float = 22.2


class BeamSectionCADInput(BaseModel):
    """Input parameters for drawing RC beam cross section."""
    name: str = "B1 (Mid)"
    b: float = 400.0           # mm
    h: float = 600.0           # mm
    cover: float = 50.0        # mm
    top_rebars: List[RebarDetail] = Field(default_factory=lambda: [RebarDetail(bar_size="D19", count=2, diameter_mm=19.1)])
    bot_rebars: List[RebarDetail] = Field(default_factory=lambda: [RebarDetail(bar_size="D22", count=4, diameter_mm=22.2)])
    stirrup_dia: float = 9.53  # D10
    stirrup_spacing: float = 200.0


class ColumnSectionCADInput(BaseModel):
    """Input parameters for drawing RC column cross section."""
    name: str = "C1"
    b: float = 600.0           # mm
    h: float = 600.0           # mm
    cover: float = 50.0        # mm
    total_bars: int = 12
    bar_dia: float = 25.4      # D25
    tie_dia: float = 9.53      # D10
    tie_spacing: float = 300.0


class CADExporter:
    """Core CAD Exporting Engine creating standard DXF files."""

    LAYER_CONFIG = {
        "S-CONC": {"color": 4, "lineweight": 35},       # Cyan
        "S-REBAR-MAIN": {"color": 1, "lineweight": 50},  # Red
        "S-REBAR-SUB": {"color": 3, "lineweight": 25},   # Green
        "S-DIM": {"color": 2, "lineweight": 18},         # Yellow
        "S-TEXT": {"color": 7, "lineweight": 25},        # White
        "S-BORDER": {"color": 7, "lineweight": 50},      # White/Thick
    }

    @classmethod
    def create_document(cls) -> Drawing:
        """Create a new DXF document and initialize standard structural layers."""
        doc = ezdxf.new("R2010", setup=True)
        msp = doc.modelspace()
        
        for name, cfg in cls.LAYER_CONFIG.items():
            if name not in doc.layers:
                doc.layers.add(name, color=cfg["color"], lineweight=cfg["lineweight"])
        return doc

    @classmethod
    def draw_rc_beam_section(
        cls,
        doc: Drawing,
        inp: BeamSectionCADInput,
        origin: Tuple[float, float] = (0.0, 0.0),
        scale: float = 1.0
    ):
        """Draw an RC beam rectangular cross section with stirrups and rebars."""
        msp = doc.modelspace()
        ox, oy = origin
        b, h = inp.b, inp.h
        c = inp.cover

        # 1. Concrete Outline (S-CONC)
        corners = [(ox, oy), (ox + b, oy), (ox + b, oy + h), (ox, oy + h), (ox, oy)]
        msp.add_lwpolyline(corners, dxfattribs={"layer": "S-CONC"})

        # 2. Stirrup Loop (S-REBAR-SUB)
        st_x1, st_y1 = ox + c * 0.6, oy + c * 0.6
        st_x2, st_y2 = ox + b - c * 0.6, oy + h - c * 0.6
        stirrup_pts = [(st_x1, st_y1), (st_x2, st_y1), (st_x2, st_y2), (st_x1, st_y2), (st_x1, st_y1)]
        msp.add_lwpolyline(stirrup_pts, dxfattribs={"layer": "S-REBAR-SUB"})

        # 3. Bottom Tension Rebars (S-REBAR-MAIN)
        bot_y = oy + c
        for r_group in inp.bot_rebars:
            cnt = r_group.count
            rad = r_group.diameter_mm / 2.0
            if cnt == 1:
                xs = [ox + b / 2.0]
            else:
                span = (b - 2 * c)
                dx = span / (cnt - 1)
                xs = [ox + c + i * dx for i in range(cnt)]
            for bx in xs:
                msp.add_circle((bx, bot_y), radius=rad, dxfattribs={"layer": "S-REBAR-MAIN"})

        # 4. Top Compression Rebars (S-REBAR-MAIN)
        top_y = oy + h - c
        for r_group in inp.top_rebars:
            cnt = r_group.count
            rad = r_group.diameter_mm / 2.0
            if cnt == 1:
                xs = [ox + b / 2.0]
            else:
                span = (b - 2 * c)
                dx = span / (cnt - 1)
                xs = [ox + c + i * dx for i in range(cnt)]
            for tx in xs:
                msp.add_circle((tx, top_y), radius=rad, dxfattribs={"layer": "S-REBAR-MAIN"})

        # 5. Dimensions and Text
        cls._add_section_labels_and_dims(msp, ox, oy, b, h, inp.name)

    @classmethod
    def draw_rc_column_section(
        cls,
        doc: Drawing,
        inp: ColumnSectionCADInput,
        origin: Tuple[float, float] = (0.0, 0.0)
    ):
        """Draw an RC column cross section with ties and perimeter rebars."""
        msp = doc.modelspace()
        ox, oy = origin
        b, h = inp.b, inp.h
        c = inp.cover

        # 1. Concrete Outline
        corners = [(ox, oy), (ox + b, oy), (ox + b, oy + h), (ox, oy + h), (ox, oy)]
        msp.add_lwpolyline(corners, dxfattribs={"layer": "S-CONC"})

        # 2. Tie Loop
        tx1, ty1 = ox + c * 0.6, oy + c * 0.6
        tx2, ty2 = ox + b - c * 0.6, oy + h - c * 0.6
        tie_pts = [(tx1, ty1), (tx2, ty1), (tx2, ty2), (tx1, ty2), (tx1, ty1)]
        msp.add_lwpolyline(tie_pts, dxfattribs={"layer": "S-REBAR-SUB"})

        # 3. Longitudinal Rebars along perimeter
        nb = inp.total_bars
        rad = inp.bar_dia / 2.0
        # Compute coordinates for 4 corners + distributed edges
        corner_rebars = [
            (ox + c, oy + c),
            (ox + b - c, oy + c),
            (ox + b - c, oy + h - c),
            (ox + c, oy + h - c)
        ]
        rebar_coords = list(corner_rebars)
        remaining = nb - 4
        if remaining > 0:
            per_side = remaining // 4
            for s in range(1, per_side + 1):
                # bottom & top
                dx = (b - 2 * c) * (s / (per_side + 1))
                rebar_coords.append((ox + c + dx, oy + c))
                rebar_coords.append((ox + c + dx, oy + h - c))
                # left & right
                dy = (h - 2 * c) * (s / (per_side + 1))
                rebar_coords.append((ox + c, oy + c + dy))
                rebar_coords.append((ox + b - c, oy + c + dy))

        for rx, ry in rebar_coords:
            msp.add_circle((rx, ry), radius=rad, dxfattribs={"layer": "S-REBAR-MAIN"})

        cls._add_section_labels_and_dims(msp, ox, oy, b, h, inp.name)

    @classmethod
    def _add_section_labels_and_dims(
        cls,
        msp: Any,
        ox: float,
        oy: float,
        b: float,
        h: float,
        title: str
    ):
        """Add dimension lines, width/depth values, and title labels."""
        # Width Dimension (bottom)
        dim_y = oy - 60.0
        msp.add_line((ox, dim_y), (ox + b, dim_y), dxfattribs={"layer": "S-DIM"})
        msp.add_line((ox, oy), (ox, dim_y - 15.0), dxfattribs={"layer": "S-DIM"})
        msp.add_line((ox + b, oy), (ox + b, dim_y - 15.0), dxfattribs={"layer": "S-DIM"})
        msp.add_text(f"{int(b)}", dxfattribs={"layer": "S-DIM", "height": 25.0}).set_placement(
            (ox + b / 2.0 - 20.0, dim_y - 35.0)
        )

        # Height Dimension (left)
        dim_x = ox - 60.0
        msp.add_line((dim_x, oy), (dim_x, oy + h), dxfattribs={"layer": "S-DIM"})
        msp.add_line((ox, oy), (dim_x - 15.0, oy), dxfattribs={"layer": "S-DIM"})
        msp.add_line((ox, oy + h), (dim_x - 15.0, oy + h), dxfattribs={"layer": "S-DIM"})
        msp.add_text(f"{int(h)}", dxfattribs={"layer": "S-DIM", "height": 25.0, "rotation": 90.0}).set_placement(
            (dim_x - 15.0, oy + h / 2.0 - 20.0)
        )

        # Title
        msp.add_text(title, dxfattribs={"layer": "S-TEXT", "height": 35.0}).set_placement(
            (ox + b / 2.0 - 50.0, oy - 130.0)
        )
