from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import (
    GasEmissionsCalculator,
)
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    ManureTreatmentConfig,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)


class SlurryStorageUnderfloor(BaseManureTreatment):
    """Class for the underfloor slurry storage.

    Attributes:
        All attributes inherited from BaseManureTreatment.
        In addition, the following attributes are defined:
        storage_time_period: Time in days that the manure is stored in the manure
            treatment system, days.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initialize the underfloor slurry storage manure treatment.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.

        """
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period

    def calc_methane_emission(self, accumulated_liquid_manure_total_solids: float) -> Tuple[float, float]:
        """Calculates the methane emission from the underfloor slurry storage.

        Args:
            accumulated_liquid_manure_total_solids: Accumulated manure total solids in the treatment system, kg.

        Returns:
            methane_loss: methane emission from the underfloor slurry storage, kg.
            new_accumulated_liquid_manure_total_solids: Accumulated total solids in the treatment system
            after the methane emission is calculated, kg.

        """
        temperature_celsius = self._get_current_day_average_temperature_celsius()
        methane_loss = GasEmissionsCalculator.methane_emission_from_slurry_storage(
            total_volatile_solids=accumulated_liquid_manure_total_solids,
            temp=temperature_celsius,
        )

        return methane_loss

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
        ammonia_loss = GasEmissionsCalculator.storage_ammonia_emission(
            num_animals=num_animals,
            manure_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen,
            manure_volume=accumulated_manure_volume,
            manure_density=ManureConstants.SLURRY_MANURE_DENSITY,
            temp=self._get_current_day_average_temperature_celsius(),
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
        self._accumulated_output = self._adjust_accumulated_output(daily_output)

        methane_loss = self.calc_methane_emission(self._accumulated_output.liquid_manure_total_solids)

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
            self._accumulated_output.liquid_manure_total_solids - methane_loss, 0.0
        )
        self._accumulated_output.liquid_manure_total_solids = new_accumulated_liquid_manure_total_solids

        new_accumulated_liquid_total_ammoniacal_nitrogen = max(
            self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen - ammonia_loss,
            0.0,
        )
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = (
            new_accumulated_liquid_total_ammoniacal_nitrogen
        )

        daily_output.storage_nitrous_oxide = self._calc_empirical_nitrogen_loss_from_nitrous_oxide_emission(
            manure_treatment_type=ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR,
            manure_cover=self.config.manure_cover,
            manure_nitrogen_kg_N_per_day=daily_output.liquid_manure_nitrogen,
        )
        daily_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide
        self._accumulated_output.storage_nitrous_oxide += daily_output.storage_nitrous_oxide
        self._accumulated_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide

        return daily_output

    def _adjust_accumulated_output(
        self, manure_treatment_daily_output: ManureTreatmentDailyOutput
    ) -> ManureTreatmentDailyOutput:
        """
        Adjust the accumulated output by either resetting it or adding the daily output to it.

        The accumulated output will be reset on the first day of every storage time period.

        Parameters
        ----------
        manure_treatment_daily_output : ManureTreatmentDailyOutput
            The daily output from the manure treatment system.

        Returns
        -------
        ManureTreatmentDailyOutput
            The adjusted accumulated output.

        """
        if self._sim_day % self.storage_time_period == 1:
            return manure_treatment_daily_output.clone()
        else:
            new_accumulated_output = self._accumulated_output + manure_treatment_daily_output
            return new_accumulated_output
