"""MIDAS Gen MGT Text Script Parser and 3D Frame Model Builder.

High-performance parser for .mgt files extracting nodes, elements,
materials, sections, and stories with automated member classification.
"""

import math
from typing import Dict, List, Optional, Tuple
from src.engine.interop.model_schema import (
    MidasNode,
    MidasElement,
    MidasMaterial,
    MidasSection,
    MidasStory,
    MidasModel3D,
)


class MGTParser:
    """Parser for MIDAS Gen .mgt text script."""

    def __init__(self):
        self.raw_blocks: Dict[str, List[str]] = {}

    def parse_string(self, text: str) -> MidasModel3D:
        """Parse entire MGT script string into MidasModel3D."""
        self._split_command_blocks(text)

        nodes = self._parse_nodes()
        materials = self._parse_materials()
        sections = self._parse_sections()
        stories = self._parse_stories()
        elements = self._parse_elements(nodes, stories)

        return MidasModel3D(
            nodes=nodes,
            elements=elements,
            materials=materials,
            sections=sections,
            stories=stories,
        )

    def parse_file(self, file_path: str) -> MidasModel3D:
        """Parse MGT script from file."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return self.parse_string(content)

    def _split_command_blocks(self, text: str) -> None:
        """Group lines by command header like *NODE, *ELEMENT."""
        self.raw_blocks = {}
        current_cmd: Optional[str] = None

        for line in text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith(";"):
                continue

            if line_str.startswith("*"):
                # Header command e.g. *NODE or *ELEMENT
                # Might have arguments on same line or comma
                parts = line_str.split(",")
                current_cmd = parts[0].strip().upper()
                if current_cmd not in self.raw_blocks:
                    self.raw_blocks[current_cmd] = []
                # If command line has sub-options or trailing data
                if len(parts) > 1:
                    extra_data = ",".join(parts[1:]).strip()
                    if extra_data:
                        self.raw_blocks[current_cmd].append(extra_data)
            else:
                if current_cmd is not None:
                    self.raw_blocks[current_cmd].append(line_str)

    def _clean_tokens(self, line: str) -> List[str]:
        """Tokenize a line by comma or whitespace."""
        # Split by comma first
        if "," in line:
            return [t.strip() for t in line.split(",") if t.strip()]
        return line.split()

    def _parse_nodes(self) -> Dict[int, MidasNode]:
        """Parse *NODE command block."""
        nodes: Dict[int, MidasNode] = {}
        lines = self.raw_blocks.get("*NODE", [])

        for line in lines:
            tokens = self._clean_tokens(line)
            if len(tokens) >= 4:
                try:
                    nid = int(tokens[0])
                    x = float(tokens[1])
                    y = float(tokens[2])
                    z = float(tokens[3])
                    nodes[nid] = MidasNode(node_id=nid, x=x, y=y, z=z)
                except (ValueError, IndexError):
                    continue
        return nodes

    def _parse_materials(self) -> Dict[int, MidasMaterial]:
        """Parse *MATERIAL command block."""
        materials: Dict[int, MidasMaterial] = {}
        lines = self.raw_blocks.get("*MATERIAL", [])

        i = 0
        while i < len(lines):
            line = lines[i]
            tokens = self._clean_tokens(line)
            if not tokens:
                i += 1
                continue

            try:
                mid = int(tokens[0])
                mtype = tokens[1].upper() if len(tokens) > 1 else "CONC"
                name = tokens[2] if len(tokens) > 2 else f"MAT_{mid}"

                mat = MidasMaterial(mat_id=mid, mat_type=mtype, name=name)

                # Next line often contains elastic modulus, poisson ratio, etc.
                if i + 1 < len(lines) and not lines[i + 1].startswith("*"):
                    sub_tokens = self._clean_tokens(lines[i + 1])
                    if len(sub_tokens) >= 2:
                        try:
                            mat.elastic_modulus = float(sub_tokens[0])
                            mat.poisson = float(sub_tokens[1])
                            if len(sub_tokens) >= 3:
                                mat.thermal_coeff = float(sub_tokens[2])
                            if len(sub_tokens) >= 4:
                                mat.unit_weight = float(sub_tokens[3])
                            i += 1
                        except ValueError:
                            pass

                # Set strength defaults based on type
                if "CONC" in mtype:
                    mat.mat_type = "CONC"
                    mat.fck = 24.0
                elif "STEEL" in mtype:
                    mat.mat_type = "STEEL"
                    mat.fy = 400.0
                    mat.fu = 500.0
                else:
                    mat.mat_type = "REBAR"

                materials[mid] = mat
            except (ValueError, IndexError):
                pass
            i += 1

        return materials

    def _parse_sections(self) -> Dict[int, MidasSection]:
        """Parse *SECTION command block."""
        sections: Dict[int, MidasSection] = {}
        lines = self.raw_blocks.get("*SECTION", [])

        i = 0
        while i < len(lines):
            line = lines[i]
            tokens = self._clean_tokens(line)
            if not tokens:
                i += 1
                continue

            try:
                sec_id = int(tokens[0])
                sec_type = tokens[1].upper() if len(tokens) > 1 else "RECT"
                # If DBUSER, tokens[2] might be shape type like H-SECTION, PIPE, etc.
                sec_name = tokens[2] if len(tokens) > 2 else f"SEC_{sec_id}"
                if len(tokens) > 3 and sec_type == "DBUSER":
                    shape_hint = tokens[2].upper()
                    sec_name = tokens[3]
                else:
                    shape_hint = sec_type

                sec = MidasSection(sec_id=sec_id, sec_type=shape_hint, sec_name=sec_name)

                # Check if dimensions follow on next lines
                if i + 1 < len(lines) and not lines[i + 1].startswith("*"):
                    sub_tokens = self._clean_tokens(lines[i + 1])
                    self._populate_sec_dims(sec, sub_tokens)
                    i += 1

                sections[sec_id] = sec
            except (ValueError, IndexError):
                pass
            i += 1

        return sections

    def _populate_sec_dims(self, sec: MidasSection, tokens: List[str]) -> None:
        """Extract dimension attributes (h, b, tw, tf) from tokens."""
        dims: List[float] = []
        for t in tokens:
            try:
                dims.append(float(t))
            except ValueError:
                continue

        shape = f"{sec.sec_type} {sec.sec_name}".upper()
        if "H-SECTION" in shape or "I-SECTION" in shape or "H " in shape:
            if len(dims) >= 4:
                sec.h = dims[0]
                sec.b = dims[1]
                sec.tw = dims[2]
                sec.tf = dims[3]
                if len(dims) >= 5:
                    sec.r = dims[4]
        elif "BOX" in shape:
            if len(dims) >= 4:
                sec.h = dims[0]
                sec.b = dims[1]
                sec.tw = dims[2]
                sec.tf = dims[3]
        elif "RECT" in shape:
            if len(dims) >= 2:
                sec.h = dims[0]
                sec.b = dims[1]
            elif len(dims) == 1:
                sec.h = dims[0]
                sec.b = dims[0]
        elif "PIPE" in shape or "ROUND" in shape:
            if len(dims) >= 2:
                sec.h = dims[0]  # Outer diameter
                sec.tw = dims[1]  # Thickness
                sec.b = dims[0]
        elif len(dims) >= 2:
            sec.h = dims[0]
            sec.b = dims[1]

    def _parse_stories(self) -> List[MidasStory]:
        """Parse *STORY command block."""
        stories: List[MidasStory] = []
        lines = self.raw_blocks.get("*STORY", [])

        for line in lines:
            tokens = self._clean_tokens(line)
            if len(tokens) >= 3:
                try:
                    name = tokens[0]
                    height = float(tokens[1])
                    elev = float(tokens[2])
                    stories.append(MidasStory(name=name, height=height, elevation=elev))
                except (ValueError, IndexError):
                    continue
        # Sort stories by elevation ascending
        stories.sort(key=lambda s: s.elevation)
        return stories

    def _parse_elements(
        self, nodes: Dict[int, MidasNode], stories: List[MidasStory]
    ) -> Dict[int, MidasElement]:
        """Parse *ELEMENT command block and categorize elements."""
        elements: Dict[int, MidasElement] = {}
        lines = self.raw_blocks.get("*ELEMENT", [])

        for line in lines:
            tokens = self._clean_tokens(line)
            if len(tokens) >= 6:
                try:
                    eid = int(tokens[0])
                    declared_type = tokens[1].upper()
                    mat_id = int(tokens[2])
                    sec_id = int(tokens[3])
                    n_ids = [int(t) for t in tokens[4:] if t.isdigit()]

                    if len(n_ids) < 2:
                        continue

                    # Geometric vector calculation
                    node1 = nodes.get(n_ids[0])
                    node2 = nodes.get(n_ids[1])

                    length = 0.0
                    cosines = (0.0, 0.0, 0.0)
                    elem_type = declared_type

                    if node1 and node2:
                        dx = node2.x - node1.x
                        dy = node2.y - node1.y
                        dz = node2.z - node1.z
                        length = math.sqrt(dx * dx + dy * dy + dz * dz)

                        if length > 1e-6:
                            cx = dx / length
                            cy = dy / length
                            cz = dz / length
                            cosines = (cx, cy, cz)

                            # Direction cosine based classification for 1D line elements
                            elem_type = self._classify_element(declared_type, cz, len(n_ids))

                        # Determine story
                        mid_z = (node1.z + node2.z) / 2.0
                        story_name = self._find_story_for_elevation(mid_z, stories)
                    else:
                        story_name = None

                    elements[eid] = MidasElement(
                        elem_id=eid,
                        elem_type=elem_type,
                        mat_id=mat_id,
                        sec_id=sec_id,
                        nodes=n_ids,
                        story=story_name,
                        length=length,
                        direction_cosines=cosines,
                    )
                except (ValueError, IndexError):
                    continue

        return elements

    def _classify_element(self, declared_type: str, abs_cos_z: float, num_nodes: int) -> str:
        """Classify member into BEAM, COLUMN, BRACE, or WALL."""
        abs_cz = abs(abs_cos_z)

        if "WALL" in declared_type or num_nodes >= 4:
            return "WALL"

        if declared_type in ("TRUSS", "BRACE"):
            return "BRACE"

        # Geometric threshold rule
        if abs_cz >= 0.85:
            return "COLUMN"
        elif abs_cz < 0.15:
            return "BEAM"
        else:
            return "BRACE"

    def _find_story_for_elevation(self, z: float, stories: List[MidasStory]) -> Optional[str]:
        """Find the corresponding story name for a given elevation Z."""
        if not stories:
            return None

        # If z is above the highest story, assign to top story
        if z >= stories[-1].elevation:
            return stories[-1].name

        # Find the story where elevation is just >= z
        for s in stories:
            if z <= s.elevation:
                return s.name

        return stories[0].name
