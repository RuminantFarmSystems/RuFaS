import pytest

from RUFAS.routines.animal.life_cycle.pen_history import PenHistory


@pytest.mark.parametrize(
    'start_date, end_date, pen, classes_in_pen',
    [
        (1, 10, 'pen1', ['class1', 'class2']),
        (5, 20, 'pen2', ['class3']),
        (100, 200, 'pen3', ['class1', 'class2', 'class3']),
    ]
)
def test_pen_history_initialization(start_date: int, end_date: int, pen, classes_in_pen: list[str]) -> None:
    """
    Unit test for the initialization of the PenHistory object in pen_history.py.

    This test checks that the PenHistory object is initialized correctly with the provided
    start date, end date, specific pen object, and the classes of animals that have been in the pen.
    """
    # Act
    pen_history = PenHistory(start_date, end_date, pen, classes_in_pen)

    # Assert
    assert pen_history.start_date == start_date, 'start_date not initialized correctly'
    assert pen_history.end_date == end_date, 'end_date not initialized correctly'
    assert pen_history.pen == pen, 'pen not initialized correctly'
    assert pen_history.classes_in_pen == classes_in_pen, 'classes_in_pen not initialized correctly'
