"""
RUFAS: Ruminant Farm Systems Model

File name: sand_separator.py

Description: This Module contains the implementation of the base SandSeparator 
class. The main function of the SandSeparator is to remove sand from manure, and 
the SandSeparator has a method, separateSand() which does that.

Author(s): Yunus Mohammed, ymm26@cornell.edu
"""

from ..materials.bedding import *

class SandSeparator():
    """
    Description
    ------------
    An instance of SandSeparator has a method separateSand() which removes sand 
    present in this SandSeparator. It also has two resetters- resetSeparator and 
    resetSand. See their implementations below for description. Each instance 
    has the following attributes and the corresponding invariants, getters, and 
    setters. 

    Attributes
    ----------
    Attribute _manure: The manure held in the SanSeparator
    invariant: _manure must be a Manure Object or None.

    Attribute _sand: The sand that has been removed from Manure.
    Invariant: _sand must be a SandBedding Object or None

    Attribute _sand_removal_efficiency: The fraction of sand removed from Manure 
    in each separation cycle. 
    Invariant: A flaot >=0.6 and <=0.9
    """

    def __init__(self,efficiency=0.9,manure=None,sand=SandBedding(0.0)):
        """
        Initializes a SandSeparator

        Parameter efficiency: the sand separation efficiency
        Precondition: float >=0.6 and <=0.9

        Parameter manure: The manure held in this SandSeparator
        Precondition: Manure Object or None

        Parameter sand: The sand present in this SandSeparator
        Precondition: Must be a SandBedding Object
        """
        self._manure = manure
        self._sand = sand
        self._sand_removal_efficiency = efficiency


    def output(self):
        """
        Returns the Manure _manure in this Separator and resets _manure to None.

        Return type: Manure or None
        """
        manure = self._manure
        self._manure = None
        return manure

    def separateSand(self):
        """
        Does one cycle of sand separation on the manure present
        """
        if not self._manure:  #Max
            return
        
        sand = self._manure.getBedding()

        separated_sand_mass = self._sand_removal_efficiency * sand.getMass()
        remaining_sand_mass = sand.getMass() - separated_sand_mass

        self._sand.setMass(separated_sand_mass)
        sand.setMass(remaining_sand_mass)


    #getters 
    def getEfficiency(self):
        """
        Returns the effiency of this SandSeparator
        """
        return self._sand_removal_efficiency

    def getManure(self):
        """
        Returns the manure in this SandSeparator
        """
        return self._manure
    
    def getSand(self):
        """
        Returns the Sand in this SandSeparator
        """
        return self._sand

    #resetters
    def resetSeparator(self):
        """
        Reset the _sand to None and _sand to 0 mass SandBedding
        """
        self._manure = None
        self.resetSand()

    def resetSand(self):
        """
        Reset Sand to 0 mass SandBedding
        """
        self._sand.setMass(0.0)

    #setters
    def setEfficiency(self, efficiency):
        """
        Sets _efficiency to efficiency
        
        Parameter efficiency: The new efficiency of the SandSeparator
        Precondition: float >=0.6 and <=0.9
        """
        self._sand_removal_efficiency = efficiency

    def setManure(self, manure=None):
        """
        Sets _manure to manure

        Parameter manure: The new manure held by this SandSeparator. 
        Precondition: manure must be distinct from _manure. 
        manure.getBedding() must return a SandBedding.
        """
        assert manure != self._manure, "The Manure is already in this SandSepearator. Use a different Manure object"
        if self._manure and manure:
            self._manure.aggregateManure(manure)
        else:
            self._manure = manure

    

   
        

    
    # def __init__(self, treatment_data, pen):
    #     super().__init__(treatment_data, pen)
    #     if self.default: self.set_defaults()

    # def set_defaults(self):
    #     self.TS_removal_efficiency = 0.3
    #     self.VS_removal_efficiency = 0.55
    #     self.N_removal_efficiency = 0.3
    #     self.P_removal_efficiency = 0.4
    #     self.K_removal_efficiency = 0.15
    #     self.TS_DM_effluent_rate = 0.2
