"""
RUFAS: Ruminant Farm Systems Model

File name: anaerobic_digester.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
"""


from .base_treatment import BaseTreatment

#Constants
#water density in kg/m3
WATERDENSITY = 1000
DAYSINAYEAR = 365

class AnaerobicDigester(BaseTreatment):
    """
    Description
    ------------
    A class representing an anaerobic digestor in a manure treatment system

    Attributes
    ----------
    Attrbute _biogas: The biogas generated, hidden
    Invariant: Non negative float in units of m3

    Attribute biogas_eff: percentage of VS corresponding to biogas
    Invariant: float >= 0.15, <= 0.38

    Attribute hrt: Hydraulic retention time
    Invariant: int in units of days. 25 <= hrt <= 30

    Attribute _manure: Manure in anaerobic digester, hidden
    Invariant: Manure object or none

    Attribute _methane: methane generated
    Invariant: Non negative float in units of m3

    Attribute methane_eff: percentage of biogas corresponding to methane
    Invariant: float >= 0.50, <= 0.65

    Attribute _mvt: Minimum volume treatment, hidden
    Invariant: Non negative float in units of m3, hidden

    Attribute sap: Sludge accumulation period
    Invariant: float in units of years. 1.0 <= sap <= 5.0 

    Attribute sar: Sludge accumulation ratio, the percentage of VS that 
                    corresponds with sav[see below] 
    Invariant: float. 0.02 <= sar <= 0.04

    Attribute _sav: Sludge accumulation volume 
    Invariant: float in units of m3

    Attribute _tcv: Top cover volume, hidden
    Invariant: float in units of m3

    Attrbute tcv_percent: Percentage of mvt corresponding to tcv
    Invariant: float >= 0.1 and <= 0.3

    Attribute _digester_volume: Total Digester volume, hidden
    Invariant: float in units of m3. == mvt + sav + tcv
    """

    def __init__(self):
        super().__init__()
        
    
    # def __init__(self, treatment_data, next_treatment):
    #     super().__init__(treatment_data, next_treatment)
    #     if self.default: self.set_defaults()

    # def set_defaults(self):
    #     self.methane_generation_percent = 0.575
    #     self.biogas_generation_percent = 0.265
    #     self.top_cover_volume = 0.2
    #     self.hrt = 25
    #     self.sludge_accumulation_rate = 0.03
    #     self.sludge_accumulation_period = 3




# consider adding as attribute...
# Attribute vslr: Volatile solid loading rate
#     Invariant: float in units of kg/m3. ==  manure.getVS()/digester_volume if
#     manure != None, 0 otherwise.