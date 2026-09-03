"""KDS 14 20 52 Standard Quantity Takeoff Engine (Phase 17-2).

Calculates concrete volumes (m3), formwork areas (m2), and rebar weights (ton)
including development (ld) and lap splice lengths per KDS standards.
"""

from typing import List, Dict, Any, Optional
import math
from pydantic import BaseModel, Field


# KDS Rebar Standard Properties: Diameter (mm), Unit Weight (kg/m), Area (mm2)
REBAR_SPECS: Dict[str, Dict[str, float]] = {
    "D10": {"dia": 9.53, "unit_weight": 0.560, "area": 71.3},
    "D13": {"dia": 12.7, "unit_weight": 0.995, "area": 126.7},
    "D16": {"dia": 15.9, "unit_weight": 1.56, "area": 198.6},
    "D19": {"dia": 19.1, "unit_weight": 2.25, "area": 286.5},
    "D22": {"dia": 22.2, "unit_weight": 3.04, "area": 387.1},
    "D25": {"dia": 25.4, "unit_weight": 3.98, "area": 506.7},
    "D29": {"dia": 28.6, "unit_weight": 5.04, "area": 642.4},
    "D32": {"dia": 31.8, "unit_weight": 6.23, "area": 794.2},
    "D35": {"dia": 34.9, "unit_weight": 7.51, "area": 956.6},
}


class MemberQuantityInput(BaseModel):
    """Member dimensional and reinforcement properties for quantity takeoff."""
    member_id: int
    story: str = "1F"
    member_type: str = "BEAM"  # BEAM, COLUMN, WALL, SLAB, FOOTING
    b: float = 400.0           # mm (Width)
    h: float = 600.0           # mm (Depth / Height)
    length: float = 6000.0     # mm (Clear span / Height)
    fck: float = 24.0          # MPa
    fy: float = 400.0          # MPa

    # Rebars
    main_bar_size: str = "D22"
    main_bar_count: int = 8
    sub_bar_size: str = "D10"
    sub_bar_spacing: float = 200.0
    sub_bar_legs: int = 2
    is_top_bar: bool = False   # True if horizontal bar with > 300mm concrete below (alpha=1.3)


class MemberQuantityResult(BaseModel):
    """Individual member quantity takeoff outcome."""
    member_id: int
    story: str
    member_type: str
    concrete_vol_m3: float
    formwork_area_m2: float
    rebar_weight_kg: float
    rebar_by_size_kg: Dict[str, float] = Field(default_factory=dict)
    steel_weight_ton: float = 0.0


class ProjectQuantitySummary(BaseModel):
    """Aggregated project bill of quantities (BOQ)."""
    total_concrete_vol_m3: float = 0.0
    total_formwork_area_m2: float = 0.0
    total_rebar_weight_ton: float = 0.0
    total_steel_weight_ton: float = 0.0
    rebar_totals_by_size_kg: Dict[str, float] = Field(default_factory=dict)
    story_breakdowns: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    member_details: List[MemberQuantityResult] = Field(default_factory=list)


class QuantityEngine:
    """Quantity Takeoff Calculation Engine adhering to KDS 14 20 52."""

    @classmethod
    def calculate_tension_development_length(
        cls,
        bar_size: str,
        fck: float = 24.0,
        fy: float = 400.0,
        is_top_bar: bool = False
    ) -> float:
        """Calculate KDS 14 20 52 basic tension development length ld (mm)."""
        spec = REBAR_SPECS.get(bar_size.upper(), REBAR_SPECS["D22"])
        db = spec["dia"]

        # KDS 14 20 52 Simplified Equation: ld = (fy / (1.4 * lambda * sqrt(fck))) * alpha * beta * db
        # For standard bars with spacing/cover conforming to requirements:
        alpha = 1.3 if is_top_bar else 1.0  # Top bar factor
        beta = 1.0                          # Epoxy coating factor (uncoated)
        lambda_val = 1.0                    # Normal-weight concrete

        coeff = (fy / (1.4 * lambda_val * math.sqrt(max(fck, 1.0)))) * alpha * beta
        ld = coeff * db
        return max(ld, 300.0)  # Minimum 300mm

    @classmethod
    def calculate_lap_splice_length(
        cls,
        bar_size: str,
        fck: float = 24.0,
        fy: float = 400.0,
        is_top_bar: bool = False
    ) -> float:
        """Calculate Class B tension lap splice length (1.3 * ld)."""
        ld = cls.calculate_tension_development_length(bar_size, fck, fy, is_top_bar)
        return max(1.3 * ld, 300.0)

    @classmethod
    def compute_member_quantity(cls, inp: MemberQuantityInput) -> MemberQuantityResult:
        """Compute exact concrete, formwork, and rebar quantities for one member."""
        b_m = inp.b / 1000.0
        h_m = inp.h / 1000.0
        l_m = inp.length / 1000.0

        # 1. Concrete Volume (m3)
        conc_vol = round(b_m * h_m * l_m, 3)

        # 2. Formwork Area (m2)
        m_type = inp.member_type.upper()
        if "BEAM" in m_type:
            # Beam: 2 sides + bottom (top is cast with slab)
            formwork = (2 * h_m + b_m) * l_m
        elif "COLUMN" in m_type:
            # Column: 4 sides
            formwork = 2 * (b_m + h_m) * l_m
        elif "WALL" in m_type:
            # Wall: 2 faces + edges
            formwork = (2 * l_m + 2 * b_m) * h_m
        elif "FOOTING" in m_type:
            # Footing: 4 vertical perimeter faces
            formwork = 2 * (b_m + l_m) * h_m
        else:
            formwork = 2 * (b_m + h_m) * l_m
        formwork = round(formwork, 2)

        # 3. Rebar Weight
        rebar_dict: Dict[str, float] = {}

        # Main Rebars: length + development length at both ends (or lap splice)
        ld = cls.calculate_tension_development_length(inp.main_bar_size, inp.fck, inp.fy, inp.is_top_bar)
        single_main_bar_len_m = (inp.length + 2 * ld) / 1000.0
        main_spec = REBAR_SPECS.get(inp.main_bar_size.upper(), REBAR_SPECS["D22"])
        total_main_wt = inp.main_bar_count * single_main_bar_len_m * main_spec["unit_weight"]
        rebar_dict[inp.main_bar_size.upper()] = round(total_main_wt, 2)

        # Stirrups / Ties
        if inp.sub_bar_spacing > 0:
            num_ties = int(inp.length / inp.sub_bar_spacing) + 1
            # Perimeter of tie = 2*(b - 2*cover) + 2*(h - 2*cover) + 2*hook
            tie_perimeter_m = (2 * (inp.b - 80) + 2 * (inp.h - 80) + 200) / 1000.0
            tie_spec = REBAR_SPECS.get(inp.sub_bar_size.upper(), REBAR_SPECS["D10"])
            total_tie_wt = num_ties * tie_perimeter_m * tie_spec["unit_weight"]
            sub_key = inp.sub_bar_size.upper()
            rebar_dict[sub_key] = round(rebar_dict.get(sub_key, 0.0) + total_tie_wt, 2)

        total_rebar_wt = sum(rebar_dict.values())

        return MemberQuantityResult(
            member_id=inp.member_id,
            story=inp.story,
            member_type=inp.member_type,
            concrete_vol_m3=conc_vol,
            formwork_area_m2=formwork,
            rebar_weight_kg=round(total_rebar_wt, 2),
            rebar_by_size_kg=rebar_dict
        )

    @classmethod
    def aggregate_project_quantities(cls, members: List[MemberQuantityInput]) -> ProjectQuantitySummary:
        """Aggregate total project-level BOQ from member specifications."""
        total_conc = 0.0
        total_form = 0.0
        total_rebar_kg = 0.0
        size_totals: Dict[str, float] = {}
        story_map: Dict[str, Dict[str, float]] = {}
        details: List[MemberQuantityResult] = []

        for m_inp in members:
            res = cls.compute_member_quantity(m_inp)
            details.append(res)

            total_conc += res.concrete_vol_m3
            total_form += res.formwork_area_m2
            total_rebar_kg += res.rebar_weight_kg

            # Rebar size totals
            for sz, wt in res.rebar_by_size_kg.items():
                size_totals[sz] = round(size_totals.get(sz, 0.0) + wt, 2)

            # Story breakdown
            st = res.story
            if st not in story_map:
                story_map[st] = {"concrete_m3": 0.0, "formwork_m2": 0.0, "rebar_ton": 0.0}
            story_map[st]["concrete_m3"] = round(story_map[st]["concrete_m3"] + res.concrete_vol_m3, 3)
            story_map[st]["formwork_m2"] = round(story_map[st]["formwork_m2"] + res.formwork_area_m2, 2)
            story_map[st]["rebar_ton"] = round(story_map[st]["rebar_ton"] + res.rebar_weight_kg / 1000.0, 3)

        return ProjectQuantitySummary(
            total_concrete_vol_m3=round(total_conc, 3),
            total_formwork_area_m2=round(total_form, 2),
            total_rebar_weight_ton=round(total_rebar_kg / 1000.0, 3),
            rebar_totals_by_size_kg=size_totals,
            story_breakdowns=story_map,
            member_details=details
        )
