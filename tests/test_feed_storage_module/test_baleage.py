from RUFAS.routines.feed_storage.baleage import Baleage
from RUFAS.routines.feed_storage.enums import CropCategory


def test_acceptable_crops():
    baleage = Baleage()
    assert baleage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]
