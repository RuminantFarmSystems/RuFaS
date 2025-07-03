from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


def test_storage_cover() -> None:
    """Tests that StorageCover enum attributes have the correct value."""

    assert StorageCover.COVER.value == "cover"
    assert StorageCover.COVER_AND_FLARE.value == "cover_and_flare"
    assert StorageCover.CRUST.value == "crust"
    assert StorageCover.NO_COVER.value == "no_crust_or_cover"
