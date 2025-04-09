import pytest
from RUFAS.biophysical.manure.storage.composting_type import CompostingType


def test_enum_members_exist() -> None:
    assert CompostingType.INTENSIVE_WINDROW.name == "INTENSIVE_WINDROW"
    assert CompostingType.PASSIVE_WINDROW.name == "PASSIVE_WINDROW"
    assert CompostingType.STATIC_PILE.name == "STATIC_PILE"


def test_enum_values() -> None:
    assert CompostingType.INTENSIVE_WINDROW.value == "intensive windrow"
    assert CompostingType.PASSIVE_WINDROW.value == "passive windrow"
    assert CompostingType.STATIC_PILE.value == "static pile"


def test_enum_reverse_lookup() -> None:
    assert CompostingType("intensive windrow") == CompostingType.INTENSIVE_WINDROW
    assert CompostingType("passive windrow") == CompostingType.PASSIVE_WINDROW
    assert CompostingType("static pile") == CompostingType.STATIC_PILE


def test_invalid_enum_raises_value_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        CompostingType("deep pit composting")
    assert "deep pit composting" in str(exc_info.value)
