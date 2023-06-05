import pytest
from typing import List

from SC_redesign.Crop_and_Soil.manager.amendment_schedule import TillageSchedule
from SC_redesign.Crop_and_Soil.manager.events import TillageEvent


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
def test_init_tillage_schedule(depths: float | List[float], incorp_fracs: float | List[float],
                               mix_fracs: float | List[float], expected_depths: float | List[float],
                               expected_incorp: float | List[float], expected_mix: float | List[float]) -> None:
    """Tests that TillageSchedules are created correctly."""
    till_sched = TillageSchedule("test", [1990, 1991], [160, 160], depths, incorp_fracs, mix_fracs, 1, 1)
    assert till_sched.tillage_depths == expected_depths
    assert till_sched.incorporation_fractions == expected_incorp
    assert till_sched.mixing_fractions == expected_mix


@pytest.mark.parametrize("depths,incorp_fracs,mix_fracs,expected", [
    ([200, 200, 200], [0.5], [0.5], "Number of years, days, depths, incorporation and mixing fractions must be equal."),
    ([300, 300], [0.5, 0.8, 0.5], [0.4, 0.4], "Number of years, days, depths, incorporation and mixing fractions must "
                                              "be equal."),
    ([200], [0.3], [0.4, 0.5, 0.6], "Number of years, days, depths, incorporation and mixing fractions must be equal."),
    ([100, -50], [0.4], [0.5], "Expected all tillage depths to be > 0.0, received '[100, -50]'."),
    ([200], [1.1], [0.55], "Expected all incorporation fractions to be in range [0.0, 1.0], received '[1.1, 1.1]'."),
    ([400], [0.66], [0.5, -0.4], "Expected all mixing fractions to be in range [0.0, 1.0], received '[0.5, -0.4]'.")
])
def test_init_tillage_schedule_error(depths: float | List[float], incorp_fracs: float | List[float],
                                     mix_fracs: float | List[float], expected: str) -> None:
    """Tests that TillageSchedule throws the correct error when passed invalid parameters."""
    with pytest.raises(ValueError) as e:
        TillageSchedule("test", [1990, 1991], [160], depths, incorp_fracs, mix_fracs, 2, 2)
    assert str(e.value) == expected


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
