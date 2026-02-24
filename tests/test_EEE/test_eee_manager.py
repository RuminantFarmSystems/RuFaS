from pytest_mock import MockerFixture

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.EEE.energy import EnergyEstimator
from RUFAS.output_manager import OutputManager


def test_eee_manager_init() -> None:
    """Test initialization of EEEManager class."""
    assert EEEManager() is not None


def test_estimate_all(mocker: MockerFixture) -> None:
    """Test estimate_all method."""
    om = OutputManager()
    mock_om_add_log = mocker.patch.object(om, "add_log")
    mocker.patch("RUFAS.EEE.emissions.EmissionsEstimator.__init__", return_value=None)
    mock_estimate_emissions = mocker.patch("RUFAS.EEE.emissions.EmissionsEstimator.estimate_farmgrown_feed_emissions")
    mock_estimate_energy = mocker.patch.object(EnergyEstimator, "estimate_all")

    EEEManager.estimate_all()

    assert mock_om_add_log.call_count == 4
    mock_estimate_emissions.assert_called_once_with()
    mock_estimate_energy.assert_called_once_with()
