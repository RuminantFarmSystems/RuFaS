import pytest
from typing import Generator

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents


@pytest.fixture
def empty_animal_events() -> Generator[AnimalEvents, None, None]:
    """Fixture providing an empty AnimalEvents instance."""
    yield AnimalEvents()


@pytest.fixture
def populated_animal_events() -> Generator[AnimalEvents, None, None]:
    """Fixture providing an AnimalEvents instance with pre-added events."""
    events = AnimalEvents()
    events.add_event(10, 0, "Born")
    events.add_event(30, 5, "Vaccination")
    events.add_event(60, 10, "Weaning")
    yield events


def test_add_event(empty_animal_events: AnimalEvents) -> None:
    """Test adding an event to the AnimalEvents object."""
    empty_animal_events.add_event(15, 0, "First Feeding")
    assert 15 in empty_animal_events.events
    assert "First Feeding" in empty_animal_events.events[15]


def test_add_event_with_simulation_day(empty_animal_events: AnimalEvents) -> None:
    """Test adding an event with a non-zero simulation day."""
    empty_animal_events.add_event(20, 3, "Deworming")
    assert 20 in empty_animal_events.events
    assert "Deworming" in empty_animal_events.events[20]
    assert "simulation_day=3" in empty_animal_events.events[20]


def test_add_event_appends_to_existing_age(empty_animal_events: AnimalEvents) -> None:
    """Test that adding an event for an existing age appends instead of overwriting."""
    empty_animal_events.add_event(15, 0, "First Feeding")
    empty_animal_events.add_event(15, 0, "Vet Check")

    assert 15 in empty_animal_events.events
    assert len(empty_animal_events.events[15]) == 2
    assert "First Feeding" in empty_animal_events.events[15]
    assert "Vet Check" in empty_animal_events.events[15]


def test_get_most_recent_date(populated_animal_events: AnimalEvents) -> None:
    """Test retrieving the most recent event date."""
    assert populated_animal_events.get_most_recent_date("Weaning") == 60
    assert populated_animal_events.get_most_recent_date("Vaccination") == 30
    assert populated_animal_events.get_most_recent_date("Born") == 10
    assert populated_animal_events.get_most_recent_date("Unknown Event") == -1


def test_init_from_string(empty_animal_events: AnimalEvents) -> None:
    """Test initializing events from a formatted string."""
    events_str = "days born 5: ['Vaccination']\ndays born 15: ['Weaning']"
    empty_animal_events.init_from_string(events_str)

    assert 5 in empty_animal_events.events
    assert "vaccination" in empty_animal_events.events[5]
    assert 15 in empty_animal_events.events
    assert "weaning" in empty_animal_events.events[15]


def test_str_representation(populated_animal_events: AnimalEvents) -> None:
    """Test the string representation of the AnimalEvents object."""
    output_str = str(populated_animal_events)
    assert "days born 10" in output_str
    assert "days born 30" in output_str
    assert "days born 60" in output_str
    assert "Born" in output_str
    assert "Vaccination" in output_str
    assert "Weaning" in output_str


def test_add_operator_merge_events() -> None:
    """Test merging two AnimalEvents objects using the + operator."""
    events1 = AnimalEvents()
    events1.add_event(10, 0, "Born")

    events2 = AnimalEvents()
    events2.add_event(30, 5, "Vaccination")

    merged_events = events1 + events2

    assert 10 in merged_events.events
    assert "Born" in merged_events.events[10]
    assert 30 in merged_events.events
    assert "Vaccination" in merged_events.events[30]


def test_add_operator_combines_existing_events() -> None:
    """Test that merging two AnimalEvents objects appends events for the same age."""
    events1 = AnimalEvents()
    events1.add_event(10, 0, "Born")

    events2 = AnimalEvents()
    events2.add_event(10, 2, "Tagged")

    merged_events = events1 + events2

    assert 10 in merged_events.events
    assert "Born" in merged_events.events[10]
    assert "Tagged" in merged_events.events[10]
