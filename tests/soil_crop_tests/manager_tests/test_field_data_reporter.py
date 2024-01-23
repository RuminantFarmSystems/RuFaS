import pytest
from typing import List

from RUFAS.routines.field.field.field import Field
from RUFAS.routines.field.field.field_data import FieldData
from RUFAS.routines.field.manager.field_data_reporter import FieldDataReporter
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.crop import Crop
from RUFAS.routines.field.manager.field_data_reporter import om
from RUFAS.routines.manure.manure_manager import ManureManager
from unittest.mock import patch, PropertyMock, MagicMock


@pytest.mark.parametrize(
    "runoff_values, current_residues, percolated_waters, root_depths",
    [([1.3, 2.4, 1.22], [1.3, 4.2, 6.94], [11.4, 20.6, 29.8, 50], [18.7, 20.5])],
)
def test_send_daily_variables(
    runoff_values: List[float],
    current_residues: List[float],
    percolated_waters: List[float],
    root_depths: List[float],
) -> None:
    """Tests that daily variables were sent correctly through OutputManager"""
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = CropData(name="crop 1", planting_day=100, planting_year=1993)
    crop_data_2 = CropData(name="crop 2", planting_day=215, planting_year=1993)
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)

    field_1 = Field(field_data=field_data_1, manure_manager=MagicMock(ManureManager))
    field_2 = Field(field_data=field_data_2, manure_manager=MagicMock(ManureManager))
    field_1.crops.append(crop_1)
    field_1.crops.append(crop_2)
    field_2.crops.append(crop_1)
    field_2.crops.append(crop_2)

    og = FieldDataReporter([field_1, field_2])
    for i in range(3):
        field_1.soil.data.accumulated_runoff = runoff_values[i]
        field_2.soil.data.accumulated_runoff = runoff_values[i]
        field_1.field_data.current_residue = current_residues[i]
        field_2.field_data.current_residue = current_residues[i]
        for index, layer in enumerate(field_1.soil.data.soil_layers):
            layer.percolated_water = percolated_waters[index]
        for index, layer in enumerate(field_2.soil.data.soil_layers):
            layer.percolated_water = percolated_waters[index]
        for index, crop in enumerate(field_1.crops):
            crop.data.root_depth = root_depths[index]
        for index, crop in enumerate(field_2.crops):
            crop.data.root_depth = root_depths[index]
        og.send_daily_variables()
    pool = om.variables_pool

    # Testing layer variables
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.current_residue.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.current_residue.field='name 1'"
    ]["values"] == [1.3, 4.2, 6.94]
    assert (
        "FieldDataReporter.send_daily_variables.current_residue.field='name 2'"
        in pool.keys()
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.current_residue.field='name 2'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.current_residue.field='name 2'"
    ]["values"] == [1.3, 4.2, 6.94]

    # Testing soil variables
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.accumulated_runoff.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.accumulated_runoff.field='name 1'"
    ]["values"] == [1.3, 2.4, 1.22]

    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.accumulated_runoff.field='name 2'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.accumulated_runoff.field='name 2'"
    ]["values"] == [1.3, 2.4, 1.22]

    # Testing vadose data
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.active_organic_nitrogen_content.field='name 1',vadose_zone_layer"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.active_organic_nitrogen_content.field='name 1',vadose_zone_layer"
    ]["values"] == [0, 0, 0]

    # Testing layer data
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='0'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='1'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='2'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='3'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='0'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='1'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='2'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='3'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='0'"
    ]["values"] == [11.4, 11.4, 11.4]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='1'"
    ]["values"] == [20.6, 20.6, 20.6]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='2'"
    ]["values"] == [29.8, 29.8, 29.8]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 1',layer='3'"
    ]["values"] == [50, 50, 50]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='0'"
    ]["values"] == [11.4, 11.4, 11.4]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='1'"
    ]["values"] == [20.6, 20.6, 20.6]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='2'"
    ]["values"] == [29.8, 29.8, 29.8]
    assert pool[
        "FieldDataReporter.send_daily_variables.percolated_water.field='name 2',layer='3'"
    ]["values"] == [50, 50, 50]

    # Testing crop data
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.root_depth.field='name 1',crop='crop 1',planted=100,1993"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.root_depth.field='name 1',crop='crop 2',planted=215,1993"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.root_depth.field='name 2',crop='crop 1',planted=100,1993"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_daily_variables.root_depth.field='name 2',crop='crop 2',planted=215,1993"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_daily_variables.root_depth.field='name 1',crop='crop 1',planted=100,1993"
    ]["values"] == [18.7, 18.7, 18.7]
    assert pool[
        "FieldDataReporter.send_daily_variables.root_depth.field='name 1',crop='crop 2',planted=215,1993"
    ]["values"] == [20.5, 20.5, 20.5]
    assert pool[
        "FieldDataReporter.send_daily_variables.root_depth.field='name 2',crop='crop 1',planted=100,1993"
    ]["values"] == [18.7, 18.7, 18.7]
    assert pool[
        "FieldDataReporter.send_daily_variables.root_depth.field='name 2',crop='crop 2',planted=215,1993"
    ]["values"] == [20.5, 20.5, 20.5]


@pytest.mark.parametrize(
    "annual_irrigation_water_use_total, annual_soil_evaporation_total,"
    "annual_nitrous_oxide_emissions_total, initial_water_content,"
    "initial_nitrates_total",
    [
        (
            [1.3, 2.4, 1.22],
            [1.5, 2.4, 3.8],
            [1.2, 7.7, 9.24, 1.31],
            [2, 3, 4],
            [4.2, 5.3, 6.5],
        )
    ],
)
def test_send_annual_variables(
    annual_irrigation_water_use_total: List[float],
    annual_soil_evaporation_total: List[float],
    annual_nitrous_oxide_emissions_total: List[float],
    initial_water_content: List[float],
    initial_nitrates_total: List[float],
) -> None:
    """Tests that annual variables were sent correctly through OutputManager"""
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = CropData(name="crop 1")
    crop_data_2 = CropData(name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)

    field_1 = Field(field_data_1, manure_manager=MagicMock(ManureManager))
    field_2 = Field(field_data_2, manure_manager=MagicMock(ManureManager))
    field_1.crops.append(crop_1)
    field_1.crops.append(crop_2)
    field_2.crops.append(crop_1)
    field_2.crops.append(crop_2)

    og = FieldDataReporter([field_1, field_2])
    for i in range(3):
        with patch.multiple(
            "RUFAS.routines.field.soil.soil_data.SoilData",
            profile_soil_water_content=PropertyMock(return_value=2),
            profile_nitrates_total=PropertyMock(return_value=8.5),
        ):
            field_1.field_data.annual_irrigation_water_use_total = (
                annual_irrigation_water_use_total[i]
            )
            field_2.field_data.annual_irrigation_water_use_total = (
                annual_irrigation_water_use_total[i]
            )
            field_1.soil.data.annual_soil_evaporation_total = (
                annual_soil_evaporation_total[i]
            )
            field_2.soil.data.annual_soil_evaporation_total = (
                annual_soil_evaporation_total[i]
            )
            field_1.soil.data.initial_water_content = initial_water_content[i]
            field_2.soil.data.initial_water_content = initial_water_content[i]
            field_1.soil.data.initial_nitrates_total = initial_nitrates_total[i]
            field_2.soil.data.initial_nitrates_total = initial_nitrates_total[i]

            for index, layer in enumerate(field_1.soil.data.soil_layers):
                layer.annual_nitrous_oxide_emissions_total = (
                    annual_nitrous_oxide_emissions_total[index]
                )
            for index, layer in enumerate(field_2.soil.data.soil_layers):
                layer.annual_nitrous_oxide_emissions_total = (
                    annual_nitrous_oxide_emissions_total[index]
                )
            og.send_annual_variables()
    print(om.variables_pool)
    pool = om.variables_pool
    # Testing water and nitrates changes
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_water_content_change.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_water_content_change.field='name 1'"
    ]["values"] == [0, -1, -2]
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_water_content_change.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_water_content_change.field='name 1'"
    ]["values"] == [0, -1, -2]

    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrates_content_change.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrates_content_change.field='name 1'"
    ]["values"] == [4.3, 3.2, 2.0]
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrates_content_change.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrates_content_change.field='name 1'"
    ]["values"] == [4.3, 3.2, 2.0]
    # Testing field variables
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_irrigation_water_use_total.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_irrigation_water_use_total.field='name 1'"
    ]["values"] == [1.3, 2.4, 1.22]
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_irrigation_water_use_total.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_irrigation_water_use_total.field='name 1'"
    ]["values"] == [1.3, 2.4, 1.22]

    # Testing soil variables
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_soil_evaporation_total.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_soil_evaporation_total.field='name 1'"
    ]["values"] == [1.5, 2.4, 3.8]

    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_soil_evaporation_total.field='name 1'"
            ]["info_maps"]
        )
        == 3
    )
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_soil_evaporation_total.field='name 1'"
    ]["values"] == [1.5, 2.4, 3.8]

    # Testing layer data
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='0'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='1'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='2'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='3'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='0'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='1'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='2'"
            ]["info_maps"]
        )
        == 3
    )
    assert (
        len(
            pool[
                "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='3'"
            ]["info_maps"]
        )
        == 3
    )

    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='0'"
    ]["values"] == [1.2, 1.2, 1.2]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='1'"
    ]["values"] == [7.7, 7.7, 7.7]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='2'"
    ]["values"] == [9.24, 9.24, 9.24]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 1',layer='3'"
    ]["values"] == [1.31, 1.31, 1.31]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='0'"
    ]["values"] == [1.2, 1.2, 1.2]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='1'"
    ]["values"] == [7.7, 7.7, 7.7]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='2'"
    ]["values"] == [9.24, 9.24, 9.24]
    assert pool[
        "FieldDataReporter.send_annual_variables.annual_nitrous_oxide_emissions_total.field='name 2',layer='3'"
    ]["values"] == [1.31, 1.31, 1.31]
