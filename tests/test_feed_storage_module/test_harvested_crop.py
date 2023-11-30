from typing import Dict
import pytest
from RUFAS.routines.feed_storage.harvested_crop import (
    HarvestedCrop,
    CropCategory,
    CropType,
)


@pytest.fixture
def sample_crop_data() -> Dict[str, float]:
    return {
        "fresh_mass": 100.0,
        "dry_matter_percentage": 50.0,
        "dry_matter_digestibility": 70.0,
        "crude_protein_percent": 10.0,
        "non_protein_nitrogen": 5.0,
        "starch": 30.0,
        "adf": 7.0,
        "ndf": 15.0,
        "lignin": 3.0,
        "sugar": 20.0,
        "ash": 6.0,
    }
