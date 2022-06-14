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
    
    def __init__(self, treatment, treatment_data, storage):
        self.treatment_name = treatment
        self.storage = storage

        self.methane_generation_percent = treatment_data['methane_generation_percent'] if \
            'methane_generation_percent' in treatment_data else 0.575
        self.biogas_generation_percent = treatment_data['biogas_generation_percent'] if \
            'biogas_generation_percent' in treatment_data else 0.265
        self.top_cover_volume = treatment_data['top_cover_volume'] if \
            'top_cover_volume' in treatment_data else 0.2
        self.hrt = treatment_data['hrt'] if 'hrt' in treatment_data else 25
        self.sludge_accumulation_rate = treatment_data['sludge_accumulation_rate'] if \
            'sludge_accumulation_rate' in treatment_data else 0.03
        self.sludge_accumulation_period = treatment_data['sludge_accumulation_period'] if \
            'sludge_accumulation_period' in treatment_data else 3

        self.TS = 0
        self.TS_liquid = 0
        self.VS = 0
        self.VS_liquid = 0
        self.N = 0
        self.N_liquid = 0
        self.P = 0
        self.P_liquid = 0
        self.K = 0
        self.K_liquid = 0
        self.CH4 = 0
        self.WIP = 0
        self.WOP = 0

    def reset_daily_variables(self):
        self.TS = 0
        self.TS_liquid = 0
        self.VS = 0
        self.VS_liquid = 0
        self.N = 0
        self.N_liquid = 0
        self.P = 0
        self.P_liquid = 0
        self.K = 0
        self.K_liquid = 0
        self.CH4 = 0
        self.WIP = 0
        self.WOP = 0

    def reset_annual_variables(self):
        pass

    def update_all(self):
        self.effluent_solids()
        self.N_effluent()
        self.P_effluent()
        self.K_effluent()
        self.CH4_effluent()
        self.WIP_WOP()

    def effluent_solids(self):
        self.storage.TS += self.TS
        self.storage.TS_liquid += self.TS_liquid
        self.storage.VS += self.VS
        self.storage.VS_liquid += self.VS_liquid

    def N_effluent(self):
        self.storage.N += self.N
        self.storage.N_liquid += self.N_liquid

    def P_effluent(self):
        self.storage.P += self.P
        self.storage.P_liquid += self.P_liquid

    def K_effluent(self):
        self.storage.K += self.K
        self.storage.K_liquid += self.K_liquid

    def CH4_effluent(self):
        self.storage.CH4 += self.CH4

    def WIP_WOP(self):
        self.storage.WIP += self.WIP
        self.storage.WOP += self.WOP
