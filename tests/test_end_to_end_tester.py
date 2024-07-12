import pytest
from pytest_mock import MockerFixture
from RUFAS.end_to_end_tester import EndToEndTester


@pytest.fixture
def tester(mocker: MockerFixture) -> EndToEndTester:
    """Fixture for an end-to-end tester."""
    mocker.patch.object(EndToEndTester, "__init__", return_value=None)
    return EndToEndTester()


def test_run_end_to_end_testing(tester: EndToEndTester, mocker: MockerFixture) -> None:
    """Tests the main routine for end to end testing."""
    simulate = mocker.patch.object(tester, "simulate")
    compare = mocker.patch.object(tester, "compare_results")

    tester.run_end_to_end_testing()

    simulate.assert_called_once()
    compare.assert_called_once()
