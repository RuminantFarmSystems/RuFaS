################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# read_json.py - Contains routines to read and interpret json files
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import json
import csv
from pathlib import Path

from MASM.output import OutputHandler
from MASM.errors import LengthMismatchError, JSONfileError, InvalidJSONfileError
from MASM.classes import State, Config, Weather

#-------------------------------------------------------------------------------
# Function: read_json_file
#           Sets up the parameters of the simulation
#           Reads and interprets the json file
#
# Parameters: fPath - Path to the MASM file for the simulation
#             c - Config object to be written to
#             w - Weather object to be written to
#             o - Output object to be written to
#
# Raises: InvalidJSONfileError - when there is a problem with the json file
#-------------------------------------------------------------------------------
def read_json_file(fPath:Path, s:State, c:Config, w:Weather, o:OutputHandler):
    
    c.fName = fPath.name
    
    with fPath.open('r') as f:
        data = json.load(f)
        
        try:
            read_config(data['config'], c)
            read_weather(data['weather'], w, c)
            read_output_options(data['output'], o, c)
            read_farm(data['farm'], s, c, o)
            
        except (JSONfileError, LengthMismatchError) as e:
            print(e.msg)
            raise InvalidJSONfileError(c.fName)
        
        #except Exception:
            #print("Something wrong with {}".format(c.fName))
            #raise InvalidJSONfileError(c.fName)
        
#-------------------------------------------------------------------------------
# Function: read_config
# 
#-------------------------------------------------------------------------------
def read_config(data, c:Config):
    
    try:
        c.iterations = data['iterations']
        c.iterate = data['iterations'] > 1
        c.years = data['years']
        
    except KeyError:
        raise JSONfileError(c.fName, "CONFIG", "Config Input Key Mismatch")

#-------------------------------------------------------------------------------
# Function: read_output_options
# 
#-------------------------------------------------------------------------------
def read_output_options(data, o:OutputHandler, c:Config):
    
    directory = data['path']
    reports = data['reports']

    if len(reports) != len(o.report_handlers):
        raise LengthMismatchError(c.fName, "OUTPUT", len(o.report_handlers))
    
    for key, value in reports.items():
        if key not in o.report_handlers:
            raise JSONfileError(c.fName, "OUTPUT",
                                "Output Report Handler name mismatch")
        else:
            o.report_handlers[key].active = value['active']
            if reports[key]['file_name'] is not None:
                o.report_handlers[key].fName = value['file_name']
                o.report_handlers[key].path = directory + o.report_handlers[key].fName
            
    
#-------------------------------------------------------------------------------
# Function: read_weather
# 1) Reads in rainfall data and stores date in w.rainfall
#-------------------------------------------------------------------------------
def read_weather(filePath:str, w:Weather, c:Config):    
    
    currentRow = 0
    
    w.rainfall = [[0 for _ in range(365)]for _ in range(c.years)]
    w.tMax = [[0 for _ in range(365)]for _ in range(c.years)]
    w.tMin = [[0 for _ in range(365)]for _ in range(c.years)]
    w.tAvg = [[0 for _ in range(365)]for _ in range(c.years)]
    w.biomass = [[0 for _ in range(365)]for _ in range(c.years)]
    w.radiation = [[0 for _ in range(365)]for _ in range(c.years)]


    rainfallData = []
    tMaxData = []
    tMinData = []
    tAvgData = []
    bioMass = []
    radiation = []
    
    with open(filePath, "r") as f:
        readCSV = csv.reader(f, delimiter=',')
        for row in readCSV:
            if currentRow != 0:
                # 1) Read rainfall data
                rainfallData.append(row[1])
                
                # 2) Read max temperature data
                tMaxData.append(row[2])
                
                # 3) Read min temperature data
                tMinData.append(row[3])
                
                # 4) Read avg temperature data
                tAvgData.append(row[4])
                
                # 5) Read biomass data
                bioMass.append(row[5])
                
                # 6) Read radiation data
                radiation.append(row[6])
            
            currentRow += 1
    
    # 1) Update Rainfall in weather
    for i in range(0, c.years):
        for j in range(0, 365):
            if (i*365+j) >= len(rainfallData):
                break
            else:
                w.rainfall[i][j] = rainfallData[i*365 + j]

    # 2) Update Max Temperature in weather
    for i in range(0, c.years):
        for j in range(0, 365):
            if (i*365+j) >= len(tMaxData):
                break
            else:
                w.tMax[i][j] = tMaxData[i*365 + j]
                
    # 3) Update Min Temperature in weather
    for i in range(0, c.years):
        for j in range(0, 365):
            if (i*365+j) >= len(tMinData):
                break
            else:
                w.tMin[i][j] = tMinData[i*365 + j]

    # 4) Update Avg Temperature in weather
    for i in range(0, c.years):
        for j in range(0, 365):
            if (i*365+j) >= len(tAvgData):
                break
            else:
                w.tAvg[i][j] = tAvgData[i*365 + j] 
                
    # 4) Update biomass in weather
    for i in range(0, c.years):
        for j in range(0, 365):
            if (i*365+j) >= len(bioMass):
                break
            else:
                w.biomass[i][j] = bioMass[i*365 + j]
                
    # 4) Update radiation in weather
    for i in range(0, c.years):
        for j in range(0, 365):
            if (i*365+j) >= len(radiation):
                break
            else:
                w.radiation[i][j] = radiation[i*365 + j]
                
#-------------------------------------------------------------------------------
# Function: read_farm
# 
#-------------------------------------------------------------------------------
def read_farm(data, s:State, c:Config, o:OutputHandler):
    
    #read_location(data['location'], s.location, c)
    read_soil(data['soil'], s.soil, c)

    #read_crops(data, s.crops, c)
    #read_feed(data, s.feed, c)
    #read_fieldOps(data, s.fieldOps, c)
    #read_herd(data, s.herd, c)
    #read_housing(data, s.housing, c)
    #read_manure(data, s.manure, c)

#-------------------------------------------------------------------------------
# Function: read_location
# 
#-------------------------------------------------------------------------------
def read_location(data, location, c:Config):
    
    try:
        location.latitude = data['latitude']
        
    except KeyError:
        raise JSONfileError(c.fName, "Location", "Location Input Key Mismatch")

#-------------------------------------------------------------------------------
# Function: read_soil
# Reads the data-fields associated with the soil portion from the json file 
#-------------------------------------------------------------------------------
def read_soil(f, so, c:Config):
    
    # read in each soil attribute
    for key, value in f.items():
        if(key == "ProfileDepth"):
            so.profileDepth = value
        elif(key == "CN2"):
            so.CN2 = value
        elif(key.startswith("Layer")):
            read_soil_layer(key, f[key], so, c)
        elif(key == "FieldSlope"):
            so.fieldSlope = value
        elif(key == "SlopeLength"):
            so.slopeLength = value
        elif(key.startswith("Manning")):
            so.manning = value
        elif(key == "FieldSize"):
            so.fieldSize = value
        elif(key == "PracticeFactor"):
            so.practiceFactor = value        
        elif(key == "Orgc"):
            so.orgc = value 
        elif(key == "Sand"):
            so.sand = value
        elif(key == "Silt"):
            so.silt = value
        elif(key == "Clay"):
            so.clay = value
        elif(key == "BulkDensity"):
            so.bulkDensity = value
        elif(key == "SoilAlbedo"):
            so.soilAlbedo = value
        else:
            raise JSONfileError(c.fName, "Soil", "Soil Input Key Mismatch")
     
   
    # sort layers by bottomDepth 
    so.listOfSoilLayers.sort(key=lambda x: x.bottomDepth) 
    
    # calculate initial depth of each soil layer
    for x in range(0, len(so.listOfSoilLayers)):
        if x == 0:
            so.listOfSoilLayers[x].depth = so.listOfSoilLayers[x].bottomDepth
        else:   
            so.listOfSoilLayers[x].depth = (so.listOfSoilLayers[x].bottomDepth
                - so.listOfSoilLayers[x-1].bottomDepth)
    
    so.convertCurrentSoilWaterToMM() # calculate initial soil water in layer
    so.calculateWiltingWater() # calculate wilting water in layer
    so.calculateFcWater() # calculate field capacity water in layer
    
#-------------------------------------------------------------------------------
# Function: read_soil_layer
# Reads the data-fields associated with a layer of soil from the json file 
#-------------------------------------------------------------------------------        
def read_soil_layer(layerName, f, so, c:Config):
    bottomDepth = 0.0
    currentSoilWater = 0.0
    kSat = 0.0
    wiltingPoint = 0.0
    fieldCapacity = 0.0
    saturation = 0.0
    temperature = 0.0
    
    for key, value in f.items():
        if(key == "BottomDepth"):
            bottomDepth = value   
        elif(key == "StartingSoilWater"):
            currentSoilWater = value
        elif(key == "Ksat"):
            kSat = value
        elif(key == "WiltingPoint"):
            wiltingPoint = value
        elif(key == "FieldCapacity"):
            fieldCapacity = value        
        elif(key == "Saturation"):
            saturation = value     
        elif(key == "InitialTemperature"):
            temperature = value
            if layerName == "Layer1":
                so.Tsurf = value   
        else:
            raise JSONfileError(c.fName, "SoilLayer", "Soil Layer Input Key Mismatch")
        
    so.addSoilLayer(layerName, bottomDepth, currentSoilWater, kSat,
                    wiltingPoint, fieldCapacity, saturation, temperature)
    
"""
#-------------------------------------------------------------------------------
# Function: read_crops
# 
#-------------------------------------------------------------------------------
def read_crops(f, cp, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_feed
# 
#-------------------------------------------------------------------------------
def read_feed(f, fd, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_fieldOps
# 
#-------------------------------------------------------------------------------
def read_fieldOps(f, fo, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_herd
# 
#-------------------------------------------------------------------------------
def read_herd(f, hd, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_housing
# 
#-------------------------------------------------------------------------------
def read_housing(f, hs, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_manure
# 
#-------------------------------------------------------------------------------
def read_manure(f, mn, c:Config):
    pass
"""