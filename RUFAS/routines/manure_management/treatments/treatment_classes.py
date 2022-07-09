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
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.treatments.treatment_output import AnaerobicDigesterOutput, TreatmentOutput


class TreatmentEnum(ExtendedEnum):
    """Enumerates available treatment options."""
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
        Description:
            An instance of this class represents a storage receptacle.
            It is primarily used by the emissions sub-module

        Args:
            pen
            treatment_init_data
        """
        self.pen = pen
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

    def update(self, pen: SimplePen) -> TreatmentOutput:
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
    ----------
    pen: SimplePen  ---> pen associated with the manure flow? -- 
                    ---> not sure this should be an input since all flow is channeled through reception pit
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
    Same as BaseTreatment: reset_daily_variables, last_output, update, methane, WIP_WOP_fraction
    calculate_digester_outputs_daily_step. --> helper function for update, returns AnaerobicDigesterOutput object

    """

    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: AnaerobicDigesterInitData,
                 weather_data):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)
        self.evaporated_water = None
        self.sludge_accumulation_volume = None
        self.top_cover_volume = None
        self.minimum_digester_volume = None

        self.weather_data = weather_data

    def update(self) -> TreatmentOutput:
        daily_output = self.calculate_digester_outputs_daily_step()
        self.all_output.append(daily_output)
        return daily_output

    def calculate_digester_outputs_daily_step(self):
        # TODO: Write description of method, input parameters, and
        """ calculates biogas production, and returns effluent characteristics
            Uses init data from AnaerobicDigestorInitData class
            Uses outputs from manure_handler, in this case ReceptionPitOutputs       
        """
        reception_pit_output_data = self.reception_pit.last_output

        total_solids = reception_pit_output_data.TSd  # kg/day
        volatile_solids_loading = reception_pit_output_data.VSd + \
            reception_pit_output_data.VSnd  # kg/day
        wastewater_volume = reception_pit_output_data.total_daily_mass / \
            Constants.DENSITY_WATER_KG_PER_M3  # m^3/day

        moisture_content = 1-total_solids/reception_pit_output_data.total_daily_mass
        T_avg = self.weather_data.T_avg
        input_energy_heating = self.calcSpecificInputEnergy(
            T_avg, moisture_content)*reception_pit_output_data.total_daily_mass

        # m^3/year  MS.3.B.1
        sav = self.treatment_init_data.SAV_FRACTION*volatile_solids_loading*self.treatment_init_data.sludge_accumulation_period * \
            Constants.DAYS_PER_YEAR/Constants.DENSITY_WATER_KG_PER_M3

        # Minimum digester volume required for processing inflow  (m^3)
        # MS.3.B.2
        minimum_digester_volume = wastewater_volume * \
            self.treatment_init_data.hydraulic_retention_time

        # MS.3.B.3
        top_cover_volume = self.treatment_init_data.TOP_COVER_VOLUME_FRACTION * \
            minimum_digester_volume

        # MS.3.B.4
        digester_volume_of_anaerobic_lagoon = minimum_digester_volume + top_cover_volume + sav

        # kg biogas generated in digester
        # MS.3.B.6
        biogas_generation = self.treatment_init_data.BIOGAS_GEN_RATIO * volatile_solids_loading

        # TODO: Double check units in spreadsheet on methane production
        # MS.3.B.7
        methane_generation_volume = biogas_generation * \
            self.treatment_init_data.METHANE_GEN_RATIO  # Methane
        # content of biogas (m3)

        # Energy content of biogas
        energy_content = methane_generation_volume * \
            Constants.METHANE_DENSITY * Constants.METHANE_ENERGY_DENSITY

        # ------------------------Digester EFFLUENT Characteristics-------------------------------------
        # MS.3.B.8
        effluent_waste_volume = wastewater_volume
        evaporated_water = self.treatment_init_data.EVAPORATION_FRACTION * \
            wastewater_volume  # m^3/day

        # TODO: Check if TS fraction should be used or percentage of loaded total solids lost or
        # MS.3.B.9
        effluent_total_solids = self.treatment_init_data.TS_FRACTION * \
            total_solids_concentration  # g/L

        # TODO: Check if VS fraction should be used or percentage of loaded volatile solids lost
        # MS.3.B.10
        effluent_volatile_solids = self.treatment_init_data.VS_FRACTION * \
            volatile_solids_concentration  # g/L

        # N_content of outputs
        N_content = (1 - self.treatment_init_data.N_FRACTION) * (
            reception_pit_output_data.manure_nitrogen / total_solids)
        P_content = (1 - self.treatment_init_data.P_FRACTION) * (
            reception_pit_output_data.p_excrt_manure / total_solids)
        K_content = (1 - self.treatment_init_data.K_FRACTION) * \
            (reception_pit_output_data.K_manure / total_solids)

        """ Track these variables for testing but not for outputs """
        self.minimum_digester_volume = minimum_digester_volume  # Minimum Digester Volume calculated based on daily
        # inflow (m^3)
        # TopCover Volume calculated based on Digester Volume (m^3)
        self.top_cover_volume = top_cover_volume
        # sludge_accumulation_volume (per day?)
        self.sludge_accumulation_volume = sav
        self.evaporated_water = evaporated_water

        daily_output = AnaerobicDigesterOutput(

            urea=0.0,
            TAN_s=0.0,
            manure_nitrogen=N_content,
            TSd=effluent_total_solids,
            VSd=effluent_volatile_solids-reception_pit_output_data.VSnd,
            VSnd=reception_pit_output_data.VSnd,
            VS_total=effluent_volatile_solids,
            p_excrt_manure=P_content,
            K_manure=K_content,
            total_daily_mass=effluent_waste_volume*Constants.DENSITY_WATER_KG_PER_M3,

            # Outputs for AD
            # methane production per day (m3/day)
            AD_effluent_volume=effluent_waste_volume,
            AD_biogas=biogas_generation,  # biogas production per day (m3/day)
            # biogas energy content (MJ/m3)
            AD_biogas_energy_content=energy_content,
            AD_methane_generation_volume=methane_generation_volume,
            AD_input_energy_heating=input_energy_heating
        )

        return daily_output

    def calcSpecificInputEnergy(self, T_avg, moisture_content):
        # TODO: Check on the weather and time data classes
        # Objects of the AnaerobicDigester Class will need to know the day of the year to access T_avg[day_of_year]
        # Another option is to pass a single day of weather data to the update method, so update methods for all upstream objects
        # will use the weather data from a particular day..
        if(T_avg < 4):
            effluent_temperature = 4
        else:
            effluent_temperature = T_avg
        heat_capacity_influent = self.calcHeatCapacityManure(
            self, T_avg, moisture_content)
        heat_capacity_AD = self.calcHeatCapacityManure(
            self, self.treatment_init_data.AD_TEMP_SETPOINT, moisture_content)
        avg_heat_capacity = (heat_capacity_influent+heat_capacity_AD)/2
        input_energy_heating = avg_heat_capacity * \
            (self.treatment_init_data.AD_TEMP_SETPOINT-effluent_temperature)
        return input_energy_heating

    def calcHeatCapacityManure(self, T_avg, moisture_content):
        # Inputs:   T_avg,  Celsius,
        #           moisture_content, decimal form (0-1)
        # Outputs:  heat capacity (kJ /kg /C)
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

    def update(self, pen: SimplePen) -> TreatmentOutput:
        handler = self.manure_handler.last_output
        daily_output = TreatmentOutput(
            TAN_s=handler.TAN_s *
            (1 - self.treatment_init_data.TAN_removal_efficiency),
            manure_nitrogen=handler.manure_nitrogen *
            (1 - self.treatment_init_data.N_removal_efficiency),
            TSd=handler.TSd *
            (1 - self.treatment_init_data.TS_removal_efficiency),
            VS_total=handler.VS_total *
            (1 - self.treatment_init_data.VS_removal_efficiency),
            p_excrt_manure=handler.p_excrt_manure *
            (1 - self.treatment_init_data.P_removal_efficiency),
            K_manure=handler.K_manure *
            (1 - self.treatment_init_data.K_removal_efficiency),
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

    percent_dry_solids = 0.0
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
class AnaerobicDigesterInitData(TreatmentInitData):
    """
    A data class that contains information used in the
    creation of a AnaerobicDigester object. Overrides default values from
    TreatmentInitData, and adds properties unique to this component

    """

    # SAV total? or is this the fraction
    sludge_accumulation_volume: float = 0.00251
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

    N_FRACTION: float = 0.01  # 0-5% N fraction
    P_FRACTION: float = 0.01  # 0-5% P fraction
    K_FRACTION: float = 0.0  # 0-5% K fraction

    AD_TEMP_SETPOINT: float = 37.5
    AD_TEMP: float = 37.5
