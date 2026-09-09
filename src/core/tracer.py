"""Calculation Tracer and AST Serializer for AltDP-Core Platform.

Captures engineering calculation steps, LaTeX/KaTeX formulas, substitutions,
results, and OK/NG evaluations into a structured JSON AST for automated A4 report rendering.
Eliminates report template hardcoding and KaTeX escape bugs.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
import json


@dataclass
class CalculationStep:
    """Individual formula calculation step in the engineering audit trail."""
    chapter: str
    section: str
    standard_ref: str
    formula: str
    substitutions: Union[Dict[str, Any], str]
    result: Union[str, float, int]
    unit: str
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter": self.chapter,
            "section": self.section,
            "standard_ref": self.standard_ref,
            "formula": self.formula,
            "substitutions": self.substitutions,
            "result": self.result,
            "unit": self.unit,
            "description": self.description or ""
        }


@dataclass
class EvaluationStep:
    """Structural compliance check with Demand-Capacity Ratio (DCR) and OK/NG verdict."""
    chapter: str
    title: str
    equation: str
    left_val: Union[str, float, int]
    right_val: Union[str, float, int]
    unit: str
    dcr: float
    status: str  # "OK" or "NG"
    standard_ref: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter": self.chapter,
            "title": self.title,
            "equation": self.equation,
            "left_val": self.left_val,
            "right_val": self.right_val,
            "unit": self.unit,
            "dcr": round(float(self.dcr), 4),
            "status": self.status,
            "standard_ref": self.standard_ref or "",
            "description": self.description or ""
        }


@dataclass
class ChapterAST:
    """Chapter grouping containing calculation steps, evaluations, and engineering notes."""
    id: str
    title: str
    steps: List[CalculationStep] = field(default_factory=list)
    evaluations: List[EvaluationStep] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "steps": [s.to_dict() for s in self.steps],
            "evaluations": [e.to_dict() for e in self.evaluations],
            "notes": list(self.notes)
        }


class CalculationTracer:
    """Engine calculation tracer collecting steps and compiling KaTeX AST reports."""

    def __init__(self, title: str = "KDS 구조계산서", standard: str = "KDS 14 20 00", member_name: str = "부재"):
        self.title = title
        self.standard = standard
        self.member_name = member_name
        self._chapters: Dict[str, ChapterAST] = {}
        self._steps: List[CalculationStep] = []
        self._evaluations: List[EvaluationStep] = []

    def _get_or_create_chapter(self, chapter_title: str) -> ChapterAST:
        if chapter_title not in self._chapters:
            chap_id = f"chap_{len(self._chapters) + 1}"
            self._chapters[chapter_title] = ChapterAST(id=chap_id, title=chapter_title)
        return self._chapters[chapter_title]

    def step(
        self,
        chapter: str,
        section: str,
        standard_ref: str,
        formula: str,
        substitutions: Union[Dict[str, Any], str],
        result: Union[str, float, int],
        unit: str,
        description: Optional[str] = None
    ) -> CalculationStep:
        """Record an explicit mathematical derivation step."""
        step_obj = CalculationStep(
            chapter=chapter,
            section=section,
            standard_ref=standard_ref,
            formula=formula,
            substitutions=substitutions,
            result=result,
            unit=unit,
            description=description
        )
        self._steps.append(step_obj)
        chap = self._get_or_create_chapter(chapter)
        chap.steps.append(step_obj)
        return step_obj

    def evaluation(
        self,
        title: str,
        equation: str,
        left_val: Union[str, float, int],
        right_val: Union[str, float, int],
        unit: str,
        dcr: float,
        status: Optional[str] = None,
        chapter: Optional[str] = None,
        standard_ref: Optional[str] = None,
        description: Optional[str] = None
    ) -> EvaluationStep:
        """Record a demand-capacity ratio (DCR) code check evaluation."""
        if status is None:
            status = "OK" if float(dcr) <= 1.0 else "NG"
        
        target_chapter = chapter or "종합 안전성 검토"
        eval_obj = EvaluationStep(
            chapter=target_chapter,
            title=title,
            equation=equation,
            left_val=left_val,
            right_val=right_val,
            unit=unit,
            dcr=dcr,
            status=status,
            standard_ref=standard_ref,
            description=description
        )
        self._evaluations.append(eval_obj)
        chap = self._get_or_create_chapter(target_chapter)
        chap.evaluations.append(eval_obj)
        return eval_obj

    def add_note(self, chapter: str, note: str) -> None:
        """Add an engineering note or textual explanation to a chapter."""
        chap = self._get_or_create_chapter(chapter)
        chap.notes.append(note)

    @property
    def max_dcr(self) -> float:
        """Maximum DCR among all recorded evaluations."""
        if not self._evaluations:
            return 0.0
        return max(float(e.dcr) for e in self._evaluations)

    @property
    def is_safe(self) -> bool:
        """True if all recorded evaluations are OK (status == 'OK' and dcr <= 1.0)."""
        if not self._evaluations:
            return True
        return all(e.status == "OK" and float(e.dcr) <= 1.0001 for e in self._evaluations)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete tracer AST to JSON-ready dictionary."""
        failed_count = sum(1 for e in self._evaluations if e.status != "OK" or float(e.dcr) > 1.0001)
        max_dcr = round(self.max_dcr, 4)
        status_str = "OK" if (self.is_safe and failed_count == 0) else "NG"

        return {
            "title": self.title,
            "standard": self.standard,
            "member_name": self.member_name,
            "summary": {
                "status": status_str,
                "is_safe": self.is_safe,
                "max_dcr": max_dcr,
                "evaluations_count": len(self._evaluations),
                "failed_count": failed_count
            },
            "chapters": [chap.to_dict() for chap in self._chapters.values()],
            "all_steps": [s.to_dict() for s in self._steps],
            "all_evaluations": [e.to_dict() for e in self._evaluations]
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to formatted JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
