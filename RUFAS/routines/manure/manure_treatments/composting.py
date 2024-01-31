import math

from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.composting_types import CompostingType
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class Composting(BaseManureTreatment):
    """
    Class for managing and simulating the composting process of manure treatment.

    This class simulates the composting process by considering various factors like weather,
    manure characteristics, and composting configurations. It provides methods for daily
    update of compost characteristics such as methane emissions, nitrogen content, and
    carbon decomposition. The calculations are based on standard composting models and
    environmental factors.

    Attributes
    ----------
    weather : Weather
        The current weather conditions.
    time : Time
        The current time information.
    manure_treatment_config : ManureTreatmentConfig
        Configuration settings for manure treatment.
    composting_type : CompostingType
        The type of composting process being used.

    Methods
    -------
    _daily_update_helper() -> ManureTreatmentDailyOutput:
        Performs daily updates to the compost characteristics.

    calc_methane_emission(*args, **kwargs) -> float:
        Calculates the methane emissions for the current day.

    calc_ammonia_emission(*args, **kwargs) -> float:
        Calculates the total nitrogen loss to ammonia emission for the current year.

    _calculate_methane_conversion_factor() -> float:
        Returns the methane conversion factor based on composting type and temperature.

    _calculate_max_microbial_decomposition_rate() -> float:
        Calculates the maximum microbial decomposition rate for the current day.

    _calculate_slow_microbial_decomposition_rate() -> float:
        Calculates the slow microbial decomposition rate for the current day.

    _calculate_carbon_decomposition_rate() -> float:
        Calculates the carbon decomposition rate for the current day.

    _calculate_anaerobic_coefficient() -> float:
        Calculates the anaerobic coefficient for the composting process.

    _calculate_carbon_decomposition(total_solid: float) -> float:
        Computes the total carbon decomposition for the current day.

    _calculate_dry_matter_loss(methane_emission: float, carbon_decomposition: float) -> float:
        Calculates the total dry matter loss for the current day.

    _calculate_nitrogen_loss_to_leaching() -> float:
        Computes the nitrogen loss due to leaching for the current year.

    _calculate_nitrogen_loss_to_direct_nitrous_Oxide_Emission() -> float:
        Calculates the nitrogen loss through direct nitrous oxide emission for the current year.

    _calculate_total_nitrogen_mass() -> float:
        Computes the total mass of nitrogen in the manure-bedding mix for the current year.

    _calculate_organic_nitrogen_mass() -> float:
        Calculates the mass of organic nitrogen in the manure-bedding mix for the current year.

    _calculate_inorganic_nitrogen_mass() -> float:
        Calculates the mass of inorganic nitrogen in the manure-bedding mix for the current year.

    _calculate_ammonium_mass() -> float:
        Computes the mass of ammonium in the manure-bedding mix for the current year.
    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """
        Initializes a new instance of the Composting class, setting up the necessary parameters for
        composting manure treatment based on provided configurations.

        Parameters
        ----------
        weather : Weather
            The current weather conditions.
        time : Time
            The current time information.
        manure_treatment_config : ManureTreatmentConfig
            Configuration settings for manure treatment.
        """
        super().__init__(weather, time, manure_treatment_config)
        self.composting_type: CompostingType = CompostingType.get_type(self.config.composting_type)

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        daily_input = self._current_manure_treatment_daily_input

        manure_volatile_solids = daily_input.liquid_manure_total_volatile_solids
        manure_total_solids = daily_input.liquid_manure_total_solids

        methane_emission = self.calc_methane_emission(volatile_solid=manure_volatile_solids)
        carbon_decomposition = self._calculate_carbon_decomposition(total_solid=manure_total_solids)

        daily_dry_matter_loss = self._calculate_dry_matter_loss(methane_emission=methane_emission,
                                                                carbon_decomposition=carbon_decomposition)

        remaining_manure_total_solids = manure_total_solids - daily_dry_matter_loss
        remaining_manure_volatile_solids = manure_volatile_solids - methane_emission
        remaining_manure_mass = remaining_manure_total_solids / 0.12
        Nitrogen_loss_to_ammonia_emission = self.calc_ammonia_emission()
        Nitrogen_loss_to_leaching = self._calculate_nitrogen_loss_to_leaching()
        Nitrogen_loss_to_direct_N2O_emission = self._calculate_nitrogen_loss_to_direct_nitrous_Oxide_Emission()
        total_Nitrogen_mass = self._calculate_total_nitrogen_mass(Nitrogen_loss_to_ammonia_emission,
                                                                  Nitrogen_loss_to_leaching,
                                                                  Nitrogen_loss_to_direct_N2O_emission)
        organic_Nitrogen_mass = self._calculate_organic_nitrogen_mass(total_Nitrogen_mass)
        inorganic_Nitrogen_mass = self._calculate_inorganic_nitrogen_mass(total_Nitrogen_mass)
        ammoniacal_nitrogen_mass = self._calculate_ammoniacal_nitrogen_mass(inorganic_Nitrogen_mass)

        daily_output = ManureTreatmentDailyOutput(
            simulation_day=daily_input.simulation_day,
            pen_id=daily_input.pen_id,
            storage_methane=methane_emission,
            storage_ammonia=Nitrogen_loss_to_ammonia_emission,
            storage_nitrogen_leached=Nitrogen_loss_to_leaching,
            storage_nitrous_oxide=Nitrogen_loss_to_direct_N2O_emission,
            solid_manure_carbon_decomposition=carbon_decomposition,
            solid_manure_total_solids=remaining_manure_total_solids,
            solid_manure_total_volatile_solids=remaining_manure_volatile_solids,
            solid_manure_daily_mass=remaining_manure_mass,
            solid_manure_phosphorus=daily_input.liquid_manure_phosphorus,
            solid_manure_potassium=daily_input.liquid_manure_potassium,
            solid_manure_nitrogen=total_Nitrogen_mass,
            solid_manure_inorganic_nitrogen=inorganic_Nitrogen_mass,
            solid_manure_organic_nitrogen=organic_Nitrogen_mass,
            solid_manure_total_ammoniacal_nitrogen=ammoniacal_nitrogen_mass
        )

        self._accumulate_daily_output(daily_output)
        return daily_output

    def calc_methane_emission(self, *args, **kwargs) -> float:
        """
        This function calculates the solid manure methane emission of the current day.

        Returns
        -------
        float
            The solid manure methane emission of the current day, kg/day.
        """
        manure_volatile_solids = self._current_manure_treatment_daily_input.liquid_manure_total_volatile_solids
        maximum_methane_producing_capacity = GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION
        methane_conversion_factor = self._calculate_methane_conversion_factor()
        return (manure_volatile_solids) * (maximum_methane_producing_capacity * 0.67 * methane_conversion_factor)

    def calc_ammonia_emission(self, *args, **kwargs) -> float:
        """
        This function calculates the total Nitrogen loss to ammonia emission of the current year.

        Returns
        -------
        float
            The total Nitrogen loss to methane emission of the current year, kg.
        """
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        fraction_Nitrogen_lost_as_ammonia = GasEmissionConstants.FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION[
            self.composting_type]

        return fraction_Nitrogen_lost_as_ammonia * N_prior_t

    def _calculate_methane_conversion_factor(self) -> float:
        """
        This function returns the methane conversion factor depending on the composting type and the temperature.

        Returns
        -------
        float
            The methane conversion factor, unitless.
        """
        if self.composting_type == CompostingType.STATIC_PILE:
            return GasEmissionConstants.MCF_COMPOSTING_STATIC_PILE
        else:
            current_day_mean_air_temperature = self._get_current_day_average_temperature_celsius()
            if current_day_mean_air_temperature < GasEmissionConstants.MCF_LOWER_BOUND_TEMPERATURE:
                return GasEmissionConstants.MCF_COMPOSTING_WINDROW_LOW
            elif 15 <= current_day_mean_air_temperature <= GasEmissionConstants.MCF_UPPER_BOUND_TEMPERATURE:
                return GasEmissionConstants.MCF_COMPOSTING_WINDROW_MEDIUM
            else:
                return GasEmissionConstants.MCF_COMPOSTING_WINDROW_HIGH

    @staticmethod
    def _calculate_max_microbial_decomposition_rate() -> float:
        """
        This function calculates the max microbial decomposition rate of the current day.

        Returns
        -------
        float
            The max microbial decomposition rate of the current day, per day.
        """
        effectiveness_of_microbial_decomposition_rate = GasEmissionConstants. \
            DEFAULT_EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        decomposition_temperature = GasEmissionConstants.DEFAULT_COMPOSTING_DECOMPOSITION_TEMPERATURE

        return effectiveness_of_microbial_decomposition_rate * (1.066 ** (decomposition_temperature - 10) - 1.21 **
                                                                (decomposition_temperature - 50))

    def _calculate_slow_microbial_decomposition_rate(self) -> float:
        """
        This function calculates the slow microbial decomposition rate of the current day.

        Returns
        -------
        float
            The slow microbial decomposition rate of the current day, per day.
        """
        effectiveness_of_microbial_decomposition_rate = GasEmissionConstants. \
            DEFAULT_EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        compost_pile_pack_temperature = self._get_current_day_average_temperature_celsius()

        return effectiveness_of_microbial_decomposition_rate * (1.066 ** (compost_pile_pack_temperature - 10) - 1.21 **
                                                                (compost_pile_pack_temperature - 50))

    def _calculate_carbon_decomposition_rate(self) -> float:
        """
        This function calculates the Carbon decomposition rate of the current day.

        Returns
        -------
        float
            The Carbon decomposition rate of the current day, per day.
        """
        max_microbial_decomposition_rate = self._calculate_max_microbial_decomposition_rate()
        slow_microbial_decomposition_rate = self._calculate_slow_microbial_decomposition_rate()

        decay = GasEmissionConstants.DEFAULT_FIRST_ORDER_DECAYING_COEFFICIENT
        last_turning_or_addition = self.config.last_compost_turning_or_addition
        lag = ManureConstants.DEFAULT_LAG_TIME

        return (max_microbial_decomposition_rate - slow_microbial_decomposition_rate) * \
               (math.e ** (decay * (last_turning_or_addition - lag))) * slow_microbial_decomposition_rate

    @staticmethod
    def _calculate_anaerobic_coefficient() -> float:
        """
        This function calculates the Anaerobic coefficient.

        Returns
        -------
        float
            The Anaerobic coefficient, unitless.
        """
        mole_fraction_of_oxygen = GasEmissionConstants.DEFAULT_MOLE_FRACTION_OF_OXYGEN
        oxygen_half_saturation = GasEmissionConstants.OXYGEN_HALF_SATURATION_CONSTANT
        ambient_air_mole_fraction_of_oxygen = GasEmissionConstants.DEFAULT_AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN

        return (mole_fraction_of_oxygen / (oxygen_half_saturation + mole_fraction_of_oxygen)) * \
               ((oxygen_half_saturation + ambient_air_mole_fraction_of_oxygen) / ambient_air_mole_fraction_of_oxygen)

    def _calculate_carbon_decomposition(self, total_solid: float) -> float:
        """
        This function calculates the total carbon decomposition of the current day.

        Returns
        -------
        float
            The total carbon decomposition of the current day, kg/day.
        """
        c_manure = ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE
        c_bedding = ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING
        effect_moist = GasEmissionConstants.DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION

        q_bedding = self._manure_handler_daily_output.total_bedding_mass

        carbon_decomposition_rate = self._calculate_carbon_decomposition_rate()
        anaerobic_coefficient = self._calculate_anaerobic_coefficient()

        return (total_solid * c_manure +
                q_bedding * c_bedding) * carbon_decomposition_rate * effect_moist * anaerobic_coefficient

    @staticmethod
    def _calculate_dry_matter_loss(methane_emission: float, carbon_decomposition: float) -> float:
        """
        This function calculates the total dry matter loss of the current day.

        Returns
        -------
        float
            The total carbon decomposition of the current day, kg/day.
        """
        return 2 * carbon_decomposition + methane_emission

    def _calculate_nitrogen_loss_to_leaching(self) -> float:
        """
        This function calculates the amount of Nitrogen leached out of the manure-bedding pile of the current year.

        Returns
        -------
        float
            The total Nitrogen loss to Leaching of the current year, kg.
        """
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        fraction_Nitrogen_lost_as_ammonia = GasEmissionConstants.FRACTION_NITROGEN_LOST_TO_LEACHING[
            self.composting_type]

        return fraction_Nitrogen_lost_as_ammonia * N_prior_t

    def _calculate_nitrogen_loss_to_direct_nitrous_Oxide_Emission(self) -> float:
        """
        This function calculates the amount of Nitrogen loss through direct Nitrous Oxide Emission of the current year.

        Returns
        -------
        float
            The total Nitrogen loss through direct Nitrous Oxide Emission of the current year, kg.
        """
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen
        fraction_Nitrogen_lost_as_ammonia = GasEmissionConstants.FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION[
            self.composting_type]

        return fraction_Nitrogen_lost_as_ammonia * N_prior_t * 44 / 28

    def _calculate_total_nitrogen_mass(self, Nitrogen_loss_to_ammonia_emission,
                                       Nitrogen_loss_to_leaching, Nitrogen_loss_to_direct_N2O_emission) -> float:
        """
        This function calculates the total mass of Nitrogen in the manure-bedding mix of the current day.

        Returns
        -------
        float
            The total mass of Nitrogen in the manure-bedding mix of the current day, kg.
        """
        N_prior_t = self._current_manure_treatment_daily_input.liquid_manure_nitrogen

        return \
            N_prior_t - Nitrogen_loss_to_ammonia_emission - Nitrogen_loss_to_leaching - \
            Nitrogen_loss_to_direct_N2O_emission

    @staticmethod
    def _calculate_organic_nitrogen_mass(total_Nitrogen_mass) -> float:
        """
        This function calculates the mass of organic Nitrogen in the manure-bedding mix of the current day.

        Returns
        -------
        float
            The mass of organic Nitrogen in the manure-bedding mix of the current day, kg.
        """

        return total_Nitrogen_mass * 0.952

    @staticmethod
    def _calculate_inorganic_nitrogen_mass(total_Nitrogen_mass) -> float:
        """
        This function calculates the mass of inorganic Nitrogen in the manure-bedding mix of the current day.

        Returns
        -------
        float
            The mass of inorganic Nitrogen in the manure-bedding mix of the current day, kg.
        """

        return total_Nitrogen_mass * 0.048

    @staticmethod
    def _calculate_ammoniacal_nitrogen_mass(inorganic_Nitrogen_mass) -> float:
        """
        This function calculates the mass of ammonium in the manure-bedding mix of the current day.

        Returns
        -------
        float
            The mass of ammonium in the manure-bedding mix of the current day, kg.
        """

        return inorganic_Nitrogen_mass * 0.5
