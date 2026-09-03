"""Tests for Ultra-Precision Multi-Unit Converter.

Validates exact floating-point round-trip conversions (precision error <= 1e-7)
across SI, MKS, and US Imperial systems.
"""

import pytest
from src.engine.international.units import (
    UnitSystem,
    UnitType,
    convert_unit,
    convert_dict_units,
    INCH_TO_MM,
    KIP_TO_KN,
    KSI_TO_MPA,
)


class TestUnitConversions:
    """Test ultra-precision conversion factors and round-trips."""

    def test_length_conversions_roundtrip(self):
        val_mm = 600.0  # 600 mm
        # Convert to US Imperial (inches)
        val_in = convert_unit(val_mm, UnitType.LENGTH, UnitSystem.SI, UnitSystem.US_IMPERIAL)
        assert val_in == pytest.approx(600.0 / 25.4, rel=1e-9)

        # Convert back to SI
        val_mm_back = convert_unit(val_in, UnitType.LENGTH, UnitSystem.US_IMPERIAL, UnitSystem.SI)
        assert val_mm_back == pytest.approx(val_mm, rel=1e-9)
        assert abs(val_mm_back - val_mm) <= 1e-7

        # Convert to MKS (cm)
        val_cm = convert_unit(val_mm, UnitType.LENGTH, UnitSystem.SI, UnitSystem.MKS)
        assert val_cm == pytest.approx(60.0, rel=1e-9)

    def test_force_conversions_roundtrip(self):
        val_kn = 250.0  # 250 kN
        # Convert to US Imperial (kip)
        val_kip = convert_unit(val_kn, UnitType.FORCE, UnitSystem.SI, UnitSystem.US_IMPERIAL)
        assert val_kip == pytest.approx(250.0 / KIP_TO_KN, rel=1e-9)

        # Roundtrip back to kN
        val_kn_back = convert_unit(val_kip, UnitType.FORCE, UnitSystem.US_IMPERIAL, UnitSystem.SI)
        assert abs(val_kn_back - val_kn) <= 1e-7

        # Convert to MKS (tf)
        val_tf = convert_unit(val_kn, UnitType.FORCE, UnitSystem.SI, UnitSystem.MKS)
        assert val_tf == pytest.approx(250.0 / 9.80665, rel=1e-9)

    def test_moment_conversions_roundtrip(self):
        val_knm = 350.0  # 350 kN*m
        val_ftkip = convert_unit(val_knm, UnitType.MOMENT, UnitSystem.SI, UnitSystem.US_IMPERIAL)
        val_knm_back = convert_unit(val_ftkip, UnitType.MOMENT, UnitSystem.US_IMPERIAL, UnitSystem.SI)
        assert abs(val_knm_back - val_knm) <= 1e-7

    def test_stress_conversions_roundtrip(self):
        val_mpa = 27.5  # 27.5 MPa
        val_ksi = convert_unit(val_mpa, UnitType.STRESS, UnitSystem.SI, UnitSystem.US_IMPERIAL)
        val_mpa_back = convert_unit(val_ksi, UnitType.STRESS, UnitSystem.US_IMPERIAL, UnitSystem.SI)
        assert abs(val_mpa_back - val_mpa) <= 1e-7

        # MKS kgf/cm2
        val_kgfcm2 = convert_unit(val_mpa, UnitType.STRESS, UnitSystem.SI, UnitSystem.MKS)
        assert val_kgfcm2 == pytest.approx(27.5 / 0.0980665, rel=1e-9)

    def test_area_inertia_modulus_conversions(self):
        val_area = 10000.0  # 10,000 mm2
        val_in2 = convert_unit(val_area, UnitType.AREA, UnitSystem.SI, UnitSystem.US_IMPERIAL)
        val_area_back = convert_unit(val_in2, UnitType.AREA, UnitSystem.US_IMPERIAL, UnitSystem.SI)
        assert abs(val_area_back - val_area) <= 1e-7

    def test_convert_dict_units(self):
        input_data = {
            "name": "Beam-1",
            "b": 300.0,
            "h": 600.0,
            "span": 6.0,
            "moment": 180.0,
            "fck": 24.0,
        }
        type_mapping = {
            "b": UnitType.LENGTH,
            "h": UnitType.LENGTH,
            "span": UnitType.SPAN_LENGTH,
            "moment": UnitType.MOMENT,
            "fck": UnitType.STRESS,
        }
        converted = convert_dict_units(input_data, type_mapping, UnitSystem.SI, UnitSystem.US_IMPERIAL)
        assert converted["name"] == "Beam-1"
        assert converted["b"] == pytest.approx(300.0 / 25.4, rel=1e-7)
        assert converted["span"] == pytest.approx(6.0 / 0.3048, rel=1e-7)
