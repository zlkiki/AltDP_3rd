# app/engines/common/units.py
"""Unit Conversion & Engineering Number Formatting Helpers."""
import math
from typing import Union


def to_si_force(val_kn: float) -> float:
    """Converts kN to N."""
    return val_kn * 1e3


def to_si_moment(val_kn_m: float) -> float:
    """Converts kN*m to N*mm."""
    return val_kn_m * 1e6


def from_si_force(val_n: float) -> float:
    """Converts N to kN."""
    return val_n * 1e-3


def from_si_moment(val_n_mm: float) -> float:
    """Converts N*mm to kN*m."""
    return val_n_mm * 1e-6


def format_num(val: Union[float, int], decimals: int = 2) -> str:
    """Formats a float to a fixed decimal string."""
    if val is None or not math.isfinite(val):
        return "N/A"
    return f"{val:.{decimals}f}"
