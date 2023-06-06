import pytest
from typing import List, Any

from SC_redesign.Crop_and_Soil.manager.amendment_schedule import TillageSchedule, ManureSchedule
from SC_redesign.Crop_and_Soil.manager.events import TillageEvent


@pytest.mark.parametrize("name,years,days,depths,incorp_fracs,mix_fracs,expected", [
    ("test_1", [1990, 1989, 1991], [100], [100], [0.5], [0.5],
     "'test_1': expected all years to be > 0 and in non-descending order, received '[1990, 1989, 1991]'."),
    ("test_2", [1990, 1991], [200, 0], [100], [0.5], [0.5],
     "'test_2': expected all planting days to be in range [1, 366], received '[200, 0]'."),
    ("test_3", [1990], [150], [150, 0, 150], [0.5], [0.5],
     "'test_3': expected all tillage depths to be > 0.0, received '[150, 0, 150]'."),
    ("test_4", [1990], [150], [100], [1.1, 0.9], [0.5],
     "'test_4': expected all incorporation fractions to be in range [0.0, 1.0], received '[1.1, 0.9]'."),
    ("test_5", [1990], [150], [100], [0.5], [-0.2, 0.3],
     "'test_5': expected all mixing fractions to be in range [0.0, 1.0], received '[-0.2, 0.3]'."),
    ("test_6", [1990], [150, 200], [100], [0.5], [0.5],
     "'test_6': expected number of years, days, depths, incorporation and mixing fractions to be equal, received "
     "'[1990]' years, '[150, 200]' days, '[100]' tillage depths, '[0.5]' incorporation fractions, and '[0.5]' mixing "
     "fractions.")
])
def test_validate_tillage_parameters(name: str, years: List[int], days: List[int], depths: List[float],
                                     incorp_fracs: List[float], mix_fracs: List[float], expected: str) -> None:
    """Tests that errors are raised correctly when invalid input is passed."""
    with pytest.raises(ValueError) as e:
        TillageSchedule(name, years, days, depths, incorp_fracs, mix_fracs, 1, 1)
    assert str(e.value) == expected


@pytest.mark.parametrize("depths,expected", [
    ([13, 22, 300], True),
    ([200, -200, 200], False),
    ([0], False),
    ([0.5, 50], True),
    ([], True)
])
def test_validate_depths(depths: List[float], expected: bool) -> None:
    """Tests that tillage depths are validated correctly."""
    actual = TillageSchedule._validate_depths(depths)
    assert actual == expected


@pytest.mark.parametrize("fracs,expected", [
    ([0.0, 0.3, 0.99], True),
    ([0.5, 1.0], True),
    ([], True),
    ([-0.01, 0.03], False),
    ([0.4, 1.1], False)
])
def test_validate_fractions(fracs: List[float], expected) -> None:
    """Tests that all fractions passed are valid."""
    actual = TillageSchedule._validate_fractions(fracs)
    assert actual == expected


@pytest.mark.parametrize("depths,incorp_fracs,mix_fracs,expected_depths,expected_incorp,expected_mix", [
    ([30, 30], [0.5, 0.5], [0.4, 0.4], [30, 30], [0.5, 0.5], [0.4, 0.4]),
    ([20], [0.4], [0.3], [20, 20], [0.4, 0.4], [0.3, 0.3])
])
def test_init_tillage_schedule(depths: List[float], incorp_fracs: List[float], mix_fracs: List[float],
                               expected_depths: List[float], expected_incorp: List[float],
                               expected_mix: List[float]) -> None:
    """Tests that TillageSchedules are created correctly."""
    till_sched = TillageSchedule("test", [1990, 1991], [160, 160], depths, incorp_fracs, mix_fracs, 1, 1)
    assert till_sched.tillage_depths == expected_depths
    assert till_sched.incorporation_fractions == expected_incorp
    assert till_sched.mixing_fractions == expected_mix


@pytest.mark.parametrize("depths,incorp_fracs,mix_fracs,years,days,skip,repeat,expected", [
    ([200, 200, 300], [0.5], [0.45, 0.45, 0.47], [1990, 1990, 1990], [90, 120, 200], 0, 1, [
        TillageEvent(200, 0.5, 0.45, 1990, 90), TillageEvent(200, 0.5, 0.45, 1990, 120),
        TillageEvent(200, 0.5, 0.47, 1990, 200), TillageEvent(200, 0.5, 0.45, 1991, 90),
        TillageEvent(200, 0.5, 0.45, 1991, 120), TillageEvent(200, 0.5, 0.47, 1991, 200)]),
    ([150], [0.3], [0.6], [1993, 1996], [100], 2, 2, [TillageEvent(150, 0.3, 0.6, 1993, 100),
                                                      TillageEvent(150, 0.3, 0.6, 1996, 100),
                                                      TillageEvent(150, 0.3, 0.6, 1999, 100),
                                                      TillageEvent(150, 0.3, 0.6, 2002, 100),
                                                      TillageEvent(150, 0.3, 0.6, 2005, 100),
                                                      TillageEvent(150, 0.3, 0.6, 2008, 100)]),
    ([150, 45], [0.4], [0.2], [1991, 1992], [120, 135], 3, 2, [TillageEvent(150, 0.4, 0.2, 1991, 120),
                                                               TillageEvent(45, 0.4, 0.2, 1992, 135),
                                                               TillageEvent(150, 0.4, 0.2, 1996, 120),
                                                               TillageEvent(45, 0.4, 0.2, 1997, 135),
                                                               TillageEvent(150, 0.4, 0.2, 2001, 120),
                                                               TillageEvent(45, 0.4, 0.2, 2002, 135)])
])
def test_generate_tillage_events(depths: List[float], incorp_fracs: List[float], mix_fracs: List[float],
                                 years: List[int], days: List[int], skip: int, repeat: int,
                                 expected: List[TillageEvent]) -> None:
    """Tests that correct list of TillageEvents are created by TillageSchedule."""
    till_sched = TillageSchedule("test", years, days, depths, incorp_fracs, mix_fracs, skip, repeat)
    actual = till_sched.generate_tillage_events()
    assert actual == expected


@pytest.mark.parametrize("values,expected", [
    ([1, 3, 4], True),
    ([0.0, 1.2, 3.8], True),
    ([], True),
    ([-0.1, 0.1], False),
    ([-2, -4], False)
])
def test_determine_if_all_non_negative_values(values: List[Any], expected: bool) -> None:
    """Tests that lists are correctly checked for negative values."""
    actual = ManureSchedule._determine_if_all_non_negative_values(values)
    assert actual == expected


@pytest.mark.parametrize("name,years,days,nitrogen,phosphorus,field_coverage,depths,remainder_fracs,expected", [
    ("test_1", [1990, 1989], [100], [15], [15], [0.75], [0.0], [1.0],
     "'test_1': expected all years to be > 0 and in non-descending order, received '[1990, 1989]'."),
    ("test_2", [1990], [0], [15], [15], [0.75], [0.0], [1.0],
     "'test_2': expected all days to be in range [1, 366], received '[0]'."),
    ("test_3", [1990], [100], [-15.0], [15], [0.75], [0.0], [1.0],
     "'test_3': expected all nitrogen masses to be >= 0, received '[-15.0]'."),
    ("test_4", [1990, 1993], [110], [15], [-10], [0.75], [0.0], [1.0],
     "'test_4': expected all phosphorus masses to be >= 0, received '[-10, -10]'."),
    ("test_5", [1991], [100], [15], [15], [1.05], [0.0], [1.0],
     "'test_5': expected all field coverage fractions to be in the range [0.0, 1.0], received '[1.05]'."),
    ("test_6", [1994], [200], [15], [15], [0.75], [-15.0], [0.85],
     "'test_6': expected all manure application depths to be >= 0, received '[-15.0]'."),
    ("test_7", [1990, 1994], [120], [15], [20], [0.8], [20], [-0.15],
     "'test_7': expected all surface remainder fractions to be in the range [0.0, 1.0], received '[-0.15, -0.15]'."),
    ("test_8", [1990, 1990, 1993], [120, 140], [20], [15, 10, 20], [0.8, 0.9], [0.0], [1.0],
     "'test_8': expected equal number of manure application parameters, received '[1990, 1990, 1993]' years, "
     "'[120, 140]' days, '[20, 20, 20]' nitrogen masses, '[15, 10, 20]' phosphorus masses, '[0.8, 0.9]' field coverage "
     "fractions, '[0.0, 0.0, 0.0]' application depths, and '[1.0, 1.0, 1.0]' surface remainder fractions.")
])
def test_validate_manure_parameters(name: str, years: List[int], days: List[int], nitrogen: List[float],
                                    phosphorus: List[float], field_coverage: List[float], depths: List[float],
                                    remainder_fracs: List[float], expected: str) -> None:
    """Tests that invalid input is caught and raised with the correct error message in the init function."""
    with pytest.raises(ValueError) as e:
        ManureSchedule(name, years, days, nitrogen, phosphorus, field_coverage, depths, remainder_fracs, 1, 1)
    assert str(e.value) == expected
