from copy import copy

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants


class AnaerobicLagoon(Storage):
    """
    Anaerobic Lagoon class

    Parameters
    ----------
    name : str
        The name of the storage.
    cover : StorageCover
        The cover for the storage.
    storage_time_period : int | None
        The storage time period.
    surface_area : float
        The surface area of the storage.
    capacity : float
        The capacity of the storage.

    """

    def __init__(
        self,
        name: str,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        capacity: float,
    ):
        """Initialize Anaerobic Lagoon object."""
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
            capacity=capacity,
        )

    @property
    def _emptying_fraction(self) -> float:
        """
        The fraction of the accumulated stored manure that is removed from storage when the emptying time is reached.
        """
        return 1.0 - ManureConstants.ANAEROBIC_LAGOON_MANURE_RETENTION

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """Processes manure in Anaerobic Lagoon.

        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The current day conditions.
        time : RufasTime
            The time.

        Returns
        -------
        dict[str, ManureStream]
            The processed manure stream. Will be empty if it is not time to empty the storage.
        """
        if self._cover in [StorageCover.NO_COVER, StorageCover.CRUST]:
            precipitation_volume = current_day_conditions.precipitation * GeneralConstants.MM_TO_M * self._surface_area
            self._received_manure.volume += precipitation_volume
            self._received_manure.water += precipitation_volume * UserConstants.WATER_DENSITY_KG_PER_M3

        received_manure = copy(self._received_manure)
        manure_to_return = super().process_manure(current_day_conditions, time)
        self._manure_to_process = manure_to_return["manure"] if manure_to_return else copy(self.stored_manure)

        manure_temperature = self._determine_outdoor_storage_temperature(
            time.current_julian_day, ManureConstants.ANAEROBIC_LAGOON_MINIMUM_TEMPERATURE
        )

        total_storage_methane, storage_methane_burned = self._apply_methane_emissions(manure_temperature)
        storage_ammonia = self._apply_ammonia_emissions(manure_temperature)
        nitrous_oxide_emissions = self._calculate_nitrous_oxide_emissions(
            nitrous_oxide_emissions_factor=ManureConstants.STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
                self._cover
            ],
            nitrogen_added=received_manure.nitrogen,
        )

        received_manure.nitrogen = max(0.0, received_manure.nitrogen - nitrous_oxide_emissions)

        if not manure_to_return:
            self.stored_manure = copy(self._manure_to_process)

        self._report_manure_stream(self._manure_to_process, "accumulated", time.simulation_day)
        self._report_manure_stream(received_manure, "received", time.simulation_day)

        function_name = self.process_manure.__name__
        self._report_processor_output(
            "storage_methane", total_storage_methane, function_name, MeasurementUnits.KILOGRAMS, time.simulation_day
        )
        self._report_processor_output(
            "outdoor_storage_manure_temperature",
            manure_temperature,
            function_name,
            MeasurementUnits.DEGREES_CELSIUS,
            time.simulation_day,
        )
        self._report_processor_output(
            "storage_methane_burned",
            storage_methane_burned,
            function_name,
            MeasurementUnits.KILOGRAMS,
            time.simulation_day,
        )
        self._report_processor_output(
            "storage_ammonia_N", storage_ammonia, function_name, MeasurementUnits.KILOGRAMS, time.simulation_day
        )
        self._report_processor_output(
            "storage_nitrous_oxide_N",
            nitrous_oxide_emissions,
            function_name,
            MeasurementUnits.KILOGRAMS,
            time.simulation_day,
        )

        return manure_to_return

    def _apply_methane_emissions(self, manure_temperature: float) -> tuple[float, float]:
        """
        This method computes the methane emissions from both degradable and non-degradable volatile solids in the
        manure, adjusts the manure's composition based on the amount of methane emitted, and accounts for the burning
        of methane if the storage cover is a cover and flare system.

        It applies the methane emissions to self._manure_to_process in-place.

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
        total_methane = (
            storage_methane_from_degradable_volatile_solids + storage_methane_from_non_degradable_volatile_solids
        )

        total_non_degradable_VS = (
            self._manure_to_process.non_degradable_volatile_solids
            + self._manure_to_process.bedding_non_degradable_volatile_solids
        )

        if (
            self._manure_to_process.non_degradable_volatile_solids == 0.0
            or self._manure_to_process.bedding_non_degradable_volatile_solids == 0.0
            or total_non_degradable_VS == 0.0
        ):
            bedding_to_manure_non_degradable_volatile_solids_ratio = 0.0
        else:
            bedding_to_manure_non_degradable_volatile_solids_ratio = (
                self._manure_to_process.bedding_non_degradable_volatile_solids / total_non_degradable_VS
            )

        storage_methane_burned = 0.0
        if self._cover == StorageCover.COVER_AND_FLARE:
            storage_methane_burned, adjusted = self._calculate_cover_and_flare_methane(total_methane)
            total_methane = adjusted

        mass_loss = total_methane * ManureConstants.VS_TO_METHANE_LOSS_RATIO
        self._manure_to_process.total_solids = max(0.0, self._manure_to_process.total_solids - mass_loss)
        self._manure_to_process.degradable_volatile_solids = max(
            0.0,
            self._manure_to_process.degradable_volatile_solids
            - (storage_methane_from_degradable_volatile_solids * ManureConstants.VS_TO_METHANE_LOSS_RATIO),
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

        return total_methane, storage_methane_burned

    def _apply_ammonia_emissions(self, manure_temperature: float) -> float:
        """
        This method computes the ammonia emissions from stored manure, and accounts the nitrogen
        and ammoniacal nitrogen loss due to ammonia emissions.

        Applies ammonia losses to self._manure_to_process in-place.

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
