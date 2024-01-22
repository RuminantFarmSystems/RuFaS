import math
from typing import Dict

from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.composting_types import CompostingType
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput

FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION: Dict[CompostingType, float] = {
        CompostingType.STATIC_PILE: 0.5,
        CompostingType.PASSIVE_WINDROW: 0.45,
        CompostingType.INTENSIVE_WINDROW: 0.5
    }

FRACTION_NITROGEN_LOST_TO_LEACHING: Dict[CompostingType, float] = {
        CompostingType.STATIC_PILE: 0.06,
        CompostingType.PASSIVE_WINDROW: 0.04,
        CompostingType.INTENSIVE_WINDROW: 0.06
    }

FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION: Dict[CompostingType, float] = {
        CompostingType.STATIC_PILE: 0.06,
        CompostingType.PASSIVE_WINDROW: 0.04,
        CompostingType.INTENSIVE_WINDROW: 0.06
    }


class Composting(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        daily_input = self._current_manure_treatment_daily_input

        manure_volatile_solids = daily_input.liquid_manure_total_volatile_solids
        manure_total_solids = daily_input.liquid_manure_total_solids

        methane_emission = self._calculate_methane_emission(volatile_solid=manure_volatile_solids)
        carbon_decomposition = self._calculate_carbon_decomposition(total_solid=manure_total_solids)

        daily_dry_matter_loss = self._calculate_dry_matter_loss(methane_emission=methane_emission,
                                                                carbon_decomposition=carbon_decomposition)

        daily_output = ManureTreatmentDailyOutput(
            simulation_day=daily_input.simulation_day,
            pen_id=daily_input.pen_id,
            storage_methane=methane_emission,
            solid_manure_phosphorus=daily_input.liquid_manure_phosphorus,
            solid_manure_potassium=daily_input.liquid_manure_potassium
        )
        self._accumulate_daily_output(daily_output)
        return daily_output

    def annual_update(self) -> None:
        total_Nitrogen_mass = self._calculate_total_Nitrogen_mass()
        organic_Nitrogen_mass = self._calculate_organic_Nitrogen_mass()
        inorganic_Nitrogen_mass = self._calculate_inorganic_Nitrogen_mass()
        ammonia_mass = self._calculate_ammonium_mass()

    def calc_methane_emission(self, *args, **kwargs) -> float:
        manure_volatile_solids = self._current_manure_treatment_daily_input.liquid_manure_total_volatile_solids
        return self._calculate_methane_emission(manure_volatile_solids)

    def calc_ammonia_emission(self, *args, **kwargs) -> float:
        return self._calculate_Nitrogen_loss_to_ammonia_emission()

    def _calculate_methane_conversion_factor(self) -> float:
        if self.config.composting_type == CompostingType.STATIC_PILE:
            return 0.005
        else:
            current_day_mean_air_temperature = self._get_current_day_average_temperature_celsius()
            if current_day_mean_air_temperature < 15:
                return 0.005
            elif 15 <= current_day_mean_air_temperature <= 25:
                return 0.01
            else:
                return 0.015

    def _calculate_methane_emission(self, volatile_solid: float) -> float:
        maximum_methane_producing_capacity = self.config.maximum_methane_producing_capacity
        methane_conversion_factor = self._calculate_methane_conversion_factor()
        return (volatile_solid * 365) * (maximum_methane_producing_capacity * 0.67 * methane_conversion_factor)

    def _calculate_max_microbial_decomposition_rate(self) -> float:
        effectiveness_of_microbial_decomposition_rate = self.config.effectiveness_of_microbial_decomposition_rate
        decomposition_temperature = self.config.decomposition_temperature

        return effectiveness_of_microbial_decomposition_rate * (1.066 ** (decomposition_temperature - 10) - 1.21 **
                                                                (decomposition_temperature - 50))

    def _calculate_slow_microbial_decomposition_rate(self) -> float:
        effectiveness_of_microbial_decomposition_rate = self.config.effectiveness_of_microbial_decomposition_rate
        compost_pile_pack_temperature = self._get_current_day_average_temperature_celsius()

        return effectiveness_of_microbial_decomposition_rate * (1.066 ** (compost_pile_pack_temperature - 10) - 1.21 **
                                                                (compost_pile_pack_temperature - 50))

    def _calculate_carbon_decomposition_rate(self) -> float:
        max_microbial_decomposition_rate = self._calculate_max_microbial_decomposition_rate()
        slow_microbial_decomposition_rate = self._calculate_slow_microbial_decomposition_rate()

        decay = self.config.first_order_decaying_coefficient
        last_turning_or_addition = self.config.last_compost_turning_or_addition
        lag = self.config.lag_time

        return (max_microbial_decomposition_rate - slow_microbial_decomposition_rate) * \
               (math.e ** (decay * (last_turning_or_addition - lag))) * slow_microbial_decomposition_rate

    def _calculate_anaerobic_coefficient(self) -> float:
        o2 = self.config.mole_fraction_of_oxygen
        o2_half_saturation = self.config.half_saturation_constant
        o2_ambient = self.config.ambient_air_mole_fraction_of_oxygen

        return (o2 / (o2_half_saturation + o2)) * ((o2_half_saturation + o2_ambient) / o2_ambient)

    def _calculate_carbon_decomposition(self, total_solid: float) -> float:
        """
        Calculate total carbon decomposition in kg/day
        """
        c_manure = self.config.proportion_of_carbon_available_in_manure
        c_bedding = self.config.proportion_of_carbon_available_in_bedding
        effect_moist = self.config.effect_of_moisture_on_microbial_decomposition

        q_bedding = self._manure_handler_daily_output.total_bedding_mass

        carbon_decomposition_rate = self._calculate_carbon_decomposition_rate()
        anaerobic_coefficient = self._calculate_anaerobic_coefficient()

        return (total_solid * c_manure +
                q_bedding * c_bedding) * carbon_decomposition_rate * effect_moist * anaerobic_coefficient

    @staticmethod
    def _calculate_dry_matter_loss(methane_emission: float, carbon_decomposition: float) -> float:
        return 2 * carbon_decomposition + methane_emission

    def _calculate_Nitrogen_loss_to_ammonia_emission(self) -> float:
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        fraction_Nitrogen_lost_as_ammonia = FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION[self.config.composting_type]

        return fraction_Nitrogen_lost_as_ammonia * N_prior_t

    def _calculate_Nitrogen_loss_to_leaching(self) -> float:
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        fraction_Nitrogen_lost_as_ammonia = FRACTION_NITROGEN_LOST_TO_LEACHING[self.config.composting_type]

        return fraction_Nitrogen_lost_as_ammonia * N_prior_t

    def _calculate_Nitrogen_loss_to_direct_Nitrous_Oxide_Emission(self) -> float:
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        fraction_Nitrogen_lost_as_ammonia = FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION[self.config.composting_type]

        return fraction_Nitrogen_lost_as_ammonia * N_prior_t * 44/28

    def _calculate_Nitrogen_loss_to_indirect_Nitrous_Oxide_Emission(self) -> float:
        Nitrogen_loss_to_leaching = self._calculate_Nitrogen_loss_to_leaching()
        Nitrogen_loss_to_ammonia_emission = self._calculate_Nitrogen_loss_to_ammonia_emission()

        return (Nitrogen_loss_to_leaching +
                Nitrogen_loss_to_ammonia_emission) * ManureConstants.COMPOSTING_N2O_INDIRECT_EMISSION_FACTOR * 44/28

    def _calculate_total_Nitrogen_mass(self) -> float:
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        Nitrogen_loss_to_ammonia_emission = self._calculate_Nitrogen_loss_to_ammonia_emission()
        Nitrogen_loss_to_leaching = self._calculate_Nitrogen_loss_to_leaching()
        Nitrogen_loss_to_direct_N2O_emission = self._calculate_Nitrogen_loss_to_direct_Nitrous_Oxide_Emission()
        Nitrogen_loss_to_indirect_N2O_emission = self._calculate_Nitrogen_loss_to_indirect_Nitrous_Oxide_Emission()

        return \
            N_prior_t - Nitrogen_loss_to_ammonia_emission - Nitrogen_loss_to_leaching - \
            Nitrogen_loss_to_direct_N2O_emission - Nitrogen_loss_to_indirect_N2O_emission

    def _calculate_organic_Nitrogen_mass(self) -> float:
        total_Nitrogen_mass = self._calculate_total_Nitrogen_mass()

        return total_Nitrogen_mass * 0.952

    def _calculate_inorganic_Nitrogen_mass(self) -> float:
        total_Nitrogen_mass = self._calculate_total_Nitrogen_mass()

        return total_Nitrogen_mass * 0.048

    def _calculate_ammonium_mass(self) -> float:
        inorganic_Nitrogen_mass = self._calculate_inorganic_Nitrogen_mass()

        return inorganic_Nitrogen_mass * 0.5
