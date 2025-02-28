from typing import Any

from pytest_mock import MockerFixture

from tests.animal_module_tests.herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd_manager
)

assert config_json
assert animal_json
assert manure_management_json
assert feed_json
assert mock_get_data_side_effect


def test_init(mocker: MockerFixture, mock_get_data_side_effect: list[Any]) -> None:
    herd_manager, mocking_methods = mock_herd_manager(
        calves=[],
        heiferIs=[],
        heiferIIs=[],
        heiferIIIs=[],
        cows=[],
        replacement=[],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )

    assert herd_manager.simulate_animals == True
    assert herd_manager.calves == []
    assert herd_manager.heiferIs == []
    assert herd_manager.heiferIIs == []
    assert herd_manager.heiferIIIs == []
    assert herd_manager.cows == []
    assert herd_manager.replacement_market == []
    assert herd_manager.heifers_sold == []
    assert herd_manager.cows_culled == []
    assert herd_manager.animal_to_pen_id_map == {}

    assert herd_manager.housing == "barn"
    assert herd_manager.pasture_concentrate == 0

    for key, mock_method in mocking_methods.items():
        if not key == "mock_get_data":
            mock_method.assert_called_once()