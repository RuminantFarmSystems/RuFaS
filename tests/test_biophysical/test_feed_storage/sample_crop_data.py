from datetime import date
from typing import Any

harvest_storage_date = date(2025, 3, 7)

sample_crop_data: dict[str, Any] = {
    "harvest_time": harvest_storage_date,
    "storage_time": harvest_storage_date,
    "field_name": "field_1",
    "config_name": "alfalfa_data",
    "dry_matter_mass": 100.0,
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

sample_crop_data_no_mass: dict[str, Any] = {
    "harvest_time": harvest_storage_date,
    "storage_time": harvest_storage_date,
    "field_name": "field_1",
    "config_name": "test_data",
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
