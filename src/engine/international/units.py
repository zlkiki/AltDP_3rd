"""Ultra-Precision Multi-Unit System Converter (SI <-> MKS <-> US Imperial).

Provides bidirectional floating-point conversions with precision error <= 1e-7.
Supports Length, Force, Moment, Stress, Area, Inertia, Section Modulus, and Density.
"""

from enum import Enum
from typing import Dict, Any, Union


class UnitSystem(str, Enum):
    """Standard structural engineering unit systems."""
    SI = "SI"                  # mm, N, MPa, kN, kN*m
    MKS = "MKS"                # cm, kgf, tf, kgf/cm2, tf*m
    US_IMPERIAL = "US_IMPERIAL"# in, ft, lb, kip, ksi, ft*kip


class UnitType(str, Enum):
    """Physical quantity unit types."""
    LENGTH = "LENGTH"                    # SI: mm | MKS: cm | US: in
    SPAN_LENGTH = "SPAN_LENGTH"          # SI: m  | MKS: m  | US: ft
    FORCE = "FORCE"                      # SI: kN | MKS: tf | US: kip
    FORCE_SMALL = "FORCE_SMALL"          # SI: N  | MKS: kgf| US: lb
    MOMENT = "MOMENT"                    # SI: kN*m | MKS: tf*m | US: ft*kip
    MOMENT_SMALL = "MOMENT_SMALL"        # SI: N*mm | MKS: kgf*m | US: in*kip
    STRESS = "STRESS"                    # SI: MPa (N/mm2) | MKS: kgf/cm2 | US: ksi
    STRESS_SMALL = "STRESS_SMALL"        # SI: kPa | MKS: kgf/m2 | US: psi
    AREA = "AREA"                        # SI: mm2 | MKS: cm2 | US: in2
    INERTIA = "INERTIA"                  # SI: mm4 | MKS: cm4 | US: in4
    SECTION_MODULUS = "SECTION_MODULUS"  # SI: mm3 | MKS: cm3 | US: in3


# High-precision base conversion factors to SI reference units:
# Base SI Reference Units:
# - LENGTH: mm
# - SPAN_LENGTH: m
# - FORCE: kN
# - FORCE_SMALL: N
# - MOMENT: kN*m
# - MOMENT_SMALL: N*mm
# - STRESS: MPa
# - STRESS_SMALL: kPa
# - AREA: mm2
# - INERTIA: mm4
# - SECTION_MODULUS: mm3

# Standard exact constants:
# 1 inch = 25.4 mm exactly
# 1 foot = 12 inches = 304.8 mm = 0.3048 m
# 1 lb mass in standard gravity (g = 9.80665 m/s2):
# 1 lb force = 0.45359237 * 9.80665 N = 4.4482216152605 N
# 1 kip = 1000 lb = 4.4482216152605 kN
# 1 kgf = 9.80665 N = 0.00980665 kN
# 1 tf = 1000 kgf = 9.80665 kN
# 1 ksi = 1 kip / 1 in2 = 4.4482216152605 kN / (25.4 mm)^2 = 6.894757293168361 MPa
# 1 kgf/cm2 = 9.80665 N / 100 mm2 = 0.0980665 MPa

INCH_TO_MM = 25.4
FT_TO_M = 0.3048
KIP_TO_KN = 4.4482216152605
LB_TO_N = 4.4482216152605
TF_TO_KN = 9.80665
KGF_TO_N = 9.80665
KSI_TO_MPA = 6.894757293168361
KGF_CM2_TO_MPA = 0.0980665

# Conversion factors: value_in_si = value_in_unit * TO_SI_FACTORS[system][unit_type]
TO_SI_FACTORS: Dict[UnitSystem, Dict[UnitType, float]] = {
    UnitSystem.SI: {
        UnitType.LENGTH: 1.0,
        UnitType.SPAN_LENGTH: 1.0,
        UnitType.FORCE: 1.0,
        UnitType.FORCE_SMALL: 1.0,
        UnitType.MOMENT: 1.0,
        UnitType.MOMENT_SMALL: 1.0,
        UnitType.STRESS: 1.0,
        UnitType.STRESS_SMALL: 1.0,
        UnitType.AREA: 1.0,
        UnitType.INERTIA: 1.0,
        UnitType.SECTION_MODULUS: 1.0,
    },
    UnitSystem.MKS: {
        UnitType.LENGTH: 10.0,                   # 1 cm = 10 mm
        UnitType.SPAN_LENGTH: 1.0,               # 1 m = 1 m
        UnitType.FORCE: TF_TO_KN,                # 1 tf = 9.80665 kN
        UnitType.FORCE_SMALL: KGF_TO_N,          # 1 kgf = 9.80665 N
        UnitType.MOMENT: TF_TO_KN,               # 1 tf*m = 9.80665 kN*m
        UnitType.MOMENT_SMALL: KGF_TO_N * 1000.0,# 1 kgf*m = 9806.65 N*mm
        UnitType.STRESS: KGF_CM2_TO_MPA,         # 1 kgf/cm2 = 0.0980665 MPa
        UnitType.STRESS_SMALL: 0.0980665 * 1000.0 / 100.0, # 1 kgf/m2 to kPa
        UnitType.AREA: 100.0,                    # 1 cm2 = 100 mm2
        UnitType.INERTIA: 10000.0,               # 1 cm4 = 10,000 mm4
        UnitType.SECTION_MODULUS: 1000.0,        # 1 cm3 = 1,000 mm3
    },
    UnitSystem.US_IMPERIAL: {
        UnitType.LENGTH: INCH_TO_MM,             # 1 in = 25.4 mm
        UnitType.SPAN_LENGTH: FT_TO_M,           # 1 ft = 0.3048 m
        UnitType.FORCE: KIP_TO_KN,               # 1 kip = 4.4482216152605 kN
        UnitType.FORCE_SMALL: LB_TO_N,           # 1 lb = 4.4482216152605 N
        UnitType.MOMENT: KIP_TO_KN * FT_TO_M,    # 1 ft*kip = 1.3558179483314004 kN*m
        UnitType.MOMENT_SMALL: KIP_TO_KN * 1000.0 * INCH_TO_MM, # 1 in*kip in N*mm
        UnitType.STRESS: KSI_TO_MPA,             # 1 ksi = 6.894757293168361 MPa
        UnitType.STRESS_SMALL: KSI_TO_MPA * 1000.0 / 1000.0, # psi to kPa
        UnitType.AREA: INCH_TO_MM ** 2,          # 1 in2 = 645.16 mm2
        UnitType.INERTIA: INCH_TO_MM ** 4,       # 1 in4 = 416231.4256 mm4
        UnitType.SECTION_MODULUS: INCH_TO_MM ** 3,# 1 in3 = 16387.064 mm3
    },
}


def convert_unit(
    value: float,
    unit_type: Union[UnitType, str],
    from_system: Union[UnitSystem, str],
    to_system: Union[UnitSystem, str],
) -> float:
    """Convert a physical engineering quantity between unit systems with ultra-precision.
    
    Args:
        value: Numeric value to convert.
        unit_type: Quantity category (UnitType enum or string).
        from_system: Source unit system (UnitSystem enum or string).
        to_system: Target unit system (UnitSystem enum or string).
        
    Returns:
        Converted value in target unit system.
    """
    if isinstance(unit_type, str):
        unit_type = UnitType(unit_type.upper())
    if isinstance(from_system, str):
        from_system = UnitSystem(from_system.upper())
    if isinstance(to_system, str):
        to_system = UnitSystem(to_system.upper())

    if from_system == to_system:
        return float(value)

    from_factor = TO_SI_FACTORS[from_system][unit_type]
    to_factor = TO_SI_FACTORS[to_system][unit_type]

    # Convert to SI reference base, then to target
    value_in_si = value * from_factor
    return value_in_si / to_factor


def convert_dict_units(
    data: Dict[str, Any],
    type_mapping: Dict[str, Union[UnitType, str]],
    from_system: Union[UnitSystem, str],
    to_system: Union[UnitSystem, str],
) -> Dict[str, Any]:
    """Convert a dictionary of engineering parameters according to specified type mapping.
    
    Args:
        data: Key-value dictionary of numerical parameters.
        type_mapping: Mapping of field name -> UnitType.
        from_system: Source system.
        to_system: Target system.
        
    Returns:
        New dictionary with converted values.
    """
    result = {}
    for key, val in data.items():
        if key in type_mapping and isinstance(val, (int, float)):
            result[key] = convert_unit(float(val), type_mapping[key], from_system, to_system)
        else:
            result[key] = val
    return result
