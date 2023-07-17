from unittest.mock import MagicMock

import pytest

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_cycling import PhosphorusCycling
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure import Manure
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.fertilizer import Fertilizer
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_mineralization import PhosphorusMineralization
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.soluble_phosphorus import SolublePhosphorus


@pytest.mark.parametrize("rainfall,runoff,field_size,mean_air_temperature", [
    (1, 2, 3, 4),
    (1.3, 0.2, 9.24, 7.7)
])
def test_phosphorus_cycling(rainfall: float, runoff: float, field_size: float, mean_air_temperature: float) -> None:
    """Tests that the main routine were executed correctly"""
    Manure.daily_manure_update = MagicMock()
    Fertilizer.do_fertilizer_phosphorus_operations = MagicMock()
    PhosphorusMineralization.mineralize_phosphorus = MagicMock()
    SolublePhosphorus.daily_update_routine = MagicMock()
    cycle = PhosphorusCycling(field_size=field_size)

    cycle.cycle_phosphorus(rainfall, runoff, field_size, mean_air_temperature)

    Manure.daily_manure_update.assert_called_once_with(rainfall, runoff, field_size, mean_air_temperature)
    Fertilizer.do_fertilizer_phosphorus_operations.assert_called_once_with(rainfall, runoff, field_size)
    PhosphorusMineralization.mineralize_phosphorus.assert_called_once_with(field_size)
    SolublePhosphorus.daily_update_routine.assert_called_once_with(runoff, field_size)
