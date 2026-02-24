from typing import List
from unittest.mock import MagicMock, PropertyMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.tillage_implements import TillageImplement
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.field.tillage_application import TillageApplication
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.units import MeasurementUnits


@pytest.mark.parametrize(
    "field_size,container_type,attr_name,attr_value,incorp_frac,expected_remaining,expected_removed",
    [
        (
            1.5,
            "manure_pool",
            "water_extractable_inorganic_phosphorus",
            23,
            0.35,
            14.95,
            8.05,
        ),
        (None, "field", "current_residue", 45, 0.22, 35.1, 9.9),
        (
            0.43,
            "soil",
            "available_phosphorus_pool",
            13.55,
            0.49,
            6.9105,
            6.6395,
        ),
    ],
)
def test_remove_amount_incorporated(
    field_size: float,
    container_type: str,
    attr_name: str,
    attr_value: float,
    incorp_frac: float,
    expected_remaining: float,
    expected_removed: float,
) -> None:
    """Tests that correct amount is removed and returned from the specified pool."""
    if container_type == "field":
        data_container = FieldData()
    else:
        soil_data = SoilData(field_size=field_size)
        if container_type == "manure_pool":
            data_container = soil_data.machine_manure
        else:
            data_container = soil_data

    setattr(data_container, attr_name, attr_value)

    actual_removed = TillageApplication._remove_amount_incorporated(data_container, attr_name, incorp_frac)
    actual_remaining = getattr(data_container, attr_name)

    assert pytest.approx(actual_removed) == expected_removed
    assert pytest.approx(actual_remaining) == expected_remaining


@pytest.mark.parametrize(
    "data,expected",
    [
        ([1, 2, 3], "<class 'list'>"),
        (
            Field(),
            "<class 'RUFAS.biophysical.field.field.field.Field'>",
        ),
    ],
)
def test_remove_amount_incorporated_error(data: object, expected: str) -> None:
    """Test that errors are handled correctly when removing material from soil surface."""
    with pytest.raises(TypeError) as e:
        TillageApplication._remove_amount_incorporated(data, "test", 0.5)
    assert (
        str(e.value) == f"Expected object containing data to be type 'SoilData' or 'FieldData', received type "
        f"'{expected}'."
    )


@pytest.mark.parametrize(
    "layers,field_size,pool_values,pool_name,till_depth,mix_frac,offset_top_layer,expected",
    [
        (
            [
                LayerData(field_size=1.3, top_depth=0, bottom_depth=20),
                LayerData(field_size=1.3, top_depth=20, bottom_depth=60),
                LayerData(field_size=1.3, top_depth=60, bottom_depth=180),
            ],
            1.3,
            [40, 50, 20],
            "nitrate_content",
            120,
            0.3,
            False,
            [33, 45, 32],
        ),
        (
            [
                LayerData(field_size=1.4, top_depth=0, bottom_depth=20),
                LayerData(field_size=1.4, top_depth=20, bottom_depth=50),
            ],
            1.4,
            [30, 10],
            "active_inorganic_phosphorus_content",
            50,
            0.25,
            False,
            [26.5, 13.5],
        ),
        (
            [
                LayerData(field_size=2.1, top_depth=0, bottom_depth=20),
                LayerData(field_size=2.1, top_depth=20, bottom_depth=50),
                LayerData(field_size=2.1, top_depth=50, bottom_depth=110),
                LayerData(field_size=2.1, top_depth=110, bottom_depth=500),
            ],
            2.1,
            [30, 10, 3, 2],
            "nitrate_content",
            50,
            0.25,
            False,
            [26.5, 13.5, 3, 2],
        ),
        (
            [LayerData(field_size=1, top_depth=0, bottom_depth=20)],
            1.0,
            [20],
            "fresh_organic_nitrogen_content",
            20,
            0.4,
            False,
            [20],
        ),
        (
            [
                LayerData(field_size=1.3, top_depth=0, bottom_depth=20),
                LayerData(field_size=1.3, top_depth=20, bottom_depth=60),
                LayerData(field_size=1.3, top_depth=60, bottom_depth=180),
            ],
            1.3,
            [0, 50, 20],
            "passive_carbon_amount",
            160,
            0.3,
            True,
            [0, 40, 27.5],
        ),
    ],
)
def test_mix_soil_layers(
    layers: List[LayerData],
    field_size: float,
    pool_values: List[float],
    pool_name: str,
    till_depth: float,
    mix_frac: float,
    offset_top_layer: bool,
    expected: List[float],
) -> None:
    """Tests that stuff is correctly redistributed between different pools in the soil layer."""
    soil_data = SoilData(field_size=field_size, soil_layers=layers)
    soil_data.set_vectorized_layer_attribute(pool_name, pool_values)
    field_data = FieldData(field_size=field_size)
    tillage_app = TillageApplication(field_data, soil_data)

    tillage_app._mix_soil_layers(pool_name, till_depth, mix_frac, offset_top_layer)

    actual = tillage_app.soil_data.get_vectorized_layer_attribute(pool_name)
    assert actual == expected


@pytest.mark.parametrize(
    "till_depth,incorp_frac,mix_frac,implement,year,day",
    [
        (30, 0.12, 0.33, TillageImplement.CULTIVATOR, 1998, 7),
        (57.8, 0.05, 0.2, TillageImplement.DISK_HARROW, 2001, 7),
        (150, 0.23, 0.19, TillageImplement.SEEDBED_CONDITIONER, 2000, 9),
        (5000, 0.44, 0.51, TillageImplement.SUBSOILER, 2023, 31),
    ],
)
def test_record_tillage(
    till_depth: float,
    incorp_frac: float,
    mix_frac: float,
    implement: TillageImplement,
    year: int,
    day: int,
    mocker: MockerFixture,
) -> None:
    field_data_1 = FieldData(name="field1", field_size=1.5)
    till_app = TillageApplication(field_data=field_data_1)

    expected_clay_percent = 25.0
    expected_units = {
        "tillage_depth": MeasurementUnits.MILLIMETERS,
        "incorporation_fraction": MeasurementUnits.UNITLESS,
        "mixing_fraction": MeasurementUnits.UNITLESS,
        "implement": MeasurementUnits.UNITLESS,
        "year": MeasurementUnits.CALENDAR_YEAR,
        "day": MeasurementUnits.ORDINAL_DAY,
        "field_size": MeasurementUnits.HECTARE,
        "average_clay_percent": MeasurementUnits.PERCENT,
        "field_name": MeasurementUnits.UNITLESS,
    }
    expected_info_map = {
        "class": TillageApplication.__name__,
        "function": TillageApplication._record_tillage.__name__,
        "suffix": "field='field1'",
        "units": expected_units,
    }
    expected_value = {
        "tillage_depth": till_depth,
        "incorporation_fraction": incorp_frac,
        "mixing_fraction": mix_frac,
        "implement": implement,
        "year": year,
        "day": day,
        "field_size": 1.5,
        "average_clay_percent": expected_clay_percent,
        "field_name": "field1",
    }

    mock_add = mocker.patch.object(till_app.om, "add_variable")
    mock_clay = mocker.patch(
        "RUFAS.biophysical.field.soil.soil_data.SoilData.average_clay_percent",
        new_callable=PropertyMock,
        return_value=expected_clay_percent,
    )

    till_app._record_tillage(till_depth, incorp_frac, mix_frac, implement, year, day)

    mock_add.assert_called_once_with("tillage_record", expected_value, expected_info_map)
    mock_clay.assert_called_once()


@pytest.mark.parametrize(
    "till_depth,incorp_frac,mix_frac,implement,year,day",
    [
        (30, 0.12, 0.33, TillageImplement.SUBSOILER, 1998, 7),
        (57.8, 0.05, 0.2, TillageImplement.DISK_HARROW, 2001, 7),
        (150, 0.23, 0.19, TillageImplement.SEEDBED_CONDITIONER, 2000, 9),
        (5000, 0.44, 0.51, TillageImplement.COULTER_CHISEL_PLOW, 2023, 31),
    ],
)
def test_till_soil(
    till_depth: float, incorp_frac: float, mix_frac: float, implement: TillageImplement, year: int, day: int
) -> None:
    """Tests that soil is tilled correctly."""
    field_data_1 = FieldData(name="field1", field_size=1.5)

    till_app = TillageApplication(field_data=field_data_1)

    till_app._remove_amount_incorporated = MagicMock(return_value=8)
    till_app.soil_data.soil_layers[0].add_to_labile_phosphorus = MagicMock()
    till_app._mix_soil_layers = MagicMock()
    till_app._record_tillage = MagicMock()
    bottom_of_soil_profile = till_app.soil_data.soil_layers[-1].bottom_depth
    if till_depth > bottom_of_soil_profile:
        expected_till_depth = bottom_of_soil_profile
    else:
        expected_till_depth = till_depth

    till_app.till_soil(till_depth, incorp_frac, mix_frac, implement, year, day)

    remove_calls = [
        call(till_app.soil_data, "", "available_phosphorus_pool", incorp_frac),
        call(till_app.soil_data, "", "recalcitrant_phosphorus_pool", incorp_frac),
        call(
            till_app.soil_data,
            "machine_manure",
            "water_extractable_inorganic_phosphorus",
            incorp_frac,
        ),
        call(
            till_app.soil_data,
            "machine_manure",
            "water_extractable_organic_phosphorus",
            incorp_frac,
        ),
        call(till_app.soil_data, "machine_manure", "stable_inorganic_phosphorus", incorp_frac),
        call(till_app.soil_data, "machine_manure", "stable_organic_phosphorus", incorp_frac),
        call(
            till_app.soil_data,
            "grazing_manure",
            "water_extractable_inorganic_phosphorus",
            incorp_frac,
        ),
        call(
            till_app.soil_data,
            "grazing_manure",
            "water_extractable_organic_phosphorus",
            incorp_frac,
        ),
        call(till_app.soil_data, "grazing_manure", "stable_inorganic_phosphorus", incorp_frac),
        call(till_app.soil_data, "grazing_manure", "stable_organic_phosphorus", incorp_frac),
    ]
    expected_total_phosphorus = len(remove_calls) * 8
    till_app.soil_data.soil_layers[0].add_to_labile_phosphorus.assert_called_once_with(expected_total_phosphorus, 1.5)
    mix_calls = [
        call("labile_inorganic_phosphorus_content", expected_till_depth, mix_frac, False),
        call("active_inorganic_phosphorus_content", expected_till_depth, mix_frac, False),
        call("stable_inorganic_phosphorus_content", expected_till_depth, mix_frac, False),
        call("nitrate_content", expected_till_depth, mix_frac, False),
        call("ammonium_content", expected_till_depth, mix_frac, False),
        call("active_organic_nitrogen_content", expected_till_depth, mix_frac, False),
        call("stable_organic_nitrogen_content", expected_till_depth, mix_frac, False),
        call("fresh_organic_nitrogen_content", expected_till_depth, mix_frac, False),
        call("metabolic_litter_amount", expected_till_depth, mix_frac, False),
        call("structural_litter_amount", expected_till_depth, mix_frac, False),
        call("active_carbon_amount", expected_till_depth, mix_frac, False),
        call("slow_carbon_amount", expected_till_depth, mix_frac, False),
        call("passive_carbon_amount", expected_till_depth, mix_frac, True),
    ]
    till_app._mix_soil_layers.assert_has_calls(mix_calls)
    till_app._record_tillage.assert_called_once_with(expected_till_depth, incorp_frac, mix_frac, implement, year, day)
