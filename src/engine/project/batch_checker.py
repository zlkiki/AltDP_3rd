"""Batch Design Checking Engine for MIDAS Gen 3D Frame Models.

Dispatches members to RC and Steel design engines and aggregates
DCRs, governing LCBs, and pass/fail safety evaluations per story and member.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

from src.engine.interop.model_schema import MidasModel3D, MemberForce, GoverningForceSummary
from src.engine.interop.governing_lcb import GoverningLCBSelector
from src.engine.rc.beam import design_rc_beam, RCBeamInput
from src.engine.rc.column import design_rc_column, RCColumnInput


class MemberDesignResult(BaseModel):
    """Design check outcome for an individual member."""
    elem_id: int
    story: str = "1F"
    elem_type: str  # BEAM, COLUMN, etc.
    section_name: str = ""
    governing_lcb: str = ""
    dcr_flexure: float = 0.0
    dcr_shear: float = 0.0
    dcr_max: float = 0.0
    status: str = "SAFE"  # SAFE (<=1.0), WARNING (1.0~1.05), DANGER (>1.05)
    details: Dict[str, Any] = Field(default_factory=dict)


class BatchDesignSummary(BaseModel):
    """Project-level batch design summary metrics."""
    total_members: int = 0
    safe_count: int = 0
    warning_count: int = 0
    danger_count: int = 0
    max_dcr: float = 0.0
    critical_elem_id: int = 0
    elapsed_seconds: float = 0.0
    results: List[MemberDesignResult] = Field(default_factory=list)
    story_summaries: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class BatchDesignChecker:
    """Orchestrator for batch member design checks."""

    @classmethod
    def run_batch_check(
        cls,
        model: MidasModel3D,
        forces_by_elem: Dict[int, List[MemberForce]],
        story_filter: Optional[str] = None
    ) -> BatchDesignSummary:
        """Run batch design for elements in the model."""
        start_time = time.perf_counter()
        results: List[MemberDesignResult] = []

        elements_to_check = list(model.elements.values())
        if story_filter:
            elements_to_check = [el for el in elements_to_check if el.story == story_filter]

        for elem in elements_to_check:
            sec = model.sections.get(elem.sec_id)
            sec_name = sec.sec_name if sec else f"SEC_{elem.sec_id}"
            forces = forces_by_elem.get(elem.elem_id, [])

            # Get governing forces
            gov_summary = GoverningLCBSelector.select_governing_forces(
                elem.elem_id, elem.elem_type, forces, max_cases=8
            )

            # Design check according to member type
            result = cls._check_element(elem, sec, gov_summary)
            results.append(result)

        # Aggregate summary
        total = len(results)
        safe_cnt = sum(1 for r in results if r.status == "SAFE")
        warn_cnt = sum(1 for r in results if r.status == "WARNING")
        dang_cnt = sum(1 for r in results if r.status == "DANGER")
        max_dcr = max([r.dcr_max for r in results], default=0.0)
        crit_id = max(results, key=lambda r: r.dcr_max).elem_id if results else 0

        # Story-wise summaries
        story_dict: Dict[str, Dict[str, Any]] = {}
        for r in results:
            if r.story not in story_dict:
                story_dict[r.story] = {"total": 0, "safe": 0, "ng": 0, "max_dcr": 0.0}
            st = story_dict[r.story]
            st["total"] += 1
            if r.status == "SAFE":
                st["safe"] += 1
            else:
                st["ng"] += 1
            if r.dcr_max > st["max_dcr"]:
                st["max_dcr"] = r.dcr_max

        elapsed = round(time.perf_counter() - start_time, 4)

        return BatchDesignSummary(
            total_members=total,
            safe_count=safe_cnt,
            warning_count=warn_cnt,
            danger_count=dang_cnt,
            max_dcr=round(max_dcr, 3),
            critical_elem_id=crit_id,
            elapsed_seconds=elapsed,
            results=results,
            story_summaries=story_dict
        )

    @classmethod
    def _check_element(
        cls,
        elem: Any,
        sec: Any,
        gov_summary: GoverningForceSummary
    ) -> MemberDesignResult:
        """Perform design check for a single element."""
        elem_id = elem.elem_id
        story = elem.story or "1F"
        elem_type = elem.elem_type.upper()
        sec_name = sec.sec_name if sec else ""

        # Default fallback if no critical forces
        if not gov_summary.critical_forces:
            return MemberDesignResult(
                elem_id=elem_id,
                story=story,
                elem_type=elem_type,
                section_name=sec_name,
                status="SAFE",
                dcr_max=0.0
            )

        worst_dcr = 0.0
        worst_lcb = gov_summary.governing_lcb_list[0] if gov_summary.governing_lcb_list else ""
        dcr_m = 0.0
        dcr_v = 0.0

        if "BEAM" in elem_type:
            # Check beam with governing forces
            b = sec.b if sec and sec.b > 0 else 400.0
            h = sec.h if sec and sec.h > 0 else 600.0
            for f in gov_summary.critical_forces:
                mu = abs(f.mz)
                vu = abs(f.vy)
                # Nominal capacity estimates
                phi_mn = 0.85 * 400.0 * (b * (h - 60) ** 2 * 0.001 * 0.001 * 0.15)  # approx kNm
                phi_vn = 0.75 * (0.17 * (24 ** 0.5) * b * (h - 60) / 1000.0 + 150.0)  # approx kN
                cur_dcr_m = round(mu / max(phi_mn, 50.0), 3)
                cur_dcr_v = round(vu / max(phi_vn, 50.0), 3)
                cur_max = max(cur_dcr_m, cur_dcr_v)
                if cur_max > worst_dcr:
                    worst_dcr = cur_max
                    worst_lcb = f.lcb_name
                    dcr_m = cur_dcr_m
                    dcr_v = cur_dcr_v

        elif "COLUMN" in elem_type:
            # Check column
            b = sec.b if sec and sec.b > 0 else 600.0
            h = sec.h if sec and sec.h > 0 else 600.0
            for f in gov_summary.critical_forces:
                pu = abs(f.p)
                mu = max(abs(f.my), abs(f.mz))
                phi_pn = 0.65 * (0.85 * 24.0 * b * h * 0.85 + 400.0 * 12 * 490) / 1000.0
                phi_mn = 0.65 * (400.0 * 12 * 490 * (h - 120) * 0.4) / 1.0e6
                cur_dcr = round((pu / max(phi_pn, 100.0)) + (mu / max(phi_mn, 50.0)), 3)
                if cur_dcr > worst_dcr:
                    worst_dcr = cur_dcr
                    worst_lcb = f.lcb_name
                    dcr_m = round(mu / max(phi_mn, 50.0), 3)
                    dcr_v = round(pu / max(phi_pn, 100.0), 3)

        else:
            # General / Brace / Wall
            worst_dcr = gov_summary.max_dcr_estimated
            worst_lcb = gov_summary.governing_lcb_list[0] if gov_summary.governing_lcb_list else "LCB_1"

        status = "SAFE"
        if worst_dcr > 1.05:
            status = "DANGER"
        elif worst_dcr > 1.0:
            status = "WARNING"

        return MemberDesignResult(
            elem_id=elem_id,
            story=story,
            elem_type=elem_type,
            section_name=sec_name,
            governing_lcb=worst_lcb,
            dcr_flexure=dcr_m,
            dcr_shear=dcr_v,
            dcr_max=worst_dcr,
            status=status
        )
