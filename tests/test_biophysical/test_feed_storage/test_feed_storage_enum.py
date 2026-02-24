from typing import Type
import pytest
from RUFAS.biophysical.feed_storage.baleage import Baleage
from RUFAS.biophysical.feed_storage.grain import Dry, HighMoisture
from RUFAS.biophysical.feed_storage.hay import Hay, ProtectedIndoors, ProtectedTarped, ProtectedWrapped, Unprotected
from RUFAS.biophysical.feed_storage.silage import Bag, Bunker, Pile
from RUFAS.biophysical.feed_storage.storage import Storage
from RUFAS.biophysical.feed_storage.feed_storage_enum import StorageType


@pytest.mark.parametrize("member", list(StorageType))
def test_get_storage_class_returns_enum_value(member: StorageType) -> None:
    """Each enum name maps to its underlying storage class."""
    cls = StorageType.get_storage_class(member.name)
    assert cls is member.value
    assert issubclass(cls, Storage)


@pytest.mark.parametrize(
    "input_str, expected_class",
    [
        ("Hay", Hay),
        ("ProtectedIndoors", ProtectedIndoors),
        ("ProtectedWrapped", ProtectedWrapped),
        ("Unprotected", Unprotected),
        ("ProtectedTarped", ProtectedTarped),
        ("Baleage", Baleage),
        ("Dry", Dry),
        ("HighMoisture", HighMoisture),
        ("Bunker", Bunker),
        ("Pile", Pile),
        ("Bag", Bag)
    ]
)
def test_get_storage_class_valid(input_str: str, expected_class: Type["Storage"]) -> None:
    assert StorageType.get_storage_class(input_str) is expected_class


@pytest.mark.parametrize("bad_name", ["Unknown", "pile", "BUNKER", "", "Hay "])
def test_get_storage_class_raises_for_unknown(bad_name: str) -> None:
    """Invalid or case-mismatched names raise ValueError."""
    with pytest.raises(ValueError) as exc:
        StorageType.get_storage_class(bad_name)
    assert f"Unknown storage type: {bad_name}." in str(exc.value)
