import copy
import math
from typing import Any
from unittest.mock import call
from dataclasses import replace
from datetime import date, datetime, timedelta
import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.feed_storage.silage import (
    Bag,
    Bunker,
    Pile,
    Silage,
    calculate_preseal_loss,
    _clamp_preseal_fraction,
    get_permeability_constants,
    calculate_respirable_substrate_fraction,
    _respirable_substrate_fraction,
    _get_or_initialize_infiltration_ceiling_kg,
    calculate_bag_infiltration_loss,
    calculate_bunker_infiltration_loss,
    calculate_feed_out_loss,
    FeedOutSection,
    build_feed_out_sections,
)
from RUFAS.biophysical.feed_storage.silage_constants import (
    PRESEAL_FALLBACK_EXPOSURE_DAYS,
    PRESEAL_EXPOSURE_CAP_DAYS,
)
from RUFAS.biophysical.feed_storage.storage import Storage
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

from .sample_crop_data import sample_crop_data


@pytest.fixture
def mock_silage_config() -> dict[str, str | float | list[str]]:
    return {
        "name": "silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "width_m": 10.0,
        "height_m": 3.0,
        "diameter_m": 3.0,
        "dry_matter_density_kg_per_m3": 180.0,
        "capacity": 1_000_000.0,
    }


@pytest.fixture
def silage(mock_silage_config: dict[str, str | float | list[str]]) -> Silage:
    return Silage(config=mock_silage_config)


@pytest.fixture
def harvested_crop() -> HarvestedCrop:
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    return HarvestedCrop(**sample_crop_data)


@pytest.fixture
def time() -> RufasTime:
    """
    Pytest fixture to create a RufasTime instance for testing.

    Returns
    -------
    RufasTime
        An instance of the RufasTime class.

    """
    return RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 3))


@pytest.fixture
def weather(mocker: MockerFixture, time: RufasTime) -> Weather:
    """Creates a Weather instance for testing."""
    mocker.patch.object(Weather, "__init__", return_value=None)
    return Weather({}, time)


@pytest.mark.parametrize("days_of_loss", [0, 10, 3])
def test_process_degradations(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop, days_of_loss: int
) -> None:
    """Tests the implementation of process_degradations in the Silage class."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 15
    mocker.patch.object(silage, "_finalize_preseal_loss")
    effluent_loss_days = mocker.patch.object(
        silage, "calculate_days_of_effluent_loss_to_process", return_value=days_of_loss
    )
    mocker.patch.object(silage, "_process_infiltration", return_value=0.0)
    mocker.patch.object(silage, "_process_feed_out")
    dry_loss = mocker.patch.object(silage, "calculate_dry_matter_loss_to_effluent", return_value=10.0)
    moisture_loss = mocker.patch.object(silage, "calculate_moisture_loss_to_effluent", return_value=20.0)
    npn_coefficient = mocker.patch.object(
        silage, "calculate_non_protein_nitrogen_after_effluent_loss", return_value=4.5
    )
    cp_coeffient = mocker.patch.object(silage, "calculate_crude_protein_after_effluent_loss", return_value=5.0)
    if days_of_loss:
        expected_mass_loss = {"dry_matter_loss": 20.0, "moisture_loss": 40.0}
    else:
        expected_mass_loss = {"dry_matter_loss": 0.0, "moisture_loss": 0.0}
    reset_attributes = mocker.patch.object(
        silage, "_calculate_mass_attributes_after_loss", return_value=expected_mass_loss
    )
    add_variable = mocker.patch.object(OutputManager, "add_variable")
    super_process_degradations = mocker.patch.object(Storage, "process_degradations")
    second_crop = copy.deepcopy(harvested_crop)
    silage.stored = [harvested_crop, second_crop]
    expected_info_map = {
        "class": silage.__class__.__name__,
        "function": silage.process_degradations.__name__,
        "prefix": "Feed.Storage.Silage.silage",
        "units": MeasurementUnits.KILOGRAMS,
        "simulation_day": mock_time.simulation_day,
    }

    silage.process_degradations(mock_weather, mock_time)

    effluent_loss_days.assert_has_calls([call(harvested_crop, mock_time), call(second_crop, mock_time)])
    assert dry_loss.call_count == (len(silage.stored) if days_of_loss else 0)
    assert moisture_loss.call_count == (len(silage.stored) if days_of_loss else 0)
    assert npn_coefficient.call_count == (len(silage.stored) if days_of_loss else 0)
    assert cp_coeffient.call_count == (len(silage.stored) if days_of_loss else 0)
    assert reset_attributes.call_count == (len(silage.stored) if days_of_loss else 0)
    add_variable.assert_has_calls(
        [
            call("total_effluent_dry_matter_loss", expected_mass_loss["dry_matter_loss"], expected_info_map),
            call("total_effluent_moisture_loss", expected_mass_loss["moisture_loss"], expected_info_map),
        ]
    )
    super_process_degradations.assert_called_once_with(mock_weather, mock_time)


def test_project_degradations(
    silage: Silage,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    weather: Weather,
    mocker: MockerFixture,
) -> None:
    """Test that project_degradations functions as expected."""
    effluent_loss_values = {
        "dry_matter_mass": 800.0,
        "dry_matter_percentage": 14.0,
        "non_protein_nitrogen": 3.0,
        "crude_protein_percent": 5.0,
        "dry_matter_loss": 20.0,
        "moisture_loss": 20.0,
    }
    expected_loss_values: dict[str, Any] = {
        "dry_matter_mass": 800.0,
        "dry_matter_percentage": 14.0,
        "non_protein_nitrogen": 3.0,
        "crude_protein_percent": 5.0,
    }
    silage.stored = [replace(harvested_crop) for _ in range(3)]
    for crop in silage.stored:
        crop.infiltration_cumulative_loss_kg = 12.5
        crop.infiltration_max_loss_kg = 40.0
    degraded_crops = [replace(crop, **expected_loss_values) for crop in silage.stored]
    for original_crop, expected_crop in zip(silage.stored, degraded_crops):
        # temperature/preseal_finalized/infiltration_cumulative_loss_kg/infiltration_max_loss_kg are
        # init=False and get recomputed by replace()'s __post_init__; project_degradations now restores
        # the pre-replace crop's actual values for all four instead of leaving them reset. Non-default
        # infiltration values are set above specifically so this test fails if any of the four go
        # unrestored (PR #49 review finding).
        expected_crop.temperature = original_crop.temperature
        expected_crop.preseal_finalized = original_crop.preseal_finalized
        expected_crop.infiltration_cumulative_loss_kg = original_crop.infiltration_cumulative_loss_kg
        expected_crop.infiltration_max_loss_kg = original_crop.infiltration_max_loss_kg
    calc_effluent_loss = mocker.patch.object(
        silage, "_calculate_effluent_loss", side_effect=[copy.copy(effluent_loss_values) for _ in range(3)]
    )
    process_degradations = mocker.patch.object(Storage, "project_degradations", return_value=degraded_crops)

    actual = silage.project_degradations(silage.stored, weather, time)

    for crop in actual:
        assert crop.dry_matter_mass == expected_loss_values["dry_matter_mass"]
        assert pytest.approx(crop.dry_matter_percentage) == expected_loss_values["dry_matter_percentage"]
        assert crop.non_protein_nitrogen == expected_loss_values["non_protein_nitrogen"]
        assert crop.crude_protein_percent == expected_loss_values["crude_protein_percent"]
    calc_effluent_loss.assert_has_calls([mocker.call(crop, time) for crop in silage.stored])
    process_degradations.assert_called_once_with(degraded_crops, weather, time)


@pytest.mark.parametrize(
    "day_stored, last_day_processed, current, expected",
    [
        (1, 1, 6, 5),
        (1, 3, 3, 0),
        (40, 45, 50, 5),
        (40, 45, 55, 10),
        (10, 22, 25, 3),
    ],
)
def test_calculate_days_of_effluent_loss_to_process(
    silage: Silage,
    time: RufasTime,
    harvested_crop: HarvestedCrop,
    day_stored: int,
    last_day_processed: int,
    current: int,
    expected: int,
) -> None:
    """Tests calculate_days_of_effluent_loss_to_process in Silage."""
    storage_date = date(2024, 6, 1)
    harvested_crop.storage_time = storage_date + timedelta(days=day_stored - 1)
    harvested_crop.last_time_degraded = storage_date + timedelta(days=last_day_processed - 1)
    time.current_date = datetime(2024, 6, 1) + timedelta(days=current - 1)

    actual = silage.calculate_days_of_effluent_loss_to_process(harvested_crop, time)
    assert actual == expected


@pytest.mark.parametrize(
    "max_effluent,days,expected", [(100.0, 10.0, 10.35), (55.0, 0, 0.0), (80.0, 4, 3.312), (120.0, 8, 9.936)]
)
def test_calculate_dry_matter_loss_to_effluent(silage: Silage, max_effluent: float, days: int, expected: float) -> None:
    """Tests calculate_dry_matter_loss_to_effluent in Silage."""
    actual = silage.calculate_dry_matter_loss_to_effluent(max_effluent, days)

    assert actual == expected


@pytest.mark.parametrize(
    "max_effluent,days,expected", [(100.0, 10.0, 89.65), (70.0, 0, 0.0), (90.0, 7, 56.4795), (150.0, 3, 40.3425)]
)
def test_calculate_moisture_loss_to_effluent(silage: Silage, max_effluent: float, days: int, expected: float) -> None:
    """Tests calculate_moisture_loss_to_effluent in Silage."""
    actual = silage.calculate_moisture_loss_to_effluent(max_effluent, days)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "npn,cp,loss_frac,expected",
    [(4.0, 25.0, 0.02, 1.63934426), (8.0, 50.0, 0.05, 5.15463917), (0.0, 3.6, 0.01, 0.0), (4.0, 20.0, 0.0, 4.0)],
)
def test_calculate_non_protein_nitrogen_after_effluent_loss(
    silage: Silage, npn: float, cp: float, loss_frac: float, expected: float
) -> None:
    """Tests calculate_non_protein_nitrogen_loss_coefficient in Silage."""
    actual = silage.calculate_non_protein_nitrogen_after_effluent_loss(npn, cp, loss_frac)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "cp,loss_frac,expected", [(5.6, 0.033, 4.767322), (2.2, 0.04, 1.041667), (0.0, 0.05, 0.0), (8.7, 0.0, 8.7)]
)
def test_calculate_crude_protein_after_effluent_loss(
    silage: Silage, cp: float, loss_frac: float, expected: float
) -> None:
    """Tests calculate_crude_protein_loss_coefficient in Silage."""
    actual = silage.calculate_crude_protein_after_effluent_loss(cp, loss_frac)

    assert pytest.approx(actual) == expected


@pytest.fixture
def bunker(mock_silage_config: dict[str, str | float | list[str]]) -> Bunker:
    return Bunker(config=mock_silage_config)


@pytest.fixture
def pile(mock_silage_config: dict[str, str | float | list[str]]) -> Pile:
    return Pile(config=mock_silage_config)


@pytest.fixture
def bag(mock_silage_config: dict[str, str | float | list[str]]) -> Bag:
    return Bag(config=mock_silage_config)


def test_bag_init(mock_silage_config: dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that the Bag class is initialized correctly."""
    mock_silage_init = mocker.patch("RUFAS.biophysical.feed_storage.silage.Silage.__init__")
    bag = Bag(config=mock_silage_config)
    assert bag.diameter_m == mock_silage_config.get("diameter_m")
    assert bag.dry_matter_density_kg_per_m3 == mock_silage_config.get("dry_matter_density_kg_per_m3")
    mock_silage_init.assert_called_once_with(mock_silage_config)


@pytest.mark.unit
def test_bunker_geometry_and_density_are_optional(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bunker constructs fine with width_m, height_m, or dry_matter_density_kg_per_m3 missing — the
    attribute is None, and no reference-table fallback is substituted."""
    config = dict(mock_silage_config)
    for missing_key in ("width_m", "height_m", "dry_matter_density_kg_per_m3"):
        bad_config = {**config, "width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
        del bad_config[missing_key]
        bunker = Bunker(config=bad_config)
        assert getattr(bunker, missing_key) is None


@pytest.mark.unit
@pytest.mark.parametrize("bad_value", [0.0, -5.0])
@pytest.mark.parametrize("field_name", ["width_m", "height_m", "dry_matter_density_kg_per_m3"])
def test_bunker_requires_positive_geometry_and_density_rejects_non_positive_values(
    mock_silage_config: dict[str, str | float | list[str]], field_name: str, bad_value: float
) -> None:
    """Bunker raises ValueError if width_m, height_m, or dry_matter_density_kg_per_m3 is zero or negative."""
    config = dict(mock_silage_config)
    bad_config = {**config, "width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
    bad_config[field_name] = bad_value
    with pytest.raises(ValueError, match=field_name):
        Bunker(config=bad_config)


@pytest.mark.unit
def test_bunker_stores_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bunker stores width_m, height_m, and dry_matter_density_kg_per_m3 from config."""
    config = dict(mock_silage_config)
    config.update({"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})

    bunker = Bunker(config=config)

    assert bunker.width_m == 10.0
    assert bunker.height_m == 3.0
    assert bunker.dry_matter_density_kg_per_m3 == 180.0


@pytest.mark.unit
def test_pile_geometry_and_density_are_optional(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Pile constructs fine with width_m, height_m, or dry_matter_density_kg_per_m3 missing — the
    attribute is None, and no reference-table fallback is substituted."""
    config = dict(mock_silage_config)
    for missing_key in ("width_m", "height_m", "dry_matter_density_kg_per_m3"):
        bad_config = {**config, "width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
        del bad_config[missing_key]
        pile = Pile(config=bad_config)
        assert getattr(pile, missing_key) is None


@pytest.mark.unit
def test_pile_stores_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Pile stores width_m, height_m, and dry_matter_density_kg_per_m3 from config."""
    config = dict(mock_silage_config)
    config.update({"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})

    pile = Pile(config=config)

    assert pile.width_m == 10.0
    assert pile.height_m == 3.0
    assert pile.dry_matter_density_kg_per_m3 == 180.0


@pytest.mark.unit
def test_bag_geometry_and_density_are_optional(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bag constructs fine with diameter_m or dry_matter_density_kg_per_m3 missing — the attribute is
    None, and no reference-table fallback is substituted."""
    config = dict(mock_silage_config)
    for missing_key in ("diameter_m", "dry_matter_density_kg_per_m3"):
        bad_config = {**config, "diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
        del bad_config[missing_key]
        bag = Bag(config=bad_config)
        assert getattr(bag, missing_key) is None


@pytest.mark.unit
def test_bag_stores_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bag stores diameter_m and dry_matter_density_kg_per_m3 from config."""
    config = dict(mock_silage_config)
    config.update({"diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})

    bag = Bag(config=config)

    assert bag.diameter_m == 3.0
    assert bag.dry_matter_density_kg_per_m3 == 180.0


@pytest.mark.unit
def test_calculate_preseal_loss_zero_exposure() -> None:
    """Zero exposure time produces zero dry matter loss and no temperature change."""
    crop = HarvestedCrop(**sample_crop_data)
    initial_temperature = crop.temperature

    result = calculate_preseal_loss(crop, exposure_days=0.0, exposed_area_m2=50.0, dry_matter_density_kg_per_m3=180.0)

    assert result["dry_matter_loss_fraction"] == 0.0
    assert result["final_temperature"] == initial_temperature


@pytest.mark.unit
def test_calculate_preseal_loss_alfalfa_positive_and_bounded() -> None:
    """Alfalfa preseal loss over 3 days of exposure is positive, less than 100%, and raises temperature."""
    crop = HarvestedCrop(**{**sample_crop_data, "config_name": "alfalfa_data", "dry_matter_percentage": 35.0})

    result = calculate_preseal_loss(crop, exposure_days=3.0, exposed_area_m2=50.0, dry_matter_density_kg_per_m3=180.0)

    assert 0.0 < result["dry_matter_loss_fraction"] < 1.0
    assert result["final_temperature"] > crop.temperature


@pytest.mark.unit
def test_calculate_preseal_loss_two_day_oracle_pins_self_heating_feedback() -> None:
    """Day 2's loss is strictly larger than day 1's, and both the cumulative loss and the final
    temperature are pinned against an independently re-derived oracle (a standalone re-implementation
    of `Silostg.for`'s `PRESEAL` day-stepping loop, not calling `calculate_preseal_loss` itself) — a
    bounds-only check (as used by `test_calculate_preseal_loss_alfalfa_positive_and_bounded`) would
    still pass even if the self-heating feedback (`temperature` feeding into the next day's
    `temperature_factor`) were broken or removed entirely, since it only confirms *some* temperature
    rise happened, not that it is correctly fed back into the next day's respiration rate (PR #49
    review finding).

    Corn silage (non-alfalfa; ``MUMAX`` coefficient 2.9), ``dry_matter_percentage=35.0``,
    ``dry_matter_mass=100.0``, initial temperature 8.0 (``INITIAL_FILL_TEMPERATURE_NON_ALFALFA_C``), 2
    days of exposure (two full iterations of `PRESEAL`'s day-stepping loop), ``exposed_area_m2 =
    sqrt(5) * 10.0 * 3.0`` (Bunker geometry, matching `test_preseal_full_cycle_bunker_matches_
    independent_oracle`'s 1-day case), density 180.0 kg DM/m3. Independently evaluating that
    translation by hand (a standalone script, not importing `silage.py`) for these inputs gives
    ``dry_matter_loss_fraction ≈ 0.007172354895645111`` and ``final_temperature ≈ 16.267689093930407``
    — day 2 alone contributes ≈0.003841629231 to the total, strictly more than day 1's
    ≈0.003330725664 (which matches `test_preseal_full_cycle_bunker_matches_independent_oracle`'s own
    1-day oracle exactly, confirming this script is a faithful re-derivation), because day 1's ≈3.84°C
    temperature rise raises day 2's ``temperature_factor``.

    """
    crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})

    result = calculate_preseal_loss(
        crop, exposure_days=2.0, exposed_area_m2=math.sqrt(5.0) * 10.0 * 3.0, dry_matter_density_kg_per_m3=180.0
    )

    assert result["dry_matter_loss_fraction"] == pytest.approx(0.007172354895645111)
    assert result["final_temperature"] == pytest.approx(16.267689093930407)


@pytest.mark.unit
def test_calculate_preseal_loss_fallback_exposure() -> None:
    """The 0.125-day fallback exposure (newest plot, no successor yet) produces a small but positive loss."""
    crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})

    result = calculate_preseal_loss(
        crop, exposure_days=PRESEAL_FALLBACK_EXPOSURE_DAYS, exposed_area_m2=30.0, dry_matter_density_kg_per_m3=180.0
    )

    assert 0.0 < result["dry_matter_loss_fraction"] < 0.01


@pytest.mark.unit
@pytest.mark.parametrize("raw_fraction,expected", [(-0.2, 0.0), (0.5, 0.5), (1.3, 1.0)])
def test_clamp_preseal_fraction_bounds(raw_fraction: float, expected: float) -> None:
    """`_clamp_preseal_fraction` floors at 0.0, ceilings at 1.0, and passes through in-range values.

    (`/challenge-plan` finding #3, cycle 3: realistic inputs at the exposure cap only reach ~1-2%
    loss — no physically plausible area/density/exposure combination drives the day-stepping equation
    itself near 1.0, so a test built on realistic physics inputs would pass identically with or
    without the clamp. Testing the clamp as its own pure function, directly, is the only way to
    actually exercise the boundary — see spec §6's floor/ceiling requirement for new Preseal code.)
    """
    assert _clamp_preseal_fraction(raw_fraction) == expected


@pytest.mark.unit
def test_receive_crop_finalizes_predecessor_preseal(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """Receiving a second crop finalizes the first crop's preseal loss using the storage-time gap."""
    first_crop = harvested_crop
    second_crop = replace(harvested_crop, storage_time=harvested_crop.storage_time + timedelta(days=2))
    finalize = mocker.patch.object(silage, "_finalize_preseal_loss")

    silage.receive_crop(first_crop, simulation_day=1)
    silage.receive_crop(second_crop, simulation_day=3)

    finalize.assert_called_once_with(first_crop, 2.0)


@pytest.mark.unit
def test_receive_crop_caps_exposure_at_three_days(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """A storage-time gap longer than 3 days is capped at PRESEAL_EXPOSURE_CAP_DAYS."""
    first_crop = harvested_crop
    second_crop = replace(harvested_crop, storage_time=harvested_crop.storage_time + timedelta(days=10))
    finalize = mocker.patch.object(silage, "_finalize_preseal_loss")

    silage.receive_crop(first_crop, simulation_day=1)
    silage.receive_crop(second_crop, simulation_day=11)

    finalize.assert_called_once_with(first_crop, PRESEAL_EXPOSURE_CAP_DAYS)


@pytest.mark.unit
def test_process_degradations_finalizes_newest_crop_with_fallback(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """A crop with no successor yet gets finalized with the fallback exposure on its first degradation pass."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 5
    finalize = mocker.patch.object(silage, "_finalize_preseal_loss")
    mocker.patch.object(silage, "calculate_days_of_effluent_loss_to_process", return_value=0)
    mocker.patch.object(silage, "_process_infiltration", return_value=0.0)
    mocker.patch.object(silage, "_process_feed_out")
    mocker.patch.object(Storage, "process_degradations")
    silage.stored = [harvested_crop]

    silage.process_degradations(mock_weather, mock_time)

    finalize.assert_called_once_with(harvested_crop, PRESEAL_FALLBACK_EXPOSURE_DAYS)
    # NOTE: _finalize_preseal_loss is mocked above, so its real body (which sets
    # preseal_finalized = True) never runs — there is deliberately no assertion on
    # harvested_crop.preseal_finalized here. That behavior is covered unmocked by Task 5's
    # test_preseal_full_cycle_stays_within_bounds. (/challenge-plan finding #2, cycle 2 — removed a
    # prior assertion here that could never pass against a mocked method.)


@pytest.mark.unit
def test_process_degradations_skips_already_finalized_crop(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """A crop already finalized is not finalized again."""
    harvested_crop.preseal_finalized = True
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    finalize = mocker.patch.object(silage, "_finalize_preseal_loss")
    mocker.patch.object(silage, "calculate_days_of_effluent_loss_to_process", return_value=0)
    mocker.patch.object(silage, "_process_infiltration", return_value=0.0)
    mocker.patch.object(silage, "_process_feed_out")
    mocker.patch.object(Storage, "process_degradations")
    silage.stored = [harvested_crop]

    silage.process_degradations(mock_weather, mock_time)

    finalize.assert_not_called()


@pytest.mark.unit
def test_process_degradations_runs_fermentation_before_infiltration(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """Fermentation (`Storage.process_degradations`) must run before Infiltration
    (`_process_infiltration`) for every crop — the exact bug this test guards against is the
    original ordering (Effluent -> Infiltration -> Fermentation), which a test only checking that
    both were eventually called would not catch."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 15
    mocker.patch.object(silage, "_finalize_preseal_loss")
    mocker.patch.object(silage, "calculate_days_of_effluent_loss_to_process", return_value=0)
    call_order: list[str] = []
    mocker.patch.object(
        Storage,
        "process_degradations",
        side_effect=lambda *args, **kwargs: call_order.append("fermentation"),
    )

    def _record_infiltration(crop: HarvestedCrop, elapsed_days: float) -> float:
        call_order.append("infiltration")
        return 0.0

    mocker.patch.object(silage, "_process_infiltration", side_effect=_record_infiltration)
    mocker.patch.object(silage, "_process_feed_out")
    second_crop = copy.deepcopy(harvested_crop)
    silage.stored = [harvested_crop, second_crop]

    silage.process_degradations(mock_weather, mock_time)

    assert call_order == ["fermentation", "infiltration", "infiltration"]


@pytest.mark.unit
def test_process_degradations_infiltration_elapsed_days_survives_fermentation(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """`elapsed_days` passed to `_process_infiltration` reflects the gap since the crop's
    pre-Fermentation `last_time_degraded`, not zero — even though `_process_infiltration` is only
    invoked after `Storage.process_degradations` (Fermentation) has already run and overwritten
    `crop.last_time_degraded` to today. This is the regression the naive "just move the loop after
    super()" fix would silently introduce (elapsed_days == 0.0 forever)."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 15
    mock_time.current_date.date.return_value = harvested_crop.storage_time + timedelta(days=10)
    harvested_crop.last_time_degraded = harvested_crop.storage_time
    mocker.patch.object(silage, "_finalize_preseal_loss")
    mocker.patch.object(silage, "calculate_days_of_effluent_loss_to_process", return_value=0)

    def _fake_fermentation(weather: Weather, time: RufasTime) -> None:
        # Mirrors Storage.process_degradations' real side effect (storage.py:215): every stored
        # crop's last_time_degraded is advanced to today once Fermentation has processed it.
        for crop in silage.stored:
            crop.last_time_degraded = time.current_date.date()

    mocker.patch.object(Storage, "process_degradations", side_effect=_fake_fermentation)
    infiltration = mocker.patch.object(silage, "_process_infiltration", return_value=0.0)
    mocker.patch.object(silage, "_process_feed_out")
    silage.stored = [harvested_crop]

    silage.process_degradations(mock_weather, mock_time)

    infiltration.assert_called_once_with(harvested_crop, 10.0)


@pytest.mark.unit
def test_process_degradations_applies_bag_infiltration(mocker: MockerFixture, harvested_crop: HarvestedCrop) -> None:
    """process_degradations reduces a Bag crop's dry matter mass via infiltration loss."""
    config: dict[str, str | float | list[str]] = {
        "name": "bag_silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
        "diameter_m": 3.0,
        "dry_matter_density_kg_per_m3": 180.0,
    }
    bag = Bag(config=config)
    harvested_crop.preseal_finalized = True
    harvested_crop.last_time_degraded = harvested_crop.storage_time - timedelta(days=30)
    bag.stored = [harvested_crop]
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 30
    mock_time.current_date.date.return_value = harvested_crop.storage_time
    mocker.patch.object(bag, "calculate_days_of_effluent_loss_to_process", return_value=0)
    mocker.patch.object(Storage, "process_degradations")
    initial_mass = harvested_crop.dry_matter_mass

    bag.process_degradations(mock_weather, mock_time)

    assert harvested_crop.dry_matter_mass < initial_mass
    assert harvested_crop.infiltration_cumulative_loss_kg > 0.0


@pytest.mark.unit
def test_process_degradations_skips_infiltration_when_geometry_missing(
    mocker: MockerFixture, harvested_crop: HarvestedCrop
) -> None:
    """A Bunker with no width_m/height_m/dry_matter_density_kg_per_m3 configured (e.g. the protected
    `example_feed_storage_configs.json` fixture's legacy `size`-only entries) skips Infiltration
    instead of crashing on `None` geometry — Open Decision 7."""
    config: dict[str, str | float | list[str]] = {
        "name": "bunker_silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
        "size": 0.0,
    }
    bunker = Bunker(config=config)
    harvested_crop.preseal_finalized = True
    harvested_crop.last_time_degraded = harvested_crop.storage_time - timedelta(days=30)
    bunker.stored = [harvested_crop]
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 30
    mock_time.current_date.date.return_value = harvested_crop.storage_time
    mocker.patch.object(bunker, "calculate_days_of_effluent_loss_to_process", return_value=0)
    mocker.patch.object(Storage, "process_degradations")
    initial_mass = harvested_crop.dry_matter_mass

    bunker.process_degradations(mock_weather, mock_time)

    assert harvested_crop.dry_matter_mass == initial_mass
    assert harvested_crop.infiltration_cumulative_loss_kg == 0.0


@pytest.mark.unit
@pytest.mark.parametrize(
    "storage_class,extra_config,missing_key",
    [
        (Bunker, {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}, "width_m"),
        (Bunker, {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}, "height_m"),
        (
            Bunker,
            {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0},
            "dry_matter_density_kg_per_m3",
        ),
        (Pile, {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}, "width_m"),
        (Pile, {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}, "height_m"),
        (
            Pile,
            {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0},
            "dry_matter_density_kg_per_m3",
        ),
        (Bag, {"diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}, "diameter_m"),
        (Bag, {"diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}, "dry_matter_density_kg_per_m3"),
    ],
)
def test_finalize_preseal_loss_skips_gracefully_when_geometry_missing(
    mock_silage_config: dict[str, str | float | list[str]],
    harvested_crop: HarvestedCrop,
    storage_class: type[Silage],
    extra_config: dict[str, float],
    missing_key: str,
) -> None:
    """A storage missing any Preseal geometry/density field skips Preseal for a crop entirely: no
    exception, no mass/nutrient/temperature change, but the crop is still marked finalized so it
    isn't re-attempted on every degradation pass. Deletes the key entirely (the real production
    route for an absent field) rather than injecting an explicit None. Covers all three storage
    classes and every field each one depends on. This is what keeps existing farm configs that
    predate the Preseal geometry fields working unchanged."""
    config: dict[str, str | float | list[str]] = dict(mock_silage_config)
    config.update(extra_config)
    del config[missing_key]
    storage = storage_class(config=config)
    initial_dry_matter_mass = harvested_crop.dry_matter_mass
    initial_dry_matter_percentage = harvested_crop.dry_matter_percentage
    initial_ndf = harvested_crop.ndf
    initial_crude_protein_percent = harvested_crop.crude_protein_percent
    initial_temperature = harvested_crop.temperature

    storage._finalize_preseal_loss(harvested_crop, exposure_days=2.0)

    assert harvested_crop.preseal_finalized is True
    assert harvested_crop.dry_matter_mass == initial_dry_matter_mass
    assert harvested_crop.dry_matter_percentage == initial_dry_matter_percentage
    assert harvested_crop.ndf == initial_ndf
    assert harvested_crop.crude_protein_percent == initial_crude_protein_percent
    assert harvested_crop.temperature == initial_temperature


@pytest.mark.component
@pytest.mark.parametrize(
    "storage_class,extra_config",
    [
        (Bunker, {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}),
        (Bag, {"diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}),
    ],
)
def test_preseal_full_cycle_stays_within_bounds(
    mock_silage_config: dict[str, str | float | list[str]],
    storage_class: type[Silage],
    extra_config: dict[str, float],
) -> None:
    """Two crops received in sequence: the first's Preseal loss finalizes on the second's arrival, stays in (0, 1)."""
    config = dict(mock_silage_config)
    config.update(extra_config)
    storage = storage_class(config=config)
    first_crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})
    second_crop = replace(
        HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0}),
        storage_time=first_crop.storage_time + timedelta(days=1),
    )

    storage.receive_crop(first_crop, simulation_day=1)
    storage.receive_crop(second_crop, simulation_day=2)

    assert first_crop.preseal_finalized is True
    assert 0.0 < first_crop.dry_matter_mass < sample_crop_data["dry_matter_mass"]
    assert first_crop.temperature > 8.0
    assert second_crop.preseal_finalized is False


@pytest.mark.component
def test_preseal_full_cycle_bunker_matches_hand_calculation(
    mock_silage_config: dict[str, str | float | list[str]],
) -> None:
    """`receive_crop`'s full cycle passes the right ``exposed_area_m2``/``dry_matter_density_kg_per_m3``
    through to `calculate_preseal_loss` — wiring coverage only.

    This computes its expected value by calling `calculate_preseal_loss` directly, the same function
    `_finalize_preseal_loss` calls internally, so it cannot catch a defect in the equation itself (a
    wrong formula would move both sides together) — it only proves the Task 1-4 integration correctly
    passes this Bunker's actual geometry/density through `receive_crop`, e.g. that
    `exposed_area_m2`/`dry_matter_density_kg_per_m3` aren't silently swapped or mis-derived on the way
    in. See `test_preseal_full_cycle_bunker_matches_independent_oracle` below for a numeric oracle
    that is independent of `calculate_preseal_loss` and would catch a shared equation defect.
    """
    config = dict(mock_silage_config)
    config.update({"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})
    bunker = Bunker(config=config)
    first_crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})
    second_crop = replace(
        HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0}),
        storage_time=first_crop.storage_time + timedelta(days=1),
    )
    reference_crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})
    expected = calculate_preseal_loss(
        reference_crop,
        exposure_days=1.0,
        exposed_area_m2=math.sqrt(5.0) * 10.0 * 3.0,
        dry_matter_density_kg_per_m3=180.0,
    )
    expected_dry_matter_loss_kg = reference_crop.dry_matter_mass * expected["dry_matter_loss_fraction"]

    bunker.receive_crop(first_crop, simulation_day=1)
    bunker.receive_crop(second_crop, simulation_day=2)

    assert first_crop.dry_matter_mass == pytest.approx(
        sample_crop_data["dry_matter_mass"] - expected_dry_matter_loss_kg
    )


@pytest.mark.component
def test_preseal_full_cycle_bunker_matches_independent_oracle(
    mock_silage_config: dict[str, str | float | list[str]],
) -> None:
    """The Bunker case's dry-matter loss matches a numeric oracle independently re-derived from
    `Silostg.for`'s ``PRESEAL`` subroutine (lines 634-714) in isolation from
    `calculate_preseal_loss` — unlike `test_preseal_full_cycle_bunker_matches_hand_calculation`
    above, a defect shared by both this test's expectation and the production equation (e.g. a wrong
    coefficient transcribed from the Fortran source) cannot pass both sides here, since this oracle
    was computed without calling any RuFaS code (spec §8's "hand-calculated expectation" requirement).

    Same inputs as the wiring-coverage test above: corn silage (non-alfalfa; ``MUMAX`` coefficient
    2.9), ``dry_matter_percentage=35.0``, ``dry_matter_mass=100.0``, initial temperature 8.0
    (``INITIAL_FILL_TEMPERATURE_NON_ALFALFA_C``), 1 day of exposure (exactly one iteration of
    `PRESEAL`'s day-stepping loop, since ``day_step = min(1.0, remaining_exposure_days)`` consumes the
    full 1.0-day ``remaining_exposure_days`` on that single pass), Bunker geometry ``width_m=10.0`` /
    ``height_m=3.0`` (``exposed_area_m2 = sqrt(5) * width_m * height_m``, Silostg.for:329), density
    180.0 kg DM/m3. Independently evaluating that translation by hand (a standalone script, not
    importing `silage.py`) for these inputs gives ``dry_matter_loss_fraction ≈ 0.0033307256642235447``
    (``dry_matter_loss_kg ≈ 0.3330725664223544``) — the fixed expectation asserted below.

    """
    config = dict(mock_silage_config)
    config.update({"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})
    bunker = Bunker(config=config)
    first_crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})
    second_crop = replace(
        HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0}),
        storage_time=first_crop.storage_time + timedelta(days=1),
    )
    independently_derived_dry_matter_loss_kg = 0.3330725664223544

    bunker.receive_crop(first_crop, simulation_day=1)
    bunker.receive_crop(second_crop, simulation_day=2)

    assert first_crop.dry_matter_mass == pytest.approx(
        sample_crop_data["dry_matter_mass"] - independently_derived_dry_matter_loss_kg
    )


@pytest.mark.unit
def test_get_permeability_constants_bunker() -> None:
    """Bunker's sourced cover permeability is 1.0 cm/h."""
    assert get_permeability_constants("Bunker") == 1.0


@pytest.mark.unit
def test_get_permeability_constants_pile() -> None:
    """Pile's sourced structure-wall permeability is 4.0 cm/h."""
    assert get_permeability_constants("Pile") == 4.0


@pytest.mark.unit
def test_get_permeability_constants_bag() -> None:
    """Bag's sourced sealed-plastic permeability is 1.0 cm/h (IFSM Reference Manual, p.76-77)."""
    assert get_permeability_constants("Bag") == 1.0


@pytest.mark.unit
def test_get_permeability_constants_unknown_raises() -> None:
    """An unsourced or unknown storage class fails loudly instead of returning a placeholder."""
    with pytest.raises(ValueError, match="Vertical"):
        get_permeability_constants("Vertical")


@pytest.mark.unit
def test_calculate_respirable_substrate_fraction() -> None:
    """RS = 1 - NDF - CP - ash, as fractions of dry matter."""
    crop = HarvestedCrop(**{**sample_crop_data, "ndf": 40.0, "crude_protein_percent": 10.0, "ash": 6.0})

    rs = calculate_respirable_substrate_fraction(crop)

    assert rs == pytest.approx(1.0 - 0.40 - 0.10 - 0.06)


@pytest.mark.unit
def test_calculate_respirable_substrate_fraction_fully_depleted() -> None:
    """RS is zero (not negative) when NDF+CP+ash already account for all dry matter."""
    crop = HarvestedCrop(**{**sample_crop_data, "ndf": 60.0, "crude_protein_percent": 30.0, "ash": 10.0})

    rs = calculate_respirable_substrate_fraction(crop)

    assert rs == pytest.approx(0.0)


@pytest.mark.unit
def test_respirable_substrate_fraction_matches_hand_calculation() -> None:
    """Pins `_respirable_substrate_fraction`'s output against a hand-computed literal, using three
    distinct argument values so an argument-order bug (e.g. ndf/crude-protein swapped) would be
    caught — `1 - a - b - c` only distinguishes argument position when a, b, c actually differ, so
    equal or symmetric inputs (as in the wrapper-equivalence test below) can't catch that class of
    wiring bug on their own."""
    result = _respirable_substrate_fraction(ndf_fraction=0.40, crude_protein_fraction=0.18, ash_fraction=0.08)
    assert result == pytest.approx(1.0 - 0.40 - 0.18 - 0.08)


@pytest.mark.unit
def test_respirable_substrate_fraction_matches_public_wrapper(harvested_crop: HarvestedCrop) -> None:
    """The private helper and the existing public `calculate_respirable_substrate_fraction` (still
    `HarvestedCrop`-typed) must agree for the same composition. Uses the named unit-conversion
    constant rather than a hardcoded `0.01`, so a future change to it stays reflected here."""
    ndf_fraction = harvested_crop.ndf * GeneralConstants.PERCENTAGE_TO_FRACTION
    crude_protein_fraction = harvested_crop.crude_protein_percent * GeneralConstants.PERCENTAGE_TO_FRACTION
    ash_fraction = harvested_crop.ash * GeneralConstants.PERCENTAGE_TO_FRACTION

    assert _respirable_substrate_fraction(ndf_fraction, crude_protein_fraction, ash_fraction) == pytest.approx(
        calculate_respirable_substrate_fraction(harvested_crop)
    )


@pytest.mark.unit
def test_infiltration_ceiling_fixed_on_first_call_and_stable_after() -> None:
    """The RS ceiling is fixed in absolute kg on first use and never recomputed from a later,
    shrunken `dry_matter_mass` — the bug the 2026-09-10 `/challenge-plan` review flagged."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    rs_fraction = calculate_respirable_substrate_fraction(crop)
    expected_ceiling_kg = crop.dry_matter_mass * rs_fraction

    first_ceiling_kg = _get_or_initialize_infiltration_ceiling_kg(crop)
    crop.dry_matter_mass -= 100.0
    second_ceiling_kg = _get_or_initialize_infiltration_ceiling_kg(crop)

    assert first_ceiling_kg == pytest.approx(expected_ceiling_kg)
    assert second_ceiling_kg == pytest.approx(first_ceiling_kg)


@pytest.mark.unit
def test_calculate_bag_infiltration_loss_zero_days() -> None:
    """Zero elapsed days produces zero loss and does not change accumulated loss."""
    crop = HarvestedCrop(**sample_crop_data)

    loss = calculate_bag_infiltration_loss(crop, elapsed_days=0.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0)

    assert loss == 0.0
    assert crop.infiltration_cumulative_loss_kg == 0.0


@pytest.mark.unit
def test_calculate_bag_infiltration_loss_positive_and_bounded() -> None:
    """A positive elapsed period produces positive loss that never exceeds the RS ceiling."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    rs_fraction = calculate_respirable_substrate_fraction(crop)
    max_loss_kg = crop.dry_matter_mass * rs_fraction

    loss = calculate_bag_infiltration_loss(crop, elapsed_days=30.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0)

    assert 0.0 < loss <= max_loss_kg
    assert crop.infiltration_cumulative_loss_kg == pytest.approx(loss)


@pytest.mark.unit
def test_calculate_bag_infiltration_loss_clips_at_rs_ceiling() -> None:
    """A very long elapsed period is clipped at the RS ceiling, never exceeding it."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    rs_fraction = calculate_respirable_substrate_fraction(crop)
    max_loss_kg = crop.dry_matter_mass * rs_fraction

    loss = calculate_bag_infiltration_loss(
        crop, elapsed_days=10_000.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0
    )

    assert loss == pytest.approx(max_loss_kg)


@pytest.mark.unit
def test_calculate_bag_infiltration_loss_stable_across_repeated_calls_with_unrelated_mass_loss() -> None:
    """Repeated calls with unrelated (e.g. Effluent/Fermentation) mass loss between them never crash
    and never move the fixed RS ceiling — regression test for the 2026-09-10 `/challenge-plan` finding."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    rs_fraction = calculate_respirable_substrate_fraction(crop)
    expected_ceiling_kg = crop.dry_matter_mass * rs_fraction

    for _ in range(20):
        calculate_bag_infiltration_loss(crop, elapsed_days=5.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0)
        crop.dry_matter_mass = max(1.0, crop.dry_matter_mass - 5.0)

    assert crop.infiltration_max_loss_kg == pytest.approx(expected_ceiling_kg)
    assert crop.infiltration_cumulative_loss_kg <= expected_ceiling_kg


@pytest.mark.unit
def test_calculate_bag_infiltration_loss_at_ceiling_does_not_crash() -> None:
    """Once cumulative loss reaches the fixed RS ceiling, a further call returns 0.0 instead of
    raising `ZeroDivisionError` on `math.log(radius_m / front_radius_m)` — regression test for the
    2026-09-11 `/challenge-plan` finding (front_radius_m == 0.0 exactly at the ceiling)."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    calculate_bag_infiltration_loss(crop, elapsed_days=10_000.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0)

    loss = calculate_bag_infiltration_loss(crop, elapsed_days=5.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0)

    assert loss == 0.0


@pytest.mark.unit
def test_calculate_bag_infiltration_loss_zero_dry_matter_percentage_returns_zero() -> None:
    """A crop with zero dry-matter percentage (reachable via `Storage._calculate_mass_attributes_after_loss`'s
    `new_fresh_mass == 0.0` branch, which can zero the percentage while `dry_matter_mass` stays positive)
    returns 0.0 instead of raising `ZeroDivisionError` on `crop.dry_matter_mass / dry_matter_fraction` —
    regression test for the 2026-09-11 `/challenge-plan` finding."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 0.0})

    loss = calculate_bag_infiltration_loss(crop, elapsed_days=5.0, diameter_m=3.0, dry_matter_density_kg_per_m3=180.0)

    assert loss == 0.0


@pytest.mark.unit
@pytest.mark.parametrize("storage_class_name", ["Bunker", "Pile"])
def test_calculate_bunker_infiltration_loss_zero_days(storage_class_name: str) -> None:
    """Zero elapsed days produces zero loss."""
    crop = HarvestedCrop(**sample_crop_data)

    loss = calculate_bunker_infiltration_loss(
        crop,
        elapsed_days=0.0,
        storage_class_name=storage_class_name,
        width_m=10.0,
        height_m=3.0,
        dry_matter_density_kg_per_m3=180.0,
    )

    assert loss == 0.0


@pytest.mark.unit
@pytest.mark.parametrize("storage_class_name", ["Bunker", "Pile"])
def test_calculate_bunker_infiltration_loss_positive_and_bounded(storage_class_name: str) -> None:
    """A positive elapsed period produces positive loss that never exceeds the RS ceiling."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    rs_fraction = calculate_respirable_substrate_fraction(crop)
    max_loss_kg = crop.dry_matter_mass * rs_fraction

    loss = calculate_bunker_infiltration_loss(
        crop,
        elapsed_days=30.0,
        storage_class_name=storage_class_name,
        width_m=10.0,
        height_m=3.0,
        dry_matter_density_kg_per_m3=180.0,
    )

    assert 0.0 < loss <= max_loss_kg


@pytest.mark.unit
def test_calculate_bunker_infiltration_loss_pile_loses_faster_than_bunker() -> None:
    """Pile's higher sourced permeability (4.0 vs 1.0 cm/h) produces more loss over the same period."""
    bunker_crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    pile_crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})

    bunker_loss = calculate_bunker_infiltration_loss(
        bunker_crop,
        elapsed_days=30.0,
        storage_class_name="Bunker",
        width_m=10.0,
        height_m=3.0,
        dry_matter_density_kg_per_m3=180.0,
    )
    pile_loss = calculate_bunker_infiltration_loss(
        pile_crop,
        elapsed_days=30.0,
        storage_class_name="Pile",
        width_m=10.0,
        height_m=3.0,
        dry_matter_density_kg_per_m3=180.0,
    )

    assert pile_loss > bunker_loss


@pytest.mark.unit
@pytest.mark.parametrize("storage_class_name", ["Bunker", "Pile"])
def test_calculate_bunker_infiltration_loss_stable_across_repeated_calls_with_unrelated_mass_loss(
    storage_class_name: str,
) -> None:
    """Repeated calls with unrelated (e.g. Effluent/Fermentation) mass loss between them never crash
    and never move the fixed RS ceiling — regression test for the 2026-09-10 `/challenge-plan` finding."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    rs_fraction = calculate_respirable_substrate_fraction(crop)
    expected_ceiling_kg = crop.dry_matter_mass * rs_fraction

    for _ in range(20):
        calculate_bunker_infiltration_loss(
            crop,
            elapsed_days=5.0,
            storage_class_name=storage_class_name,
            width_m=10.0,
            height_m=3.0,
            dry_matter_density_kg_per_m3=180.0,
        )
        crop.dry_matter_mass = max(1.0, crop.dry_matter_mass - 5.0)

    assert crop.infiltration_max_loss_kg == pytest.approx(expected_ceiling_kg)
    assert crop.infiltration_cumulative_loss_kg <= expected_ceiling_kg


@pytest.mark.unit
@pytest.mark.parametrize("storage_class_name", ["Bunker", "Pile"])
def test_calculate_bunker_infiltration_loss_at_ceiling_returns_zero(storage_class_name: str) -> None:
    """Once cumulative loss reaches the fixed RS ceiling, a further call returns 0.0 without
    re-running the full per-day formula — symmetry fix with `Bag`'s equivalent guard, added during the
    2026-09-11 `/challenge-plan` re-review (not a crash risk here, since `front_depth_cm` grows toward
    the ceiling rather than shrinking to zero, but avoids wasted computation on a fully-capped crop)."""
    crop = HarvestedCrop(**{**sample_crop_data, "dry_matter_percentage": 35.0})
    calculate_bunker_infiltration_loss(
        crop,
        elapsed_days=10_000.0,
        storage_class_name=storage_class_name,
        width_m=10.0,
        height_m=3.0,
        dry_matter_density_kg_per_m3=180.0,
    )

    loss = calculate_bunker_infiltration_loss(
        crop,
        elapsed_days=5.0,
        storage_class_name=storage_class_name,
        width_m=10.0,
        height_m=3.0,
        dry_matter_density_kg_per_m3=180.0,
    )

    assert loss == 0.0


@pytest.mark.unit
def test_calculate_feed_out_loss_zero_rate_returns_zero() -> None:
    """A storage with no Feed-out rate yet (nothing to feed out from) loses nothing."""
    loss = calculate_feed_out_loss(
        dry_matter_fraction=0.35,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=0.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=30.0,
    )
    assert loss == pytest.approx(0.0)


@pytest.mark.unit
def test_calculate_feed_out_loss_zero_face_area_returns_zero() -> None:
    """A missing/zero feedout face area (e.g. unconfigured geometry) loses nothing rather than dividing
    by zero."""
    loss = calculate_feed_out_loss(
        dry_matter_fraction=0.35,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=0.0,
    )
    assert loss == pytest.approx(0.0)


@pytest.mark.unit
def test_calculate_feed_out_loss_zero_dry_matter_fraction_returns_zero() -> None:
    """A fully wet (0% DM) input loses nothing rather than dividing by zero."""
    loss = calculate_feed_out_loss(
        dry_matter_fraction=0.0,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=30.0,
    )
    assert loss == pytest.approx(0.0)


@pytest.mark.unit
def test_calculate_feed_out_loss_full_dry_matter_fraction_returns_zero() -> None:
    """A 100% DM input (dry_matter_fraction == 1.0) loses nothing rather than dividing by zero in
    the water-activity term (1.0 - coefficient*DM/(1.0-DM)) — a physically implausible edge, but a
    genuine ZeroDivisionError if unguarded."""
    loss = calculate_feed_out_loss(
        dry_matter_fraction=1.0,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=30.0,
    )
    assert loss == pytest.approx(0.0)


@pytest.mark.unit
def test_calculate_feed_out_loss_positive_and_bounded() -> None:
    """A normal, realistic scenario produces a small positive loss fraction, well under the
    respirable-substrate ceiling."""
    loss = calculate_feed_out_loss(
        dry_matter_fraction=0.35,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=30.0,
    )
    assert 0.0 < loss < 0.34  # respirable substrate ceiling here is 1 - 0.40 - 0.18 - 0.08 = 0.34


@pytest.mark.unit
def test_calculate_feed_out_loss_alfalfa_loses_faster_than_non_alfalfa() -> None:
    """Same inputs, only `is_alfalfa` differs: FEEDOUT_LOADER_ALFALFA_COEFFICIENT (1.37) >
    FEEDOUT_LOADER_NON_ALFALFA_COEFFICIENT (1.18), so alfalfa's face-loss term must be larger."""
    kwargs: dict[str, float] = dict(
        dry_matter_fraction=0.35,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=30.0,
    )
    alfalfa_loss = calculate_feed_out_loss(is_alfalfa=True, **kwargs)
    non_alfalfa_loss = calculate_feed_out_loss(is_alfalfa=False, **kwargs)
    assert alfalfa_loss > non_alfalfa_loss


@pytest.mark.unit
def test_calculate_feed_out_loss_clips_at_rs_ceiling() -> None:
    """An already-mostly-depleted composition (respirable substrate close to 0) clips the loss at
    the RS ceiling rather than exceeding it.

    Uses a deliberately tiny `feed_out_rate_kg_dm_per_day` (not a large one): the face-diffusion term
    is inversely proportional to `face_advance_rate_cm_per_day`, which is itself directly proportional
    to the Feed-out rate — a slow (near-zero) Feed-out rate means the exposed face advances very
    slowly, maximizing exposure time and thus loss; a fast rate minimizes it. A large rate was verified
    (independently, outside this implementation) to leave the loss far under the 0.01 ceiling here
    (~0.00097), not over it.
    """
    loss = calculate_feed_out_loss(
        dry_matter_fraction=0.35,
        ndf_fraction=0.55,
        crude_protein_fraction=0.30,
        ash_fraction=0.14,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=1e-6,  # deliberately tiny to try to exceed the ceiling
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=1.0,
    )
    assert loss == pytest.approx(0.01, abs=1e-9)  # 1 - 0.55 - 0.30 - 0.14 = 0.01


@pytest.mark.unit
def test_calculate_feed_out_loss_respirable_substrate_already_zero_returns_zero() -> None:
    """A composition with zero (or negative) respirable substrate left loses nothing further."""
    loss = calculate_feed_out_loss(
        dry_matter_fraction=0.35,
        ndf_fraction=0.60,
        crude_protein_fraction=0.30,
        ash_fraction=0.10,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=180.0,
        face_area_m2=30.0,
    )
    # 1.0 - 0.60 - 0.30 - 0.10 is not exactly representable in IEEE-754 double precision (it lands a
    # few ULPs off zero), so the RS ceiling guard sees a vanishingly small positive value rather than
    # exactly 0.0 and the clipped result carries that same ~1e-17 residue through — pytest.approx per
    # tests/CLAUDE.md's "never == for floats, even literal-zero" rule, not a strict equality.
    assert loss == pytest.approx(0.0, abs=1e-9)


@pytest.mark.unit
def test_calculate_feed_out_loss_near_max_density_does_not_zero_face_loss() -> None:
    """At maximum packed density (relative_density == max_relative_density), porosity reaches its own
    floor of 0.035 (FEEDOUT_PHI_SCALE*(1-FEEDOUT_PHI_LOADER_COEFFICIENT)) — still above
    FEEDOUT_MIN_PHI (0.01), so FEEDOUT_MIN_PHI's face-diffusion gate is never triggered, even at this
    density ceiling. This test proves that directly — loss stays positive and finite at the density
    ceiling."""
    dry_matter_fraction = 0.35
    max_relative_density = 3.0 / (3.0 - dry_matter_fraction)  # PRESEAL_MAX_RELATIVE_DENSITY_NUMERATOR/(...)
    wet_density_at_cap = max_relative_density / 0.001  # relative_density * 1000, inverting *0.001 step
    dry_matter_density_kg_per_m3 = wet_density_at_cap * dry_matter_fraction

    loss = calculate_feed_out_loss(
        dry_matter_fraction=dry_matter_fraction,
        ndf_fraction=0.40,
        crude_protein_fraction=0.18,
        ash_fraction=0.08,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=500.0,
        dry_matter_density_kg_per_m3=dry_matter_density_kg_per_m3,
        face_area_m2=30.0,
    )
    assert 0.0 < loss <= 1.0  # positive and RS-ceiling-bounded; not zeroed by the unreachable gate


@pytest.mark.unit
def test_calculate_feed_out_loss_numeric_oracle() -> None:
    """Independent numeric oracle: hand-computes the same scenario term-by-term outside the
    implementation, to catch a transcription error in the dense equation chain that a mock-heavy or
    trivial-input test would not."""
    dry_matter_fraction = 0.35
    ndf_fraction = 0.40
    crude_protein_fraction = 0.18
    ash_fraction = 0.08
    feed_out_rate_kg_dm_per_day = 500.0
    dry_matter_density_kg_per_m3 = 180.0
    face_area_m2 = 30.0

    wet_density = dry_matter_density_kg_per_m3 / dry_matter_fraction
    max_relative_density = 3.0 / (3.0 - dry_matter_fraction)
    relative_density = min(max_relative_density, wet_density * 0.001)
    porosity = 0.7 * (1.0 - 0.95 * relative_density / max_relative_density)
    assert porosity >= 0.01  # sanity: this scenario must exercise the face-loss branch

    diffusion_coefficient = 0.0086 * (273.0 + 18.0) ** 2
    face_advance_rate_cm_per_day = (
        100.0 * (feed_out_rate_kg_dm_per_day / dry_matter_fraction) / (wet_density * face_area_m2)
    )
    mumax = 0.88 * dry_matter_fraction
    water_activity = 1.0 - 0.03 * dry_matter_fraction / (1.0 - dry_matter_fraction)
    assert 0.9233 <= water_activity <= 0.9931  # sanity: this scenario exercises the mid branch of FD
    water_activity_factor = 14.306 * water_activity - 13.208
    import math as _math

    temperature_factor = _math.exp(36.1 - 10830.0 / 291.0)
    respiration_rate = mumax * water_activity_factor * temperature_factor

    gamma = (
        relative_density
        * respiration_rate
        * (0.00145 + 0.21)
        * 1.0
        / (diffusion_coefficient * porosity * (2.0 / 3.0) * 0.21)
    )
    c = max(0.01, _math.sqrt(9.0 * gamma))
    average_respiration_rate = (
        -respiration_rate
        * 1.0
        * (0.00145 + 0.21)
        * (_math.log(0.00145 + 0.21 * _math.exp(-c * 300.0)) - _math.log(0.00145 + 0.21))
        / (0.21 * c * 300.0)
    )
    face_loss_fraction = (
        1.37 * 0.0299 * average_respiration_rate * 300.0 / (face_advance_rate_cm_per_day * dry_matter_fraction)
    )
    bunk_loss_fraction = 0.0299 * respiration_rate * 0.125 / dry_matter_fraction
    expected = min(1.0 - ndf_fraction - crude_protein_fraction - ash_fraction, face_loss_fraction + bunk_loss_fraction)

    actual = calculate_feed_out_loss(
        dry_matter_fraction=dry_matter_fraction,
        ndf_fraction=ndf_fraction,
        crude_protein_fraction=crude_protein_fraction,
        ash_fraction=ash_fraction,
        is_alfalfa=True,
        feed_out_rate_kg_dm_per_day=feed_out_rate_kg_dm_per_day,
        dry_matter_density_kg_per_m3=dry_matter_density_kg_per_m3,
        face_area_m2=face_area_m2,
    )
    assert actual == pytest.approx(expected, rel=1e-9)


@pytest.mark.unit
def test_build_feed_out_sections_empty_storage_returns_empty_list() -> None:
    assert build_feed_out_sections([], feed_out_rate_kg_dm_per_day=100.0) == []


@pytest.mark.unit
def test_build_feed_out_sections_single_crop_returns_one_section(harvested_crop: HarvestedCrop) -> None:
    sections: list[FeedOutSection] = build_feed_out_sections([harvested_crop], feed_out_rate_kg_dm_per_day=1.0)

    assert len(sections) == 1
    assert sections[0].crops == [harvested_crop]
    assert sections[0].dry_matter_mass_kg == pytest.approx(harvested_crop.dry_matter_mass)


@pytest.mark.unit
def test_build_feed_out_sections_zero_rate_returns_one_section(harvested_crop: HarvestedCrop) -> None:
    """No Feed-out rate yet (storage hasn't been assigned one) — treat everything as a single section
    rather than dividing by zero computing NVS."""
    second_crop = copy.deepcopy(harvested_crop)
    sections = build_feed_out_sections([harvested_crop, second_crop], feed_out_rate_kg_dm_per_day=0.0)

    assert len(sections) == 1
    assert sections[0].crops == [harvested_crop, second_crop]


@pytest.mark.unit
def test_build_feed_out_sections_groups_multiple_crops_by_target_mass(harvested_crop: HarvestedCrop) -> None:
    """4 crops of 100 kg DM each (400 kg total), rate chosen so NVS = floor(400/(10*20)) = 2 — the 4
    crops must be grouped into exactly 2 sections, not left as 4 or collapsed to 1."""
    crops = [copy.deepcopy(harvested_crop) for _ in range(4)]
    for crop in crops:
        crop.dry_matter_mass = 100.0

    sections = build_feed_out_sections(crops, feed_out_rate_kg_dm_per_day=20.0)

    assert len(sections) == 2
    assert sum(len(section.crops) for section in sections) == 4
    assert sum(section.dry_matter_mass_kg for section in sections) == pytest.approx(400.0)


@pytest.mark.unit
def test_build_feed_out_sections_mass_weighted_average_composition() -> None:
    """Two crops of different mass and composition in one section: the section's ndf_fraction must be
    the *mass-weighted* average, not a plain (unweighted) average — proves the weighting is real."""
    light_crop = HarvestedCrop(**(sample_crop_data | {"dry_matter_mass": 10.0, "ndf": 10.0}))
    heavy_crop = HarvestedCrop(**(sample_crop_data | {"dry_matter_mass": 90.0, "ndf": 50.0}))

    # rate=0 forces a single section containing both crops (see the zero-rate test above).
    sections = build_feed_out_sections([light_crop, heavy_crop], feed_out_rate_kg_dm_per_day=0.0)

    assert len(sections) == 1
    plain_average = (10.0 + 50.0) / 2.0 * 0.01
    mass_weighted_average = (10.0 * 10.0 + 90.0 * 50.0) / 100.0 * 0.01
    assert sections[0].ndf_fraction == pytest.approx(mass_weighted_average)
    assert sections[0].ndf_fraction != pytest.approx(plain_average)


@pytest.mark.unit
def test_build_feed_out_sections_dry_matter_fraction_uses_total_dm_over_total_wet_mass() -> None:
    """`dry_matter_fraction` is NOT a mass-weighted average of each crop's own DM fraction — it is
    `total_DM / total_wet_mass` (Silostg.for:899,909). This test uses two crops with different DM%
    specifically to distinguish the two formulas."""
    # 10 kg DM @ 10% DM -> 100 kg wet; 90 kg DM @ 50% DM -> 180 kg wet.
    light_crop = HarvestedCrop(**(sample_crop_data | {"dry_matter_mass": 10.0, "dry_matter_percentage": 10.0}))
    heavy_crop = HarvestedCrop(**(sample_crop_data | {"dry_matter_mass": 90.0, "dry_matter_percentage": 50.0}))

    sections = build_feed_out_sections([light_crop, heavy_crop], feed_out_rate_kg_dm_per_day=0.0)

    naive_mass_weighted_average = (10.0 * 0.10 + 90.0 * 0.50) / 100.0  # the WRONG formula -> 0.46
    correct_total_over_total_wet = 100.0 / (100.0 + 180.0)  # the source's own formula -> ~0.3571
    assert sections[0].dry_matter_fraction == pytest.approx(correct_total_over_total_wet)
    assert sections[0].dry_matter_fraction != pytest.approx(naive_mass_weighted_average)


@pytest.mark.unit
def test_build_feed_out_sections_zero_fresh_mass_does_not_raise() -> None:
    """A crop with dry_matter_mass > 0 but dry_matter_percentage == 0 (an inconsistent but
    constructible HarvestedCrop state) makes `fresh_mass` return 0.0 — `dry_matter_fraction` must
    fall back to 0.0 rather than raising ZeroDivisionError."""
    degenerate_crop = HarvestedCrop(**(sample_crop_data | {"dry_matter_mass": 10.0, "dry_matter_percentage": 0.0}))

    sections = build_feed_out_sections([degenerate_crop], feed_out_rate_kg_dm_per_day=0.0)

    assert sections[0].dry_matter_fraction == 0.0


@pytest.mark.unit
def test_build_feed_out_sections_is_alfalfa_matches_section_own_first_crop() -> None:
    """A single section's crop-type flag matches its own first crop, not a majority vote or the last
    crop."""
    alfalfa_crop = HarvestedCrop(**(sample_crop_data | {"config_name": "alfalfa_data", "dry_matter_mass": 10.0}))
    corn_crop = HarvestedCrop(**(sample_crop_data | {"config_name": "corn_data", "dry_matter_mass": 90.0}))

    sections = build_feed_out_sections([alfalfa_crop, corn_crop], feed_out_rate_kg_dm_per_day=0.0)

    assert sections[0].is_alfalfa is True


@pytest.mark.unit
def test_build_feed_out_sections_is_alfalfa_is_per_section_not_storage_wide() -> None:
    """A storage refilled with a different crop type over time, split into 2+ sections, must give
    EACH section its OWN first crop's type — not `Silostg.for:923`'s literal behavior of stamping
    every section with the storage's single very-first crop (a deliberate, documented design-spec
    deviation). 4 corn crops (100 kg DM each) then 4 alfalfa crops (100 kg DM each), rate chosen so
    NVS = floor(800/(10*40)) = 2 — the corn crops must group into the first section and the alfalfa
    crops into the second, giving each section a DIFFERENT is_alfalfa, not both False (which
    storage-wide first-crop typing would produce)."""
    corn_crops = [
        HarvestedCrop(**(sample_crop_data | {"config_name": "corn_data", "dry_matter_mass": 100.0})) for _ in range(4)
    ]
    alfalfa_crops = [
        HarvestedCrop(**(sample_crop_data | {"config_name": "alfalfa_data", "dry_matter_mass": 100.0}))
        for _ in range(4)
    ]

    sections = build_feed_out_sections(corn_crops + alfalfa_crops, feed_out_rate_kg_dm_per_day=40.0)

    assert len(sections) == 2
    assert sections[0].is_alfalfa is False
    assert sections[1].is_alfalfa is True


@pytest.mark.unit
def test_build_feed_out_sections_trailing_zero_mass_crop_does_not_spawn_extra_section(
    harvested_crop: HarvestedCrop,
) -> None:
    """A depleted crop (dry_matter_mass == 0.0 — e.g. already fully fed out via
    `remove_dry_matter_mass` but not yet purged from `self.stored`) sitting after the last real
    section boundary must not spawn its own spurious extra section. This is exactly what the
    `len(sections) < number_of_sections - 1` guard in `build_feed_out_sections` exists to prevent —
    a test that only checks total section count for zero-mass-free inputs would not catch that guard
    being deleted."""
    first_crop = copy.deepcopy(harvested_crop)
    first_crop.dry_matter_mass = 100.0
    second_crop = copy.deepcopy(harvested_crop)
    second_crop.dry_matter_mass = 100.0
    depleted_crop = copy.deepcopy(harvested_crop)
    depleted_crop.dry_matter_mass = 0.0

    sections = build_feed_out_sections([first_crop, second_crop, depleted_crop], feed_out_rate_kg_dm_per_day=10.0)

    assert len(sections) == 2
    assert sections[0].crops == [first_crop]
    assert sections[1].crops == [second_crop, depleted_crop]


@pytest.mark.component
@pytest.mark.parametrize(
    "storage_class,extra_config",
    [
        (Bunker, {"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}),
        (Bag, {"diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}),
    ],
)
def test_full_ensiling_chain_stays_under_total_dry_matter(
    mocker: MockerFixture,
    mock_silage_config: dict[str, str | float | list[str]],
    storage_class: type[Silage],
    extra_config: dict[str, float],
) -> None:
    """A crop run through Preseal, Effluent, Fermentation, and Infiltration never loses >= 100% DM."""
    config = dict(mock_silage_config)
    config.update(extra_config)
    storage = storage_class(config=config)
    first_crop = HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0})
    second_crop = replace(
        HarvestedCrop(**{**sample_crop_data, "config_name": "corn_silage", "dry_matter_percentage": 35.0}),
        storage_time=first_crop.storage_time + timedelta(days=1),
    )
    initial_mass = first_crop.dry_matter_mass

    storage.receive_crop(first_crop, simulation_day=1)
    storage.receive_crop(second_crop, simulation_day=2)

    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 32
    mock_time.current_date.date.return_value = first_crop.storage_time + timedelta(days=30)

    storage.process_degradations(mock_weather, mock_time)

    assert 0.0 < first_crop.dry_matter_mass < initial_mass
    assert first_crop.infiltration_cumulative_loss_kg > 0.0


@pytest.mark.unit
def test_get_or_compute_feed_out_rate_empty_storage_returns_zero_and_does_not_cache(silage: Silage) -> None:
    """An empty storage has no Feed-out rate yet — returns 0.0 without permanently freezing at 0.0,
    so a later call (once crops exist) can still compute a real rate."""
    assert silage.stored == []

    rate = silage._get_or_compute_feed_out_rate_kg_dm_per_day()

    assert rate == 0.0
    assert silage._feed_out_rate_kg_dm_per_day is None


@pytest.mark.unit
def test_get_or_compute_feed_out_rate_computes_total_over_365(silage: Silage, harvested_crop: HarvestedCrop) -> None:
    """Silostg.for:233,242 — FDRTE = total stored DM / 365."""
    silage.stored = [harvested_crop]

    rate = silage._get_or_compute_feed_out_rate_kg_dm_per_day()

    assert rate == pytest.approx(harvested_crop.dry_matter_mass / 365.0)


@pytest.mark.unit
def test_get_or_compute_feed_out_rate_held_between_receipts(silage: Silage, harvested_crop: HarvestedCrop) -> None:
    """Between crop receipts the rate is held: a change to self.stored (Effluent/Fermentation/
    Infiltration shrinking a crop) must NOT change the already-computed rate."""
    silage.stored = [harvested_crop]
    first_rate = silage._get_or_compute_feed_out_rate_kg_dm_per_day()

    harvested_crop.dry_matter_mass *= 0.5
    second_rate = silage._get_or_compute_feed_out_rate_kg_dm_per_day()

    assert second_rate == first_rate


@pytest.mark.unit
def test_get_or_compute_feed_out_rate_recomputed_after_crop_received(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop
) -> None:
    """A later receipt resets the rate, so the next call recomputes it from the total now stored
    (stored DM / 365). A small first batch must not fix a small rate for the rest of the run."""
    mocker.patch.object(silage, "_finalize_preseal_loss")
    first_crop = copy.deepcopy(harvested_crop)
    first_crop.dry_matter_mass = 20.0
    silage.receive_crop(first_crop, simulation_day=1)
    first_rate = silage._get_or_compute_feed_out_rate_kg_dm_per_day()
    assert first_rate == pytest.approx(20.0 / 365.0)

    second_crop = copy.deepcopy(harvested_crop)
    second_crop.dry_matter_mass = 480.0
    silage.receive_crop(second_crop, simulation_day=2)
    second_rate = silage._get_or_compute_feed_out_rate_kg_dm_per_day()

    total_dry_matter_kg = sum(crop.dry_matter_mass for crop in silage.stored)
    assert second_rate == pytest.approx(total_dry_matter_kg / 365.0)
    assert second_rate > first_rate


@pytest.mark.unit
def test_apply_feed_out_loss_dilutes_both_ndf_and_crude_protein(harvested_crop: HarvestedCrop, silage: Silage) -> None:
    """Unlike `_apply_infiltration_loss` (which deliberately leaves crude protein unchanged,
    Silostg.for:871-872,978-979), Feed-out DOES dilute crude protein (Silostg.for:1100) — this test
    exists specifically to catch the two being conflated."""
    initial_ndf = harvested_crop.ndf
    initial_cp = harvested_crop.crude_protein_percent
    initial_mass = harvested_crop.dry_matter_mass

    silage._apply_feed_out_loss(harvested_crop, dry_matter_loss_kg=initial_mass * 0.05)

    assert harvested_crop.dry_matter_mass == pytest.approx(initial_mass * 0.95)
    assert harvested_crop.ndf > initial_ndf
    assert harvested_crop.crude_protein_percent > initial_cp


@pytest.mark.unit
def test_apply_feed_out_loss_zero_loss_is_a_noop(harvested_crop: HarvestedCrop, silage: Silage) -> None:
    initial_mass = harvested_crop.dry_matter_mass
    silage._apply_feed_out_loss(harvested_crop, dry_matter_loss_kg=0.0)
    assert harvested_crop.dry_matter_mass == initial_mass


@pytest.mark.unit
def test_process_feed_out_default_raises_not_implemented(silage: Silage) -> None:
    with pytest.raises(NotImplementedError):
        silage._process_feed_out(elapsed_days=30.0)


@pytest.mark.unit
def test_bag_process_feed_out_reduces_mass(harvested_crop: HarvestedCrop) -> None:
    config: dict[str, str | float | list[str]] = {
        "name": "bag_silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
        "diameter_m": 3.0,
        "dry_matter_density_kg_per_m3": 180.0,
    }
    bag = Bag(config=config)
    bag.stored = [harvested_crop]
    initial_mass = harvested_crop.dry_matter_mass

    bag._process_feed_out(elapsed_days=30.0)

    assert harvested_crop.dry_matter_mass < initial_mass


@pytest.mark.unit
def test_bag_process_feed_out_skips_when_geometry_missing(harvested_crop: HarvestedCrop) -> None:
    config: dict[str, str | float | list[str]] = {
        "name": "bag_silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
    }
    bag = Bag(config=config)
    bag.stored = [harvested_crop]
    initial_mass = harvested_crop.dry_matter_mass

    bag._process_feed_out(elapsed_days=30.0)

    assert harvested_crop.dry_matter_mass == initial_mass


@pytest.mark.unit
@pytest.mark.parametrize("storage_class", [Bunker, Pile])
def test_bunker_process_feed_out_applies_same_fraction_within_a_section(
    storage_class: type[Silage], harvested_crop: HarvestedCrop
) -> None:
    """Crops grouped into the same section must lose the same *fraction* of their own dry matter —
    proves the section-uniform-loss semantics (design spec Section 5.3.2). The two small crops sit
    below the per-section target mass (total / 36), so they share section 1 with the large crop."""
    storage = _make_feed_out_storage(storage_class, harvested_crop, [10.0, 5.0, 985.0])
    initial_masses = [crop.dry_matter_mass for crop in storage.stored]

    storage._process_feed_out(elapsed_days=30.0)

    fractions_lost = [1.0 - crop.dry_matter_mass / initial for crop, initial in zip(storage.stored, initial_masses)]
    assert fractions_lost[0] > 0.0
    assert fractions_lost[1] == pytest.approx(fractions_lost[0])
    assert fractions_lost[2] == pytest.approx(fractions_lost[0])


@pytest.mark.unit
@pytest.mark.parametrize("storage_class_name", ["Bunker", "Pile"])
def test_bunker_process_feed_out_skips_when_geometry_missing(
    storage_class_name: str, harvested_crop: HarvestedCrop
) -> None:
    config: dict[str, str | float | list[str]] = {
        "name": "storage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
    }
    storage_class = Bunker if storage_class_name == "Bunker" else Pile
    storage = storage_class(config=config)
    storage.stored = [harvested_crop]
    initial_mass = harvested_crop.dry_matter_mass

    storage._process_feed_out(elapsed_days=30.0)

    assert harvested_crop.dry_matter_mass == initial_mass


def _make_feed_out_storage(storage_class: type[Silage], crop: HarvestedCrop, crop_masses: list[float]) -> Silage:
    """Builds a Bunker/Pile with one copy of `crop` per entry in `crop_masses` (kg DM, oldest first)."""
    config: dict[str, str | float | list[str]] = {
        "name": "storage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
        "width_m": 9.14,
        "height_m": 3.05,
        "dry_matter_density_kg_per_m3": 180.0,
    }
    storage = storage_class(config=config)
    storage.stored = []
    for mass in crop_masses:
        stored_crop = copy.deepcopy(crop)
        stored_crop.dry_matter_mass = mass
        storage.stored.append(stored_crop)
    return storage


@pytest.mark.unit
@pytest.mark.parametrize("storage_class", [Bunker, Pile])
def test_process_feed_out_total_loss_independent_of_call_frequency(
    storage_class: type[Silage], harvested_crop: HarvestedCrop
) -> None:
    """One 30-day call and two calls (10 days, then 20 days) lose the same dry matter: Feed-out is a
    fraction of the dry matter fed out, so it must not depend on how often process_degradations runs
    (production calls it only on harvest days, up to 30 days apart)."""
    one_call = _make_feed_out_storage(storage_class, harvested_crop, [500_000.0])
    two_calls = _make_feed_out_storage(storage_class, harvested_crop, [500_000.0])
    initial_mass = one_call.stored[0].dry_matter_mass

    one_call._process_feed_out(elapsed_days=30.0)
    two_calls._process_feed_out(elapsed_days=10.0)
    two_calls._process_feed_out(elapsed_days=20.0)

    loss_one_call = initial_mass - one_call.stored[0].dry_matter_mass
    loss_two_calls = initial_mass - two_calls.stored[0].dry_matter_mass
    assert loss_one_call > 0.0
    # Not exact: each call re-reads the crop's composition, which concentrates slightly as dry matter
    # is lost, so the second call's loss fraction differs by ~1e-4. The old per-call behaviour
    # differed by a factor of ~3 here.
    assert loss_two_calls == pytest.approx(loss_one_call, rel=1e-3)


@pytest.mark.unit
@pytest.mark.parametrize("storage_class", [Bunker, Pile])
def test_process_feed_out_loss_bounded_by_loss_fraction_times_fed_out_mass(
    storage_class: type[Silage], harvested_crop: HarvestedCrop
) -> None:
    """Each kg is hit once, so cumulative loss over many calls can never exceed the (RS-clipped) loss
    fraction times the mass fed out. 12 monthly calls on a 500 t bunker used to lose ~36% of DM."""
    storage = _make_feed_out_storage(storage_class, harvested_crop, [500_000.0])
    initial_mass = storage.stored[0].dry_matter_mass
    rate = storage._get_or_compute_feed_out_rate_kg_dm_per_day()

    for _ in range(12):
        storage._process_feed_out(elapsed_days=30.0)

    fed_out_kg = rate * 360.0
    lost_kg = initial_mass - storage.stored[0].dry_matter_mass
    assert 0.0 < lost_kg < 0.5 * fed_out_kg
    assert lost_kg / initial_mass < 0.05


@pytest.mark.unit
def test_process_feed_out_zero_elapsed_days_is_a_noop(harvested_crop: HarvestedCrop) -> None:
    storage = _make_feed_out_storage(Bunker, harvested_crop, [500_000.0])
    initial_mass = storage.stored[0].dry_matter_mass

    storage._process_feed_out(elapsed_days=0.0)

    assert storage.stored[0].dry_matter_mass == initial_mass


@pytest.mark.unit
def test_apply_feed_out_front_first_spills_to_next_group_and_leaves_the_rest(harvested_crop: HarvestedCrop) -> None:
    """Fed-out mass larger than the front group moves on to the next group; groups past the fed-out
    mass are untouched, and the loss is split by dry matter within a group."""
    silage = Silage(config=_make_feed_out_config())
    front, second, back_a, back_b = (copy.deepcopy(harvested_crop) for _ in range(4))
    front.dry_matter_mass = 100.0
    second.dry_matter_mass = 100.0
    back_a.dry_matter_mass = 300.0
    back_b.dry_matter_mass = 100.0

    # Fed out 150 kg: all of the front group (100 kg at 10%) then 50 kg of the second (at 20%).
    silage._apply_feed_out_front_first([([front], 0.10), ([second], 0.20), ([back_a, back_b], 0.50)], 150.0)

    assert front.dry_matter_mass == pytest.approx(100.0 - 0.10 * 100.0)
    assert second.dry_matter_mass == pytest.approx(100.0 - 0.20 * 50.0)
    assert back_a.dry_matter_mass == 300.0
    assert back_b.dry_matter_mass == 100.0


@pytest.mark.unit
def test_apply_feed_out_front_first_splits_group_loss_by_dry_matter(harvested_crop: HarvestedCrop) -> None:
    silage = Silage(config=_make_feed_out_config())
    crop_a, crop_b = copy.deepcopy(harvested_crop), copy.deepcopy(harvested_crop)
    crop_a.dry_matter_mass = 300.0
    crop_b.dry_matter_mass = 100.0

    # Whole 400 kg group fed out at a 10% loss fraction: 40 kg lost, 30 kg from A and 10 kg from B.
    silage._apply_feed_out_front_first([([crop_a, crop_b], 0.10)], 400.0)

    assert crop_a.dry_matter_mass == pytest.approx(270.0)
    assert crop_b.dry_matter_mass == pytest.approx(90.0)


@pytest.mark.unit
def test_process_degradations_passes_oldest_crops_elapsed_days_to_feed_out(
    mocker: MockerFixture, silage: Silage
) -> None:
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 40
    mock_time.current_date = datetime(2022, 3, 31)
    mocker.patch.object(silage, "_finalize_preseal_loss")
    mocker.patch.object(silage, "calculate_days_of_effluent_loss_to_process", return_value=0)
    mocker.patch.object(Storage, "process_degradations")
    mocker.patch.object(silage, "_process_infiltration", return_value=0.0)
    feed_out = mocker.patch.object(silage, "_process_feed_out")
    old_crop, new_crop = HarvestedCrop(**sample_crop_data), HarvestedCrop(**sample_crop_data)
    old_crop.last_time_degraded = datetime(2022, 3, 1).date()
    new_crop.last_time_degraded = datetime(2022, 3, 21).date()
    silage.stored = [old_crop, new_crop]

    silage.process_degradations(mock_weather, mock_time)

    feed_out.assert_called_once_with(30.0)


def _make_feed_out_config() -> dict[str, str | float | list[str]]:
    return {
        "name": "silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
    }


@pytest.mark.unit
def test_process_degradations_runs_infiltration_before_feed_out(mocker: MockerFixture, silage: Silage) -> None:
    """Extends the existing Effluent->Fermentation->Infiltration call-order regression test
    (test_process_degradations_runs_fermentation_before_infiltration) one phase further — Feed-out
    must run last, after Infiltration, not before or interleaved with it."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 15
    mocker.patch.object(silage, "_finalize_preseal_loss")
    mocker.patch.object(silage, "calculate_days_of_effluent_loss_to_process", return_value=0)
    call_order: list[str] = []

    def _record_fermentation(*args: Any, **kwargs: Any) -> None:
        call_order.append("fermentation")

    def _record_infiltration(crop: HarvestedCrop, elapsed_days: float) -> float:
        call_order.append("infiltration")
        return 0.0

    def _record_feed_out(elapsed_days: float) -> None:
        call_order.append("feed_out")

    mocker.patch.object(Storage, "process_degradations", side_effect=_record_fermentation)
    mocker.patch.object(silage, "_process_infiltration", side_effect=_record_infiltration)
    mocker.patch.object(silage, "_process_feed_out", side_effect=_record_feed_out)
    silage.stored = [HarvestedCrop(**sample_crop_data)]

    silage.process_degradations(mock_weather, mock_time)

    assert call_order == ["fermentation", "infiltration", "feed_out"]


@pytest.mark.component
def test_process_degradations_full_chain_bag_stays_under_100_percent_loss(mocker: MockerFixture) -> None:
    """Component test: a small synthetic Bag crop through Preseal -> Effluent -> Fermentation ->
    Infiltration -> Feed-out, all via process_degradations alone (no FeedManager involved, matching
    design spec Section 8's revised testing strategy) — total DM loss must stay under 100%."""
    config: dict[str, str | float | list[str]] = {
        "name": "bag_silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "capacity": 1_000_000.0,
        "diameter_m": 3.0,
        "dry_matter_density_kg_per_m3": 180.0,
    }
    bag = Bag(config=config)
    crop = HarvestedCrop(**sample_crop_data)
    crop.last_time_degraded = crop.storage_time - timedelta(days=60)
    bag.stored = [crop]
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 60
    mock_time.current_date.date.return_value = crop.storage_time
    initial_mass = crop.dry_matter_mass

    bag.process_degradations(mock_weather, mock_time)

    assert 0.0 <= crop.dry_matter_mass < initial_mass
