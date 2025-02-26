import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.handler import HandlerConfig
from RUFAS.biophysical.manure.parlor_cleaning import ParlorCleaningHandler


@pytest.fixture
def handler(mocker: MockerFixture) -> ParlorCleaningHandler:
    """Default handler instance."""
    mock_manure_handler_config = mocker.MagicMock(auto_spec=HandlerConfig)
    return ParlorCleaningHandler("handler_name", True, mock_manure_handler_config)


@pytest.mark.parametrize(
    "num_animals,expected",
    [(1, 30), (5, 150), (10, 300)]
)
def test_determine_fresh_water_volume_used_for_milking(num_animals: int, expected: float,
                                                       handler: ParlorCleaningHandler) -> None:
    """Tests the calculation of fresh water used for milking."""
    assert handler.determine_fresh_water_volume_used_for_milking(num_animals) == expected


def test_determine_cleaning_water_volume_in_main_barn