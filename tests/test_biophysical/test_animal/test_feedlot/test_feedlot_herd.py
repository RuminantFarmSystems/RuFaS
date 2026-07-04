"""Tests for feedlot herd and pen infrastructure."""

import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen


def _make_minimal_pen(mocker: MockerFixture) -> Pen:
    """Build a minimal feedlot Pen, patching bedding init to avoid InputManager dependency."""
    mocker.patch.object(Pen, "_initialize_beddings")
    return Pen(
        pen_id=10,
        pen_name="Feedlot Pen A",
        vertical_dist_to_milking_parlor=0.0,
        horizontal_dist_to_milking_parlor=0.0,
        number_of_stalls=100,
        housing_type="Open_Lot",
        pen_type="open_lot",
        animal_combination=AnimalCombination.FEEDLOT_FINISHING,
        max_stocking_density=1.0,
        minutes_away_for_milking=0,
        first_parlor_processor=None,
        parlor_stream_name=None,
        manure_streams=[],
    )


@pytest.mark.unit
def test_pen_has_mud_condition_attribute(mocker: MockerFixture) -> None:
    """Pen must expose a mud_condition attribute."""
    pen = _make_minimal_pen(mocker)
    assert hasattr(pen, "mud_condition")


@pytest.mark.unit
def test_pen_mud_condition_defaults_to_none(mocker: MockerFixture) -> None:
    """Pen.mud_condition must default to 'none' when not specified."""
    pen = _make_minimal_pen(mocker)
    assert pen.mud_condition == "none"


@pytest.mark.unit
def test_herd_manager_feedlot_animals_in_animals_by_type() -> None:
    """animals_by_type must include FEEDLOT_STEER and FEEDLOT_HEIFER keys."""
    hm: HerdManager = HerdManager.__new__(HerdManager)
    hm.calves = []
    hm.heiferIs = []
    hm.heiferIIs = []
    hm.heiferIIIs = []
    hm.cows = []
    hm.feedlot_animals = []
    hm.beef_cows = []
    hm.beef_replacement_heifers = []
    hm.beef_calves = []
    hm.beef_bulls = []

    result = hm.animals_by_type
    assert AnimalType.FEEDLOT_STEER in result
    assert AnimalType.FEEDLOT_HEIFER in result


@pytest.mark.unit
def test_herd_manager_animals_by_type_steer_heifer_filtered_separately() -> None:
    """animals_by_type must filter steers and heifers into separate cohort lists.

    FEEDLOT_STEER must contain only steer animals; FEEDLOT_HEIFER only heifers.
    The two lists must not be identical (i.e. they are separate filtered views).
    """
    hm: HerdManager = HerdManager.__new__(HerdManager)
    hm.calves = []
    hm.heiferIs = []
    hm.heiferIIs = []
    hm.heiferIIIs = []
    hm.cows = []
    hm.beef_cows = []
    hm.beef_replacement_heifers = []
    hm.beef_calves = []
    hm.beef_bulls = []

    steer = MagicMock()
    steer.animal_type = AnimalType.FEEDLOT_STEER
    heifer = MagicMock()
    heifer.animal_type = AnimalType.FEEDLOT_HEIFER
    hm.feedlot_animals = [steer, heifer]

    result = hm.animals_by_type
    assert result[AnimalType.FEEDLOT_STEER] == [steer]
    assert result[AnimalType.FEEDLOT_HEIFER] == [heifer]
    assert result[AnimalType.FEEDLOT_STEER] is not result[AnimalType.FEEDLOT_HEIFER]


@pytest.mark.unit
def test_reporter_report_feedlot_performance_is_callable() -> None:
    """AnimalModuleReporter must expose a callable report_feedlot_performance classmethod."""
    assert hasattr(AnimalModuleReporter, "report_feedlot_performance")
    assert callable(AnimalModuleReporter.report_feedlot_performance)


@pytest.mark.unit
def test_herd_factory_has_feedlot_animals_class_attr() -> None:
    """HerdFactory must expose a feedlot_animals class-level list attribute."""
    assert hasattr(HerdFactory, "feedlot_animals")
    assert isinstance(HerdFactory.feedlot_animals, list)


@pytest.mark.unit
def test_herd_factory_initialize_feedlot_herd_creates_correct_count(mocker: MockerFixture) -> None:
    """_initialize_feedlot_herd must create num_steers + num_heifers Animal objects."""
    factory: HerdFactory = HerdFactory.__new__(HerdFactory)
    factory.im = mocker.MagicMock()
    factory.im.get_data.return_value = {  # type: ignore[attr-defined]
        "num_steers": 2,
        "num_heifers": 1,
        "entry_weight": 320.0,
        "mature_body_weight": 600.0,
        "breed": "AN",
        "days_on_feed": 0,
    }
    factory.time = mocker.MagicMock()
    factory.time.simulation_day = 0  # type: ignore[misc]

    mock_animal_cls = mocker.patch("RUFAS.biophysical.animal.herd_factory.Animal")
    mock_animal_cls.side_effect = [mocker.MagicMock() for _ in range(3)]

    result = factory._initialize_feedlot_herd()

    assert len(result) == 3
    assert mock_animal_cls.call_count == 3


@pytest.mark.unit
def test_herd_factory_initialize_feedlot_herd_empty_on_missing_config(mocker: MockerFixture) -> None:
    """_initialize_feedlot_herd must return [] when feedlot config key is absent."""
    factory: HerdFactory = HerdFactory.__new__(HerdFactory)
    factory.im = mocker.MagicMock()
    factory.im.get_data.side_effect = KeyError("no feedlot key")  # type: ignore[attr-defined]
    factory.time = mocker.MagicMock()

    result = factory._initialize_feedlot_herd()

    assert result == []


@pytest.mark.unit
def test_herd_factory_initialize_feedlot_herd_empty_on_non_dict_config(mocker: MockerFixture) -> None:
    """_initialize_feedlot_herd must return [] when feedlot config is not a dict.

    Verifies the isinstance guard: a truthy non-dict value (e.g. a list) must
    not propagate to feedlot_cfg.get() and must instead return an empty list.
    """
    factory: HerdFactory = HerdFactory.__new__(HerdFactory)
    factory.im = mocker.MagicMock()
    factory.im.get_data.return_value = ["not", "a", "dict"]  # type: ignore[attr-defined]
    factory.time = mocker.MagicMock()

    result = factory._initialize_feedlot_herd()

    assert result == []
