import pytest

from RUFAS.routines.animal.life_cycle.body_weight_history import BodyWeightHistory


@pytest.mark.parametrize(
    'sim_day, days_born, body_weight',
    [
        (1, 10, 15.5),
        (2, 20, 20.2),
        (100, 200, 50.5),
    ]
)
def test_body_weight_history_initialization(sim_day: int, days_born: int, body_weight: float) -> None:
    """
    Unit test for the initialization of the BodyWeightHistory object in body_weight_history.py.

    This test checks that the BodyWeightHistory object is initialized correctly with the provided
    simulation day, days born, and body weight values.
    """
    # Act
    bw_history = BodyWeightHistory(sim_day, days_born, body_weight)

    # Assert
    assert bw_history.simulation_day == sim_day, 'simulation_day not initialized correctly'
    assert bw_history.days_born == days_born, 'days_born not initialized correctly'
    assert bw_history.body_weight == body_weight, 'body_weight not initialized correctly'
