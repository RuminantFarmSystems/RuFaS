import pytest

from RUFAS.routines.animal.life_cycle.pen_history import PenHistory
from RUFAS.enums import AnimalCombination


@pytest.mark.parametrize(
    "start_date, end_date, pen, animal_combination",
    [
        (1, 10, 1, AnimalCombination.CALF),
        (5, 20, 2, AnimalCombination.CLOSE_UP),
        (100, 200, 3, AnimalCombination.LAC_COW),
    ],
)
def test_pen_history_initialization(
    start_date: int, end_date: int, pen: int, animal_combination: AnimalCombination
) -> None:
    """
    Unit test for the initialization of the PenHistory object in pen_history.py.

    This test checks that the PenHistory object is initialized correctly with the provided
    start date, end date, specific pen object, and the animal combination in the pen.
    """
    # Act
    pen_history = PenHistory(start_date=start_date, end_date=end_date, pen=pen, animal_combination=animal_combination)

    # Assert
    assert pen_history["start_date"] == start_date, "start_date not initialized correctly"
    assert pen_history["end_date"] == end_date, "end_date not initialized correctly"
    assert pen_history["pen"] == pen, "pen not initialized correctly"
    assert pen_history["animal_combination"] == animal_combination, "animal_combination not initialized correctly"
