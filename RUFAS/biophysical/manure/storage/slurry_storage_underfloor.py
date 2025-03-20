from copy import copy

from math import inf

from RUFAS.biophysical.manure.storage.storage import (
    Storage,
    DEFAULT_PH_FOR_AMMONIA,
    STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING,
)
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


SLURRY_MANURE_DENSITY = 990
"""The density of slurry manure (kg/:math:`m^3`)."""

STORAGE_HSC = 4.1
"""Housing specific constant for manure storage (s/m)."""

METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO: float = 9.25
"""
The mass conversion factor from methane to methane and carbon dioxide emitted from stored manure, based on a molar
ratio of 1:3 (methane : carbon dioxide).
"""


class SlurryStorageUnderfloor(Storage):
    def __init__(
        self,
        name: str,
        is_housing_emissions_calculator: bool,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        nitrous_oxide_emissions_factor: float,
        capacity: float = inf,
    ):
        super().__init__(
            name=name,
            is_housing_emissions_calculator=is_housing_emissions_calculator,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
            nitrous_oxide_emissions_factor=nitrous_oxide_emissions_factor,
            capacity=capacity,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        received_manure = self._received_manure
        manure_to_return = super().process_manure(current_day_conditions, time)
        stored_manure = manure_to_return["manure"] if manure_to_return else copy(self._stored_manure)

        manure_temperature = self._determine_outdoor_storage_temperature(
            air_temperature=current_day_conditions.mean_air_temperature
        )
        storage_methane_from_degradable_volatile_solids = self._calculate_methane_emissions(
            volatile_solids=stored_manure.degradable_volatile_solids,
            manure_temperature=manure_temperature,
            is_degradable=True,
        )
        storage_methane_from_non_degradable_volatile_solids = self._calculate_methane_emissions(
            volatile_solids=stored_manure.non_degradable_volatile_solids,
            manure_temperature=manure_temperature,
            is_degradable=False,
        )
        total_storage_methane = (
            storage_methane_from_degradable_volatile_solids + storage_methane_from_non_degradable_volatile_solids
        )

        stored_manure.total_solids = max(
            0.0, stored_manure.total_solids - total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
        stored_manure.degradable_volatile_solids = max(
            0.0,
            (
                stored_manure.degradable_volatile_solids
                - storage_methane_from_degradable_volatile_solids * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
            ),
        )
        stored_manure.non_degradable_volatile_solids = max(
            0.0,
            (
                stored_manure.non_degradable_volatile_solids
                - storage_methane_from_non_degradable_volatile_solids * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
            ),
        )

        storage_ammonia = self._calculate_ammonia_emissions(
            total_ammoniacal_nitrogen=stored_manure.ammoniacal_nitrogen,
            volume=stored_manure.volume,
            density=SLURRY_MANURE_DENSITY,
            temperature=manure_temperature,
            ammonia_resistance=STORAGE_HSC,
            surface_area=self._surface_area,
            pH=DEFAULT_PH_FOR_AMMONIA,
        )
        stored_manure.ammoniacal_nitrogen = max(0.0, stored_manure.ammoniacal_nitrogen - storage_ammonia)
        stored_manure.nitrogen = max(0.0, stored_manure.nitrogen - storage_ammonia)

        nitrous_oxide_emissions = self._calculate_nitrous_oxide_emissions(
            nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[self._cover],
            nitrogen_added=received_manure.nitrogen,
        )
        stored_manure.nitrogen = max(0.0, stored_manure.nitrogen - nitrous_oxide_emissions)

        if not manure_to_return:
            self._stored_manure = copy(stored_manure)

        self._report_manure_stream(stored_manure, "accumulated", time)
        self._report_manure_stream(received_manure, "received", time)

        self._report_storage_outputs(total_storage_methane, storage_ammonia, nitrous_oxide_emissions, time)

        return manure_to_return
