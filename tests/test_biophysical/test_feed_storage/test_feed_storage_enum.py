import pytest
from RUFAS.biophysical.feed_storage.storage import Storage
from RUFAS.biophysical.feed_storage.feed_storage_enum import StorageType


@pytest.mark.parametrize("member", list(StorageType))
def test_get_storage_class_returns_enum_value(member) -> None:
    """Each enum name maps to its underlying storage class."""
    cls = StorageType.get_storage_class(member.name)
    assert cls is member.value
    assert issubclass(cls, Storage)


@pytest.mark.parametrize("bad_name", ["Unknown", "pile", "BUNKER", "", "Hay "])
def test_get_storage_class_raises_for_unknown(bad_name: str) -> None:
    """Invalid or case-mismatched names raise ValueError."""
    with pytest.raises(ValueError) as exc:
        StorageType.get_storage_class(bad_name)
    assert f"Unknown storage type: {bad_name}." in str(exc.value)
