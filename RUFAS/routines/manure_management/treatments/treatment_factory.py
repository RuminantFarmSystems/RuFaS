from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.base_separator import BaseSeparator
from RUFAS.routines.manure_management.treatments.treatment_classes.anaerobic_digestion import \
    AnaerobicDigestion
from RUFAS.routines.manure_management.treatments.treatment_classes.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure_management.treatments.treatment_classes.base_treatment import BaseTreatment
from RUFAS.routines.manure_management.treatments.treatment_classes.custom_treatment import CustomTreatment
from RUFAS.routines.manure_management.treatments.treatment_enum import TreatmentEnum
from RUFAS.routines.manure_management.treatments.treatment_init_data import TreatmentInitData
from RUFAS.routines.manure_management.treatments.treatment_classes.storage_pond import StoragePond


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
            'treatment_init_data': cls.get_treatment_init_data(treatment_enum)
        }
        enum_to_class = {
            treatment_enum.STORAGE_POND: StoragePond,
            treatment_enum.ANAEROBIC_LAGOON: AnaerobicLagoon,
            treatment_enum.ANAEROBIC_DIGESTION: AnaerobicDigestion,
            treatment_enum.CUSTOM_STORAGE: CustomTreatment
        }
        return enum_to_class[treatment_enum](**params)

    @classmethod
    def get_treatment_init_data(cls, treatment_enum: TreatmentEnum) -> TreatmentInitData:
        init_data = TreatmentInitData()

        # Customize init data here based on enum if necessary
        # ...

        return init_data
