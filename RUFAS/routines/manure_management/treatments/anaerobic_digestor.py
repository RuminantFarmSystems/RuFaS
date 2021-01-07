from .base_treatment import BaseTreatment


class AnaerobicDigestor(BaseTreatment):
    def __init__(self, treatment_data, next_treatment):
        super().__init__(treatment_data, next_treatment)
        if self.default: self.set_defaults()

    def set_defaults(self):
        self.methane_generation_percent = 0.575
        self.biogas_generation_percent = 0.265
        self.top_cover_volume = 0.2
        self.hrt = 25
        self.sludge_accumulation_rate = 0.03
        self.sludge_accumulation_period = 3
