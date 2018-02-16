################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# nitrogen_cycling.py - 
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import math

#------------------------------------------------------------------------------
# Function: daily_nitrogen_cycling_routine
# Executes all the daily nitrogen cycling  routines
#------------------------------------------------------------------------------
def daily_nitrogen_cycling_routine(soil):
    daily_soil_nitrogen(soil)    


#------------------------------------------------------------------------------
# Function: daily_soil_nitrogen
# Equations taken from SWAT 2009 documentation
# We will simulate 3 organic N pools (Fresh, Active, Stable) and 2 inorganic 
# pools (NO3 and NH4).    
#
# 1) Initialize soil N Pools
# 2) Mineralization and Decomposition  
# 3) Nitrification and Volatilization
# 4) N loss in Leaching, runoff, and erosion  
#------------------------------------------------------------------------------
def daily_soil_nitrogen(soil):
    
    # FOR each soil layer
    for x in range(0, len(soil.listOfSoilLayers)):
    
    # 1) ----------------Initialize soil N Pools--------------------------------
        
        
        bottomDepth = soil.listOfSoilLayers[x].bottomDepth # depth of boundary
        BD = soil.bulkDensity # soil layer bulk density (g/cm3)
        depth = soil.listOfSoilLayers[x].depth # soil layer thickness (mm)
        
        # Organic carbon in a soil layer (%, user input)
        OrgC = soil.listOfSoilLayers[x].orgC 
        
        # top soil layer soil residue (input)
        residue = 0 
        if x == 0:
            residue = soil.residue 

        # Initial NO3 levels (mg/kg) in the soil are varied by depth as: 
        NO3 = 7 * math.exp(-bottomDepth/1000)
        NO3 = (NO3 * BD * depth) / 100 # convert to kg/ha
    
        # Organic N (Active + Stable, mg/kg) is initialized as:
        OrgN = (10**4) * (OrgC / 14)
    
        # Variable to partition OrgN into pools
        FracN = 0.02
    
        # Active N Pool
        activeN = FracN * OrgN
        activeN = (activeN * BD * depth) / 100 # convert to kg/ha
    
        # Stable N Pool
        stableN = (1 - FracN) * OrgN
        stableN = (stableN * BD * depth) / 100 # convert to kg/ha
    
        # Fresh N Pool --- only in top soil layer
        freshN = 0
        if x == 0:
            freshN = 0.0015 * residue
            freshN = (freshN * BD * depth) / 100 # convert to kg/ha

        # NH4 is initialized to 0 mg/kg.
        NH4 = 0
        NH4 = (NH4 * BD * depth) / 100 # convert to kg/ha
    
    # 2) Mineralization and Decomposition
        # Mineralization equations represent net mineralization. Both Fresh and 
        # Active N are subject to mineralization. Mineralization uses soil 
        # temperature and soil water factors in calculations. 
        
        # temperature of soil layer
        soilTemp = soil.listOfSoilLayers[x].temperature 
        
        # water content of the soil layer (mm)
        SW = soil.listOfSoilLayers[x].currentSoilWaterMM
         
        # field capacity water content of the soil layer (mm)
        FC = soil.listOfSoilLayers[x].fcWater
        
        
        # Active N mineralization rate (kg/ha; user defined)
        minRate =  soil.listOfSoilLayers[x].activeMineralRate
    
        # the soil temperature factor; has to be >= 0.1
        tempFac = max(0.1, 0.1 + 0.9 * soilTemp / (soilTemp + math.exp(9.93 - 
                                                    0.312 * soilTemp)))
            
        # the soil water factor
        waterFac = SW / FC
    
        # N moves between the Active and Stable pools to maintain an equilibrium as:
        Ntrans = 0.00001 * (activeN * (1/FracN - 1) - stableN)
    
        # When Ntrans is positive, N moves from Active to Stable pool. When Ntrans 
        # is negative, N moves from Stable to Active pool. 
        if Ntrans > 0:
            stableN += Ntrans
            activeN -= Ntrans
        elif Ntrans < 0:
            activeN += Ntrans
            stableN -= Ntrans
        
        # Mineralization from Active N pool is:
        Nminact = minRate * ((tempFac * waterFac)**0.5) * activeN
    
        # Decomposition and mineralization of Fresh N is only in the first soil 
        # layer. Decomposition and mineralization are a function of a daily rate 
        # constant that is calculated with the C:N ratio and C:P ratio of the 
        # residue, and temperature and soil water factors.
        freshOrganicP = soil.residue * 0.0003
        freshOrganicP = freshOrganicP * BD * soil.listOfSoilLayers[x].bottomDepth / 100 # kg
        labileP = soil.labileP #input
        labileP = labileP * BD * soil.listOfSoilLayers[x].bottomDepth / 100
        resComp = soil.freshNMineralRate #fresh N mineral rate
        
            
        carbonToNitrogen = (0.58 * residue) / (freshN + NO3) # C:N ratio
        carbonToPhosphorus = (0.58 * residue) / (freshOrganicP + labileP) # C:P ratio
    
        #A decay rate constant (Decay) defines the fraction of residue that is 
        # decomposed as: 
        residueFactor = min(math.exp(-0.693 * (carbonToNitrogen - 25) / 25), 
                       1)
        
        decay = 0
        if x == 0:
            decay = residueFactor * resComp * ((tempFac * waterFac)**0.5)
    
        # Mineralization of Fresh N (kg/ha) is then calculated as:
        #freshMin = residueFactor * freshN
        freshMin = 0
        freshDecomp = 0
        if x == 0:
            freshMin = 0.8 * decay * freshN
            freshDecomp = 0.2 * decay * freshN
    
        # 20% of FreshMin is added to the Active N pool, and 80% is added to the 
        # NO3 pool.
        #activeN += 0.2*freshMin
        #NO3 += 0.8*freshMin
        
    # 3) Nitrification and Volatilization
        # Nitrification is the transfer of NH4 to NO3. Nitrification occurs only 
        # when the soil temperature exceeds 5oC. It is a function of soil 
        # temperature and water factors. 
        WP = soil.listOfSoilLayers[x].wiltingWater

        # depth to the midpoint of the soil layer (mm) 
        midpointDepth = soil.listOfSoilLayers[x].bottomDepth/2 

        nitrTFac = 0
        if soil.listOfSoilLayers[x].temperature > 5.0:
            nitrTFac = 0.41 * (soilTemp - 5) / 10 # temperature factor
    
        nitrWaterFac = min((SW - WP) / (0.25 * (FC - WP)), 1.0) # water factor
    
        # volatilization depth factor is calculated as:
        depthFac = 1 -(midpointDepth / (midpointDepth + math.exp(4.706 - 0.0305
                                                             * midpointDepth)))
    
        CECFac = 0.15 # volatilization cation exchange factor
        nitrFac = nitrTFac * nitrWaterFac # nitrification regulator 
        volatilFact = nitrTFac * depthFac * CECFac # volatilization regulator
    
        # Total combined nitrification and volatilization (kg/ha) is:
        totNitriVolatil = NH4 * (1 - math.exp(-nitrFac - volatilFact))
    
        # Fraction of the total that is nitrification is:
        #fracNitri = 1 - math.exp(nitrFac)
        fracNitri = 1 - math.exp(-nitrFac)
    
        # Fraction of the total that is volatilization is:
        #fracVolatili = 1 - math.exp(volatilFact)
        fracVolatili = 1 - math.exp(-volatilFact)
    
        # Mass of nitrification (kg/ha) is:
        nitrification = 0
        if fracNitri + fracVolatili != 0:
            nitrification = (fracNitri / (fracNitri + fracVolatili)
                                    ) * totNitriVolatil
    
        # Mass of volatilization (kg/ha) is:
        volatilization = (fracVolatili /(fracNitri + 
                                     fracVolatili)) * totNitriVolatil
    
    # 4) N loss in leaching, runoff, and erosion
        # All N lost in runoff and erosion is removed from soil layer 1. N in 
        # leaching is removed from a given soil layer and added to the next deeper 
        # layer.
        anionEx = soil.listOfSoilLayers[x].cationExclusionFraction # Fraction of soil porosity where anions are excluded (user defined)
        
        runoff = soil.runoff # runoff on a particular given day
        perc = soil.listOfSoilLayers[x].perc # percolation on a particular given day    
        
        w = perc 
        # soil water (includes runoff for soil layer 1)
        if x == 0:
            w += runoff
    
        # water content at soil saturation for layer
        SAT = soil.listOfSoilLayers[x].saturation 
    
        Sed = soil.sedimentYield # daily soil loss (Metric Tons)
    
        # Concentration (kg N/mm H20) of NO3 in a soil layer is:
        NO3Conc = 0
        if w != 0:
            NO3Conc = NO3 * (1 - math.exp(-w / ((1 - anionEx) * SAT))) / w
        
        # Mass (kg/ha) of NO3 loss in runoff (mm) from soil layer 1 only is:
        NO3Runoff = 0
        if x == 0:    
            NO3Runoff = NO3Conc * runoff
        
        # Mass (kg/ha) of NO3 loss in percolation water (mm) from all soil 
        # layers is:
        NO3Perc = NO3Conc * perc
        
        # Concentration (kg N/mm H20) of NO3 in a soil layer is:
        NH4Conc = 0
        if w != 0:
            NH4Conc = NH4 * (1 - math.exp(-w / ((1 - anionEx) * SAT))) / w
        
        # Mass (kg/ha) of NH4 loss in runoff (mm) from soil layer 1 only is:
        NH4Runoff = 0
        if x == 0:    
            NH4Runoff = NH4Conc * runoff
        
        # Mass (kg/ha) of NH4 loss in percolation water (mm) from all soil 
        # layers is:
        NH4Perc = NH4Conc * perc    
        
        # For N loss in erosion, soil N concentrations (mg/kg) for each pool except
        # NO3 are calculated as:
        freshSoilNConc = (100 * freshN) / (BD * soil.listOfSoilLayers[x].bottomDepth)
        activeSoilNConc = (100 * activeN) / (BD * soil.listOfSoilLayers[x].bottomDepth)
        stableSoilNConc = (100 * stableN) / (BD * soil.listOfSoilLayers[x].bottomDepth)
        NH4SoilNConc = (100 * NH4) / (BD * soil.listOfSoilLayers[x].bottomDepth)

        # Enrichment ratio
        ER = 0
        if Sed != 0.0:
            ER = max(1, math.exp(1.21 - 0.16 * math.log(Sed * 1000)))
    
        # N mass loss in erosion (kg/ha) is calculated as:
        freshSoilNLoss = 0
        activeSoilNLoss = 0
        stableSoilNLoss = 0
        NH4SoilNLoss = 0
        if Sed > 0:
            freshSoilNLoss = 0.001 * freshSoilNConc * Sed * ER
            activeSoilNLoss = 0.001 * activeSoilNConc * Sed * ER
            stableSoilNLoss = 0.001 * stableSoilNConc * Sed * ER
            NH4SoilNLoss = 0.001 * NH4SoilNConc * Sed * ER
        
        denitrificationRate = soil.listOfSoilLayers[x].denitrificationRate
        denitrification = 0
        if soil.listOfSoilLayers[x].currentSoilWaterMM  <= SAT*0.6:
            denitrification = NO3 * (1 - math.exp(-denitrificationRate *
                                                  tempFac * OrgC))
            
        NO3 += totNitriVolatil
        #NO3 += Nminact # N mineralized from the Active pool is added to the NO3 pool
        NO3 -= denitrification
        NO3 -= NO3Runoff
        NO3 -= NO3Perc
        
        NH4 += Nminact
        NH4 += freshMin
        NH4 -= totNitriVolatil
        NH4 -= NH4Runoff
        NH4 -= NH4Perc
        NH4 -= NH4SoilNLoss
        
        activeN -= Ntrans
        activeN -= Nminact
        activeN += freshDecomp
        activeN -= activeSoilNLoss
        
        stableN += Ntrans
        stableN -= stableSoilNLoss
        
        if x == 0:
            freshN = max(0, freshN - freshMin - freshDecomp - freshSoilNLoss)        
        
        print(freshN)
