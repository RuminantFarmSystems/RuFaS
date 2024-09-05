from typing import Generator, Any

import pytest
from mock.mock import MagicMock
from pytest_mock import MockerFixture

from RUFAS.routines.EEE.emissions import EmissionsEstimator


def test_estimate_emissions(mocker: MockerFixture) -> None:
    em = EmissionsEstimator()
    mock_gather = mocker.patch.object(em, "_gather_homegrown_feeds_and_fertilizer_apps", return_value=(1, 2, 3, 4))
    mock_purchase = mocker.patch.object(em, "_calculate_purchased_feed_emissions")
    mock_homegrown = mocker.patch.object(em, "_calculate_homegrown_feed_emissions")

    em.estimate_emissions()
    mock_gather.assert_called_once()
    mock_purchase.assert_called_once_with(1)
    mock_homegrown.assert_called_once_with(1, 2, 3, 4)
