from dataclasses import dataclass

from RUFAS.routines.manure.enums.ManureCoverEnum import ManureCoverEnum
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)


@dataclass
class ManureTreatmentConfig:
    """Class for storing manure treatment configuration data.

    Attribute
    ---------
    manure_treatment_type : ManureTreatmentType
        The type of manure treatment that will be created with this configuration.
    total_solids_removal_efficiency_for_treatment:
        Percent of total solids removed from manure during treatment.
    volatile_solids_removal_efficiency_for_treatment:
        Percent of volatile solids removed from manure during treatment.
    nitrogen_removal_efficiency_for_treatment:
        Percent of nitrogen removed from manure during treatment.
    total_ammoniacal_nitrogen_removal_efficiency_for_treatment:
        Percent of total ammoniacal nitrogen removed from manure during treatment.
    phosphorus_removal_efficiency_for_treatment:
        Percent of phosphorus removed from manure during treatment.
    potassium_removal_efficiency_for_treatment:
        Percent of potassium removed from manure during treatment.
    hydraulic_retention_time:
        Time in days spent in the treatment system.
    sludge_accumulation_period:
        Time in days/years that sludge accumulates in the treatment system.
    sludge_accumulation_volume_fraction:
        Sludge Accumulation Volume (SAV) fraction based on the manure solids entering the treatment system.
    top_cover_volume_fraction:
        Fraction of the total volume of the treatment system that is assumed to be the top cover volume.
    evaporation_fraction:
        Fraction of the liquid portion evaporated from the treatment system.
    anaerobic_digestion_temperature_set_point:
        Temperature set point for the anaerobic digestion.
    anaerobic_digestion_temperature_celsius:
        Temperature of the anaerobic digestion.
    storage_time_period:
        Time in days that manure is stored in the treatment system.
    freeboard_input:
        Empty storage space above the manure in the treatment system.
    composting_type: str
        The type of composting.
    last_compost_turning_or_addition:
        Number of days since last compot turning or addition activity.
    manure_cover: str
        Indicates the presence or absence of a cover in the manure treatment or storage system.
        When used in the case of a slurry storage system (underfloor or outdoors) the manure cover
        refers to the presence of a natural crust.

    """

    manure_treatment_type: ManureTreatmentType

    total_solids_removal_efficiency_for_treatment: float = 0.0
    volatile_solids_removal_efficiency_for_treatment: float = 0.0
    nitrogen_removal_efficiency_for_treatment: float = 0.0
    total_ammoniacal_nitrogen_removal_efficiency_for_treatment: float = 0.0
    phosphorus_removal_efficiency_for_treatment: float = 0.0
    potassium_removal_efficiency_for_treatment: float = 0.0

    hydraulic_retention_time: int = 0
    sludge_accumulation_period: float = 0.0
    sludge_accumulation_volume_fraction: float = 0.0
    top_cover_volume_fraction: float = 0.0

    evaporation_fraction: float = 0.0
    anaerobic_digestion_temperature_set_point: float = 0.0
    anaerobic_digestion_temperature_celsius: float = 0.0

    storage_time_period: int = 0
    freeboard_input: float = 0.0

    composting_type: str = "intensive windrow"
    last_compost_turning_or_addition: int = 1
    manure_cover: str = ManureCoverEnum.NO_COVER.value
