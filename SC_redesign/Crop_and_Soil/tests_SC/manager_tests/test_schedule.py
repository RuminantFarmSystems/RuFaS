import pytest

from SC_redesign.Crop_and_Soil.manager.schedule import Schedule


def test_repeat_pattern() -> None:
    """Tests that repeat_pattern correctly repeats patterns."""
    assert Schedule.repeat_pattern([1, 3, 5], 1, 3) == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
    assert Schedule.repeat_pattern([1, 3, 5], 0, 1) == [1, 3, 5, 6, 8, 10]
    assert Schedule.repeat_pattern([2, 3, 7], 3, 2) == [2, 3, 7, 11, 12, 16, 20, 21, 25]
    assert Schedule.repeat_pattern([2, 3, 7], 0, 0) == [2, 3, 7]

    assert Schedule.repeat_pattern([2], 0, 0) == [2]
    assert Schedule.repeat_pattern([2], 3, 1) == [2, 6]
    assert Schedule.repeat_pattern([2], 0, 5) == [2, 3, 4, 5, 6, 7]

    assert Schedule.repeat_pattern([2, 3, 3], 2, 3) == [2, 3, 3, 6, 7, 7, 10, 11, 11, 14, 15, 15]
    assert Schedule.repeat_pattern([1, 1], 0, 4) == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert Schedule.repeat_pattern([1, 1, 3], 3, 1) == [1, 1, 3, 7, 7, 9]

    assert Schedule.repeat_pattern([], 0, 0) == []
    assert Schedule.repeat_pattern([], 3, 7) == []