from .base_separator import BaseSeparator


class NullSeparator(BaseSeparator):
    def __init__(self,  treatment, separator='null_separator', separator_data=None):
        if separator_data is None:
            separator_data = {
                'TS_removal_efficiency': 0,
                'VS_removal_efficiency': 0,
                'N_removal_efficiency': 0,
                'P_removal_efficiency': 0,
                'K_removal_efficiency': 0,
                'TS_DM_effluent_rate': 0
            }
        super().__init__(separator, separator_data, treatment)

    def update_all(self):
        super().update_treatment()
