from .base_treatment import BaseTreatment


class CustomTreatment(BaseTreatment):
    def __init__(self, pen, treatment_init_data):
        super().__init__(pen, treatment_init_data)
