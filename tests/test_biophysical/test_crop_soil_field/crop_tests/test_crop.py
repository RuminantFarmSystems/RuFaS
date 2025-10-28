from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.biophysical.field.crop.crop import Crop
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.crop_data_factory import CropDataFactory
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.rufas_time import RufasTime

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


def test_data_property() -> None:
    """Test for Crop data property."""
    mock_crop_data = Mock(spec=CropData)
    crop = Crop(mock_crop_data)

    result = crop.data
    assert result == mock_crop_data


@pytest.mark.parametrize(
    "is_mature, is_dormant, should_update",
    [
        (False, False, True),  # Crop is not mature nor dormant, should update
        (True, False, False),  # Crop is mature, should not update
        (False, True, False),  # Crop is dormant, should not update
    ],
)
def test_perform_daily_crop_update(
    mocker: MockerFixture, mock_crop_data: CropData, is_mature: bool, is_dormant: bool, should_update: bool
) -> None:
    """Test perform_daily_crop_update() method in crop.py."""
    crop = Crop(mock_crop_data)
    mocker.patch.object(CropData, "is_dormant", new_callable=mocker.PropertyMock, return_value=is_dormant)
    mocker.patch.object(CropData, "is_mature", new_callable=mocker.PropertyMock, return_value=is_mature)

    # Mock the methods that should be called during the update
    mock_absorb_heat_units = mocker.patch.object(crop._heat_units, "absorb_heat_units")
    mock_develop_roots = mocker.patch.object(crop._root_development, "develop_roots")
    mock_incorporate_nitrogen = mocker.patch.object(crop._nitrogen_uptake, "uptake")
    mock_incorporate_phosphorus = mocker.patch.object(crop._phosphorus_uptake, "uptake")
    mock_constrain_growth = mocker.patch.object(crop._growth_constraints, "constrain_growth")
    mock_grow_canopy = mocker.patch.object(crop._leaf_area_index, "grow_canopy")
    mock_allocate_biomass = mocker.patch.object(crop._biomass_allocation, "allocate_biomass")

    # Create mock objects for the conditions, field data, and soil data
    mock_conditions = mocker.Mock(
        spec=CurrentDayConditions(
            min_air_temperature=-1, max_air_temperature=1, mean_air_temperature=2, incoming_light=12
        )
    )
    mock_field_data = mocker.Mock(spec=FieldData)
    mock_soil_data = mocker.Mock(spec=SoilData)
    mock_time = mocker.Mock(spec=RufasTime)

    # Call the method
    crop.perform_daily_crop_update(mock_conditions, mock_field_data, mock_soil_data, mock_time)

    # Assertions
    if should_update:
        mock_absorb_heat_units.assert_called_once_with(
            mock_conditions.mean_air_temperature,
            mock_conditions.min_air_temperature,
            mock_conditions.max_air_temperature,
        )
        mock_develop_roots.assert_called_once()
        mock_incorporate_nitrogen.assert_called_once_with(mock_soil_data)
        mock_incorporate_phosphorus.assert_called_once_with(mock_soil_data)
        mock_constrain_growth.assert_called_once_with(
            crop._data.max_transpiration,
            mock_conditions.mean_air_temperature,
            mock_field_data.simulate_water_stress,
            mock_field_data.simulate_temp_stress,
            mock_field_data.simulate_nitrogen_stress,
            mock_field_data.simulate_phosphorus_stress,
        )
        mock_grow_canopy.assert_called_once()
        mock_allocate_biomass.assert_called_once_with(mock_conditions.incoming_light)
    else:
        mock_absorb_heat_units.assert_not_called()
        mock_develop_roots.assert_not_called()
        mock_incorporate_nitrogen.assert_not_called()
        mock_incorporate_phosphorus.assert_not_called()
        mock_constrain_growth.assert_not_called()
        mock_grow_canopy.assert_not_called()
        mock_allocate_biomass.assert_not_called()


@pytest.mark.parametrize(
    "in_growing_season, should_update",
    [
        (True, True),  # Crop is in growing season, should update
        (False, False),  # Crop is not in growing season, should not update
    ],
)
def test_cycle_water_for_crops(
    mocker: MockerFixture, mock_crop_data: CropData, in_growing_season: bool, should_update: bool
) -> None:
    """Test cycle_water_for_crops() method in crop.py."""
    mocker.patch.object(CropData, "in_growing_season", new_callable=mocker.PropertyMock, return_value=in_growing_season)
    crop = Crop(mock_crop_data)

    mock_uptake_water = mocker.patch.object(crop._water_uptake, "uptake")
    mock_cycle_water = mocker.patch.object(crop._water_dynamics, "cycle_water")
    mock_soil_data = mocker.Mock(spec=SoilData)

    if should_update:
        crop._data.water_uptake = 5.0

    crop.cycle_water_for_crop(10.0, 20.0, mock_soil_data)

    # Assertions
    if should_update:
        mock_uptake_water.assert_called_once_with(mock_soil_data)
        mock_cycle_water.assert_called_once_with(10.0, 5.0, 20.0)
    else:
        mock_uptake_water.assert_not_called()
        mock_cycle_water.assert_not_called()
        assert crop._data.cumulative_evaporation == 0.0
        assert crop._data.cumulative_transpiration == 0.0
        assert crop._data.cumulative_potential_evapotranspiration == 0.0
        assert crop._data.cumulative_water_uptake == 0.0


@pytest.mark.parametrize(
    "water_canopy_storage_capacity, initial_canopy_water, precipitation_reaching_soil,"
    "expected_precipitation_reaching_soil",
    [
        (10.0, 5.0, 8.0, 3.0),  # Partial canopy storage, no excess water
        (10.0, 10.0, 5.0, 5.0),  # Full canopy storage, no excess water
        (10.0, 15.0, 10.0, 10.0),  # Canopy overfilled, excess water
    ],
)
def test_handle_water_in_canopy(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    water_canopy_storage_capacity: float,
    initial_canopy_water: float,
    precipitation_reaching_soil: float,
    expected_precipitation_reaching_soil: float,
) -> None:
    """Test handle_water_in_canopy() method in crop.py."""
    crop = Crop(mock_crop_data)

    mocker.patch.object(
        CropData,
        "water_canopy_storage_capacity",
        new_callable=mocker.PropertyMock,
        return_value=water_canopy_storage_capacity,
    )

    canopy_water_mock = mocker.PropertyMock()
    mocker.patch.object(CropData, "canopy_water", canopy_water_mock)

    canopy_water_mock.return_value = initial_canopy_water

    actual_precipitation_reaching_soil = crop.handle_water_in_canopy(precipitation_reaching_soil)

    assert actual_precipitation_reaching_soil == expected_precipitation_reaching_soil

    expected_canopy_water = min(
        water_canopy_storage_capacity,
        initial_canopy_water + min(precipitation_reaching_soil, water_canopy_storage_capacity - initial_canopy_water),
    )
    if water_canopy_storage_capacity > initial_canopy_water:
        canopy_water_mock.assert_called_with(expected_canopy_water)
    else:
        canopy_water_mock.assert_called_with(initial_canopy_water)


def test_evaporate_from_canopy(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Test evaporate_from_canopy() method in crop.py."""
    crop = Crop(mock_crop_data)

    evapotranspirative_demand = 5.0
    expected_evaporation = 3.5

    water_dynamics_mock = mocker.patch.object(
        crop._water_dynamics, "evaporate_from_canopy", return_value=expected_evaporation
    )

    actual_evaporation = crop.evaporate_from_canopy(evapotranspirative_demand)

    water_dynamics_mock.assert_called_once_with(evapotranspirative_demand)
    assert actual_evaporation == expected_evaporation


@pytest.mark.parametrize(
    "use_heat_scheduling, heat_fraction, harvest_heat_fraction, expected_result",
    [
        (True, 0.9, 0.85, True),  # Heat scheduling is used, and heat fraction exceeds the threshold
        (True, 0.8, 0.85, False),  # Heat scheduling is used, but heat fraction does not exceed the threshold
        (False, 0.9, 0.85, False),  # Heat scheduling is not used, regardless of heat fraction
    ],
)
def test_should_harvest_based_on_heat(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    use_heat_scheduling: bool,
    heat_fraction: float,
    harvest_heat_fraction: float,
    expected_result: bool,
) -> None:
    """Test should_harvest_based_on_heat() method in crop.py."""
    crop = Crop(mock_crop_data)

    mocker.patch.object(
        CropData, "use_heat_scheduling", new_callable=mocker.PropertyMock, return_value=use_heat_scheduling
    )
    mocker.patch.object(CropData, "heat_fraction", new_callable=mocker.PropertyMock, return_value=heat_fraction)
    mocker.patch.object(
        CropData, "harvest_heat_fraction", new_callable=mocker.PropertyMock, return_value=harvest_heat_fraction
    )

    result = crop.should_harvest_based_on_heat()

    assert result == expected_result


def test_manage_crop_harvest(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Test for manage_crop_harvest() method in crop.py."""
    crop = Crop(mock_crop_data)

    mock_harvest_op = mocker.Mock(spec=HarvestOperation)
    field_name = "Test Field"
    field_size = 10.0  # hectares
    mock_time = mocker.Mock(spec=RufasTime)
    mock_soil_data = mocker.Mock(spec=SoilData)
    mock_crop_harvest = mocker.Mock(spec=HarvestedCrop)
    manage_harvest_mock = mocker.patch.object(crop._crop_management, "manage_harvest", return_value=mock_crop_harvest)

    actual = crop.manage_crop_harvest(mock_harvest_op, field_name, field_size, mock_time, mock_soil_data)

    manage_harvest_mock.assert_called_once_with(mock_harvest_op, field_name, field_size, mock_time, mock_soil_data)
    assert actual == mock_crop_harvest


def test_set_maximum_transpiration(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Test for set_maximum_transpiration method in crop.py."""
    crop = Crop(mock_crop_data)

    evapotranspirative_demand = 7.5
    set_max_transpiration_mock = mocker.patch.object(crop._water_dynamics, "set_maximum_transpiration")

    crop.set_maximum_transpiration(evapotranspirative_demand)

    set_max_transpiration_mock.assert_called_once_with(evapotranspirative_demand)


@pytest.mark.parametrize(
    "daylength, dormancy_threshold_daylength, rainfall, should_enter_dormancy",
    [
        (10.0, 12.0, 5.0, True),  # Daylength is below the threshold, should enter dormancy
        (12.0, 12.0, 5.0, True),  # Daylength is exactly at the threshold, should enter dormancy
        (13.0, 12.0, 5.0, False),  # Daylength is above the threshold, should exit dormancy
    ],
)
def test_assess_dormancy(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    daylength: float,
    dormancy_threshold_daylength: float,
    rainfall: float,
    should_enter_dormancy: bool,
) -> None:
    """Test assess_dormancy() method in crop.py."""
    crop = Crop(mock_crop_data)

    enter_dormancy_mock = mocker.patch.object(crop, "enter_dormancy")
    exit_dormancy_mock = mocker.patch.object(crop, "exit_dormancy")

    mock_soil = mocker.Mock(spec=Soil)
    mock_soil_data = mocker.Mock(spec=SoilData)

    crop.assess_dormancy(daylength, dormancy_threshold_daylength, rainfall, mock_soil_data, mock_soil)

    if should_enter_dormancy:
        enter_dormancy_mock.assert_called_once_with(rainfall, mock_soil_data, mock_soil)
        exit_dormancy_mock.assert_not_called()
    else:
        enter_dormancy_mock.assert_not_called()
        exit_dormancy_mock.assert_called_once()


def test_enter_dormancy(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Test enter_dormancy() method in crop.py."""
    crop = Crop(mock_crop_data)

    dormancy_mock = mocker.patch.object(crop._dormancy, "enter_dormancy")
    biomass_allocation_mock = mocker.patch.object(crop._biomass_allocation, "partition_biomass")

    mock_soil = mocker.Mock(spec=Soil)
    mock_soil_data = mocker.Mock(spec=SoilData)
    mock_carbon_cycling = mocker.Mock()
    mock_residue_partition = mocker.Mock()
    mock_soil.carbon_cycling = mock_carbon_cycling
    mock_carbon_cycling.residue_partition = mock_residue_partition

    rainfall = 12.5

    crop.enter_dormancy(rainfall, mock_soil_data, mock_soil)

    dormancy_mock.assert_called_once_with(mock_soil_data)
    biomass_allocation_mock.assert_called_once()
    mock_residue_partition.add_residue_to_pools.assert_called_once_with(rainfall)


def test_exit_dormancy(mock_crop_data: CropData) -> None:
    """Test exit_dormancy() method in crop.py."""
    mock_crop_data.is_dormant = True
    crop = Crop(mock_crop_data)

    crop.exit_dormancy()
    assert crop._data.is_dormant is False


@pytest.mark.parametrize(
    "crop_reference,heat_scheduled",
    [
        ("corn_silage", False),
        ("custom_alfalfa", False),
        ("alien_crop", True),
        ("unknown_crop", False),
    ],
)
def test_create_crop(
    mocker: MockerFixture,
    mock_crop_data: CropData,
    crop_reference: str,
    heat_scheduled: bool,
) -> None:
    """Tests that a new Crop instance is properly created or raises KeyError if crop_reference is invalid."""
    mocked_time = MagicMock(RufasTime)
    mock_create_crop_data = mocker.patch.object(CropDataFactory, "create_crop_data", return_value=mock_crop_data)

    crop = Crop.create_crop(crop_reference, heat_scheduled, mocked_time)

    mock_create_crop_data.assert_called_once_with(crop_reference)

    assert crop._data.id == crop_reference
    assert crop._data.use_heat_scheduling == heat_scheduled


def test_set_crop_planting_attributes(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Test for set_crop_planting_attributes() in crop.py."""
    crop = Crop(mock_crop_data)

    mock_time = mocker.Mock(spec=RufasTime)
    mock_time.current_calendar_year = 2024
    mock_time.current_julian_day = 150

    crop_reference = "winter_wheat_grain"
    use_heat_scheduled_harvesting = True
    crop.set_crop_planting_attributes(crop_reference, use_heat_scheduled_harvesting, mock_time)

    assert crop._data.use_heat_scheduling == use_heat_scheduled_harvesting
    assert crop._data.id == crop_reference
    assert crop._data.planting_year == 2024
    assert crop._data.planting_day == 150


def test_update_crop_max_root_depth(mock_crop_data: CropData) -> None:
    """Tests update_crop_max_root_depth()."""
    crop = Crop(mock_crop_data)
    assert crop.data.max_root_depth == 3000
