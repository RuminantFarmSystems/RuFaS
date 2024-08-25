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
