from __future__ import annotations

import math
from typing import Tuple

from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.enums.ManureCoverEnum import ManureCoverEnum
from RUFAS.routines.manure.gas_emissions.calculator import GasEmissionsCalculator
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.time import Time
from RUFAS.weather import Weather


class SlurryStorageOutdoor(BaseManureTreatment):
    """Class for the outdoor slurry storage.

    Attributes:
        All attributes inherited from BaseManureTreatment.
        In addition, the following attributes are defined:
        storage_time_period: Time in days that the manure is stored in the manure
            treatment system, days.
        freeboard_input: Empty storage space above the manure in the treatment system.
            onto the treatment system.

    """

    def __init__(self, weather: Weather, time: Time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initializes the outdoor slurry storage manure treatment.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.
        """

        super().__init__(weather, time, manure_treatment_config)
        self.freeboard_input = self.config.freeboard_input

    @property
    def wastewater_volume(self) -> float:
        """Calculates the volume of wastewater in the treatment system.

        Returns:
            The volume of wastewater in the treatment system, m^3.

        """
        if self._current_manure_treatment_daily_input:
            return self._current_manure_treatment_daily_input.liquid_manure_daily_volume
        return 0.0

    @property
    def treatment_volume(self) -> float:
        """Calculates the minimum treatment volume.

        Returns:
            The minimum treatment volume, m^3.

        """
        if isinstance(self.storage_time_period, int):
            return self.wastewater_volume * self.storage_time_period
        else:
            return 0.0

    @property
    def total_pit_volume(self) -> float:
        """Calculates the total pit volume.

        Returns:
            The total lagoon pit, m^3.

        """
        if self._current_manure_treatment_daily_input:
            return self.treatment_volume + self.freeboard_volume + self.precipitation_volume
        return 0.0

    @property
    def pit_depth(self) -> float:
        """Returns the depth of the pit.

        Returns:
            The depth of the pit, m.

        """
        return 3.657

    @property
    def pit_slope(self) -> float:
        """Returns the slope of the pit.

        Returns:
            The slope of the pit, dimensionless.

        """
        return 2.0

    def _calc_abc(self) -> Tuple[float, float, float]:
        """Calculates the coefficients a, b, and c for volume calculations.

        Returns:
            A tuple containing the coefficients a, b, and c for volume calculations.

        """
        a = 3 * self.pit_depth
        b = -4 * self.pit_slope * self.pit_depth**2
        c = 4 * (self.pit_slope**2) * (self.pit_depth**3) / 3 - self.treatment_volume
        return a, b, c

    @property
    def pit_width(self) -> float:
        """Calculates the width of the pit.

        Returns:
            The width of the pit, m.

        """
        if self._current_manure_treatment_daily_input:
            a, b, c = self._calc_abc()
            return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)
        return 0.0

    @property
    def pit_length(self) -> float:
        """Calculate the length of the pit.

        Returns:
            The length of the pit, m.

        """
        return self.pit_width * 3

    @property
    def pit_surface_area(self) -> float:
        """Calculate the surface area of the pit.

        The surface area is calculated as the product of the number of animals in the pen
        and the DEFAULT_STORAGE_AREA_PER_ANIMAL constant.

        Returns:
            The surface area of the pit, m^2.

        """
        if self._current_pen is not None and self._current_pen.num_animals is not None:
            return self._current_pen.num_animals * GasEmissionConstants.DEFAULT_STORAGE_AREA_PER_ANIMAL
        else:
            return 0

    @property
    def pit_volume(self) -> float:
        """Calculates the volume of the pit.

        Returns:
            The volume of the pit, m^3.

        """
        return (
            self.pit_length * self.pit_width * self.pit_depth
            - (self.pit_slope * (self.pit_depth**2)) * (self.pit_length + self.pit_width)
            + (4 * self.pit_slope * (self.pit_depth**3) / 3)
        )

    @property
    def precipitation_volume(self) -> float:
        """Calculates the additional pit volume needed for precipitation.

        Returns:
            The additional pit volume needed for precipitation, m^3.

        """
        return self._get_current_day_rainfall() * self.pit_surface_area

    @property
    def freeboard_volume(self) -> float:
        """Calculates the additional pit volume needed for freeboard.

        Returns:
            The additional pit volume needed for freeboard, m^3.

        """
        return self.freeboard_input * self.pit_surface_area

    def _adjust_final_manure_volume(self, current_day_final_manure_volume: float) -> float:
        """
        Adjust the final manure volume to account for the precipitation and the storage time period.

        Parameters
        ----------
        current_day_final_manure_volume : float
            The final manure volume for the current simulation day (:math:`m^3`).

        Returns
        -------
        float
            The adjusted final manure volume.

        """
        if self.config.manure_cover in [ManureCoverEnum.NO_COVER.value, ManureCoverEnum.CRUST.value]:
            return current_day_final_manure_volume + self.precipitation_volume
        else:
            return current_day_final_manure_volume

    def calc_methane_emission(
        self,
        accumulated_liquid_manure_total_volatile_solids: float,
        accumulated_liquid_manure_total_degradable_volatile_solids: float,
        accumulated_liquid_manure_total_non_degradable_volatile_solids: float,
    ) -> Tuple[float, float]:
        """Calculates the CH4 emission from the outdoor slurry storage treatment system.

        Parameters
        ----------
        accumulated_liquid_manure_total_volatile_solids: float
            The accumulated total VS in the treatment system, kg VS.
        accumulated_liquid_manure_total_degradable_volatile_solids: float
            The accumulated total degradable VS in the treatment system, kg VSd.
        accumulated_liquid_manure_total_non_degradable_volatile_solids: float
            The accumulated total non-degradable VS in the treatment system, kg VSnd.

        Returns
        -------
        float
            methane_loss: methane emission from the outdoor slurry storage treatment system, (kg :math:`CH_4`/day).
        float
            methane_emission_from_degradable_volatile_solids: methane emission from total degradable solids,
            (kg :math:`CH_4`/day).

        """
        air_temperature = self._get_current_day_average_temperature_celsius()
        stored_manure_temperature = self._determine_outdoor_storage_temperature(air_temperature)
        # fmt: off
        methane_loss, methane_emission_from_degradable_volatile_solids = (
            GasEmissionsCalculator.calculate_liquid_storage_methane(
                accumulated_liquid_manure_total_degradable_volatile_solids=(
                    accumulated_liquid_manure_total_degradable_volatile_solids),
                accumulated_liquid_manure_total_non_degradable_volatile_solids=(
                    accumulated_liquid_manure_total_non_degradable_volatile_solids),
                stored_manure_temperature=stored_manure_temperature,
            )
        )
        # fmt: on
        return methane_loss, methane_emission_from_degradable_volatile_solids

    def calc_ammonia_emission(
        self,
        num_animals: int,
        accumulated_manure_volume: float,
        accumulated_manure_total_ammoniacal_nitrogen: float,
    ) -> float:
        """Calculates the ammonia emission from the outdoor slurry storage treatment system.

        Parameters
        ----------
        num_animals : int
            The number of animals in the barn.
        accumulated_manure_volume : float
            The accumulated manure volume in the treatment system, m^3.
        accumulated_manure_total_ammoniacal_nitrogen : float
            The accumulated TAN in the treatment system, kg.
        accumulated_manure_total_solids : float
            The accumulated total solids in the treatment system, kg.

        Returns
        -------
        float
            The ammonia emission from the outdoor slurry storage in kg.

        """
        air_temperature = self._get_current_day_average_temperature_celsius()
        storage_temperature = self._determine_outdoor_storage_temperature(air_temperature)
        ammonia_loss = GasEmissionsCalculator.calculate_liquid_storage_ammonia_emission(
            num_animals=num_animals,
            manure_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen,
            manure_volume=accumulated_manure_volume,
            manure_density=ManureConstants.SLURRY_MANURE_DENSITY,
            storage_temperature=storage_temperature,
        )

        return ammonia_loss

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the daily output of the outdoor slurry storage treatment system.

        Returns
        -------
        ManureTreatmentDailyOutput
            An object containing the daily output of the slurry storage outdoor treatment system.

        """
        daily_input = self._current_manure_treatment_daily_input
        if daily_input:
            daily_output = self._initialize_daily_output_during_update(daily_input)
        adjusted_daily_final_manure_volume = self._adjust_final_manure_volume(daily_output.daily_final_manure_volume)
        daily_output.set_daily_final_manure_volume(adjusted_daily_final_manure_volume)

        self._adjust_accumulated_output(daily_output)
        # fmt: off
        methane_loss, methane_emission_from_degradable_volatile_solids = self.calc_methane_emission(
            accumulated_liquid_manure_total_volatile_solids=(
                self._accumulated_output.liquid_manure_total_volatile_solids),
            accumulated_liquid_manure_total_degradable_volatile_solids=(
                self._accumulated_output.liquid_manure_total_degradable_volatile_solids),
            accumulated_liquid_manure_total_non_degradable_volatile_solids=(
                self._accumulated_output.liquid_manure_total_non_degradable_volatile_solids),
        )

        daily_output.storage_methane = methane_loss

        if self.config.manure_cover == ManureCoverEnum.COVER_AND_FLARE.value:
            daily_output.storage_methane_burned, daily_output.storage_methane = self.calculate_cover_and_flare_methane(
                methane_loss)

        # fmt: on
        methane_emission_from_non_degradable_volatile_solids = (
            methane_loss - methane_emission_from_degradable_volatile_solids
        )

        ammonia_loss = self.calc_ammonia_emission(
            num_animals=self._current_pen.num_animals,
            accumulated_manure_volume=self._accumulated_output.daily_final_manure_volume,
            accumulated_manure_total_ammoniacal_nitrogen=(
                self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen
            ),
        )
        daily_output.storage_ammonia = ammonia_loss

        new_daily_output_liquid_manure_total_solids = max(daily_output.liquid_manure_total_solids - methane_loss, 0.0)
        daily_output.liquid_manure_total_solids = new_daily_output_liquid_manure_total_solids

        new_daily_output_liquid_manure_nitrogen = max(daily_output.liquid_manure_nitrogen - ammonia_loss, 0.0)
        daily_output.liquid_manure_nitrogen = new_daily_output_liquid_manure_nitrogen

        new_daily_output_liquid_manure_total_ammoniacal_nitrogen = max(
            daily_output.liquid_manure_total_ammoniacal_nitrogen - ammonia_loss, 0.0
        )
        daily_output.liquid_manure_total_ammoniacal_nitrogen = new_daily_output_liquid_manure_total_ammoniacal_nitrogen

        self._accumulated_output.storage_ammonia += ammonia_loss
        self._accumulated_output.storage_methane += methane_loss

        new_accumulated_liquid_manure_total_solids = max(
            self._accumulated_output.liquid_manure_total_solids
            - (methane_loss * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_solids = new_accumulated_liquid_manure_total_solids

        new_accumulated_liquid_manure_total_volatile_solids = max(
            self._accumulated_output.liquid_manure_total_volatile_solids
            - (methane_loss * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_volatile_solids = (
            new_accumulated_liquid_manure_total_volatile_solids
        )

        new_accumulated_liquid_manure_total_degradable_volatile_solids = max(
            self._accumulated_output.liquid_manure_total_degradable_volatile_solids
            - (
                methane_emission_from_degradable_volatile_solids
                * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
            ),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_degradable_volatile_solids = (
            new_accumulated_liquid_manure_total_degradable_volatile_solids
        )

        new_accumulated_liquid_manure_total_non_degradable_volatile_solids = max(
            self._accumulated_output.liquid_manure_total_non_degradable_volatile_solids
            - (
                methane_emission_from_non_degradable_volatile_solids
                * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
            ),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_non_degradable_volatile_solids = (
            new_accumulated_liquid_manure_total_non_degradable_volatile_solids
        )

        new_accumulated_liquid_manure_nitrogen = max(
            self._accumulated_output.liquid_manure_nitrogen - ammonia_loss, 0.0
        )
        self._accumulated_output.liquid_manure_nitrogen = new_accumulated_liquid_manure_nitrogen
        new_accumulated_liquid_manure_total_ammoniacal_nitrogen = max(
            self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen - ammonia_loss,
            0.0,
        )
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = (
            new_accumulated_liquid_manure_total_ammoniacal_nitrogen
        )
        emissions_factor = self._get_nitrous_oxide_emissions_factor(
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR, self.config.manure_cover
        )
        daily_output.storage_nitrous_oxide = (
            GasEmissionsCalculator.calculate_empirical_nitrogen_loss_from_nitrous_oxide_emission(
                emission_factor_kg_nitrous_oxide_N_per_kg_manure_N=emissions_factor,
                manure_nitrogen_kg_N_per_day=daily_input.liquid_manure_nitrogen,
            )
        )
        daily_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide
        self._accumulated_output.storage_nitrous_oxide += daily_output.storage_nitrous_oxide
        self._accumulated_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide

        return daily_output
