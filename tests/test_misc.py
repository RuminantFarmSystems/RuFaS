import pytest
from pytest import approx
from pytest_mock.plugin import MockerFixture

from RUFAS.config import Config
from RUFAS.general_constants import GeneralConstants
from RUFAS.util import Utility


def test_annual_reset():
    """Unit test for function annual_reset in classes"""
    pass


def test_annual_mass_balance():
    """Unit test for function annual_mass_balance in classes"""
    pass


def test_calc_sim_length():
    """Unit test for function calc_sim_length in classes"""
    pass


def test_to_str():
    """Unit test for function to_str in classes"""
    pass


def test_advance():
    """Unit test for function advance in classes"""
    pass


def test_end_year():
    """Unit test for function end_year in classes"""
    pass


def test_end_simulation():
    """Unit test for function end_simulation in classes"""
    pass


def test_general_constants() -> None:
    """Tests the general constants in file general_constants.py."""
    constants = GeneralConstants
    assert constants.GRAMS_TO_KG == approx(0.001)
    assert constants.LITERS_TO_CUBIC_METERS == approx(0.001)
    assert constants.KG_TO_CUBIC_METERS == approx(0.001)
    assert constants.DAYS_PER_YEAR == 365
    assert constants.SECONDS_PER_DAY == 86400
    assert constants.WATER_DENSITY_KG_PER_LITER == approx(0.997)
    assert constants.WATER_DENSITY_KG_PER_M3 == approx(0.997 * 0.001)


def test_is_leap_year():
    """Unit test for function is_leap_year in classes"""
    pass


def test_input_prompt():
    """Unit test for function input_prompt in file user_prompt.py"""
    pass


class DummyClass:
    def __init__(self, value: int) -> None:
        self.value = value


class DummyNestedClass:
    def __init__(self, value: int) -> None:
        self.value = DummyClass(value)


@pytest.mark.parametrize(
    "input_obj, depth, max_depth, expected_output",
    [
        (42, 0, 1, 42),
        (3.14, 0, 1, 3.14),
        ("test", 0, 1, "test"),
        (True, 0, 1, True),
        (False, 0, 1, False),
        (None, 0, 1, None),
        ([], 0, 1, []),
        ((), 0, 1, ()),
        ({}, 0, 1, {}),
        (set(), 0, 1, []),
        ([1, "test", True], 0, 1, [1, "test", True]),
        ((1, "test", True), 0, 1, (1, "test", True)),
        ({1, 2, 3}, 0, 1, [1, 2, 3]),
        ({"a": 1, "b": 2}, 0, 1, {"a": 1, "b": 2}),
        ({"a": [1, 2, 3], "b": {"c": 4}}, 0, 3, {"a": [1, 2, 3], "b": {"c": 4}}),
        (["a", (1, 2), {"b": 3}], 0, 2, ["a", (1, 2), {"b": 3}]),
        ([1, [2, [3, 4], 5], 6], 0, 2, [1, [2, "[3, 4]", 5], 6]),
        ({"a": {"b": {"c": 42}}}, 0, 2, {"a": {"b": {"c": 42}}}),
        (DummyClass(42), 0, 1, {"value": 42}),
        (DummyNestedClass(42), 0, 2, {"value": {"value": 42}}),
        ({"a": {"b": DummyClass(42)}}, 0, 3, {"a": {"b": {"value": 42}}}),
        (
                [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
                0,
                2,
                [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
        ),
    ],
)
def test_make_serializable_recursive(
        input_obj: object,
        depth: int,
        max_depth: int,
        expected_output: object,
        mocker: MockerFixture,
) -> None:
    """Unit test for function _make_serializable() in file util.py"""
    # Arrange
    _ = mocker.patch.object(Utility, "_get_str", side_effect=lambda x: str(x))

    # Act
    result = Utility._make_serializable(input_obj, depth, max_depth)

    # Assert
    assert result == expected_output
