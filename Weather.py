'''
Created on Oct 19, 2017

Created by the USDA-ARS at Madison, Wisconsin
Kristan, Kass, Jit
'''

"""This class represents a Weather object. An instance of this object
represents the weather for a simulation."""

class Weather:

    def __init__(self):
        pass
    
    def getTemperature(self):
        return self.temperature
    
    def setTemperature(self, newTemp):
        self.temperature = newTemp