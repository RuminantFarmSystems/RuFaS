from typing import Dict, Tuple, Type, Union

from RUFAS.routines.manure.manure_treatments.anaerobic_digestion import AnaerobicDigestion
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon import AnaerobicDigestionAndLagoon
from RUFAS.routines.manure.manure_treatments.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn import CompostBeddedPackBarn
from RUFAS.routines.manure.manure_treatments.composting import Composting
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.routines.manure.manure_treatments.open_lots import OpenLots
from RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor import SlurryStorageUnderfloor
from RUFAS.time import Time
from RUFAS.weather import Weather


class ManureTreatmentFactory:
    """Class for creating different types of manure treatment systems."""

    @staticmethod
    def get_instance(
        configuration_name: str,
        weather: Weather,
        time: Time,
        manure_treatment_config: Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]],
    ) -> BaseManureTreatment:
        """Returns a manure treatment system instance for the given manure treatment type name.

        Parameters
        ----------
        configuration_name : str
            The name of the manure treatment configuration.
        weather : Weather
            The weather data.
        time : Time
            The time data.
        manure_treatment_config : Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]]
            The manure treatment configuration data.

        Returns
        -------
        BaseManureTreatment
            A manure treatment system instance for the given manure treatment type name.

        """

        manure_treatment_class_by_type: Dict[ManureTreatmentType, Type[BaseManureTreatment]] = {
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: SlurryStorageUnderfloor,
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: SlurryStorageOutdoor,
            ManureTreatmentType.ANAEROBIC_LAGOON: AnaerobicLagoon,
            ManureTreatmentType.ANAEROBIC_DIGESTION: AnaerobicDigestion,
            ManureTreatmentType.COMPOST_BEDDED_PACK_BARN: CompostBeddedPackBarn,
            ManureTreatmentType.OPEN_LOTS: OpenLots,
            ManureTreatmentType.COMPOSTING: Composting,
        }

        treatment_storage_combinations = {
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON.value,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR.value,
        }
        if configuration_name in treatment_storage_combinations:
            manure_treatment_class = AnaerobicDigestionAndLagoon
        else:
            manure_treatment_class = manure_treatment_class_by_type[manure_treatment_config.manure_treatment_type]

        manure_treatment_obj = manure_treatment_class(weather, time, manure_treatment_config)

        return manure_treatment_obj
