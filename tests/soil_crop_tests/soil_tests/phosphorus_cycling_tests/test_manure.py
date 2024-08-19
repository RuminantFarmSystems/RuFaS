import pytest
from pytest_mock import MockerFixture

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
def test_daily_manure_update(rain: float,
                             runoff: float,
                             area: float,
                             mean_temp: float,
                             mocker: MockerFixture) -> None:
    """Tests that the main manure update method correctly calls all subroutines."""
    data1 = SoilData(field_size=area)
    incorp = Manure(data1)
    mock_machine_reset = mocker.patch.object(data1.machine_manure, "runoff_reset")
    mock_graze_reset = mocker.patch.object(data1.grazing_manure, "runoff_reset")
    mock_leach = mocker.patch.object(incorp, "_leach_and_update_phosphorus_pools")
    mock_machine_update = mocker.patch.object(data1.machine_manure, "daily_manure_update",
                                              return_value=152)
    mock_grazing_update = mocker.patch.object(data1.grazing_manure, "daily_manure_update",
                                              return_value=152)
    mock_add = mocker.patch.object(incorp, "_add_infiltrated_phosphorus_to_soil")
    incorp.daily_manure_update(rain, runoff, area, mean_temp)
    mock_machine_reset.assert_called_once()
    mock_graze_reset.assert_called_once()

    if rain > 0:
        mock_leach.assert_called_once_with(rain, runoff, area)

    mock_machine_update.assert_called_once()
    mock_grazing_update.assert_called_once()
    mock_add.assert_called_once_with(304, area)



