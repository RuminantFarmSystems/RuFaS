from __future__ import annotations

from abc import ABC
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import auto
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from RUFAS.classes import Weather
from RUFAS.classes import Time
from RUFAS.routines.manure.constants.constants import ManureManagementConstants
from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


class TreatmentType(DefaultEnum):
    """Enumerates the different types of manure treatments."""
    SLURRY_STORAGE_UNDERFLOOR = auto()
    SLURRY_STORAGE_OUTDOOR = auto()
    DEFAULT = SLURRY_STORAGE_UNDERFLOOR


class BaseManureTreatment(ABC):
    def __init__(self, weather: Weather, time: Time, manure_treatment_config: ManureTreatmentConfig) -> None:
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config
        self.all_output: List[ManureTreatmentDailyOutput] = []
        self.accumulated_output = ManureTreatmentDailyOutput()
        self.simulation_day = 0

    @property
    def last_output(self) -> Optional[ManureTreatmentDailyOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    @staticmethod
    def _pick_input_data(reception_pit_daily_output: ReceptionPitDailyOutput,
                         manure_separator_daily_output: ManureSeparatorDailyOutput) \
            -> Union[ReceptionPitDailyOutput, ManureSeparatorDailyOutput]:
        if manure_separator_daily_output is not None:
            return manure_separator_daily_output
        else:
            return reception_pit_daily_output

    @abstractmethod
    def _update_helper(self,
                       reception_pit_daily_output: ReceptionPitDailyOutput,
                       manure_separator_daily_output: Optional[ManureSeparatorDailyOutput]
                       ) -> ManureTreatmentDailyOutput:
        pass

    def daily_update(self,
                     reception_pit_daily_output: ReceptionPitDailyOutput,
                     manure_separator_daily_output: Optional[ManureSeparatorDailyOutput],
                     sim_day: int
                     ) -> ManureTreatmentDailyOutput:
        daily_output = self._update_helper(reception_pit_daily_output, manure_separator_daily_output)
        self.all_output.append(daily_output)
        self.accumulated_output += daily_output
        self.simulation_day += 1
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

    def land_application_day_update_manure_storage(self, requested_manure_fraction=1):
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


class SlurryStorageUnderfloor(BaseManureTreatment):

    def __init__(self, weather: Weather, time: Time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period  # days

    def _calc_total_volume(self, input_data: Union[ManureSeparatorDailyOutput, ReceptionPitDailyOutput]) -> float:
        return self.storage_time_period * input_data.total_daily_manure_volume

    def _calc_final_manure_volume(self, input_data: Union[ManureSeparatorDailyOutput, ReceptionPitDailyOutput]) -> float:
        return self._calc_total_volume(input_data) - (
                (input_data.TS + input_data.VS_total) * self.storage_time_period *
                ManureManagementConstants.KG_TO_CUBIC_METERS
        )

    def _update_helper(self,
                       reception_pit_daily_output: ReceptionPitDailyOutput,
                       manure_separator_daily_output: Optional[ManureSeparatorDailyOutput]) \
            -> ManureTreatmentDailyOutput:
        input_data = super()._pick_input_data(reception_pit_daily_output, manure_separator_daily_output)

        daily_output = ManureTreatmentDailyOutput(
                simulation_day=input_data.simulation_day,
                pen_id=input_data.pen_id,
                TAN=input_data.TAN * (1 - self.config.TAN_removal_efficiency),
                N=input_data.N * (1 - self.config.N_removal_efficiency),
                TS=input_data.TS * (1 - self.config.TS_removal_efficiency),
                VS_total=input_data.VS_total * (1 - self.config.VS_removal_efficiency),
                P=input_data.P * (1 - self.config.P_removal_efficiency),
                K=input_data.K * (1 - self.config.K_removal_efficiency),
        )
        daily_output.final_manure_volume = self._calc_final_manure_volume(input_data)
        return daily_output


class SlurryStorageOutdoor(BaseManureTreatment):
    def __init__(self, weather: Weather, time: Time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period  # m^3 (25-year 24h storm event)
        self.freeboard_input = self.config.freeboard_input  # m
        self.precip_input = self.config.precip_input  # m (25-year 24h storm event)

    def _update_helper(self,
                       reception_pit_daily_output: ReceptionPitDailyOutput,
                       manure_separator_daily_output: Optional[ManureSeparatorDailyOutput],
                       ) -> ManureTreatmentDailyOutput:
        input_data = super()._pick_input_data(reception_pit_daily_output, manure_separator_daily_output)
        daily_output = ManureTreatmentDailyOutput(
                TAN=input_data.TAN * (1 - self.config.TAN_removal_efficiency),
                N=input_data.N * (1 - self.config.N_removal_efficiency),
                TS=input_data.TS * (1 - self.config.TS_removal_efficiency),
                VS_total=input_data.VS_total * (1 - self.config.VS_removal_efficiency),
                P=input_data.P * (1 - self.config.P_removal_efficiency),
                K=input_data.K * (1 - self.config.K_removal_efficiency),
        )
        return daily_output

    @property
    def wastewater_volume(self):
        """returns wastewater volume in m^3"""
        return self.manure_handler.last_output.total_daily_manure_volume

    @property
    def treatment_volume(self) -> float:
        """returns minimum treatment volume in m^3"""
        return (
                self.manure_handler.last_output.total_daily_manure_volume *
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
        c = 4 * (self.pit_slope ** 2) * (self.pit_depth ** 3) / 3 - self.total_treatment_volume
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
        current_day_rainfall = self.weather.rainfall[self.time.year - 1][self.time.day - 1]
        return current_day_rainfall * self.pit_surface_area  # m3 of rain

    @property
    def freeboard(self):
        """returns additional lagoon volume needed for freeboard in m^3"""
        return self.freeboard_input * self.pit_surface_area  # m3 of rain


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

    @classmethod
    def get_instance(cls, treatment_type: TreatmentType) -> ManureTreatmentConfig:
        manure_treatment_config_by_type = {
            TreatmentType.SLURRY_STORAGE_UNDERFLOOR: cls.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
            TreatmentType.SLURRY_STORAGE_OUTDOOR: cls.SLURRY_STORAGE_OUTDOOR_CONFIG,
        }
        return manure_treatment_config_by_type[treatment_type]


class ManureTreatmentFactory:
    @staticmethod
    def get_instance(manure_treatment_type_name: str,
                     weather: Weather,
                     time: Time,
                     customer_manure_treatment_config: Optional[ManureTreatmentConfig] = None) \
            -> BaseManureTreatment:

        manure_treatment_class_by_type: Dict[TreatmentType, Type[BaseManureTreatment]] = {
            TreatmentType.SLURRY_STORAGE_UNDERFLOOR: SlurryStorageUnderfloor,
            TreatmentType.SLURRY_STORAGE_OUTDOOR: SlurryStorageOutdoor,
        }

        manure_treatment_type = TreatmentType.get_type(manure_treatment_type_name)
        manure_treatment_class = manure_treatment_class_by_type[manure_treatment_type]

        if customer_manure_treatment_config:
            return manure_treatment_class(weather, time, customer_manure_treatment_config)
        else:
            default_manure_treatment_config = DefaultManureTreatmentConfigFactory.get_instance(manure_treatment_type)
            return manure_treatment_class(weather, time, default_manure_treatment_config)
