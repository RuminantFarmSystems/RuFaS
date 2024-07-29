import pytest
from pytest_mock import MockerFixture
from math import exp
from unittest.mock import PropertyMock, call

from RUFAS.routines.field.soil.nitrogen_cycling.denitrification import Denitrification
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData


@pytest.fixture
def denitrifier(mocker: MockerFixture) -> Denitrification:
    mocker.patch.object(Denitrification, "__init__", return_value=None)
    return Denitrification()


@pytest.mark.parametrize(
    "nitrates,denitrification_rate,temp_factor,carbon_proportion",
    [
        (78, 1.4, 0.88, 0.60),
        (104.55, 0.33, 0.233, 0.4455),
        (22.12, 0.0, 0.5561, 0.71223),
        (204.445, 3.0, 0.781, 0.22334),
        (0.0, 2.55, 0.1554, 0.39112),
    ],
)
def test_calculate_denitrification_amount(
    nitrates: float,
    denitrification_rate: float,
    temp_factor: float,
    carbon_proportion: float,
) -> None:
    """Tests that the amount of nitrified nitrates is calculated correctly."""
    actual = Denitrification._calculate_denitrification_amount(
        nitrates, denitrification_rate, temp_factor, carbon_proportion
    )
    expected_denitrification_factor = max(
        min(1 - exp(-1 * denitrification_rate * temp_factor * carbon_proportion * 100), 1.0), 0.0
    )
    expected = nitrates * expected_denitrification_factor
    assert actual == expected


@pytest.mark.parametrize("nitrates,expected", [(25.0, -0.5165393), (0.0, -0.3209067), (150.0, -4.348873)])
def test_calculate_nitrate_effect(denitrifier: Denitrification, nitrates: float, expected: float) -> None:
    """Tests that the nitrate effect is correctly calculated."""
    actual = denitrifier._calculate_nitrate_effect(nitrates)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("carbon,expected", [(0.0, 0.9067742), (100.0, 27.8783693), (200.0, 28.1517989)])
def test_calculate_carbon_effect(denitrifier: Denitrification, carbon: float, expected: float) -> None:
    """Tests that the carbon effect is correctly calculated."""
    actual = denitrifier._calculate_carbon_effect(carbon)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("pH,expected", [(5.0, 0.1664570), (6.5, 0.8667387), (7.5, 2.6038270), (10.0, 40.7307086)])
def test_calculate_pH_effect(denitrifier: Denitrification, pH: float, expected: float) -> None:
    """Tests that the pH effect is correctly calculated."""
    actual = denitrifier._calculate_pH_effect(pH)

    assert pytest.approx(actual) == expected


# @pytest.mark.parametrize("nitrate,carbon,moisture,pH,expected", [(-0.3, 28.0, 0.4, 0.6, 0.0)])


def test_denitrify(mocker: MockerFixture) -> None:
    """
    Tests that the main routine correctly gets the amount of nitrates nitrified and removes it from the nitrate pool.

    Notes
    -----
    This test achieves full code coverage by creating a soil profile in which the top (first), third, and fourth layers
    should have nitrate removed by denitrification, while the second layer should not. This is done by setting the
    `denitrification_threshold_water_content` attribute of the top, third, and fourth layers to be below the mocked
    `nutrient_cycling_water_factor`, and above for the second.

    """
    mocker.patch.object(LayerData, "nutrient_cycling_water_factor", new_callable=PropertyMock, return_value=0.91)
    mocker.patch.object(LayerData, "nutrient_cycling_temp_factor", new_callable=PropertyMock, return_value=0.89)
    data = SoilData(field_size=1.8)
    incorp = Denitrification(data)
    incorp.data.set_vectorized_layer_attribute("nitrate_content", [35] * 4)
    incorp.data.set_vectorized_layer_attribute("denitrification_threshold_water_content", [0.5, 1.3, 0.5, 0.5])
    incorp.data.set_vectorized_layer_attribute("denitrification_rate_coefficient", [1.5] * 4)
    incorp.data.set_vectorized_layer_attribute("soil_overall_carbon_fraction", [0.65] * 4)
    incorp.data.set_vectorized_layer_attribute("nitrous_oxide_emissions", [0.11] * 4)
    calc_denit = mocker.patch.object(incorp, "_calculate_denitrification_amount", return_value=15.0)
    nitrate = mocker.patch.object(incorp, "_calculate_nitrate_effect")
    carbon = mocker.patch.object(incorp, "_calculate_carbon_effect")
    moisture = mocker.patch.object(incorp, "_calculate_moisture_effect")
    pH = mocker.patch.object(incorp, "_calculate_pH_effect")
    partition_factor = mocker.patch.object(incorp, "_calculate_partitioning_factor")
    calc_nitrous_oxide = mocker.patch.object(incorp, "_calculate_nitrous_oxide_emissions", return_value=10.0)

    incorp.denitrify()

    nitrification_amount_calls = [call(35, 1.5, 0.89, 0.65)] * 3
    calc_denit.assert_has_calls(nitrification_amount_calls)
    assert nitrate.call_count == 3
    assert carbon.call_count == 3
    assert moisture.call_count == 3
    assert pH.call_count == 3
    assert partition_factor.call_count == 3
    assert calc_nitrous_oxide.call_count == 3
    for index in [0, 2, 3]:
        assert incorp.data.soil_layers[index].nitrate_content == 20
        assert incorp.data.soil_layers[index].nitrous_oxide_emissions == 10.0
        assert incorp.data.soil_layers[index].annual_nitrous_oxide_emissions_total == 10.0
        assert incorp.data.soil_layers[index].dinitrogen_emissions == 5.0
    assert incorp.data.soil_layers[1].nitrate_content == 35
    assert incorp.data.soil_layers[1].nitrous_oxide_emissions == 0.0
    assert incorp.data.soil_layers[1].annual_nitrous_oxide_emissions_total == 0.0
    assert incorp.data.soil_layers[1].dinitrogen_emissions == 0.0
