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
