import copy
from typing import Any
from unittest.mock import call
from dataclasses import replace
from datetime import date, datetime, timedelta
import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.feed_storage.silage import (  # noqa: F401
    Bag,
    Bunker,
    Pile,
    Silage,
    calculate_preseal_loss,
    _clamp_preseal_fraction,
    PRESEAL_FALLBACK_EXPOSURE_DAYS,
    PRESEAL_EXPOSURE_CAP_DAYS,
)
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
    super_process_degradations = mocker.patch("RUFAS.biophysical.feed_storage.storage.Storage.process_degradations")
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
    expected_loss_values = {
        "dry_matter_mass": 800.0,
        "dry_matter_percentage": 14.0,
        "non_protein_nitrogen": 3.0,
        "crude_protein_percent": 5.0,
    }
    silage.stored = [replace(harvested_crop) for _ in range(3)]
    degraded_crops = [replace(crop, **expected_loss_values) for crop in silage.stored]
    calc_effluent_loss = mocker.patch.object(
        silage, "_calculate_effluent_loss", side_effect=[copy.copy(effluent_loss_values) for _ in range(3)]
    )
    process_degradations = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.project_degradations", return_value=degraded_crops
    )

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
def test_bunker_requires_positive_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bunker raises ValueError if width_m, height_m, or dry_matter_density_kg_per_m3 is missing or non-positive."""
    config = dict(mock_silage_config)
    config.pop("size", None)
    for missing_key in ("width_m", "height_m", "dry_matter_density_kg_per_m3"):
        bad_config = {**config, "width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
        del bad_config[missing_key]
        with pytest.raises(ValueError, match=missing_key):
            Bunker(config=bad_config)


@pytest.mark.unit
def test_bunker_stores_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bunker stores width_m, height_m, and dry_matter_density_kg_per_m3 from config."""
    config = dict(mock_silage_config)
    config.pop("size", None)
    config.update({"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})

    bunker = Bunker(config=config)

    assert bunker.width_m == 10.0
    assert bunker.height_m == 3.0
    assert bunker.dry_matter_density_kg_per_m3 == 180.0


@pytest.mark.unit
def test_pile_requires_positive_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Pile raises ValueError if width_m, height_m, or dry_matter_density_kg_per_m3 is missing or non-positive."""
    config = dict(mock_silage_config)
    config.pop("size", None)
    for missing_key in ("width_m", "height_m", "dry_matter_density_kg_per_m3"):
        bad_config = {**config, "width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
        del bad_config[missing_key]
        with pytest.raises(ValueError, match=missing_key):
            Pile(config=bad_config)


@pytest.mark.unit
def test_pile_stores_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Pile stores width_m, height_m, and dry_matter_density_kg_per_m3 from config."""
    config = dict(mock_silage_config)
    config.pop("size", None)
    config.update({"width_m": 10.0, "height_m": 3.0, "dry_matter_density_kg_per_m3": 180.0})

    pile = Pile(config=config)

    assert pile.width_m == 10.0
    assert pile.height_m == 3.0
    assert pile.dry_matter_density_kg_per_m3 == 180.0


@pytest.mark.unit
def test_bag_requires_positive_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bag raises ValueError if diameter_m or dry_matter_density_kg_per_m3 is missing or non-positive."""
    config = dict(mock_silage_config)
    config.pop("size", None)
    for missing_key in ("diameter_m", "dry_matter_density_kg_per_m3"):
        bad_config = {**config, "diameter_m": 3.0, "dry_matter_density_kg_per_m3": 180.0}
        del bad_config[missing_key]
        with pytest.raises(ValueError, match=missing_key):
            Bag(config=bad_config)


@pytest.mark.unit
def test_bag_stores_geometry_and_density(mock_silage_config: dict[str, str | float | list[str]]) -> None:
    """Bag stores diameter_m and dry_matter_density_kg_per_m3 from config."""
    config = dict(mock_silage_config)
    config.pop("size", None)
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
    mocker.patch("RUFAS.biophysical.feed_storage.storage.Storage.process_degradations")
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
    mocker.patch("RUFAS.biophysical.feed_storage.storage.Storage.process_degradations")
    silage.stored = [harvested_crop]

    silage.process_degradations(mock_weather, mock_time)

    finalize.assert_not_called()
