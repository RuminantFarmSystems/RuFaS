"""
RUFAS: Ruminant Farm Systems Model

File name: base_treatment.py

Description: 

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
"""

#Constants
#water density in kg/m3
WATERDENSITY = 1000
DAYSINAYEAR = 365

class BaseTreatment:
    """
    Description
    ------------
    A class representing a base treatment in a manure treatment system

    Attributes
    ----------
    Attrbute _biogas: The biogas generated, hidden
    Invariant: Non negative float in units of m3

    Attribute biogas_eff: percentage of VS of manure corresponding to biogas
    Invariant: float >= 0.15, <= 0.38

    Attribute _digester_volume: Total Digester volume, hidden
    Invariant: float in units of m3. == mvt + sav + tcv

    Attribute hrt: Hydraulic retention time
    Invariant: int in units of days. 25 <= hrt <= 30

    Attribute k_loss_per: Percentage of potassium lost from manure
    Invariant: non negative float <= 0.05

    Attribute _manure: Manure in anaerobic digester, hidden
    Invariant: Manure object or none

    Attribute _methane: methane generated
    Invariant: Non negative float in units of m3

    Attribute methane_eff: percentage of biogas corresponding to methane
    Invariant: float >= 0.50, <= 0.65

    Attribute _mvt: Minimum volume treatment, hidden
    Invariant: Non negative float in units of m3, hidden

    Attribute n_loss_per: Percentage of nitrogen lost from manure
    Invariant: non negative float <= 0.05

    Attribute p_loss_per: Percentage of phosphorus lost from manure
    Invariant: non negative float <= 0.05

    Attribute sap: Sludge accumulation period
    Invariant: float in units of years. 1.0 <= sap <= 5.0 

    Attribute sar: Sludge accumulation ratio, the percentage of VS that 
                    corresponds with sav[see below] 
    Invariant: float. 0.02 <= sar <= 0.04

    Attribute _sav: Sludge accumulation volume 
    Invariant: float in units of m3

    Attribute tan_loss_per: Percentage of TAN lost from manure
    Invariant: float <= 0.05

    Attribute _tcv: Top cover volume, hidden
    Invariant: float in units of m3

    Attribute tcv_percent: Percentage of mvt corresponding to tcv
    Invariant: float >= 0.10 and <= 0.30

    Attribute ts_loss_per: Percentage of TS lost from manure
    Invariant: float >= 0.40 and <= 0.65 

    Attribute vs_loss_per: Percentage of VS lost from manure
    Invariant: float >= 0.30 and <= 0.40
    """

    def __init__(self, biogas_eff=0.38, hrt=25, k_loss_per=0.0,manure=None, 
                methane_eff=0.65, n_loss_per=0.0, p_loss_per=0.0, sap=1, 
                sar=0.01, tcv_percent=0.2, ts_loss_per=0.45, vs_loss_per=0.40):
        """
        Initializes a base treatment

        Parameter biogas_eff: percentage of VS of manure corresponding to biogas
        Precondition: float >= 0.15, <= 0.38

        Parameter hrt: Hydraulic retention time
        Precondition: int in units of days. 25 <= hrt <= 30

        Parameter k_loss_per: Percentage of potassium lost from manure
        Precondition: non negative float <= 0.05

        Parameter manure: Manure in anaerobic digester, hidden
        Precondition: Manure object or none

        Parameter methane_eff: percentage of biogas corresponding to methane
        Precondition: float >= 0.50, <= 0.65

        Parameter n_loss_per: Percentage of nitrogen lost from manure
        Precondition: non negative float <= 0.05

        Parameter p_loss_per: Percentage of phosphorus lost from manure
        Precondition: non negative float <= 0.05

        Parameter sap: Sludge accumulation period
        Precondition: float in units of years. 1.0 <= sap <= 5.0 

        Parameter sar: Sludge accumulation ratio, the percentage of VS that 
                        corresponds with sav
        Precondition: float. 0.02 <= sar <= 0.04

        Parameter tan_loss_per: Percentage of TAN lost from manure
        Precondition: float <= 0.05

        Parameter tcv_percent: Percentage of mvt corresponding to tcv
        Precondition: float >= 0.10 and <= 0.30

        Parameter ts_loss_per: Percentage of TS lost from manure
        Precondition: float >= 0.40 and <= 0.65 

        Parameter vs_loss_per: Percentage of VS lost from manure
        Precondition: float >= 0.30 and <= 0.40 
        """
        self.biogas_eff = biogas_eff
        self.hrt = hrt
        self.k_loss_per = k_loss_per
        self._manure = manure
        self.methane_eff = methane_eff
        self.n_loss_per = n_loss_per
        self.p_loss_per = p_loss_per
        self.sap = sap
        self.sar = sar
        self.tcv_percent = tcv_percent
        self.ts_loss_per = ts_loss_per
        self.vs_loss_per = vs_loss_per

        #Initializing hidden values to 0
        self._biogas = 0
        self._digester_volume = 0
        self._methane = 0
        self._mvt = 0
        self._sav = 0
        self._tcv = 0

        #Setting hidden values to correct values
        if self._manure:
            self._setManureDependentAtt()
            # self._setBiogas()
            # self._setMethae()
            # self._setMVT()
            # self._setSAV()
            # self._setTCV()
            # self._setDigestorVolume()

    def outputManure(self):
        """
        Returns the Manure in this Base Treatment and sets _manure to None
        """
        manure = self._manure
        self._manure = None
        return manure

    #hidden methods
    def _updateManure(self):
        """
        Accounts for the losses in the attributes of the manure in this 
        Base Treatment

        Precondition: self._manure is a Manure object
        """
        manure = self._manure
        ts = manure.getTS() * (1-self.ts_loss_per)
        vs = manure.getVS() * (1-self.vs_loss_per)
        tan = manure.getTAN() * (1-self.tan_loss_per)
        n = manure.getN() * (1-self.n_loss_per)
        p = manure.getP() * (1-self.p_loss_per)
        k = manure.getK() * (1-self.k_loss_per)

        manure.setTS(ts)
        manure.setVS(vs)
        manure.setTAN(tan)
        manure.setN(n)
        manure.setP(p)
        manure.setK(k)
        

    def _setManureDependentAtt(self):
        """
        Sets the manure dependent attributes of the Base Treatment to their 
        correct values.

        Precondition: self._manure is a Manure object.
        """
        manure = self._manure
        vs = manure.getVS()
        self._biogas += self.biogas_eff * vs
        self._methane += self.methane_eff * self._biogas
        self._mvt += manure.getTWV() * hrt
        self._sav += vs * self.sar * self.sap * DAYSINAYEAR / WATERDENSITY
        self._tcv += self._mvt * self.tcv_percent
        self._digester_volume += self._mvt + self._tcv + self._sav
        

    
    # def __init__(self, treatment_data, next_treatment):
    #     self.next_treatment = next_treatment
    #     if treatment_data is None or treatment_data['default']:
    #         self.default = True
    #         self.set_defaults()
    #     else:
    #         self.methane_generation_percent = treatment_data['methane_generation_percent']
    #         self.biogas_generation_percent = treatment_data['biogas_generation_percent']
    #         self.top_cover_volume = treatment_data['top_cover_volume']
    #         self.hrt = treatment_data['hrt']
    #         self.sludge_accumulation_rate = treatment_data['sludge_accumulation_rate']
    #         self.sludge_accumulation_period = treatment_data['sludge_accumulation_period']

    # def set_defaults(self):
    #     pass
