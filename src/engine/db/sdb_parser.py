"""Section Database (.sdb) Parser for AltDP_3rd.

Parses Midas 'MDSW-SDB' binary databases (KS, AISC, JIS, DIN, etc.)
and provides structured section properties for structural member design.
"""

from dataclasses import dataclass, field
import os
import re
import struct
from typing import List, Dict, Optional, Any


@dataclass
class SectionRecord:
    """Steel Section Record Model."""
    name: str
    db_name: str = "KS"
    category: str = "H-Section"
    H: float = 0.0          # Height (mm)
    B: float = 0.0          # Width (mm)
    tw: float = 0.0         # Web thickness (mm)
    tf: float = 0.0         # Flange thickness (mm)
    r: float = 0.0          # Root fillet radius (mm)
    A: float = 0.0          # Cross-sectional area (cm2)
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
    extra_props: Dict[str, float] = field(default_factory=dict)


class SDBParser:
    """Parser for Midas Section Database (*.sdb) files."""

    def __init__(self, sdb_path: str, db_name: Optional[str] = None):
        self.sdb_path = sdb_path
        self.db_name = db_name or os.path.splitext(os.path.basename(sdb_path))[0]
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

        self.sections = []
        file_len = len(data)
        seen_names = set()

        # Regular expression for section names in binary stream
        pattern = rb'[HLCBWPTU-][0-9A-Za-z_.\- /]{2,30}'
        for match in re.finditer(pattern, data):
            try:
                candidate = match.group(0).decode("latin1").strip("\x00 \t\r\n")
                if len(candidate) < 4 or candidate in seen_names:
                    continue
                # Check if this string looks like a standard steel section specification
                if any(delim in candidate for delim in ["x", "X", "*", "-"]) or any(char.isdigit() for char in candidate):
                    sec = self._parse_dimensions_from_name(candidate)
                    if sec:
                        sec.db_name = self.db_name
                        self._calculate_defaults(sec)
                        self.sections.append(sec)
                        seen_names.add(candidate)
            except Exception:
                continue

        # If regex extracted fewer sections, scan with chunk fallback
        if len(self.sections) < 5:
            offset = 16
            while offset + 32 <= file_len:
                chunk = data[offset:offset + 32]
                name_bytes = chunk[:20].split(b'\x00')[0]
                try:
                    name_str = name_bytes.decode('latin1').strip()
                    if len(name_str) >= 4 and name_str not in seen_names:
                        sec = self._parse_dimensions_from_name(name_str)
                        if sec:
                            sec.db_name = self.db_name
                            self._calculate_defaults(sec)
                            self.sections.append(sec)
                            seen_names.add(name_str)
                except Exception:
                    pass
                offset += 4

        self._parsed = True
        return self.sections

    def search(self, keyword: str) -> List[SectionRecord]:
        """Search parsed sections by name keyword."""
        if not self._parsed:
            self.parse()
        kw = keyword.lower().replace(" ", "")
        return [s for s in self.sections if kw in s.name.lower().replace(" ", "")]

    def _parse_dimensions_from_name(self, name: str) -> Optional[SectionRecord]:
        """Extract geometric parameters from standard section name string."""
        rec = SectionRecord(name=name)
        clean = name.replace(" ", "")

        # Categorize
        upper = clean.upper()
        if upper.startswith(("HN", "HM", "HW", "H-", "H", "RH", "SH", "UB", "UC", "W", "HP")):
            rec.category = "H-Section"
        elif upper.startswith(("BOX", "RHS", "SHS", "SR", "SQ")):
            rec.category = "Box"
        elif upper.startswith(("PIPE", "CHS", "P-", "O-")):
            rec.category = "Pipe"
        elif upper.startswith(("C", "CH", "CHANNEL", "[", "MC")):
            rec.category = "Channel"
        elif upper.startswith(("L", "ANGLE")):
            rec.category = "Angle"
        elif upper.startswith(("T", "TEE", "WT")):
            rec.category = "Tee"
        else:
            rec.category = "H-Section"

        # Parsing numeric dimensions e.g., H400x200x8x13, 400x200x8x13, L100x100x10
        # Split by 'x', 'X', or '*'
        parts = re.split(r'[xX*]', clean)
        nums = []
        for part in parts:
            match = re.search(r'([0-9]+\.?[0-9]*)', part)
            if match:
                try:
                    nums.append(float(match.group(1)))
                except ValueError:
                    pass

        if not nums:
            return None

        if rec.category in ["H-Section", "Channel", "Tee"]:
            if len(nums) >= 1:
                rec.H = nums[0]
            if len(nums) >= 2:
                rec.B = nums[1]
            if len(nums) >= 3:
                rec.tw = nums[2]
            if len(nums) >= 4:
                rec.tf = nums[3]
            elif len(nums) == 3:
                rec.tf = nums[2]
        elif rec.category == "Box":
            if len(nums) >= 1:
                rec.H = nums[0]
                rec.B = nums[0]
            if len(nums) >= 2:
                rec.B = nums[1]
            if len(nums) >= 3:
                rec.tw = nums[2]
                rec.tf = nums[2]
        elif rec.category == "Angle":
            if len(nums) >= 1:
                rec.H = nums[0]
                rec.B = nums[0]
            if len(nums) >= 2:
                rec.B = nums[1]
            if len(nums) >= 3:
                rec.tw = nums[2]
                rec.tf = nums[2]
        elif rec.category == "Pipe":
            if len(nums) >= 1:
                rec.H = nums[0]
                rec.B = nums[0]
            if len(nums) >= 2:
                rec.tw = nums[1]
                rec.tf = nums[1]

        return rec

    def _calculate_defaults(self, sec: SectionRecord) -> None:
        """Calculate basic cross-section properties if missing."""
        if sec.category == "H-Section" and sec.H > 0 and sec.B > 0:
            tw = sec.tw if sec.tw > 0 else 6.0
            tf = sec.tf if sec.tf > 0 else 9.0
            sec.tw, sec.tf = tw, tf
            
            # Area in cm2
            area_mm2 = 2 * sec.B * tf + (sec.H - 2 * tf) * tw
            sec.A = round(area_mm2 / 100.0, 2)
            
            # Moment of inertia (cm4)
            ix_mm4 = (sec.B * (sec.H ** 3) - (sec.B - tw) * ((sec.H - 2 * tf) ** 3)) / 12.0
            iy_mm4 = (2 * tf * (sec.B ** 3) + (sec.H - 2 * tf) * (tw ** 3)) / 12.0
            sec.Ix = round(ix_mm4 / 10000.0, 2)
            sec.Iy = round(iy_mm4 / 10000.0, 2)
            
            # Elastic modulus (cm3)
            sec.Sx = round(ix_mm4 / (sec.H / 2.0) / 1000.0, 2)
            sec.Sy = round(iy_mm4 / (sec.B / 2.0) / 1000.0, 2)
            
            # Plastic modulus (cm3)
            zx_mm3 = sec.B * tf * (sec.H - tf) + 0.25 * tw * ((sec.H - 2 * tf) ** 2)
            zy_mm3 = 0.5 * tf * (sec.B ** 2) + 0.25 * (sec.H - 2 * tf) * (tw ** 2)
            sec.Zx = round(zx_mm3 / 1000.0, 2)
            sec.Zy = round(zy_mm3 / 1000.0, 2)
            
            # Radius of gyration (cm)
            if sec.A > 0:
                sec.rx = round((sec.Ix / sec.A) ** 0.5, 2)
                sec.ry = round((sec.Iy / sec.A) ** 0.5, 2)
            
            # Weight (kg/m)
            sec.weight = round(sec.A * 0.785, 2)
