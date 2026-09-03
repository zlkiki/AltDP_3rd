"""CAD Schedule Table Generator for Reinforcement and Member Schedules (Phase 17-1).

Draws grid tables and text headers/rows into DXF model space for Beam/Column Schedules.
"""

from typing import List, Dict, Any, Tuple
import ezdxf
from ezdxf.document import Drawing


class CADScheduleTable:
    """Draws structural schedule tables into DXF drawings."""

    @classmethod
    def draw_schedule_table(
        cls,
        doc: Drawing,
        headers: List[str],
        rows: List[List[str]],
        origin: Tuple[float, float] = (0.0, 0.0),
        col_widths: List[float] = None,
        row_height: float = 40.0,
        text_height: float = 18.0
    ):
        """Draw an AutoCAD-compliant schedule table with headers and data rows."""
        msp = doc.modelspace()
        ox, oy = origin
        num_cols = len(headers)
        if col_widths is None:
            col_widths = [120.0] * num_cols

        total_width = sum(col_widths)
        num_rows = len(rows) + 1  # header + data
        total_height = num_rows * row_height

        # 1. Outer Border
        msp.add_lwpolyline([
            (ox, oy),
            (ox + total_width, oy),
            (ox + total_width, oy - total_height),
            (ox, oy - total_height),
            (ox, oy)
        ], dxfattribs={"layer": "S-BORDER"})

        # 2. Horizontal Grid Lines
        for r in range(1, num_rows):
            y = oy - r * row_height
            layer = "S-BORDER" if r == 1 else "S-DIM"
            msp.add_line((ox, y), (ox + total_width, y), dxfattribs={"layer": layer})

        # 3. Vertical Grid Lines
        cur_x = ox
        for c, w in enumerate(col_widths):
            if c > 0:
                msp.add_line((cur_x, oy), (cur_x, oy - total_height), dxfattribs={"layer": "S-DIM"})
            cur_x += w

        # 4. Draw Header Texts
        cur_x = ox
        header_y = oy - row_height * 0.7
        for c, (hdr, w) in enumerate(zip(headers, col_widths)):
            tx = cur_x + w * 0.1
            msp.add_text(hdr, dxfattribs={"layer": "S-TEXT", "height": text_height}).set_placement((tx, header_y))
            cur_x += w

        # 5. Draw Row Texts
        for r_idx, row in enumerate(rows):
            row_y = oy - (r_idx + 2) * row_height + row_height * 0.3
            cur_x = ox
            for c_idx, val in enumerate(row):
                w = col_widths[c_idx] if c_idx < len(col_widths) else 120.0
                tx = cur_x + w * 0.1
                msp.add_text(str(val), dxfattribs={"layer": "S-TEXT", "height": text_height * 0.85}).set_placement((tx, row_y))
                cur_x += w

    @classmethod
    def draw_sample_beam_schedule(cls, doc: Drawing, origin: Tuple[float, float] = (0.0, 0.0)):
        """Utility helper to generate standard Beam Schedule table."""
        headers = ["Story", "Member", "Section (bxh)", "Top Rebar", "Bot Rebar", "Stirrups"]
        rows = [
            ["2F", "2G1", "400x600", "4-D22", "4-D22", "D10 @ 150"],
            ["2F", "2B1", "300x500", "3-D19", "3-D19", "D10 @ 200"],
            ["1F", "1G1", "500x700", "5-D25", "5-D25", "D10 @ 150"],
            ["1F", "1B1", "350x550", "4-D19", "4-D19", "D10 @ 200"],
        ]
        col_widths = [80.0, 90.0, 140.0, 120.0, 120.0, 130.0]
        cls.draw_schedule_table(doc, headers, rows, origin, col_widths)
