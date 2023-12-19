from RUFAS.routines.feed_storage.grain import Grain
from RUFAS.routines.feed_storage.enums import CropCategory


def test_acceptable_crops():
    grain = Grain()
    assert grain.acceptable_crops == [
        CropCategory.CORN,
        CropCategory.SMALL_GRAIN,
        CropCategory.SOY,
    ]
