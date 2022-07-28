"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseSeparator
from RUFAS.routines.manure_management.misc.simple_weather import SimpleWeather
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.treatments.treatment_output import AnaerobicDigesterOutput, TreatmentOutput


class TreatmentEnum(ExtendedEnum):
    """
    Enumerates available treatment options.
    """

    STORAGE_POND = 1
    ANAEROBIC_LAGOON = 2
    ANAEROBIC_DIGESTION = 3

    SLURRY_STORAGE = STORAGE_POND
    STORAGE_PIT = STORAGE_POND
    DEFAULT = STORAGE_POND


class BaseTreatment:
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        """
        An instance of this class represents a storage receptacle.
        It is primarily used by the emissions sub-module

        Parameters
        ----------
        pen
        treatment_init_data

        Returns
        -------
        None

        """

        self.treatment_enum = TreatmentEnum.get_enum(pen.manure_storage)
        self.treatment_init_data = treatment_init_data

        self.manure_handler = manure_handler
        self.reception_pit = manure_separator.reception_pit
        
        self.manure_separator = manure_separator

        self.all_output: List[TreatmentOutput] = []

    def reset_daily_variables(self):
        pass

    @property
    def last_output(self) -> Optional[ReceptionPitOutput]:
        """

        Returns:

        """
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def update(self) -> TreatmentOutput:
        daily_output = TreatmentOutput()
        self.all_output.append(daily_output)
        return daily_output


class AnaerobicDigestion(BaseTreatment):
    """
    Description
    ------------
    This class represents a manure treatment method that that takes in a flow of water/waste mixture and produces 
    biogas, effluent, with unique output attributes to other treatment methods


    Constructor Objects 
    -------------------
    pen: SimplePen  ---> pen associated with the manure flow? -- 
                    ---> not sure this should be an input since all flow is channeled through
                     reception pit, manure handler or separator
    manure_handler: BaseManureHandler ---> Associated manure handler before ReceptionPit
    manure_separator: BaseSeparator,  ---> Associated Separator
    treatment_init_data: TreatmentInitData ---> AnaerobicDigesterInitData object
    

    Attributes
    -----------
    Same as BaseTreatment: pen, manure_handler,manure_separator,treatment_enum, treatment_init_data, all_output
    reception_pit: a reception_pit object that can be created from the manure_handler object when being created,
                   or could be an input. 

    Methods
    -----------
    Same as BaseTreatment: update,
    calculate_digester_outputs_daily_step. --> helper function for update, returns AnaerobicDigesterOutput object

    """

    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: AnaerobicDigesterInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)
        self.weather_data = SimpleWeather()

        handler = self.manure_handler.last_output
        self.total_solids = 0.0
        self.volatile_solids = 0.0
        self.wastewater_volume = 0.0
        self.minimum_digester_volume=0
        self.top_cover_volume=0
        self.biogas_generation=0
        self.effluent_total_solids=0
        self.effluent_volatile_solids=0
        self.methane_generation_volume=0
        self.energy_content=0
        self.input_energy_heating=0
        self.sludge_accumulation_volume=0
        self.evaporated_water=0
        self.effluent_waste_volume=0
        self.N_content=0
        self.P_content=0
        self.K_content=0
        self.sludge_accumulation_volume=0
        

    def update(self) -> TreatmentOutput:
        daily_output = self.calculate_digester_outputs_daily_step()
        self.all_output.append(daily_output)
        return daily_output


    def calculate_digester_outputs_daily_step(self):

        """ Returns the daily_ouput of AnaerobicDigestion output
            :params self
                Uses data from AnaerobicDigestorInitData class
                Uses outputs from ReceptionPitOutputs       
        """
        handler = self.manure_handler.last_output
        self.total_solids = handler.TSd  # kg/day
        self.volatile_solids = handler.VSd + handler.VSnd  # kg/day
        self.wastewater_volume = handler.total_daily_mass

        moisture_content = self.get_moisture_content()
        T_avg = self.weather_data.T_avg
        self.input_energy_heating = self.calcSpecificInputEnergy(T_avg,moisture_content)*self.wastewater_volume
        
        ## m^3/year  MS.3.B.1
        self.sludge_accumulation_volume = self.get_sav()

        # Minimum digester volume required for processing inflow  (m^3)
        # MS.3.B.2
        self.minimum_digester_volume = self.get_minimum_digester_volume()

        # MS.3.B.3
        self.top_cover_volume = self.get_top_cover_volume(self.minimum_digester_volume)


        # MS.3.B.4
        self.digester_volume_of_anaerobic_lagoon = self.minimum_digester_volume + self.top_cover_volume + self.sludge_accumulation_volume

        # kg biogas generated in digester
        # MS.3.B.6
        self.biogas_generation = self.get_biogas_generation()

        # MS.3.B.7
        self.methane_generation_volume = self.get_methane_generation_volume(self.biogas_generation)
        # content of biogas (m3)

        # Energy content of biogas
        self.energy_content = self.get_energy_content(self.methane_generation_volume)

        # ------------------------Digester EFFLUENT Characteristics-------------------------------------
        # MS.3.B.8
        self.effluent_waste_volume = self.wastewater_volume
        self.evaporated_water = self.get_evaporated_water() ## m^3/day

        # MS.3.B.9
        self.effluent_total_solids = self.get_effluent_total_solids()

        # MS.3.B.10
        self.effluent_volatile_solids = self.get_effluent_volatile_solids()
        # Nutrient content of outputs
        self.N_content = self.get_nutrient_content(self.treatment_init_data.N_FRACTION,handler.manure_nitrogen)
        self.P_content = self.get_nutrient_content(self.treatment_init_data.P_FRACTION,handler.p_excrt_manure)
        self.K_content = self.get_nutrient_content(self.treatment_init_data.K_FRACTION,handler.K_manure)

        ad_daily_output = AnaerobicDigesterOutput(
                    urea = 0.0,
                    TAN_s = 0.0,
                    manure_nitrogen = self.N_content,
                    TSd = self.effluent_total_solids,
                    VSd = self.effluent_volatile_solids-handler.VSnd,
                    VSnd = handler.VSnd,
                    VS_total = self.effluent_volatile_solids,
                    p_excrt_manure = self.P_content,
                    K_manure = self.K_content,
                    total_daily_mass = self.effluent_waste_volume, 
                    final_volume=self.effluent_waste_volume,

                    ## Outputs for AD
                    AD_effluent_volume = self.effluent_waste_volume,                     ## methane production per day (m3/day)
                    AD_biogas = self.biogas_generation,                                  ## biogas production per day (m3/day)
                    AD_biogas_energy_content = self.energy_content,                       ## biogas energy content (MJ/m3)  
                    AD_methane_generation_volume =self.methane_generation_volume,   
                    AD_input_energy_heating =self.input_energy_heating                   
        )

        daily_output = TreatmentOutput(
                    manure_nitrogen = self.N_content,
                    TSd = self.effluent_total_solids,
                    VSd = self.effluent_volatile_solids-handler.VSnd,
                    VSnd = handler.VSnd,
                    VS_total = self.effluent_volatile_solids,
                    p_excrt_manure = self.P_content,
                    K_manure = self.K_content,
                    total_daily_mass = self.effluent_waste_volume, 
                    final_volume=self.effluent_waste_volume,
        )
        return daily_output

   
    def get_moisture_content(self):
        """Returns moisture_content of influent as decimal (0-1)
        """
        if(self.wastewater_volume>0.0):
            return 1-self.total_solids/self.wastewater_volume
        else: 
            return 0

    def get_nutrient_content(self,nutrient_fraction, manure_nutrient_content):
        """Returns nutrient content of effluent
        :param nutrient_fraction: the predefined fraction from init_data.
        :param manure_nutrient_content: manure_nutrient_content from reception_pit_output_data 
        """
        if(self.total_solids>0):
            return (1 - nutrient_fraction) * (
                    manure_nutrient_content / self.total_solids)
        else:
            return 0.0
    
    def get_biogas_generation(self):
        """Returns biogas generation volume
        """
        return self.treatment_init_data.BIOGAS_GEN_RATIO * self.volatile_solids

    def get_minimum_digester_volume(self):
        """Returns minimum digester volume required based on HRT
        """
        return self.wastewater_volume * self.treatment_init_data.hydraulic_retention_time

    def get_top_cover_volume(self,minimum_digester_volume):
        """Returns top cover volume
        :param minimum_digester_volume: minimum digester volume in m3
        """
        return self.treatment_init_data.TOP_COVER_VOLUME_FRACTION * minimum_digester_volume

    def get_sav(self):
        """Returns sludge_accumulation_volume
        """
        return self.treatment_init_data.SAV_FRACTION*self.volatile_solids*self.treatment_init_data.sludge_accumulation_period* \
            Constants.DAYS_PER_YEAR/Constants.DENSITY_WATER_KG_PER_M3

    def get_effluent_total_solids(self):
        """Returns effluent_total_solids
        """
        if(self.wastewater_volume>0):
            return self.treatment_init_data.TS_FRACTION * self.total_solids/self.wastewater_volume  ## g/L
        else:
            return 0.0
            
    def get_effluent_volatile_solids(self):
        """Returns effluent_volatile_solids
        """
        if(self.wastewater_volume>0):
            return self.treatment_init_data.VS_FRACTION * self.volatile_solids/self.wastewater_volume  ## g/L
        else:
            return 0.0

    def get_evaporated_water(self):
        """Returns evaporated water volume
        """
        return self.treatment_init_data.EVAPORATION_FRACTION * self.wastewater_volume  ## m^3/day

    def get_methane_generation_volume(self,biogas_generation):
        """Returns methane_generation_volume
        :param biogas_generation: 
        """
        return biogas_generation * self.treatment_init_data.METHANE_GEN_RATIO  ## MethaneY_DENSITY  ###

    def get_methane_volume_using_chen_equation(self):
        """Returns methane_generation_volume as calculated by Chen and Hashimoto Model 
        """
        Go = 240 ## Methane potential (mL/g VS)
        KCH = 3.1 ## Chen and Hashimoto kinetic constant 
        sgr = 0.637 ## Specific Growth Rate (micrometers)
        return Go*(1-KCH/(self.treatment_init_data.hydraulic_retention_time*sgr+KCH-1)) * self.effluent_volatile_solids*Constants.GRAMS_TO_KG  ##

    def get_energy_content(self,methane_generation_volume):
        """Returns energy content of methane
        :param methane_generation_volume: 
        """
        return methane_generation_volume * Constants.METHANE_DENSITY * Constants.METHANE_ENERGY_DENSITY  ###

    def calcSpecificInputEnergy(self,T_avg,moisture_content):
        """ Returns the energy required to maintain AD temperature at setpoint
            :params:   T_avg: Average daily temperature (C)
                       moisture_content: 0-1 decimal representing water content of manure
        """
        effluent_temperature = self.bound_influent_temperature(T_avg)
        heat_capacity_influent = self.calcHeatCapacityManure(T_avg, moisture_content)
        heat_capacity_AD = self.calcHeatCapacityManure(self.treatment_init_data.AD_TEMP_SETPOINT, moisture_content)
        avg_heat_capacity =(heat_capacity_influent+heat_capacity_AD)/2
        input_energy_heating = avg_heat_capacity * (self.treatment_init_data.AD_TEMP_SETPOINT-effluent_temperature)
        return input_energy_heating

    def bound_influent_temperature(self,T_avg):
        """ Returns the max between T_avg and temperature bound
        :param T_avg: average daily temperature
        """
        the_max =max(T_avg,4)
        return the_max

    def calcHeatCapacityManure(self,T_avg,moisture_content):
        """ Returns heat capacity of manure.  (kJ /kg /C)
            :param T_avg: Average daily temp (C) 
            :param moisture_content: decimal form (0-1)
        """ 
        return 0.68298+0.025662*T_avg+0.01306*moisture_content*100


class AnaerobicLagoon(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


class StoragePond(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: StoragePondInitData,
                 storage_time_period=90,
                 freeboard=0.0,
                 precip=0.0):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)

        self.storage_time_period = storage_time_period  # days
        self.freeboard = freeboard  # m^3
        self.precip = precip  # m^3 (25-year 24h storm event)

    @property
    def treatment_volume(self) -> float:
        return self.storage_time_period * self.manure_handler.last_output.total_daily_mass  # m^3

    @property
    def total_volume(self) -> float:
        return self.treatment_volume + self.freeboard + self.precip  # m^3

    def update(self) -> TreatmentOutput:
        handler = self.manure_handler.last_output
        daily_output = TreatmentOutput(
                TAN_s=handler.TAN_s * (1 - self.treatment_init_data.TAN_removal_efficiency),
                manure_nitrogen=handler.manure_nitrogen * (1 - self.treatment_init_data.N_removal_efficiency),
                TSd=handler.TSd * (1 - self.treatment_init_data.TS_removal_efficiency),
                VS_total=handler.VS_total * (1 - self.treatment_init_data.VS_removal_efficiency),
                p_excrt_manure=handler.p_excrt_manure * (1 - self.treatment_init_data.P_removal_efficiency),
                K_manure=handler.K_manure * (1 - self.treatment_init_data.K_removal_efficiency),
        )

        daily_output.final_volume = self.total_volume - (
                (daily_output.TSd + daily_output.VS_total) * self.storage_time_period * Constants.KG_TO_CUBIC_METERS)

        # If needed, modify output based on different combinations
        # of handler and separator
        # But if the logic is complex, then abstract that out and handle it differently
        # if self.manure_handler.manure_handler_enum == ManureHandlerEnum.FLUSH_SYSTEM:
        #     pass

        self.all_output.append(daily_output)
        return daily_output


class TreatmentInitData(ABC):
    def __getattr__(self, item):
        return 0.0

    # Can remove this method altogether if we only use default values
    @classmethod
    @abstractmethod
    def get_instance(cls, *args, **kwargs):
        pass


class TreatmentFactory:
    @classmethod
    def get_instance(cls,
                     pen: SimplePen,
                     manure_handler: BaseManureHandler,
                     manure_separator: BaseSeparator) -> BaseTreatment:
        treatment_enum = TreatmentEnum.get_enum(pen.manure_storage)

        enum_to_class: Dict[TreatmentEnum, Tuple[Type[BaseTreatment], Type[TreatmentInitData]]] = {
            treatment_enum.STORAGE_POND: (StoragePond, StoragePondInitData),
            treatment_enum.ANAEROBIC_DIGESTION: (AnaerobicDigestion, AnaerobicDigesterInitData),
            # treatment_enum.ANAEROBIC_LAGOON: (AnaerobicLagoon, AnaerobicLagoonInitData),
        }

        params = {
            'pen': pen,
            'manure_handler': manure_handler,
            'manure_separator': manure_separator,
            'treatment_init_data': enum_to_class[treatment_enum][1].get_instance()
        }

        return enum_to_class[treatment_enum][0](**params)


@dataclass
class StoragePondInitData(TreatmentInitData):
    """
    A data class that contains information used in the
    creation of a Treatment object.

    """

    percent_dry_solids = 1.0
    TS_removal_efficiency = 0.15
    VS_removal_efficiency = 0.85
    N_removal_efficiency = 0.05
    TAN_removal_efficiency = 0.1
    P_removal_efficiency = 0.0
    K_removal_efficiency = 0.0
    TS_DM_effluent_rate = 0.0

    @classmethod
    def get_instance(cls) -> TreatmentInitData:
        return StoragePondInitData()


@dataclass
class AnaerobicDigesterInitData(TreatmentInitData, ABC):
    """
    A data class that contains information used in the
    creation of a AnaerobicDigester object. Overrides default values from
    TreatmentInitData, and adds properties unique to this component

    """


    hydraulic_retention_time: int = 25  # 25 -30 days
    sludge_accumulation_period: float = 1.0  # Sludge accumulation period 1-5 years

    SAV_FRACTION: float = 0.03  # Sludge Accumulation volume fraction 2-4% of VS loaded

    TOP_COVER_VOLUME_FRACTION: float = 0.2  # Should be between 10-30%
    BIOGAS_GEN_RATIO: float = 0.38  # 0.23 to 0.39 kg CH4/kg VS
    METHANE_GEN_RATIO: float = 0.65  # 0.5-0.65 according to spreadsheet

    # Digester EFFLUENT Characteristics
    EVAPORATION_FRACTION: float = 0.02  # 2-5% of Wastewater Volume

    # Fraction of total solids loading in effluent to original concentration
    TS_FRACTION: float = 0.45
    # Fraction of volatile solids in effluent to original concentration
    VS_FRACTION: float = 0.40

    N_FRACTION: float = 0.0  # 0-5% N fraction
    P_FRACTION: float = 0.0  # 0-5% P fraction
    K_FRACTION: float = 0.0  # 0-5% K fraction

    AD_TEMP_SETPOINT: float = 37.5
    AD_TEMP: float = 37.5
    @classmethod
    def get_instance(cls) -> TreatmentInitData:
        return AnaerobicDigesterInitData()
