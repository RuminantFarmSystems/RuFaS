from typing import Dict
from RUFAS.time import Time
from RUFAS.config import Config


sample_crop_data: Dict[str, float] = {
    "harvest_time": Time(
        Config(
            {
                "start_date": "1:1",
                "end_date": "1:10",
                "set_seed": False,
                "random_seed": 42,
            }
        )
    ),
    "storage_time": Time(
        Config(
            {
                "start_date": "1:1",
                "end_date": "1:10",
                "set_seed": False,
                "random_seed": 42,
            }
        )
    ),
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
