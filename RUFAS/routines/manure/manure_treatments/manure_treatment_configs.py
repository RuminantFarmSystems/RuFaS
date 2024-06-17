from dataclasses import dataclass
from typing import Union, Tuple

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


class DefaultManureTreatmentConfigFactory:
    """Class for creating default manure treatment configuration data."""

    SLURRY_STORAGE_UNDERFLOOR_CONFIG = ManureTreatmentConfig(
        total_solids_removal_efficiency_for_treatment=0.0,  # Previously set between 10-30%
        volatile_solids_removal_efficiency_for_treatment=0.20,  # Between 20-40%
        nitrogen_removal_efficiency_for_treatment=0.10,  # # Between 10-30%
        total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.45,  # Between 61-80%
        phosphorus_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
        potassium_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
        storage_time_period=120,
        manure_cover=ManureCoverEnum.CRUST.value,
    )

    SLURRY_STORAGE_OUTDOOR_CONFIG = ManureTreatmentConfig(
        total_solids_removal_efficiency_for_treatment=0.0,  # Previously set between 10-30%
        volatile_solids_removal_efficiency_for_treatment=0.20,  # Between 20-40%
        nitrogen_removal_efficiency_for_treatment=0.10,  # # Between 10-30%
        total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.45,  # Between 61-80%
        phosphorus_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
        potassium_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
        storage_time_period=120,
        freeboard_input=0.3048,
        manure_cover=ManureCoverEnum.CRUST.value,
    )

    ANAEROBIC_DIGESTION_CONFIG = ManureTreatmentConfig(
        total_solids_removal_efficiency_for_treatment=0.45,
        volatile_solids_removal_efficiency_for_treatment=0.40,
        nitrogen_removal_efficiency_for_treatment=0.0,  # 0-5% N fraction
        phosphorus_removal_efficiency_for_treatment=0.0,  # 0-5% P fraction
        potassium_removal_efficiency_for_treatment=0.0,  # 0-5% K fraction
        total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.1,
        hydraulic_retention_time=25,  # 25 -30 days
        sludge_accumulation_period=1.0,  # Sludge accumulation period 1-5 years
        sludge_accumulation_volume_fraction=0.0,  # Previous Sludge Accumulation volume fraction 2-4% of VS loaded
        top_cover_volume_fraction=0.2,  # Should be between 10-30%
        evaporation_fraction=0.02,  # 2-5% of Wastewater Volume
        anaerobic_digestion_temperature_set_point=37.5,
        anaerobic_digestion_temperature_celsius=37.5,
        manure_cover=ManureCoverEnum.NOT_APPLICABLE.value,
    )

    ANAEROBIC_LAGOON_CONFIG = ManureTreatmentConfig(
        total_solids_removal_efficiency_for_treatment=0.75,  # Between 70-85%
        volatile_solids_removal_efficiency_for_treatment=0.85,  # Between 80-90%
        nitrogen_removal_efficiency_for_treatment=0.65,  # Between 60-80%
        total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.7,  # Between 61-80%
        phosphorus_removal_efficiency_for_treatment=0.6,  # Between 60-70%
        potassium_removal_efficiency_for_treatment=0.2,  # Between 20-30%
        hydraulic_retention_time=365,  # 180 - 365 days
        sludge_accumulation_period=10.0,  # Sludge accumulation period 5-20 years
        sludge_accumulation_volume_fraction=0.0,
        # Sludge Accumulation volume fraction 0.00274-0.00455 of VS loaded
        storage_time_period=365,
        freeboard_input=0.3048,
        manure_cover=ManureCoverEnum.NO_COVER.value,
    )

    COMPOST_BEDDED_PACK_BARN_CONFIG = ManureTreatmentConfig()
    OPEN_LOTS_CONFIG = ManureTreatmentConfig()
    COMPOSTING_CONFIG = ManureTreatmentConfig()

    @classmethod
    def get_instance(
        cls, treatment_type: ManureTreatmentType
    ) -> Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]]:
        """Return a default manure treatment configuration data instance for the given treatment type.

        Args:
            treatment_type: The type of manure treatment.

        Returns:
            A default manure treatment configuration data instance for the given treatment type.

        """
        manure_treatment_config_by_type = {
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: cls.SLURRY_STORAGE_UNDERFLOOR_CONFIG,
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: cls.SLURRY_STORAGE_OUTDOOR_CONFIG,
            ManureTreatmentType.ANAEROBIC_DIGESTION: cls.ANAEROBIC_DIGESTION_CONFIG,
            ManureTreatmentType.ANAEROBIC_LAGOON: cls.ANAEROBIC_LAGOON_CONFIG,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON: (
                cls.ANAEROBIC_DIGESTION_CONFIG,
                cls.ANAEROBIC_LAGOON_CONFIG,
            ),
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR: (
                cls.ANAEROBIC_DIGESTION_CONFIG,
                cls.ANAEROBIC_LAGOON_CONFIG,
            ),
            ManureTreatmentType.COMPOST_BEDDED_PACK_BARN: cls.COMPOST_BEDDED_PACK_BARN_CONFIG,
            ManureTreatmentType.OPEN_LOTS: cls.OPEN_LOTS_CONFIG,
            ManureTreatmentType.COMPOSTING: cls.COMPOSTING_CONFIG,
        }
        return manure_treatment_config_by_type[treatment_type]
