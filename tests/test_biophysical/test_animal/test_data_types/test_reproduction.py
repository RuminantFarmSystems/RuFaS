import pytest

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.reproduction import (
    AnimalReproductionStatistics,
    HerdReproductionStatistics,
    ReproductionDataStream,
    ReproductionInputs,
    ReproductionOutputs,
)


@pytest.fixture
def sample_animal_events() -> AnimalEvents:
    """Fixture for an empty AnimalEvents instance."""
    return AnimalEvents()


@pytest.fixture
def sample_animal_statistics() -> AnimalReproductionStatistics:
    """Fixture for an empty AnimalReproductionStatistics instance."""
    return AnimalReproductionStatistics()


@pytest.fixture
def sample_herd_statistics() -> HerdReproductionStatistics:
    """Fixture for an empty HerdReproductionStatistics instance."""
    return HerdReproductionStatistics()


@pytest.fixture
def reproduction_inputs() -> ReproductionInputs:
    """Fixture for a sample ReproductionInputs instance."""
    return ReproductionInputs(
        animal_type=AnimalType.LAC_COW,
        body_weight=650.0,
        breed=Breed.HO,
        days_born=1000,
        days_in_pregnancy=150,
        days_in_milk=200,
        net_merit=5.0,
        phosphorus_for_gestation_required_for_calf=0.8,
    )


def test_repro_stats_initial_values_are_stored_correctly() -> None:
    """Verify that initialization arguments are preserved in the dataclass."""
    stats = AnimalReproductionStatistics(
        ED_days=12,
        estrus_count=3,
        GnRH_injections=2,
        PGF_injections=1,
        CIDR_injections=1,
        semen_number=4,
        AI_times=5,
        pregnancy_diagnoses=2,
        calving_to_pregnancy_time=150,
    )

    assert stats.ED_days == 12
    assert stats.estrus_count == 3
    assert stats.GnRH_injections == 2
    assert stats.PGF_injections == 1
    assert stats.CIDR_injections == 1
    assert stats.semen_number == 4
    assert stats.AI_times == 5
    assert stats.pregnancy_diagnoses == 2
    assert stats.calving_to_pregnancy_time == 150


def test_repro_stats_reset_daily_statistics_zeroes_expected_fields() -> None:
    """reset_daily_statistics should reset ONLY the daily counters."""
    stats = AnimalReproductionStatistics(
        ED_days=20,
        estrus_count=7,
        GnRH_injections=3,
        PGF_injections=2,
        CIDR_injections=1,
        semen_number=5,
        AI_times=4,
        pregnancy_diagnoses=1,
        calving_to_pregnancy_time=200,
    )

    stats.reset_daily_statistics()

    assert stats.GnRH_injections == 0
    assert stats.PGF_injections == 0
    assert stats.CIDR_injections == 0
    assert stats.semen_number == 0
    assert stats.AI_times == 0
    assert stats.pregnancy_diagnoses == 0

    assert stats.ED_days == 20
    assert stats.estrus_count == 7
    assert stats.calving_to_pregnancy_time == 200


@pytest.fixture
def reproduction_outputs(
    sample_animal_events: AnimalEvents,
) -> ReproductionOutputs:
    """Fixture for a sample ReproductionOutputs instance."""
    return ReproductionOutputs(
        body_weight=680.0,
        days_in_milk=220,
        days_in_pregnancy=160,
        events=sample_animal_events,
        phosphorus_for_gestation_required_for_calf=1.0,
        herd_reproduction_statistics=HerdReproductionStatistics(),
        newborn_calf_config=None,
    )


@pytest.fixture
def reproduction_data_stream(
    sample_animal_events: AnimalEvents,
) -> ReproductionDataStream:
    """Fixture for a sample ReproductionDataStream instance."""
    return ReproductionDataStream(
        animal_type=AnimalType.LAC_COW,
        body_weight=700.0,
        breed=Breed.HO,
        days_born=1200,
        days_in_pregnancy=170,
        days_in_milk=230,
        events=sample_animal_events,
        net_merit=6.5,
        phosphorus_for_gestation_required_for_calf=1.2,
        herd_reproduction_statistics=HerdReproductionStatistics(),
        newborn_calf_config=None,
    )


def test_reproduction_inputs_initialization(reproduction_inputs: ReproductionInputs) -> None:
    """Test that ReproductionInputs initializes with correct values."""
    assert reproduction_inputs.animal_type == AnimalType.LAC_COW
    assert reproduction_inputs.body_weight == 650.0
    assert reproduction_inputs.breed == Breed.HO
    assert reproduction_inputs.days_born == 1000
    assert reproduction_inputs.days_in_pregnancy == 150
    assert reproduction_inputs.days_in_milk == 200
    assert reproduction_inputs.net_merit == 5.0
    assert reproduction_inputs.phosphorus_for_gestation_required_for_calf == 0.8


@pytest.mark.parametrize(
    "total_ai, total_successful, expected_rate",
    [
        (10, 4, 0.4),
        (0, 0, 0.0),
    ],
    ids=["normal-rate", "no-ai-performed"],
)
def test_overall_conception_rate(total_ai: int, total_successful: int, expected_rate: float) -> None:
    """Test overall_conception_rate calculation in HerdReproductionStatistics."""
    stats = HerdReproductionStatistics(
        total_num_ai_performed=total_ai,
        total_num_successful_conceptions=total_successful,
    )

    assert stats.overall_conception_rate == pytest.approx(expected_rate)


@pytest.mark.parametrize(
    "heifer_ai, heifer_successful, expected_rate",
    [
        (12, 6, 0.5),
        (0, 0, 0.0),
    ],
    ids=["normal-rate", "no-ai-performed"],
)
def test_heifer_conception_rate(heifer_ai: int, heifer_successful: int, expected_rate: float) -> None:
    """Test heifer_conception_rate calculation in HerdReproductionStatistics."""
    stats = HerdReproductionStatistics(
        heifer_num_ai_performed=heifer_ai,
        heifer_num_successful_conceptions=heifer_successful,
    )

    assert stats.heifer_conception_rate == pytest.approx(expected_rate)


@pytest.mark.parametrize(
    "cow_ai, cow_successful, expected_rate",
    [
        (20, 8, 0.4),
        (0, 0, 0.0),
    ],
    ids=["normal-rate", "no-ai-performed"],
)
def test_cow_conception_rate(cow_ai: int, cow_successful: int, expected_rate: float) -> None:
    """Test cow_conception_rate calculation in HerdReproductionStatistics."""
    stats = HerdReproductionStatistics(
        cow_num_ai_performed=cow_ai,
        cow_num_successful_conceptions=cow_successful,
    )

    assert stats.cow_conception_rate == pytest.approx(expected_rate)


@pytest.mark.parametrize(
    "ai_ed, successful_ed, expected_rate",
    [
        (10, 3, 0.3),
        (0, 0, 0.0),
    ],
    ids=["normal-rate", "no-ai-performed"],
)
def test_heifer_ED_conception_rate(ai_ed: int, successful_ed: int, expected_rate: float) -> None:
    """Test heifer_ED_conception_rate calculation in HerdReproductionStatistics."""
    stats = HerdReproductionStatistics(
        heifer_num_ai_performed_in_ED=ai_ed,
        heifer_num_successful_conceptions_in_ED=successful_ed,
    )

    assert stats.heifer_ED_conception_rate == pytest.approx(expected_rate)


@pytest.mark.parametrize(
    "ai_tai, successful_tai, expected_rate",
    [
        (15, 9, 0.6),
        (0, 0, 0.0),
    ],
    ids=["normal-rate", "no-ai-performed"],
)
def test_heifer_TAI_conception_rate(ai_tai: int, successful_tai: int, expected_rate: float) -> None:
    """Test heifer_TAI_conception_rate calculation in HerdReproductionStatistics."""
    stats = HerdReproductionStatistics(
        heifer_num_ai_performed_in_TAI=ai_tai,
        heifer_num_successful_conceptions_in_TAI=successful_tai,
    )

    assert stats.heifer_TAI_conception_rate == pytest.approx(expected_rate)


@pytest.mark.parametrize(
    "ai_synched, successful_synched, expected_rate",
    [
        (8, 2, 0.25),
        (0, 0, 0.0),
    ],
    ids=["normal-rate", "no-ai-performed"],
)
def test_heifer_SynchED_conception_rate(ai_synched: int, successful_synched: int, expected_rate: float) -> None:
    """Test heifer_SynchED_conception_rate calculation in HerdReproductionStatistics."""
    stats = HerdReproductionStatistics(
        heifer_num_ai_performed_in_SynchED=ai_synched,
        heifer_num_successful_conceptions_in_SynchED=successful_synched,
    )

    assert stats.heifer_SynchED_conception_rate == pytest.approx(expected_rate)


def test_herd_reproduction_statistics_add() -> None:
    """Test addition of two HerdReproductionStatistics instances."""
    stats1 = HerdReproductionStatistics(
        total_num_ai_performed=10,
        total_num_successful_conceptions=4,
        heifer_num_ai_performed=6,
        heifer_num_ai_performed_in_ED=2,
        heifer_num_ai_performed_in_TAI=3,
        heifer_num_ai_performed_in_SynchED=1,
        heifer_num_successful_conceptions=3,
        heifer_num_successful_conceptions_in_ED=1,
        heifer_num_successful_conceptions_in_TAI=1,
        heifer_num_successful_conceptions_in_SynchED=1,
        cow_num_ai_performed=4,
        cow_num_successful_conceptions=2,
    )

    stats2 = HerdReproductionStatistics(
        total_num_ai_performed=5,
        total_num_successful_conceptions=3,
        heifer_num_ai_performed=4,
        heifer_num_ai_performed_in_ED=1,
        heifer_num_ai_performed_in_TAI=2,
        heifer_num_ai_performed_in_SynchED=1,
        heifer_num_successful_conceptions=2,
        heifer_num_successful_conceptions_in_ED=1,
        heifer_num_successful_conceptions_in_TAI=1,
        heifer_num_successful_conceptions_in_SynchED=0,
        cow_num_ai_performed=3,
        cow_num_successful_conceptions=1,
    )

    result = stats1 + stats2

    assert result.total_num_ai_performed == 15
    assert result.total_num_successful_conceptions == 7

    assert result.heifer_num_ai_performed == 10
    assert result.heifer_num_ai_performed_in_ED == 3
    assert result.heifer_num_ai_performed_in_TAI == 5
    assert result.heifer_num_ai_performed_in_SynchED == 2

    assert result.heifer_num_successful_conceptions == 5
    assert result.heifer_num_successful_conceptions_in_ED == 2
    assert result.heifer_num_successful_conceptions_in_TAI == 2
    assert result.heifer_num_successful_conceptions_in_SynchED == 1

    assert result.cow_num_ai_performed == 7
    assert result.cow_num_successful_conceptions == 3

    assert result is not stats1
    assert result is not stats2


@pytest.mark.parametrize("days_in_pregnancy, expected", [(150, True), (0, False)])
def test_reproduction_inputs_is_pregnant(
    reproduction_inputs: ReproductionInputs, days_in_pregnancy: int, expected: bool
) -> None:
    """Test is_pregnant property."""
    reproduction_inputs.days_in_pregnancy = days_in_pregnancy
    assert reproduction_inputs.is_pregnant == expected


@pytest.mark.parametrize("days_in_milk, expected", [(200, True), (0, False)])
def test_reproduction_inputs_is_milking(
    reproduction_inputs: ReproductionInputs, days_in_milk: int, expected: bool
) -> None:
    """Test is_milking property."""
    reproduction_inputs.days_in_milk = days_in_milk
    assert reproduction_inputs.is_milking == expected


def test_reproduction_outputs_initialization(reproduction_outputs: ReproductionOutputs) -> None:
    """Test that ReproductionOutputs initializes with correct values."""
    assert reproduction_outputs.body_weight == 680.0
    assert reproduction_outputs.days_in_milk == 220
    assert reproduction_outputs.days_in_pregnancy == 160
    assert isinstance(reproduction_outputs.events, AnimalEvents)
    assert reproduction_outputs.phosphorus_for_gestation_required_for_calf == 1.0
    assert reproduction_outputs.newborn_calf_config is None


def test_reproduction_outputs_is_pregnant(reproduction_outputs: ReproductionOutputs) -> None:
    """Test is_pregnant property for ReproductionOutputs."""
    assert reproduction_outputs.is_pregnant is True
    reproduction_outputs.days_in_pregnancy = 0
    assert reproduction_outputs.is_pregnant is False


def test_reproduction_outputs_is_milking(reproduction_outputs: ReproductionOutputs) -> None:
    """Test is_milking property for ReproductionOutputs."""
    assert reproduction_outputs.is_milking is True
    reproduction_outputs.days_in_milk = 0
    assert reproduction_outputs.is_milking is False


def test_reproduction_data_stream_initialization(reproduction_data_stream: ReproductionDataStream) -> None:
    """Test that ReproductionDataStream initializes with correct values."""
    assert reproduction_data_stream.animal_type == AnimalType.LAC_COW
    assert reproduction_data_stream.body_weight == 700.0
    assert reproduction_data_stream.breed == Breed.HO
    assert reproduction_data_stream.days_born == 1200
    assert reproduction_data_stream.days_in_pregnancy == 170
    assert reproduction_data_stream.days_in_milk == 230
    assert isinstance(reproduction_data_stream.events, AnimalEvents)
    assert reproduction_data_stream.net_merit == 6.5
    assert reproduction_data_stream.phosphorus_for_gestation_required_for_calf == 1.2
    assert reproduction_data_stream.newborn_calf_config is None


def test_reproduction_data_stream_is_pregnant(reproduction_data_stream: ReproductionDataStream) -> None:
    """Test is_pregnant property for ReproductionDataStream."""
    assert reproduction_data_stream.is_pregnant is True
    reproduction_data_stream.days_in_pregnancy = 0
    assert reproduction_data_stream.is_pregnant is False


def test_reproduction_data_stream_is_milking(reproduction_data_stream: ReproductionDataStream) -> None:
    """Test is_milking property for ReproductionDataStream."""
    assert reproduction_data_stream.is_milking is True
    reproduction_data_stream.days_in_milk = 0
    assert reproduction_data_stream.is_milking is False
