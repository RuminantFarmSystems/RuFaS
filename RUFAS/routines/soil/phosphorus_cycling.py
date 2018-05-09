################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# phosphorus_cycling.py -
#
# Authors: DR. Peter A. Vadas
#          USDA-ARS Dairy Forage Research Center
#          1925 Linden Dr. West
#          Madison, WI 53706
#          PHONE NO. (608) 890-0069
#          E-mail: peter.vadas@ars.usda.gov
#          
# Coders:  Kass Chupongstimun
#          Jit Patil
#
################################################################################

import math

#------------------------------------------------------------------------------
# Function: daily_phosphorus_cycling_routine
# Executes all the daily phosphorus cycling  routines
#------------------------------------------------------------------------------
def daily_phosphorus_cycling_routine(soil, time, weather, config):
    if time.year == 1 and time.day == 1:    
        initializePhosphorusInputs(soil, time, weather, config)    
        soilChem(soil)
    
    fertilizer(soil, time)
    manure(soil, time)

#------------------------------------------------------------------------------
# Function: daily_phosphorus_update
# Update attributes of soil phosphorus in preparation of following day
#------------------------------------------------------------------------------
def daily_phosphorus_update(soil, time, weather):
    pass

#------------------------------------------------------------------------------
# Function: manure
# This subroutine calculates # of plops added per day and amount of TP, WIP, 
# and WOP added in manure. Adds P to surface manure pool, and updates
# cumulative manure and TP added during model run.
#
# Calculates TP, WIP, and WOP added in the manure, adds P to surface manure 
# pools. All units are KG or HA.
#------------------------------------------------------------------------------
def manure(soil, time):
    for x in range(0, len(soil.manureApplications)):
        if(time.day == soil.manureApplications[x].appDay and 
                            time.year == soil.manureApplications[x].appYear):
            COVSLP = 0.0154 * (soil.manureApplications[x].mass**-0.555)
            
            soil.manureApplications[x].percentCover = min(1.0,
                    0.012*soil.manureApplications[x].mass**0.48)
            MCOVAPP = soil.fieldSize * soil.manureApplications[x].percentCover
            MANPAPP = (soil.manureApplications[x].mass *
                       soil.manureApplications[x].totalP)
            soil.summan += soil.manureApplications[x].mass
            soil.summanP += MANPAPP
    pass

#------------------------------------------------------------------------------
# Function: fertilizer
# This subroutine calculates P added in fertilizer, adds fertilizer P to 
# surface pool, and updates cumulative fertilizer P added during the model run
#
# Calculates TP, WIP, and WOP added in the manure,
# adds P to surface manure pools. All units are KG or HA
#------------------------------------------------------------------------------
def fertilizer(soil, time):
    for x in range(0, len(soil.fertilizerApplications)):
        if(time.day == soil.fertilizerApplications[x].appDay and 
           time.year == soil.fertilizerApplications[x].appYear):
            sumFert = 0.0 #needed?
            noRains = 0.0
            fertCnt = 1.0
            
            if(soil.fertilizerApplications[x].depth == 0.0):
                AvFrtP = 0.0
                FrtPSt = 0.0 
                RSFRTP = 0.0
            else:
                AvFrtP = 0.0
                FrtPSt = 0.0 
                RSFRTP = 0.0     
                
                for y in range(0, len(soil.listOfSoilLayers)):           
                    if(soil.listOfSoilLayers[y].depth > 
                                        soil.fertilizerApplications[x].depth):
                        sumfac = 0.0
                        soil.listOfSoilLayers[y].labileP *= soil.fieldSize
                        for z in range (0, y):
                            fact = (soil.listOfSoilLayers[z].depth /
                                    soil.fertilizerApplications[x].depth)
                            soil.listOfSoilLayers[z].labileP += (
                                soil.fertilizerApplications[x].fertPMass *
                                fact * (1.0 - 
                                soil.fertilizerApplications[x].percentOnSurface))
                        
                        soil.listOfSoilLayers[x].labileP /= soil.fieldSize
                        
    #for x in range(0, len(soil.listOfSoilLayers)):
    #    labileP = soil.listOfSoilLayers[x].labileP
    #    print("HI")

#------------------------------------------------------------------------------
# Function: soilChem
# This subroutine initializes soil chemical properties
#------------------------------------------------------------------------------
def soilChem(soil):
    for x in range(0, len(soil.listOfSoilLayers)):
        labileP = soil.listOfSoilLayers[x].labileP
        psp = soil.listOfSoilLayers[x].psp
        soilOC = soil.listOfSoilLayers[x].soilOC
        
        soil.listOfSoilLayers[x].activeP = (labileP *
                (1.0 - psp)/ 
                psp)
        
        soil.listOfSoilLayers[x].stableP = (soil.listOfSoilLayers[x].activeP *4.0)  
        
        soil.listOfSoilLayers[x].orgP = (soilOC / 8.0/
                    14.0*10000.0*soil.listOfSoilLayers[x].bulkDensity*
                    soil.listOfSoilLayers[x].depth*0.1)   
        
        print("HI")

#------------------------------------------------------------------------------
# Function: initializePhosphorusInputs
# Initialize phosphorus variable on at the beginning of the simulation
#------------------------------------------------------------------------------
def initializePhosphorusInputs(soil, time, weather, config):
    uptake(soil.pUptake, soil, config)
    
    for x in range(0, len(soil.listOfSoilLayers)):
        soil.listOfSoilLayers[x].soilOC = soil.listOfSoilLayers[x].OMpercent * 0.58
        
        
        soil.listOfSoilLayers[x].psp = (-0.045 * math.log(
            soil.listOfSoilLayers[x].clay) + 0.001*soil.listOfSoilLayers[x].labileP - 
            0.035 * soil.listOfSoilLayers[x].soilOC + 0.43)
        
        soil.listOfSoilLayers[x].labileP = (soil.listOfSoilLayers[x].labileP
                * soil.listOfSoilLayers[x].bulkDensity  * 
                soil.listOfSoilLayers[x].depth / 10)
                
    7500, 3000, 2500, 2300, 2100, 1900, 1700, 1500, 1700, 2500, 6000, 9000
    soil.lightFactor.append(0.0)
    soil.yieldFactor.append(0.0)
    for y in range(1, 366):
        if y == 1:
            soil.lightFactor.append(1.0)
            soil.yieldFactor.append(7500.0)
        elif y < 32:
            soil.lightFactor.append((0.9-1.0)/31+soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((3000.0-7500.0)/31+soil.yieldFactor
                                    [len(soil.yieldFactor)-1])
        elif y == 32:
            soil.lightFactor.append(0.9)
            soil.yieldFactor.append(3000.0)
        elif y > 32 and y < 60:
            soil.lightFactor.append((0.85-0.9)/28.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((2500.0-3000.0)/28+soil.yieldFactor
                                    [len(soil.yieldFactor)-1])
        elif y == 60:
            soil.lightFactor.append(0.85)
            soil.yieldFactor.append(2500.0)
        elif y > 60 and y < 91:
            soil.lightFactor.append((0.7-0.9)/31.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((2300.0-2500.0)/31+soil.yieldFactor
                                    [len(soil.yieldFactor)-1])            
        elif y == 91:
            soil.lightFactor.append(0.7)
            soil.yieldFactor.append(2300.0)
        elif y > 91 and y < 121:
            soil.lightFactor.append((0.5-0.7)/30.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1]) 
            soil.yieldFactor.append((2100.0-2300.0)/30.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1])          
        elif y == 121:
            soil.lightFactor.append(0.5)
            soil.yieldFactor.append(2100.0)
        elif y > 121 and y < 152:
            soil.lightFactor.append((0.2-0.5)/31.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((1900.0-2100.0)/31.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1])     
        elif y == 152:
            soil.lightFactor.append(0.2)
            soil.yieldFactor.append(1900.0)
        elif y > 152 and y < 182:
            soil.lightFactor.append((0.25-0.2)/30.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])  
            soil.yieldFactor.append((1700.0-1900.0)/30.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1])            
        elif y == 182:
            soil.lightFactor.append(0.25)
            soil.yieldFactor.append(1700.0)
        elif y > 182 and y < 213:
            soil.lightFactor.append((0.4-0.25)/31.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((1500.0-1700.0)/31.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1]) 
        elif y == 213:
            soil.lightFactor.append(0.4)
            soil.yieldFactor.append(1500.0)
        elif y > 213 and y < 244:
            soil.lightFactor.append((0.8-0.4)/31.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((1700.0-1500.0)/31.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1]) 
        elif y == 244:
            soil.lightFactor.append(0.8)
            soil.yieldFactor.append(1700.0)
        elif y > 244 and y < 274:
            soil.lightFactor.append((0.9-0.8)/30.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((2500.0-1700.0)/30.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1]) 
        elif y == 274:
            soil.lightFactor.append(0.9)
            soil.yieldFactor.append(2500.0)
        elif y > 274 and y < 305:
            soil.lightFactor.append((0.95-0.9)/31.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((6000.0-2500.0)/31.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1]) 
        elif y == 305:
            soil.lightFactor.append(0.95)
            soil.yieldFactor.append(6000.0)
        elif y > 305 and y < 335:
            soil.lightFactor.append((1.0-0.95)/30.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((9000.0-6000.0)/30.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1]) 
        elif y == 335:
            soil.lightFactor.append(1.0)
            soil.yieldFactor.append(9000.0)
        elif y > 335 and y < 366:
            soil.lightFactor.append((1.0-1.0)/31.0 + soil.lightFactor
                                    [len(soil.lightFactor)-1])
            soil.yieldFactor.append((7500.0-9000.0)/31.0+soil.yieldFactor
                                    [len(soil.yieldFactor)-1]) 
            
    print("HI")

#------------------------------------------------------------------------------
# Function: uptake
# Initilaize crop phosphorus uptake array
#------------------------------------------------------------------------------
def uptake(pUptake, soil, config):
    for i in range(0, len(soil.cropPUptakes)):
        if(soil.cropPUptakes[i].uptakeYear == config.startYear):
            for j in range(0, 365):
                pUptake[soil.cropPUptakes[i].uptakeYear][j] = (
                    soil.cropPUptakes[i].pUptake/364)
                print(pUptake[soil.cropPUptakes[i].uptakeYear][j])
        
        elif(soil.cropPUptakes[i].uptakeYear == config.endYear):
            for j in range(0, 365):
                pUptake[soil.cropPUptakes[i].uptakeYear][j] = (
                    soil.cropPUptakes[i].pUptake/365)
                
        else:
            for j in range(0, 365):
                pUptake[soil.cropPUptakes[i].uptakeYear][j] = (
                    soil.cropPUptakes[i].pUptake/365)

def plow():
    pass

def solp():
    pass

def fertLeach():
    pass

def manLeach():
    pass

def PMinrl():
    pass

def writeDay():
    pass

def writeSum():
    pass