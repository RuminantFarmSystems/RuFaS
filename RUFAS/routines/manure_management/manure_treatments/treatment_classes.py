from __future__ import annotations

from dataclasses import dataclass
from enum import auto
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from RUFAS.routines.manure_management.helpers.enum_helpers import DefaultEnum
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure_management.manure_treatments.treatment_output import TreatmentOutput,AggregatedManureOutputforField
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.time import Time
from RUFAS.weather import Weather


class TreatmentType(DefaultEnum):
    """
    Enumerates available treatment options.
    """

    ANAEROBIC_LAGOON = auto()
    ANAEROBIC_DIGESTION = auto()
    ANAEROBIC_DIGESTION_AND_LAGOON = auto()

    SLURRY_STORAGE_UNDERFLOOR = auto()
    SLURRY_STORAGE_OUTDOOR = auto()
    DEFAULT = SLURRY_STORAGE_UNDERFLOOR


class BaseManureTreatment:
    def __init__(self,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        """
        An instance of this class represents a storage receptacle.
        It is primarily used by the emissions sub-module

        """

        self.config = manure_treatment_config
        self.manure_separator = manure_separator
        self.reception_pit = self.manure_separator.reception_pit
        self.manure_handler = self.reception_pit.manure_handler
        self.weather_data = weather
        self.time = time
        self.all_output: List[TreatmentOutput] = []
        self.accumulated_output = TreatmentOutput()
        self.simulation_day = 0

    def reset_daily_variables(self):
        pass

    @property
    def last_output(self) -> Optional[TreatmentOutput]:
        """

        Returns:

        """
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def update(self, simulation_day: int) -> TreatmentOutput:
        daily_output = TreatmentOutput()
        self.all_output.append(daily_output)
        # self.accumulated_output.__add__(daily_output)
        self.accumulated_output += daily_output  # TODO: Check if this is intended
        self.simulation_day = simulation_day
        return daily_output

    def land_application_day_check_available_manure(self):
        """
        Description: Allows Field Module to check nutrient content of manure storage without modifying.
        Returns: AggregatedManureOutputforField object containing accumulated attributes
        """
        ## Convert aggregated outputs from TreatmentOutput type, to object type expected in Field
        output_to_field = AggregatedManureOutputforField()
        output_to_field.convert_treatment_ouput_to_field_outputs(self.accumulated_output)
        return output_to_field

    def land_application_day_update_manure_storage(self,requested_manure_fraction=1):
        """
        Returns: AggregatedOutput object for field application before resetting self.accumulated_output to new levels
        outputs_for_land_application = self.accumulated_output
        """
        ## Convert aggregated outputs from TreatmentOutput type, to object type expected in Field
        output_to_field = AggregatedManureOutputforField()
        output_to_field.convert_treatment_ouput_to_field_outputs(self.accumulated_output)
        # TODO Currently resets accumulated outputs to zero, 
        # but should reset to new levels based on requested_manure_mass. Should be based on
        #  percentage requested
        # Input requested_manure_fraction for calculating remainder in tank
        self.accumulated_output = TreatmentOutput()
        return output_to_field


class AnaerobicDigestion(BaseManureTreatment):
    """
    Description
    ------------
    This class represents a manure treatment method that that takes in a flow of water/waste mixture and produces 
    biogas, effluent, with unique output attributes to other treatment methods


    Constructor Objects 
    -------------------
    pen: SimplePen  ---> Associated Pen
    manure_handler: BaseManureHandler ---> Associated manure handler before ReceptionPit
    manure_separator: BaseSeparator,  ---> Associated Separator
    treatment_init_data: TreatmentInitData ---> AnaerobicDigesterInitData object
    

    Attributes
    -----------
    Same as BaseTreatment: pen, manure_handler,manure_separator,treatment_enum, treatment_init_data, all_output

    Methods
    -----------
    Same as BaseTreatment: update,
    update_helper. --> helper function for update, returns TreatmentOutput object and calculates non-output values 
    to track

    """

    def __init__(self,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(manure_separator, weather, time, manure_treatment_config)
        # self.weather_data = SimpleWeather()

        self.total_solids = 0.0
        self.volatile_solids = 0.0
        self.wastewater_volume = 0.0
        self.minimum_Lagoon_volume = 0
        self.top_cover_volume = 0
        self.biogas_generation = 0
        self.effluent_total_solids = 0
        self.effluent_volatile_solids = 0
        self.methane_generation_volume = 0
        self.energy_content = 0
        self.input_energy_heating = 0
        self.sludge_accumulation_volume = 0
        self.evaporated_water = 0
        self.effluent_waste_volume = 0
        self.N_content = 0
        self.P_content = 0
        self.K_content = 0
        self.sludge_accumulation_volume = 0
        self.minimum_digester_volume = 0.0
        self.volume_of_anaerobic_lagoon = 0.0

    def update(self, simulation_day: int) -> TreatmentOutput:
        daily_output = self.update_helper()
        self.all_output.append(daily_output)
        self.simulation_day = simulation_day

        return daily_output

    def update_helper(self) -> TreatmentOutput:

        """ Returns the daily_ouput of AnaerobicDigestion output
            :params self
                Uses data from AnaerobicDigestorInitData class
                Uses outputs from ReceptionPitOutputs       
        """

        handler_output = self.manure_handler.last_output
        self.total_solids = handler_output.TSd  # kg/day
        self.volatile_solids = handler_output.VSd + handler_output.VSnd  # kg/day
        self.wastewater_volume = handler_output.total_daily_mass

        moisture_content = self.get_moisture_content()

        T_avg = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]  # TODO: Fix this

        self.input_energy_heating = self.calc_specific_input_energy(T_avg,
                                                                    moisture_content) * self.wastewater_volume * \
                                    Constants.LITERS_TO_CUBIC_METERS

        # m^3/year  MS.3.B.1
        self.sludge_accumulation_volume = self.get_sav()

        # Minimum Lagoon volume required for processing inflow  (m^3)
        # MS.3.B.2
        self.minimum_digester_volume = self.get_minimum_digester_volume()

        # MS.3.B.3
        self.top_cover_volume = self.get_top_cover_volume(self.minimum_Lagoon_volume)

        # MS.3.B.4
        self.volume_of_anaerobic_lagoon = self.minimum_digester_volume + self.top_cover_volume + \
                                          self.sludge_accumulation_volume

        # kg biogas generated in Lagoon
        # MS.3.B.6
        self.biogas_generation = self.get_biogas_generation()

        # MS.3.B.7
        self.methane_generation_volume = self.get_methane_generation_volume(self.biogas_generation)
        # content of biogas (m3)

        # Energy content of biogas
        self.energy_content = self.get_energy_content(self.methane_generation_volume)

        # ------------------------Lagoon EFFLUENT Characteristics-------------------------------------
        # MS.3.B.8
        self.effluent_waste_volume = self.wastewater_volume
        self.evaporated_water = self.get_evaporated_water()  # m^3/day

        # MS.3.B.9
        self.effluent_total_solids = self.get_effluent_total_solids()

        # MS.3.B.10
        self.effluent_volatile_solids = self.get_effluent_volatile_solids()
        # Nutrient content of outputs
        self.N_content = self.get_nutrient_content(self.config.N_removal_efficiency,
                                                   handler_output.manure_nitrogen)
        self.P_content = self.get_nutrient_content(self.config.P_removal_efficiency,
                                                   handler_output.p_excrt_manure)
        self.K_content = self.get_nutrient_content(self.config.K_removal_efficiency,
                                                   handler_output.K_manure)

        daily_output = TreatmentOutput(
                manure_nitrogen=self.N_content,
                # urea=prev_output.urea,  # TODO: unexpected attributes
                TAN_s=handler_output.TAN_s * (1 - self.config.TAN_removal_efficiency),
                TSd=self.effluent_total_solids,
                VSd=self.effluent_volatile_solids - handler_output.VSnd,
                VSnd=handler_output.VSnd,
                VS_total=self.effluent_volatile_solids,
                p_excrt_manure=self.P_content,
                K_manure=self.K_content,
                total_daily_mass=self.effluent_waste_volume,
                final_volume=self.effluent_waste_volume,
        )
        return daily_output

    def get_moisture_content(self):
        """Returns moisture_content of influent as decimal (0-1)
        """
        if self.wastewater_volume > 0.0:
            return 1 - self.total_solids / self.wastewater_volume
        else:
            return 0

    def get_nutrient_content(self, nutrient_fraction, manure_nutrient_content):
        """Returns nutrient content of effluent
        :param nutrient_fraction: the predefined fraction from init_data.
        :param manure_nutrient_content: manure_nutrient_content from reception_pit_output_data 
        """
        if self.total_solids > 0:
            return (1 - nutrient_fraction) * (
                    manure_nutrient_content / self.total_solids)
        else:
            return 0.0

    def get_biogas_generation(self):
        """Returns biogas generation volume
        """
        return self.config.biogas_gen_ratio * self.volatile_solids

    def get_minimum_digester_volume(self) -> float:
        """Returns minimum Lagoon volume required based on HRT
        """
        return self.wastewater_volume * self.config.hydraulic_retention_time

    def get_top_cover_volume(self, minimum_digester_volume):
        """Returns top cover volume
        :param minimum_Lagoon_volume: minimum Lagoon volume in m3
        """
        return self.config.top_cover_volume_fraction * minimum_digester_volume

    def get_sav(self):
        """Returns sludge_accumulation_volume
        """
        return self.config.SAV_fraction * self.volatile_solids * \
               self.config.sludge_accumulation_period * \
               Constants.DAYS_PER_YEAR / Constants.DENSITY_WATER_KG_PER_M3

    def get_effluent_total_solids(self):
        """Returns effluent_total_solids
        """
        if self.wastewater_volume > 0:
            return (1 - self.config.TS_removal_efficiency) * self.total_solids
        else:
            return 0.0

    def get_effluent_volatile_solids(self):
        """Returns effluent_volatile_solids
        """
        if self.wastewater_volume > 0:
            return (1 - self.config.VS_removal_efficiency) * self.volatile_solids
        else:
            return 0.0

    def get_evaporated_water(self):
        """Returns evaporated water volume
        """
        return self.config.evaporation_fraction * self.wastewater_volume  # m^3/day

    def get_methane_generation_volume(self, biogas_generation):
        """Returns methane_generation_volume
        :param biogas_generation: 
        """
        return biogas_generation * self.config.methane_gen_ratio  # MethaneY_DENSITY  ###

    def get_methane_volume_using_chen_equation(self):
        """Returns methane_generation_volume as calculated by Chen and Hashimoto Model 
        """
        Go = 240  # Methane potential (mL/g VS)
        KCH = 3.1  # Chen and Hashimoto kinetic constant
        sgr = 0.637  # Specific Growth Rate (micrometers)
        return Go * (1 - KCH / (
                self.config.hydraulic_retention_time * sgr + KCH - 1)) * \
               self.effluent_volatile_solids * Constants.GRAMS_TO_KG  #

    def get_energy_content(self, methane_generation_volume):
        """Returns energy content of methane
        :param methane_generation_volume: 
        """
        return methane_generation_volume * Constants.METHANE_DENSITY * Constants.METHANE_ENERGY_DENSITY  ###

    def calc_specific_input_energy(self, T_avg, moisture_content):
        """ Returns the energy required to maintain AD temperature at setpoint
            :params:   T_avg: Average daily temperature (C)
                       moisture_content: 0-1 decimal representing water content of manure
        """
        effluent_temperature = self.bound_influent_temperature(T_avg)
        heat_capacity_influent = self.calc_heat_capacity_manure(T_avg, moisture_content)
        heat_capacity_AD = self.calc_heat_capacity_manure(self.config.AD_temp_set_point, moisture_content)
        avg_heat_capacity = (heat_capacity_influent + heat_capacity_AD) / 2
        input_energy_heating = avg_heat_capacity * (self.config.AD_temp_set_point - effluent_temperature)
        return input_energy_heating

    def bound_influent_temperature(self, T_avg):
        """ Returns the max between T_avg and temperature bound
        :param T_avg: average daily temperature
        """
        the_max = max(T_avg, 4)
        return the_max

    def calc_heat_capacity_manure(self, T_avg, moisture_content):
        """ Returns heat capacity of manure.  (kJ /kg /C)
            :param T_avg: Average daily temp (C) 
            :param moisture_content: decimal form (0-1)
        """
        return 0.68298 + 0.025662 * T_avg + 0.01306 * moisture_content * 100


class AnaerobicLagoon(BaseManureTreatment):
    def __init__(self,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(manure_separator, weather, time, manure_treatment_config)
        self.storage_time_period = manure_treatment_config.storage_time_period  # m^3 (25-year 24h storm event)
        self.freeboard_input = manure_treatment_config.freeboard_input  # m
        self.precip_input = manure_treatment_config.freeboard_input  # m (25-year 24h storm event)

    def update(self, simulation_day: int) -> TreatmentOutput:
        daily_output = self.update_helper()
        self.all_output.append(daily_output)
        self.accumulated_output.__add__(daily_output)
        self.simulation_day = simulation_day
        return daily_output

    def update_helper(self):
        handler_output = self.manure_handler.last_output
        # prev_output = self.manure_handler.last_output
        daily_output = TreatmentOutput(
                TAN_s=handler_output.TAN_s * (1 - self.config.TAN_removal_efficiency),
                # urea=prev_output.urea,  # TODO: unexpected attribute
                manure_nitrogen=handler_output.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler_output.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler_output.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler_output.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler_output.K_manure * (1 - self.config.K_removal_efficiency),
                total_daily_mass=handler_output.total_daily_mass
        )

        # Sludge Nutrient Values -- Initial calcs
        sludge_TSd = handler_output.TSd * self.config.TS_removal_efficiency
        sludge_VS = handler_output.VS_total * self.config.VS_removal_efficiency
        sludge_nitrogen = handler_output.manure_nitrogen * self.config.N_removal_efficiency
        sludge_phosphorous = handler_output.p_excrt_manure * self.config.P_removal_efficiency
        sludge_potassium = handler_output.K_manure * self.config.K_removal_efficiency

        # TODO: The following values are not being used.
        # Bounded Sludge Nutrient Values
        sludge_TSd = self.boundSludgeValue(sludge_TSd, 40, 70)
        sludge_VS = self.boundSludgeValue(sludge_VS, 1.99, 2.99)
        sludge_nitrogen = self.boundSludgeValue(sludge_nitrogen, 1.99, 2.99)
        sludge_phosphorous = self.boundSludgeValue(sludge_phosphorous, 1.07, 5.02)
        sludge_potassium = self.boundSludgeValue(sludge_potassium, 1.1, 1.75)

        return daily_output

    @property
    def sludge_accumulation_volume(self):
        """Returns sludge accumulation volume in m^3
        """
        if self.manure_handler.last_output:
            return self.config.SAV_fraction * self.manure_handler.last_output.TSd * \
                   self.config.sludge_accumulation_period * Constants.DAYS_PER_YEAR
        else:
            return 0

    @property
    def flushing_recycled(self):
        """returns flushing water recycled in m^3"""
        if self.simulation_day > 0:
            return self.manure_handler.last_output.cleaning_water * Constants.LITERS_TO_CUBIC_METERS
        else:
            return 0

    @property
    def wastewater_volume(self):
        """returns wastewater volume in m^3"""
        return self.manure_handler.last_output.total_daily_mass * Constants.LITERS_TO_CUBIC_METERS

    @property
    def reduced_volume(self):
        """returns reduced volume in m^3"""
        return self.wastewater_volume - self.flushing_recycled  # m^3

    @property
    def minimum_treatment_volume(self) -> float:
        """returns minimum treatment volume in m^3"""

        return (
                self.manure_handler.last_output.total_daily_mass * Constants.LITERS_TO_CUBIC_METERS +
                self.storage_time_period * (
                    self.reduced_volume))  # m^3

    @property
    def total_lagoon_volume(self) -> float:
        """returns Total Lagoon Volume in m^3"""
        return self.volume_needed + self.freeboard + self.precip

    @property
    def volume_needed(self):
        """returns volume needed for lagoon sizing in m^3"""
        return self.minimum_treatment_volume + self.sludge_accumulation_volume

    @property
    def lagoon_depth(self):
        """returns lagoon depth in meters"""
        return 3.657  # meters

    @property
    def lagoon_slope(self):
        """returns lagoon slope (unitless)"""
        return 2.0

    def calc_abc(self):
        """returns coefficients for volume calculations as tuple (a,b,c)"""
        a = 3 * self.lagoon_depth
        b = -4 * self.lagoon_slope * self.lagoon_depth ** 2
        c = 4 * (self.lagoon_slope ** 2) * (self.lagoon_depth ** 3) / 3 - self.volume_needed
        return a, b, c

    @property
    def lagoon_width(self):
        """returns lagoon width in meters"""
        abc = self.calc_abc()
        a, b, c = abc[0], abc[1], abc[2]
        return (-1 * b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

    @property
    def lagoon_length(self):
        """returns lagoon width in meters"""
        return self.lagoon_width * 3

    @property
    def lagoon_surface_area(self):
        """returns lagoon surface area in m^2"""
        return self.lagoon_width * self.lagoon_length

    @property
    def lagoon_volume(self):
        """returns lagoon volume in m^3, should match volume needed"""
        return self.lagoon_length * self.lagoon_width * self.lagoon_depth \
               - (self.lagoon_slope * self.lagoon_depth ** 2) * (self.lagoon_length + self.lagoon_width) \
               + 4 * self.lagoon_slope * self.lagoon_depth ** 3 / 3

    @property
    def precip(self):
        """returns additional lagoon volume needed for precipitation in m^3"""
        current_day_rainfall = self.weather_data.rainfall[self.time.year - 1][self.time.day - 1]

        return current_day_rainfall * self.lagoon_surface_area  # m3 of rain

    @property
    def freeboard(self):
        """returns additional lagoon volume needed for freeboard in m^3"""
        return self.freeboard_input * self.lagoon_surface_area  # m3 of rain

    def calc_emissions(self):
        pass

    def boundSludgeValue(self, calculated_value, lower_bound, upper_bound):
        """returns value bounded by lower and upper bounds"""
        return min(max(self.sludge_accumulation_volume * lower_bound, calculated_value),
                   self.sludge_accumulation_volume * upper_bound)


class AnaerobicDigestionAndLagoon(AnaerobicLagoon):
    pass


class SlurryStorageUnderfloor(BaseManureTreatment):
    def __init__(self,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(manure_separator, weather, time, manure_treatment_config)

        self.storage_time_period = manure_treatment_config.storage_time_period  # days

    @property
    def treatment_volume(self) -> float:
        return self.storage_time_period * self.manure_handler.last_output.total_daily_mass  # m^3

    @property
    def total_volume(self) -> float:
        return self.treatment_volume  # m^3

    def update(self, simulation_day: int) -> TreatmentOutput:
        handler = self.manure_handler.last_output
        daily_output = TreatmentOutput(
                TAN_s=handler.TAN_s * (1 - self.config.TAN_removal_efficiency),
                # urea=handler.U,
                manure_nitrogen=handler.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler.K_manure * (1 - self.config.K_removal_efficiency),
        )

        daily_output.final_volume = self.total_volume - (
                (daily_output.TSd + daily_output.VS_total) * self.storage_time_period * Constants.KG_TO_CUBIC_METERS)

        self.all_output.append(daily_output)
        self.accumulated_output.__add__(daily_output)
        self.simulation_day = simulation_day
        return daily_output
    def calc_gas(self):
        pass



class SlurryStorageOutdoor(BaseManureTreatment):
    def __init__(self,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(manure_separator, weather, time, manure_treatment_config)
        self.storage_time_period = manure_treatment_config.storage_time_period  # m^3 (25-year 24h storm event)
        self.freeboard_input = manure_treatment_config.freeboard_input  # m
        self.precip_input = manure_treatment_config.precip_input  # m (25-year 24h storm event)

    def update(self, simulation_day: int) -> TreatmentOutput:
        daily_output = self.update_helper()
        self.all_output.append(daily_output)
        # self.accumulated_output.__add__(daily_output)
        self.accumulated_output += daily_output  # TODO: Check if this is intended
        self.simulation_day += 1
        return daily_output

    def update_helper(self):
        handler = self.manure_handler.last_output
        daily_output = TreatmentOutput(
                TAN_s=handler.TAN_s * (1 - self.config.TAN_removal_efficiency),
                # urea=handler.urea,  # TODO: check if this is correct
                manure_nitrogen=handler.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler.K_manure * (1 - self.config.K_removal_efficiency),
                total_daily_mass=handler.total_daily_mass
        )
        return daily_output

    @property
    def wastewater_volume(self):
        """returns wastewater volume in m^3"""
        return self.manure_handler.last_output.total_daily_mass * Constants.LITERS_TO_CUBIC_METERS

    @property
    def treatment_volume(self) -> float:
        """returns minimum treatment volume in m^3"""
        return (
                self.manure_handler.last_output.total_daily_mass * Constants.LITERS_TO_CUBIC_METERS *
                self.storage_time_period)  # m^3

    @property
    def total_pit_volume(self) -> float:
        """returns Total Lagoon Volume in m^3"""
        return self.treatment_volume + self.freeboard + self.precip

    @property
    def pit_depth(self):
        """returns lagoon depth in meters"""
        return 3.657  # meters

    @property
    def pit_slope(self):
        """returns lagoon slope (unitless)"""
        return 2.0

    def calc_abc(self):
        """returns coefficients for volume calculations as tuple (a,b,c)"""
        a = 3 * self.pit_depth
        b = -4 * self.pit_slope * self.pit_depth ** 2
        c = 4 * (self.pit_slope ** 2) * (self.pit_depth ** 3) / 3 - self.total_pit_volume
        # TODO: Check if it is self.total_pit_volume or self.treatment_volume
        return a, b, c

    @property
    def pit_width(self):
        """returns lagoon width in meters"""
        abc = self.calc_abc()
        a, b, c = abc[0], abc[1], abc[2]
        return (-1 * b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

    @property
    def pit_length(self):
        """returns lagoon width in meters"""
        # return self.lagoon_width * 3
        return self.pit_width * 3  # TODO: Check if this is intended

    @property
    def pit_surface_area(self):
        """returns lagoon surface area in m^2"""
        # return self.lagoon_width * self.lagoon_length
        return self.pit_width * self.pit_length  # TODO: Check if this is intended

    @property
    def pit_volume(self):
        """returns lagoon volume in m^3, should match volume needed"""
        return self.pit_length * self.pit_width * self.pit_depth \
               - (self.pit_slope * self.pit_depth ** 2) * (self.pit_length + self.pit_width) \
               + 4 * self.pit_slope * self.pit_depth ** 3 / 3

    @property
    def precip(self):
        """returns additional lagoon volume needed for precipitation in m^3"""
        current_day_rainfall = self.weather_data.rainfall[self.time.year - 1][self.time.day - 1]
        return current_day_rainfall * self.pit_surface_area  # m3 of rain

    @property
    def freeboard(self):
        """returns additional lagoon volume needed for freeboard in m^3"""
        return self.freeboard_input * self.pit_surface_area  # m3 of rain

    def calc_emissions(self):
        pass


@dataclass
class ManureTreatmentConfig:
    percent_dry_solids: float = 1.0
    TS_removal_efficiency: float = 0.0
    VS_removal_efficiency: float = 0.0
    N_removal_efficiency: float = 0.0
    TAN_removal_efficiency: float = 0.0
    P_removal_efficiency: float = 0.0
    K_removal_efficiency: float = 0.0
    TS_DM_effluent_rate: float = 0.0

    hydraulic_retention_time: int = 0
    sludge_accumulation_period: float = 0.0
    SAV_fraction: float = 0.0  # Sludge Accumulation Volume fraction
    top_cover_volume_fraction: float = 0.0
    biogas_gen_ratio: float = 0.0
    methane_gen_ratio: float = 0.0

    evaporation_fraction: float = 0.0
    AD_temp_set_point: float = 0.0
    AD_temp: float = 0.0

    storage_time_period: float = 0.0,
    precip_input: float = 0.0,
    freeboard_input: float = 0.0


class DefaultManureTreatmentConfigFactory:
    SLURRY_STORAGE_UNDERFLOOR_CONFIG = ManureTreatmentConfig(
            percent_dry_solids=1.0,
            TS_removal_efficiency=0.1,  # Between 10-30%
            VS_removal_efficiency=0.85,  # Between 80-90%
            N_removal_efficiency=0.1,  # # Between 10-30%
            TAN_removal_efficiency=0.45,  # Between 61-80%
            P_removal_efficiency=0.05,  # # Between 5-30%
            K_removal_efficiency=0.05,  # # Between 5-30%
            TS_DM_effluent_rate=0.0,
            storage_time_period=120.0,
    )

    SLURRY_STORAGE_OUTDOOR_CONFIG = ManureTreatmentConfig(
            percent_dry_solids=1.0,
            TS_removal_efficiency=0.1,  # Between 10-30%
            VS_removal_efficiency=0.85,  # Between 80-90%
            N_removal_efficiency=0.1,  # # Between 10-30%
            TAN_removal_efficiency=0.45,  # Between 61-80%
            P_removal_efficiency=0.05,  # # Between 5-30%
            K_removal_efficiency=0.05,  # # Between 5-30%
            TS_DM_effluent_rate=0.0,
            storage_time_period=120.0,
            precip_input=0.0,
            freeboard_input=0.3048
    )

    ANAEROBIC_DIGESTION_CONFIG = ManureTreatmentConfig(
            # Fraction of total solids loading in effluent to original concentration
            TS_removal_efficiency=0.45,
            # Fraction of volatile solids in effluent to original concentration
            VS_removal_efficiency=0.40,
            N_removal_efficiency=0.0,  # 0-5% N fraction
            P_removal_efficiency=0.0,  # 0-5% P fraction
            K_removal_efficiency=0.0,  # 0-5% K fraction
            TAN_removal_efficiency=0.1,
            TS_DM_effluent_rate=0.0,

            hydraulic_retention_time=25,  # 25 -30 days
            sludge_accumulation_period=1.0,  # Sludge accumulation period 1-5 years
            SAV_fraction=0.03,  # Sludge Accumulation volume fraction 2-4% of VS loaded
            top_cover_volume_fraction=0.2,  # Should be between 10-30%
            biogas_gen_ratio=0.38,  # 0.23 to 0.39 kg CH4/kg VS
            methane_gen_ratio=0.65,  # 0.5-0.65 according to spreadsheet

            evaporation_fraction=0.02,  # 2-5% of Wastewater Volume
            AD_temp_set_point=37.5,
            AD_temp=37.5
    )

    ANAEROBIC_LAGOON_CONFIG = ManureTreatmentConfig(
            hydraulic_retention_time=365,  # 180 - 365 days
            sludge_accumulation_period=10.0,  # Sludge accumulation period 5-20 years
            SAV_fraction=0.00251,  # Sludge Accumulation volume fraction 0.00274-0.00455 of VS loaded

            percent_dry_solids=1.0,
            TS_removal_efficiency=0.75,  # Between 70-85%
            VS_removal_efficiency=0.85,  # Between 80-90%
            N_removal_efficiency=0.65,  # Between 60-80%
            TAN_removal_efficiency=0.7,  # Between 61-80%
            P_removal_efficiency=0.6,  # Between 60-70%
            K_removal_efficiency=0.2,  # Between 20-30%
            TS_DM_effluent_rate=0.0,
            storage_time_period=365.0,
            precip_input=0.0,
            freeboard_input=0.3048
    )

    @classmethod
    def get_instance(cls, treatment_type: TreatmentType) -> ManureTreatmentConfig:
        manure_treatment_config_by_type = {
            TreatmentType.ANAEROBIC_DIGESTION: cls.ANAEROBIC_DIGESTION_CONFIG,
            TreatmentType.ANAEROBIC_LAGOON: cls.ANAEROBIC_LAGOON_CONFIG,
            TreatmentType.SLURRY_STORAGE_UNDERFLOOR: cls.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
            TreatmentType.SLURRY_STORAGE_OUTDOOR: cls.SLURRY_STORAGE_OUTDOOR_CONFIG,
        }
        return manure_treatment_config_by_type[treatment_type]


class TreatmentFactory:
    @classmethod
    def get_instance(cls,
                     manure_treatment_type_name: str,
                     manure_separator: BaseManureSeparator,
                     weather: Weather,
                     time: Time,
                     manure_treatment_config: Optional[ManureTreatmentConfig] = None) \
            -> BaseManureTreatment:

        manure_treatment_class_by_type: Dict[TreatmentType, Type[BaseManureTreatment]] = {
            TreatmentType.ANAEROBIC_DIGESTION: AnaerobicDigestion,
            TreatmentType.ANAEROBIC_LAGOON: AnaerobicLagoon,
            # TODO: Fix the init data for this mixed class
            TreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON: AnaerobicDigestionAndLagoon,
            TreatmentType.SLURRY_STORAGE_UNDERFLOOR: SlurryStorageUnderfloor,
            TreatmentType.SLURRY_STORAGE_OUTDOOR: SlurryStorageOutdoor,
        }

        manure_treatment_type = TreatmentType.get_type(manure_treatment_type_name)
        manure_treatment_class = manure_treatment_class_by_type[manure_treatment_type]

        if manure_treatment_config:
            return manure_treatment_class(manure_separator, weather, time, manure_treatment_config)
        else:
            default_manure_treatment_config = DefaultManureTreatmentConfigFactory.get_instance(manure_treatment_type)
            return manure_treatment_class(manure_separator, weather, time, default_manure_treatment_config)
