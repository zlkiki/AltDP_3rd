"""International Structural Codes and Ultra-Precision Multi-Unit Converter Package.

Includes:
- Multi-unit converter (SI, MKS, US Imperial)
- Eurocode 2 (EN 1992-1-1) & Eurocode 3 (EN 1993-1-1)
- US Standards ACI 318-19 & AISC 360-16 LRFD
- Indian Standards IS 456:2000 & IS 800:2007
"""

from src.engine.international.units import (
    UnitSystem,
    UnitType,
    convert_unit,
    convert_dict_units,
)
from src.engine.international.eurocode import (
    EC2BeamDesignResult,
    check_ec2_rc_beam,
    EC3SteelDesignResult,
    check_ec3_steel_beam,
)
from src.engine.international.us_code import (
    ACI318BeamDesignResult,
    check_aci318_rc_beam,
    AISC360SteelDesignResult,
    check_aisc360_steel_beam,
)
from src.engine.international.is_code import (
    IS456BeamDesignResult,
    check_is456_rc_beam,
    IS800SteelDesignResult,
    check_is800_steel_beam,
)

__all__ = [
    "UnitSystem",
    "UnitType",
    "convert_unit",
    "convert_dict_units",
    "EC2BeamDesignResult",
    "check_ec2_rc_beam",
    "EC3SteelDesignResult",
    "check_ec3_steel_beam",
    "ACI318BeamDesignResult",
    "check_aci318_rc_beam",
    "AISC360SteelDesignResult",
    "check_aisc360_steel_beam",
    "IS456BeamDesignResult",
    "check_is456_rc_beam",
    "IS800SteelDesignResult",
    "check_is800_steel_beam",
]
