from .base_treatment import BaseTreatment


class CustomTreatment(BaseTreatment):
    def __init__(self, treatment, treatment_data, storage):
        super().__init__(treatment, treatment_data, storage)
