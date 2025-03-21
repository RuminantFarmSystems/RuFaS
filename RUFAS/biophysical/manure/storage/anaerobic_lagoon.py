from copy import copy
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits

METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO: float = 9.25
"""
The mass conversion factor from methane to methane and carbon dioxide emitted from stored manure, based on a molar
ratio of 1:3 (methane : carbon dioxide).
"""

SLURRY_MANURE_DENSITY = 990
"""The density of slurry manure (kg/:math:`m^3`)."""

STORAGE_HSC = 4.1
"""Housing specific constant for manure storage (s/m)."""

DEFAULT_PH_FOR_AMMONIA: float = 7.5
"""Default pH for ammonia (unitless)."""

"""
Mapping of storage cover types to the nitrous oxide emissions factor associated with that cover type (kg nitrous oxide N
/ kg manure N).
"""
STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING: dict[StorageCover, float] = {
    StorageCover.COVER: 0.005,
    StorageCover.CRUST: 0.005,
    StorageCover.NO_COVER: 0.0,
    StorageCover.COVER_AND_FLARE: 0.005,
}


class AnaerobicLagoon(Storage):
    """
    Anaerobic Lagoon class

    Parameters
    ----------
    name: str
        The name of the storage.
    is_housing_emissions_calculator: bool
        True if the storage is used for housing emissions calculation.
    cover: StorageCover
        The cover for the storage.
    storage_time_period: int | None
        The storage time period.
    surface_area: float
        The surface area of the storage.
    nitrous_oxide_emissions_factor: float
        The nitrous oxide emissions factor.
    capacity: float
        The capacity of the storage.

    """

    def __init__(
        self,
        name: str,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        nitrous_oxide_emissions_factor: float,
        capacity: float,
    ):
        """Initialize Anaerobic Lagoon object."""
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
            nitrous_oxide_emissions_factor=nitrous_oxide_emissions_factor,
            capacity=capacity,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """Processes manure in Anaerobic Lagoon.

        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The current day conditions.
        time : Time
            The time.

        Returns
        -------
        dict[str, ManureStream]
            The processed manure stream. Will be empty if it is not time to empty the storage.
        """
        precipitation_volume = current_day_conditions.precipitation * GeneralConstants.MM_TO_M * self._surface_area
        if self._cover in [StorageCover.NO_COVER, StorageCover.CRUST]:
            self._received_manure.volume += precipitation_volume
            self._received_manure.water += precipitation_volume * GeneralConstants.WATER_DENSITY_KG_PER_M3

        received_manure = copy(self._received_manure)
        manure_to_return = super().process_manure(current_day_conditions, time)
        stored_manure = manure_to_return["manure"] if manure_to_return else copy(self._stored_manure)

        manure_temperature = self._determine_outdoor_storage_temperature(
            air_temperature=current_day_conditions.mean_air_temperature
        )

        total_storage_methane, storage_methane_burned = self._apply_methane_emissions(stored_manure, manure_temperature)
        storage_ammonia = self._apply_ammonia_emissions(stored_manure, manure_temperature)
        nitrous_oxide_emissions = self._apply_nitrous_oxide_emissions(stored_manure, received_manure)

        if not manure_to_return:
            self._stored_manure = copy(stored_manure)

        self._report_manure_stream(stored_manure, "accumulated", time)
        self._report_manure_stream(received_manure, "received", time)

        self._report_storage_gas_emissions(total_storage_methane, storage_ammonia, nitrous_oxide_emissions, time)
        self._report_anaerobic_lagoon_outputs(storage_methane_burned, time)

        return manure_to_return

    def _apply_methane_emissions(self, stored_manure: ManureStream, manure_temp: float) -> tuple[float, float]:
        """
        Modifies stored_manure in-place to apply methane losses.
        Returns total methane emitted and methane burned.
        """
        methane_degradable = self._calculate_methane_emissions(
            volatile_solids=stored_manure.degradable_volatile_solids,
            manure_temperature=manure_temp,
            is_degradable=True,
        )
        methane_non_degradable = self._calculate_methane_emissions(
            volatile_solids=stored_manure.non_degradable_volatile_solids,
            manure_temperature=manure_temp,
            is_degradable=False,
        )
        total_methane = methane_degradable + methane_non_degradable
        methane_burned = 0.0

        if self._cover == StorageCover.COVER_AND_FLARE:
            methane_burned, adjusted = self._calculate_cover_and_flare_methane(total_methane)
            total_methane = adjusted

        carbon_loss = total_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        stored_manure.total_solids = max(0.0, stored_manure.total_solids - carbon_loss)
        stored_manure.degradable_volatile_solids = max(
            0.0, stored_manure.degradable_volatile_solids - methane_degradable * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
        stored_manure.non_degradable_volatile_solids = max(
            0.0,
            stored_manure.non_degradable_volatile_solids
            - (methane_non_degradable * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
        )

        return total_methane, methane_burned

    def _apply_ammonia_emissions(self, stored_manure: ManureStream, manure_temp: float) -> float:
        """
        Modifies stored_manure in-place to apply ammonia losses.
        Returns storage ammonia emissions.
        """
        storage_ammonia = self._calculate_ammonia_emissions(
            total_ammoniacal_nitrogen=stored_manure.ammoniacal_nitrogen,
            volume=stored_manure.volume,
            density=SLURRY_MANURE_DENSITY,
            temperature=manure_temp,
            ammonia_resistance=STORAGE_HSC,
            surface_area=self._surface_area,
            pH=DEFAULT_PH_FOR_AMMONIA,
        )
        stored_manure.ammoniacal_nitrogen = max(0.0, stored_manure.ammoniacal_nitrogen - storage_ammonia)
        stored_manure.nitrogen = max(0.0, stored_manure.nitrogen - storage_ammonia)
        return storage_ammonia

    def _apply_nitrous_oxide_emissions(self, stored_manure: ManureStream, received_manure: ManureStream) -> float:
        """
        Modifies stored_manure in-place to apply nitrous oxide losses.
        Returns nitrous oxide emissions.
        """
        nitrous_oxide_emissions = self._calculate_nitrous_oxide_emissions(
            nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[self._cover],
            nitrogen_added=received_manure.nitrogen,
        )
        stored_manure.nitrogen = max(0.0, stored_manure.nitrogen - nitrous_oxide_emissions)
        return nitrous_oxide_emissions

    def _report_anaerobic_lagoon_outputs(self, storage_methane_burned: float, time: Time) -> None:
        """Reports the outputs of the Anaerobic Lagoon."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._report_storage_gas_emissions.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
            "units": MeasurementUnits.KILOGRAMS,
        }

        self._om.add_variable("storage_methane_burned", storage_methane_burned, info_map)
