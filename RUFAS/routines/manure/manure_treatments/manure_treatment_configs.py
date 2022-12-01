from __future__ import annotations
from __future__ import annotations

from dataclasses import dataclass

from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType


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

    storage_time_period: int = 0
    freeboard_input: float = 0.0


class DefaultManureTreatmentConfigFactory:
    """Class for creating default manure treatment configuration data."""

    SLURRY_STORAGE_UNDERFLOOR_CONFIG = ManureTreatmentConfig(
            TS_removal_efficiency_for_treatment=0.10,  # Between 10-30%
            VS_removal_efficiency_for_treatment=0.20,  # Between 20-40%
            N_removal_efficiency_for_treatment=0.10,  # # Between 10-30%
            TAN_removal_efficiency_for_treatment=0.45,  # Between 61-80%
            P_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            K_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            storage_time_period=120,
    )

    SLURRY_STORAGE_OUTDOOR_CONFIG = ManureTreatmentConfig(
            TS_removal_efficiency_for_treatment=0.10,  # Between 10-30%
            VS_removal_efficiency_for_treatment=0.20,  # Between 20-40%
            N_removal_efficiency_for_treatment=0.10,  # # Between 10-30%
            TAN_removal_efficiency_for_treatment=0.45,  # Between 61-80%
            P_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            K_removal_efficiency_for_treatment=0.05,  # # Between 5-30%
            storage_time_period=120,
            freeboard_input=0.3048
    )

    ANAEROBIC_DIGESTION_CONFIG = ManureTreatmentConfig(
            TS_removal_efficiency_for_treatment=0.45,
            VS_removal_efficiency_for_treatment=0.40,
            N_removal_efficiency_for_treatment=0.0,  # 0-5% N fraction
            P_removal_efficiency_for_treatment=0.0,  # 0-5% P fraction
            K_removal_efficiency_for_treatment=0.0,  # 0-5% K fraction
            TAN_removal_efficiency_for_treatment=0.1,

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

            TS_removal_efficiency_for_treatment=0.75,  # Between 70-85%
            VS_removal_efficiency_for_treatment=0.85,  # Between 80-90%
            N_removal_efficiency_for_treatment=0.65,  # Between 60-80%
            TAN_removal_efficiency_for_treatment=0.7,  # Between 61-80%
            P_removal_efficiency_for_treatment=0.6,  # Between 60-70%
            K_removal_efficiency_for_treatment=0.2,  # Between 20-30%
            storage_time_period=365,
            freeboard_input=0.3048
    )

    ANAEROBIC_DIGESTION_AND_LAGOON_CONFIG = ManureTreatmentConfig(
            TS_removal_efficiency_for_treatment=0.45,
            VS_removal_efficiency_for_treatment=0.40,
            N_removal_efficiency_for_treatment=0.0,
            TAN_removal_efficiency_for_treatment=0.1,
            P_removal_efficiency_for_treatment=0.0,
            K_removal_efficiency_for_treatment=0.0,
            storage_time_period=365,
            freeboard_input=0.3048,
            hydraulic_retention_time=25,
            sludge_accumulation_period=1.0,
            SAV_fraction=0.03,
            top_cover_volume_fraction=0.2,
            biogas_gen_ratio=0.38,
            methane_gen_ratio=0.65,
            evaporation_fraction=0.02,
            AD_temp_set_point=37.5,
            AD_temp=37.5
    )

    @classmethod
    def get_instance(cls, treatment_type: ManureTreatmentType) -> ManureTreatmentConfig:
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
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON: cls.ANAEROBIC_DIGESTION_AND_LAGOON_CONFIG,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT: cls.ANAEROBIC_DIGESTION_AND_LAGOON_CONFIG
        }
        return manure_treatment_config_by_type[treatment_type]
