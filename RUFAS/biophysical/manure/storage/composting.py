from copy import copy
from math import inf

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.composting_type import CompostingType
from RUFAS.biophysical.manure.storage.solids_storage_calculator import SolidsStorageCalculator
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits

FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION: dict[CompostingType, float] = {
    CompostingType.STATIC_PILE: 0.5,
    CompostingType.PASSIVE_WINDROW: 0.45,
    CompostingType.INTENSIVE_WINDROW: 0.5,
}

FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION: dict[CompostingType, float] = {
    CompostingType.STATIC_PILE: 0.01,
    CompostingType.PASSIVE_WINDROW: 0.005,
    CompostingType.INTENSIVE_WINDROW: 0.005,
}

FRACTION_NITROGEN_LOST_TO_LEACHING: dict[CompostingType, float] = {
    CompostingType.STATIC_PILE: 0.06,
    CompostingType.PASSIVE_WINDROW: 0.04,
    CompostingType.INTENSIVE_WINDROW: 0.06,
}

MCF_TABLE: dict[tuple[float, float], dict[CompostingType, float]] = {
    (0.0, 10.0): {
        CompostingType.STATIC_PILE: 1.0,
        CompostingType.INTENSIVE_WINDROW: 0.5,
        CompostingType.PASSIVE_WINDROW: 1.0,
    },
    (10.0, 18.0): {
        CompostingType.STATIC_PILE: 2.0,
        CompostingType.INTENSIVE_WINDROW: 1.0,
        CompostingType.PASSIVE_WINDROW: 2.0,
    },
    (18.0, inf): {
        CompostingType.STATIC_PILE: 2.5,
        CompostingType.INTENSIVE_WINDROW: 1.5,
        CompostingType.PASSIVE_WINDROW: 2.5,
    },
}


class Composting(Storage):
    """
    Class for managing and simulating the composting process of manure treatment.

    This class simulates the composting process by considering various factors like weather,
    manure characteristics, and composting configurations. It provides methods for daily
    update of compost characteristics such as methane emissions, nitrogen content, and
    carbon decomposition. The calculations are based on standard composting models and
    environmental factors.

    Parameters
    ----------
    name : str
        The name of the storage.
    composting_type : str
        The type of the composting process being used.
    storage_time_period : int
        The storage time period.
    """

    def __init__(
        self,
        name: str,
        composting_type: str,
        storage_time_period: int,
        surface_area: float = inf,
    ):
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=StorageCover.NO_COVER,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
        )
        self._composting_type: CompostingType = CompostingType(composting_type)

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """Processes manure in Composting.

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

        manure_annual_temperature = current_day_conditions.annual_mean_air_temperature
        manure_temperature = current_day_conditions.mean_air_temperature
        if manure_annual_temperature:
            storage_methane = self._calculate_composting_methane_emissions(
                manure_annual_temperature,
                self._manure_to_process.degradable_volatile_solids
                + self._manure_to_process.non_degradable_volatile_solids,
                self._composting_type,
                self._manure_to_process.methane_production_potential,
            )
        else:
            storage_methane = 0
            info_map = {
                "class": self.__class__.__name__,
                "function": self.process_manure.__name__,
            }
            self._om.add_error(
                "No annual mean temperature",
                "No data of annual mean temperature available in current day condition to calculate MCF.",
                info_map=info_map,
            )

        carbon_decomposition = SolidsStorageCalculator.calculate_carbon_decomposition(
            manure_temperature,
            self._manure_to_process.non_degradable_volatile_solids,
            self._manure_to_process.degradable_volatile_solids,
        )
        self._apply_dry_matter_loss(storage_methane, carbon_decomposition)

        storage_nitrous_oxide_N = self._calculate_nitrous_oxide_emissions(
            FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION[self._composting_type],
            self._manure_to_process.nitrogen,
        )
        storage_N_loss_from_leaching = SolidsStorageCalculator.calculate_nitrogen_loss_to_leaching(
            FRACTION_NITROGEN_LOST_TO_LEACHING[self._composting_type], self._manure_to_process.nitrogen
        )
        storage_ammonia_N = self._calculate_composting_ammonia_emissions(
            self._composting_type, self._manure_to_process.nitrogen
        )
        self._apply_nitrogen_losses(storage_nitrous_oxide_N, storage_ammonia_N, storage_N_loss_from_leaching)
        self._manure_to_process.volume = self._manure_to_process.mass / ManureConstants.SOLID_MANURE_DENSITY

        self._received_manure = copy(self._manure_to_process)
        manure_to_return = super().process_manure(current_day_conditions, time)

        data_origin_function = self.process_manure.__name__
        simulation_day = time.simulation_day
        self._report_processor_output(
            "storage_methane", storage_methane, data_origin_function, MeasurementUnits.KILOGRAMS, simulation_day
        )
        self._report_processor_output(
            "storage_ammonia_N",
            storage_ammonia_N,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "storage_nitrous_oxide_N",
            storage_nitrous_oxide_N,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "storage_N_loss_from_leaching",
            storage_N_loss_from_leaching,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "carbon_decomposition",
            carbon_decomposition,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        accumulated_manure = manure_to_return["manure"] if "manure" in manure_to_return else self.stored_manure
        self._report_manure_stream(accumulated_manure, "accumulated", simulation_day)
        self._report_manure_stream(original_received_manure, "received", simulation_day)

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
    def _calculate_composting_ammonia_emissions(
        composting_type: CompostingType, received_manure_nitrogen: float
    ) -> float:
        """
        This function calculates the total nitrogen loss to ammonia emission on the current day.

        Parameters
        ----------
        composting_type : CompostingType
            The type of composting being used.
        received_manure_nitrogen : float
            The nitrogen content of the received manure, kg.

        Returns
        -------
        float
            The total nitrogen loss to ammonia emission on the current day, kg.
        """
        return FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION[composting_type] * received_manure_nitrogen

    @staticmethod
    def _calculate_composting_methane_emissions(
        manure_temperature: float,
        manure_volatile_solids: float,
        composting_type: CompostingType,
        methane_production_potential: float,
    ) -> float:
        """
        This function calculates the composting solid manure methane emission on the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature on the current day, Celsius.
        manure_volatile_solids : float
            The manure volatile solids of the received manure, kg.
        composting_type : CompostingType
            The type of composting being used.
        methane_production_potential : float
            Achievable emission of methane from dairy manure (m^3 methane / kg volatile solids).

        Returns
        -------
        float
            The solid manure methane emission on the current day, kg/day.
        """
        methane_conversion_factor = (
            Composting._calculate_methane_conversion_factor(manure_temperature, composting_type)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        )
        return manure_volatile_solids * (methane_production_potential * 0.67 * methane_conversion_factor)

    @staticmethod
    def _calculate_methane_conversion_factor(manure_temperature: float, composting_type: CompostingType) -> float:
        """
        This function returns the methane conversion factor depending on the composting type and the temperature.

        Parameters
        ----------
        manure_temperature : float
            The mean annual manure temperature, Celsius.
        composting_type : CompostingType
            The type of composting being used.

        Returns
        -------
        float
            The methane conversion factor, unitless.

        """
        om = OutputManager()
        if manure_temperature < 0:
            info_map = {
                "class": Composting.__class__.__name__,
                "function": Composting._calculate_methane_conversion_factor.__name__,
            }
            om.add_warning(
                "Unexpected value or temperature",
                f"Unrealistic (< 0 C) annual temperature provided." f" on average, received {manure_temperature}.",
                info_map=info_map,
            )
            return 0

        if manure_temperature < 10.0:
            return MCF_TABLE[(0.0, 10.0)][composting_type]

        elif manure_temperature < 18.0:
            return MCF_TABLE[(10.0, 18.0)][composting_type]
        else:
            return MCF_TABLE[(18.0, inf)][composting_type]
