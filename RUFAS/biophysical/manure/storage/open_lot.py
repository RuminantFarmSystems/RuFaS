from copy import copy

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.open_lot_composting_emission import OpenLotCompostingEmission
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits

ACHIEVABLE_METHANE_EMISSION: float = 0.24
"""Achievable emission of methane (:math:`CH_4`) from dairy manure (:math:`m^3 CH_4`/kg VS)."""

METHANE_FACTOR: float = 0.67
"""Unit conversion factor for methane from :math:`m^3` to kg (unitless)."""

MCF_CONSTANT_A: float = 0.0625
"""
Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
Methane Conversion Factor (MCF) calculation. The coefficient scales the ambient barn temperature.
"""

MCF_CONSTANT_B: float = 0.25
"""
Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
Methane Conversion Factor (MCF) calculation. The coefficient is a constant offset.
"""

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


class OpenLot(Storage, OpenLotCompostingEmission):
    def __init__(
        self,
        name: str,
        is_housing_emissions_calculator: bool,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        nitrous_oxide_emissions_factor: float,
    ):
        super().__init__(
            name,
            is_housing_emissions_calculator,
            cover,
            storage_time_period,
            surface_area,
            nitrous_oxide_emissions_factor,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        received_manure = copy(self._received_manure)
        manure_to_return = super().process_manure(current_day_conditions, time)
        self._manure_to_process = manure_to_return["manure"] if manure_to_return else copy(self._stored_manure)

        # Report these three in received only.
        storage_nitrous_oxide = self._calculate_nitrous_oxide_emissions(NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS,
                                                                        received_manure.nitrogen)
        storage_methane = self.calculate_ifsm_methane_emission(
            self._received_manure.total_volatile_solids, current_day_conditions.mean_air_temperature
        )
        storage_nitrogen_leached = self.calculate_nitrogen_loss_from_leaching(received_manure.nitrogen)
        storage_ammonia = self._apply_ammonia_emission(received_manure.nitrogen)

        dry_matter_loss = self._calc_dry_matter_changes(current_day_conditions.mean_air_temperature,
                                                        received_manure.total_solids,
                                                        received_manure.total_volatile_solids)
        degradable_volatile_solids_fraction = received_manure.degradable_volatile_solids / received_manure.total_solids
        self._manure_to_process.nitrogen = max(0.0,
                                               self._manure_to_process.nitrogen -
                                               self.calculate_total_nitrogen_loss_from_open_lots(
                                                   received_manure.nitrogen))
        self._manure_to_process.non_degradable_volatile_solids = \
            max(0.0,
                self._manure_to_process.non_degradable_volatile_solids - (dry_matter_loss
                                                                          * degradable_volatile_solids_fraction))
        self._manure_to_process.degradable_volatile_solids = \
            max(0.0,
                self._manure_to_process.degradable_volatile_solids - (dry_matter_loss
                                                                      * (1 - degradable_volatile_solids_fraction)))
        self._manure_to_process.total_solids  = max(0.0, self._manure_to_process.total_solids - dry_matter_loss)
        self._manure_to_process.volume = self._manure_to_process.mass / ManureConstants.SOLID_MANURE_DENSITY
        if not manure_to_return:
            self._stored_manure = copy(self._manure_to_process)

        self._report_manure_stream(self._manure_to_process, "accumulated", time.simulation_day)
        self._report_manure_stream(received_manure, "received", time.simulation_day)

        data_origin_name = self.process_manure.__name__
        units = MeasurementUnits.KILOGRAMS
        self._report_processor_output(
            "storage_methane", storage_methane, data_origin_name, units, time.simulation_day)
        self._report_processor_output(
            "storage_ammonia_N", storage_ammonia, data_origin_name, units, time.simulation_day)
        self._report_processor_output(
            "storage_nitrous_oxide_N", storage_nitrous_oxide, data_origin_name, units, time.simulation_day)

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

    def calculate_total_nitrogen_loss_from_open_lots(self, received_nitrogen: float) -> float:
        """
        Calculate the total nitrogen loss from the open lots manure treatment.

        Parameters
        ----------
        received_nitrogen : float
            The amount of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The total nitrogen loss from the open lots manure treatment (kg).

        """
        return (
            OpenLot.calculate_nitrogen_loss_in_open_lots_from_ammonia_emission(received_nitrogen)
            + OpenLot.calculate_nitrogen_loss_from_leaching(received_nitrogen)
            + self._calculate_nitrous_oxide_emissions(NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS, received_nitrogen)
        )

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
            The amount of nitrogen that leaches out of the bedding mixture (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if received_nitrogen < 0.0:
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {received_nitrogen}")

        return LEACHING_COEFFICIENT * received_nitrogen

    @staticmethod
    def calculate_ifsm_methane_emission(manure_volatile_solids: float, ambient_barn_temp: float) -> float:
        """Calculates emission of methane for a day using an adaptation of the tier 2 approach
        of the IPCC(2006), given ambient barn temperature and a methane conversion factor for the manure
        management.

        Parameters
        ----------
        manure_volatile_solids : float
            The volatile solids (in kg)

        ambient_barn_temp : float
            The ambient barn temperature (in Celsius)

        Returns
        -------
        float
            The calculated methane emissions (in kg) for the given ambient barn temperature.

        Notes
        -----
        CH4 emission = (VS * Bo * 0.67 * MCF) / 100

        """
        if manure_volatile_solids < 0:
            raise ValueError(f"{manure_volatile_solids=} mass must be positive.")
        Bo = ACHIEVABLE_METHANE_EMISSION
        methane_conversion_factor = OpenLot.calculate_methane_conversion_factor(ambient_barn_temp)
        methane_emissions_in_kg = (manure_volatile_solids * Bo * METHANE_FACTOR * methane_conversion_factor) / 100
        return methane_emissions_in_kg

    @staticmethod
    def calculate_methane_conversion_factor(ambient_barn_temp: float) -> float:
        """
        Calculate the Methane Conversion Factor (MCF) for the open lots treatment using the following function:

        MCF(T) = 0.0625 * T - 0.25

        Parameters
        ----------
        ambient_barn_temp : float
            The ambient barn temperature (in Celsius).

        Returns
        -------
        float
            The calculated Methane Conversion Factor (MCF) for the given ambient barn temperature.

        References
        ----------
        .. [1] Open Lots Design Document, V1 eqn. M.1.A.1

        """
        return MCF_CONSTANT_A * ambient_barn_temp - MCF_CONSTANT_B

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

    def _calc_dry_matter_changes(
        self,
        temperature: float,
        total_solids: float,
        manure_volatile_solids: float,
        moisture_effect: float = ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP,
        days_since_last_tillage: int = ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE,
        lag: int = ManureConstants.DEFAULT_LAG_TIME,
        carbon_fraction_available_in_manure: float = ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
    ) -> float:
        """
        Calculate the changes in dry-matter for the manure-bedding mixture.

        Parameters
        ----------
        temperature : float
            Average temperature of the current day (Celsius).
        total_solids : float
            The total mass of the manure (kg).
        manure_volatile_solids : float
            The mass of manure volatile solids (kg).
        days_since_last_tillage : float
            The number of days since the manure-bedding mixture was last tilled.
            The default value can be found in ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE.
        lag : int
            The lag time used in the calculation of the carbon decomposition rate (days).
            The default value can be found in ManureConstants.DEFAULT_LAG_TIME.
        moisture_effect : float
            The effect of moisture on microbial decomposition (unitless).
            The default value can be found in ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP.
        carbon_fraction_available_in_manure : float
            The proportion of carbon available in manure (unitless).
            The default value can be found in ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE.

        Returns
        -------
        float
            The dry matter lost from carbon and methane emissions (kg).

        """
        methane_emission = self.calculate_ifsm_methane_emission(manure_volatile_solids, temperature)
        carbon_decomposition = self.total_carbon_decomposition(
            manure_total_solids=total_solids,
            days_since_last_tillage=days_since_last_tillage,
            lag=lag,
            moisture_effect=moisture_effect,
            carbon_available_in_manure=carbon_fraction_available_in_manure
        )

        dry_matter_loss = 2 * carbon_decomposition + methane_emission

        return dry_matter_loss
