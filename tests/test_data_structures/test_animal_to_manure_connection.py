from typing import Optional, Type
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.animal_to_manure_connection import ManureStream, StreamType, PenManureData


@pytest.fixture
def manure_stream(mocker: MockerFixture) -> ManureStream:
    return ManureStream(1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 8.8, 7.7, 10, 9.9, 10, 0.24,
                        mocker.MagicMock(autospec=PenManureData))


def test_total_volatile_solids(manure_stream: ManureStream) -> None:
    """Checks that the property method correctly calculated total_volatile_solids."""
    assert manure_stream.total_volatile_solids == 26.5


def test_mass(manure_stream: ManureStream) -> None:
    """Checks that the property method correctly calculated mass."""
    assert manure_stream.mass == 11


def test_clear_pen_manure_data(manure_stream: ManureStream) -> None:
    """Checks that the method correctly clears the pen manure data instance"""
    manure_stream.clear_pen_manure_data()
    assert manure_stream.pen_manure_data is None


@pytest.fixture
def manure_stream_1() -> ManureStream:
    pen_data = PenManureData(
        num_animals=10,
        manure_deposition_surface_area=100.0,
        animal_combination=AnimalCombination.LAC_COW,
        pen_type="Type A",
        manure_urine_mass=50.0,
        manure_urine_nitrogen=5.0,
        stream_type=StreamType.PARLOR,
    )
    return ManureStream(
        water=1000.0,
        ammoniacal_nitrogen=10.0,
        nitrogen=20.0,
        phosphorus=5.0,
        potassium=3.0,
        ash=15.0,
        non_degradable_volatile_solids=25.0,
        degradable_volatile_solids=35.0,
        total_solids=60.0,
        volume=1.0,
        methane_production_potential=0.24,
        pen_manure_data=pen_data,
        bedding_non_degradable_volatile_solids=10
    )


@pytest.mark.parametrize(
    "other_stream, expected_error, expected_values",
    [
        # Case 1: Successful addition of two compatible streams
        (
            ManureStream(
                water=800.0,
                ammoniacal_nitrogen=8.0,
                nitrogen=16.0,
                phosphorus=4.0,
                potassium=2.5,
                ash=12.0,
                non_degradable_volatile_solids=20.0,
                degradable_volatile_solids=28.0,
                total_solids=48.0,
                volume=0.8,
                methane_production_potential=0.17,
                pen_manure_data=PenManureData(
                    num_animals=5,
                    manure_deposition_surface_area=50.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="Type B",
                    manure_urine_mass=30.0,
                    manure_urine_nitrogen=3.0,
                    stream_type=StreamType.PARLOR,
                ),
                bedding_non_degradable_volatile_solids=2
            ),
            None,
            {
                "water": 1800.0,
                "ammoniacal_nitrogen": 18.0,
                "nitrogen": 36.0,
                "phosphorus": 9.0,
                "potassium": 5.5,
                "ash": 27.0,
                "total_solids": 108.0,
                "volume": 1.8,
                "methane_production_potential": 0.21083333,
                "pen_data_num_animals": 15,
            },
        ),
        # Case 2: Addition with missing pen manure data
        (
            ManureStream(
                water=500.0,
                ammoniacal_nitrogen=5.0,
                nitrogen=10.0,
                phosphorus=2.5,
                potassium=1.5,
                ash=8.0,
                non_degradable_volatile_solids=10.0,
                degradable_volatile_solids=15.0,
                total_solids=25.0,
                volume=0.5,
                methane_production_potential=0.17,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=2
            ),
            None,
            {
                "water": 1500.0,
                "ammoniacal_nitrogen": 15.0,
                "nitrogen": 30.0,
                "phosphorus": 7.5,
                "potassium": 4.5,
                "ash": 23.0,
                "total_solids": 85.0,
                "volume": 1.5,
                "methane_production_potential": 0.2205154,
                "pen_data_num_animals": None,
            },
        ),
    ],
)
def test_add_manure_streams(
    manure_stream_1: ManureStream,
    other_stream: ManureStream,
    expected_error: Optional[Type[Exception]],
    expected_values: Optional[dict[str, float]],
) -> None:
    if expected_error:
        with pytest.raises(
            expected_error, match="Cannot combine PenManureData instances with different animal combinations."
        ):
            _ = manure_stream_1 + other_stream
    else:
        combined = manure_stream_1 + other_stream

        assert expected_values is not None
        assert combined.water == expected_values["water"]
        assert combined.ammoniacal_nitrogen == expected_values["ammoniacal_nitrogen"]
        assert combined.nitrogen == expected_values["nitrogen"]
        assert combined.phosphorus == expected_values["phosphorus"]
        assert combined.potassium == expected_values["potassium"]
        assert combined.ash == expected_values["ash"]
        assert combined.total_solids == expected_values["total_solids"]
        assert combined.volume == expected_values["volume"]
        assert pytest.approx(combined.methane_production_potential) == expected_values["methane_production_potential"]

        if expected_values["pen_data_num_animals"] is not None:
            assert combined.pen_manure_data is not None
            assert combined.pen_manure_data.num_animals == expected_values["pen_data_num_animals"]
        else:
            assert combined.pen_manure_data is None


def test_make_empty_manure_stream() -> None:
    """Tests that a new, empty ManureStream is created correctly."""
    actual = ManureStream.make_empty_manure_stream()

    assert actual.ammoniacal_nitrogen == 0.0
    assert actual.ash == 0.0
    assert actual.degradable_volatile_solids == 0.0
    assert actual.nitrogen == 0.0
    assert actual.non_degradable_volatile_solids == 0.0
    assert actual.pen_manure_data is None
    assert actual.phosphorus == 0.0
    assert actual.potassium == 0.0
    assert actual.total_solids == 0.0


@pytest.mark.parametrize(
    "enum_member, expected_value, expected_name",
    [
        (StreamType.PARLOR, "parlor", "PARLOR"),
        (StreamType.GENERAL, "general", "GENERAL"),
    ],
)
def test_manure_stream_type_members(enum_member: StreamType, expected_value: str, expected_name: str) -> None:
    """Test that enum members have the correct values and names."""
    assert enum_member.value == expected_value
    assert enum_member.name == expected_name
    assert StreamType.PARLOR in StreamType
    assert StreamType.GENERAL in StreamType


@pytest.fixture
def pen_data_1() -> PenManureData:
    return PenManureData(
        num_animals=10,
        manure_deposition_surface_area=100.0,
        animal_combination=AnimalCombination.LAC_COW,
        pen_type="Type A",
        manure_urine_mass=50.0,
        manure_urine_nitrogen=5.0,
        stream_type=StreamType.PARLOR,
    )


@pytest.fixture
def pen_data_2() -> PenManureData:
    return PenManureData(
        num_animals=5,
        manure_deposition_surface_area=50.0,
        animal_combination=AnimalCombination.LAC_COW,
        pen_type="Type B",
        manure_urine_mass=30.0,
        manure_urine_nitrogen=3.0,
        stream_type=StreamType.PARLOR,
    )


@pytest.mark.parametrize(
    "stream_type, animal_combination, expect_error",
    [
        (StreamType.PARLOR, AnimalCombination.LAC_COW, False),
        (StreamType.GENERAL, AnimalCombination.CLOSE_UP, False),
        (StreamType.PARLOR, AnimalCombination.CLOSE_UP, True),
    ],
)
def test_pen_manure_data_init(
    stream_type: StreamType,
    animal_combination: AnimalCombination,
    expect_error: bool,
) -> None:
    """Test initialization of PenManureData with different stream types and animal combinations."""
    if expect_error:
        with pytest.raises(ValueError, match="Manure from a non-lactating pen assigned to parlor manure stream."):
            PenManureData(
                num_animals=10,
                manure_deposition_surface_area=100.0,
                animal_combination=animal_combination,
                pen_type="Type A",
                manure_urine_mass=50.0,
                manure_urine_nitrogen=5.0,
                stream_type=stream_type,
            )
    else:
        data = PenManureData(
            num_animals=10,
            manure_deposition_surface_area=100.0,
            animal_combination=animal_combination,
            pen_type="Type A",
            manure_urine_mass=50.0,
            manure_urine_nitrogen=5.0,
            stream_type=stream_type,
        )
        assert data.stream_type == stream_type
        assert data.animal_combination == animal_combination


def test_pen_manure_data_add_valid(pen_data_1: PenManureData, pen_data_2: PenManureData) -> None:
    """Test successful addition of two compatible PenManureData instances."""
    combined = pen_data_1 + pen_data_2

    assert combined.num_animals == 15
    assert combined.manure_deposition_surface_area == 150.0
    assert combined.manure_urine_mass == 80.0
    assert combined.manure_urine_nitrogen == 8.0
    assert combined.stream_type == StreamType.PARLOR
    assert combined.animal_combination == AnimalCombination.LAC_COW
    assert combined.pen_type is None


def test_set_first_processor_updates_value(pen_data_1: PenManureData) -> None:
    """Test that set_first_processor correctly updates the attribute."""
    assert pen_data_1.first_processor is None
    pen_data_1.set_first_processor("Separator_A")
    assert pen_data_1.first_processor == "Separator_A"


def test_pen_manure_data_add_mismatched_first_processors(pen_data_1: PenManureData) -> None:
    """Test that combining PenManureData instances with different first processors raises an error."""
    pen_data_1.set_first_processor("Separator_A")

    pen_data_2 = PenManureData(
        num_animals=5,
        manure_deposition_surface_area=50.0,
        animal_combination=pen_data_1.animal_combination,
        pen_type=pen_data_1.pen_type,
        manure_urine_mass=25.0,
        manure_urine_nitrogen=2.0,
        stream_type=StreamType.PARLOR,
        first_processor="Separator_B",
    )

    with pytest.raises(ValueError, match="Cannot combine PenManureData instances with different first processors."):
        _ = pen_data_1 + pen_data_2


def test_pen_manure_data_add_invalid_stream_type(pen_data_1: PenManureData) -> None:
    """Test that adding PenManureData instances with a general stream type raises an error."""
    pen_data_general = PenManureData(
        num_animals=8,
        manure_deposition_surface_area=80.0,
        animal_combination=AnimalCombination.LAC_COW,
        pen_type="Type C",
        manure_urine_mass=40.0,
        manure_urine_nitrogen=4.0,
        stream_type=StreamType.GENERAL,
    )

    with pytest.raises(ValueError, match="Cannot combine PenManureData instances with a general manure stream type."):
        _ = pen_data_1 + pen_data_general


def test_manure_stream_is_empty() -> None:
    """Test that ManureStream.is_empty() returns True for an empty stream."""
    empty_stream = ManureStream.make_empty_manure_stream()
    assert empty_stream.is_empty
    non_empty_stream = ManureStream(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0.24, None, 10)
    assert not non_empty_stream.is_empty


@pytest.fixture
def sample_manure_stream(pen_data_2: PenManureData) -> ManureStream:
    return ManureStream(
        water=100.0,
        ammoniacal_nitrogen=10.0,
        nitrogen=20.0,
        phosphorus=5.0,
        potassium=3.0,
        ash=2.0,
        non_degradable_volatile_solids=4.0,
        degradable_volatile_solids=6.0,
        total_solids=15.0,
        volume=1.0,
        methane_production_potential=0.24,
        pen_manure_data=pen_data_2,
        bedding_non_degradable_volatile_solids=10
    )


def test_split_stream_valid(sample_manure_stream: ManureStream) -> None:
    split_ratio = 0.5
    stream_type = StreamType.PARLOR

    split = sample_manure_stream.split_stream(split_ratio=split_ratio, stream_type=stream_type)

    assert split.water == 50.0
    assert split.nitrogen == 10.0
    assert split.total_solids == 7.5
    assert split.volume == 0.5

    assert split.pen_manure_data is not None
    assert split.pen_manure_data.num_animals == 5
    assert split.pen_manure_data.stream_type == stream_type
    assert split.pen_manure_data.manure_urine_mass == 15.0
    assert split.methane_production_potential == sample_manure_stream.methane_production_potential


def test_split_stream_invalid_ratios(sample_manure_stream: ManureStream) -> None:
    with pytest.raises(ValueError, match="Split ratio must be greater than 0 and less than 1."):
        sample_manure_stream.split_stream(-0.1)

    with pytest.raises(ValueError, match="Split ratio must be greater than 0 and less than 1."):
        sample_manure_stream.split_stream(1.5)


def test_split_stream_without_pen_manure_data() -> None:
    stream = ManureStream(
        water=50.0,
        ammoniacal_nitrogen=5.0,
        nitrogen=10.0,
        phosphorus=2.5,
        potassium=1.5,
        ash=1.0,
        non_degradable_volatile_solids=2.0,
        degradable_volatile_solids=3.0,
        total_solids=7.5,
        volume=0.5,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10
    )

    split = stream.split_stream(0.5, stream_type=StreamType.GENERAL)
    assert split.pen_manure_data is None
    assert split.water == 25.0
    assert split.methane_production_potential == stream.methane_production_potential
