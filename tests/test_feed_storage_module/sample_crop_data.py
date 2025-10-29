from typing import Dict

from mock.mock import MagicMock

from RUFAS.rufas_time import RufasTime

mock_time = MagicMock(auto_spec=RufasTime)
mock_time.year = 1
mock_time.day = 1

sample_crop_data: Dict[str, float] = {
    "harvest_time": mock_time,
    "storage_time": mock_time,
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

sample_crop_data_no_mass: Dict[str, float] = {
    "harvest_time": mock_time,
    "storage_time": mock_time,
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
