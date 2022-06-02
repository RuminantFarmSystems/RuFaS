from .base_treatment import BaseTreatment
from ..treatment_init_data import TreatmentInitData
from ...data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import BaseManureHandler
from ...manure_separators.manure_separator_classes.base_separator import BaseSeparator


class CustomTreatment(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)
