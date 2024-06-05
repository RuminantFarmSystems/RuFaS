import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.animal.purchased_feed_emissions_estimator import PurchasedFeedEmissionsEstimator


def test_purchased_feed_emissions_estimator(mocker: MockerFixture) -> None:
    """Tests that PurchasedFeedEmissionsEstimator is created correctly."""
    get_data = mocker.patch("RUFAS.routines.animal.purchased_feed_emissions_estimator.im.get_data")
    add_var = mocker.patch("RUFAS.routines.animal.purchased_feed_emissions_estimator.om.add_variable")
    setup_emissions = mocker.patch.object(PurchasedFeedEmissionsEstimator, "_setup_feed_emissions")
    expected_get_data_calls = [
        mocker.call("config.FIPS_county_code"),
        mocker.call("purchased_feeds_emissions"),
        mocker.call("purchased_feed_land_use_change_emissions"),
    ]

    estimator = PurchasedFeedEmissionsEstimator()

    get_data.assert_has_calls(expected_get_data_calls)
    assert add_var.call_count == 3
    assert setup_emissions.call_count == 2
    assert estimator.missing_purchased_feed_ids == []
    assert estimator.missing_land_use_change_feed_ids == []


def test_create_daily_purchased_feed_emissions_report(mocker: MockerFixture) -> None:
    """Tests that the daily report of purchased feed emissions totals is calculated correctly."""
    mock_feed_totals = {"dry_matter_intake_total": 100.0, "byproducts_total": 20.0, "1": 20.0, "2": 15.0, "3": 10.0}
    add_warning = mocker.patch("RUFAS.routines.animal.purchased_feed_emissions_estimator.om.add_warning")
    mocker.patch(
        "RUFAS.routines.animal.purchased_feed_emissions_estimator.PurchasedFeedEmissionsEstimator.__init__",
        return_value=None,
    )
    mock_estimator = PurchasedFeedEmissionsEstimator()
    mock_estimator.missing_purchased_feed_ids = ["2"]
    mock_estimator.purchased_feed_emissions = {"1": 0.15}
    expected_emissions_report = {"1": 3.0, "feed_emissions_total": 3.0}
    expected_warning_call = mocker.call(
        "Missing Purchased Feed Emissions",
        "Missing data for RuFaS feed 3, omitting from purchased feed emissions estimation.",
        {"class": "PurchasedFeedEmissionsEstimator", "function": "create_daily_purchased_feed_emissions_report"},
    )

    actual = mock_estimator.create_daily_purchased_feed_emissions_report(mock_feed_totals)

    assert actual == expected_emissions_report
    add_warning.assert_has_calls([expected_warning_call])
    assert mock_estimator.missing_purchased_feed_ids == ["2", "3"]


@pytest.mark.parametrize(
    "code,expected",
    [
        (1000, {"1": 0.3, "2": 1.33, "3": 0.6}),
        (1001, {"1": 0.4, "2": 2.33, "3": 0.7}),
        (1002, {"1": 0.5, "2": 3.33, "3": 0.8}),
    ],
)
def test_setup_feed_emissions(mocker: MockerFixture, code: int, expected: dict[str, float]) -> None:
    """Tests that feed emissions data is gathered and selected correctly."""
    mock_data = {"county_code": [1000, 1001, 1002], "1": [0.3, 0.4, 0.5], "2": [1.33, 2.33, 3.33], "3": [0.6, 0.7, 0.8]}
    mocker.patch(
        "RUFAS.routines.animal.purchased_feed_emissions_estimator.PurchasedFeedEmissionsEstimator.__init__",
        return_value=None,
    )
    mock_estimator = PurchasedFeedEmissionsEstimator()
    mock_estimator.FIPS_county_code = code

    actual = mock_estimator._setup_feed_emissions(mock_data)

    assert actual == expected
