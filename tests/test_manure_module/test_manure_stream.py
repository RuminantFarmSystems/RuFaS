import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.manure_stream import ManureStream
from RUFAS.data_structures.pen_manure_data import PenManureData


@pytest.fixture
def manure_stream(mocker: MockerFixture) -> ManureStream:
    return ManureStream(1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, mocker.MagicMock(autospec=PenManureData))


def test_total_volatile_solids(manure_stream: ManureStream) -> None:
    """Checks that the property method correctly calculated total_volatile_solids."""
    assert manure_stream.total_volatile_solids == 16.5


def test_mass(manure_stream: ManureStream) -> None:
    """Checks that the property method correctly calculated mass."""
    assert manure_stream.mass == 11


def test_volume(manure_stream: ManureStream) -> None:
    pass


def test_clear_pen_manure_data(manure_stream: ManureStream) -> None:
    """Checks that the method correctly clears the pen manure data instance"""
    manure_stream.clear_pen_manure_data()
    assert manure_stream.pen_manure_data is None


def test_add() -> None:
    pass
