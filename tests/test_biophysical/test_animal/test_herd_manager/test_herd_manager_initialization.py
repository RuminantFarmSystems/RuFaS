from typing import Any
from unittest.mock import MagicMock

from RUFAS.biophysical.animal.herd_manager import HerdManager
from pytest_mock import MockerFixture

from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd_manager,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None


def test_init(mocker: MockerFixture, mock_get_data_side_effect: list[Any]) -> None:
    """Unit test for __init__()"""
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

    assert herd_manager.simulate_animals is True
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


def test_init_uses_set_ration_feeds_when_not_user_defined(mocker: MockerFixture) -> None:
    """HerdManager.__init__ should call RationManager.set_ration_feeds when is_ration_defined_by_user is False."""
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.herd_manager.InputManager")
    mock_om_cls = mocker.patch("RUFAS.biophysical.animal.herd_manager.OutputManager")
    mock_im = mock_im_cls.return_value
    _ = mock_om_cls.return_value

    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.AnimalConfig.initialize_animal_config",
        return_value=None,
    )
    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.LactationCurve.set_lactation_parameters",
        return_value=None,
    )
    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.MilkProduction.set_milk_quality",
        return_value=None,
    )

    mock_set_user_defined_rations = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.RationManager.set_user_defined_rations"
    )
    mock_set_user_defined_ration_tolerance = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.RationManager.set_user_defined_ration_tolerance"
    )
    mock_set_ration_feeds = mocker.patch("RUFAS.biophysical.animal.herd_manager.RationManager.set_ration_feeds")

    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.AdvancePurchaseAllowance",
        return_value=MagicMock(),
    )
    mock_nutrient_standard_cls = mocker.patch("RUFAS.biophysical.animal.herd_manager.NutrientStandard")
    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.Animal.set_nutrient_standard",
        return_value=None,
    )

    mocker.patch.object(HerdManager, "initialize_pens", return_value=None)
    mocker.patch.object(HerdManager, "allocate_animals_to_pens", return_value=None)
    mocker.patch.object(HerdManager, "initialize_nutrient_requirements", return_value=None)
    mocker.patch.object(HerdManager, "_print_animal_num_warnings", return_value=None)
    mocker.patch.object(HerdManager, "set_milk_type_in_calf_ration_manager", return_value=None)

    config_data: dict[str, Any] = {
        "simulate_animals": False,
        "nutrient_standard": {"dummy": "ns"},
    }

    animal_data: dict[str, Any] = {
        "herd_information": {"herd_num": 123},
        "housing": "barn",
        "pasture_concentrate": 0,
        "ration": {"formulation_interval": 7, "maximum_ration_reformulation_attempts": 250},
        "pen_information": [],
    }

    feed_data = {"some": "feed-config"}
    allowances_data = [{"purchased_feed": 1}, {"purchased_feed": 2}, {"purchased_feed": 3}]

    def get_data_side_effect(key: str) -> Any:
        if key == "config":
            return config_data
        if key == "animal":
            return animal_data
        if key == "feed":
            return feed_data
        if key == "feed.allowances":
            return allowances_data
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    weather = MagicMock()
    time = MagicMock()
    time.simulation_day = 0
    available_feeds: list[Any] = []

    herd_manager = HerdManager(
        weather=weather,
        time=time,
        is_ration_defined_by_user=False,
        available_feeds=available_feeds,
    )

    mock_set_ration_feeds.assert_called_once_with(feed_data)
    mock_set_user_defined_rations.assert_not_called()
    mock_set_user_defined_ration_tolerance.assert_not_called()

    mock_nutrient_standard_cls.assert_called_once_with(config_data["nutrient_standard"])
    assert herd_manager.simulate_animals is False
