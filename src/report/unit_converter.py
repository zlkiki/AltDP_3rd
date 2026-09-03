"""Unit Conversion and Numerical Formatting Engine for AltDP_3rd Reports.

Provides bidirectional conversion between SI, MKS, and US Customary units
with structural engineering precision and significant figure rules.
"""

from typing import Union


class UnitConverter:
    """Handles unit conversion for force, moment, stress, and dimensions."""

    # Conversion Factors to base SI units (kN, kN·m, MPa, mm)
    # MKS factors
    KN_TO_TONF = 0.101971621
    KNM_TO_TONFM = 0.101971621
    MPA_TO_KGFCM2 = 10.1971621
    MM_TO_CM = 0.1

    # US Customary factors
    KN_TO_KIP = 0.224808943
    KNM_TO_FTKIP = 0.737562149
    MPA_TO_KSI = 0.145037738
    MM_TO_IN = 0.0393700787

    @classmethod
    def convert_force(cls, value: float, target_unit: str = "SI") -> tuple[float, str]:
        """Convert force from kN to target unit."""
        unit = target_unit.upper()
        if unit == "MKS":
            return value * cls.KN_TO_TONF, "tonf"
        elif unit == "US":
            return value * cls.KN_TO_KIP, "kip"
        return value, "kN"

    @classmethod
    def convert_moment(cls, value: float, target_unit: str = "SI") -> tuple[float, str]:
        """Convert moment from kN·m to target unit."""
        unit = target_unit.upper()
        if unit == "MKS":
            return value * cls.KNM_TO_TONFM, "tonf·m"
        elif unit == "US":
            return value * cls.KNM_TO_FTKIP, "ft·kip"
        return value, "kN·m"

    @classmethod
    def convert_stress(cls, value: float, target_unit: str = "SI") -> tuple[float, str]:
        """Convert stress from MPa to target unit."""
        unit = target_unit.upper()
        if unit == "MKS":
            return value * cls.MPA_TO_KGFCM2, "kgf/cm²"
        elif unit == "US":
            return value * cls.MPA_TO_KSI, "ksi"
        return value, "MPa"

    @classmethod
    def convert_length(cls, value: float, target_unit: str = "SI") -> tuple[float, str]:
        """Convert length from mm to target unit."""
        unit = target_unit.upper()
        if unit == "MKS":
            return value * cls.MM_TO_CM, "cm"
        elif unit == "US":
            return value * cls.MM_TO_IN, "in"
        return value, "mm"

    @classmethod
    def format_force(cls, value: Union[float, int], target_unit: str = "SI") -> str:
        """Format force string with engineering units."""
        val, symbol = cls.convert_force(float(value), target_unit)
        return f"{val:,.2f} {symbol}"

    @classmethod
    def format_moment(cls, value: Union[float, int], target_unit: str = "SI") -> str:
        """Format moment string with engineering units."""
        val, symbol = cls.convert_moment(float(value), target_unit)
        return f"{val:,.2f} {symbol}"

    @classmethod
    def format_stress(cls, value: Union[float, int], target_unit: str = "SI") -> str:
        """Format stress string with engineering units."""
        val, symbol = cls.convert_stress(float(value), target_unit)
        return f"{val:,.2f} {symbol}"
