'''
Created on Oct 19, 2017

Created by the USDA-ARS at Madison, Wisconsin
Kristan, Kass, Jit
'''

"""This class is a Simulation Controller object. An instance of this object
runs a simulation. Functions in the class are divided based on time periods;
year, month, day"""

from SimController import SimController
from Input import readInput
from Input import readWeather

def main():
    print('MASM: Modular Agricultural Systems Modeling Environment')
    
    'A new simulation object is created'
    simulation = SimController()
    simulation.setDuration(4) # set the length of the simulation
    
    '1) Read farm inputs and configurations'
#    readInput(simulation)
    
    '2) Read weather file'
#    readWeather(simulation)

    '3) BEGIN SIMULATION CYCLE'
    simulation.runSimulation()  # insert functions within time sequences to acquire desired output

    '4) PRINT SIMULATION SUMMARY'

"""Execution of the program begins here."""
if __name__ == '__main__':
    main()