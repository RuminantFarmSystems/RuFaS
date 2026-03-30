from collections import defaultdict
from datetime import datetime
from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.EEE.emissions import EmissionsEstimator
from RUFAS.units import MeasurementUnits

from tests.test_EEE.fixtures import (
    raw_nitrous_oxide_emissions_data,
    raw_ammonia_emissions_data,
    parsed_emissions_data,
    test_emissions_data,
    raw_fertilizer_application_data,
    raw_manure_application_data,
    parsed_fertilizer_and_manure_application_data,
    raw_received_crop_data,
    expected_crop_to_feed_id_mapping,
    raw_harvest_data,
    expected_harvest_yield_data,
    raw_farmgrown_feed_deductions_data,
    expected_farmgrown_feed_deductions_data,
    expected_daily_farmgrown_feed_emissions_and_resources,
    expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id,
)

assert raw_nitrous_oxide_emissions_data is not None
assert raw_ammonia_emissions_data is not None
assert parsed_emissions_data is not None
assert test_emissions_data is not None
assert raw_fertilizer_application_data is not None
assert raw_manure_application_data is not None
assert parsed_fertilizer_and_manure_application_data is not None
assert raw_received_crop_data is not None
assert expected_crop_to_feed_id_mapping is not None
assert raw_harvest_data is not None
assert expected_harvest_yield_data is not None
assert raw_farmgrown_feed_deductions_data is not None
assert expected_farmgrown_feed_deductions_data is not None
assert expected_daily_farmgrown_feed_emissions_and_resources is not None
assert expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id is not None


@pytest.fixture
def em(mocker: MockerFixture) -> EmissionsEstimator:
    mocker.patch.object(EmissionsEstimator, "__init__", return_value=None)
    em = EmissionsEstimator()

    em.im = InputManager()
    em.om = OutputManager()
    em.crop_species_to_purchased_feed_id = {
        "corn_silage": ["50", "51", "52"],
        "alfalfa_hay": ["100", "103", "106", "107", "108"],
        "wheat": [],
    }
    em.purchased_feed_emissions_by_location = {"44": 0.8, "50": 1.0, "51": 2.0, "52": 3.0, "100": 26.3, "110": 1.1}
    em.land_use_change_emissions_by_location = {"44": 0.6, "50": 0.1, "51": 0.2, "52": 0.3, "100": 2.63, "110": 0.11}

    em._missing_purchased_ids = set()
    em._missing_land_use_ids = set()

    return em


@pytest.fixture
def feeds_grown() -> list[dict[str, Any]]:
    feeds_grown = [
        {
            "crop_name": "corn_silage",
            "dry_yield": 3,
            "area": 10,
            "field_size": 200,
            "planting_year": 2024,
            "planting_day": 3,
        },
        {
            "crop_name": "alfalfa",
            "dry_yield": 9,
            "area": 5,
            "field_size": 200,
            "planting_year": 2024,
            "planting_day": 3,
        },
        {
            "crop_name": "wheat",
            "dry_yield": 500,
            "area": 7,
            "field_size": 200,
            "planting_year": 2024,
            "planting_day": 3,
        },
    ]
    return feeds_grown


@pytest.fixture
def field_emissions() -> dict[str, float]:
    return {"nitrous_oxide": 120.5, "ammonia": 200.75, "carbon_stock_change": 150.0}


@pytest.fixture
def fertilizer_applications_data() -> list[dict[str, Any]]:
    return [
        {"field_name": "field1", "nitrogen": 30.5, "phosphorus": 20.0, "year": 2024, "day": 314},
        {"field_name": "field2", "nitrogen": 25.0, "phosphorus": 15.0, "year": 2024, "day": 314},
        {"field_name": "field3", "nitrogen": 40.0, "phosphorus": 25.5, "year": 2024, "day": 314},
    ]


def test_emissions_estimator_init(mocker: MockerFixture) -> None:
    """Initialize EmissionsEstimator and verify crop_species→rufas_ids mapping is built
    from feed_storage_configurations filtered by feed_storage_instances."""
    mocker.patch("RUFAS.EEE.emissions.OutputManager")
    im_cls = mocker.patch("RUFAS.EEE.emissions.InputManager")
    im = im_cls.return_value

    mocker.patch.object(
        EmissionsEstimator,
        "_get_feed_emissions_data",
        side_effect=[{"50": 1.0}, {"50": 0.1}],
    )

    county_code = 11111

    feed_storage_configurations = {
        "bag": [
            {
                "name": "alfalfa_bag_A",
                "crop_species": "alfalfa_hay",
                "rufas_ids": [100, 103, 106, 107, 108],
            },
            {
                "name": "wheat_bag_X",
                "crop_species": "wheat",
                "rufas_ids": [],
            },
        ],
        "bunker": [
            {
                "name": "corn_silage_bunker_1",
                "crop_species": "corn_silage",
                "rufas_ids": [50, 51, 52],
            }
        ],
    }

    feed_storage_instances = {
        "freestall": ["alfalfa_bag_A", "corn_silage_bunker_1"],
    }

    purchased_feed_emissions_data = {
        "county_code": [county_code],
        "emissions": [{"50": 1.0, "51": 2.0, "52": 3.0}],
    }

    land_use_change_emissions_data = {
        "county_code": [county_code],
        "emissions": [{"50": 0.1, "51": 0.2, "52": 0.3}],
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "config.FIPS_county_code":
            return county_code
        if key == "purchased_feeds_emissions":
            return purchased_feed_emissions_data
        if key == "purchased_feed_land_use_change_emissions":
            return land_use_change_emissions_data
        if key == "feed_storage_configurations":
            return feed_storage_configurations
        if key == "feed_storage_instances":
            return feed_storage_instances
        raise KeyError(key)

    im.get_data.side_effect = get_data_side_effect

    estimator = EmissionsEstimator()

    expected = {
        "corn_silage": ["50", "51", "52"],
        "alfalfa_hay": ["100", "103", "106", "107", "108"],
    }
    assert estimator.crop_species_to_purchased_feed_id == expected


def test_estimate_emissions(
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    """Tests the estimation routines are called correctly."""
    mock_im_get_data = mocker.patch.object(
        em.im, "get_data", return_value={"start_date": "2000:1", "end_date": "2000:100"}
    )
    mock_parse_farmgrown_feeds_emission_data = mocker.patch.object(em, "_parse_farmgrown_feeds_emission_data")
    mock_parse_manure_and_fertilizer_application_data = mocker.patch.object(
        em, "_parse_manure_and_fertilizer_application_data"
    )
    mock_parse_crop_to_feed_id_mapping = mocker.patch.object(em, "_parse_crop_to_feed_id_mapping")
    mock_parse_harvest_data = mocker.patch.object(em, "_parse_harvest_data")
    mock_parse_farmgrown_feed_deductions_data = mocker.patch.object(em, "_parse_farmgrown_feed_deductions_data")
    mock_calculate_daily_farmgrown_feed_emissions_and_resources = mocker.patch.object(
        em, "_calculate_daily_farmgrown_feed_emissions_and_resources"
    )
    mock_calculate_daily_farmgrown_feed_fed_emissions_and_resources = mocker.patch.object(
        em, "_calculate_daily_farmgrown_feed_fed_emissions_and_resources", return_value={}
    )
    mock_report_daily_farmgrown_feed_fed_emissions_and_resources = mocker.patch.object(
        em, "_report_daily_farmgrown_feed_fed_emissions_and_resources"
    )
    mock_calculate_and_report_lca_and_luc_emissions = mocker.patch.object(em, "_calculate_and_report_lca_emissions")

    em.estimate_farmgrown_feed_emissions()

    mock_im_get_data.assert_called_once_with("config")
    mock_parse_farmgrown_feeds_emission_data.assert_called_once()
    mock_parse_manure_and_fertilizer_application_data.assert_called_once()
    mock_parse_crop_to_feed_id_mapping.assert_called_once()
    mock_parse_harvest_data.assert_called_once()
    mock_parse_farmgrown_feed_deductions_data.assert_called_once()
    mock_calculate_daily_farmgrown_feed_emissions_and_resources.assert_called_once()
    mock_calculate_daily_farmgrown_feed_fed_emissions_and_resources.assert_called_once()
    mock_report_daily_farmgrown_feed_fed_emissions_and_resources.assert_called_once()
    mock_calculate_and_report_lca_and_luc_emissions.assert_called_once()


def test_check_available_purchased_feed_data_with_missing(em: EmissionsEstimator, mocker: MockerFixture) -> None:
    """Verifies warnings and set updates when some IDs are missing from both purchased and LUC dicts."""
    warn_spy = mocker.spy(em.om, "add_warning")

    available: list[int] = [52, 100, 103]

    em.check_available_purchased_feed_data(available)

    assert warn_spy.call_count == 2

    titles = [call.args[0] for call in warn_spy.call_args_list]
    messages = [call.args[1] for call in warn_spy.call_args_list]

    assert "Missing Purchased Feed Emissions Data" in titles
    assert "Missing Land Use Change Purchased Feed Emissions Data" in titles
    assert (
        "Missing emissions data for RuFaS feed IDs: 103. "
        "These feeds will be omitted from purchased feed emissions estimations." in messages
    )
    assert (
        "Missing land use change emissions data for RuFaS feed IDs: 103. "
        "These feeds will be omitted from land use change purchased feed emissions estimations." in messages
    )

    assert em._missing_purchased_ids == {"103"}
    assert em._missing_land_use_ids == {"103"}


def test_check_available_purchased_feed_data_accumulates_across_calls(
    em: EmissionsEstimator, mocker: MockerFixture
) -> None:
    """Confirms that missing ID tracking accumulates (set union) over multiple invocations."""
    em._missing_purchased_ids.update({"999"})
    em._missing_land_use_ids.update({"999"})

    warn_spy = mocker.spy(em.om, "add_warning")

    em.check_available_purchased_feed_data([50, 51, 52, 100, 103])

    em.check_available_purchased_feed_data([108])

    assert warn_spy.call_count == 4
    assert em._missing_purchased_ids == {"999", "103", "108"}
    assert em._missing_land_use_ids == {"999", "103", "108"}


def test_calculate_emissions_string_keys_basic(em: EmissionsEstimator, mocker: MockerFixture) -> None:
    """Emissions are calculated for known string feed IDs; unknown IDs are ignored."""
    mock_add_variable = mocker.patch.object(em.om, "add_variable")

    em.calculate_purchased_feed_emissions({50: 10.0, 51: 5.0, 999: 7.0})

    expected_purchased = {"50": 10.0 * 1.0, "51": 5.0 * 2.0}
    expected_luc = {"50": 10.0 * 0.1, "51": 5.0 * 0.2}

    assert mock_add_variable.call_count == 2

    name1, val1, info1 = mock_add_variable.call_args_list[0].args
    assert name1 == "purchased_feed_emissions"
    assert val1 == expected_purchased
    assert info1["function"] == "calculate_purchased_feed_emissions"
    assert info1["units"] == MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER

    name2, val2, info2 = mock_add_variable.call_args_list[1].args
    assert name2 == "land_use_change_emissions"
    assert val2 == expected_luc
    assert info2["function"] == "calculate_purchased_feed_emissions"
    assert info2["units"] == MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER


def test_calculate_emissions_int_keys_stringified(em: EmissionsEstimator, mocker: MockerFixture) -> None:
    """Int feed IDs are stringified for factor lookup, but output dict keeps original key types."""
    mock_add_variable = mocker.patch.object(em.om, "add_variable")

    em.calculate_purchased_feed_emissions({50: 1.5, 100: 2.0})

    expected_purchased = {"50": 1.5 * 1.0, "100": 2.0 * 26.3}
    expected_luc = {"50": 1.5 * 0.1, "100": 2.0 * 2.63}

    assert mock_add_variable.call_count == 2

    name1, val1, info1 = mock_add_variable.call_args_list[0].args
    assert name1 == "purchased_feed_emissions"
    assert val1 == expected_purchased
    assert info1["function"] == "calculate_purchased_feed_emissions"
    assert info1["units"] == MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER

    name2, val2, info2 = mock_add_variable.call_args_list[1].args
    assert name2 == "land_use_change_emissions"
    assert val2 == expected_luc
    assert info2["function"] == "calculate_purchased_feed_emissions"
    assert info2["units"] == MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER


def test_calculate_emissions_empty_input(em: EmissionsEstimator, mocker: MockerFixture) -> None:
    """Empty input still logs two variables with empty dicts."""
    mock_add_variable = mocker.patch.object(em.om, "add_variable")

    em.calculate_purchased_feed_emissions({})

    assert mock_add_variable.call_count == 2

    name1, val1, info1 = mock_add_variable.call_args_list[0].args
    assert name1 == "purchased_feed_emissions"
    assert val1 == {}
    assert info1["function"] == "calculate_purchased_feed_emissions"
    assert info1["units"] == MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER

    name2, val2, info2 = mock_add_variable.call_args_list[1].args
    assert name2 == "land_use_change_emissions"
    assert val2 == {}
    assert info2["function"] == "calculate_purchased_feed_emissions"
    assert info2["units"] == MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER


@pytest.mark.parametrize(
    "feed_emission_data,county_code,expected",
    [
        ({"county_code": [53705, 94545], "data1": [7.7, 92.4]}, 53705, {"data1": 7.7}),
        (
            {"county_code": [53705, 94545], "data1": [7.7, 92.4], "data2": [54.1, 35.4]},
            94545,
            {"data1": 92.4, "data2": 35.4},
        ),
    ],
)
def test_get_feed_emissions_data(
    feed_emission_data: dict[str, list[float]], county_code: int, expected: dict[str, float], em: EmissionsEstimator
) -> None:
    """Tests that feed emission data is correctly retrieved."""
    observed = em._get_feed_emissions_data(county_code, feed_emission_data)
    assert observed == expected


@pytest.mark.parametrize(
    "feed_emission_data,county_code",
    [
        ({"county_code": [53705, 94545], "data1": [7.7, 92.4]}, 53706),
    ],
)
def test_get_feed_emissions_data_invalid_county_code(
    feed_emission_data: dict[str, list[float]], county_code: int, mocker: MockerFixture, em: EmissionsEstimator
) -> None:
    """Tests errors were handled when trying to access invalid county code."""
    mock_add_error = mocker.patch.object(em.om, "add_error")
    try:
        em._get_feed_emissions_data(county_code, feed_emission_data)
    except ValueError:
        mock_add_error.assert_called_once_with(
            "Invalid country code access.",
            "Emission data have county codes [53705, 94545]," "Tried to get data with county code: 53706",
            {"class": "EmissionsEstimator", "function": "_get_feed_emissions_data"},
        )


def test_parse_farmgrown_feeds_emission_data(
    raw_nitrous_oxide_emissions_data: dict[str, dict[str, list[Any]]],
    raw_ammonia_emissions_data: dict[str, dict[str, list[Any]]],
    parsed_emissions_data: dict[str, dict[str, dict[int, float]]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(
        em.om, "filter_variables_pool", side_effect=[raw_nitrous_oxide_emissions_data, raw_ammonia_emissions_data]
    )
    actual_data = em._parse_farmgrown_feeds_emission_data()
    assert actual_data == parsed_emissions_data
    assert mock_om_filter_variables_pool.call_count == 2


def test_parse_manure_and_fertilizer_application_data(
    raw_fertilizer_application_data: dict[str, dict[str, list[Any]]],
    raw_manure_application_data: dict[str, dict[str, list[Any]]],
    parsed_fertilizer_and_manure_application_data: dict[str, dict[str, dict[int, dict[str, float]]]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(
        em.om, "filter_variables_pool", side_effect=[raw_manure_application_data, raw_fertilizer_application_data]
    )
    actual_data = em._parse_manure_and_fertilizer_application_data(datetime.strptime("2013:1", "%Y:%j"))
    assert actual_data == parsed_fertilizer_and_manure_application_data
    assert mock_om_filter_variables_pool.call_count == 2


def test_parse_manure_and_fertilizer_application_no_data(
    raw_fertilizer_application_data: dict[str, dict[str, list[Any]]],
    raw_manure_application_data: dict[str, dict[str, list[Any]]],
    parsed_fertilizer_and_manure_application_data: dict[str, dict[str, dict[int, dict[str, float]]]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(em.om, "filter_variables_pool", side_effect=[{}, {}])
    actual_data = em._parse_manure_and_fertilizer_application_data(datetime.strptime("2013:1", "%Y:%j"))
    assert actual_data == defaultdict(dict)
    assert mock_om_filter_variables_pool.call_count == 2


def test_parse_crop_to_feed_id_mapping(
    raw_received_crop_data: dict[str, dict[str, list[Any]]],
    expected_crop_to_feed_id_mapping: dict[tuple[str, str], RUFAS_ID],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(
        em.om, "filter_variables_pool", return_value=raw_received_crop_data
    )
    actual_data = em._parse_crop_to_feed_id_mapping()
    assert actual_data == expected_crop_to_feed_id_mapping
    mock_om_filter_variables_pool.assert_called_once()


def test_parse_harvest_data(
    raw_harvest_data: dict[str, dict[str, list[Any]]],
    expected_crop_to_feed_id_mapping: dict[tuple[str, str], RUFAS_ID],
    expected_harvest_yield_data: dict[str, dict[int, dict[str, int | str | float]]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(em.om, "filter_variables_pool", return_value=raw_harvest_data)
    actual_data = em._parse_harvest_data(expected_crop_to_feed_id_mapping, datetime.strptime("2013:1", "%Y:%j"))
    assert actual_data == expected_harvest_yield_data
    mock_om_filter_variables_pool.assert_called_once()


def test_parse_farmgrown_feed_deductions_data(
    raw_farmgrown_feed_deductions_data: dict[str, dict[str, list[Any]]],
    expected_farmgrown_feed_deductions_data: dict[RUFAS_ID, dict[int, float]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(
        em.om, "filter_variables_pool", return_value=raw_farmgrown_feed_deductions_data
    )
    all_simulation_days = list(range(0, 750))
    actual_data = em._parse_farmgrown_feed_deductions_data(all_simulation_days)
    assert actual_data == expected_farmgrown_feed_deductions_data
    mock_om_filter_variables_pool.assert_called_once()


def test_parse_farmgrown_feed_deductions_no_data(
    raw_farmgrown_feed_deductions_data: dict[str, dict[str, list[Any]]],
    expected_farmgrown_feed_deductions_data: dict[RUFAS_ID, dict[int, float]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_om_filter_variables_pool = mocker.patch.object(em.om, "filter_variables_pool", return_value={})
    all_simulation_days = list(range(0, 750))
    actual_data = em._parse_farmgrown_feed_deductions_data(all_simulation_days)
    assert actual_data == defaultdict(dict)
    mock_om_filter_variables_pool.assert_called_once()


def test_calculate_daily_farmgrown_feed_emissions_and_resources(
    test_emissions_data: dict[str, dict[str, dict[int, float]]],
    parsed_fertilizer_and_manure_application_data: dict[str, dict[str, dict[int, dict[str, float]]]],
    expected_harvest_yield_data: dict[str, dict[int, dict[str, int | str | float]]],
    expected_daily_farmgrown_feed_emissions_and_resources: dict[RUFAS_ID, dict[int, dict[str, float]]],
    em: EmissionsEstimator,
) -> None:
    all_simulation_days = list(range(0, 750))
    actual_data = em._calculate_daily_farmgrown_feed_emissions_and_resources(
        test_emissions_data,
        parsed_fertilizer_and_manure_application_data,
        expected_harvest_yield_data,
        all_simulation_days,
    )
    for feed_id, day_data in actual_data.items():
        for simulation_day, day_emissions_and_resources in day_data.items():
            for key, value in day_emissions_and_resources.items():
                assert (
                    pytest.approx(actual_data[feed_id][simulation_day][key])
                    == expected_daily_farmgrown_feed_emissions_and_resources[feed_id][simulation_day][key]
                )


def test_calculate_daily_farmgrown_feed_fed_emissions_and_resources(
    expected_daily_farmgrown_feed_emissions_and_resources: dict[RUFAS_ID, dict[int, dict[str, float]]],
    expected_farmgrown_feed_deductions_data: dict[RUFAS_ID, dict[int, float]],
    expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id: dict[RUFAS_ID, dict[int, dict[str, float]]],
    em: EmissionsEstimator,
) -> None:
    all_simulation_days = list(range(0, 750))
    actual_data = em._calculate_daily_farmgrown_feed_fed_emissions_and_resources(
        expected_daily_farmgrown_feed_emissions_and_resources,
        expected_farmgrown_feed_deductions_data,
        all_simulation_days,
    )
    for feed_id, day_data in actual_data.items():
        for simulation_day, day_emissions_and_resources in day_data.items():
            for key, value in day_emissions_and_resources.items():
                assert (
                    pytest.approx(actual_data[feed_id][simulation_day][key])
                    == expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id[feed_id][simulation_day][
                        key
                    ]
                )


def test_report_daily_farmgrown_feed_fed_emissions_and_resources(
    expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id: dict[RUFAS_ID, dict[int, dict[str, float]]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_add_variable_bulk = mocker.patch.object(em.om, "add_variable_bulk")
    em._report_daily_farmgrown_feed_fed_emissions_and_resources(
        expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id
    )
    assert mock_add_variable_bulk.call_count == 2 * 6


def test_calculate_and_report_lca_and_luc_emissions(
    expected_farmgrown_feed_deductions_data: dict[RUFAS_ID, dict[int, float]],
    expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id: dict[RUFAS_ID, dict[int, dict[str, float]]],
    em: EmissionsEstimator,
    mocker: MockerFixture,
) -> None:
    mock_add_variable_bulk = mocker.patch.object(em.om, "add_variable_bulk")
    em._calculate_and_report_lca_emissions(
        list(expected_daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id.keys()),
        expected_farmgrown_feed_deductions_data,
    )
    assert mock_add_variable_bulk.call_count == 2 * 2
