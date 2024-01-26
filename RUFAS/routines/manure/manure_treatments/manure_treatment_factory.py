from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from RUFAS.routines.manure.manure_treatments.anaerobic_digestion import (
    AnaerobicDigestion,
)
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon import (
    AnaerobicDigestionAndLagoon,
)
from RUFAS.routines.manure.manure_treatments.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.composting import Composting
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    DefaultManureTreatmentConfigFactory,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    ManureTreatmentConfig,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)
from RUFAS.routines.manure.manure_treatments.open_lots import OpenLots
from RUFAS.routines.manure.manure_treatments.slurry_storage_outdoor import (
    SlurryStorageOutdoor,
)
from RUFAS.routines.manure.manure_treatments.slurry_storage_underfloor import (
    SlurryStorageUnderfloor,
)
from RUFAS.routines.manure.manure_treatments.compost_bedded_pack_barn import (
    CompostBeddedPackBarn,
)


class ManureTreatmentFactory:
    """Class for creating different types of manure treatment systems."""

    @staticmethod
    def get_instance(
        manure_treatment_type_name: str,
        weather,
        time,
        custom_manure_treatment_config: Optional[
            Union[
                ManureTreatmentConfig,
                Tuple[ManureTreatmentConfig, ManureTreatmentConfig],
            ]
        ] = None,
    ) -> BaseManureTreatment:
        """Returns a manure treatment system instance for the given manure treatment type name.

        Args:
            manure_treatment_type_name: The name of the manure treatment type.
            weather: The weather data.
            time: The time data.
            custom_manure_treatment_config: The custom manure treatment configuration data.

        Returns:
            A manure treatment system instance for the given manure treatment type name.

        """

        manure_treatment_class_by_type: Dict[
            ManureTreatmentType, Type[BaseManureTreatment]
        ] = {
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: SlurryStorageUnderfloor,
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: SlurryStorageOutdoor,
            ManureTreatmentType.ANAEROBIC_LAGOON: AnaerobicLagoon,
            ManureTreatmentType.ANAEROBIC_DIGESTION: AnaerobicDigestion,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON: AnaerobicDigestionAndLagoon,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT: AnaerobicDigestionAndLagoon,
            ManureTreatmentType.COMPOST_BEDDED_PACK_BARN: CompostBeddedPackBarn,
            ManureTreatmentType.OPEN_LOTS: OpenLots,
            ManureTreatmentType.COMPOSTING: Composting
        }

        manure_treatment_type = ManureTreatmentType.get_type(manure_treatment_type_name)
        manure_treatment_class = manure_treatment_class_by_type[manure_treatment_type]

        if custom_manure_treatment_config:
            manure_treatment_obj = manure_treatment_class(
                weather, time, custom_manure_treatment_config
            )
        else:
            default_manure_treatment_config = (
                DefaultManureTreatmentConfigFactory.get_instance(manure_treatment_type)
            )
            manure_treatment_obj = manure_treatment_class(
                weather, time, default_manure_treatment_config
            )

        return manure_treatment_obj
