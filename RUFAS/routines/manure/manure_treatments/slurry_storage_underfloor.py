from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import GasEmissionsCalculator
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather


class SlurryStorageUnderfloor(BaseManureTreatment):
    """Class for the underfloor slurry storage.

    Attributes:
        All attributes inherited from BaseManureTreatment.
        In addition, the following attributes are defined:
        storage_time_period: RufasTime in days that the manure is stored in the manure
            treatment system, days.

    """

    def __init__(self, weather: Weather, time: RufasTime, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initialize the underfloor slurry storage manure treatment.

        Args:
            weather: A Weather object.
            time: A RufasTime object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.

        """
        super().__init__(weather, time, manure_treatment_config)

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

        Notes
        -----
        Barn temperature is being calculated and used here because the slurry is indoors.

        """
        air_temperature = self._get_current_day_average_temperature_celsius()
        barn_temperature = GasEmissionsCalculator.determine_barn_air_temperature(air_temperature)
        # fmt: off
        methane_loss, methane_emission_from_degradable_volatile_solids = (
            GasEmissionsCalculator.calculate_liquid_storage_methane(
                accumulated_liquid_manure_total_degradable_volatile_solids=(
                    accumulated_liquid_manure_total_degradable_volatile_solids),
                accumulated_liquid_manure_total_non_degradable_volatile_solids=(
                    accumulated_liquid_manure_total_non_degradable_volatile_solids),
                stored_manure_temperature=barn_temperature,
            )
        )
        # fmt: on
        return methane_loss, methane_emission_from_degradable_volatile_solids

    def calc_ammonia_emission(
        self,
        num_animals: int,
        accumulated_manure_volume: float,
        accumulated_manure_total_ammoniacal_nitrogen: float,
    ) -> Tuple[float, float]:
        """Calculates the ammonia emission from the underfloor slurry storage.

        Args:
            num_animals: Number of animals in the pen, animals.
            barn_area: Area of the barn per animal, m^2/animal.
            accumulated_manure_volume: Accumulated manure volume in the treatment system, m^3.
            accumulated_manure_total_ammoniacal_nitrogen: Accumulated total ammoniacal nitrogen in the treatment
            system, kg.

        Returns:
            ammonia_loss: ammonia emission from the underfloor slurry storage, kg.
            new_accumulated_liquid_manure_total_ammoniacal_nitrogen: Accumulated total ammoniacal nitrogen
            in the treatment system after the ammonia emission is calculated, kg.

        """
        air_temperature = self._get_current_day_average_temperature_celsius()
        barn_temperature = GasEmissionsCalculator.determine_barn_air_temperature(air_temperature)
        ammonia_loss = GasEmissionsCalculator.calculate_liquid_storage_ammonia_emission(
            num_animals=num_animals,
            manure_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen,
            manure_volume=accumulated_manure_volume,
            manure_density=ManureConstants.SLURRY_MANURE_DENSITY,
            storage_temperature=barn_temperature,
        )

        return ammonia_loss

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the daily output of the slurry storage underfloor system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage underfloor system.

        """
        daily_input = self._current_manure_treatment_daily_input
        daily_output = self._initialize_daily_output_during_update(daily_input)
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

        daily_output.storage_methane = methane_loss
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

        new_accumulated_liquid_manure_nitrogen = max(
            self._accumulated_output.liquid_manure_nitrogen - ammonia_loss, 0.0
        )
        self._accumulated_output.liquid_manure_nitrogen = new_accumulated_liquid_manure_nitrogen

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

        new_accumulated_liquid_total_ammoniacal_nitrogen = max(
            self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen - ammonia_loss,
            0.0,
        )
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = (
            new_accumulated_liquid_total_ammoniacal_nitrogen
        )
        emissions_factor = self._get_nitrous_oxide_emissions_factor(
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR, self.config.manure_cover
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
