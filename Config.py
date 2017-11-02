'''
Created on Nov 2, 2017

Created by the USDA-ARS at Madison, Wisconsin
Kristan, Kass, Jit
'''

"""The object contain the various configurations for the simulation"""
class Config():
    
    def __init__(self):
        self.years = 1
        self.repetitions = 1
    
    def modifyParameters(self, r, state):
        pass