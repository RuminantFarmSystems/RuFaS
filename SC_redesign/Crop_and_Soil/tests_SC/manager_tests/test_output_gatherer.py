import pytest
from typing import List

from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.manager.output_gatherer import om
from unittest.mock import patch, PropertyMock


@pytest.mark.parametrize("runoff_values, current_residues, percolated_waters, root_depths", [
    ([1.3, 2.4, 1.22], [1.3, 4.2, 6.94], [11.4, 20.6, 29.8, 50], [18.7, 20.5])
])
def test_send_daily_variables(runoff_values: List[float],
                              current_residues: List[float],
                              percolated_waters: List[float],
                              root_depths: List[float]) -> None:
    """Tests that daily variables were sent correctly through OutputManager"""
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = CropData(name="crop 1")
    crop_data_2 = CropData(name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)
    field_1 = Field(field_data=field_data_1)
    field_2 = Field(field_data=field_data_2)
    field_1.add_crop(crop_1)
    field_1.add_crop(crop_2)
    field_2.add_crop(crop_1)
    field_2.add_crop(crop_2)
    og = OutputGatherer([field_1, field_2])
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
    print(om.variables_pool)
    pool = om.variables_pool

    # Testing layer variables
    assert len(pool["field:'name 1'.current_residue"]['info_maps']) == 3
    assert pool["field:'name 1'.current_residue"]['values'] == [1.3, 4.2, 6.94]
    assert "field:'name 2'.current_residue" in pool.keys()
    assert len(pool["field:'name 2'.current_residue"]['info_maps']) == 3
    assert pool["field:'name 2'.current_residue"]['values'] == [1.3, 4.2, 6.94]

    # Testing soil variables
    assert len(pool["field:'name 1'.accumulated_runoff"]['info_maps']) == 3
    assert pool["field:'name 1'.accumulated_runoff"]['values'] == [1.3, 2.4, 1.22]

    assert len(pool["field:'name 2'.accumulated_runoff"]['info_maps']) == 3
    assert pool["field:'name 2'.accumulated_runoff"]['values'] == [1.3, 2.4, 1.22]

    # Testing vadose data
    assert len(pool["field:'name 1_vadose_layer'.active_organic_nitrogen_content"]['info_maps']) == 3
    assert pool["field:'name 1_vadose_layer'.active_organic_nitrogen_content"]['values'] == [0, 0, 0]

    # Testing layer data
    assert len(pool["field:'name 1',layer_index:'0'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 1',layer_index:'1'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 1',layer_index:'2'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 1',layer_index:'3'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'0'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'1'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'2'.percolated_water"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'3'.percolated_water"]['info_maps']) == 3
    assert pool["field:'name 1',layer_index:'0'.percolated_water"]['values'] == [11.4, 11.4, 11.4]
    assert pool["field:'name 1',layer_index:'1'.percolated_water"]['values'] == [20.6, 20.6, 20.6]
    assert pool["field:'name 1',layer_index:'2'.percolated_water"]['values'] == [29.8, 29.8, 29.8]
    assert pool["field:'name 1',layer_index:'3'.percolated_water"]['values'] == [50, 50, 50]
    assert pool["field:'name 2',layer_index:'0'.percolated_water"]['values'] == [11.4, 11.4, 11.4]
    assert pool["field:'name 2',layer_index:'1'.percolated_water"]['values'] == [20.6, 20.6, 20.6]
    assert pool["field:'name 2',layer_index:'2'.percolated_water"]['values'] == [29.8, 29.8, 29.8]
    assert pool["field:'name 2',layer_index:'3'.percolated_water"]['values'] == [50, 50, 50]

    # Testing crop data
    assert len(pool["field:'name 1',crop:'crop 1'.root_depth"]['info_maps']) == 3
    assert len(pool["field:'name 1',crop:'crop 2'.root_depth"]['info_maps']) == 3
    assert len(pool["field:'name 2',crop:'crop 1'.root_depth"]['info_maps']) == 3
    assert len(pool["field:'name 2',crop:'crop 2'.root_depth"]['info_maps']) == 3
    assert pool["field:'name 1',crop:'crop 1'.root_depth"]['values'] == [18.7, 18.7, 18.7]
    assert pool["field:'name 1',crop:'crop 2'.root_depth"]['values'] == [20.5, 20.5, 20.5]
    assert pool["field:'name 2',crop:'crop 1'.root_depth"]['values'] == [18.7, 18.7, 18.7]
    assert pool["field:'name 2',crop:'crop 2'.root_depth"]['values'] == [20.5, 20.5, 20.5]


@pytest.mark.parametrize("annual_irrigation_water_use_total, annual_soil_evaporation_total,"
                         "annual_denitrified_nitrogen_total, initial_water_content,"
                         "initial_nitrates_total", [
                            ([1.3, 2.4, 1.22], [1.5, 2.4, 3.8], [1.2, 7.7, 9.24, 1.31], [2, 3, 4],
                             [4.2, 5.3, 6.5])])
def test_send_annual_variables(annual_irrigation_water_use_total: List[float],
                               annual_soil_evaporation_total: List[float],
                               annual_denitrified_nitrogen_total: List[float],
                               initial_water_content: List[float],
                               initial_nitrates_total: List[float]) -> None:
    """Tests that annual variables were sent correctly through OutputManager"""
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = CropData(name="crop 1")
    crop_data_2 = CropData(name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)
    field_1 = Field(field_data=field_data_1)
    field_2 = Field(field_data=field_data_2)
    field_1.add_crop(crop_1)
    field_1.add_crop(crop_2)
    field_2.add_crop(crop_1)
    field_2.add_crop(crop_2)
    og = OutputGatherer([field_1, field_2])
    for i in range(3):
        with patch.multiple("SC_redesign.Crop_and_Soil.soil.soil_data.SoilData",
                            profile_soil_water_content=PropertyMock(return_value=2),
                            profile_nitrates_total=PropertyMock(return_value=8.5)):
            field_1.field_data.annual_irrigation_water_use_total = annual_irrigation_water_use_total[i]
            field_2.field_data.annual_irrigation_water_use_total = annual_irrigation_water_use_total[i]
            field_1.soil.data.annual_soil_evaporation_total = annual_soil_evaporation_total[i]
            field_2.soil.data.annual_soil_evaporation_total = annual_soil_evaporation_total[i]
            field_1.soil.data.initial_water_content = initial_water_content[i]
            field_2.soil.data.initial_water_content = initial_water_content[i]
            field_1.soil.data.initial_nitrates_total = initial_nitrates_total[i]
            field_2.soil.data.initial_nitrates_total = initial_nitrates_total[i]

            for index, layer in enumerate(field_1.soil.data.soil_layers):
                layer.annual_denitrified_nitrogen_total = annual_denitrified_nitrogen_total[index]
            for index, layer in enumerate(field_2.soil.data.soil_layers):
                layer.annual_denitrified_nitrogen_total = annual_denitrified_nitrogen_total[index]
            og.send_annual_variables()
    print(om.variables_pool)
    pool = om.variables_pool
    # Testing water and nitrates changes
    assert len(pool["field:'name 1'.annual_water_content_change"]['info_maps']) == 3
    assert pool["field:'name 1'.annual_water_content_change"]['values'] == [0, -1, -2]
    assert len(pool["field:'name 2'.annual_water_content_change"]['info_maps']) == 3
    assert pool["field:'name 2'.annual_water_content_change"]['values'] == [0, -1, -2]

    assert len(pool["field:'name 1'.annual_nitrates_content_change"]['info_maps']) == 3
    assert pool["field:'name 1'.annual_nitrates_content_change"]['values'] == [4.3, 3.2, 2.0]
    assert len(pool["field:'name 2'.annual_nitrates_content_change"]['info_maps']) == 3
    assert pool["field:'name 2'.annual_nitrates_content_change"]['values'] == [4.3, 3.2, 2.0]
    # Testing field variables
    assert len(pool["field:'name 1'.annual_irrigation_water_use_total"]['info_maps']) == 3
    assert pool["field:'name 1'.annual_irrigation_water_use_total"]['values'] == [1.3, 2.4, 1.22]
    assert len(pool["field:'name 2'.annual_irrigation_water_use_total"]['info_maps']) == 3
    assert pool["field:'name 2'.annual_irrigation_water_use_total"]['values'] == [1.3, 2.4, 1.22]

    # Testing soil variables
    assert len(pool["field:'name 1'.annual_soil_evaporation_total"]['info_maps']) == 3
    assert pool["field:'name 1'.annual_soil_evaporation_total"]['values'] == [1.5, 2.4, 3.8]

    assert len(pool["field:'name 2'.annual_soil_evaporation_total"]['info_maps']) == 3
    assert pool["field:'name 2'.annual_soil_evaporation_total"]['values'] == [1.5, 2.4, 3.8]

    # Testing layer data
    assert len(pool["field:'name 1',layer_index:'0'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 1',layer_index:'1'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 1',layer_index:'2'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 1',layer_index:'3'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'0'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'1'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'2'.annual_denitrified_nitrogen_total"]['info_maps']) == 3
    assert len(pool["field:'name 2',layer_index:'3'.annual_denitrified_nitrogen_total"]['info_maps']) == 3

    assert pool["field:'name 1',layer_index:'0'.annual_denitrified_nitrogen_total"]['values'] == [1.2, 1.2, 1.2]
    assert pool["field:'name 1',layer_index:'1'.annual_denitrified_nitrogen_total"]['values'] == [7.7, 7.7, 7.7]
    assert pool["field:'name 1',layer_index:'2'.annual_denitrified_nitrogen_total"]['values'] == [9.24, 9.24, 9.24]
    assert pool["field:'name 1',layer_index:'3'.annual_denitrified_nitrogen_total"]['values'] == [1.31, 1.31, 1.31]
    assert pool["field:'name 2',layer_index:'0'.annual_denitrified_nitrogen_total"]['values'] == [1.2, 1.2, 1.2]
    assert pool["field:'name 2',layer_index:'1'.annual_denitrified_nitrogen_total"]['values'] == [7.7, 7.7, 7.7]
    assert pool["field:'name 2',layer_index:'2'.annual_denitrified_nitrogen_total"]['values'] == [9.24, 9.24, 9.24]
    assert pool["field:'name 2',layer_index:'3'.annual_denitrified_nitrogen_total"]['values'] == [1.31, 1.31, 1.31]
