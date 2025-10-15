from math import inf
from typing import List
from unittest.mock import PropertyMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


def test_get_vectorized_layer_attribute() -> None:
    """ensures that layer data can be vectorized."""
    soil_layers = [
        LayerData(
            top_depth=0,
            bottom_depth=20,
            soil_water_concentration=500,
            field_capacity_water_concentration=0.15,
            saturation_point_water_concentration=0.2,
            field_size=1.55,
        ),
        LayerData(
            top_depth=20,
            bottom_depth=25,
            soil_water_concentration=1000,
            field_capacity_water_concentration=0.5,
            saturation_point_water_concentration=0.8,
            field_size=1.55,
        ),
        LayerData(
            top_depth=25,
            bottom_depth=30,
            soil_water_concentration=30,
            field_capacity_water_concentration=0.10,
            saturation_point_water_concentration=0.11,
            field_size=1.55,
        ),
        LayerData(
            top_depth=30,
            bottom_depth=100,
            soil_water_concentration=5000,
            field_capacity_water_concentration=0.5,
            saturation_point_water_concentration=0.5,
            field_size=1.55,
        ),
    ]
    soil_data = SoilData(soil_layers=soil_layers, field_size=1.55)

    assert soil_data.get_vectorized_layer_attribute("top_depth") == [0, 20, 25, 30]
    assert soil_data.get_vectorized_layer_attribute("bottom_depth") == [20, 25, 30, 100]
    assert soil_data.get_vectorized_layer_attribute("soil_water_concentration") == [
        500,
        1000,
        30,
        5000,
    ]
    assert soil_data.get_vectorized_layer_attribute("field_capacity_water_concentration") == [0.15, 0.5, 0.10, 0.5]
    assert soil_data.get_vectorized_layer_attribute("saturation_point_water_concentration") == [0.2, 0.8, 0.11, 0.5]
    with pytest.raises(Exception):
        soil_data.get_vectorized_layer_attribute("non_existant_variable")


def test_set_vectorized_layer_attribute() -> None:
    """ensures that layer attributes are properly set"""
    soil_data = SoilData(field_size=1.55)  # 4 layers by default
    water_concentration = [0.1, 0.2, 1, 0.8]
    soil_data.set_vectorized_layer_attribute("soil_water_concentration", water_concentration)
    assert soil_data.get_vectorized_layer_attribute("soil_water_concentration") == water_concentration


def test_manual_soil_data_configuration() -> None:
    """Test that creating a custom SoilData object actually has all the correct values in its fields"""
    mollisols = SoilData(
        name="mollisols",
        field_size=1.8,
        soil_layers=[
            LayerData(
                top_depth=0,
                bottom_depth=80,
                initial_soil_nitrate_concentration=1.8,
                field_size=1.8,
            ),
            LayerData(
                top_depth=80,
                bottom_depth=150,
                initial_soil_nitrate_concentration=2.6,
                field_size=1.8,
            ),
            LayerData(
                top_depth=150,
                bottom_depth=300,
                initial_soil_nitrate_concentration=5,
                field_size=1.8,
            ),
        ],
    )

    assert mollisols.name == "mollisols"
    assert mollisols.soil_layers[0] == LayerData(
        top_depth=0,
        bottom_depth=20,
        initial_soil_nitrate_concentration=1.8,
        field_size=1.8,
    )
    assert mollisols.soil_layers[1] == LayerData(
        top_depth=20,
        bottom_depth=80,
        initial_soil_nitrate_concentration=1.8,
        field_size=1.8,
    )
    assert mollisols.soil_layers[2] == LayerData(
        top_depth=80,
        bottom_depth=150,
        initial_soil_nitrate_concentration=2.6,
        field_size=1.8,
    )
    assert mollisols.soil_layers[3] == LayerData(
        top_depth=150,
        bottom_depth=300,
        initial_soil_nitrate_concentration=5,
        field_size=1.8,
    )
    expected_vadose_zone_layer = LayerData(
        top_depth=300,
        bottom_depth=10000000,
        soil_water_concentration=0,
        field_size=1.8,
        saturation_point_water_concentration=inf,
        initial_labile_inorganic_phosphorus_concentration=0,
        initial_soil_nitrate_concentration=0,
    )
    expected_vadose_zone_layer.active_organic_nitrogen_content = 0
    expected_vadose_zone_layer.stable_organic_nitrogen_content = 0
    assert mollisols.vadose_zone_layer == expected_vadose_zone_layer


def test_error_manual_soil_data_configuration() -> None:
    """Test that an error is correctly raised when an invalid input is used to create SoilData object."""
    with pytest.raises(TypeError) as e:
        SoilData(
            field_size=1.8,
            soil_layers=[
                LayerData(top_depth=0, bottom_depth=19, initial_soil_nitrate_concentration=1.8),
                LayerData(
                    top_depth=19,
                    bottom_depth=150,
                    initial_soil_nitrate_concentration=2.6,
                ),
                LayerData(
                    top_depth=150,
                    bottom_depth=300,
                    initial_soil_nitrate_concentration=5,
                ),
            ],
        )
    assert str(e.value) == "'field_size' attribute is NoneType, must be given value when LayerData is initialized."
    with pytest.raises(ValueError) as e:
        SoilData(
            field_size=1.8,
            soil_layers=[
                LayerData(
                    top_depth=0,
                    bottom_depth=19,
                    initial_soil_nitrate_concentration=1.8,
                    field_size=1.8,
                ),
                LayerData(
                    top_depth=19,
                    bottom_depth=150,
                    initial_soil_nitrate_concentration=2.6,
                    field_size=1.8,
                ),
                LayerData(
                    top_depth=150,
                    bottom_depth=300,
                    initial_soil_nitrate_concentration=5,
                    field_size=-1.8,
                ),
            ],
        )
    assert str(e.value) == "Expected field_size to be greater than 0, received '-1.8'."
    with pytest.raises(ValueError) as e:
        SoilData(
            field_size=1.8,
            soil_layers=[
                LayerData(
                    top_depth=0,
                    bottom_depth=19,
                    initial_soil_nitrate_concentration=1.8,
                    field_size=1.8,
                ),
                LayerData(
                    top_depth=19,
                    bottom_depth=150,
                    initial_soil_nitrate_concentration=2.6,
                    field_size=1.8,
                ),
                LayerData(
                    top_depth=150,
                    bottom_depth=300,
                    initial_soil_nitrate_concentration=5,
                    field_size=1.8,
                ),
            ],
        )
    assert str(e.value) == "Expected bottom depth of top soil layer must be 20 mm or greater, received '19'."


def test_annual_reset() -> None:
    """Test that annual_reset() actually resets the values it should"""
    soil_data = SoilData(name="test", field_size=2.11)

    soil_data.initial_water_content = 1.5
    soil_data.initial_nitrates_total = 2.5
    soil_data.annual_soil_evaporation_total = 1
    soil_data.annual_runoff_total = 2
    soil_data.annual_eroded_sediment_total = 3
    soil_data.annual_surface_runoff_total = 4
    soil_data.annual_runoff_fertilizer_phosphorus = 5
    soil_data.machine_manure.annual_runoff_manure_organic_phosphorus = 6
    soil_data.machine_manure.annual_runoff_manure_inorganic_phosphorus = 7
    soil_data.grazing_manure.annual_runoff_manure_organic_phosphorus = 8
    soil_data.grazing_manure.annual_runoff_manure_inorganic_phosphorus = 9
    soil_data.annual_soil_phosphorus_runoff = 10
    soil_data.annual_runoff_nitrates_total = 11
    soil_data.annual_runoff_ammonium_total = 12
    soil_data.annual_eroded_fresh_organic_nitrogen_total = 13
    soil_data.annual_eroded_stable_organic_nitrogen_total = 14
    soil_data.annual_eroded_active_organic_nitrogen_total = 15

    with patch.multiple(
        "RUFAS.biophysical.field.soil.soil_data.SoilData",
        profile_soil_water_content=PropertyMock(return_value=1.05),
        profile_nitrates_total=PropertyMock(return_value=2.83),
    ):
        soil_data.do_annual_reset()

        assert soil_data.initial_water_content == soil_data.profile_soil_water_content
        assert soil_data.initial_nitrates_total == soil_data.profile_nitrates_total
        assert soil_data.annual_soil_evaporation_total == 0
        assert soil_data.annual_runoff_total == 0
        assert soil_data.annual_eroded_sediment_total == 0
        assert soil_data.annual_surface_runoff_total == 0
        assert soil_data.annual_runoff_fertilizer_phosphorus == 0
        assert soil_data.machine_manure.annual_runoff_manure_organic_phosphorus == 0
        assert soil_data.machine_manure.annual_runoff_manure_inorganic_phosphorus == 0
        assert soil_data.grazing_manure.annual_runoff_manure_organic_phosphorus == 0
        assert soil_data.grazing_manure.annual_runoff_manure_inorganic_phosphorus == 0
        assert soil_data.annual_soil_phosphorus_runoff == 0
        assert soil_data.annual_runoff_nitrates_total == 0
        assert soil_data.annual_runoff_ammonium_total == 0
        assert soil_data.annual_eroded_fresh_organic_nitrogen_total == 0
        assert soil_data.annual_eroded_stable_organic_nitrogen_total == 0
        assert soil_data.annual_eroded_active_organic_nitrogen_total == 0


def test_profile_soil_water_content() -> None:
    """Test that SoilData correctly calculates amount of water in the entire soil profile"""
    # Set water content and wilting point content of every soil layer to certain amount
    with patch.multiple(
        "RUFAS.biophysical.field.soil.layer_data.LayerData",
        soil_water_concentration=PropertyMock(return_value=0.87),
        layer_thickness=PropertyMock(return_value=1),
        wilting_point_content=PropertyMock(return_value=0.32),
    ):
        soil_data = SoilData(field_size=0.98)
        observe = soil_data.profile_soil_water_content
        expect = len(soil_data.soil_layers) * (0.87 - 0.32)
        assert observe == expect


def test_profile_saturation() -> None:
    """Test that SoilData correctly calculates the amount of water in soil profile when completely saturated"""
    with patch(
        "RUFAS.biophysical.field.soil.layer_data.LayerData.saturation_content",
        new_callable=PropertyMock,
        return_value=0.98,
    ):
        soil_data = SoilData(field_size=1.83)
        observe = soil_data.profile_saturation
        expect = len(soil_data.soil_layers) * 0.98
        assert observe == expect


def test_profile_field_capacity() -> None:
    """Test that SoilData correctly calculates the amount of water in the soil profile when at field capacity"""
    with patch(
        "RUFAS.biophysical.field.soil.layer_data.LayerData.field_capacity_content",
        new_callable=PropertyMock,
        return_value=0.67,
    ):
        soil_data = SoilData(field_size=1.223)
        observe = soil_data.profile_field_capacity
        expect = len(soil_data.soil_layers) * 0.67
        assert observe == expect


@pytest.mark.parametrize(
    "profile_water,profile_field_capacity,expected",
    [(3.5, 4.5, 0.91503268), (5.0, 5.5, 1.0), (0.0, 3.0, 0.0), (-1.0, 3.0, 0.0)],
)
def test_soil_water_factor(profile_water: float, profile_field_capacity: float, expected: float) -> None:
    """Test that SoilData correctly calculates the soil water factor for a soil profile."""
    with patch.multiple(
        "RUFAS.biophysical.field.soil.soil_data.SoilData",
        profile_soil_water_content=PropertyMock(return_value=profile_water),
        profile_field_capacity=PropertyMock(return_value=profile_field_capacity),
    ):
        soil_data = SoilData(field_size=1.88)
        actual = soil_data.soil_water_factor
        assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "layers",
    [
        [
            LayerData(top_depth=0, bottom_depth=30, bulk_density=2.4, field_size=1.5),
            LayerData(top_depth=30, bottom_depth=76, bulk_density=2.9, field_size=1.5),
            LayerData(top_depth=76, bottom_depth=145, bulk_density=3.4, field_size=1.5),
        ],
        [
            LayerData(top_depth=0, bottom_depth=140, bulk_density=5.683745, field_size=1.5),
            LayerData(top_depth=140, bottom_depth=369, bulk_density=8.9384785, field_size=1.5),
            LayerData(top_depth=369, bottom_depth=798, bulk_density=7.485968, field_size=1.5),
        ],
        [
            LayerData(top_depth=0, bottom_depth=99, bulk_density=1.88973834, field_size=1.5),
            LayerData(top_depth=99, bottom_depth=213, bulk_density=2.119481, field_size=1.5),
            LayerData(top_depth=213, bottom_depth=359, bulk_density=2.556948, field_size=1.5),
        ],
    ],
)
def test_profile_bulk_density(layers: List[LayerData]) -> None:
    """Test that SoilData correctly calculates average bulk density of soil profile, weighted by layer thickness"""
    soil_data = SoilData(field_size=1.5, soil_layers=layers)
    observe = soil_data.profile_bulk_density
    expect_top = 0
    expect_bottom = 0
    for layer in layers:
        expect_top += layer.bulk_density * layer.layer_thickness
        expect_bottom += layer.layer_thickness
    assert observe == (expect_top / expect_bottom)


@pytest.mark.parametrize(
    "layers",
    [
        [
            LayerData(
                top_depth=0,
                bottom_depth=30,
                initial_soil_nitrate_concentration=3.8,
                field_size=0.95,
            ),
            LayerData(
                top_depth=30,
                bottom_depth=76,
                initial_soil_nitrate_concentration=2.9,
                field_size=0.95,
            ),
            LayerData(
                top_depth=76,
                bottom_depth=145,
                initial_soil_nitrate_concentration=1.99,
                field_size=0.95,
            ),
        ],
        [
            LayerData(
                top_depth=0,
                bottom_depth=140,
                initial_soil_nitrate_concentration=10.9983,
                field_size=0.95,
            ),
            LayerData(
                top_depth=140,
                bottom_depth=369,
                initial_soil_nitrate_concentration=8.9384785,
                field_size=0.95,
            ),
            LayerData(
                top_depth=369,
                bottom_depth=798,
                initial_soil_nitrate_concentration=7.485968,
                field_size=0.95,
            ),
        ],
        [
            LayerData(
                top_depth=0,
                bottom_depth=99,
                initial_soil_nitrate_concentration=5.3950,
                field_size=0.95,
            ),
            LayerData(
                top_depth=99,
                bottom_depth=213,
                initial_soil_nitrate_concentration=3.20583,
                field_size=0.95,
            ),
            LayerData(
                top_depth=213,
                bottom_depth=359,
                initial_soil_nitrate_concentration=2.556948,
                field_size=0.95,
            ),
        ],
    ],
)
def test_profile_nitrates_total(layers: List[LayerData]) -> None:
    """Test that SoilData correctly sums nitrates contained in soil profile"""
    soil_data = SoilData(field_size=0.95, soil_layers=layers)
    expect = 10 * len(soil_data.soil_layers)
    for layer in soil_data.soil_layers:
        layer.nitrate_content = 10
    observe = soil_data.profile_nitrates_total
    assert observe == expect


@pytest.mark.parametrize(
    "residues,expected",
    [([0.5, 12.0, 15.0, 0.0], 27.5), ([0.0, 0.0, 0.0], 0.0), ([10.0, 10.0, 10.0], 30.0)],
)
def test_total_residue(mocker: MockerFixture, residues: list[float], expected: float) -> None:
    """Tests the property method total_residue sums up the residues correctly"""
    soil_data = SoilData(field_size=0.98)
    get_vec_attr = mocker.patch.object(soil_data, "get_vectorized_layer_attribute", return_value=residues)

    actual = soil_data.total_residue

    assert actual == expected
    get_vec_attr.assert_called_once_with("plant_residue")


def test_soil_data_post_init_error() -> None:
    """Test that the correct errors were thrown when incorrect values were used in post init"""
    with pytest.raises(TypeError) as e:
        soil_data = SoilData(field_size=0.98)
        soil_data.__post_init__(None)
        assert str(e) == "'field_size' attribute is NoneType, must be given value when SoilData is initialized."

    with pytest.raises(ValueError) as e2:
        soil_data = SoilData(field_size=0.98)
        soil_data.__post_init__(-20)
        assert str(e2) == "Expected field_size to be greater than 0, received -20."


@pytest.mark.parametrize("cover_type", ["BARE", "RESIDUE_COVER", "GRASSED", "SOU"])
def test_cover_factor(cover_type: str) -> None:
    """Test that the cover factor method returns the correct value for each time or else gives the right error"""
    soil_data = SoilData(field_size=0.98, cover_type=cover_type)
    if cover_type == "BARE":
        assert soil_data.cover_factor == 0.5333
    elif cover_type == "RESIDUE_COVER":
        assert soil_data.cover_factor == 0.6667
    elif cover_type == "GRASSED":
        assert soil_data.cover_factor == 0.8
    else:
        with pytest.raises(ValueError) as e:
            soil_data.cover_factor
            assert (
                str(e) == f"Expected cover type to be 'BARE', 'RESIDUE_COVER', or 'GRASSED', "
                f"received: '{cover_type}'."
            )


def test_zero_silt_clay_warning(mocker: MockerFixture) -> None:
    """Tests the case when silt and clay are zero."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_warning")
    soil_layers = [
        LayerData(
            top_depth=0,
            bottom_depth=20,
            soil_water_concentration=500,
            field_capacity_water_concentration=0.15,
            saturation_point_water_concentration=0.2,
            field_size=1.55,
            silt_fraction=0,
            clay_fraction=0,
        )
    ]
    data = SoilData(soil_layers=soil_layers, field_size=0.95)  # noqa: F841
    info_map = {"class": "SoilData", "function": "__post_init__"}
    mock_add.assert_called_once_with(
        "Silt and clay fractions in the soil are 0, which will lead to unreliable "
        "predictions of erosion and soil emissions",
        "It is assumed that the ratio of clay to silt in the soil layer will not have "
        "any effect on the amount of erosion from the soil.",
        info_map,
    )
