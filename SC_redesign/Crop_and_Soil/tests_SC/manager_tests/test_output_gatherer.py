import pytest
from typing import List

from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.manager.output_gatherer import om


@pytest.mark.parametrize("runoff_values, current_residues, percolated_waters, root_depths", [
    ([1.3, 2.4, 1.22], [1.3, 4.2, 6.94], [11.4, 20.6, 29.8, 50], [18.7, 20.5])
])
def test_send_daily_variables(runoff_values: List[float],
                              current_residues: List[float],
                              percolated_waters: List[float],
                              root_depths: List[float]) -> None:
    field_data_1 = FieldData(name="name 1")
    field_data_2 = FieldData(name="name 2")
    crop_data_1 = CropData(name="crop 1")
    crop_data_2 = CropData(name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)
    field_1 = Field(field_data_1)
    field_2 = Field(field_data_2)
    field_1.crops.append(crop_1)
    field_1.crops.append(crop_2)
    field_2.crops.append(crop_1)
    field_2.crops.append(crop_2)
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
