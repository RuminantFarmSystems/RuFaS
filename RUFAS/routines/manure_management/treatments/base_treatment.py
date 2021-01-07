"""
RUFAS: Ruminant Farm Systems Model

File name: base_treatment.py

Description: 

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
"""



class BaseTreatment:
    """
    Description
    ------------


    Attributes
    ----------

    """
    
    def __init__(self, treatment_data, next_treatment):
        self.next_treatment = next_treatment
        if treatment_data is None or treatment_data['default']:
            self.default = True
            self.set_defaults()
        else:
            self.methane_generation_percent = treatment_data['methane_generation_percent']
            self.biogas_generation_percent = treatment_data['biogas_generation_percent']
            self.top_cover_volume = treatment_data['top_cover_volume']
            self.hrt = treatment_data['hrt']
            self.sludge_accumulation_rate = treatment_data['sludge_accumulation_rate']
            self.sludge_accumulation_period = treatment_data['sludge_accumulation_period']

    def set_defaults(self):
        pass
