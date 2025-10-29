from copy import copy
from math import inf

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.solids_storage_calculator import SolidsStorageCalculator
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class OpenLot(Storage):
    def __init__(
        self,
        name: str,
        storage_time_period: int | None,
        surface_area: float = inf,
        cover: StorageCover = StorageCover.NO_COVER,
    ):
        super().__init__(
            name=name,
            is_housing_emissions_calculator=True,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """Processes manure in open lot.

        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The current day conditions.
        time : RufasTime
            The time of the simulation.

        Returns
        -------
        dict[str, ManureStream]
            _The processed manure stream.

        """
        original_received_manure = copy(self._received_manure)
        self._manure_to_process = copy(self._received_manure)

        storage_methane = SolidsStorageCalculator.calculate_ifsm_methane_emission(
            self._manure_to_process.degradable_volatile_solids
            + self._manure_to_process.non_degradable_volatile_solids,
            current_day_conditions.mean_air_temperature,
            self._manure_to_process.methane_production_potential,
        )
        carbon_decomposition = SolidsStorageCalculator.calculate_carbon_decomposition(
            ManureConstants.DEFAULT_LAYER_TEMPERATURE,
            self._manure_to_process.non_degradable_volatile_solids,
            self._manure_to_process.degradable_volatile_solids,
        )
        self._apply_dry_matter_loss(storage_methane, carbon_decomposition)

        storage_nitrous_oxide_N = self._calculate_nitrous_oxide_emissions(
            ManureConstants.NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS, self._manure_to_process.nitrogen
        )

        storage_N_loss_from_leaching = SolidsStorageCalculator.calculate_nitrogen_loss_to_leaching(
            ManureConstants.LEACHING_COEFFICIENT, self._manure_to_process.nitrogen
        )
        storage_ammonia_N = self._calculate_open_lot_ammonia_emissions(self._manure_to_process.nitrogen)

        self._apply_nitrogen_losses(storage_nitrous_oxide_N, storage_ammonia_N, storage_N_loss_from_leaching)
        self._manure_to_process.volume = self._manure_to_process.mass / ManureConstants.SOLID_MANURE_DENSITY

        self._received_manure = copy(self._manure_to_process)
        manure_to_return = super().process_manure(current_day_conditions, time)

        data_origin_function = self.process_manure.__name__
        simulation_day = time.simulation_day
        units = MeasurementUnits.KILOGRAMS
        self._report_processor_output("storage_methane", storage_methane, data_origin_function, units, simulation_day)
        self._report_processor_output(
            "storage_ammonia_N", storage_ammonia_N, data_origin_function, units, simulation_day
        )
        self._report_processor_output(
            "storage_nitrous_oxide_N", storage_nitrous_oxide_N, data_origin_function, units, simulation_day
        )
        self._report_processor_output(
            "storage_N_loss_from_leaching", storage_N_loss_from_leaching, data_origin_function, units, simulation_day
        )
        self._report_processor_output(
            "carbon_decomposition", carbon_decomposition, data_origin_function, units, simulation_day
        )

        accumulated_manure = manure_to_return["manure"] if "manure" in manure_to_return else self.stored_manure
        self._report_manure_stream(accumulated_manure, "accumulated", simulation_day)
        self._report_manure_stream(original_received_manure, "received", time.simulation_day)

        return manure_to_return

    def _apply_dry_matter_loss(self, methane_emission: float, carbon_decomposition: float) -> None:
        """
        This function calculates and then applies the dry matter loss to the received manure in place.

        Parameters
        ----------
        methane_emission : float
            The methane emission on the current day, kg/day.
        carbon_decomposition : float
            The carbon decomposition on the current day, kg/day.

        Raises
        ------
        ValueError
            If any of the dry matter loss calculations results in negative values for received-manure
            non-degradable volatile solids, degradable volatile solids, or total solids.
        """
        dry_matter_loss = SolidsStorageCalculator.calculate_dry_matter_loss(methane_emission, carbon_decomposition)
        degradable_volatile_solids_fraction = SolidsStorageCalculator.calculate_degradable_volatile_solids_fraction(
            self._manure_to_process.degradable_volatile_solids, self._manure_to_process.total_volatile_solids
        )
        non_degradable_volatile_solids_after_losses = max(0, (
            self._manure_to_process.non_degradable_volatile_solids
            - dry_matter_loss * (1 - degradable_volatile_solids_fraction)
        ))
        degradable_volatile_solids_after_losses = max(0, (
            self._manure_to_process.degradable_volatile_solids
            - dry_matter_loss * degradable_volatile_solids_fraction
        ))
        total_solids_after_losses = self._manure_to_process.total_solids - dry_matter_loss

        errors = []
        if non_degradable_volatile_solids_after_losses < 0:
            errors.append("non_degradable_volatile_solids")
        if degradable_volatile_solids_after_losses < 0:
            errors.append("degradable_volatile_solids")
        if total_solids_after_losses < 0:
            errors.append("total_solids")

        if errors:
            error_message = (
                f"Dry-matter loss calculations resulted in negative received-manure values for: {', '.join(errors)}."
            )
            self._om.add_error(
                "Dry-matter loss application error",
                error_message,
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._apply_dry_matter_loss.__name__,
                },
            )
            raise ValueError(error_message)

        self._manure_to_process.non_degradable_volatile_solids = non_degradable_volatile_solids_after_losses
        self._manure_to_process.degradable_volatile_solids = degradable_volatile_solids_after_losses
        self._manure_to_process.total_solids = total_solids_after_losses

    def _apply_nitrogen_losses(
        self, storage_nitrous_oxide_N: float, storage_ammonia_N: float, storage_N_loss_from_leaching: float
    ) -> None:
        """
        This function applies the nitrogen losses to the received manure nitrogen and ammoniacal nitrogen in place.

        Parameters
        ----------
        storage_nitrous_oxide_N : float
            The nitrogen loss through nitrous oxide emissions on the current day, kg.
        storage_ammonia_N : float
            The nitrogen loss through ammonia emissions on the current day, kg.
        storage_N_loss_from_leaching : float
            The nitrogen loss through leaching on the current day, kg.

        Raises
        ------
        ValueError
            If the total nitrogen losses are greater than the total received manure nitrogen.
        """
        received_manure_nitrogen_after_losses = (
            self._manure_to_process.nitrogen
            - storage_nitrous_oxide_N
            - storage_ammonia_N
            - storage_N_loss_from_leaching
        )
        if received_manure_nitrogen_after_losses < 0:
            self._om.add_error(
                "Nitrogen loss application error",
                "Cannot have total nitrogen losses greater than total received manure nitrogen.",
                info_map={"class": self.__class__.__name__, "function": self._apply_nitrogen_losses.__name__},
            )
            raise ValueError(
                "Nitrogen loss application error: cannot have total nitrogen losses greater than "
                "total received manure nitrogen."
            )
        self._manure_to_process.ammoniacal_nitrogen = max(
            0.0, self._manure_to_process.ammoniacal_nitrogen - storage_ammonia_N
        )
        self._manure_to_process.nitrogen = received_manure_nitrogen_after_losses

    @staticmethod
    def _calculate_open_lot_ammonia_emissions(received_nitrogen: float) -> float:
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

        return ManureConstants.AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS * received_nitrogen
