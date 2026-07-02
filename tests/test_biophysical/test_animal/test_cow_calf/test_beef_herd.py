"""Tests for beef cow-calf herd cohort lists in HerdFactory and HerdManager (Tasks 7.1 + 7.2)."""

import math
from collections.abc import Mapping
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_herd_updates import DailyHerdUpdates
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.nutrients import NutrientsInputs
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.data_validator import DataValidator
from RUFAS.input_manager import InputManager
from RUFAS.rufas_time import RufasTime
from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    animal_json,
    config_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd_manager as _make_herd_manager,
)

assert animal_json is not None
assert config_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None


@pytest.mark.unit
def test_herd_factory_has_beef_cow_calf_animals_class_attr() -> None:
    """HerdFactory must expose a beef_cow_calf_animals class-level list attribute.

    Verifies Task 7.1: the factory uses the same class-attr staging pattern as
    feedlot_animals so HerdManager can iterate the list at init time.
    """
    assert hasattr(HerdFactory, "beef_cow_calf_animals")
    assert isinstance(HerdFactory.beef_cow_calf_animals, list)


@pytest.mark.unit
def test_animals_by_type_returns_distinct_lists() -> None:
    """BEEF_COW, BEEF_HEIFER_REPLACEMENT, BEEF_CALF, BEEF_BULL each resolve to separate list objects.

    Verifies each beef type maps to its OWN named list in HerdManager,
    never pooled into a single shared list.
    """
    hm: HerdManager = HerdManager.__new__(HerdManager)
    hm.calves = []
    hm.heiferIs = []
    hm.heiferIIs = []
    hm.heiferIIIs = []
    hm.cows = []
    hm.feedlot_animals = []

    cow = MagicMock()
    cow.animal_type = AnimalType.BEEF_COW

    heifer = MagicMock()
    heifer.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT

    calf = MagicMock()
    calf.animal_type = AnimalType.BEEF_CALF

    bull = MagicMock()
    bull.animal_type = AnimalType.BEEF_BULL

    hm.beef_cows = [cow]
    hm.beef_replacement_heifers = [heifer]
    hm.beef_calves = [calf]
    hm.beef_bulls = [bull]

    result = hm.animals_by_type

    assert AnimalType.BEEF_COW in result
    assert AnimalType.BEEF_HEIFER_REPLACEMENT in result
    assert AnimalType.BEEF_CALF in result
    assert AnimalType.BEEF_BULL in result

    assert result[AnimalType.BEEF_COW] == [cow]
    assert result[AnimalType.BEEF_HEIFER_REPLACEMENT] == [heifer]
    assert result[AnimalType.BEEF_CALF] == [calf]
    assert result[AnimalType.BEEF_BULL] == [bull]

    assert result[AnimalType.BEEF_COW] is hm.beef_cows
    assert result[AnimalType.BEEF_HEIFER_REPLACEMENT] is hm.beef_replacement_heifers
    assert result[AnimalType.BEEF_CALF] is hm.beef_calves
    assert result[AnimalType.BEEF_BULL] is hm.beef_bulls

    assert result[AnimalType.BEEF_COW] is not result[AnimalType.BEEF_HEIFER_REPLACEMENT]
    assert result[AnimalType.BEEF_COW] is not result[AnimalType.BEEF_CALF]
    assert result[AnimalType.BEEF_COW] is not result[AnimalType.BEEF_BULL]
    assert result[AnimalType.BEEF_HEIFER_REPLACEMENT] is not result[AnimalType.BEEF_CALF]
    assert result[AnimalType.BEEF_HEIFER_REPLACEMENT] is not result[AnimalType.BEEF_BULL]
    assert result[AnimalType.BEEF_CALF] is not result[AnimalType.BEEF_BULL]


@pytest.mark.unit
def test_herd_manager_beef_lists_populated_from_factory(
    mocker: MockerFixture, mock_get_data_side_effect: dict[str, object]
) -> None:
    """HerdManager.__init__ must split HerdFactory.beef_cow_calf_animals into four typed lists.

    Uses the real constructor so that changes to the split logic in __init__ are caught
    rather than testing a manually replicated copy of the logic.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for patching HerdFactory class attributes and post-split steps.
    mock_get_data_side_effect : dict[str, object]
        Mapping from InputManager.get_data key to its return value.
    """
    cow = MagicMock()
    cow.animal_type = AnimalType.BEEF_COW
    heifer = MagicMock()
    heifer.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    calf = MagicMock()
    calf.animal_type = AnimalType.BEEF_CALF
    bull = MagicMock()
    bull.animal_type = AnimalType.BEEF_BULL

    mocker.patch.object(HerdFactory, "beef_cow_calf_animals", [cow, heifer, calf, bull])
    # Patch post-split steps: real constructor calls these after splitting, but
    # MagicMock animals and a dairy-scenario herd would crash inside them.
    mocker.patch.object(HerdManager, "allocate_animals_to_pens")
    mocker.patch.object(HerdManager, "initialize_nutrient_requirements")

    hm, _ = _make_herd_manager(
        calves=[],
        heiferIs=[],
        heiferIIs=[],
        heiferIIIs=[],
        cows=[],
        replacement=[],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )

    assert hm.beef_cows == [cow]
    assert hm.beef_replacement_heifers == [heifer]
    assert hm.beef_calves == [calf]
    assert hm.beef_bulls == [bull]

    assert hm.beef_cows is not hm.beef_replacement_heifers
    assert hm.beef_cows is not hm.beef_calves
    assert hm.beef_cows is not hm.beef_bulls


# ---------------------------------------------------------------------------
# Task 7.2 — RED tests
# ---------------------------------------------------------------------------


def _make_herd_manager_stub(
    beef_cows: list[MagicMock] | None = None,
    beef_replacement_heifers: list[MagicMock] | None = None,
    beef_calves: list[MagicMock] | None = None,
    beef_bulls: list[MagicMock] | None = None,
) -> HerdManager:
    """Return a HerdManager instance with all list attrs pre-set (no __init__).

    Parameters
    ----------
    beef_cows : list[MagicMock] | None, optional
        Initial BEEF_COW list; defaults to empty.
    beef_replacement_heifers : list[MagicMock] | None, optional
        Initial BEEF_HEIFER_REPLACEMENT list; defaults to empty.
    beef_calves : list[MagicMock] | None, optional
        Initial BEEF_CALF list; defaults to empty.
    beef_bulls : list[MagicMock] | None, optional
        Initial BEEF_BULL list; defaults to empty.

    Returns
    -------
    HerdManager
        A minimally constructed HerdManager with all dairy and beef list attributes initialised.
    """
    hm: HerdManager = HerdManager.__new__(HerdManager)
    hm.calves = []
    hm.heiferIs = []
    hm.heiferIIs = []
    hm.heiferIIIs = []
    hm.cows = []
    hm.feedlot_animals = []
    hm.beef_cows = beef_cows if beef_cows is not None else []  # type: ignore[assignment]
    hm.beef_replacement_heifers = (
        beef_replacement_heifers if beef_replacement_heifers is not None else []  # type: ignore[assignment]
    )
    hm.beef_calves = beef_calves if beef_calves is not None else []  # type: ignore[assignment]
    hm.beef_bulls = beef_bulls if beef_bulls is not None else []  # type: ignore[assignment]
    hm.herd_reproduction_statistics = HerdReproductionStatistics()
    hm.herd_statistics = MagicMock()
    hm.herd_statistics.animals_deaths_by_stage = {}
    return hm


def _make_time_mock(simulation_day: int = 1) -> MagicMock:
    """Return a RufasTime mock with simulation_day set.

    Parameters
    ----------
    simulation_day : int, optional
        Day counter to assign to the mock.  Default 1.

    Returns
    -------
    MagicMock
        RufasTime mock with ``simulation_day`` set to the given value.
    """
    t: MagicMock = MagicMock(spec=RufasTime)
    t.simulation_day = simulation_day
    return t


def _make_animal_mock(animal_type: AnimalType, status: AnimalStatus = AnimalStatus.REMAIN) -> MagicMock:
    """Return an Animal mock whose daily_routines returns the given status.

    Parameters
    ----------
    animal_type : AnimalType
        The animal_type to assign to the mock.
    status : AnimalStatus, optional
        The ``animal_status`` to embed in the returned DailyRoutinesOutput.  Default REMAIN.

    Returns
    -------
    MagicMock
        Animal mock with ``daily_routines`` returning a DailyRoutinesOutput set to ``status``.
    """
    animal: MagicMock = MagicMock()
    animal.animal_type = animal_type
    output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
    output.animal_status = status
    animal.daily_routines.return_value = output
    return animal


@pytest.mark.unit
def test_process_daily_herd_updates_includes_beef_groups(mocker: MockerFixture) -> None:
    """_process_daily_herd_updates must call _perform_daily_routines_for_animals for all four beef lists.

    Verifies beef_cows, beef_replacement_heifers, beef_calves, and beef_bulls
    are each passed as the ``animals`` argument in a separate call.
    """
    cow = _make_animal_mock(AnimalType.BEEF_COW)
    heifer = _make_animal_mock(AnimalType.BEEF_HEIFER_REPLACEMENT)
    calf = _make_animal_mock(AnimalType.BEEF_CALF)
    bull = _make_animal_mock(AnimalType.BEEF_BULL)

    hm = _make_herd_manager_stub(
        beef_cows=[cow],
        beef_replacement_heifers=[heifer],
        beef_calves=[calf],
        beef_bulls=[bull],
    )

    empty_result: tuple[list[MagicMock], list[MagicMock], list[MagicMock], list[MagicMock], list[MagicMock]] = (
        [],
        [],
        [],
        [],
        [],
    )
    spy = mocker.patch.object(hm, "_perform_daily_routines_for_animals", return_value=empty_result)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)

    time = _make_time_mock()
    hm._process_daily_herd_updates(time)

    called_animals_args = [c.args[1] for c in spy.call_args_list]
    assert any(
        a is hm.beef_cows for a in called_animals_args
    ), "beef_cows not passed to _perform_daily_routines_for_animals"
    assert any(a is hm.beef_replacement_heifers for a in called_animals_args), "beef_replacement_heifers not passed"
    assert any(a is hm.beef_calves for a in called_animals_args), "beef_calves not passed"
    assert any(a is hm.beef_bulls for a in called_animals_args), "beef_bulls not passed"


@pytest.mark.unit
def test_beef_cow_calving_propagates_to_newborn_calves(mocker: MockerFixture) -> None:
    """REMAIN + BEEF_COW + non-None newborn_calf_config must populate daily_herd_updates.newborn_calves.

    Verifies that the beef-calving branch in _perform_daily_routines_for_animals
    captures newborns even though the cow stays REMAIN (not LIFE_STAGE_CHANGED).
    """
    cow = MagicMock()
    cow.animal_type = AnimalType.BEEF_COW
    newborn_cfg: MagicMock = MagicMock()
    output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
    output.animal_status = AnimalStatus.REMAIN
    output.newborn_calf_config = newborn_cfg
    cow.daily_routines.return_value = output

    hm = _make_herd_manager_stub(beef_cows=[cow])

    newborn_animal = MagicMock()
    newborn_animal.stillborn = False
    newborn_animal.sold = False
    mocker.patch.object(hm, "_create_newborn_calf", return_value=newborn_animal)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)

    time = _make_time_mock()
    daily_herd_updates: DailyHerdUpdates = hm._process_daily_herd_updates(time)

    assert (
        newborn_animal in daily_herd_updates.newborn_calves
    ), "Newborn calf from BEEF_COW REMAIN calving must appear in daily_herd_updates.newborn_calves"


@pytest.mark.unit
def test_process_daily_herd_updates_calls_reporter_for_beef(mocker: MockerFixture) -> None:
    """_process_daily_herd_updates must call report_cow_calf_performance once per beef animal.

    Verifies the reporter is called from HerdManager (not animal.py),
    once for each animal in the four beef lists combined.
    """
    cow = _make_animal_mock(AnimalType.BEEF_COW)
    heifer = _make_animal_mock(AnimalType.BEEF_HEIFER_REPLACEMENT)
    calf = _make_animal_mock(AnimalType.BEEF_CALF)
    bull = _make_animal_mock(AnimalType.BEEF_BULL)

    hm = _make_herd_manager_stub(
        beef_cows=[cow],
        beef_replacement_heifers=[heifer],
        beef_calves=[calf],
        beef_bulls=[bull],
    )

    reporter_spy = mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)
    time = _make_time_mock(simulation_day=5)

    hm._process_daily_herd_updates(time)

    assert (
        reporter_spy.call_count == 4
    ), f"Expected 4 reporter calls (one per beef animal), got {reporter_spy.call_count}"
    called_animals = [c.args[0] for c in reporter_spy.call_args_list]
    assert cow in called_animals
    assert heifer in called_animals
    assert calf in called_animals
    assert bull in called_animals


@pytest.mark.unit
def test_initialize_beef_cow_calf_herd_non_dict_config_returns_empty() -> None:
    """_initialize_beef_cow_calf_herd must return [] when config value is not a dict.

    Verifies the isinstance(cfg, dict) guard prevents attempts to call
    .get() on a non-dict value such as a list, int, or None.
    """
    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    hf.im = MagicMock()
    hf.time = _make_time_mock()

    bad_values: list[object] = [None, [], "string", 42]
    for bad_value in bad_values:
        hf.im.get_data.return_value = bad_value
        result = hf._initialize_beef_cow_calf_herd()
        assert result == [], f"Expected [] for config value {bad_value!r}, got {result}"


@pytest.mark.unit
def test_first_calving_heifer_newborn_captured_in_herd_updates(mocker: MockerFixture) -> None:
    """LIFE_STAGE_CHANGED from beef_replacement_heifers with non-None newborn_calf_config must populate newborn_calves.

    Verifies Fix B-1: beef_replacement_heifers is included in collect_birth_results so that
    first-calving heifers do not silently drop their newborn.
    """
    heifer = MagicMock()
    heifer.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    newborn_cfg: MagicMock = MagicMock()
    output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
    output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
    output.newborn_calf_config = newborn_cfg
    heifer.daily_routines.return_value = output

    hm = _make_herd_manager_stub(beef_replacement_heifers=[heifer])

    newborn_animal = MagicMock()
    newborn_animal.stillborn = False
    newborn_animal.sold = False
    mocker.patch.object(hm, "_create_newborn_calf", return_value=newborn_animal)
    mocker.patch.object(hm, "_update_genetic_values_at_lactation_start", return_value=None)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)

    time = _make_time_mock()
    daily_herd_updates: DailyHerdUpdates = hm._process_daily_herd_updates(time)

    assert (
        newborn_animal in daily_herd_updates.newborn_calves
    ), "Newborn from first-calving heifer (LIFE_STAGE_CHANGED) must appear in daily_herd_updates.newborn_calves"


@pytest.mark.unit
def test_herd_statistics_deaths_by_stage_includes_beef_types() -> None:
    """HerdStatistics() must initialise animals_deaths_by_stage with all four beef types at 0.

    Verifies Task 7.3: BEEF_COW, BEEF_HEIFER_REPLACEMENT, BEEF_CALF, and BEEF_BULL must
    each appear as keys so that death-count updates never KeyError.
    """
    from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics

    stats = HerdStatistics()

    assert AnimalType.BEEF_COW in stats.animals_deaths_by_stage
    assert AnimalType.BEEF_HEIFER_REPLACEMENT in stats.animals_deaths_by_stage
    assert AnimalType.BEEF_CALF in stats.animals_deaths_by_stage
    assert AnimalType.BEEF_BULL in stats.animals_deaths_by_stage

    assert stats.animals_deaths_by_stage[AnimalType.BEEF_COW] == 0
    assert stats.animals_deaths_by_stage[AnimalType.BEEF_HEIFER_REPLACEMENT] == 0
    assert stats.animals_deaths_by_stage[AnimalType.BEEF_CALF] == 0
    assert stats.animals_deaths_by_stage[AnimalType.BEEF_BULL] == 0


def _make_minimal_pen(mocker: MockerFixture, forage_quality_factor: float | None = None) -> Pen:
    """Construct a minimal Pen with bedding mocked out via InputManager.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to stub InputManager.get_data for bedding lookup.
    forage_quality_factor : float | None, optional
        If provided, passed as a constructor kwarg; omitted otherwise to exercise
        the default-1.0 path.

    Returns
    -------
    Pen
        A Pen instance built with minimal required parameters and a single bedding stream.
    """
    im = InputManager()
    mocker.patch.object(
        im,
        "get_data",
        return_value=[
            {
                "name": "bedding_1",
                "bedding_type": "sawdust",
                "bedding_mass_per_day": 1.97,
                "bedding_density": 250.0,
                "bedding_dry_matter_content": 0.9,
                "bedding_carbon_fraction": 0.0,
                "bedding_phosphorus_content": 0.0,
                "sand_removal_efficiency": 0.0,
            }
        ],
    )
    kwargs: dict[str, object] = {
        "pen_id": 1,
        "pen_name": "Test Pen",
        "vertical_dist_to_milking_parlor": 0.0,
        "horizontal_dist_to_milking_parlor": 0.0,
        "number_of_stalls": 10,
        "housing_type": "freestall",
        "pen_type": "freestall",
        "animal_combination": AnimalCombination.LAC_COW,
        "max_stocking_density": 1.0,
        "minutes_away_for_milking": 0,
        "first_parlor_processor": None,
        "parlor_stream_name": None,
        "manure_streams": [{"stream_name": "s1", "stream_proportion": 1.0, "bedding_name": "bedding_1"}],
    }
    if forage_quality_factor is not None:
        kwargs["forage_quality_factor"] = forage_quality_factor
    return Pen(**kwargs)  # type: ignore[arg-type]


@pytest.mark.unit
def test_pen_forage_quality_factor_defaults_to_one(mocker: MockerFixture) -> None:
    """Pen must have forage_quality_factor defaulting to 1.0 when not in config.

    Verifies FIX 12: forage_quality_factor from pen_data is forwarded to Pen() so
    beef simulations that set it get the correct value, while dairy runs default to 1.0.
    """
    pen_default = _make_minimal_pen(mocker)
    assert pen_default.forage_quality_factor == 1.0

    pen_custom = _make_minimal_pen(mocker, forage_quality_factor=0.8)
    assert pen_custom.forage_quality_factor == 0.8


# ---------------------------------------------------------------------------
# Task 7.4 — nutrients.py phosphorus guard verification
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_nutrients_phosphorus_requirement_set_for_beef() -> None:
    """_calculate_phosphorus_requirements sets a finite positive value for beef animals.

    Verifies Task 7.4: the void method modifies self.phosphorus_requirement in-place
    and produces a valid (finite, > 0) result for BEEF_COW without raising an error.
    No guard is needed because the existing code already produces a valid finite positive
    value via the non-cow fallback paths in the sub-calculations.
    """
    nutrients = Nutrients()
    nutrients_inputs = NutrientsInputs(
        animal_type=AnimalType.BEEF_COW,
        body_weight=550.0,
        mature_body_weight=550.0,
        daily_growth=0.0,
        days_in_pregnancy=0,
        days_in_milk=0,
        daily_milk_produced=0.0,
    )
    nutrients.set_dry_matter_intake(10.0)

    nutrients._calculate_phosphorus_requirements(nutrients_inputs)

    assert math.isfinite(nutrients.phosphorus_requirement), "phosphorus_requirement must be finite for BEEF_COW"
    assert nutrients.phosphorus_requirement > 0, "phosphorus_requirement must be positive for BEEF_COW"


@pytest.mark.unit
def test_validate_beef_cow_calf_config_rejects_nan_weight() -> None:
    """mature_cow_weight_kg of NaN must raise ValueError.

    NaN propagates silently through NRC equations; the validator must catch it
    at config-load time rather than producing nonsensical requirements at runtime.
    """
    with pytest.raises(ValueError, match="mature_cow_weight_kg"):
        DataValidator.validate_beef_cow_calf_config({"mature_cow_weight_kg": float("nan")})


@pytest.mark.unit
def test_validate_beef_cow_calf_config_rejects_zero_weaning_age() -> None:
    """weaning_age_days of 0 must raise ValueError.

    A zero weaning age would trigger weaning on day 0 before the calf is born;
    the validator guards this boundary condition.
    """
    with pytest.raises(ValueError, match="weaning_age_days"):
        DataValidator.validate_beef_cow_calf_config({"mature_cow_weight_kg": 500.0, "weaning_age_days": 0})


@pytest.mark.unit
def test_validate_beef_cow_calf_config_rejects_excessive_bull_ratio() -> None:
    """natural_service_bull_ratio above MAX_BULL_TO_COW_RATIO must raise ValueError.

    Ratios beyond the physiological maximum (defined in animal_constants) indicate
    a data-entry error; the validator surfaces this before the simulation starts.
    """
    with pytest.raises(ValueError, match="natural_service_bull_ratio"):
        DataValidator.validate_beef_cow_calf_config(
            {
                "mature_cow_weight_kg": 500.0,
                "weaning_age_days": 180,
                "breeding_season_length": 63,
                "natural_service_bull_ratio": 999,
            }
        )


@pytest.mark.unit
def test_validate_beef_cow_calf_config_accepts_valid_config() -> None:
    """A valid config that omits natural_service_bull_ratio must not raise (default=25).

    Verifies FIX 3: the validator must operate on the merged config (defaults filled in),
    not the raw user config, so omitted optional keys pass validation.
    """
    DataValidator.validate_beef_cow_calf_config(
        {
            "mature_cow_weight_kg": 500.0,
            "weaning_age_days": 180,
            "breeding_season_length": 63,
        }
    )


# ---------------------------------------------------------------------------
# Task 7.6 — None-guards and required metric fields in report_cow_calf_performance
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_report_cow_calf_performance_does_not_raise_with_none_attrs(mocker: MockerFixture) -> None:
    """report_cow_calf_performance must handle None-valued animal attributes gracefully.

    Exercises the None-guards for wean_weight and any other Optional attributes
    that may be None on non-cow beef animals (e.g. BEEF_HEIFER_REPLACEMENT) at
    initialization time. The call must not raise and must emit at least the five
    required metric variables: days_in_pregnancy, lactation_day,
    body_condition_score_9, times_calved (parity), and wean_weight.
    """
    animal: MagicMock = MagicMock()
    animal.id = 42
    animal.animal_type = MagicMock()
    animal.animal_type.value = AnimalType.BEEF_COW.value
    animal.days_in_pregnancy = 0
    animal.lactation_day = 0
    animal.body_condition_score_9 = 5.0
    animal.times_calved = 1
    animal.wean_weight = None  # None triggers the guard being tested

    add_variable_spy = mocker.patch("RUFAS.biophysical.animal.animal_module_reporter.om.add_variable")

    AnimalModuleReporter.report_cow_calf_performance(animal, simulation_day=100)

    reported_names = [call.args[0] for call in add_variable_spy.call_args_list]
    assert "beef_days_in_pregnancy" in reported_names
    assert "beef_lactation_day" in reported_names
    assert "beef_body_condition_score_9" in reported_names
    assert "beef_times_calved" in reported_names
    assert "beef_wean_weight_kg" in reported_names


@pytest.mark.unit
def test_report_cow_calf_performance_wean_weight_none_maps_to_zero(mocker: MockerFixture) -> None:
    """report_cow_calf_performance must pass 0.0 for beef_wean_weight_kg when wean_weight is None.

    Verifies the exact None-fallback value so that OutputManager receives a
    valid float, not None, when the attribute has not been set on initialization.
    """
    animal: MagicMock = MagicMock()
    animal.id = 7
    animal.animal_type = MagicMock()
    animal.animal_type.value = AnimalType.BEEF_HEIFER_REPLACEMENT.value
    animal.days_in_pregnancy = 0
    animal.lactation_day = 0
    animal.body_condition_score_9 = 4.5
    animal.times_calved = 0
    animal.wean_weight = None

    add_variable_spy = mocker.patch("RUFAS.biophysical.animal.animal_module_reporter.om.add_variable")

    AnimalModuleReporter.report_cow_calf_performance(animal, simulation_day=50)

    wean_call = next(
        (c for c in add_variable_spy.call_args_list if c.args[0] == "beef_wean_weight_kg"),
        None,
    )
    assert wean_call is not None, "beef_wean_weight_kg must be reported"
    assert wean_call.args[1] == 0.0, "None wean_weight must fall back to 0.0"


@pytest.mark.unit
def test_report_cow_calf_performance_uses_times_calved_not_calves(mocker: MockerFixture) -> None:
    """report_cow_calf_performance must log animal.times_calved (parity int), not animal.calves.

    Verifies FIX 1: beef cows track parity via times_calved (set in
    _initialize_beef_cow_calf_animal). The dairy calves property reads from
    reproduction.calves which is not initialised for beef types, causing a crash.
    This test sets animal.times_calved = 3 and asserts that the reported value is 3.
    """
    animal: MagicMock = MagicMock()
    animal.id = 10
    animal.animal_type = MagicMock()
    animal.animal_type.value = AnimalType.BEEF_COW.value
    animal.days_in_pregnancy = 150
    animal.lactation_day = 60
    animal.body_condition_score_9 = 5.5
    animal.times_calved = 3
    animal.wean_weight = None

    add_variable_spy = mocker.patch("RUFAS.biophysical.animal.animal_module_reporter.om.add_variable")

    AnimalModuleReporter.report_cow_calf_performance(animal, simulation_day=200)

    times_calved_call = next(
        (c for c in add_variable_spy.call_args_list if c.args[0] == "beef_times_calved"),
        None,
    )
    assert times_calved_call is not None, "beef_times_calved must be reported"
    assert times_calved_call.args[1] == 3, (
        "beef_times_calved must use animal.times_calved, not animal.calves — "
        "the calves property reads from the dairy reproduction object"
    )


@pytest.mark.unit
def test_beef_factory_passes_sex_field_for_cows_heifers_and_bulls(mocker: MockerFixture) -> None:
    """HerdFactory._initialize_beef_cow_calf_herd must pass sex='FEMALE' for cows/heifers and sex='MALE' for bulls.

    Verifies FIX 5: absent sex field causes random sex assignment which is biologically incorrect
    for a production herd. The factory must pass the sex key explicitly so Animal.__init__
    initialises each animal with the correct sex.
    """
    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    hf.im = MagicMock()
    hf.time = _make_time_mock()
    hf.im.get_data.return_value = {
        "num_cows": 1,
        "num_replacement_heifers": 1,
        "num_calves": 0,
        "num_bulls": 1,
        "mature_cow_weight_kg": 520.0,
        "breed": "AN",
    }

    captured_args: list[dict[str, object]] = []

    def _capture(args: Mapping[str, object], _time: RufasTime) -> MagicMock:
        captured_args.append(dict(args))
        return MagicMock()

    mocker.patch("RUFAS.biophysical.animal.herd_factory.Animal", side_effect=_capture)
    hf._initialize_beef_cow_calf_herd()

    assert len(captured_args) == 3, f"Expected 3 animals (1 cow + 1 heifer + 1 bull), got {len(captured_args)}"
    cow_args = next(a for a in captured_args if a["animal_type"] == AnimalType.BEEF_COW.value)
    heifer_args = next(a for a in captured_args if a["animal_type"] == AnimalType.BEEF_HEIFER_REPLACEMENT.value)
    bull_args = next(a for a in captured_args if a["animal_type"] == AnimalType.BEEF_BULL.value)

    assert cow_args.get("sex") == "FEMALE", "BEEF_COW must be initialised with sex='FEMALE'"
    assert heifer_args.get("sex") == "FEMALE", "BEEF_HEIFER_REPLACEMENT must be initialised with sex='FEMALE'"
    assert bull_args.get("sex") == "MALE", "BEEF_BULL must be initialised with sex='MALE'"


@pytest.mark.unit
def test_animals_by_combination_skips_beef_cow_in_beef_cow_calf_herd(mocker: MockerFixture) -> None:
    """animals_by_combination must skip BEEF_COW gracefully under BEEF_COW_CALF_HERD.

    Verifies FIX A + FIX 11 contract: beef cohort lists are included in the loop so
    pen allocation can be extended in a future PR.  Until runtime reproduction-state
    dispatch replaces the Step 1 guard (Step 7), find_animal_combination raises
    NotImplementedError for BEEF_COW — the guard catches it and skips the cow.
    Other beef types (BEEF_HEIFER_REPLACEMENT, BEEF_CALF, BEEF_BULL) must still
    appear in the output so this test also pins that beef_cows is included in the
    loop (a silent removal would cause heifer/calf/bull to vanish too).

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for patching HerdManager class attributes.
    """
    from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario

    mocker.patch.object(
        HerdManager,
        "ANIMAL_GROUPING_SCENARIO",
        new=AnimalGroupingScenario.BEEF_COW_CALF_HERD,
        create=True,
    )

    cow = MagicMock()
    cow.animal_type = AnimalType.BEEF_COW
    heifer = MagicMock()
    heifer.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    calf = MagicMock()
    calf.animal_type = AnimalType.BEEF_CALF
    bull = MagicMock()
    bull.animal_type = AnimalType.BEEF_BULL

    hm = _make_herd_manager_stub(
        beef_cows=[cow],
        beef_replacement_heifers=[heifer],
        beef_calves=[calf],
        beef_bulls=[bull],
    )

    # Must not raise — NotImplementedError for BEEF_COW is caught by the FIX A guard
    result = hm.animals_by_combination

    all_result_animals = [a for animals in result.values() for a in animals]
    assert cow not in all_result_animals, "BEEF_COW must be skipped (Step 7 dispatch not yet wired)"
    assert heifer in all_result_animals, "BEEF_HEIFER_REPLACEMENT must appear in animals_by_combination"
    assert calf in all_result_animals, "BEEF_CALF must appear in animals_by_combination"
    assert bull in all_result_animals, "BEEF_BULL must appear in animals_by_combination"


# ---------------------------------------------------------------------------
# FIX 2 + FIX 7 regression tests (PR #35 round 2)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_bull_initialized_with_unscaled_mature_body_weight(mocker: MockerFixture) -> None:
    """BEEF_BULL must receive mature_body_weight == mature_bw (not body_weight).

    Verifies FIX 2: prior code accidentally passed the scaled initial body weight
    as the mature_body_weight target, causing the bull to plateau at a fraction of
    the correct adult size.
    """
    import RUFAS.biophysical.animal.animal_constants as animal_constants

    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    hf.im = MagicMock()
    hf.time = _make_time_mock()
    mature_bw = 900.0
    hf.im.get_data.return_value = {
        "num_cows": 0,
        "num_replacement_heifers": 0,
        "num_calves": 0,
        "num_bulls": 1,
        "mature_cow_weight_kg": mature_bw,
        "breed": "AN",
    }

    captured_args: list[dict[str, object]] = []

    def _capture(args: Mapping[str, object], _time: RufasTime) -> MagicMock:
        captured_args.append(dict(args))
        return MagicMock()

    mocker.patch("RUFAS.biophysical.animal.herd_factory.Animal", side_effect=_capture)
    hf._initialize_beef_cow_calf_herd()

    assert len(captured_args) == 1
    bull_args = captured_args[0]
    assert bull_args["mature_body_weight"] == mature_bw, (
        f"BEEF_BULL mature_body_weight must be {mature_bw}, " f"got {bull_args['mature_body_weight']}"
    )
    assert bull_args["body_weight"] == mature_bw * animal_constants.BEEF_BULL_INITIAL_WEIGHT_PCT_MATURE


@pytest.mark.unit
def test_initialize_pens_forage_quality_factor_zero_preserved(mocker: MockerFixture) -> None:
    """forage_quality_factor=0.0 in pen config must be forwarded to Pen as 0.0, not 1.0.

    Verifies FIX 7: the previous ``or 1.0`` fallback collapsed explicit 0.0 to the
    default, breaking bare-ground pasture scenarios.  The None-check must treat 0.0
    as a valid user-supplied value.
    """
    mock_pen_init = mocker.patch.object(Pen, "__init__", return_value=None)

    hm: HerdManager = HerdManager.__new__(HerdManager)
    hm.all_pens = []
    hm.animal_to_pen_id_map = {}

    pen_data = [
        {
            "id": 1,
            "name": "pasture",
            "animal_combination": "BEEF_COW_CALF_PAIR",
            "vertical_dist_to_milking_parlor": 0.0,
            "horizontal_dist_to_milking_parlor": 0.0,
            "number_of_stalls": 50,
            "housing_type": "open",
            "pen_type": "pasture",
            "max_stocking_density": 1.0,
            "forage_quality_factor": 0.0,
        }
    ]

    hm.initialize_pens(pen_data)

    _, kwargs = mock_pen_init.call_args
    assert (
        kwargs["forage_quality_factor"] == 0.0
    ), "forage_quality_factor=0.0 in config must not be replaced by the 1.0 default"


@pytest.mark.unit
def test_pen_forage_quality_factor_negative_raises() -> None:
    """Pen constructor must reject forage_quality_factor < 0.0.

    0.0 is valid (complete forage failure / drought stress); negative is biologically impossible.
    The ValueError is raised before _initialize_beddings() so no InputManager mock is needed.
    """
    with pytest.raises(ValueError, match="forage_quality_factor must be a non-negative finite value"):
        Pen(
            pen_id=1,
            pen_name="test",
            vertical_dist_to_milking_parlor=0.0,
            horizontal_dist_to_milking_parlor=0.0,
            number_of_stalls=10,
            housing_type="freestall",
            pen_type="freestall",
            animal_combination=AnimalCombination.BEEF_COW_CALF_PAIR,
            max_stocking_density=1.0,
            minutes_away_for_milking=0,
            first_parlor_processor=None,
            parlor_stream_name=None,
            manure_streams=[],
            forage_quality_factor=-0.1,
        )


@pytest.mark.unit
def test_pen_forage_quality_factor_zero_valid(mocker: MockerFixture) -> None:
    """Pen constructor must accept forage_quality_factor=0.0 (complete forage failure is a valid scenario).

    The ValueError guard must only block negative values and non-finite values, not 0.0.
    _initialize_beddings is mocked to avoid InputManager dependency in this unit test.
    """
    mocker.patch.object(Pen, "_initialize_beddings")
    pen = Pen(
        pen_id=1,
        pen_name="test",
        vertical_dist_to_milking_parlor=0.0,
        horizontal_dist_to_milking_parlor=0.0,
        number_of_stalls=10,
        housing_type="freestall",
        pen_type="freestall",
        animal_combination=AnimalCombination.BEEF_COW_CALF_PAIR,
        max_stocking_density=1.0,
        minutes_away_for_milking=0,
        first_parlor_processor=None,
        parlor_stream_name=None,
        manure_streams=[],
        forage_quality_factor=0.0,
    )
    assert pen.forage_quality_factor == 0.0
