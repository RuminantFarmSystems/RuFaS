import pytest
from typing import List

from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.crop import Crop


@pytest.mark.parametrize("runoff_values, residue_values", [
    ([1.3, 2.4, 1.22], [2, 3, 2.4])
])
def test_send_daily_variables(runoff_values: List[float], residue_values: List[float]) -> None:
    field_data_1 = FieldData(name=" name 1 ")
    field_data_2 = FieldData(name=" name 2 ")
    crop_data_1 = CropData(name="crop 1")
    crop_data_2 = CropData(name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)
    field_1 = Field(field_data_1)
    field_2 = Field(field_data_2)
    field_1.add_crop(crop_1)
    field_1.add_crop(crop_2)
    field_2.add_crop(crop_1)
    field_2.add_crop(crop_2)
    og = OutputGatherer([field_1, field_2])
    for i in range(len(runoff_values)):
        field_1.soil.data.accumulated_runoff = runoff_values[i]
        field_2.soil.data.accumulated_runoff = runoff_values[i]
        field_1.field_data.current_residue = residue_values[i]
        field_2.field_data.current_residue = residue_values[i]
        og.send_daily_variables()
    print(og.om.variables_pool)
    pool = og.om.variables_pool

    # Testing crop variables
    assert 'field name 1 .current_residue' in pool.keys()
    assert len(pool['field name 1 .current_residue']['info_maps']) == 3
    assert pool['field name 1 .current_residue']['values'] == [0, 0, 0]
    assert 'field name 2 .current_residue' in pool.keys()
    assert len(pool['field name 2 .current_residue']['info_maps']) == 3
    assert pool['field name 2 .current_residue']['values'] == [0, 0, 0]

    # Testing soil variables
    assert 'field name 1 .accumulated_runoff' in pool.keys()
    assert len(pool['field name 1 .water_evaporated']['info_maps']) == 3
    assert pool['field name 1 .water_evaporated']['values'] == [0, 0, 0]

    assert 'field name 2 .water_evaporated' in pool.keys()
    assert len(pool['field name 2 .water_evaporated']['info_maps']) == 3
    assert pool['field name 2 .water_evaporated']['values'] == [0, 0, 0]

    # Testing layer data
    assert 'field name 1  layer index 0.percolated_water' in pool.keys()
    assert 'field name 1  layer index 1.percolated_water' in pool.keys()
    assert 'field name 1  layer index 2.percolated_water' in pool.keys()
    assert 'field name 2  layer index 0.percolated_water' in pool.keys()
    assert 'field name 2  layer index 1.percolated_water' in pool.keys()
    assert 'field name 2  layer index 2.percolated_water' in pool.keys()
    assert len(pool['field name 1  layer index 0.percolated_water']['info_maps']) == 3
    assert len(pool['field name 1  layer index 1.percolated_water']['info_maps']) == 3
    assert len(pool['field name 1  layer index 2.percolated_water']['info_maps']) == 3
    assert len(pool['field name 2  layer index 0.percolated_water']['info_maps']) == 3
    assert len(pool['field name 2  layer index 1.percolated_water']['info_maps']) == 3
    assert len(pool['field name 2  layer index 2.percolated_water']['info_maps']) == 3

    assert pool['field name 1  layer index 0.percolated_water']['values'] == [0, 0, 0]
    assert pool['field name 1  layer index 1.percolated_water']['values'] == [0, 0, 0]
    assert pool['field name 1  layer index 2.percolated_water']['values'] == [0, 0, 0]
    assert pool['field name 2  layer index 0.percolated_water']['values'] == [0, 0, 0]
    assert pool['field name 2  layer index 1.percolated_water']['values'] == [0, 0, 0]
    assert pool['field name 2  layer index 2.percolated_water']['values'] == [0, 0, 0]

    # Testing crop data
    assert 'field name 1  crop crop 1.root_depth' in pool.keys()
    assert 'field name 1  crop crop 2.root_depth' in pool.keys()
    assert 'field name 2  crop crop 1.root_depth' in pool.keys()
    assert 'field name 2  crop crop 2.root_depth' in pool.keys()
    assert len(pool['field name 1  crop crop 1.root_depth']['info_maps']) == 3
    assert len(pool['field name 1  crop crop 2.root_depth']['info_maps']) == 3
    assert len(pool['field name 2  crop crop 1.root_depth']['info_maps']) == 3
    assert len(pool['field name 1  crop crop 2.root_depth']['info_maps']) == 3
    assert pool['field name 1  crop crop 1.root_depth']['values'] == [1, 1, 1]
    assert pool['field name 1  crop crop 2.root_depth']['values'] == [1, 1, 1]
    assert pool['field name 2  crop crop 1.root_depth']['values'] == [1, 1, 1]
    assert pool['field name 2  crop crop 2.root_depth']['values'] == [1, 1, 1]


@pytest.mark.parametrize("annual_irrigation_water_use_total", [
    [1.3, 2.4, 1.22]
])
def test_send_annual_variables(annual_irrigation_water_use_total: List[float]) -> None:
    field_data_1 = FieldData(name=" name 1 ")
    field_data_2 = FieldData(name=" name 2 ")
    crop_data_1 = CropData(name="crop 1")
    crop_data_2 = CropData(name="crop 2")
    crop_1 = Crop(crop_data_1)
    crop_2 = Crop(crop_data_2)
    field_1 = Field(field_data_1)
    field_2 = Field(field_data_2)
    field_1.add_crop(crop_1)
    field_1.add_crop(crop_2)
    field_2.add_crop(crop_1)
    field_2.add_crop(crop_2)
    og = OutputGatherer([field_1, field_2])
    for i in range(len(annual_irrigation_water_use_total)):
        field_1.field_data.annual_irrigation_water_use_total = annual_irrigation_water_use_total[i]
        field_2.field_data.annual_irrigation_water_use_total = annual_irrigation_water_use_total[i]
        og.send_annual_variables()
    print(og.om.variables_pool)
    pool = og.om.variables_pool

    # assert False

    # Testing crop variables
    assert 'field name 1 .annual_irrigation_water_use_total' in pool.keys()
    assert len(pool['field name 1 .annual_irrigation_water_use_total']['info_maps']) == 3
    assert pool['field name 1 .annual_irrigation_water_use_total']['values'] == [1.3, 2.4, 1.22]
    assert 'field name 2 .annual_irrigation_water_use_total' in pool.keys()
    # assert len(pool['field name 2 .current_residue']['info_maps']) == 3
    # assert pool['field name 2 .current_residue']['values'] == [0, 0, 0]
    #
    # # Testing soil variables
    # assert 'field name 1 .water_evaporated' in pool.keys()
    # assert len(pool['field name 1 .water_evaporated']['info_maps']) == 3
    # assert pool['field name 1 .water_evaporated']['values'] == [0, 0, 0]
    #
    # assert 'field name 2 .water_evaporated' in pool.keys()
    # assert len(pool['field name 2 .water_evaporated']['info_maps']) == 3
    # assert pool['field name 2 .water_evaporated']['values'] == [0, 0, 0]
    #
    # # Testing layer data
    # assert 'field name 1  layer index 0.percolated_water' in pool.keys()
    # assert 'field name 1  layer index 1.percolated_water' in pool.keys()
    # assert 'field name 1  layer index 2.percolated_water' in pool.keys()
    # assert 'field name 2  layer index 0.percolated_water' in pool.keys()
    # assert 'field name 2  layer index 1.percolated_water' in pool.keys()
    # assert 'field name 2  layer index 2.percolated_water' in pool.keys()
    # assert len(pool['field name 1  layer index 0.percolated_water']['info_maps']) == 3
    # assert len(pool['field name 1  layer index 1.percolated_water']['info_maps']) == 3
    # assert len(pool['field name 1  layer index 2.percolated_water']['info_maps']) == 3
    # assert len(pool['field name 2  layer index 0.percolated_water']['info_maps']) == 3
    # assert len(pool['field name 2  layer index 1.percolated_water']['info_maps']) == 3
    # assert len(pool['field name 2  layer index 2.percolated_water']['info_maps']) == 3
    #
    # assert pool['field name 1  layer index 0.percolated_water']['values'] == [0, 0, 0]
    # assert pool['field name 1  layer index 1.percolated_water']['values'] == [0, 0, 0]
    # assert pool['field name 1  layer index 2.percolated_water']['values'] == [0, 0, 0]
    # assert pool['field name 2  layer index 0.percolated_water']['values'] == [0, 0, 0]
    # assert pool['field name 2  layer index 1.percolated_water']['values'] == [0, 0, 0]
    # assert pool['field name 2  layer index 2.percolated_water']['values'] == [0, 0, 0]
    #
    # # Testing crop data
    # assert 'field name 1  crop crop 1.root_depth' in pool.keys()
    # assert 'field name 1  crop crop 2.root_depth' in pool.keys()
    # assert 'field name 2  crop crop 1.root_depth' in pool.keys()
    # assert 'field name 2  crop crop 2.root_depth' in pool.keys()
    # assert len(pool['field name 1  crop crop 1.root_depth']['info_maps']) == 3
    # assert len(pool['field name 1  crop crop 2.root_depth']['info_maps']) == 3
    # assert len(pool['field name 2  crop crop 1.root_depth']['info_maps']) == 3
    # assert len(pool['field name 1  crop crop 2.root_depth']['info_maps']) == 3
    # assert pool['field name 1  crop crop 1.root_depth']['values'] == [1, 1, 1]
    # assert pool['field name 1  crop crop 2.root_depth']['values'] == [1, 1, 1]
    # assert pool['field name 2  crop crop 1.root_depth']['values'] == [1, 1, 1]
    # assert pool['field name 2  crop crop 2.root_depth']['values'] == [1, 1, 1]
