import pytest
from typing import List, Any

from SC_redesign.Crop_and_Soil.manager.fertilizer_schedule import FertilizerSchedule


@pytest.mark.parametrize("name,mix_names,years,days,nitrogen,phosphorus,depths,fractions,expected", [
    ("test_1", ["name_1", "name_2"], [1992, 1991], [100], [10], [10], [50.0], [0.4],
     "'test_1': expected all years to be > 0 and in non-descending order, received "
     "'[1992, 1991]'."),
    ("test_2", ["name_3"], [1996, 1997], [0, 366], [10], [10], [0.0], [1.0],
     "'test_2': expected all days to be in range [1, 366], received '[0, 366]'."),
    ("test_3", ["test_mix"], [1991, 1992], [100], [-15, 10], [10], [0.0], [1.0],
     "'test_3': expected all nitrogen masses to be in >= 0, received '[-15, 10]'."),
    ("test_4", ["mix_1", "mix_2"], [1993, 1994], [100], [10], [10, -15], [0.0], [1.0],
     "'test_4': expected all phosphorus masses to be >= 0, received '[10, -15]'."),
    ("test_5", ["chex_mix"], [1990, 1992], [100], [10], [10], [-30.0, 30.0], [0.8],
     "'test_5': expected all application depths to be >= 0, received '[-30.0, 30.0]'."),
    ("test_6", ["mix_4"], [1991, 1991], [100, 200], [10], [10], [0.0], [1.0, 1.02],
     "'test_6': expected all surface remainder fractions to be in range [0.0, 1.0], received '[1.0, 1.02]'."),
    ("test_7", ["mix_5"], [1999, 2000, 2001], [100], [15, 15], [10], [0.0], [1.0],
     "'test_7': expected equal numbers of fertilizer application parameters, received '[1999, 2000, 2001]' years, "
     "'[100, 100, 100]' days, '['mix_5', 'mix_5', 'mix_5']' mix names, '[15, 15]' nitrogen masses, '[10, 10, 10]' "
     "phosphorus masses, '[0.0, 0.0, 0.0]' application depths, and '[1.0, 1.0, 1.0]' surface remainder fractions.")
])
def test_validate_fertilizer_parameters(name: str, mix_names: List[str], years: List[int], days: List[int],
                                        nitrogen: List[float], phosphorus: List[float], depths: List[float],
                                        fractions: List[float], expected: str) -> None:
    """Tests that FertilizerSchedule raises proper errors when initialized with invalid input."""
    with pytest.raises(ValueError) as e:
        FertilizerSchedule(name, mix_names, years, days, nitrogen, phosphorus, depths, fractions, 1, 1)
    assert str(e.value) == expected


@pytest.mark.parametrize("values,expected", [
    ([1, 3, 4], True),
    ([0.0, 1.2, 3.8], True),
    ([], True),
    ([-0.1, 0.1], False),
    ([-2, -4], False)
])
def test_determine_if_all_non_negative_values(values: List[Any], expected: bool) -> None:
    """Tests that lists are correctly checked for negative values."""
    actual = FertilizerSchedule._determine_if_all_non_negative_values(values)
    assert actual == expected
#
# @pytest.mark.parametrize("name,years,days,nitrogen,phosphorus,depths,fractions,expected", [
#     ("mix_1", [1990, 1993], [100], [10.0], [10.0], [30.0], [0.8], )
# ])
