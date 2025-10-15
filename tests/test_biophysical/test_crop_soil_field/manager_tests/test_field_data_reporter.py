from dataclasses import replace
from unittest.mock import PropertyMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.biophysical.field.crop.crop import Crop
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.manager.field_data_reporter import FieldDataReporter
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.biophysical.field.soil.soil_data import SoilData

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.fixture
def output_manager() -> OutputManager:
    """Fixture for om"""
    return OutputManager()


@pytest.fixture
def mock_time(mocker: MockerFixture) -> RufasTime:
    """Fixture for RufasTime"""
    mocker.patch.object(RufasTime, "__init__", return_value=None)
    return RufasTime()


def test_send_crop_daily_variables(
    mocker: MockerFixture, mock_crop_data: CropData, mock_time: RufasTime, output_manager: OutputManager
) -> None:
    """Checks that crop daily variables were sent correctly."""
    field_data_1 = FieldData(name="name 1")
    mock_crop_data.name = "crop 1"
    mock_crop_data.planting_day = 100
    mock_crop_data.planting_year = 1993
    mock_crop_data.root_depth = 1
    mock_crop_data.biomass = 2
    mock_crop_data.biomass_growth_max = 4
    crop = Crop(mock_crop_data)
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=1)

    field_1 = Field(field_data=field_data_1)

    og = FieldDataReporter([field_1])
    mock_add = mocker.patch.object(og.om, "add_variable", side_effect=output_manager.add_variable)

    og.send_crop_daily_variables(crop, "f1", mock_time)

    pool = output_manager.variables_pool

    assert pool["FieldDataReporter.send_crop_daily_variables.root_depth.field='f1',crop='crop 1',planted=100,1993"][
        "values"
    ] == [1]
    assert pool["FieldDataReporter.send_crop_daily_variables.biomass.field='f1',crop='crop 1',planted=100,1993"][
        "values"
    ] == [2]
    assert pool[
        (
            "FieldDataReporter.send_crop_daily_variables.biomass_growth_max.field='f1',crop='crop 1',"
            "planted=100,"
            "1993"
        )
    ]["values"] == [4]

    assert mock_add.call_count == 43


def test_send_soil_layer_daily_variables(
    mocker: MockerFixture, mock_time: RufasTime, output_manager: OutputManager
) -> None:
    """Tests that layer daily variables are sent correctly."""
    mock_add = mocker.patch.object(output_manager, "add_variable", side_effect=output_manager.add_variable)
    field_data_1 = FieldData(name="name 1")
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=1)

    field_1 = Field(field_data=field_data_1)

    og = FieldDataReporter([field_1])
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        plant_metabolic_active_carbon_usage=3,
        evaporated_water_content=4,
        temperature=5,
        percolated_water=6,
    )

    og.send_soil_layer_daily_variables(layer, 1, "name 1", mock_time)

    pool = output_manager.variables_pool

    assert pool["FieldDataReporter.send_soil_layer_daily_variables.temperature.field='name 1',layer='1'"]["values"] == [
        5
    ]
    assert pool["FieldDataReporter.send_soil_layer_daily_variables.evaporated_water_content.field='name 1',layer='1'"][
        "values"
    ] == [4]
    assert pool[
        (
            "FieldDataReporter.send_soil_layer_daily_variables.plant_metabolic_active_carbon_usage.field='name 1',"
            "layer='1'"
        )
    ]["values"] == [3]
    assert pool["FieldDataReporter.send_soil_layer_daily_variables.percolated_water.field='name 1',layer='1'"][
        "values"
    ] == [6]

    assert mock_add.call_count == 60


def test_send_vadose_zone_layer_daily_variables(
    mocker: MockerFixture, mock_time: RufasTime, output_manager: OutputManager
) -> None:
    """Tests that layer daily variables are sent correctly."""
    mocker.patch.object(LayerData, "determine_soil_nutrient_area_density", return_value=1)
    mock_add = mocker.patch.object(output_manager, "add_variable", side_effect=output_manager.add_variable)
    field_data_1 = FieldData(name="name 1")
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        nitrate_content=1,
        fresh_organic_nitrogen_content=2,
        labile_inorganic_phosphorus_content=3,
        active_inorganic_phosphorus_content=4,
    )
    soil_data = SoilData(vadose_zone_layer=layer, field_size=6)
    soil = Soil(soil_data=soil_data)
    field_1 = Field(field_data=field_data_1, soil=soil)
    og = FieldDataReporter([field_1])
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=1)

    og.send_vadose_zone_layer_daily_variables(field_1, mock_time)

    pool = output_manager.variables_pool

    assert mock_add.call_count == 10
    assert pool[
        ("FieldDataReporter.send_vadose_zone_layer_daily_variables.nitrate_content.field='name 1'," "vadose_zone_layer")
    ]["values"] == [1]
    assert pool[
        (
            "FieldDataReporter.send_vadose_zone_layer_daily_variables.fresh_organic_nitrogen_content.field='name "
            "1',vadose_zone_layer"
        )
    ]["values"] == [2]
    assert pool[
        (
            "FieldDataReporter.send_vadose_zone_layer_daily_variables.labile_inorganic_phosphorus_content.field"
            "='name 1',vadose_zone_layer"
        )
    ]["values"] == [1]
    assert pool[
        (
            "FieldDataReporter.send_vadose_zone_layer_daily_variables.active_inorganic_phosphorus_content.field"
            "='name 1',vadose_zone_layer"
        )
    ]["values"] == [1]


def test_send_soil_daily_variables(mocker: MockerFixture, mock_time: RufasTime, output_manager: OutputManager) -> None:
    """Tests that soil daily variables are sent correctly."""
    mocker.patch.object(LayerData, "determine_soil_nutrient_area_density", return_value=1)
    mock_add = mocker.patch.object(output_manager, "add_variable", side_effect=output_manager.add_variable)
    field_data_1 = FieldData(name="name 1")
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        nitrate_content=1,
        fresh_organic_nitrogen_content=2,
        labile_inorganic_phosphorus_content=3,
        active_inorganic_phosphorus_content=4,
    )
    soil_data = SoilData(vadose_zone_layer=layer, field_size=6, water_evaporated=1, water_sublimated=2, cover_type="a")
    soil = Soil(soil_data=soil_data)
    field_1 = Field(field_data=field_data_1, soil=soil)
    og = FieldDataReporter([field_1])
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=1)

    og.send_soil_daily_variables(field_1, mock_time)

    pool = output_manager.variables_pool

    assert mock_add.call_count == 48

    assert pool["FieldDataReporter.send_soil_daily_variables.water_evaporated.field='name 1'"]["values"] == [1]
    assert pool["FieldDataReporter.send_soil_daily_variables.water_sublimated.field='name 1'"]["values"] == [2]
    assert pool["FieldDataReporter.send_soil_daily_variables.cover_type.field='name 1'"]["values"] == ["a"]


def test_send_field_daily_variables(mocker: MockerFixture, mock_time: RufasTime, output_manager: OutputManager) -> None:
    """Tests that field daily variables are sent correctly."""
    mocker.patch.object(LayerData, "determine_soil_nutrient_area_density", return_value=1)
    mock_add = mocker.patch.object(output_manager, "add_variable", side_effect=output_manager.add_variable)
    field_data_1 = FieldData(
        name="name 1",
        transpiration=1,
        current_residue=2,
        max_transpiration=3,
        max_evapotranspiration=4,
        days_into_watering_interval=5,
    )
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        nitrate_content=1,
        fresh_organic_nitrogen_content=2,
        labile_inorganic_phosphorus_content=3,
        active_inorganic_phosphorus_content=4,
    )
    soil_data = SoilData(vadose_zone_layer=layer, field_size=6, water_evaporated=1, water_sublimated=2, cover_type="a")
    soil = Soil(soil_data=soil_data)
    field_1 = Field(field_data=field_data_1, soil=soil)
    og = FieldDataReporter([field_1])
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=1)

    og.send_field_daily_variables(field_1, mock_time)

    pool = output_manager.variables_pool
    assert mock_add.call_count == 5

    assert pool["FieldDataReporter.send_field_daily_variables.current_residue.field='name 1'"]["values"] == [2]
    assert pool["FieldDataReporter.send_field_daily_variables.transpiration.field='name 1'"]["values"] == [1]
    assert pool["FieldDataReporter.send_field_daily_variables.max_transpiration.field='name 1'"]["values"] == [3]
    assert pool["FieldDataReporter.send_field_daily_variables.max_evapotranspiration.field='name 1'"]["values"] == [4]
    assert pool["FieldDataReporter.send_field_daily_variables.days_into_watering_interval.field='name 1'"][
        "values"
    ] == [5]


def test_send_soil_layer_annual_variables(mocker: MockerFixture, output_manager: OutputManager) -> None:
    """Tests that soil layer annual variables are sent correctly."""
    mock_add = mocker.patch.object(output_manager, "add_variable", side_effect=output_manager.add_variable)
    field_data_1 = FieldData(name="name 1")
    field_1 = Field(field_data=field_data_1)

    og = FieldDataReporter([field_1])
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        annual_nitrous_oxide_emissions_total=3,
        annual_ammonia_emissions_total=4,
        annual_decomposition_carbon_CO2_lost=5,
        annual_carbon_CO2_lost=6,
    )

    og.send_soil_layer_annual_variables(layer, "name 1", 1)

    pool = output_manager.variables_pool

    assert mock_add.call_count == 4

    assert pool[
        (
            "FieldDataReporter.send_soil_layer_annual_variables.annual_nitrous_oxide_emissions_total.field='name "
            "1',"
            "layer='1'"
        )
    ]["values"] == [3]
    assert pool[
        (
            "FieldDataReporter.send_soil_layer_annual_variables.annual_ammonia_emissions_total.field='name "
            "1',"
            "layer='1'"
        )
    ]["values"] == [4]
    assert pool[
        (
            "FieldDataReporter.send_soil_layer_annual_variables.annual_decomposition_carbon_CO2_lost.field='name "
            "1',"
            "layer='1'"
        )
    ]["values"] == [5]
    assert pool[
        ("FieldDataReporter.send_soil_layer_annual_variables.annual_carbon_CO2_lost.field='name " "1'," "layer='1'")
    ]["values"] == [6]


def test_send_field_annual_variables(mocker: MockerFixture, output_manager: OutputManager) -> None:
    """Tests that field annual variables are sent correctly."""
    mocker.patch.object(LayerData, "determine_soil_nutrient_area_density", return_value=1)
    field_data_1 = FieldData(name="name 1", annual_irrigation_water_use_total=2)
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        nitrate_content=1,
        fresh_organic_nitrogen_content=2,
        labile_inorganic_phosphorus_content=3,
        active_inorganic_phosphorus_content=4,
    )
    soil_data = SoilData(vadose_zone_layer=layer, field_size=6, water_evaporated=1, water_sublimated=2, cover_type="a")
    soil = Soil(soil_data=soil_data)
    field_1 = Field(field_data=field_data_1, soil=soil)
    og = FieldDataReporter([field_1])
    mock_add = mocker.patch.object(og.om, "add_variable", side_effect=output_manager.add_variable)
    og.send_field_annual_variables(field_1)

    pool = output_manager.variables_pool

    assert mock_add.call_count == 1
    assert pool["FieldDataReporter.send_field_annual_variables.annual_irrigation_water_use_total.field='name 1'"][
        "values"
    ] == [2]


def test_send_soil_annual_variables(mocker: MockerFixture, output_manager: OutputManager) -> None:
    """Tests that soil annual variables are sent correctly."""
    mocker.patch.object(LayerData, "determine_soil_nutrient_area_density", return_value=1)
    mock_add = mocker.patch.object(output_manager, "add_variable", side_effect=output_manager.add_variable)

    mocker.patch.object(SoilData, "profile_soil_water_content", new_callable=PropertyMock, return_value=10)
    mocker.patch.object(SoilData, "profile_nitrates_total", new_callable=PropertyMock, return_value=4)
    field_data_1 = FieldData(name="name 1")
    layer = LayerData(
        field_size=25,
        residue=1,
        top_depth=1,
        bottom_depth=2,
        nitrate_content=1,
        fresh_organic_nitrogen_content=2,
        labile_inorganic_phosphorus_content=3,
        active_inorganic_phosphorus_content=4,
    )
    soil_data = SoilData(
        field_size=25,
        vadose_zone_layer=layer,
        initial_water_content=1,
        initial_nitrates_total=2,
        annual_soil_evaporation_total=3,
        annual_eroded_sediment_total=4,
    )
    soil = Soil(soil_data=soil_data)
    field_1 = Field(field_data=field_data_1, soil=soil)
    og = FieldDataReporter([field_1])

    og.send_soil_annual_variables(field_1)

    pool = output_manager.variables_pool

    assert mock_add.call_count == 18

    assert pool["FieldDataReporter.send_soil_annual_variables.annual_water_content_change.field='name 1'"][
        "values"
    ] == [0]
    assert pool["FieldDataReporter.send_soil_annual_variables.annual_nitrates_content_change.field='name 1'"][
        "values"
    ] == [0]
    assert pool["FieldDataReporter.send_soil_annual_variables.annual_soil_evaporation_total.field='name 1'"][
        "values"
    ] == [3]
    assert pool["FieldDataReporter.send_soil_annual_variables.annual_eroded_sediment_total.field='name 1'"][
        "values"
    ] == [4]


def test_send_daily_variables(mocker: MockerFixture, mock_time: RufasTime, mock_crop_data: CropData) -> None:
    """Tests that daily variables were sent correctly through OutputManager"""
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = replace(mock_crop_data, name="crop 1", planting_day=100, planting_year=1993)
    crop_data_2 = replace(mock_crop_data, name="crop 2", planting_day=215, planting_year=1993)
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)
    field_1 = Field(field_data=field_data_1)
    field_2 = Field(field_data=field_data_2)
    field_1.crops.append(crop_1)
    field_1.crops.append(crop_2)
    field_2.crops.append(crop_1)
    field_2.crops.append(crop_2)

    og = FieldDataReporter([field_1, field_2])

    mock_send_field_daily = mocker.patch.object(og, "send_field_daily_variables")
    mock_send_soil_daily_variables = mocker.patch.object(og, "send_soil_daily_variables")
    mock_send_vadose_zone_layer_daily_variables = mocker.patch.object(og, "send_vadose_zone_layer_daily_variables")
    mock_send_soil_layer_daily_variables = mocker.patch.object(og, "send_soil_layer_daily_variables")
    mock_send_crop_daily_variables = mocker.patch.object(og, "send_crop_daily_variables")

    og.send_daily_variables(mock_time)

    mock_send_field_daily.assert_has_calls([call(field_1, mock_time), call(field_2, mock_time)])
    mock_send_soil_daily_variables.assert_has_calls([call(field_1, mock_time), call(field_2, mock_time)])
    mock_send_vadose_zone_layer_daily_variables.assert_has_calls([call(field_1, mock_time), call(field_2, mock_time)])

    assert mock_send_soil_layer_daily_variables.call_count == 8
    mock_send_crop_daily_variables.assert_has_calls(
        [
            call(crop_1, "name 1", mock_time),
            call(crop_2, "name 1", mock_time),
            call(crop_1, "name 2", mock_time),
            call(crop_2, "name 2", mock_time),
        ]
    )


def test_send_annual_variables(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Tests that annual variables were sent correctly through OutputManager"""
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = replace(mock_crop_data, name="crop 1")
    crop_data_2 = replace(mock_crop_data, name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)

    field_1 = Field(field_data=field_data_1)
    field_2 = Field(field_data=field_data_2)
    field_1.crops.append(crop_1)
    field_1.crops.append(crop_2)
    field_2.crops.append(crop_1)
    field_2.crops.append(crop_2)

    og = FieldDataReporter([field_1, field_2])
    mock_send_field_annual_variables = mocker.patch.object(og, "send_field_annual_variables")
    mock_send_soil_annual_variables = mocker.patch.object(og, "send_soil_annual_variables")
    mock_send_soil_layer_annual_variables = mocker.patch.object(og, "send_soil_layer_annual_variables")

    og.send_annual_variables()

    mock_send_field_annual_variables.assert_has_calls([call(field_1), call(field_2)])
    mock_send_soil_annual_variables.assert_has_calls([call(field_1), call(field_2)])

    assert mock_send_soil_layer_annual_variables.call_count == 8
