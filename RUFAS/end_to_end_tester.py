from .time import Time
from .input_manager import InputManager
from .output_manager import OutputManager
from .weather import Weather
from .routines.feed_storage.feed_manager import FeedManager, StorageType
from .routines.feed_storage.baleage import Baleage
from .routines.feed_storage.enums import CropCategory, CropType
from .routines.feed_storage.grain import Dry, HighMoisture
from .routines.feed_storage.harvested_crop import HarvestedCrop
from .routines.feed_storage.hay import ProtectedIndoors, ProtectedWrapped, ProtectedTarped, Unprotected
from .routines.feed_storage.silage import Bag, Bunker, Pile
from .routines.feed_storage.storage import Storage
from .routines.field.crop.crop_data import DEFAULT_DRY_MATTER_DIGESTIBILITY


class EndToEndTester:
    """Executes an end-to-end test on RuFaS."""

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.time = Time()
        weather_data = self.im.get_data("weather")
        self.weather = Weather(weather_data, self.time)
        self.feed_manager = FeedManager()
        self._setup_feed_storage()

    def run_end_to_end_testing(self) -> None:
        """Runs a limited RuFaS simulation and compares the output to pre-computed outputs."""
        self.simulate()

        self.compare_results()

    def simulate(self) -> None:
        """Runs a limited RuFaS simulation."""
        while not self.time.current_date > self.time.end_date:
            self.feed_manager.process_degradations(self.weather, self.time)
            self.weather.record_weather(self.time)
            self.time.record_time()
            self.time.advance()

    def _setup_feed_storage(self) -> None:
        """Prepares the FeedManager to simulate stored feed degradations."""
        reusable_values = {
            "harvest_time": self.time,
            "storage_time": self.time,
            "fresh_mass": 1000.0,
            "dry_matter_digestibility": DEFAULT_DRY_MATTER_DIGESTIBILITY,
        }
        hay_values = {
            "category": CropCategory.ALFALFA,
            "type": CropType.ALFALFA,
            "dry_matter_percentage": 88.136,
            "lignin": 6.643,
            "crude_protein_percent": 20.745,
            "non_protein_nitrogen": 7.18,
            "starch": 1.513,
            "adf": 32.073,
            "ndf": 41.109,
            "sugar": 8.97,
            "ash": 10.762,
            **reusable_values,
        }
        baleage_values = {
            "category": CropCategory.SMALL_GRAIN,
            "type": CropType.RYE,
            "dry_matter_percentage": 34.881,
            "lignin": 4.932,
            "crude_protein_percent": 14.434,
            "non_protein_nitrogen": 8.904,
            "starch": 1.477,
            "adf": 38.282,
            "ndf": 58.026,
            "sugar": 8.761,
            "ash": 10.275,
            **reusable_values,
        }
        grain_values = {
            "category": CropCategory.SOY,
            "type": CropType.GRAIN,
            "dry_matter_percentage": 89.105,
            "lignin": 1.516,
            "crude_protein_percent": 39.98,
            "non_protein_nitrogen": 16.826,
            "starch": 4.17,
            "adf": 6.992,
            "ndf": 11.883,
            "sugar": 9.0,
            "ash": 5.31,
            **reusable_values,
        }
        silage_values = {
            "category": CropCategory.CORN,
            "type": CropType.SILAGE,
            "dry_matter_percentage": 35.361,
            "lignin": 3.054,
            "crude_protein_percent": 7.707,
            "non_protein_nitrogen": 3.996,
            "starch": 32.867,
            "adf": 24.332,
            "ndf": 40.931,
            "sugar": 2.971,
            "ash": 3.843,
            **reusable_values,
        }

        storages: dict[StorageType, Storage] = {
            StorageType.PROTECTED_INDOORS: ProtectedIndoors(),
            StorageType.PROTECTED_WRAPPED: ProtectedWrapped(),
            StorageType.PROTECTED_TARPED: ProtectedTarped(),
            StorageType.UNPROTECTED: Unprotected(),
            StorageType.BALEAGE: Baleage(),
            StorageType.DRY: Dry(),
            StorageType.HIGH_MOISTURE: HighMoisture(),
            StorageType.BUNKER: Bunker(),
            StorageType.PILE: Pile(),
            StorageType.BAG: Bag(),
        }
        storages[StorageType.PROTECTED_INDOORS].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.PROTECTED_WRAPPED].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.PROTECTED_TARPED].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.UNPROTECTED].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.BALEAGE].receive_crop(HarvestedCrop(**baleage_values))  # type: ignore[arg-type]
        storages[StorageType.DRY].receive_crop(HarvestedCrop(**grain_values))  # type: ignore[arg-type]
        storages[StorageType.HIGH_MOISTURE].receive_crop(HarvestedCrop(**grain_values))  # type: ignore[arg-type]
        storages[StorageType.BUNKER].receive_crop(HarvestedCrop(**silage_values))  # type: ignore[arg-type]
        storages[StorageType.PILE].receive_crop(HarvestedCrop(**silage_values))  # type: ignore[arg-type]
        storages[StorageType.BAG].receive_crop(HarvestedCrop(**silage_values))  # type: ignore[arg-type]

        self.feed_manager.active_storages = storages

    def compare_results(self) -> None:
        """Compares expected test results with actual results."""
        all_result_data = self.om.filter_variables_pool({"filters": [".*"]})
        actual_results = self.convert_data_to_expected_format(all_result_data)
        expected_results = self.im.get_data("end_to_end_testing_results")
        if expected_results is None:
            raise ValueError("Could not obtain expected end-to-end testing results.")
        assert actual_results == expected_results

    def convert_data_to_expected_format(self, data_to_convert) -> None:
        pass
