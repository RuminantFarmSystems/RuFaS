from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.field.soil.phosphorus_cycling.fertilizer import Fertilizer
from RUFAS.biophysical.field.soil.phosphorus_cycling.manure import Manure
from RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_cycling import PhosphorusCycling
from RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_mineralization import PhosphorusMineralization
from RUFAS.biophysical.field.soil.phosphorus_cycling.soluble_phosphorus import SolublePhosphorus


@pytest.mark.parametrize(
    "rainfall,runoff,field_size,mean_air_temperature",
    [(1, 2, 3, 4), (1.3, 0.2, 9.24, 7.7)],
)
def test_phosphorus_cycling(rainfall: float, runoff: float, field_size: float, mean_air_temperature: float) -> None:
    """Tests that the main routine were executed correctly"""
    manure = MagicMock(Manure)
    manure.daily_manure_update = MagicMock()
    fert = MagicMock(Fertilizer)
    fert.do_fertilizer_phosphorus_operations = MagicMock()
    mineralization = MagicMock(PhosphorusMineralization)
    mineralization.mineralize_phosphorus = MagicMock()
    soluble_phosphorus = MagicMock(SolublePhosphorus)
    soluble_phosphorus.daily_update_routine = MagicMock()
    cycle = PhosphorusCycling(field_size=field_size)
    cycle.manure = manure
    cycle.fertilizer = fert
    cycle.mineralization = mineralization
    cycle.soluble_phosphorus = soluble_phosphorus

    cycle.cycle_phosphorus(rainfall, runoff, field_size, mean_air_temperature)

    manure.daily_manure_update.assert_called_once_with(rainfall, runoff, field_size, mean_air_temperature)
    fert.do_fertilizer_phosphorus_operations.assert_called_once_with(rainfall, runoff, field_size)
    mineralization.mineralize_phosphorus.assert_called_once_with(field_size)
    soluble_phosphorus.daily_update_routine.assert_called_once_with(runoff, field_size)
