from __future__ import annotations

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import (
    GasEmissionsCalculator,
)
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


class AnaerobicDigestion(BaseManureTreatment):
    """A class that calculates the output of an anaerobic digester.

    Attributes:
        Same as BaseManureTreatment.

    """

    def _calc_daily_sludge_output(
        self,
        daily_output: ManureTreatmentDailyOutput,
        manure_treatment_daily_input: LiquidManurePortionProtocol,
    ) -> ManureTreatmentDailyOutput:
        """Calculates the daily sludge output for the current day."""
        new_daily_output = daily_output.clone()
        new_daily_output.sludge_manure_total_solids = (
            manure_treatment_daily_input.liquid_manure_total_solids
            * self.config.total_solids_removal_efficiency_for_treatment
        )
        new_daily_output.sludge_manure_total_volatile_solids = (
            manure_treatment_daily_input.liquid_manure_total_volatile_solids
            * self.config.volatile_solids_removal_efficiency_for_treatment
        )
        new_daily_output.sludge_manure_nitrogen = (
            manure_treatment_daily_input.liquid_manure_nitrogen
            * self.config.nitrogen_removal_efficiency_for_treatment
        )
        new_daily_output.sludge_manure_phosphorus = (
            manure_treatment_daily_input.liquid_manure_phosphorus
            * self.config.phosphorus_removal_efficiency_for_treatment
        )
        new_daily_output.sludge_manure_potassium = (
            manure_treatment_daily_input.liquid_manure_potassium
            * self.config.potassium_removal_efficiency_for_treatment
        )
        new_daily_output.sludge_manure_daily_volume = (
            manure_treatment_daily_input.liquid_manure_total_volatile_solids
            * 0.03
            / ManureConstants.MANURE_DENSITY
        )  # TODO: Use constants instead
        return new_daily_output

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the daily output from anaerobic digestion.

        Returns:
            The daily output from anaerobic digestion.

        """
        daily_input = self._current_manure_treatment_daily_input
        daily_output = self._initialize_daily_output_during_update(
            self._current_manure_treatment_daily_input
        )
        daily_output = self._calc_daily_sludge_output(
            daily_output, self._current_manure_treatment_daily_input
        )
        daily_output = self._calc_anaerobic_digestion_daily_output(daily_output)
        self._accumulate_daily_output(daily_output)
        return daily_output

    def _calc_anaerobic_digestion_daily_output(
        self, manure_treatment_daily_output: ManureTreatmentDailyOutput
    ) -> ManureTreatmentDailyOutput:
        """Returns the daily output from anaerobic digestion.

        Args:

        Returns:
            The daily output from anaerobic digestion.

        """
        daily_final_manure_volume = (
            manure_treatment_daily_output.daily_final_manure_volume
        )
        new_daily_output = manure_treatment_daily_output.clone()

        moisture_content = self._calc_moisture_content(
            total_daily_mass=daily_final_manure_volume,
            liquid_manure_total_solids=self._manure_handler_daily_output.liquid_manure_total_solids,
        )
        average_temperature_celsius = (
            self._get_current_day_average_temperature_celsius()
        )
        heating_input_energy = (
            self._calc_specific_input_energy(
                average_temperature_celsius, moisture_content
            )
            * daily_final_manure_volume
            * GeneralConstants.LITERS_TO_CUBIC_METERS
        )
        # MS.3.B.7R
        methane_generation_volume = GasEmissionsCalculator.methane_volume_via_Chen_equation(
            manure_total_volatile_solids=self._manure_handler_daily_output.liquid_manure_total_volatile_solids,
            hydraulic_retention_time=self.config.hydraulic_retention_time,
        )
        biogas_energy_content = GasEmissionsCalculator.biogas_energy_content(
            methane_volume=methane_generation_volume
        )
        # MS.3.B.2
        minimum_digester_volume = (
            daily_final_manure_volume * self.config.hydraulic_retention_time
        )
        # MS.3.B.3
        top_cover_volume = (
            minimum_digester_volume * self.config.top_cover_volume_fraction
        )

        new_daily_output.biogas = (
            self.config.biogas_generation_ratio
            * self._manure_handler_daily_output.liquid_manure_total_volatile_solids
        )
        new_daily_output.heating_input_energy = heating_input_energy
        new_daily_output.evaporated_water = (
            self.config.evaporation_fraction * daily_final_manure_volume
        )
        new_daily_output.biogas_energy_content = biogas_energy_content
        new_daily_output.minimum_digester_volume = minimum_digester_volume
        new_daily_output.top_cover_volume = top_cover_volume
        return new_daily_output

    @classmethod
    def _calc_moisture_content(
        cls, total_daily_mass: float, liquid_manure_total_solids: float
    ) -> float:
        """Returns moisture_content of influent as decimal (0-1).

        Args:
            total_daily_mass: Total daily mass of influent, kg.
            liquid_manure_total_solids: Total solids of influent, kg.

        Returns:
            Moisture content of influent as decimal (0-1).

        """
        if total_daily_mass > 0:
            return 1 - (liquid_manure_total_solids / total_daily_mass)
        return 0.0

    def _calc_specific_input_energy(
        self, average_temperature_celsius, moisture_content
    ) -> float:
        """Returns the energy required to maintain anaerobic digestion temperature at set point.

        Args:
            average_temperature_celsius: Average daily temperature, C.
            moisture_content: A 0-1 decimal representing water content of manure.

        Returns:
            Energy required to maintain anaerobic digestion temperature at set point, MJ/m^3.

        """
        effluent_temperature = self._bound_influent_temperature(
            average_temperature_celsius
        )
        influent_heat_capacity = self._calc_manure_heat_capacity(
            average_temperature_celsius, moisture_content
        )
        anaerobic_digestion_heat_capacity = self._calc_manure_heat_capacity(
            self.config.anaerobic_digestion_temperature_set_point, moisture_content
        )
        average_manure_heat_capacity = (
            influent_heat_capacity + anaerobic_digestion_heat_capacity
        ) / 2
        heating_input_energy = average_manure_heat_capacity * (
            self.config.anaerobic_digestion_temperature_set_point - effluent_temperature
        )
        return heating_input_energy

    @classmethod
    def _bound_influent_temperature(cls, average_temperature_celsius: float) -> float:
        """Returns the max between the given average temperature and temperature bound.

        Args:
            average_temperature_celsius: Average daily temperature, C.

        """
        return max(average_temperature_celsius, 4.0)  # TODO: Use constants instead

    @classmethod
    def _calc_manure_heat_capacity(
        cls, average_temperature_celsius: float, moisture_content: float
    ) -> float:
        """Returns heat capacity of manure.

        Args:
            average_temperature_celsius: Average daily temperature, C.
            moisture_content: A 0-1 decimal representing water content of manure.

        Returns:
            Heat capacity of manure, kJ /kg /C.

        """
        # TODO: Name the constants if you can
        return (
            0.68298
            + 0.025662 * average_temperature_celsius
            + 0.01306 * moisture_content * 100
        )
