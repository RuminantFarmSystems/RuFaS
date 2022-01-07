from .base_treatment import BaseTreatment


class NullTreatment(BaseTreatment):
    def __init__(self, storage, treatment='null_treatment', treatment_data=None):
        if treatment_data is None:
            treatment_data = {
                'methane_generation_percent': 0,
                'biogas_generation_percent': 0,
                'top_cover_volume': 0,
                'sludge_accumulation_rate': 0,
                'sludge_accumulation_period': 0
            }
        super().__init__(treatment, treatment_data, storage)

    def update_all(self):
        # TODO: this will need to be updated when improvements are made to the base treatment class.
        super(NullTreatment, self).update_all()
