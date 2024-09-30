from datetime import datetime
from typing import Any
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.EEE.emissions import EmissionsEstimator
from RUFAS.routines.field.crop.crop_enum import CropSpecies
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


@pytest.mark.parametrize(
    "homegrown_feeds,fertilizer_applications,manure_applications,manure_requests",
    [
        (
            [
                {"feed_type": "Alfalfa", "quantity_tons": 10.5, "is_organic": True, "harvest_date": "2024-08-15"},
                {"feed_type": "Corn Silage", "quantity_tons": 25.0, "is_organic": False, "harvest_date": "2024-07-10"},
            ],
            [
                {
                    "field_id": 101,
                    "fertilizer_type": "Nitrogen",
                    "application_rate_kg_per_ha": 50,
                    "application_date": "2024-04-15",
                    "is_organic": False,
                },
                {
                    "field_id": 102,
                    "fertilizer_type": "Compost",
                    "application_rate_kg_per_ha": 100,
                    "application_date": "2024-05-20",
                    "is_organic": True,
                },
            ],
            [
                {
                    "field_id": 201,
                    "manure_type": "Cow Manure",
                    "application_rate_kg_per_ha": 200,
                    "application_date": "2024-06-10",
                    "method": "Broadcast",
                },
                {
                    "field_id": 202,
                    "manure_type": "Pig Manure",
                    "application_rate_kg_per_ha": 180,
                    "application_date": "2024-07-05",
                    "method": "Injection",
                },
            ],
            [
                {
                    "request_id": 301,
                    "farm_name": "Green Valley Farms",
                    "manure_type": "Cow Manure",
                    "quantity_tons": 50,
                    "requested_date": "2024-08-01",
                    "status": "Pending",
                },
                {
                    "request_id": 302,
                    "farm_name": "Sunny Acres",
                    "manure_type": "Calf Manure",
                    "quantity_tons": 30,
                    "requested_date": "2024-08-10",
                    "status": "Fulfilled",
                },
            ],
        )
    ],
)
def test_estimate_emissions(
    homegrown_feeds: list[dict[str, Any]],
    fertilizer_applications: list[dict[str, Any]],
    manure_applications: list[dict[str, Any]],
    manure_requests: list[dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Tests the estimation routines are called correctly."""
    em = EmissionsEstimator()
    mock_gather = mocker.patch.object(
        em,
        "_gather_homegrown_feeds_and_fertilizer_apps",
        return_value={
            "Homegrown Feeds": homegrown_feeds,
            "Fertilizer Applications": fertilizer_applications,
            "Manure Applications": manure_applications,
            "Manure Requests": manure_requests,
        },
    )
    mock_purchase = mocker.patch.object(em, "_calculate_purchased_feed_emissions")
    mock_homegrown = mocker.patch.object(em, "_calculate_homegrown_feed_emissions")

    em.estimate_emissions()
    mock_gather.assert_called_once()
    mock_purchase.assert_called_once_with(homegrown_feeds)
    mock_homegrown.assert_called_once_with(
        homegrown_feeds, fertilizer_applications, manure_applications, manure_requests
    )


@pytest.mark.parametrize(
    "homegrown_feeds,purchased_feeds,actual_purchased_feeds,actual_purchased_feed_emissions,"
    "actual_land_use_change_emissions",
    [
        (
            [{"feed1": 5, "feed2": 2.6}, {"feed3": 9.24, "feed4": 7.7}],
            {"feed5": 5.3, "feed6": 7.6},
            {"feed7": 5.6, "feed8": 7.95},
            {"emission1": 5.6, "emission2": 7.95},
            {"emission1": 5.6, "emission2": 7.95},
        )
    ],
)
def test_calculate_purchased_feed_emissions(
    homegrown_feeds: list[dict[str, Any]],
    purchased_feeds: dict[str, float],
    actual_purchased_feeds: dict[str, float],
    actual_purchased_feed_emissions: dict[str, float],
    actual_land_use_change_emissions: dict[str, float],
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of purchased feed emissions."""
    em = EmissionsEstimator()
    mock_add = mocker.patch.object(OutputManager, "add_variable")
    mock_gather_feeds = mocker.patch.object(em, "_gather_ration_feed_totals", return_value=purchased_feeds)
    mock_calc_actual = mocker.patch.object(em, "_calculate_actual_purchased_feeds", return_value=actual_purchased_feeds)
    mock_calc_actual_emission = mocker.patch.object(
        em,
        "_calculate_actual_purchased_feed_emissions",
        return_value=(actual_purchased_feed_emissions, actual_land_use_change_emissions),
    )

    em._calculate_purchased_feed_emissions(homegrown_feeds)

    assert mock_add.call_count == 3
    mock_gather_feeds.assert_called_once()
    mock_calc_actual.assert_called_once_with(homegrown_feeds, purchased_feeds)
    mock_calc_actual_emission.assert_called_once_with(actual_purchased_feeds)


def test_gather_homegrown_feeds_and_fertilizer_apps(mocker: MockerFixture) -> None:
    em = EmissionsEstimator()
    mock_filter_variable = mocker.patch.object(
        em.om,
        "filter_variables_pool",
        return_value={"Time.day": {"values": [20]}, "Time.calendar_year": {"values": [2014]}},
    )
    mock_convert_time = mocker.patch.object(Time, "convert_year_jday_to_date", return_value=datetime(2014, 1, 20))
    mock_filter_results = mocker.patch.object(em, "_filter_results", return_value=[{"dry_yield": 4, "field_size": 2}])
    time_filter = {
        "name": "Time Filter",
        "description": "Collects the date a year before the simulation ended, to be used as a cutoff for deciding "
        "which crop yields and nutrient applications to estimate emissions for.",
        "filters": ["Time.(day|calendar_year)"],
        "slice_start": -365,
        "slice_end": -364,
    }

    expected = {
        "Homegrown Feeds": [{"dry_yield": 4, "field_size": 2, "total_dry_yield": 8}],
        "Fertilizer Applications": [{"dry_yield": 4, "field_size": 2, "total_dry_yield": 8}],
        "Manure Applications": [{"dry_yield": 4, "field_size": 2, "total_dry_yield": 8}],
        "Manure Requests": [{"dry_yield": 4, "field_size": 2, "total_dry_yield": 8}],
    }
    observed = em._gather_homegrown_feeds_and_fertilizer_apps()

    assert observed == expected
    mock_convert_time.assert_called_once_with(2014, 20)
    mock_filter_variable.assert_called_once_with(time_filter)
    assert mock_filter_results.call_count == 4
    mock_filter_results.assert_has_calls(
        [
            mocker.call(
                {
                    "name": "Homegrown Feeds",
                    "description": "Collects all crop harvests that occurred in the simulation.",
                    "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
                    "variables": [".*"],
                    "date_fields": ("harvest_year", "harvest_day"),
                },
                datetime(2014, 1, 20),
                "harvest_year",
                "harvest_day",
            ),
            mocker.call(
                {
                    "name": "Fertilizer Applications",
                    "description": "Collects all synthetic fertilizer applications that occurred in the simulation.",
                    "filters": ["Field._record_fertilizer_application\\.fertilizer_application\\.field='.*'"],
                    "variables": [".*"],
                    "date_fields": ("year", "day"),
                },
                datetime(2014, 1, 20),
                "year",
                "day",
            ),
            mocker.call(
                {
                    "name": "Manure Applications",
                    "description": "Collects all manure applications that occurred in the simulation.",
                    "filters": ["Field._record_manure_application\\.manure_application\\.field='.*'"],
                    "variables": [".*"],
                    "date_fields": ("year", "day"),
                },
                datetime(2014, 1, 20),
                "year",
                "day",
            ),
            mocker.call(
                {
                    "name": "Manure Requests",
                    "description": "Collects all manure requests that occurred in the simulation.",
                    "filters": ["Field._record_manure_application\\.manure_request\\.field='.*'"],
                    "variables": [".*"],
                    "date_fields": ("year", "day"),
                },
                datetime(2014, 1, 20),
                "year",
                "day",
            ),
        ]
    )


def test_gather_ration_feed_totals(mocker: MockerFixture) -> None:
    """
    Test that the totals of feeds from rations given to animals in the last 365 days of the simulation are correct.
    """
    em = EmissionsEstimator()
    mock_filter = mocker.patch.object(em.om, "filter_variables_pool", return_value={"test": {"values": [2, 3, 4]}})
    expected = {"test": 9.0}
    observed = em._gather_ration_feed_totals()
    assert observed == expected
    mock_filter.assert_called_once_with(
        {
            "name": "Feed Ration Totals",
            "description": "Gathers the amounts of purchased feeds fed to animals in the last year of the simulation.",
            "filters": ["AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals.*"],
            "variables": [r"^\d+$"],
            "slice_start": -365,
        }
    )


def test_transform_outputs_to_list_of_dicts() -> None:
    """Test that the function transform data to correct list of dicts."""
    em = EmissionsEstimator()
    expected = [{"one": 1, "two": 4}, {"one": 2, "two": 5}, {"one": 3, "two": 6}]
    data = {"one": {"values": [1, 2, 3]}, "two": {"values": [4, 5, 6]}}
    observed = em._transform_outputs_to_list_of_dicts(data)
    assert observed == expected


def test_transform_outputs_to_list_of_dicts_length_unmatched(mocker: MockerFixture) -> None:
    """Test that the function transform data to correct list of dicts with unmatched list length."""
    em = EmissionsEstimator()
    mock_add_error = mocker.patch.object(em.om, "add_error")
    expected = [{"one": 1, "two": 4}, {"one": 2, "two": 5}, {"one": 3, "two": 6}]
    data = {"one": {"values": [1, 2, 3]}, "two": {"values": [4, 5, 6, 9]}}
    observed = em._transform_outputs_to_list_of_dicts(data)
    assert observed == expected
    mock_add_error.assert_called_once_with(
        "Found unequal lengths of data while processing simulation outputs for emissions estimation.",
        "Ignoring extraneous data.",
        {"class": "EmissionsEstimator", "function": "_transform_outputs_to_list_of_dicts"},
    )


@pytest.mark.parametrize(
    "purchased_feeds,expected",
    [
        ({"100": 300.0, "random": 500.0, "not in list": 50.0}, {"100": 100.0, "random": 500.0, "not in list": 50.0}),
        ({"100": 100.0, "random": 500.0, "not in list": 50.0}, {"100": 0.0, "random": 500.0, "not in list": 50.0}),
    ],
)
def test_calculate_actual_purchased_feeds(
    purchased_feeds: dict[str, float], expected: dict[str, float], mocker: MockerFixture
) -> None:
    """Tests that the amount of actual purchased feeds were calculated correctly."""
    em = EmissionsEstimator()
    homegrown_feeds = [
        {"crop": CropSpecies.CORN_SILAGE, "total_dry_yield": 1200, "dry_matter_content": 0.35},
        {"crop": CropSpecies.ALFALFA_HAY, "total_dry_yield": 800, "dry_matter_content": 0.9},
    ]

    mock_totals = mocker.patch.object(
        em, "_calculate_total_homegrown_feed_amounts_by_crop_type", return_value={CropSpecies.ALFALFA_HAY: 200}
    )

    observed = em._calculate_actual_purchased_feeds(homegrown_feeds, purchased_feeds)
    assert observed == expected

    mock_totals.assert_called_once_with(homegrown_feeds)


def test_calculate_total_homegrown_feed_amounts_by_crop_type(mocker: MockerFixture) -> None:
    """Tests that the amount of homegrown feeds for all the crop types were calculated correctly."""
    em = EmissionsEstimator()
    homegrown_feeds = [
        {"crop": CropSpecies.CORN_SILAGE, "total_dry_yield": 1200, "dry_matter_content": 0.35},
        {"crop": CropSpecies.ALFALFA_HAY, "total_dry_yield": 800, "dry_matter_content": 0.9},
    ]

    mock_add = mocker.patch.object(OutputManager, "add_variable")
    expected = {
        CropSpecies.ALFALFA_HAY: 800.0,
        CropSpecies.ALFALFA_SILAGE: 0.0,
        CropSpecies.ALFALFA_BALEAGE: 0.0,
        CropSpecies.CEREAL_RYE_HAY: 0.0,
        CropSpecies.CEREAL_RYE_GRAIN: 0.0,
        CropSpecies.CEREAL_RYE_SILAGE: 0.0,
        CropSpecies.CEREAL_RYE_BALEAGE: 0.0,
        CropSpecies.CORN_GRAIN: 0.0,
        CropSpecies.CORN_SILAGE: 1200.0,
        CropSpecies.SOYBEAN_HAY: 0.0,
        CropSpecies.SOYBEAN_GRAIN: 0.0,
        CropSpecies.TALL_FESCUE_HAY: 0.0,
        CropSpecies.TALL_FESCUE_SILAGE: 0.0,
        CropSpecies.TALL_FESCUE_BALEAGE: 0.0,
        CropSpecies.TRITICALE_HAY: 0.0,
        CropSpecies.TRITICALE_GRAIN: 0.0,
        CropSpecies.TRITICALE_SILAGE: 0.0,
        CropSpecies.TRITICALE_BALEAGE: 0.0,
        CropSpecies.WINTER_WHEAT_HAY: 0.0,
        CropSpecies.WINTER_WHEAT_GRAIN: 0.0,
        CropSpecies.WINTER_WHEAT_SILAGE: 0.0,
        CropSpecies.WINTER_WHEAT_BALEAGE: 0.0,
    }

    observed = em._calculate_total_homegrown_feed_amounts_by_crop_type(homegrown_feeds)
    assert observed == expected

    mock_add.assert_called_once_with(
        "homegrown_feed_totals",
        expected,
        {
            "class": "EmissionsEstimator",
            "function": "_calculate_total_homegrown_feed_amounts_by_crop_type",
            "units": MeasurementUnits.KILOGRAMS,
        },
    )


def test_calculate_actual_purchased_feed_emissions(mocker: MockerFixture) -> None:
    """Test the amount of purchased feed emissions with no errors."""
    em = EmissionsEstimator()
    mock_get_data = mocker.patch.object(em.im, "get_data", side_effect=[94545, {"emission1": 1.0}, {"emission2": 2.0}])
    mock_get_feed_data = mocker.patch.object(
        em, "_get_feed_emissions_data", return_value={"100": 26.3, "total_dry_yield": 1200, "dry_matter_content": 0.35}
    )

    expected = ({"100": 263.0}, {"100": 263.0})
    observed = em._calculate_actual_purchased_feed_emissions({"100": 10})
    assert observed == expected

    calls = [
        call(94545, {"emission1": 1.0}),
        call(94545, {"emission2": 2.0}),
    ]
    mock_get_feed_data.assert_has_calls(calls)
    calls = [
        call("config.FIPS_county_code"),
        call("purchased_feeds_emissions"),
        call("purchased_feed_land_use_change_emissions"),
    ]
    mock_get_data.assert_has_calls(calls)


@pytest.mark.parametrize(
    "msg_name,message,emissions",
    [
        (
            "Missing Purchased Feed Emissions",
            "Missing data for RuFaS feed 100, omitting from purchased feed emissions estimation.",
            [{"3": 100.0, "random": 500.0, "not in list": 50.0}, {"100": 100.0, "random": 500.0, "not in list": 50.0}],
        ),
        (
            "Missing Land Use Change Purchased Feed Emissions",
            "Missing data for RuFaS feed 100, omitting from land use change purchased feed emissions estimation.",
            [{"100": 100.0, "random": 500.0, "not in list": 50.0}, {"3": 100.0, "random": 500.0, "not in list": 50.0}],
        ),
    ],
)
def test_calculate_actual_purchased_feed_emissions_no_key(
    msg_name: str, message: str, emissions: list[dict[str, float]], mocker: MockerFixture
) -> None:
    """Test the amount of purchased feed emissions with key errors."""
    em = EmissionsEstimator()
    mock_add = mocker.patch.object(OutputManager, "add_warning")
    mock_get_data = mocker.patch.object(em.im, "get_data", side_effect=[94545, {"emission1": 1.0}, {"emission2": 2.0}])
    mock_get_feed_data = mocker.patch.object(em, "_get_feed_emissions_data", side_effect=emissions)

    em._calculate_actual_purchased_feed_emissions({"100": 10})
    calls = [
        call(94545, {"emission1": 1.0}),
        call(94545, {"emission2": 2.0}),
    ]
    mock_get_feed_data.assert_has_calls(calls)
    calls = [
        call("config.FIPS_county_code"),
        call("purchased_feeds_emissions"),
        call("purchased_feed_land_use_change_emissions"),
    ]
    mock_get_data.assert_has_calls(calls)
    info_map = {
        "class": "EmissionsEstimator",
        "function": "_calculate_actual_purchased_feed_emissions",
    }
    mock_add.assert_called_once_with(msg_name, message, info_map)
