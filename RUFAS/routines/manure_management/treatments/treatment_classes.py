"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import auto
from typing import Dict, List, Optional, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseSeparator
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import ReceptionPitFactory
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.treatments.treatment_output import TreatmentOutput, AnaerobicDigesterOutput


class TreatmentEnum(ExtendedEnum):
    STORAGE_POND = auto()
    ANAEROBIC_LAGOON = auto()
    ANAEROBIC_DIGESTION = auto()
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
            An instance of this class represents an storage receptacle.
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
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def update(self, pen: SimplePen) -> TreatmentOutput:
        # self.methane(pen.manure)
        # self.WIP_WOP_frac()
        daily_output = TreatmentOutput(

        )
        self.all_output.append(daily_output)
        return daily_output

    def methane(self, manure):
        # manure.CH4_emissions = self.VS * manure.Bo * manure.MCF * manure.MS * manure.m3
        # self.daily_vars.CH4 = self.daily_vars.VS * Constants.Bo * Constants.MCF * Constants.MS * Constants.m3
        pass

    def WIP_WOP_frac(self):
        # daily = self.daily_vars
        # if daily.TS + daily.VS == 0:
        #     daily.WIP_frac = 0.0
        #     daily.WOP_frac = 0.0
        # else:
        #     daily.WIP_frac = daily.WIP / (daily.TS + daily.VS)
        #     daily.WOP_frac = daily.WOP / (daily.TS + daily.VS)
        pass


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
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)

        ## TODO: Check whether reception pit will always be the component preceding AD.. could move to be input.
        self.reception_pit = ReceptionPitFactory.get_instance(manure_handler=self.manure_handler)
        self.all_output: List[AnaerobicDigesterOutput] = []

    def update(self, pen: SimplePen) -> TreatmentOutput:
        ## TODO: Check whether SimplePen should be an input for update, it is not used in the BaseTreatment update
        ## and is not used here.. why is it an input?
        daily_output = self.calculate_digester_outputs_daily_step()
        self.all_output.append(daily_output)
        return daily_output

    def calculate_digester_outputs_daily_step(self):
        # TODO: Write description of method, input parameters, and 
        """ calculates biogas production, and returns effluent characteristics
            Uses init data from AnaerobicDigestorInitData class
            Uses outputs from manure_handler, in this case ReceptionPitOutputs       
        """
        reception_pit_output_data = self.reception_pit.last_output  ## What to do when last output is None? (i.e.
        # first day?)

        total_solids = reception_pit_output_data.TSd  # kg/day
        volatile_solids_loading = reception_pit_output_data.VSd + reception_pit_output_data.VSnd  # kg/day
        wastewater_volume = reception_pit_output_data.total_daily_mass / self.treatment_init_data.density_water  #
        # m^3/day

        # May use these default input values to test the calculation method
        # wastewater_volume = 270.51         # From pens-   m^3/day
        # total_solids = 2548.70             # from pen - kg/day
        # volatile_solids_loading = 1980.94  # from pen - kg/day

        total_solids_concentration = total_solids / wastewater_volume  ## g/L
        volatile_solids_concentration = volatile_solids_loading / wastewater_volume  ## g/L

        # TODO: Check whether this variable should be an output.
        ## m^3/year  MS.3.B.1
        sav = self.treatment_init_data.SAV_FRACTION * volatile_solids_loading * \
              self.treatment_init_data.sludge_accumulation_period * \
              self.treatment_init_data.days_in_year / self.treatment_init_data.density_water

        # Minimum digester volume required for processing inflow  (m^3)
        # MS.3.B.2
        minimum_digester_volume = wastewater_volume * self.treatment_init_data.hydraulic_retention_time

        # MS.3.B.3
        top_cover_volume = self.treatment_init_data.TOP_COVER_VOLUME_FRACTION * minimum_digester_volume

        # MS.3.B.4
        digester_volume_of_anaerobic_lagoon = minimum_digester_volume + top_cover_volume + sav

        # MS.3.B.5
        vs_loading_rate = volatile_solids_concentration / digester_volume_of_anaerobic_lagoon

        # kg biogas generated in digester

        # MS.3.B.6
        biogas_generation = self.treatment_init_data.BIOGAS_GEN_RATIO * volatile_solids_loading

        # TODO: Double check units in spreadsheet on methane production
        # MS.3.B.7
        methane_generation_volume = biogas_generation * self.treatment_init_data.METHANE_GEN_RATIO  ## Methane
        # content of biogas (m3)

        # TODO: Add these constants to init data or constants class in misc module
        methane_energy_density = 55  # MJ / kg
        methane_density = 0.657  # kg/m^3

        # Energy content of biogas
        energy_content = methane_generation_volume * methane_density * methane_energy_density  ###

        # ------------------------Digester EFFLUENT Characteristics-------------------------------------
        # MS.3.B.8
        effluent_waste_volume = wastewater_volume
        evaporated_water = self.treatment_init_data.EVAPORATION_FRACTION * wastewater_volume  ## m^3/day

        # TODO: Check if TS fraction should be used or percentage of loaded total solids lost or 
        # MS.3.B.9
        effluent_total_solids = self.treatment_init_data.TS_FRACTION * total_solids_concentration  ## g/L

        # TODO: Check if VS fraction should be used or percentage of loaded volatile solids lost   
        # MS.3.B.10
        effluent_volatile_solids = self.treatment_init_data.VS_FRACTION * volatile_solids_concentration  ## g/L

        """ May want to save these values for testing the methods"""
        # N_from_pen = 7.32 # g/L
        # P_from_pen = 0.26 # g/L
        # K_from_pen = 0.53 # g/L

        # N_from_pen_kg_per_day = 1980.9 # kg/day
        # P_from_pen_kg_per_day = 69.6 # kg/day
        # K_from_pen_kg_per_day = 136.0 # kg/day

        """ These variables come from the Pen 1 sheet in spreadsheet, and  reception pit in Rufas"""
        """ These should be replaced by mapping reception pit outputs to required inputs (TS,VS, and volumetric flow)"""

        N_from_pen = 7.32  # g/L
        P_from_pen = 0.26  # g/L
        K_from_pen = 0.53  # g/L

        N_from_pen_kg_per_day = reception_pit_output_data.manure_nitrogen  # kg/day
        P_from_pen_kg_per_day = reception_pit_output_data.p_excrt_manure  # kg/day
        K_from_pen_kg_per_day = reception_pit_output_data.K_manure  # kg/day
        # TODO: Should I use the N_FRACTION or (1-N_FRACTION)
        # MS.3.B.11
        N_content = N_from_pen - (N_from_pen_kg_per_day / total_solids) * self.treatment_init_data.N_FRACTION
        P_content = P_from_pen - (P_from_pen_kg_per_day / total_solids) * self.treatment_init_data.P_FRACTION
        K_content = K_from_pen - (K_from_pen_kg_per_day / total_solids) * self.treatment_init_data.K_FRACTION

        daily_output = AnaerobicDigesterOutput(
                # TODO: Check difference between TS and TS_liquid for effluent
                TS=effluent_total_solids,
                VS=effluent_volatile_solids,
                N=N_content,
                P=P_content,
                K=K_content,

                TS_liquid=0.0,
                VS_liquid=0.0,
                N_liquid=0.0,
                P_liquid=0.0,
                K_liquid=0.0,

                WIP=0.0,
                WOP=0.0,
                WIP_frac=0.0,
                WOP_frac=0.0,
                CH4=0.0,  # May use this variable name instead of methane_generation_volume

                # Important Outputs from AD object

                biogas=biogas_generation,  # biogas production per day (m3/day)
                methane_generation_volume=methane_generation_volume,  # biogas production per day (m3/day)
                energy_content=energy_content,  # biogas energy content (MJ/m3)
                minimum_digester_volume=minimum_digester_volume,
                # Minimum Digester Volume calculated based on daily inflow (m^3)
                top_cover_volume=top_cover_volume,  # TopCover Volume calculated based on Digester Volume (m^3)
                sludge_accumulation_volume=sav,  # sludge_accumulation_volume (per day?)

                evaporated_water=evaporated_water,
                effluent_waste_volume=effluent_waste_volume,
                effluent_total_solids=effluent_total_solids,
                effluent_volatile_solids=effluent_volatile_solids

        )

        return daily_output


class AnaerobicLagoon(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


class CustomTreatment(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData,
                 storage_time_period=90,
                 freeboard=0.0,
                 precip=0.0):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


class StoragePond(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData,
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
        rp = self.reception_pit.last_output
        sep = self.manure_separator.last_output
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
        # if self.manure_handler.manure_handler_enum == ManureHandlerEnum.FLUSH_SYSTEM:
        #     pass

        self.all_output.append(daily_output)
        return daily_output


@dataclass
class TreatmentInitData:
    """
    A data class that contains information used in the
    creation of a Treatment object.

    """
    percent_dry_solids: float = 0.0
    TS_removal_efficiency: float = 0.0
    VS_removal_efficiency: float = 0.0
    N_removal_efficiency: float = 0.0
    TAN_removal_efficiency: float = 0.0
    P_removal_efficiency: float = 0.0
    K_removal_efficiency: float = 0.0
    TS_DM_effluent_rate: float = 0.0

    # sludge_accumulation_volume: float = 0.00251
    # hydraulic_retention_time: int = 180
    # sludge_accumulation_period: float = 5.0

    @classmethod
    def get_instance(cls, treatment_enum: TreatmentEnum) -> TreatmentInitData:
        enum_to_init_data: Dict[TreatmentEnum, TreatmentInitData] = {
            TreatmentEnum.STORAGE_POND: TreatmentInitData(
                    percent_dry_solids=0.0,
                    TS_removal_efficiency=0.15,
                    VS_removal_efficiency=0.85,
                    N_removal_efficiency=0.05,
                    TAN_removal_efficiency=0.1,
                    P_removal_efficiency=0.0,
                    K_removal_efficiency=0.0,
                    TS_DM_effluent_rate=0.0
            ),
        }

        if treatment_enum in enum_to_init_data:
            return enum_to_init_data[treatment_enum]
        return TreatmentInitData()

        # init_data = TreatmentInitData()
        #
        # # Customize init data here based on enum if necessary
        # # ...
        # if(treatment_enum.name == 'ANAEROBIC_DIGESTION'):
        #     init_data = AnaerobicDigestorInitData()
        #
        #
        # return init_data


class TreatmentFactory:
    @classmethod
    def get_instance(cls,
                     pen: SimplePen,
                     manure_handler: BaseManureHandler,
                     manure_separator: BaseSeparator) -> BaseTreatment:
        treatment_enum = TreatmentEnum.get_enum(pen.manure_storage)
        params = {
            'pen': pen,
            'manure_handler': manure_handler,
            'manure_separator': manure_separator,
            'treatment_init_data': TreatmentInitData.get_instance(treatment_enum)
        }
        enum_to_class: Dict[TreatmentEnum, Type[BaseTreatment]] = {
            treatment_enum.STORAGE_POND: StoragePond,
            treatment_enum.ANAEROBIC_LAGOON: AnaerobicLagoon,
            treatment_enum.ANAEROBIC_DIGESTION: AnaerobicDigestion,
            treatment_enum.CUSTOM_STORAGE: CustomTreatment
        }
        return enum_to_class[treatment_enum](**params)


@dataclass
class AnaerobicDigestorInitData(TreatmentInitData):
    """
    A data class that contains information used in the
    creation of a AnaerobicDigester object. Overrides default values from
    TreatmentInitData, and adds properties unique to this component

    """

    sludge_accumulation_volume: float = 0.00251  # SAV total? or is this the fraction
    hydraulic_retention_time: int = 25  # 25 -30 days
    sludge_accumulation_period: float = 1.0  # Sludge accumulation period 1-5 years

    SAV_FRACTION: float = 0.03  # Sludge Accumulation volume fraction 2-4% of VS loaded

    density_water: float = 999  # kg/m3
    days_in_year: int = 365  # days per year

    TOP_COVER_VOLUME_FRACTION: float = 0.2  # Should be between 10-30%
    BIOGAS_GEN_RATIO: float = 0.38  # 0.23 to 0.39 kg CH4/kg VS
    METHANE_GEN_RATIO: float = 0.65  # 0.5-0.65 according to spreadsheet

    # Digester EFFLUENT Characteristics
    EVAPORATION_FRACTION: float = 0.02  # 2-5% of Wastewater Volume

    TS_FRACTION: float = 0.45  # Fraction of total solids loading in effluent to original concentration
    VS_FRACTION: float = 0.40  # Fraction of volatile solids in effluent to original concentration

    N_FRACTION: float = 0.01  # 0-5% N fraction
    P_FRACTION: float = 0.01  # 0-5% P fraction
    K_FRACTION: float = 0.0  # 0-5% K fraction

    @classmethod
    def get_instance(cls, treatment_enum: TreatmentEnum) -> TreatmentInitData:
        init_data = AnaerobicDigestorInitData()
        return init_data
