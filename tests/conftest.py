"""Pytest Configuration and Fixtures for AltDP_3rd."""

import pytest
from src.engine.db.materials import ConcreteMaterial, RebarMaterial, SteelMaterial


@pytest.fixture
def default_concrete():
    return ConcreteMaterial(fck=24.0)


@pytest.fixture
def default_rebar():
    return RebarMaterial(fy=400.0)


@pytest.fixture
def default_steel():
    return SteelMaterial(Fy=275.0)
