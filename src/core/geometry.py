"""Parametric CAD 2D Geometry Primitives and P-M Curve Specifications for AltDP-Core.

Conforms to Requirement 23 & 29 specifications.
Eliminates manual pixel-drawing on frontend canvases by packaging pure structural
world coordinates (in mm) and 200-fiber P-M interaction envelopes.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class Point2D:
    """2D Point in millimeter world coordinates."""
    x: float
    y: float

    def to_list(self) -> List[float]:
        return [round(float(self.x), 2), round(float(self.y), 2)]

    def to_dict(self) -> Dict[str, float]:
        return {"x": round(float(self.x), 2), "y": round(float(self.y), 2)}


@dataclass
class PolygonGeometry:
    """2D closed polygon outline (e.g. concrete section boundary or opening)."""
    points: List[Point2D]
    color: str = "#334155"
    fill: Optional[str] = "#f1f5f9"
    name: str = "section_boundary"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "points": [p.to_list() for p in self.points],
            "color": self.color,
            "fill": self.fill
        }


@dataclass
class RebarPoint:
    """Longitudinal reinforcing bar position and diameter."""
    x: float
    y: float
    dia: float
    layer: int = 1
    tag: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": round(float(self.x), 2),
            "y": round(float(self.y), 2),
            "dia": round(float(self.dia), 1),
            "layer": self.layer,
            "tag": self.tag
        }


@dataclass
class StirrupLoop:
    """Transverse tie / stirrup hoop with 135-degree seismic hook detailing."""
    path: List[Point2D]
    dia: float
    is_closed: bool = True
    hook_angle: float = 135.0
    legs_x: int = 2
    legs_y: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": [p.to_list() for p in self.path],
            "dia": round(float(self.dia), 1),
            "is_closed": self.is_closed,
            "hook_angle": self.hook_angle,
            "legs_x": self.legs_x,
            "legs_y": self.legs_y
        }


@dataclass
class DimensionLine:
    """Parametric dimension annotation with arrows and text."""
    p1: Point2D
    p2: Point2D
    text: str
    dim_type: str = "linear"  # "horizontal", "vertical", "linear"
    offset: float = 35.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "p1": self.p1.to_list(),
            "p2": self.p2.to_list(),
            "text": self.text,
            "dim_type": self.dim_type,
            "offset": self.offset
        }


@dataclass
class PMCurveData:
    """200-Fiber P-M Interaction Diagram Envelope and Factored Demand."""
    theta_deg: float
    nominal_curve: List[Dict[str, float]]   # list of {"Pn": float, "Mn": float}
    design_curve: List[Dict[str, float]]    # list of {"phi_Pn": float, "phi_Mn": float, "phi": float}
    demand_point: Dict[str, float]          # {"Pu": float, "Mu": float, "dcr": float}
    capacity_point: Optional[Dict[str, float]] = None  # {"phi_Pn": float, "phi_Mn": float}
    Po: float = 0.0
    Pt: float = 0.0
    Pn_max: float = 0.0
    phi_Pn_max: float = 0.0
    phi_Pt: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theta_deg": self.theta_deg,
            "nominal_curve": self.nominal_curve,
            "design_curve": self.design_curve,
            "demand_point": self.demand_point,
            "capacity_point": self.capacity_point,
            "Po": round(float(self.Po), 2),
            "Pt": round(float(self.Pt), 2),
            "Pn_max": round(float(self.Pn_max), 2),
            "phi_Pn_max": round(float(self.phi_Pn_max), 2),
            "phi_Pt": round(float(self.phi_Pt), 2)
        }


@dataclass
class SectionGeometry:
    """Complete 2D parametric geometry package for canvas viewports."""
    boundary: List[Point2D]
    rebars: List[RebarPoint] = field(default_factory=list)
    stirrups: List[StirrupLoop] = field(default_factory=list)
    dimensions: List[DimensionLine] = field(default_factory=list)
    pm_curve_x: Optional[PMCurveData] = None
    pm_curve_y: Optional[PMCurveData] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "boundary": [p.to_list() for p in self.boundary],
            "rebars": [r.to_dict() for r in self.rebars],
            "stirrups": [s.to_dict() for s in self.stirrups],
            "dimensions": [d.to_dict() for d in self.dimensions],
            "pm_curve_x": self.pm_curve_x.to_dict() if self.pm_curve_x else None,
            "pm_curve_y": self.pm_curve_y.to_dict() if self.pm_curve_y else None
        }
