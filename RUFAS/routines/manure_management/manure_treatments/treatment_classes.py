from __future__ import annotations
from dataclasses import dataclass
from enum import auto
from tkinter import N
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from RUFAS.routines.manure_management.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure_management.helpers.enum_helpers import DefaultEnum
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure_management.manure_treatments.treatment_output import TreatmentOutput,AggregatedManureOutputforField,SludgeOutput, AnaerobicDigestionOutput
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
                 pen: SimplePen,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        """
        An instance of this class represents a storage receptacle.
        It is primarily used by the emissions sub-module

        """
        self.pen=pen
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

        self.accumulated_output += daily_output  # TODO: Check if this is intended
        self.simulation_day = simulation_day
        daily_output.accumulated_TS = self.accumulated_output.TSd
        daily_output.ch4_emissions = self.calc_emissions()
        daily_output.nh3_emissions = self.calc_NH3_emissions()
        self.all_output.append(daily_output)
        return daily_output
    @property
    def treatment_volume(self) -> float:
        """returns  treatment volume in L"""
        return self.accumulated_output.total_daily_mass # L
    def calc_emissions(self) -> float:
        return 0.0
    def calc_NH3_emissions(self) -> float:
        return 0.0

    def land_application_day_check_available_manure(self):
        """
        Description: Allows Field Module to check nutrient content of manure storage without modifying.
        Returns: AggregatedManureOutputforField object containing accumulated attributes
        """
        ## Convert aggregated outputs from TreatmentOutput type, to object type expected in Field
        output_to_field = AggregatedManureOutputforField()
        output_to_field.convert_treatment_output_to_field_outputs(self.accumulated_output)
        return output_to_field

    def land_application_day_update_manure_storage(self,requested_manure_fraction=1):
        """
        Returns: AggregatedOutput object for field application before resetting self.accumulated_output to new levels
        outputs_for_land_application = self.accumulated_output
        """
        ## Convert aggregated outputs from TreatmentOutput type, to object type expected in Field
        output_to_field = AggregatedManureOutputforField()
        output_to_field.convert_treatment_output_to_field_outputs(self.accumulated_output)
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
                 pen: SimplePen,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(pen,manure_separator, weather, time, manure_treatment_config)
        self.accumulated_sludge = SludgeOutput()
        self.all_ad_output: List[AnaerobicDigestionOutput] = []

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
        daily_output = TreatmentOutput(
                TAN_s=handler_output.TAN_s * (1 - self.config.TAN_removal_efficiency),
                manure_nitrogen=handler_output.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler_output.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler_output.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler_output.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler_output.K_manure * (1 - self.config.K_removal_efficiency),
                total_daily_mass=handler_output.total_daily_mass,
                final_volume=handler_output.total_daily_mass
        )
        sludge_output = SludgeOutput(
            TS=handler_output.TSd * self.config.TS_removal_efficiency,
            VS=handler_output.VS_total * self.config.VS_removal_efficiency,
            N_mass=handler_output.manure_nitrogen * self.config.N_removal_efficiency,
            P_mass=handler_output.p_excrt_manure * self.config.P_removal_efficiency,
            K_mass=handler_output.K_manure * self.config.K_removal_efficiency
        )
        self.accumulated_sludge+=sludge_output
       
        moisture_content = self.get_moisture_content(daily_output.total_daily_mass,handler_output.TSd)
        T_avg = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1] 
        input_energy_heating = self.calc_specific_input_energy(T_avg,
                                                                    moisture_content) * daily_output.total_daily_mass * \
                                    Constants.LITERS_TO_CUBIC_METERS
        ad_output = AnaerobicDigestionOutput(
                biogas = self.config.biogas_gen_ratio * handler_output.VS_total,   # biogas production per day (m3/day)                             
                input_energy_heating= input_energy_heating,
                evaporated_water=self.config.evaporation_fraction * handler_output.total_daily_mass,
        )

        # MS.3.B.7
        ad_output.methane_generation_volume= self.get_methane_volume_using_chen_equation(handler_output.VS_total)
        ad_output.biogas_energy_content = ad_output.methane_generation_volume * Constants.METHANE_DENSITY * Constants.METHANE_ENERGY_DENSITY  # biogas energy content (MJ/m3)
        # MS.3.B.2
        ad_output.minimum_digester_volume = daily_output.total_daily_mass * self.config.hydraulic_retention_time
        # MS.3.B.3
        ad_output.top_cover_volume = self.config.top_cover_volume_fraction * ad_output.minimum_digester_volume        
        self.all_ad_output.append(ad_output)
        return daily_output

    @property
    def sludge_volume(self):
        """returns total accumulated sludge volume in m^3"""
        return self.accumulated_sludge.VS*Constants.KG_TO_CUBIC_METERS

    def get_moisture_content(self,total_daily_mass,TSd):
        """Returns moisture_content of influent as decimal (0-1)
        """
        if total_daily_mass > 0.0:
            return 1 - TSd / total_daily_mass
        else:
            return 0

    def get_methane_volume_using_chen_equation(self,VS_total):
        """Returns methane_generation_volume as calculated by Chen and Hashimoto Model 
        """
        Go = 240  # Methane potential (mL/g VS)
        KCH = 3.1  # Chen and Hashimoto kinetic constant
        sgr = 0.637  # Specific Growth Rate (micrometers)
        return Go * (1 - KCH / (
                self.config.hydraulic_retention_time * sgr + KCH - 1)) * \
               VS_total * Constants.GRAMS_TO_KG  #

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
                 pen:SimplePen,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(pen,manure_separator, weather, time, manure_treatment_config)
        self.storage_time_period = manure_treatment_config.storage_time_period  # days
        self.freeboard_input = manure_treatment_config.freeboard_input  # m
        self.precip_input = manure_treatment_config.freeboard_input  # m (25-year 24h storm event)
        self.accumulated_sludge=SludgeOutput()

    def update(self, simulation_day: int) -> TreatmentOutput:
        daily_output = self.update_helper()
        self.all_output.append(daily_output)
        self.accumulated_output+=daily_output
        self.simulation_day = simulation_day
        return daily_output

    def update_helper(self):
        handler_output = self.manure_handler.last_output
        rain_volume_added = self.precip
        reduced_volume_from_recycled_flush = self.flushing_recycled
        daily_output = TreatmentOutput(
                TAN_s=handler_output.TAN_s * (1 - self.config.TAN_removal_efficiency),
                manure_nitrogen=handler_output.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler_output.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler_output.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler_output.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler_output.K_manure * (1 - self.config.K_removal_efficiency),
                total_daily_mass=handler_output.total_daily_mass+rain_volume_added-reduced_volume_from_recycled_flush
        )

        sludge_output = SludgeOutput(
            TS=handler_output.TSd * self.config.TS_removal_efficiency,
            VS=handler_output.VS_total * self.config.VS_removal_efficiency,
            N_mass=handler_output.manure_nitrogen * self.config.N_removal_efficiency,
            P_mass=handler_output.p_excrt_manure * self.config.P_removal_efficiency,
            K_mass=handler_output.K_manure * self.config.K_removal_efficiency
        )
        self.accumulated_sludge+=sludge_output
        daily_output.nh3_emissions = self.calc_NH3_emissions()
        return daily_output

    @property
    def sludge_accumulation_volume(self):
        """Returns sludge accumulation volume in m^3
        """
        return self.accumulated_sludge.TS/1000

    @property
    def flushing_recycled(self):
        """returns flushing water recycled in m^3"""
        if(self.simulation_day > 0 and self.manure_handler.last_output.cleaning_water is not None):
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
        """returns Total Lagoon Volume in m^3. The precipitation is already included in volume_needed"""
        return self.volume_needed + self.freeboard

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
    def modeled_lagoon_volume(self):
        """returns modeled lagoon volume in m^3. This modeled volume is used to verify 
        that equations for surface area, with slope assumptions, match the volume needed for treatment"""
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
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        ch4_loss = GasEmissions.calc_E_CH4_anaerobic_lagoon(self.accumulated_output.VS_total)
        self.accumulated_output.TSd = max(0,self.accumulated_output.TSd -ch4_loss)
        return ch4_loss
    def calc_NH3_emissions(self):
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        nh3_loss = max(0,self.pen.num_animals*GasEmissions.calc_E_NH3_storage_v2(barn_area=self.pen.barn_area_from_pen_type,TAN = self.accumulated_output.TAN_s,U=self.accumulated_output.total_daily_mass,tempC=tempC))
        self.accumulated_output.TAN_s = max(0,self.accumulated_output.TAN_s-nh3_loss)
        return nh3_loss

    def boundSludgeValue(self, calculated_value, lower_bound, upper_bound):
        """returns value bounded by lower and upper bounds"""
        return min(max(self.sludge_accumulation_volume * lower_bound, calculated_value),
                   self.sludge_accumulation_volume * upper_bound)

class AnaerobicDigestionAndLagoon(AnaerobicLagoon):
    pass
class SlurryStorageUnderfloor(BaseManureTreatment):
    def __init__(self,
                 pen:SimplePen,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(pen,manure_separator, weather, time, manure_treatment_config)

        self.storage_time_period = manure_treatment_config.storage_time_period  # days

    @property
    def total_volume(self) -> float:
        return self.accumulated_output.total_daily_mass # L

    def update(self, simulation_day: int) -> TreatmentOutput:
        handler = self.manure_handler.last_output
        
        daily_output = TreatmentOutput(
                TAN_s=handler.TAN_s * (1 - self.config.TAN_removal_efficiency),
                manure_nitrogen=handler.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler.K_manure * (1 - self.config.K_removal_efficiency),
                total_daily_mass=handler.total_daily_mass
        )
        self.accumulated_output+=daily_output   
        daily_output.ch4_emissions = self.calc_emissions()
        daily_output.nh3_emissions = self.calc_NH3_emissions()
        daily_output.accumulated_TS =self.accumulated_output.TSd
        daily_output.accumulated_volume =self.accumulated_output.total_daily_mass/1000
        daily_output.tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        daily_output.rainfall = self.weather_data.rainfall[self.time.year - 1][self.time.day - 1]
        daily_output.final_volume = self.total_volume - (
                (daily_output.TSd + daily_output.VS_total) * Constants.KG_TO_CUBIC_METERS)

        self.all_output.append(daily_output)
        self.simulation_day = simulation_day
        if(simulation_day%self.storage_time_period ==0):
            self.land_application_day_update_manure_storage(1)
        return daily_output
    def calc_emissions(self):
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        ch4_loss = GasEmissions.calc_E_CH4_slurry_storage_v3(Ts = self.accumulated_output.TSd,enclosed=True,tempC=tempC)
        self.accumulated_output.TSd = max(0,self.accumulated_output.TSd -ch4_loss)
        return ch4_loss

    def calc_NH3_emissions(self):
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        nh3_loss = max(0,self.pen.num_animals*GasEmissions.calc_E_NH3_storage_v2(barn_area=self.pen.barn_area_from_pen_type,TAN = self.accumulated_output.TAN_s,U=self.accumulated_output.total_daily_mass,tempC=tempC))
        self.accumulated_output.TAN_s = max(0,self.accumulated_output.TAN_s-nh3_loss)
        return nh3_loss

class SlurryStorageOutdoor(BaseManureTreatment):
    def __init__(self,
                 pen:SimplePen,
                 manure_separator: BaseManureSeparator,
                 weather: Weather,
                 time: Time,
                 manure_treatment_config: ManureTreatmentConfig):
        super().__init__(pen,manure_separator, weather, time, manure_treatment_config)
        self.storage_time_period = manure_treatment_config.storage_time_period  # days
        self.freeboard_input = manure_treatment_config.freeboard_input  # m
        self.precip_input = manure_treatment_config.precip_input  # m (25-year 24h storm event)

    def update(self, simulation_day: int) -> TreatmentOutput:
        daily_output = self.update_helper()
        self.all_output.append(daily_output)
        self.accumulated_output += daily_output 
        self.simulation_day =simulation_day
        if(simulation_day%self.storage_time_period ==0):
            self.land_application_day_update_manure_storage(1)
        return daily_output

    def update_helper(self):
        handler = self.manure_handler.last_output
        rain_volume_added = self.precip
        daily_output = TreatmentOutput(
                TAN_s=handler.TAN_s * (1 - self.config.TAN_removal_efficiency),
                manure_nitrogen=handler.manure_nitrogen * (1 - self.config.N_removal_efficiency),
                TSd=handler.TSd * (1 - self.config.TS_removal_efficiency),
                VS_total=handler.VS_total * (1 - self.config.VS_removal_efficiency),
                p_excrt_manure=handler.p_excrt_manure * (1 - self.config.P_removal_efficiency),
                K_manure=handler.K_manure * (1 - self.config.K_removal_efficiency),
                total_daily_mass=handler.total_daily_mass +rain_volume_added/1000
        )
        self.accumulated_output+=daily_output   
        daily_output.ch4_emissions = self.calc_emissions()
        daily_output.nh3_emissions = self.calc_NH3_emissions()
        daily_output.accumulated_TS =self.accumulated_output.TSd
        daily_output.accumulated_volume =self.accumulated_output.total_daily_mass/1000
        daily_output.tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        daily_output.rainfall = self.weather_data.rainfall[self.time.year - 1][self.time.day - 1]
        
        return daily_output

    @property
    def treatment_volume(self) -> float:
        """returns  treatment volume in L"""
        return self.accumulated_output.total_daily_mass # L

    @property
    def total_pit_volume(self) -> float:
        """returns Total Lagoon Volume in m^3. The precipitation is already included in treatment_volume"""
        return self.treatment_volume + self.freeboard

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
        c = 4 * (self.pit_slope ** 2) * (self.pit_depth ** 3) / 3 - self.treatment_volume
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
        return self.pit_width * 3  

    @property
    def pit_surface_area(self):
        """returns lagoon surface area in m^2"""
        return self.pit_width * self.pit_length 

    @property
    def modeled_pit_volume(self):
        """returns lagoon volume in m^3, This modeled volume is used to verify 
        that equations for surface area, with slope assumptions, match the volume needed for treatment"""
        return self.pit_length * self.pit_width * self.pit_depth \
               - (self.pit_slope * self.pit_depth ** 2) * (self.pit_length + self.pit_width) \
               + 4 * self.pit_slope * self.pit_depth ** 3 / 3

    @property
    def precip(self):
        """returns additional lagoon volume needed for precipitation in m^3"""
        current_day_rainfall = self.weather_data.rainfall[self.time.year - 1][self.time.day - 1]
        return current_day_rainfall * self.pit_surface_area  # m3 of rain
        #TODO Check rain input units are mm or meter. 

    @property
    def freeboard(self):
        """returns additional lagoon volume needed for freeboard in m^3"""
        return self.freeboard_input * self.pit_surface_area  # m3 of freeboard

    def calc_emissions(self):
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        TS_input = self.accumulated_output.TSd
        ch4_loss = GasEmissions.calc_E_CH4_slurry_storage_v3(Ts = TS_input, enclosed=False,tempC=tempC)
        self.accumulated_output.TSd = max(0,self.accumulated_output.TSd)
        return ch4_loss

    def calc_NH3_emissions(self):
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        nh3_loss = max(0,self.pen.num_animals*GasEmissions.calc_E_NH3_storage_v2(barn_area=self.pen.barn_area_from_pen_type,TAN = self.accumulated_output.TAN_s,U=self.accumulated_output.total_daily_mass,tempC=tempC))
        self.accumulated_output.TAN_s = max(0,self.accumulated_output.TAN_s-nh3_loss)
        return nh3_loss
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

    storage_time_period: float = 0.0
    precip_input: float = 0.0
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
                     pen: SimplePen,
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
            return manure_treatment_class(pen,manure_separator, weather, time, manure_treatment_config)
        else:
            default_manure_treatment_config = DefaultManureTreatmentConfigFactory.get_instance(manure_treatment_type)
            return manure_treatment_class(pen,manure_separator, weather, time, default_manure_treatment_config)
