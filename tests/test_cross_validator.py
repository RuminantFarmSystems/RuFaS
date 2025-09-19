from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.cross_validator import CrossValidator


@pytest.mark.parametrize(
    "alias_name,value,expected_pool",
    [("test1", 16.4, {"test1": 16.4}), ("test2", 924.6, {"test1": 13, "test2": 924.6})],
)
def test_save_to_alias_pool(alias_name: str, value: Any, expected_pool: dict[str, Any]) -> None:
    validator = CrossValidator()
    validator._alias_pool = {"test1": 13}
    validator._save_to_alias_pool(alias_name, value)
    assert validator._alias_pool == expected_pool


@pytest.mark.parametrize(
    "pool,alias,expected",
    [
        ({"a": 1}, "a", 1),
        ({"x": "Y", "z": 3.14}, "x", "Y"),
    ],
)
def test_get_alias_value_returns(pool: dict[str, Any], alias: str, expected: Any) -> None:
    v = CrossValidator()
    v._alias_pool = dict(pool)
    assert v._get_alias_value(alias) == expected


def test_get_alias_value_raises_key_error_when_missing() -> None:
    v = CrossValidator()
    v._alias_pool = {"exists": 10}

    result = v._get_alias_value("missing")

    assert result is None
    assert len(v._event_logs) == 1


def test_target_and_save(mocker: MockerFixture) -> None:
    v = CrossValidator()
    mock_check = mocker.patch.object(v, "_check_target_and_save_block")
    mock_get_data = mocker.patch.object(v.im, "get_data", return_value=1)

    v._target_and_save({"variables": {"a": "test.address.1", "b": "test.address.2"}, "constants": {"c": "value"}})

    assert v._alias_pool == {"a": 1, "b": 1, "c": "value"}
    mock_check.assert_called_once()
    assert mock_get_data.call_count == 2


@pytest.mark.parametrize(
    "block",
    [
        ({"variables": {}, "constants": {}}),
        ({"variables": {"x": "A1"}, "constants": {}}),
        ({"variables": {}, "constants": {"k": "K1"}}),
        ({}),
    ],
)
def test_check_target_and_save_block_no_errors(block: dict[str, dict[str, Any]]) -> None:
    """Should not append errors when only allowed keys are present."""
    cv = CrossValidator()
    cv._check_target_and_save_block(block)
    assert len(cv._event_logs) == 0


@pytest.mark.parametrize(
    "block",
    [
        ({"variables": {}, "constants": {}}),
        ({"variables": {"x": "A1"}, "constants": {}}),
        ({"variables": {}, "constants": {"k": "K1"}}),
        ({}),
    ],
)
def test_check_target_and_save_block_no_errors(block: dict[str, dict[str, Any]]) -> None:
    """Should not append errors when only allowed keys are present."""
    cv = CrossValidator()
    cv._check_target_and_save_block(block)
    assert len(cv._event_logs) == 0


def test_check_target_and_save_block_message_contains_all_invalid_keys() -> None:
    """Sanity check: when multiple invalid keys exist, logs each (not a single aggregated one)."""
    cv = CrossValidator()
    block = {"variables": {}, "constants": {}, "a": {}, "b": {}, "c": {}}

    cv._check_target_and_save_block(block)

    assert len(cv._event_logs) == 3
    assert all(any(f"Unsupported keys {k} provided." in e["message"] for e in cv._event_logs) for k in ("a", "b", "c"))
