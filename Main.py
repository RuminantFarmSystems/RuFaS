'''
Created on Oct 19, 2017

Created by the USDA-ARS at Madison, Wisconsin
Kristan, Kass, Jit
'''

"""This class is a Simulation Controller object. An instance of this object
runs a simulation. Functions in the class are divided based on time periods;
year, month, day"""

from SimController import SimController
from Weather import Weather

"""Execution of the program begins here."""
if __name__ == '__main__':
    
    SimWeather = Weather(20)
    print(SimWeather.getTemperature())
    SimWeather.setTemperature(50)
    print(SimWeather.getTemperature())


    """
    1) READ INPUT DATA AND STORE IN OBJECTS 2) SET MODEL PARAMETERS?

    I) Create and set Feed Object
        a) Initial feed availability (or simulated for first year)
        b) Feed storage information

    II) Create and set Weather Object'
        a) Set parameters such as temperature, precipitation, etc.

    III) Create and set Soil Object
        a) Set parameters such as 
            i) % land area for each major soil type – each major type includes parameters below
            ii) Slope for soil types 
            iii) Layer depths, Organic matter, Clay content, bulk density, field capacity, wilting point
            iv) Initial C, N, P pool sizes
            v) Initial residue on soil surface
            vi) Porosity
            vii) C, N, P pool sizes
            viii) Soil moisture- initialized a field capacity

    IV) Create and set Herd Object
        a) Set parameters such as 
            i) Number of lactating cows and replacement rate and/or number of heifers
            ii) Number of feeding groups
            iii) Reproductive protocol/ efficiency
            iv) User defined ration/ ration formulation option (i.e. least cost, max income/feed, min N excretion, min methane?)
            v) Animal specific parameters/distributions – breed, BW (frame size?), production, reproduction, health

    V) Create and set Housing Object
        a) Set parameters such as 
            i) Housing types available
                Size 
                Ventilation
                Surface type and % vegetation
                Bedding
            ii) Type of animal and time spent in each housing type 
            iii) Manure handling system
            iv) Collection type and frequency

    VI) Create and set Manure Object
        a) Set parameters such as
            i) Digester, lagoon, separation, chemical treatment
            
    VII) Create and set FieldOperations Object
        a) Set parameters such as
            i) Dates for planting, harvest, tillage, irrigation (yes/no model determines amount based on soil moisture)
    
    VIII) Create and set Crop Object
        a) Set parameters such as
            i) Rotation - model develops crop distribution from acreage and rotation years
            
    IX) Create Output Object
    """

    '3) BEGIN SIMULATION CYCLE'
    'A new simulation object is created and run; add parameters (objects above) other then year which are specific to simulation'
    simulation = SimController(4)
    simulation.runSimulation()  # insert functions within time sequences to acquire desired output

    '4) PRINT OUTPUT- MASM OUTPUT FORMAT'
