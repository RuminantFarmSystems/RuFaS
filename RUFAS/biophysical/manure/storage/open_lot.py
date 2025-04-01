from copy import copy

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.open_lot_cbpb_calculator import OpenLotCbpbCalculator
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS: float = 0.36
"""
Ammonia emission coefficient used for calculating nitrogen loss in an open lot (unitless).
"""

NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS: float = 0.02
"""
Nitrous oxide coefficient used for calculating nitrogen loss in an open lot (unitless).
"""

LEACHING_COEFFICIENT: float = 0.035
"""Leaching coefficient used in the calculation of nitrogen loss in a compost bedded pack barn (unitless)."""


class OpenLot(Storage, OpenLotCbpbCalculator):
    def __init__(self, name: str, cover: StorageCover, storage_time_period: int | None, surface_area: float):
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        received_manure = copy(self._received_manure)
        manure_to_return = super().process_manure(current_day_conditions, time)
        self._manure_to_process = manure_to_return["manure"] if manure_to_return else copy(self._stored_manure)

        storage_nitrous_oxide = self._calculate_nitrous_oxide_emissions(
            NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS, received_manure.nitrogen
        )
        storage_methane = self.calculate_ifsm_methane_emission(
            self._received_manure.total_volatile_solids, current_day_conditions.mean_air_temperature
        )
        storage_nitrogen_leached = self.calculate_nitrogen_loss_from_leaching(received_manure.nitrogen)
        storage_ammonia = self._apply_ammonia_emission(received_manure.nitrogen)

        dry_matter_loss = self.calculate_dry_matter_changes(
            methane_emission=storage_methane,
            degradable_volatile_solids=received_manure.degradable_volatile_solids,
            non_degradable_volatile_solids=received_manure.non_degradable_volatile_solids,
        )

        degradable_volatile_solids_fraction = received_manure.degradable_volatile_solids / received_manure.total_solids
        self._manure_to_process.nitrogen = max(
            0.0,
            self._manure_to_process.nitrogen
            - self.calculate_total_nitrogen_loss_from_open_lots(
                storage_ammonia, storage_nitrogen_leached, storage_nitrous_oxide
            ),
        )
        self._manure_to_process.non_degradable_volatile_solids = max(
            0.0,
            self._manure_to_process.non_degradable_volatile_solids
            - (dry_matter_loss * degradable_volatile_solids_fraction),
        )
        self._manure_to_process.degradable_volatile_solids = max(
            0.0,
            self._manure_to_process.degradable_volatile_solids
            - (dry_matter_loss * (1 - degradable_volatile_solids_fraction)),
        )

        self._manure_to_process.total_solids = max(0.0, self._manure_to_process.total_solids - dry_matter_loss)
        self._manure_to_process.volume = self._manure_to_process.mass / ManureConstants.SOLID_MANURE_DENSITY

        if not manure_to_return:
            self._stored_manure = copy(self._manure_to_process)

        self._report_manure_stream(self._manure_to_process, "accumulated", time.simulation_day)
        self._report_manure_stream(received_manure, "received", time.simulation_day)

        data_origin_name = self.process_manure.__name__
        units = MeasurementUnits.KILOGRAMS
        self._report_processor_output("storage_methane", storage_methane, data_origin_name, units, time.simulation_day)
        self._report_processor_output(
            "storage_ammonia_N", storage_ammonia, data_origin_name, units, time.simulation_day
        )
        self._report_processor_output(
            "storage_nitrous_oxide_N", storage_nitrous_oxide, data_origin_name, units, time.simulation_day
        )
        self._report_processor_output(
            "storage_nitrogen_leached", storage_nitrogen_leached, data_origin_name, units, time.simulation_day
        )

        return manure_to_return

    def _apply_ammonia_emission(self, received_nitrogen) -> float:
        """
        Execute the ammonia emission process.

        Parameters
        ----------
        received_nitrogen : float


        Returns
        -------

        """
        storage_ammonia = self.calculate_nitrogen_loss_in_open_lots_from_ammonia_emission(received_nitrogen)
        self._manure_to_process.ammoniacal_nitrogen -= storage_ammonia
        return storage_ammonia

    @staticmethod
    def calculate_total_nitrogen_loss_from_open_lots(
        storage_ammonia: float, storage_nitrogen_leached: float, storage_nitrous_oxide: float
    ) -> float:
        """
        Calculate the total nitrogen loss from the open lots manure treatment.

        Parameters
        ----------
        storage_ammonia : float
            The amount of nitrogen lost to ammonia emission (kg).
        storage_nitrogen_leached : float
            The amount of nitrogen that leaches out of the bedding mixture (kg).
        storage_nitrous_oxide : float
            Nitrous oxide nitrogen emissions (kg).

        Returns
        -------
        float
            The total nitrogen loss from the open lots manure treatment (kg).

        """
        return storage_ammonia + storage_nitrogen_leached + storage_nitrous_oxide

    @staticmethod
    def calculate_nitrogen_loss_from_leaching(received_nitrogen: float) -> float:
        """
        Calculate the mass of nitrogen that leaches out of the manure-bedding mixture.

        Parameters
        ----------
        received_nitrogen : float
            The mass of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The amount of nitrogen that leaches out of the mixture (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.

        """

        if received_nitrogen < 0.0:
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {received_nitrogen}")

        return LEACHING_COEFFICIENT * received_nitrogen

    @staticmethod
    def calculate_nitrogen_loss_in_open_lots_from_ammonia_emission(received_nitrogen: float) -> float:
        """

        Parameters
        ----------
        received_nitrogen : float
            The amount of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The amount of nitrogen lost to ammonia emission (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.

        """
        if received_nitrogen < 0.0:
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {received_nitrogen}")

        return AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS * received_nitrogen

    def calculate_dry_matter_changes(
        self,
        methane_emission: float,
        degradable_volatile_solids: float,
        non_degradable_volatile_solids: float,
        moisture_effect: float = ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP,
        days_since_last_tillage: int = ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE,
        lag: int = ManureConstants.DEFAULT_LAG_TIME,
    ) -> float:
        """
        Calculate the changes in dry-matter for the manure-bedding mixture.

        Parameters
        ----------
        methane_emission : float
            The calculated methane emissions (in kg) for the given ambient barn temperature.
        degradable_volatile_solids : float
            Mass of degradable volatile solids in the manure stream (kg).
        non_degradable_volatile_solids : float
            Mass of non degradable volatile solids in the manure stream (kg).
        days_since_last_tillage : float
            The number of days since the manure-bedding mixture was last tilled.
            The default value can be found in ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE.
        lag : int
            The lag time used in the calculation of the carbon decomposition rate (days).
            The default value can be found in ManureConstants.DEFAULT_LAG_TIME.
        moisture_effect : float
            The effect of moisture on microbial decomposition (unitless).
            The default value can be found in ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP.

        Returns
        -------
        float
            The dry matter lost from carbon and methane emissions (kg).

        """
        carbon_decomposition = self.calculate_total_carbon_decomposition(
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            days_since_last_tillage=days_since_last_tillage,
            lag=lag,
            moisture_effect=moisture_effect,
        )
        dry_matter_loss = 2 * carbon_decomposition + methane_emission

        return dry_matter_loss
