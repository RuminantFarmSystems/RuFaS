from copy import copy

from math import inf

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants


class SlurryStorageOutdoor(Storage):
    """Representation of slurry storage outdoor and its associated processes."""

    def __init__(
        self,
        name: str,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        capacity: float = inf,
    ):
        """Initializes a new instance of the SlurryStorageOutdoor class."""
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=StorageCover(cover),
            storage_time_period=storage_time_period,
            surface_area=surface_area,
            capacity=capacity,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Calculates the methane, ammonia, and nitrous oxide emissions from stored manure,
        and updates relevant storage properties.

        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The weather conditions of the current day, including precipitation and mean
            air temperature.
        time : RufasTime
            The current time.

        Returns
        -------
        dict[str, ManureStream]
            A dictionary containing manure to be passed onto the next processor
            if it is the scheduled emptying day; otherwise an empty dictionary.

        """
        if self._cover in [StorageCover.NO_COVER, StorageCover.CRUST]:
            precipitation_volume = current_day_conditions.precipitation * GeneralConstants.MM_TO_M * self._surface_area
            self._received_manure.volume += precipitation_volume
            self._received_manure.water += precipitation_volume * UserConstants.WATER_DENSITY_KG_PER_M3
        received_manure = copy(self._received_manure)
        manure_to_return = super().process_manure(current_day_conditions, time)
        self._manure_to_process = manure_to_return["manure"] if manure_to_return else copy(self.stored_manure)

        manure_temperature = self._determine_outdoor_storage_temperature(
            time.current_julian_day, ManureConstants.SLURRY_OUTDOOR_MINIMUM_TEMPERATURE
        )

        storage_methane_burned, total_storage_methane = self._apply_methane_emissions(manure_temperature)
        storage_ammonia_nitrogen = self._apply_ammonia_emissions(manure_temperature)
        storage_nitrous_oxide_nitrogen = self._apply_nitrous_oxide_emissions(received_manure.nitrogen)

        if not manure_to_return:
            self.stored_manure = copy(self._manure_to_process)

        self._report_manure_stream(self._manure_to_process, "accumulated", time.simulation_day)
        self._report_manure_stream(received_manure, "received", time.simulation_day)

        data_origin_name = self.process_manure.__name__
        units = MeasurementUnits.KILOGRAMS
        self._report_processor_output(
            "outdoor_storage_manure_temperature",
            manure_temperature,
            data_origin_name,
            MeasurementUnits.DEGREES_CELSIUS,
            time.simulation_day,
        )
        self._report_processor_output(
            "storage_methane", total_storage_methane, data_origin_name, units, time.simulation_day
        )
        self._report_processor_output(
            "storage_ammonia_N", storage_ammonia_nitrogen, data_origin_name, units, time.simulation_day
        )
        self._report_processor_output(
            "storage_nitrous_oxide_N", storage_nitrous_oxide_nitrogen, data_origin_name, units, time.simulation_day
        )
        self._report_processor_output(
            "storage_methane_burned", storage_methane_burned, data_origin_name, units, time.simulation_day
        )

        return manure_to_return

    def _apply_methane_emissions(self, manure_temperature: float) -> tuple[float, float]:
        """
        This method computes the methane emissions from both degradable and non-degradable volatile solids in the
        manure, adjusts the manure's composition based on the amount of methane emitted, and accounts for the burning
        of methane if the storage cover is a cover and flare system.

        Parameters
        ----------
        manure_temperature : float
            The temperature of the manure in, (degrees Celsius).

        Returns
        -------
        tuple[float, float]
            A tuple containing:
            - The methane burned from manure storage on the current day, (kg).
            - The methane emitted from manure storage on the current day, (kg).

        """
        storage_methane_from_degradable_volatile_solids = self._calculate_methane_emissions(
            volatile_solids=self._manure_to_process.degradable_volatile_solids,
            manure_temperature=manure_temperature,
            is_degradable=True,
        )
        storage_methane_from_non_degradable_volatile_solids = self._calculate_methane_emissions(
            volatile_solids=self._manure_to_process.non_degradable_volatile_solids
            + self._manure_to_process.bedding_non_degradable_volatile_solids,
            manure_temperature=manure_temperature,
            is_degradable=False,
        )
        total_storage_methane = (
            storage_methane_from_degradable_volatile_solids + storage_methane_from_non_degradable_volatile_solids
        )

        storage_methane_burned = 0.0
        if self._cover == StorageCover.COVER_AND_FLARE:
            storage_methane_burned, total_storage_methane = self._calculate_cover_and_flare_methane(
                total_storage_methane
            )

        if (
            self._manure_to_process.non_degradable_volatile_solids
            + self._manure_to_process.bedding_non_degradable_volatile_solids
        ) > 0:
            bedding_to_manure_non_degradable_volatile_solids_ratio = (
                self._manure_to_process.bedding_non_degradable_volatile_solids
                / (
                    self._manure_to_process.non_degradable_volatile_solids
                    + self._manure_to_process.bedding_non_degradable_volatile_solids
                )
            )
        else:
            bedding_to_manure_non_degradable_volatile_solids_ratio = 0

        self._manure_to_process.total_solids = max(
            0.0,
            self._manure_to_process.total_solids - total_storage_methane * ManureConstants.VS_TO_METHANE_LOSS_RATIO,
        )
        self._manure_to_process.degradable_volatile_solids = max(
            0.0,
            (
                self._manure_to_process.degradable_volatile_solids
                - storage_methane_from_degradable_volatile_solids * ManureConstants.VS_TO_METHANE_LOSS_RATIO
            ),
        )
        self._manure_to_process.non_degradable_volatile_solids = max(
            0.0,
            self._manure_to_process.non_degradable_volatile_solids
            - (
                storage_methane_from_non_degradable_volatile_solids
                * ManureConstants.VS_TO_METHANE_LOSS_RATIO
                * (1 - bedding_to_manure_non_degradable_volatile_solids_ratio)
            ),
        )
        self._manure_to_process.bedding_non_degradable_volatile_solids = max(
            0.0,
            self._manure_to_process.bedding_non_degradable_volatile_solids
            - (
                storage_methane_from_non_degradable_volatile_solids
                * ManureConstants.VS_TO_METHANE_LOSS_RATIO
                * bedding_to_manure_non_degradable_volatile_solids_ratio
            ),
        )

        return storage_methane_burned, total_storage_methane

    def _apply_ammonia_emissions(self, manure_temperature: float) -> float:
        """
        This method computes the ammonia emissions from stored manure, and accounts the nitrogen
        and ammoniacal nitrogen loss due to ammonia emissions.

        Parameters
        ----------
        manure_temperature : float
            The temperature of the manure, (0degrees Celsius).

        Returns
        -------
        float
            The amount of nitrogen in the ammonia emitted from manure storage on the current day, (kg).

        """
        storage_ammonia_nitrogen = self._calculate_ammonia_emissions(
            total_ammoniacal_nitrogen=self._manure_to_process.ammoniacal_nitrogen,
            mass=self._manure_to_process.volume * ManureConstants.SLURRY_MANURE_DENSITY,
            density=ManureConstants.SLURRY_MANURE_DENSITY,
            temperature=manure_temperature,
            ammonia_resistance=ManureConstants.STORAGE_RESISTANCE,
            surface_area=self._surface_area,
            pH=ManureConstants.DEFAULT_STORED_MANURE_PH,
        )
        self._manure_to_process.ammoniacal_nitrogen = max(
            0.0, self._manure_to_process.ammoniacal_nitrogen - storage_ammonia_nitrogen
        )
        self._manure_to_process.nitrogen = max(0.0, self._manure_to_process.nitrogen - storage_ammonia_nitrogen)
        return storage_ammonia_nitrogen

    def _apply_nitrous_oxide_emissions(self, received_manure_nitrogen: float) -> float:
        """
        Calculates nitrous oxide emissions from stored manure and accounts for the nitrogen
        loss due to nitrous oxide emissions.

        Parameters
        ----------
        received_manure_nitrogen : float
            The nitrogen in the received manure on the current day.

        Returns
        -------
        float
            The amount of nitrogen in the nitrous oxide emitted from manure storage on the current day, (kg).

        """
        storage_nitrous_oxide_nitrogen = self._calculate_nitrous_oxide_emissions(
            nitrous_oxide_emissions_factor=ManureConstants.STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
                self._cover
            ],
            nitrogen_added=received_manure_nitrogen,
        )
        self._manure_to_process.nitrogen = max(0.0, self._manure_to_process.nitrogen - storage_nitrous_oxide_nitrogen)
        return storage_nitrous_oxide_nitrogen
