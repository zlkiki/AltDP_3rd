"""Governing Load Combination (LCB) Filter and Envelope Selector.

Reduces hundreds of load combinations into critical governing cases (4-12 cases)
for RC and Steel member design (P-M interaction extremes, max shear, max positive/negative moment).
"""

from typing import List, Dict, Set
from .model_schema import MemberForce, GoverningForceSummary


class GoverningLCBSelector:
    """Intelligent filter to identify critical governing load combinations."""

    @classmethod
    def select_governing_forces(
        cls,
        elem_id: int,
        elem_type: str,
        forces: List[MemberForce],
        max_cases: int = 12
    ) -> GoverningForceSummary:
        """Select critical governing forces for a specific member."""
        if not forces:
            return GoverningForceSummary(
                member_id=elem_id,
                member_type=elem_type,
                total_lcb_count=0,
                governing_lcb_list=[],
                critical_forces=[],
                max_dcr_estimated=0.0
            )

        elem_type_upper = elem_type.upper()
        if "COLUMN" in elem_type_upper:
            selected = cls._select_for_column(forces)
        elif "BEAM" in elem_type_upper or "GIRDER" in elem_type_upper:
            selected = cls._select_for_beam(forces)
        elif "WALL" in elem_type_upper:
            selected = cls._select_for_wall(forces)
        else:
            selected = cls._select_general(forces)

        # Unique LCB names
        gov_lcb_names = list(dict.fromkeys([f.lcb_name for f in selected]))
        if len(gov_lcb_names) > max_cases:
            gov_lcb_names = gov_lcb_names[:max_cases]
            selected = [f for f in selected if f.lcb_name in gov_lcb_names]

        # Calculate estimated rough DCR index for ranking
        max_dcr = cls._estimate_rough_dcr(elem_type_upper, selected)

        return GoverningForceSummary(
            member_id=elem_id,
            member_type=elem_type,
            total_lcb_count=len(set(f.lcb_name for f in forces)),
            governing_lcb_list=gov_lcb_names,
            critical_forces=selected,
            max_dcr_estimated=round(max_dcr, 3)
        )

    @classmethod
    def _select_for_column(cls, forces: List[MemberForce]) -> List[MemberForce]:
        """Critical cases for columns: Max/Min Axial, Max |My|, Max |Mz|, Max resultant M."""
        critical: Set[int] = set()

        # Group by index
        indexed_forces = list(enumerate(forces))

        # 1. Max Compression (most negative P if standard sign, or max abs(P))
        # Note: In standard Midas, compression is often (-) or (+) depending on convention.
        # We consider both max positive P (Tension) and max negative P (Compression).
        idx_max_p = max(indexed_forces, key=lambda x: x[1].p)[0]
        idx_min_p = min(indexed_forces, key=lambda x: x[1].p)[0]
        critical.add(idx_max_p)
        critical.add(idx_min_p)

        # 2. Max Bending Moments
        idx_max_my = max(indexed_forces, key=lambda x: abs(x[1].my))[0]
        idx_max_mz = max(indexed_forces, key=lambda x: abs(x[1].mz))[0]
        critical.add(idx_max_my)
        critical.add(idx_max_mz)

        # 3. Resultant Moment sqrt(My^2 + Mz^2)
        idx_max_m_res = max(indexed_forces, key=lambda x: (x[1].my ** 2 + x[1].mz ** 2) ** 0.5)[0]
        critical.add(idx_max_m_res)

        # 4. Max Shear
        idx_max_vy = max(indexed_forces, key=lambda x: abs(x[1].vy))[0]
        idx_max_vz = max(indexed_forces, key=lambda x: abs(x[1].vz))[0]
        critical.add(idx_max_vy)
        critical.add(idx_max_vz)

        return [forces[i] for i in sorted(critical)]

    @classmethod
    def _select_for_beam(cls, forces: List[MemberForce]) -> List[MemberForce]:
        """Critical cases for beams: Max (+)/(-) Mz, Max Vy at ends (I, J) and mid (M)."""
        critical: Set[int] = set()
        indexed_forces = list(enumerate(forces))

        # Separate by position
        for pos in ("I", "M", "J"):
            pos_forces = [item for item in indexed_forces if item[1].position == pos]
            if not pos_forces:
                continue

            # Max Positive Moment (usually Mz)
            idx_max_pos_m = max(pos_forces, key=lambda x: x[1].mz)[0]
            # Max Negative Moment
            idx_min_neg_m = min(pos_forces, key=lambda x: x[1].mz)[0]
            # Max Shear Vy
            idx_max_v = max(pos_forces, key=lambda x: abs(x[1].vy))[0]

            critical.add(idx_max_pos_m)
            critical.add(idx_min_neg_m)
            critical.add(idx_max_v)

        return [forces[i] for i in sorted(critical)]

    @classmethod
    def _select_for_wall(cls, forces: List[MemberForce]) -> List[MemberForce]:
        """Critical cases for shear walls: Max Axial, Max In-plane Moment, Max Shear."""
        critical: Set[int] = set()
        indexed_forces = list(enumerate(forces))

        idx_max_p = max(indexed_forces, key=lambda x: abs(x[1].p))[0]
        idx_max_m = max(indexed_forces, key=lambda x: max(abs(x[1].my), abs(x[1].mz)))[0]
        idx_max_v = max(indexed_forces, key=lambda x: max(abs(x[1].vy), abs(x[1].vz)))[0]

        critical.update([idx_max_p, idx_max_m, idx_max_v])
        return [forces[i] for i in sorted(critical)]

    @classmethod
    def _select_general(cls, forces: List[MemberForce]) -> List[MemberForce]:
        """Fallback selector for braces and general elements."""
        critical: Set[int] = set()
        indexed_forces = list(enumerate(forces))

        idx_max_p = max(indexed_forces, key=lambda x: x[1].p)[0]
        idx_min_p = min(indexed_forces, key=lambda x: x[1].p)[0]
        idx_max_m = max(indexed_forces, key=lambda x: (x[1].my ** 2 + x[1].mz ** 2) ** 0.5)[0]

        critical.update([idx_max_p, idx_min_p, idx_max_m])
        return [forces[i] for i in sorted(critical)]

    @staticmethod
    def _estimate_rough_dcr(elem_type: str, forces: List[MemberForce]) -> float:
        """Estimate preliminary DCR index based on force intensities."""
        if not forces:
            return 0.0
        # Representative metric: normalize based on standard typical capacities
        # Column: (P/5000 + M/500), Beam: M/300
        max_val = 0.0
        for f in forces:
            if "COLUMN" in elem_type:
                dcr = abs(f.p) / 4000.0 + max(abs(f.my), abs(f.mz)) / 400.0
            elif "BEAM" in elem_type:
                dcr = abs(f.mz) / 300.0 + abs(f.vy) / 250.0
            else:
                dcr = abs(f.p) / 2000.0 + max(abs(f.my), abs(f.mz)) / 200.0
            if dcr > max_val:
                max_val = dcr
        return min(max_val, 2.0)
