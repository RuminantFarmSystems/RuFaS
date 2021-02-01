"""
RUFAS: Ruminant Farm Systems Model

File name: manure.py

Description: This module contains the implementation of the Manure class with 
all the getters and setters of attributes of an instance of Manure. 

Author(s): Yunus Mohammed, ymm26@cornell.edu
"""

from .bedding import OrganicBedding


class Manure:
    """
    Description
    ------------
    An instance of Manure represents gathered or aggregated manure in any given 
    component.

    Attributes
    ----------
    Attribute _bedding: The bedding material in this manure
    Invariant: Must be an instance of Bedding

    Attribute _K: Total Potassium (K2O) present
    Invariant: Non negative float in units of kg

    Attribute _N: Total nitrogen contained in this manure object
    Invariant: Non negative float in units of kg

    Attribute _P: Total Phosphorus (inorganic P2O5) present 
    Invariant: Non negative float in units of kg

    Attribute _RFW: Recycled flush water
    Invariant: Non negative float in units of m3

    Attribute _TAN: Total Ammoniacal Nitrogen contained in this manure object
    Invariant: Non negative float in units of kg

    Attribute _TS: The total solids in this manure object
    Invariant: Non negative float in units of kg

    Attribute _TWV: The total waste volume of the manure
    Invariant: Non negative float in units of m^3

    Attribute _VS: Total volatile solids contained in this manure object
    Invariant: Non negative float in units of kg
    """   

    def __init__(self, bedding, k=0, n=0, p=0, rfw=0, tan=0, ts=0, twv=0, vs=0):
        """
        Description: initializes a Manure object.

        Parameter bedding: The bedding material
        Parameter k : the mass of potassium
        Parameter n: the mass of nitrogen
        Parameter p: the mass of potassium
        Parameter rfw: volume of the recycled flush water
        Parameter tan: the mass of total ammoniacal nitrogen

        Parameter twv: the total waste volume
        Invariant: != 0 if any of k, n, p, tan, ts, vs != 0

        Parameter vs: the total mass of volatile solids

        Preconditions: the values of the parameters should make corresponding 
        invariants true 
        """
        self._bedding = bedding
        self._K = k
        self._N = n
        self._P = p
        self._RFW = rfw
        self._TAN = tan
        self._TS = ts
        self._TWV = twv
        self._VS = vs
    
    def aggregateManure(self, other):
        """
        Aggregates this manure object with another manure object, other.

        Parameter other: The manure object being added to this manure object
        Precondition: other is a manure object
        """
        self._K += other._K
        self._N += other._N
        self._P += other._P
        self._TAN += other._TAN
        self._TS += other._TS
        self._TWV += other._TWV
        self._VS += other._VS

        #Aggregating the bedding material
        if isinstance(self._bedding, OrganicBedding) and not isinstance(other._bedding, OrganicBedding):
            other._bedding.aggregateBedding(self._bedding)
            self._bedding = other._bedding
        else:
            self._bedding.aggregateBedding(other._bedding)



    #Getters
    def getBedding(self):
        """
        Returns _bedding in this Manure
        """
        return self._bedding

    def getK(self):
        """
        Returns the value of _K 
        """
        return self._K

    def getKconc(self):
        """
        Returns the concentration of potassium in units of g/L (kg/m3)
        """
        if not self._K:
            return 0
        else:
            return self._K / self._TWV


    def getN(self):
        """
        Returns the value of _N
        """
        return self._N 

    def getNconc(self):
        """
        Returns the concentration of nitrogen in units of g/L (kg/m3)
        """
        if not self._N:
            return 0
        else:
            return self._N / self._TWV

    def getP(self):
        """
        Returns the value of _P to p
        """
        return self._P 

    def getPconc(self):
        """
        Returns the concentration of phosphorus in units of g/L (kg/m3)
        """
        if not self._P:
            return 0
        else:
            return self._P / self._TWV

    def getRFW(self):
        """
        Returns the flush water volume of this manure
        """
        return self._RFW

    def getTAN(self):
        """
        Returns the value of _TAN
        """
        return self._TAN 

    def getTANconc(self):
        """
        Returns the concentration of total ammoniacal nitrogen 
        in units of g/L (kg/m3)
        """
        if not self._TAN:
            return 0
        else:
            return self._TAN / self._TWV

    def getTS(self):
        """
        Returns the value of _TS
        """
        return self._TS 

    def getTSconc(self):
        """
        Returns the concentration of total solids in units of g/L (kg/m3)
        """
        if not self._TS:
            return 0
        else:
            return self._TS / self._TWV

    def getTWV(self):
        """
        Returns the value of _TWV
        """
        return self._TWV

    def getVS(self):
        """
        Return the value of _VS
        """
        return self._VS 
    
    def getVSconc(self):
        """
        Returns the concentration of volatile solids in units of g/L (kg/m3)
        """
        if not self._VS:
            return 0
        else:
            return self._VS / self._TWV


    #Setters
    def setK(self, k):
        """
        Sets the value of _K to k.

        Parameter k: mass of potassium.
        Precondition: k is a non-negative float in units of kg
        """
        self._K = k

    def setN(self, n):
        """
        Sets the value of _N to n.

        Parameter n: mass of nitrogen.
        Precondition: n is a non-negative float in units of kg
        """
        self._N = n

    def setP(self, p):
        """
        Sets the value of _P to p.

        Parameter p: mass of phosphorus.
        Precondition: p is a non-negative float in units of kg
        """
        self._P = p

    def setRFW(self, rfw):
        """
        Sets the value of _RFW to rfw

        Parameter rfw: the volume of recycled flush water
        Precondition: A non negative float in units of m3
        """

    def setTAN(self, tan):
        """
        Sets the value of _TAN to tan.

        Parameter tan: total mass of ammoniacal nitrogen
        Precondition: tan is a non-negative float in units of kg
        """
        self._TAN = tan

    def setTS(self, ts):
        """
        Sets the value of _TS to ts.

        Parameter ts: total mass of solids.
        Precondition: ts is a non-negative float in units of kg
        """
        self._TS = ts

    def setTWV(self, twv):
        """
        Sets the value of _TWV to twv.

        Parameter twv: total waste volume
        Precondition: twv is a non-negative float in units of m3
        """
        self._TWV = twv

    def setVS(self, vs):
        """
        Sets the value of _VS to vs.

        Parameter vs: total mass of volatile solids.
        Precondition: vs is a non-negative float in units of kg
        """
        self._VS = vs
