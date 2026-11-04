import pytest
from pytest_mock import MockerFixture

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.EEE.energy import EnergyEstimator
from RUFAS.output_manager import OutputManager


def test_eee_manager_init() -> None:
    """Test initialization of EEEManager class."""
    assert EEEManager() is not None


@pytest.mark.parametrize(
    "simulate_animals,simulate_feed,simulate_fields,simulate_manure,expected_log_count,"
    "expect_emissions,expect_energy",
    [
        (True, True, True, True, 4, True, True),
        (False, True, True, True, 4, True, True),
        (True, False, True, True, 4, True, True),
        (True, True, True, False, 4, True, True),
        (True, True, False, True, 1, False, False),
        (False, False, False, False, 1, False, False),
    ],
)
def test_estimate_all(
    mocker: MockerFixture,
    simulate_animals: bool,
    simulate_feed: bool,
    simulate_fields: bool,
    simulate_manure: bool,
    expected_log_count: int,
    expect_emissions: bool,
    expect_energy: bool,
) -> None:
    """Test estimate_all runs emissions and energy only when fields are simulated."""
    om = OutputManager()
    mock_om_add_log = mocker.patch.object(om, "add_log")
    mock_emissions_init = mocker.patch("RUFAS.EEE.emissions.EmissionsEstimator.__init__", return_value=None)
    mock_estimate_emissions = mocker.patch("RUFAS.EEE.emissions.EmissionsEstimator.estimate_farmgrown_feed_emissions")
    mock_estimate_energy = mocker.patch.object(EnergyEstimator, "estimate_all")

    EEEManager.estimate_all(
        simulate_animals=simulate_animals,
        simulate_feed=simulate_feed,
        simulate_fields=simulate_fields,
        simulate_manure=simulate_manure,
    )

    assert mock_om_add_log.call_count == expected_log_count

    if expect_emissions:
        mock_emissions_init.assert_called_once_with(
            simulate_animals=simulate_animals,
            simulate_feed=simulate_feed,
            simulate_fields=simulate_fields,
            simulate_manure=simulate_manure,
        )
        mock_estimate_emissions.assert_called_once_with()
    else:
        mock_emissions_init.assert_not_called()
        mock_estimate_emissions.assert_not_called()

    if expect_energy:
        mock_estimate_energy.assert_called_once_with(
            simulate_animals=simulate_animals,
            simulate_feed=simulate_feed,
            simulate_fields=simulate_fields,
            simulate_manure=simulate_manure,
        )
    else:
        mock_estimate_energy.assert_not_called()
