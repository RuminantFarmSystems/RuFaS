import pytest
from typing import List

from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer


@pytest.mark.parametrize("runoff_values", [
    [1.3, 2.4, 1.22]
])
def test_send_daily_variables(runoff_values: List[float]) -> None:
    field_data_1 = FieldData(name=" name 1 ")
    field_data_2 = FieldData(name=" name 2 ")
    field_1 = Field(field_data_1)
    field_2 = Field(field_data_2)
    og = OutputGatherer([field_1, field_2])
    for i in range(len(runoff_values)):
        field_1.soil.data.accumulated_runoff = runoff_values[i]
        field_2.soil.data.accumulated_runoff = runoff_values[i]
        og.send_daily_variables()
    print(og.om.variables_pool)
    pool = og.om.variables_pool
    assert 'field name 1 .current_residue' in pool.keys()
    assert len(pool['field name 1 .current_residue']['info_maps']) == 3
    assert len(pool['field name 1 .current_residue']['values']) == 3
    for prefix_dict in pool['field name 1 .current_residue']['info_maps']:
        assert prefix_dict['prefix'] == 'field name 1 '
    assert 'field name 2 .current_residue' in pool.keys()
    assert len(pool['field name 2 .current_residue']['info_maps']) == 3
    assert len(pool['field name 2 .current_residue']['values']) == 3
    for prefix_dict in pool['field name 2 .current_residue']['info_maps']:
        assert prefix_dict['prefix'] == 'field name 2 '
