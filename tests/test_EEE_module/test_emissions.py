from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.EEE.emissions import EmissionsEstimator


@pytest.mark.parametrize(
    "homegrown_feeds",
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
def test_estimate_emissions(homegrown_feeds: list[dict[str, Any]], mocker: MockerFixture) -> None:
    """Tests the estimation routines are called correctly."""
    em = EmissionsEstimator()
    mock_gather = mocker.patch.object(em, "_gather_homegrown_feeds_and_fertilizer_apps", return_value=homegrown_feeds)
    mock_purchase = mocker.patch.object(em, "_calculate_purchased_feed_emissions")
    mock_homegrown = mocker.patch.object(em, "_calculate_homegrown_feed_emissions")

    em.estimate_emissions()
    mock_gather.assert_called_once()
    mock_purchase.assert_called_once_with(1)
    mock_homegrown.assert_called_once_with(1, 2, 3, 4)


@pytest.mark.parametrize(
    "homegrown_feeds,purchased_feeds,actual_purchased_feeds",
    [
        (
            [{"feed1": 5, "feed2": 2.6}, {"feed3": 9.24, "feed4": 7.7}],
            {"feed5": 5.3, "feed6": 7.6},
            {"feed7": 5.6, "feed8": 7.95},
        )
    ],
)
def test_calculate_purchased_feed_emissions(
    homegrown_feeds: list[dict[str, Any]],
    purchased_feeds: dict[str, float],
    actual_purchased_feeds: dict[str, float],
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of purchased feed emissions."""
    em = EmissionsEstimator()
    mock_add = mocker.patch.object(OutputManager, "add_variable")
    mock_gather_feeds = mocker.patch.object(em, "_gather_ration_feed_totals", return_value=purchased_feeds)
    mock_calc_actual = mocker.patch.object(em, "_calculate_actual_purchased_feeds", return_value=actual_purchased_feeds)
