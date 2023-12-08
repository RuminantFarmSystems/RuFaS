import pytest

from RUFAS.schema_manager import SchemaManager

@pytest.mark.parametrize("pattern,expected", [
    ("^(kg)$", ["kg"]),
    ("^(default|no_kill)$", ["default", "no_kill"]),
    ("^(TAI|ED|Synch-ED)$", ["TAI", "ED", "Synch-ED"])
])
def test_get_list_of_options(pattern: str, expected: list[str]) -> None:
    """Tests that list of options are produced correctly from a Regex filter."""
    actual = SchemaManager._get_list_of_options(pattern)
    assert actual == expected


@pytest.mark.parametrize("pattern", [
    "(kg)$",
    "(kg)",
    "$(kg)^",
    "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$"
])
def test_get_list_of_options_error(pattern: str) -> None:
    """Tests that an incorrectly structured Regex pattern produces an error."""
    with pytest.raises(ValueError):
        SchemaManager._get_list_of_options(pattern)
