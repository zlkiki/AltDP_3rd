"""Section Database (.sdb) Parser for AltDP_3rd.

Parses Midas 'MDSW-SDB' binary databases (KS, AISC, JIS, DIN, etc.)
and provides structured section properties for structural member design.
"""

from dataclasses import dataclass, field
import os
import struct
from typing import List, Dict, Optional, Any


@dataclass
class SectionRecord:
    """Steel Section Record Model."""
    name: str
    category: str = "H-Section"
    H: float = 0.0          # Height (mm)
    B: float = 0.0          # Width (mm)
    tw: float = 0.0         # Web thickness (mm)
    tf: float = 0.0         # Flange thickness (mm)
    r: float = 0.0          # Root radius (mm)
    A: float = 0.0          # Cross-sectional area (cm2 or mm2)
    Ix: float = 0.0         # Moment of inertia X (cm4)
    Iy: float = 0.0         # Moment of inertia Y (cm4)
    rx: float = 0.0         # Radius of gyration X (cm)
    ry: float = 0.0         # Radius of gyration Y (cm)
    Zx: float = 0.0         # Plastic section modulus X (cm3)
    Zy: float = 0.0         # Plastic section modulus Y (cm3)
    Sx: float = 0.0         # Elastic section modulus X (cm3)
    Sy: float = 0.0         # Elastic section modulus Y (cm3)
    J: float = 0.0          # Torsional constant (cm4)
    Cw: float = 0.0         # Warping constant (cm6)
    weight: float = 0.0     # Unit weight (kg/m)


class SDBParser:
    """Parser for Midas Section Database (*.sdb) files."""

    def __init__(self, sdb_path: str):
        self.sdb_path = sdb_path
        self.sections: List[SectionRecord] = []
        self._parsed = False

    def parse(self) -> List[SectionRecord]:
        """Parse the .sdb file and return list of section records."""
        if not os.path.exists(self.sdb_path):
            raise FileNotFoundError(f"SDB file not found: {self.sdb_path}")

        with open(self.sdb_path, "rb") as f:
            data = f.read()

        if len(data) < 16 or data[:8] != b"MDSW-SDB":
            raise ValueError(f"Invalid MDSW-SDB magic header in {self.sdb_path}")

        # Scan for ASCII section names in 28-byte chunk blocks
        self.sections = []
        offset = 24
        file_len = len(data)

        # Basic parser extracting naming and standard section parameters
        while offset + 28 <= file_len:
            name_bytes = data[offset : offset + 20]
            # Check if name contains valid ASCII characters
            try:
                name_str = name_bytes.decode("latin1").strip()
                if name_str and all(c.isprintable() for c in name_str) and len(name_str) >= 3:
                    sec = self._parse_dimensions_from_name(name_str)
                    if sec:
                        self.sections.append(sec)
                    offset += 28
                else:
                    offset += 4
            except Exception:
                offset += 4

        self._parsed = True
        return self.sections

    def _parse_dimensions_from_name(self, name: str) -> Optional[SectionRecord]:
        """Extract geometric parameters from standard section name string."""
        rec = SectionRecord(name=name)
        clean = name.replace(" ", "")

        # Try parsing standard H-beam: e.g. H400x200x8x13 or HN400x200
        if "x" in clean:
            parts = clean.split("x")
            try:
                # Leading prefix removal
                h_str = "".join(c for c in parts[0] if c.isdigit() or c == ".")
                if h_str:
                    rec.H = float(h_str)
                if len(parts) >= 2:
                    b_str = "".join(c for c in parts[1] if c.isdigit() or c == ".")
                    if b_str:
                        rec.B = float(b_str)
                if len(parts) >= 3:
                    rec.tw = float(parts[2])
                if len(parts) >= 4:
                    rec.tf = float(parts[3])

                # Calculate approximate cross section area and inertia if not parsed directly
                if rec.H > 0 and rec.B > 0 and rec.tw > 0 and rec.tf > 0:
                    rec.A = (2.0 * rec.B * rec.tf + (rec.H - 2.0 * rec.tf) * rec.tw) / 100.0  # cm2
                    # Approximate Ix
                    rec.Ix = (rec.B * (rec.H**3) - (rec.B - rec.tw) * ((rec.H - 2.0 * rec.tf)**3)) / 12.0 / 10000.0 # cm4
                    rec.Iy = (2.0 * rec.tf * (rec.B**3) + (rec.H - 2.0 * rec.tf) * (rec.tw**3)) / 12.0 / 10000.0 # cm4
                    rec.weight = rec.A * 0.785 # kg/m
                return rec
            except (ValueError, IndexError):
                return None
        return None

    def search(self, query: str) -> List[SectionRecord]:
        """Search sections matching query."""
        if not self._parsed:
            self.parse()
        q = query.lower()
        return [s for s in self.sections if q in s.name.lower()]
