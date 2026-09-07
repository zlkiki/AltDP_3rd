"""Data models and schemas for 3D Structural Frame Model Interoperability.

Complies with KDS standards and provides seamless bidirectional mapping
for nodes, elements, materials, sections, and stories.
"""

from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field


class FrameNode(BaseModel):
    """3D nodal coordinate definition."""
    node_id: int
    x: float
    y: float
    z: float


class FrameElement(BaseModel):
    """Finite element record with geometry and member categorization."""
    elem_id: int
    elem_type: str  # "BEAM", "COLUMN", "WALL", "BRACE", "TRUSS", "PLATE"
    mat_id: int
    sec_id: int
    nodes: List[int]
    story: Optional[str] = None
    length: float = 0.0
    direction_cosines: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class FrameMaterial(BaseModel):
    """Material definition (Concrete, Rebar, Structural Steel)."""
    mat_id: int
    mat_type: str  # "CONC", "STEEL", "REBAR"
    name: str = ""
    elastic_modulus: float = 200000.0  # MPa
    poisson: float = 0.2
    thermal_coeff: float = 1.0e-5
    unit_weight: float = 24.5  # kN/m3
    # Specific strengths
    fck: float = 24.0  # MPa for concrete
    fy: float = 400.0  # MPa for steel / rebar
    fu: float = 500.0  # MPa for steel


class FrameSection(BaseModel):
    """Section geometry and dimension properties."""
    sec_id: int
    sec_type: str = "RECT"  # "RECT", "H-SECTION", "BOX", "PIPE", "DBUSER", "WALL"
    sec_name: str = ""
    # Geometric dimensions (mm)
    h: float = 0.0   # Height / Depth
    b: float = 0.0   # Width
    tw: float = 0.0  # Web thickness
    tf: float = 0.0  # Flange thickness
    r: float = 0.0   # Fillet radius
    thickness: float = 0.0  # Plate / Wall thickness
    area: float = 0.0
    ix: float = 0.0
    iy: float = 0.0


class FrameStory(BaseModel):
    """Story / Floor level metadata."""
    name: str
    height: float
    elevation: float


class FrameModel3D(BaseModel):
    """Complete 3D Structural Frame Model."""
    nodes: Dict[int, FrameNode] = Field(default_factory=dict)
    elements: Dict[int, FrameElement] = Field(default_factory=dict)
    materials: Dict[int, FrameMaterial] = Field(default_factory=dict)
    sections: Dict[int, FrameSection] = Field(default_factory=dict)
    stories: List[FrameStory] = Field(default_factory=list)

    def get_elements_by_type(self, elem_type: str) -> List[FrameElement]:
        """Filter elements by type (e.g. BEAM, COLUMN, WALL, BRACE)."""
        return [el for el in self.elements.values() if el.elem_type == elem_type]

    def get_elements_by_story(self, story_name: str) -> List[FrameElement]:
        """Filter elements located at a specific story."""
        return [el for el in self.elements.values() if el.story == story_name]


class MemberForce(BaseModel):
    """6-DOF internal forces at specific section location for a load combination."""
    elem_id: int = 0
    lcb_name: str = ""
    position: str = "I"  # "I", "M", "J"
    p: float = 0.0       # Axial force (kN, (+) Tension, (-) Compression in KDS standard)
    vy: float = 0.0      # Shear force y (kN)
    vz: float = 0.0      # Shear force z (kN)
    my: float = 0.0      # Bending moment y (kN*m)
    mz: float = 0.0      # Bending moment z (kN*m)
    t: float = 0.0       # Torsion (kN*m)


class GoverningForceSummary(BaseModel):
    """Summarized critical forces and governing load combinations for member design."""
    member_id: int
    member_type: str
    total_lcb_count: int = 0
    governing_lcb_list: List[str] = Field(default_factory=list)
    critical_forces: List[MemberForce] = Field(default_factory=list)
    max_dcr_estimated: float = 0.0

