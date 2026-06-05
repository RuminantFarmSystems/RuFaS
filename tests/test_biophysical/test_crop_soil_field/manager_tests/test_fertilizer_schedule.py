from typing import List

import pytest

from RUFAS.data_structures.events import FertilizerEvent
from RUFAS.biophysical.field.manager.fertilizer_schedule import FertilizerSchedule


@pytest.mark.parametrize(
    "name,mix_names,years,days,nitrogen,phosphorus,potassium,depths,fractions,expected_err_msg",
    [
        (
            "test_1",
            ["name_1", "name_2"],
            [1992, 1991],
            [100],
            [10],
            [10],
            [10],
            [50.0],
            [0.4],
            "'test_1': expected all years to be > 0 and in non-descending order, received " "'[1992, 1991]'.",
        ),
        (
            "test_2",
            ["name_3"],
            [1996, 1997],
            [0, 366],
            [10],
            [10],
            [10],
            [0.0],
            [1.0],
            "'test_2': expected all days to be in range [1, 366], received '[0, 366]'.",
        ),
        (
            "test_3",
            ["test_mix"],
            [1991, 1992],
            [100],
            [-15, 10],
            [10],
            [10],
            [0.0],
            [1.0],
            "'test_3': expected all nitrogen masses to be in >= 0, received '[-15, 10]'.",
        ),
        (
            "test_4",
            ["mix_1", "mix_2"],
            [1993, 1994],
            [100],
            [10],
            [10, -15],
            [10],
            [0.0],
            [1.0],
            "'test_4': expected all phosphorus masses to be in >= 0, received '[10, -15]'.",
        ),
        (
            "test_5",
            ["chex_mix"],
            [1990, 1992],
            [100],
            [10],
            [10],
            [10],
            [-30.0, 30.0],
            [0.8],
            "'test_5': expected all application depths to be in >= 0, received '[-30.0, 30.0]'.",
        ),
        (
            "test_6",
            ["mix_4"],
            [1991, 1991],
            [100, 200],
            [10],
            [10],
            [10],
            [0.0],
            [1.0, 1.02],
            "'test_6': expected all surface remainder fractions to be in range [0.0, 1.0], received " "'[1.0, 1.02]'.",
        ),
        (
            "test_7",
            ["mix_5"],
            [1999, 2000, 2001],
            [100],
            [15, 15],
            [10],
            [10],
            [0.0],
            [1.0],
            "'test_7':  Mismatch in length of parameters. Provided parameters are: "
            "years=[1999, 2000, 2001], days=[100, 100, 100], mix_names=['mix_5', 'mix_5', "
            "'mix_5'], nitrogen_masses=[15, 15], phosphorus_masses=[10, 10, 10], "
            "potassium_masses=[10, 10, 10], application_depths=[0.0, 0.0, 0.0], "
            "surface_remainder_fractions=[1.0, 1.0, 1.0]. Lengths are: {'years': 3, "
            "'days': 3, 'mix_names': 3, 'nitrogen_masses': 2, 'phosphorus_masses': 3, "
            "'potassium_masses': 3, 'application_depths': 3, "
            "'surface_remainder_fractions': 3}.",
        ),
    ],
)
def test_validate_fertilizer_parameters(
    name: str,
    mix_names: List[str],
    years: List[int],
    days: List[int],
    nitrogen: List[float],
    phosphorus: List[float],
    potassium: List[float],
    depths: List[float],
    fractions: List[float],
    expected_err_msg: str,
) -> None:
    """Tests that FertilizerSchedule raises proper errors when initialized with invalid input."""
    with pytest.raises(ValueError) as e:
        FertilizerSchedule(name, mix_names, years, days, nitrogen, phosphorus, potassium, depths, fractions, 1, 1)
    assert str(e.value) == expected_err_msg


@pytest.mark.parametrize(
    "mixes,years,days,nitrogen,phosphorus,potassium,depths,fractions,skip,repeat,expected",
    [
        (
            ["mix_1"],
            [1990, 1993],
            [100],
            [10.0],
            [10.0],
            [10.0],
            [30.0],
            [0.8],
            1,
            2,
            [
                FertilizerEvent("mix_1", 10.0, 10.0, 10.0, 30.0, 0.8, 1990, 100),
                FertilizerEvent("mix_1", 10.0, 10.0, 10.0, 30.0, 0.8, 1993, 100),
                FertilizerEvent("mix_1", 10.0, 10.0, 10.0, 30.0, 0.8, 1995, 100),
                FertilizerEvent("mix_1", 10.0, 10.0, 10.0, 30.0, 0.8, 1998, 100),
                FertilizerEvent("mix_1", 10.0, 10.0, 10.0, 30.0, 0.8, 2000, 100),
                FertilizerEvent("mix_1", 10.0, 10.0, 10.0, 30.0, 0.8, 2003, 100),
            ],
        ),
        (
            ["mix_1", "mix_2", "mix_1"],
            [1991, 1991, 1992],
            [150, 240, 90],
            [15.0, 8.0, 20.0],
            [10.0, 10.0, 10.0],
            [6.0, 6.0, 6.0],
            [0.0],
            [1.0],
            0,
            1,
            [
                FertilizerEvent("mix_1", 15.0, 10.0, 6.0, 0.0, 1.0, 1991, 150),
                FertilizerEvent("mix_2", 8.0, 10.0, 6.0, 0.0, 1.0, 1991, 240),
                FertilizerEvent("mix_1", 20.0, 10.0, 6.0, 0.0, 1.0, 1992, 90),
                FertilizerEvent("mix_1", 15.0, 10.0, 6.0, 0.0, 1.0, 1993, 150),
                FertilizerEvent("mix_2", 8.0, 10.0, 6.0, 0.0, 1.0, 1993, 240),
                FertilizerEvent("mix_1", 20.0, 10.0, 6.0, 0.0, 1.0, 1994, 90),
            ],
        ),
        (
            ["mix_3", "mix_4"],
            [1995, 1996],
            [100],
            [10.0, 20.0],
            [25.0, 10.0],
            [8.0, 8.0],
            [0.0],
            [1.0],
            0,
            2,
            [
                FertilizerEvent("mix_3", 10.0, 25.0, 8.0, 0.0, 1.0, 1995, 100),
                FertilizerEvent("mix_4", 20.0, 10.0, 8.0, 0.0, 1.0, 1996, 100),
                FertilizerEvent("mix_3", 10.0, 25.0, 8.0, 0.0, 1.0, 1997, 100),
                FertilizerEvent("mix_4", 20.0, 10.0, 8.0, 0.0, 1.0, 1998, 100),
                FertilizerEvent("mix_3", 10.0, 25.0, 8.0, 0.0, 1.0, 1999, 100),
                FertilizerEvent("mix_4", 20.0, 10.0, 8.0, 0.0, 1.0, 2000, 100),
            ],
        ),
        (
            ["mix_1", "mix_2", "mix_1"],
            [1991, 1991, 1992],
            [150, 240, 90],
            [15.0, 8.0, 20.0],
            [10.0, 10.0, 10.0],
            [5.0, 5.0, 5.0],
            None,
            None,
            0,
            1,
            [
                FertilizerEvent("mix_1", 15.0, 10.0, 5.0, 0.0, 1.0, 1991, 150),
                FertilizerEvent("mix_2", 8.0, 10.0, 5.0, 0.0, 1.0, 1991, 240),
                FertilizerEvent("mix_1", 20.0, 10.0, 5.0, 0.0, 1.0, 1992, 90),
                FertilizerEvent("mix_1", 15.0, 10.0, 5.0, 0.0, 1.0, 1993, 150),
                FertilizerEvent("mix_2", 8.0, 10.0, 5.0, 0.0, 1.0, 1993, 240),
                FertilizerEvent("mix_1", 20.0, 10.0, 5.0, 0.0, 1.0, 1994, 90),
            ],
        ),
    ],
)
def test_generate_fertilizer_events(
    mixes: List[str],
    years: List[int],
    days: List[int],
    nitrogen: List[float],
    phosphorus: List[float],
    potassium: List[float],
    depths: List[float],
    fractions: List[float],
    skip: int,
    repeat: int,
    expected: list[FertilizerEvent],
) -> None:
    """Tests that FertilizerEvents are properly generated by FertilizerSchedules."""
    fert_sched = FertilizerSchedule(
        "test",
        mixes,
        years,
        days,
        nitrogen,
        phosphorus,
        potassium,
        depths,
        fractions,
        skip,
        repeat,
    )
    actual = fert_sched.generate_fertilizer_events()
    assert actual == expected
