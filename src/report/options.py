"""Report Options Data Structures for AltDP_3rd Calculation Reports.

Defines report presentation modes, unit systems, and filtering toggles.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReportOptions:
    """Configuration options for structural calculation report generation."""
    report_mode: str = "standard"        # "summary" | "standard" | "detail" | "input_data"
    unit_system: str = "SI"              # "SI" | "MKS" | "US"
    include_user_input: bool = True     # Toggle raw input data table
    governing_only: bool = False        # Filter only governing load combination
    include_drawings: bool = True       # Include SVG cross-sections and diagrams
    author: Optional[str] = "AltDP Engineer"
    company: Optional[str] = "AltDP Engineering"
    notes: Optional[str] = None
