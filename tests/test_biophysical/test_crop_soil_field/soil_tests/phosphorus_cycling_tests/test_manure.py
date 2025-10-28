from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.manure_pool import ManurePool
from RUFAS.biophysical.field.soil.phosphorus_cycling.manure import Manure
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "rain,runoff,area,mean_temp",
    [
        (12, 1.8, 2.1, 14),
        (14, 12.2, 3.4, 9),
        (0, 0, 2.4, 28),
    ],
)
def test_daily_manure_update(rain: float, runoff: float, area: float, mean_temp: float, mocker: MockerFixture) -> None:
    """Tests that the main manure update method correctly calls all subroutines."""
    data1 = SoilData(field_size=area)
    incorp = Manure(data1)
    mock_machine_reset = mocker.patch.object(data1.machine_manure, "runoff_reset")
    mock_graze_reset = mocker.patch.object(data1.grazing_manure, "runoff_reset")
    mock_leach = mocker.patch.object(incorp, "_leach_and_update_phosphorus_pools")
    mock_machine_update = mocker.patch.object(data1.machine_manure, "daily_manure_update", return_value=152)
    mock_grazing_update = mocker.patch.object(data1.grazing_manure, "daily_manure_update", return_value=152)
    mock_add = mocker.patch.object(incorp, "_add_infiltrated_phosphorus_to_soil")
    incorp.daily_manure_update(rain, runoff, area, mean_temp)
    mock_machine_reset.assert_called_once()
    mock_graze_reset.assert_called_once()

    if rain > 0:
        mock_leach.assert_called_once_with(rain, runoff, area)

    mock_machine_update.assert_called_once()
    mock_grazing_update.assert_called_once()
    mock_add.assert_called_once_with(304, area)


@pytest.mark.parametrize(
    "rain,runoff,area",
    [
        (13, 4, 1.8),
        (12, 1.8, 2.1),
        (14, 12.2, 3.4),
        (4.2, 0, 2.4),
    ],
)
def test_leach_and_update_phosphorus_pools(rain: float, runoff: float, area: float, mocker: MockerFixture) -> None:
    """Tests that the update subroutine for phosphorus pools in Manure correctly calls methods and sets attributes."""
    data = SoilData(
        machine_manure=ManurePool(
            manure_dry_mass=1000,
            manure_field_coverage=0.86,
            water_extractable_inorganic_phosphorus=200,
            water_extractable_organic_phosphorus=90,
        ),
        grazing_manure=ManurePool(
            manure_dry_mass=800,
            manure_field_coverage=0.78,
            water_extractable_inorganic_phosphorus=125,
            water_extractable_organic_phosphorus=70,
        ),
        field_size=area,
    )
    incorp = Manure(data)
    mock_grazing_leach_phosphorus_pools = mocker.patch.object(
        data.grazing_manure, "leach_phosphorus_pools", return_value=(9, 24)
    )
    mock_machine_leach_phosphorus_pools = mocker.patch.object(
        data.machine_manure, "leach_phosphorus_pools", return_value=(9, 24)
    )
    mock_detemine_phosphorus_operation = mocker.patch.object(
        ManurePool, "determine_phosphorus_leach", return_value=(9, 24)
    )
    mock_add = mocker.patch.object(incorp, "_add_infiltrated_phosphorus_to_soil")

    incorp._leach_and_update_phosphorus_pools(rain, runoff, area)
    assert mock_detemine_phosphorus_operation.call_count == 2
    mock_grazing_leach_phosphorus_pools.assert_called_once_with(rain, runoff, area)
    mock_machine_leach_phosphorus_pools.assert_called_once_with(rain, runoff, area)
    add_calls = [
        call(9, area),
        call(24, area),
        call(9, area),
        call(24, area),
    ]
    mock_add.assert_has_calls(add_calls)


@pytest.mark.parametrize(
    "amount_phosphorus,field_size",
    [
        (100, 3.1),
        (25.6, 2),
        (66.23, 1.88),
    ],
)
def test_add_infiltrated_phosphorus_to_soil(amount_phosphorus: float, field_size: float, mocker: MockerFixture) -> None:
    """Test that methods are called correctly on correct layers of soil profile."""
    data = SoilData(field_size=field_size)
    incorp = Manure(data)
    mock_add = mocker.patch.object(LayerData, "add_to_labile_phosphorus")
    incorp._add_infiltrated_phosphorus_to_soil(amount_phosphorus, field_size)
    add_calls = [call(0.8 * amount_phosphorus, field_size), call(0.2 * amount_phosphorus, field_size)]
    mock_add.assert_has_calls(add_calls)
