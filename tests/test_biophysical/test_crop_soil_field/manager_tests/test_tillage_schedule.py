from typing import List

import pytest

from RUFAS.data_structures.tillage_implements import TillageImplement
from RUFAS.data_structures.events import TillageEvent
from RUFAS.biophysical.field.manager.tillage_schedule import TillageSchedule


@pytest.mark.parametrize(
    "name,years,days,depths,incorp_fracs,mix_fracs,implements,expected",
    [
        (
            "test_1",
            [1990, 1989, 1991],
            [100],
            [100],
            [0.5],
            [0.5],
            ["subsoiler"],
            "'test_1': expected all years to be > 0 and in non-descending order, received '[1990, 1989, 1991]'.",
        ),
        (
            "test_2",
            [1990, 1991],
            [200, 0],
            [100],
            [0.5],
            [0.5],
            ["coulter-chisel-plow"],
            "'test_2': expected all days to be in range [1, 366], received '[200, 0]'.",
        ),
        (
            "test_3",
            [1990],
            [150],
            [150, 0, 150],
            [0.5],
            [0.5],
            ["disk-harrow"],
            "'test_3': expected all tillage depths to be > 0.0, received '[150, 0, 150]'.",
        ),
        (
            "test_4",
            [1990],
            [150],
            [100],
            [1.1, 0.9],
            [0.5],
            ["disk-harrow"],
            "'test_4': expected all incorporation fractions to be in range [0.0, 1.0], received '[1.1, 0.9]'.",
        ),
        (
            "test_5",
            [1990],
            [150],
            [100],
            [0.5],
            [-0.2, 0.3],
            ["disk-harrow"],
            "'test_5': expected all mixing fractions to be in range [0.0, 1.0], received '[-0.2, 0.3]'.",
        ),
        (
            "test_6",
            [1990],
            [150, 200],
            [100],
            [0.5],
            [0.5],
            ["disk-harrow"],
            "'test_6':  Mismatch in length of parameters. Provided parameters are: "
            "years=[1990], days=[150, 200], tillage_depths=[100], "
            "incorporation_fractions=[0.5], mixing_fractions=[0.5], "
            "implements=[<TillageImplement.DISK_HARROW: 'disk-harrow'>]. Lengths are: "
            "{'years': 1, 'days': 2, 'tillage_depths': 1, 'incorporation_fractions': 1, "
            "'mixing_fractions': 1, 'implements': 1}.",
        ),
    ],
)
def test_validate_tillage_parameters(
    name: str,
    years: List[int],
    days: List[int],
    depths: List[float],
    incorp_fracs: List[float],
    mix_fracs: List[float],
    implements: List[str],
    expected: str,
) -> None:
    """Tests that errors are raised correctly when invalid input is passed."""
    with pytest.raises(ValueError) as e:
        TillageSchedule(name, years, days, depths, incorp_fracs, mix_fracs, implements, 1, 1)
    assert str(e.value) == expected


@pytest.mark.parametrize(
    "depths,expected",
    [
        ([13, 22, 300], True),
        ([200, -200, 200], False),
        ([0], False),
        ([0.5, 50], True),
        ([], True),
    ],
)
def test_validate_depths(depths: List[float], expected: bool) -> None:
    """Tests that tillage depths are validated correctly."""
    actual = TillageSchedule.validate_positive_values(depths)
    assert actual == expected


@pytest.mark.parametrize(
    "depths,incorp_fracs,mix_fracs,implements,expected_depths,expected_incorp,expected_mix,expected_implements",
    [
        (
            [30, 30],
            [0.5, 0.5],
            [0.4, 0.4],
            ["disk-harrow", "coulter-chisel-plow"],
            [30, 30],
            [0.5, 0.5],
            [0.4, 0.4],
            [TillageImplement.DISK_HARROW, TillageImplement.COULTER_CHISEL_PLOW],
        ),
        (
            [20],
            [0.4],
            [0.3],
            ["subsoiler"],
            [20, 20],
            [0.4, 0.4],
            [0.3, 0.3],
            [TillageImplement.SUBSOILER, TillageImplement.SUBSOILER],
        ),
    ],
)
def test_init_tillage_schedule(
    depths: List[float],
    incorp_fracs: List[float],
    mix_fracs: List[float],
    implements: List[str],
    expected_depths: List[float],
    expected_incorp: List[float],
    expected_mix: List[float],
    expected_implements: List[TillageImplement],
) -> None:
    """Tests that TillageSchedules are created correctly."""
    till_sched = TillageSchedule("test", [1990, 1991], [160, 160], depths, incorp_fracs, mix_fracs, implements, 1, 1)
    assert till_sched.tillage_depths == expected_depths
    assert till_sched.incorporation_fractions == expected_incorp
    assert till_sched.mixing_fractions == expected_mix
    assert till_sched.implements == expected_implements


@pytest.mark.parametrize(
    "depths,incorp_fracs,mix_fracs,implements,years,days,skip,repeat,expected",
    [
        (
            [200, 200, 300],
            [0.5],
            [0.45, 0.45, 0.47],
            ["subsoiler", "subsoiler", "disk-harrow"],
            [1990, 1990, 1990],
            [90, 120, 200],
            0,
            1,
            [
                TillageEvent(200, 0.5, 0.45, TillageImplement.SUBSOILER, 1990, 90),
                TillageEvent(200, 0.5, 0.45, TillageImplement.SUBSOILER, 1990, 120),
                TillageEvent(300, 0.5, 0.47, TillageImplement.DISK_HARROW, 1990, 200),
                TillageEvent(200, 0.5, 0.45, TillageImplement.SUBSOILER, 1991, 90),
                TillageEvent(200, 0.5, 0.45, TillageImplement.SUBSOILER, 1991, 120),
                TillageEvent(300, 0.5, 0.47, TillageImplement.DISK_HARROW, 1991, 200),
            ],
        ),
        (
            [150],
            [0.3],
            [0.6],
            ["coulter-chisel-plow"],
            [1993, 1996],
            [100],
            2,
            2,
            [
                TillageEvent(150, 0.3, 0.6, TillageImplement.COULTER_CHISEL_PLOW, 1993, 100),
                TillageEvent(150, 0.3, 0.6, TillageImplement.COULTER_CHISEL_PLOW, 1996, 100),
                TillageEvent(150, 0.3, 0.6, TillageImplement.COULTER_CHISEL_PLOW, 1999, 100),
                TillageEvent(150, 0.3, 0.6, TillageImplement.COULTER_CHISEL_PLOW, 2002, 100),
                TillageEvent(150, 0.3, 0.6, TillageImplement.COULTER_CHISEL_PLOW, 2005, 100),
                TillageEvent(150, 0.3, 0.6, TillageImplement.COULTER_CHISEL_PLOW, 2008, 100),
            ],
        ),
        (
            [150, 45],
            [0.4],
            [0.2],
            ["seedbed-conditioner", "cultivator"],
            [1991, 1992],
            [120, 135],
            3,
            2,
            [
                TillageEvent(150, 0.4, 0.2, TillageImplement.SEEDBED_CONDITIONER, 1991, 120),
                TillageEvent(45, 0.4, 0.2, TillageImplement.CULTIVATOR, 1992, 135),
                TillageEvent(150, 0.4, 0.2, TillageImplement.SEEDBED_CONDITIONER, 1996, 120),
                TillageEvent(45, 0.4, 0.2, TillageImplement.CULTIVATOR, 1997, 135),
                TillageEvent(150, 0.4, 0.2, TillageImplement.SEEDBED_CONDITIONER, 2001, 120),
                TillageEvent(45, 0.4, 0.2, TillageImplement.CULTIVATOR, 2002, 135),
            ],
        ),
    ],
)
def test_generate_tillage_events(
    depths: List[float],
    incorp_fracs: List[float],
    mix_fracs: List[float],
    implements: List[str],
    years: List[int],
    days: List[int],
    skip: int,
    repeat: int,
    expected: List[TillageEvent],
) -> None:
    """Tests that correct list of TillageEvents are created by TillageSchedule."""
    till_sched = TillageSchedule("test", years, days, depths, incorp_fracs, mix_fracs, implements, skip, repeat)
    actual = till_sched.generate_tillage_events()
    assert actual == expected
