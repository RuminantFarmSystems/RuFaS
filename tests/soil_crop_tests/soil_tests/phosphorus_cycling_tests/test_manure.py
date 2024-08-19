import pytest
from math import exp, sqrt
from unittest.mock import patch, call, MagicMock, PropertyMock

from RUFAS.routines.field.crop_and_soil_constants import (
    HECTARES_TO_SQUARE_MILLIMETERS,
    CUBIC_MILLIMETERS_TO_LITERS,
    MILLIGRAMS_TO_KILOGRAMS,
)
from RUFAS.routines.field.soil.manure_pool import ManurePool
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.phosphorus_cycling.manure import Manure


@pytest.mark.parametrize(
    "rain,runoff,area,mean_temp",
    [
        (12, 1.8, 2.1, 14),
        (14, 12.2, 3.4, 9),
        (0, 0, 2.4, 28),
    ],
)
def test_daily_manure_update(rain: float, runoff: float, area: float, mean_temp: float) -> None:
    """Tests that the main manure update method correctly calls all subroutines."""

