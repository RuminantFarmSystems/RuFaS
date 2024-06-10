import pytest
from typing import List, Any

from RUFAS.routines.field.manager.fertilizer_schedule import FertilizerSchedule
from RUFAS.routines.field.manager.events import FertilizerEvent
from RUFAS.output_manager import OutputManager

om = OutputManager()


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
            "'test_4': expected all phosphorus masses to be >= 0, received '[10, -15]'.",
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
            "'test_5': expected all application depths to be >= 0, received '[-30.0, 30.0]'.",
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
            "'test_7': expected equal numbers of fertilizer application parameters, received "
            "'[1999, 2000, 2001]' years, '[100, 100, 100]' days, '['mix_5', 'mix_5', 'mix_5']' "
            "mix names, '[15, 15]' nitrogen masses, '[10, 10, 10]' phosphorus masses, '[10, 10, 10]' potassium masses, "
            "'[0.0, 0.0, 0.0]' application depths, and '[1.0, 1.0, 1.0]' surface remainder "
            "fractions.",
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
    "values,expected",
    [
        ([1, 3, 4], True),
        ([0.0, 1.2, 3.8], True),
        ([], True),
        ([-0.1, 0.1], False),
        ([-2, -4], False),
    ],
)
def test_determine_if_all_non_negative_values(values: List[Any], expected: bool) -> None:
    """Tests that lists are correctly checked for negative values."""
    actual = FertilizerSchedule._determine_if_all_non_negative_values(values)
    assert actual == expected


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
                FertilizerEvent("mix_1", 1990, 100, 10.0, 10.0, 10.0, 30.0, 0.8),
                FertilizerEvent("mix_1", 1993, 100, 10.0, 10.0, 10.0, 30.0, 0.8),
                FertilizerEvent("mix_1", 1995, 100, 10.0, 10.0, 10.0, 30.0, 0.8),
                FertilizerEvent("mix_1", 1998, 100, 10.0, 10.0, 10.0, 30.0, 0.8),
                FertilizerEvent("mix_1", 2000, 100, 10.0, 10.0, 10.0, 30.0, 0.8),
                FertilizerEvent("mix_1", 2003, 100, 10.0, 10.0, 10.0, 30.0, 0.8),
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
                FertilizerEvent("mix_1", 1991, 150, 15.0, 10.0, 6.0, 0.0, 1.0),
                FertilizerEvent("mix_2", 1991, 240, 8.0, 10.0, 6.0, 0.0, 1.0),
                FertilizerEvent("mix_1", 1992, 90, 20.0, 10.0, 6.0, 0.0, 1.0),
                FertilizerEvent("mix_1", 1993, 150, 15.0, 10.0, 6.0, 0.0, 1.0),
                FertilizerEvent("mix_2", 1993, 240, 8.0, 10.0, 6.0, 0.0, 1.0),
                FertilizerEvent("mix_1", 1994, 90, 20.0, 10.0, 6.0, 0.0, 1.0),
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
                FertilizerEvent("mix_3", 1995, 100, 10.0, 25.0, 8.0,0.0, 1.0),
                FertilizerEvent("mix_4", 1996, 100, 20.0, 10.0, 8.0,0.0, 1.0),
                FertilizerEvent("mix_3", 1997, 100, 10.0, 25.0, 8.0,0.0, 1.0),
                FertilizerEvent("mix_4", 1998, 100, 20.0, 10.0, 8.0,0.0, 1.0),
                FertilizerEvent("mix_3", 1999, 100, 10.0, 25.0, 8.0,0.0, 1.0),
                FertilizerEvent("mix_4", 2000, 100, 20.0, 10.0, 8.0,0.0, 1.0),
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
                FertilizerEvent("mix_1", 1991, 150, 15.0, 10.0, 5.0, 0.0, 1.0),
                FertilizerEvent("mix_2", 1991, 240, 8.0, 10.0, 5.0, 0.0, 1.0),
                FertilizerEvent("mix_1", 1992, 90, 20.0, 10.0, 5.0, 0.0, 1.0),
                FertilizerEvent("mix_1", 1993, 150, 15.0, 10.0, 5.0, 0.0, 1.0),
                FertilizerEvent("mix_2", 1993, 240, 8.0, 10.0, 5.0, 0.0, 1.0),
                FertilizerEvent("mix_1", 1994, 90, 20.0, 10.0, 5.0, 0.0, 1.0),
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
    expected: str,
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
