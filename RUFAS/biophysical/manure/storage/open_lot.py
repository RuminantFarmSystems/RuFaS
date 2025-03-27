from copy import copy

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time

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

class OpenLot(Storage):
    def __init__(self, name: str, is_housing_emissions_calculator: bool, cover: StorageCover,
                 storage_time_period: int | None, surface_area: float, nitrous_oxide_emissions_factor: float):
        super().__init__(name, is_housing_emissions_calculator, cover, storage_time_period, surface_area,
                         nitrous_oxide_emissions_factor)

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        received_manure = copy(self._received_manure)
        manure_to_return = super().process_manure(current_day_conditions, time)
        self._manure_to_process = manure_to_return["manure"] if manure_to_return else copy(self._stored_manure)
        storage_methane = self.calculate_ifsm_methane_emission(self._received_manure.total_volatile_solids,
                                                               current_day_conditions.mean_air_temperature)
        return {}

    @classmethod
    def calculate_ifsm_methane_emission(cls, manure_volatile_solids: float, ambient_barn_temp: float) -> float:
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
        methane_conversion_factor = cls.calculate_methane_conversion_factor(ambient_barn_temp)
        methane_emissions_in_kg = (
            manure_volatile_solids * Bo * METHANE_FACTOR * methane_conversion_factor
        ) / 100
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

    @staticmethod
    def calculate_nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(received_nitrogen: float) -> float:
        """
        Calculate the nitrogen loss from nitrous oxide emission in the open lots manure treatment.

        Parameters
        ----------
        received_nitrogen : float
            The amount of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The nitrogen lost to nitrous oxide emission (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.

        """

        if received_nitrogen < 0.0:
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {received_nitrogen}")

        return NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS * received_nitrogen
