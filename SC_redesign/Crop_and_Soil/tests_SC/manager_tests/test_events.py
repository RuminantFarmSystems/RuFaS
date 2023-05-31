from SC_redesign.Crop_and_Soil.manager.events import Event


def test_project_sequence():
    """ensure that all examples are tested for project_sequence"""
    assert Event.project_sequence(start=0, repeat=1, skip=1, cycles=3) == [0, 1, 3, 4, 6, 7]
    assert Event.project_sequence(start=[1, 2, 4], skip=1, cycles=3) == [1, 2, 4, 6, 7, 9, 11, 12, 14]
    assert Event.project_sequence(start=[1, 2, 4], repeat=1, skip=2, cycles=3) == [1, 2, 4, 5, 6, 8,
                                                                                   11, 12, 14, 15, 16, 18,
                                                                                   21, 22, 24, 25, 26, 28]
    assert Event.project_sequence(start=1, cycles=10) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert Event.project_sequence(start=[1, 2, 3, 4, 5], repeat=1) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert Event.project_sequence(start=[1, 2, 3, 4, 5], cycles=2) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert Event.project_sequence(start=1, repeat=3, skip=3, cycles=4) == [1, 2, 3, 4,
                                                                           8, 9, 10, 11,
                                                                           15, 16, 17, 18,
                                                                           22, 23, 24, 25]
    assert Event.project_sequence(start=[1, 2, 3, 4], skip=3, cycles=4) == [1, 2, 3, 4,
                                                                            8, 9, 10, 11,
                                                                            15, 16, 17, 18,
                                                                            22, 23, 24, 25]
    assert Event.project_sequence([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert Event.project_sequence(0) == [0]
    assert Event.project_sequence(1, repeat=4) == [1, 2, 3, 4, 5]

    # Old tests (for "repeat_pattern" - replaced by project sequence)
    assert Event.project_sequence([1, 2, 3], skip=0, cycles=3) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert Event.project_sequence([1, 2, 3], skip=1, cycles=2) == [1, 2, 3, 5, 6, 7]
    assert Event.project_sequence([1, 2, 4], skip=2, cycles=3) == [1, 2, 4, 7, 8, 10, 13, 14, 16]
    assert Event.project_sequence([1], skip=0, cycles=5) == [1, 2, 3, 4, 5]
    assert Event.project_sequence([1], skip=-1, cycles=5) == [1, 1, 1, 1, 1]
    assert Event.project_sequence([2, 4], skip=1, cycles=3) == [2, 4, 6, 8, 10, 12]
    assert Event.project_sequence([2, 4], skip=2, cycles=3) == [2, 4, 7, 9, 12, 14]
    assert Event.project_sequence([1], skip=2, cycles=4) == [1, 4, 7, 10]
    assert Event.project_sequence([3, 4, 6], skip=0, cycles=3) == [3, 4, 6, 7, 8, 10, 11, 12, 14]
