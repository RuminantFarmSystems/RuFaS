from __future__ import annotations

import math
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import auto
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from RUFAS.classes import Time
from RUFAS.classes import Weather
from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import \
    AggregatedManureDailyOutputForFieldManure
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput

ManureTreatmentInputDataType = Union[ReceptionPitDailyOutput, ManureSeparatorDailyOutput]


class ManureTreatmentType(DefaultEnum):
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
        self._current_input_data: Optional[ManureTreatmentInputDataType] = None

    @property
    def last_output(self) -> Optional[ManureTreatmentDailyOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    @staticmethod
    def _pick_input_data(reception_pit_daily_output: ReceptionPitDailyOutput,
                         manure_separator_daily_output: ManureSeparatorDailyOutput) \
            -> ManureTreatmentInputDataType:
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
        self._current_input_data = self._pick_input_data(reception_pit_daily_output, manure_separator_daily_output)
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
        output_to_field = AggregatedManureDailyOutputForFieldManure()
        output_to_field.convert_treatment_ouput_to_field_outputs(self.accumulated_output)
        return output_to_field

    def land_application_day_update_manure_storage(self, requested_manure_fraction=1):
        """
        Returns: AggregatedOutput object for field application before resetting self.accumulated_output to new levels
        outputs_for_land_application = self.accumulated_output
        """
        ## Convert aggregated outputs from TreatmentOutput type, to object type expected in Field
        output_to_field = AggregatedManureDailyOutputForFieldManure()
        output_to_field.convert_treatment_ouput_to_field_outputs(self.accumulated_output)
        # TODO Currently resets accumulated outputs to zero,
        # but should reset to new levels based on requested_manure_mass. Should be based on
        #  percentage requested
        # Input requested_manure_fraction for calculating remainder in tank
        self.accumulated_output = ManureTreatmentDailyOutput()
        return output_to_field


class SlurryStorageUnderfloor(BaseManureTreatment):

    def __init__(self, weather: Weather, time: Time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period  # days

    def _update_helper(self,
                       reception_pit_daily_output: ReceptionPitDailyOutput,
                       manure_separator_daily_output: Optional[ManureSeparatorDailyOutput],
                       ) -> ManureTreatmentDailyOutput:
        if manure_separator_daily_output:
            input_data = manure_separator_daily_output
            daily_output = ManureTreatmentDailyOutput(
                    simulation_day=input_data.simulation_day,
                    pen_id=input_data.pen_id,
                    TAN=input_data.TAN_liquid * (1 - self.config.TAN_removal_efficiency_for_treatment),
                    N=input_data.N_liquid * (1 - self.config.N_removal_efficiency_for_treatment),
                    TS=input_data.TS_liquid * (1 - self.config.TS_removal_efficiency_for_treatment),
                    VS_total=input_data.VS_liquid * (1 - self.config.VS_removal_efficiency_for_treatment),
                    P=input_data.P_liquid * (1 - self.config.P_removal_efficiency_for_treatment),
                    K=input_data.K_liquid * (1 - self.config.K_removal_efficiency_for_treatment),
                    final_manure_volume=input_data.final_daily_volume
            )
        else:
            input_data = reception_pit_daily_output
            daily_output = ManureTreatmentDailyOutput(
                    simulation_day=input_data.simulation_day,
                    pen_id=input_data.pen_id,
                    TAN=input_data.TAN * (1 - self.config.TAN_removal_efficiency_for_treatment),
                    N=input_data.N * (1 - self.config.N_removal_efficiency_for_treatment),
                    TS=input_data.TS * (1 - self.config.TS_removal_efficiency_for_treatment),
                    VS_total=input_data.VS_total * (1 - self.config.VS_removal_efficiency_for_treatment),
                    P=input_data.P * (1 - self.config.P_removal_efficiency_for_treatment),
                    K=input_data.K * (1 - self.config.K_removal_efficiency_for_treatment),
                    final_manure_volume=input_data.total_daily_manure_volume
            )

        return daily_output


class SlurryStorageOutdoor(BaseManureTreatment):
    def __init__(self, weather: Weather, time: Time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period  # m^3 (25-year 24h storm event)
        self.freeboard_input = self.config.freeboard_input  # m
        self.precip_input = self.config.precip_input  # m (25-year 24h storm event)

    def _update_helper(self,
                       reception_pit_daily_output: ReceptionPitDailyOutput,
                       manure_separator_daily_output: Optional[ManureSeparatorDailyOutput]
                       ) -> ManureTreatmentDailyOutput:
        input_data = self._current_input_data
        if manure_separator_daily_output:
            input_data = manure_separator_daily_output
            daily_output = ManureTreatmentDailyOutput(
                    simulation_day=input_data.simulation_day,
                    pen_id=input_data.pen_id,
                    TAN=input_data.TAN_liquid * (1 - self.config.TAN_removal_efficiency_for_treatment),
                    N=input_data.N_liquid * (1 - self.config.N_removal_efficiency_for_treatment),
                    TS=input_data.TS_liquid * (1 - self.config.TS_removal_efficiency_for_treatment),
                    VS_total=input_data.VS_liquid * (1 - self.config.VS_removal_efficiency_for_treatment),
                    P=input_data.P_liquid * (1 - self.config.P_removal_efficiency_for_treatment),
                    K=input_data.K_liquid * (1 - self.config.K_removal_efficiency_for_treatment),
                    final_manure_volume=input_data.final_daily_volume
            )
        else:
            input_data = reception_pit_daily_output
            daily_output = ManureTreatmentDailyOutput(
                    simulation_day=input_data.simulation_day,
                    pen_id=input_data.pen_id,
                    TAN=input_data.TAN * (1 - self.config.TAN_removal_efficiency_for_treatment),
                    N=input_data.N * (1 - self.config.N_removal_efficiency_for_treatment),
                    TS=input_data.TS * (1 - self.config.TS_removal_efficiency_for_treatment),
                    VS_total=input_data.VS_total * (1 - self.config.VS_removal_efficiency_for_treatment),
                    P=input_data.P * (1 - self.config.P_removal_efficiency_for_treatment),
                    K=input_data.K * (1 - self.config.K_removal_efficiency_for_treatment),
                    final_manure_volume=input_data.total_daily_manure_volume
            )

        return daily_output

    @property
    def wastewater_volume(self) -> float:
        """returns wastewater volume in m^3"""
        if self._current_input_data:
            return self._current_input_data.total_daily_manure_volume
        return 0.0

    @property
    def treatment_volume(self) -> float:
        """returns minimum treatment volume in m^3"""
        if self._current_input_data:
            return self._current_input_data.total_daily_manure_volume * self.storage_time_period  # m^3
        return 0.0

    @property
    def total_pit_volume(self) -> float:
        """returns Total Lagoon Volume in m^3"""
        if self._current_input_data:
            return self.treatment_volume + self.freeboard + self.precip
        return 0.0

    @property
    def pit_depth(self):
        """returns lagoon depth in meters"""
        return 3.657  # meters

    @property
    def pit_slope(self):
        """returns lagoon slope (unitless)"""
        return 2.0

    def _calc_abc(self) -> Tuple[float, float, float]:
        """returns coefficients for volume calculations as tuple (a,b,c)"""
        a = 3 * self.pit_depth
        b = -4 * self.pit_slope * self.pit_depth ** 2
        c = 4 * (self.pit_slope ** 2) * (self.pit_depth ** 3) / 3 - self.treatment_volume
        # TODO: Check if it is self.total_pit_volume or self.treatment_volume
        return a, b, c

    @property
    def pit_width(self) -> float:
        """returns lagoon width in meters"""
        if self._current_input_data:
            a, b, c = self._calc_abc()
            return (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        return 0.0

    @property
    def pit_length(self) -> float:
        """returns lagoon width in meters"""
        return self.pit_width * 3

    @property
    def pit_surface_area(self) -> float:
        """returns lagoon surface area in m^2"""
        return self.pit_width * self.pit_length

    @property
    def pit_volume(self) -> float:
        """returns lagoon volume in m^3, should match volume needed"""
        return self.pit_length * self.pit_width * self.pit_depth \
               - (self.pit_slope * (self.pit_depth ** 2)) * (self.pit_length + self.pit_width) \
               + (4 * self.pit_slope * (self.pit_depth ** 3) / 3)

    @property
    def precip(self) -> float:
        """returns additional lagoon volume needed for precipitation in m^3"""
        current_day_rainfall = self.weather.rainfall[self.time.year - 1][self.time.day - 1]
        return current_day_rainfall * self.pit_surface_area  # m3 of rain

    @property
    def freeboard(self):
        """returns additional lagoon volume needed for freeboard in m^3"""
        return self.freeboard_input * self.pit_surface_area  # m3 of rain


@dataclass
class ManureTreatmentConfig:
    """Class for storing manure treatment configuration data.

    Attributes:
        TS_removal_efficiency_for_treatment: Percent of total solids removed from manure during treatment.
        VS_removal_efficiency_for_treatment: Percent of volatile solids removed from manure during treatment.
        N_removal_efficiency_for_treatment: Percent of nitrogen removed from manure during treatment.
        TAN_removal_efficiency_for_treatment: Percent of total ammoniacal nitrogen removed from manure during treatment.
        P_removal_efficiency_for_treatment: Percent of phosphorus removed from manure during treatment.
        K_removal_efficiency_for_treatment: Percent of potassium removed from manure during treatment.

        hydraulic_retention_time: Time in days spent in the treatment system.
        sludge_accumulation_period: Time in days/years that sludge accumulates in the treatment system.
        SAV_fraction: Sludge Accumulation Volume (SAV) fraction based on the manure solids
            entering the treatment system.
        top_cover_volume_fraction: Fraction of the total volume of the treatment system
            that is assumed to be the top cover volume.
        biogas_gen_ratio: Amount of biogas generated from the treatment system.
        methane_gen_ratio: Amount of methane generated from the treatment system
            (calculated from the amount of biogas generated).
        evaporation_fraction: Fraction of the liquid portion evaporated from the treatment system.
        AD_temp_set_point: Temperature set point for the anaerobic digestion.
        AD_temp: Temperature of the anaerobic digestion.

        storage_time_period: Time in days that manure is stored in the treatment system.
        precip_input: Storage space for the amount of precipitation that falls onto the treatment system.
        freeboard_input: Empty storage space above the manure in the treatment system.

    """
    TS_removal_efficiency_for_treatment: float = 0.0
    VS_removal_efficiency_for_treatment: float = 0.0
    N_removal_efficiency_for_treatment: float = 0.0
    TAN_removal_efficiency_for_treatment: float = 0.0
    P_removal_efficiency_for_treatment: float = 0.0
    K_removal_efficiency_for_treatment: float = 0.0

    hydraulic_retention_time: int = 0
    sludge_accumulation_period: float = 0.0
    SAV_fraction: float = 0.0
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
            TS_removal_efficiency_for_treatment=0.1,  # Between 10-30%
            VS_removal_efficiency_for_treatment=0.20,  # Between 20-40%
            N_removal_efficiency_for_treatment=0.1,  # # Between 10-30%
            TAN_removal_efficiency_for_treatment=0.45,  # Between 61-80%
            P_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            K_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            storage_time_period=120.0,
    )

    SLURRY_STORAGE_OUTDOOR_CONFIG = ManureTreatmentConfig(
            TS_removal_efficiency_for_treatment=0.1,  # Between 10-30%
            VS_removal_efficiency_for_treatment=0.20,  # Between 20-40%
            N_removal_efficiency_for_treatment=0.1,  # # Between 10-30%
            TAN_removal_efficiency_for_treatment=0.45,  # Between 61-80%
            P_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            K_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            storage_time_period=120.0,
            precip_input=0.0,
            freeboard_input=0.3048
    )

    @classmethod
    def get_instance(cls, treatment_type: ManureTreatmentType) -> ManureTreatmentConfig:
        manure_treatment_config_by_type = {
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: cls.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: cls.SLURRY_STORAGE_OUTDOOR_CONFIG,
        }
        return manure_treatment_config_by_type[treatment_type]


class ManureTreatmentFactory:
    @staticmethod
    def get_instance(manure_treatment_type_name: str,
                     weather: Weather,
                     time: Time,
                     customer_manure_treatment_config: Optional[ManureTreatmentConfig] = None) \
            -> BaseManureTreatment:

        manure_treatment_class_by_type: Dict[ManureTreatmentType, Type[BaseManureTreatment]] = {
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: SlurryStorageUnderfloor,
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: SlurryStorageOutdoor,
        }

        manure_treatment_type = ManureTreatmentType.get_type(manure_treatment_type_name)
        manure_treatment_class = manure_treatment_class_by_type[manure_treatment_type]

        if customer_manure_treatment_config:
            return manure_treatment_class(weather, time, customer_manure_treatment_config)
        else:
            default_manure_treatment_config = DefaultManureTreatmentConfigFactory.get_instance(manure_treatment_type)
            return manure_treatment_class(weather, time, default_manure_treatment_config)
