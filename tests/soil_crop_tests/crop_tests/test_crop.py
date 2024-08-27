from pytest_mock import MockerFixture
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.field.crop.crop import Crop
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.field.field_data import FieldData
from RUFAS.routines.field.soil.soil_data import SoilData
import pytest


@pytest.mark.parametrize(
    "is_mature, is_dormant, should_update",
    [
        (False, False, True),  # Crop is not mature nor dormant, should update
        (True, False, False),  # Crop is mature, should not update
        (False, True, False),  # Crop is dormant, should not update
    ],
)
def test_perform_daily_crop_update(
    mocker: MockerFixture, is_mature: bool, is_dormant: bool, should_update: bool
) -> None:
    crop_data = CropData()
    crop = Crop(crop_data)
    mocker.patch.object(CropData, 'is_dormant', new_callable=mocker.PropertyMock, return_value=is_dormant)
    mocker.patch.object(CropData, 'is_mature', new_callable=mocker.PropertyMock, return_value=is_mature)

    # Mock the methods that should be called during the update
    mocker.patch.object(crop._heat_units, "absorb_heat_units")
    mocker.patch.object(crop._root_development, "develop_roots")
    mocker.patch.object(crop._nitrogen_incorporation, "incorporate_nitrogen")
    mocker.patch.object(crop._phosphorus_incorporation, "incorporate_phosphorus")
    mocker.patch.object(crop._growth_constraints, "constrain_growth")
    mocker.patch.object(crop._leaf_area_index, "grow_canopy")
    mocker.patch.object(crop._biomass_allocation, "allocate_biomass")

    # Create mock objects for the conditions, field data, and soil data
    mock_conditions = mocker.Mock(spec=CurrentDayConditions)
    mock_field_data = mocker.Mock(spec=FieldData)
    mock_soil_data = mocker.Mock(spec=SoilData)

    # Call the method
    crop.perform_daily_crop_update(mock_conditions, mock_field_data, mock_soil_data)

    # Assertions
    if should_update:
        crop._heat_units.absorb_heat_units.assert_called_once_with(
            mock_conditions.mean_air_temperature,
            mock_conditions.min_air_temperature,
            mock_conditions.max_air_temperature,
        )
        crop._root_development.develop_roots.assert_called_once()
        crop._nitrogen_incorporation.incorporate_nitrogen.assert_called_once_with(mock_soil_data)
        crop._phosphorus_incorporation.incorporate_phosphorus.assert_called_once_with(mock_soil_data)
        crop._growth_constraints.constrain_growth.assert_called_once_with(
            crop._data.max_transpiration,
            mock_conditions.mean_air_temperature,
            mock_field_data.simulate_water_stress,
            mock_field_data.simulate_temp_stress,
            mock_field_data.simulate_nitrogen_stress,
            mock_field_data.simulate_phosphorus_stress,
        )
        crop._leaf_area_index.grow_canopy.assert_called_once()
        crop._biomass_allocation.allocate_biomass.assert_called_once_with(mock_conditions.incoming_light)
    else:
        crop._heat_units.absorb_heat_units.assert_not_called()
        crop._root_development.develop_roots.assert_not_called()
        crop._nitrogen_incorporation.incorporate_nitrogen.assert_not_called()
        crop._phosphorus_incorporation.incorporate_phosphorus.assert_not_called()
        crop._growth_constraints.constrain_growth.assert_not_called()
        crop._leaf_area_index.grow_canopy.assert_not_called()
        crop._biomass_allocation.allocate_biomass.assert_not_called()


@pytest.mark.parametrize(
    "in_growing_season, should_update",
    [
        (True, True),  # Crop is in growing season, should update
        (False, False),  # Crop is not in growing season, should not update
    ],
)
def test_cycle_water_for_crops(
    mocker: MockerFixture, in_growing_season: bool, should_update: bool
) -> None:
    crop_data = CropData()
    mocker.patch.object(CropData, 'in_growing_season', new_callable=mocker.PropertyMock,
                        return_value=in_growing_season)
    crop = Crop(crop_data)

    mocker.patch.object(crop._water_uptake, "uptake_water")
    mocker.patch.object(crop._water_dynamics, "cycle_water")
    mock_soil_data = mocker.Mock(spec=SoilData)

    if should_update:
        crop._data.water_uptake = 5.0

    crop.cycle_water_for_crops(10.0, 20.0, mock_soil_data)

    # Assertions
    if should_update:
        crop._water_uptake.uptake_water.assert_called_once_with(mock_soil_data)
        crop._water_dynamics.cycle_water.assert_called_once_with(
            10.0, 5.0, 20.0
        )
    else:
        crop._water_uptake.uptake_water.assert_not_called()
        crop._water_dynamics.cycle_water.assert_not_called()
        assert crop._data.cumulative_evaporation == 0.0
        assert crop._data.cumulative_transpiration == 0.0
        assert crop._data.cumulative_potential_evapotranspiration == 0.0
        assert crop._data.cumulative_water_uptake == 0.0


@pytest.mark.parametrize(
    "water_canopy_storage_capacity, initial_canopy_water, precipitation_reaching_soil,"
    "expected_precipitation_reaching_soil, expected_excess_canopy_water",
    [
        (10.0, 5.0, 8.0, 3.0, 0.0),   # Partial canopy storage, no excess water
        (10.0, 10.0, 5.0, 5.0, 0.0),  # Full canopy storage, no excess water
        # (10.0, 15.0, 10.0, 10.0, 5.0),  # Canopy overfilled, excess water
    ],
)
def test_handle_water_in_canopy(
    mocker: MockerFixture,
    water_canopy_storage_capacity: float,
    initial_canopy_water: float,
    precipitation_reaching_soil: float,
    expected_precipitation_reaching_soil: float,
    expected_excess_canopy_water: float,
) -> None:
    crop_data = CropData()
    crop = Crop(crop_data)

    mocker.patch.object(CropData, 'water_canopy_storage_capacity', new_callable=mocker.PropertyMock,
                        return_value=water_canopy_storage_capacity)

    canopy_water_mock = mocker.PropertyMock()
    mocker.patch.object(CropData, 'canopy_water', canopy_water_mock)

    canopy_water_mock.return_value = initial_canopy_water

    actual_precipitation_reaching_soil, actual_excess_canopy_water = \
        crop.handle_water_in_canopy(precipitation_reaching_soil)

    assert actual_precipitation_reaching_soil == expected_precipitation_reaching_soil
    assert actual_excess_canopy_water == expected_excess_canopy_water

    expected_canopy_water = min(water_canopy_storage_capacity, initial_canopy_water
                                + min(precipitation_reaching_soil, water_canopy_storage_capacity
                                      - initial_canopy_water))
    if water_canopy_storage_capacity > initial_canopy_water:
        canopy_water_mock.assert_called_with(expected_canopy_water)
    else:
        canopy_water_mock.assert_called_with(water_canopy_storage_capacity)
