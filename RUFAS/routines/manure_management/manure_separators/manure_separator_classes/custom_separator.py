from .base_separator import BaseSeparator
from ..manure_separator_init_data import ManureSeparatorInitData
from ...data_models.simple_pen import SimplePen
from ...treatments.treatment_classes.base_treatment import BaseTreatment


class CustomSeparator(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 treatment: BaseTreatment,
                 separator_data: ManureSeparatorInitData):
        super().__init__(pen, treatment, separator_data)
