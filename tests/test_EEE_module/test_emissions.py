from datetime import datetime
from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.EEE.emissions import EmissionsEstimator
from RUFAS.routines.field.crop.crop_enum import CropSpecies
from RUFAS.time import Time


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


def test_gather_homegrown_feeds_and_fertilizer_apps(mocker: MockerFixture):
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
    mock_filter.assert_called_once_with({
        "name": "Feed Ration Totals",
        "description": "Gathers the amounts of purchased feeds fed to animals in the last year of the simulation.",
        "filters": ["AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals.*"],
        "variables": [r"^\d+$"],
        "slice_start": -365,
    })


def test_transform_outputs_to_list_of_dicts() -> None:
    """Test that the function transform data to correct list of dicts."""
    em = EmissionsEstimator()
    expected = [{'one': 1, 'two': 4}, {'one': 2, 'two': 5}, {'one': 3, 'two': 6}]
    data = {'one': {'values': [1, 2, 3]}, 'two': {'values': [4, 5, 6]}}
    observed = em._transform_outputs_to_list_of_dicts(data)
    assert observed == expected


def test_transform_outputs_to_list_of_dicts_length_unmatched(mocker: MockerFixture) -> None:
    """Test that the function transform data to correct list of dicts with unmatched list length."""
    em = EmissionsEstimator()
    mock_add_error = mocker.patch.object(em.om, "add_error")
    expected = [{'one': 1, 'two': 4}, {'one': 2, 'two': 5}, {'one': 3, 'two': 6}]
    data = {'one': {'values': [1, 2, 3]}, 'two': {'values': [4, 5, 6, 9]}}
    observed = em._transform_outputs_to_list_of_dicts(data)
    assert observed == expected
    mock_add_error.assert_called_once_with(
        "Found unequal lengths of data while processing simulation outputs for emissions estimation.",
        "Ignoring extraneous data.",
        {"class": "EmissionsEstimator", "function": "_transform_outputs_to_list_of_dicts"}
    )

def test_calculate_actual_purchased_feeds(mocker: MockerFixture) -> None:
    em = EmissionsEstimator()
    homegrown_feeds = [
        {"feed_name": "corn_silage", "quantity": 1200, "dry_matter_content": 0.35},
        {"feed_name": "alfalfa_hay", "quantity": 800, "dry_matter_content": 0.9}
    ]

    purchased_feeds = {
        "corn_silage": 300.0,
        "soybean_meal": 500.0,
        "mineral_supplement": 50.0
    }

    mock_totals = mocker.patch.object(em, "_calculate_total_homegrown_feed_amounts_by_crop_type",
                                      return_value={CropSpecies.ALFALFA_HAY: 23.4})

    observed = em._calculate_actual_purchased_feeds(homegrown_feeds, purchased_feeds)
    print(observed)

