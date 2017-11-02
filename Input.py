################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
# Input.py
#     Contains input file routines
# Author: Kass Chupongstimun
#
################################################################################
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

from warnings import catch_warnings

def readInput(SIMULATION):
    while True:
        try:
            fName = input("Enter Input File Name: ")
            f = open(fName, "r")
            break
        except FileNotFoundError:
            print("File does not exist, please try again")
    
    if not readConfigurations(SIMULATION, f):
        return False
    if not readFarmInputs(SIMULATION, f):
        return False
    
    return True

def readConfigurations(SIMULATION, f):
    return True

def readFarmInputs(SIMULATION, f):
    if not readCrops(SIMULATION.crop):
        return False
    if not readHerd(SIMULATION.herd):
        return False
    if not readManure(SIMULATION.manure):
        return False
    if not readSoil(SIMULATION.soil):
        return False

    return True

def readCrops(c):
    return True

def readHerd(h):
    return True

def readManure(m):
    return True

def readSoil(s):
    return True

def readWeather(SIMULATION):
    while True:
        try:
            fName = input("Enter Weather File Name: ")
            f = open(fName, "r")
            break
        except FileNotFoundError:
            print("File does not exist, please try again")
    
def verifyWeather(W, config):
    pass
    