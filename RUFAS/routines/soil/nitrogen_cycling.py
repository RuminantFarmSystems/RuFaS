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
def daily_nitrogen_cycling_routine(soil, time, weather):
    daily_soil_nitrogen(soil, time.day, time.year,
                        float(weather.rainfall[time.year-1][time.day-1]))


#------------------------------------------------------------------------------
# Function: daily_nitrogen_update
# Update attributes of soil nitrogen in preparation of following day
#------------------------------------------------------------------------------
def daily_nitrogen_update(soil, time, weather):
    daily_soil_nitrogen_update(soil, time.day, time.year,
                    float(weather.addedN[time.year-1][time.day-1]))


#------------------------------------------------------------------------------
# Function: daily_soil_nitrogen
# Equations taken from SWAT 2009 documentation
# We will simulate 3 organic N pools (Fresh, Active, Stable) and 2 inorganic
# pools (NO3 and NH4).
#
# 1) Get current soil N Pools
# 2) Mineralization and Decomposition
# 3) Nitrification and Volatilization
# 4) N loss in Leaching, runoff, and erosion
#------------------------------------------------------------------------------
def daily_soil_nitrogen(soil, jday, year, rainfall):

    # FOR each soil layer
    for x in range(0, len(soil.listOfSoilLayers)):

    # 1) ----------------Current soil N Pools-----------------------------------

        # soil layer bulk density (g/cm3)
        BD = soil.listOfSoilLayers[x].bulkDensity

        # Organic carbon in a soil layer (%, user input)
        OrgC = soil.listOfSoilLayers[x].orgC

        # NO3 level (kg/ha) in the soil layer
        NO3 = soil.listOfSoilLayers[x].NO3

        # Organic N (Active + Stable, mg/kg) is:
        OrgN = soil.listOfSoilLayers[x].orgN

        # Variable to partition OrgN into pools
        FracN = soil.listOfSoilLayers[x].fracActiveN

        # Active N Pool
        activeN = soil.listOfSoilLayers[x].activeN

        # Stable N Pool
        stableN = soil.listOfSoilLayers[x].stableN

        # NH4 Pool
        NH4 = soil.listOfSoilLayers[x].NH4

    # 2) ----------------Mineralization and Decomposition-----------------------
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
        minRate = soil.listOfSoilLayers[x].activeMineralRate

        # the soil temperature factor; has to be >= 0.1
        tempFac = max(0.1, 0.1 + 0.9 * soilTemp / (soilTemp + math.exp(9.93 -
                                                    0.312 * soilTemp)))

        # the soil water factor
        waterFac = min(1, max(0.05, SW / FC))

        resComp = soil.freshNMineralRate  # fresh N mineral rate

        # Decomposition and mineralization of Fresh N is only in the first soil
        # layer. Decomposition and mineralization are a function of a daily rate
        # constant that is calculated with the C:N ratio and C:P ratio of the
        # residue, and temperature and soil water factors.
        if x == 0:
            freshOrganicP = soil.residue * 0.0003
            freshOrganicP = freshOrganicP * BD * soil.listOfSoilLayers[x].bottomDepth / 100  # kg
            labileP = soil.listOfSoilLayers[x].labileP  # input

            carbonToNitrogen = (0.58 * soil.residue) / (soil.topLayerFreshN + NO3)  # C:N ratio
            soil.CToN = carbonToNitrogen

            carbonToPhosphorus = (0.58 * soil.residue) / (freshOrganicP + labileP)  # C:P ratio
            soil.CToP = carbonToPhosphorus

            # A decay rate constant (Decay) defines the fraction of residue that is
            # decomposed as:
            residueFactor = min(math.exp(-0.693 * (carbonToNitrogen - 25) / 25),
                       1)
            decay = residueFactor * resComp * ((tempFac * waterFac) ** 0.5)
            soil.decayRate = decay

            # Mineralization of Fresh N (kg/ha) is then calculated as:
            # freshMin = residueFactor * freshN
            freshMin = 0.8 * decay * soil.topLayerFreshN
            soil.freshMin = freshMin

            freshDecomp = 0.2 * decay * soil.topLayerFreshN
            soil.freshDecomp = freshDecomp

    # 3) ----------------Nitrification and Volatilization-----------------------
        # Nitrification is the transfer of NH4 to NO3. Nitrification occurs only
        # when the soil temperature exceeds 5oC. It is a function of soil
        # temperature and water factors.
        WP = soil.listOfSoilLayers[x].wiltingWater

        # calculate temperature factor
        nitrTFac = 0.0
        if soil.listOfSoilLayers[x].temperature > 5.0:
            nitrTFac = 0.41 * (soilTemp - 5) / 10
        nitrTFac = min(1.0, nitrTFac)

        # volatilization depth factor is calculated as:
        depthFac = 0.9500
        if x != 0:
            # depth to the midpoint of the soil layer (mm)
            midpointDepth = (soil.listOfSoilLayers[x-1].bottomDepth
                             + soil.listOfSoilLayers[x].bottomDepth) / 2
            depthFac = 1 - (midpointDepth / (midpointDepth + math.exp(4.706 - 0.0305
                                                             * midpointDepth)))

        # volatilization cation exchange factor
        CECFac = soil.listOfSoilLayers[x].volatileExchangeFactor

        nitrReg = tempFac * waterFac * 0.1 # nitrification regulator

        volatilReg = nitrTFac * depthFac * CECFac  # volatilization regulator

        # Total combined nitrification and volatilization (kg/ha) is:
        totNitriVolatil = NH4 * (1 - math.exp(-nitrReg - volatilReg))
        soil.listOfSoilLayers[x].totNitriVolatil = totNitriVolatil

        # Fraction of the total that is nitrification is:
        # fracNitri = 1 - math.exp(nitrFac)
        fracNitri = 1 - math.exp(-nitrReg)

        # Fraction of the total that is volatilization is:
        fracVolatili = 1 - math.exp(-volatilReg)

        # Mass of volatilization (kg/ha) is:
        volatilization = (soil.listOfSoilLayers[x].NH4 *
                          volatilReg)
        soil.listOfSoilLayers[x].volatilization = volatilization

        # Mass of nitrification (kg/ha) is:
        nitrification = (soil.listOfSoilLayers[x].NH4 - volatilization
                         ) * nitrReg
        soil.listOfSoilLayers[x].nitrification = nitrification

    # 4) ----------------N loss in leaching, runoff, and erosion----------------
        # All N lost in runoff and erosion is removed from soil layer 1. N in
        # leaching is removed from a given soil layer and added to the next deeper
        # layer.

        # Fraction of soil porosity where anions are excluded (user defined)
        anionEx = soil.listOfSoilLayers[x].cationExclusionFraction

        runoff = soil.runoff  # runoff on a particular given day

        # percolation on a particular given day
        perc = soil.listOfSoilLayers[x].perc

        # water content at soil saturation for layer
        SAT = soil.listOfSoilLayers[x].saturation

        Sed = soil.snowCorrectedSed  # daily soil loss (Metric Tons)

        # calculate Denitrification in soil layer
        denitrificationRate = soil.listOfSoilLayers[x].denitrificationRate
        denitrification = 0.0
        if (soil.listOfSoilLayers[x].currentSoilWaterMM >
                                    soil.listOfSoilLayers[x].satWater * 0.6):
            denitrification = NO3 * (1 - math.exp(-denitrificationRate *
                                                  tempFac * OrgC))

        soil.listOfSoilLayers[x].denitrification = denitrification

        # Update NO3
        NO3 = max(0, NO3 - soil.listOfSoilLayers[x].denitrification)

        if x == 0 and SW != 0:
            soil.runoffNO3Conc = (1 - math.exp((-SW-rainfall)/
                        (soil.listOfSoilLayers[x].satWater + rainfall))
                       ) * NO3 / (SW+rainfall)/25

        # Update NO3
        if x == 0:
            NO3 = max(0, NO3 - soil.NO3Runoff)

        # Concentration (kg N/mm H20) of NO3 in a soil layer is:
        NO3Conc = 0.0
        if SW != 0:
            NO3Conc = (1 - math.exp(-SW/soil.listOfSoilLayers[x].satWater)
                       )/SW*NO3/5

        soil.listOfSoilLayers[x].NO3Conc = NO3Conc


        # Mass (kg/ha) of NO3 loss in runoff (mm) from soil layer 1 only is:
        NO3Runoff = 0.0
        if x == 0:
            NO3Runoff = soil.runoffNO3Conc * runoff
            soil.NO3Runoff = NO3Runoff

        # Mass (kg/ha) of NO3 loss in percolation water (mm) from all soil
        # layers is:
        NO3Perc = NO3Conc * perc
        soil.listOfSoilLayers[x].NO3Perc = NO3Perc

        # NH4 UPDATE
        NH4 = max(0, NH4 - totNitriVolatil)

        if x == 0 and SW != 0:
            soil.runoffNH4Conc = (1 - math.exp((-SW-rainfall) /
                        (soil.listOfSoilLayers[x].satWater+rainfall))
                        ) * NH4/(SW+rainfall)/5

        # Mass (kg/ha) of NH4 loss in runoff (mm) from soil layer 1 only is:
        NH4Runoff = 0.0
        if x == 0:
            NH4Runoff = soil.runoffNH4Conc * runoff
            soil.NH4Runoff = NH4Runoff

        # NH4 Update
        if x == 0:
            NH4 = max(0, NH4 - soil.NH4Runoff)

        # For N loss in erosion, soil N concentrations (mg/kg) for each pool except
        # NO3 are calculated as:
        if x == 0:
            soil.freshNConc = (100 * soil.topLayerFreshN) / (BD / soil.listOfSoilLayers[x].bottomDepth)
            soil.stableNConc = (100 * stableN) / BD / soil.listOfSoilLayers[x].bottomDepth
            soil.NH4Conc = (100 * NH4) / BD / soil.listOfSoilLayers[x].bottomDepth
            soil.activeNConc = (100 * activeN) / BD / soil.listOfSoilLayers[x].bottomDepth

        # Update Active N
        if x == 0:
            activeN = max(0, activeN - soil.activeNLoss)

        # Concentration (kg N/mm H20) of active N in a soil layer is:
        activeNConc = 0.0
        if SW != 0:
            activeNConc = (1 - math.exp(-SW / soil.listOfSoilLayers[x].satWater)) * activeN/SW/15
        soil.listOfSoilLayers[x].activeNConc = activeNConc

        # Mass (kg/ha) of active N loss in percolation water (mm) from all soil
        # layers is:
        activeNPerc = activeNConc * perc
        soil.listOfSoilLayers[x].activeNPerc = activeNPerc

        # Enrichment ratio
        ER = 0.0
        if Sed != 0.0:
            ER = max(1, math.exp(1.21 - 0.16 * math.log(Sed * 1000)))
        soil.enrichmentRatio = ER

        # N mass loss in erosion (kg/ha) is calculated as:
        if x == 0:
            if Sed > 0:
                soil.freshNLoss = 0.001 * soil.freshNConc * Sed * ER
                soil.activeNLoss = 0.001 * soil.activeNConc * Sed * ER
                soil.stableNLoss = 0.001 * soil.stableNConc * Sed * ER
                soil.NH4Loss = 0.001 * soil.NH4Conc * Sed * ER
            else:
                soil.freshNLoss = 0.0
                soil.activeNLoss = 0.0
                soil.stableNLoss = 0.0
                soil.NH4Loss = 0.0

        # Mineralization from Active N pool is:
        Nminact = minRate * (tempFac * waterFac) ** 0.5 * activeN
        soil.listOfSoilLayers[x].nMinAct = Nminact

        # Update Stable N
        stableN = max(0, stableN - soil.stableNLoss)

        # Update Active N
        if x == 0:
            activeN -= soil.listOfSoilLayers[x].activeNPerc
        else:
            activeN -= soil.listOfSoilLayers[x].activeNPerc
            activeN += soil.listOfSoilLayers[x-1].activeNPerc

        activeN = max(0, activeN
                      - soil.listOfSoilLayers[x].nMinAct)

        # N moves between the Active and Stable pools to maintain an equilibrium as:
        Ntrans = 0.00001 * (activeN * (1 / FracN - 1) - stableN)
        soil.listOfSoilLayers[x].nTrans = Ntrans

        # Update NH4
        if x == 0:
            NH4 = max(0, NH4-soil.NH4Loss)

        # Concentration (kg N/mm H20) of NH4 in a soil layer is:
        NH4Conc = 0.0
        if SW != 0:
            NH4Conc = (1 - math.exp(-SW / soil.listOfSoilLayers[x].satWater)) * NH4/SW
        soil.listOfSoilLayers[x].NH4Conc = NH4Conc

        NH4Perc = NH4Conc * perc
        soil.listOfSoilLayers[x].NH4Perc = NH4Perc


#---------------------------------------------------------------------------
# Function: daily_soil_nitrogen_update
# Updates the nitrogen pools in the soil for each layer
#---------------------------------------------------------------------------
def daily_soil_nitrogen_update(soil, jday, year, addedN):

    for x in range(0, len(soil.listOfSoilLayers)):

        # UPDATE NO3 POOL
        NO3 = soil.listOfSoilLayers[x].NO3
        NO3 -= soil.listOfSoilLayers[x].denitrification

        if x == 0:
            NO3 -= soil.NO3Runoff

        if x == 0:
            NO3 -= soil.listOfSoilLayers[x].NO3Perc
        else:
            NO3 -= soil.listOfSoilLayers[x].NO3Perc
            NO3 += soil.listOfSoilLayers[x - 1].NO3Perc

        NO3 += soil.listOfSoilLayers[x].nitrification
        soil.listOfSoilLayers[x].NO3 = NO3

        # UPDATE NH4 POOL
        NH4 = soil.listOfSoilLayers[x].NH4
        NH4 = max(0, NH4 - soil.listOfSoilLayers[x].totNitriVolatil)

        if x == 0:
            NH4 -= soil.NH4Runoff

        if x == 0:
            NH4 -= soil.NH4Loss

        if x == 0:
            NH4 -= soil.listOfSoilLayers[x].NH4Perc
        else:
            NH4 -= soil.listOfSoilLayers[x].NH4Perc
            NH4 += soil.listOfSoilLayers[x-1].NH4Perc

        if x == 0:
            NH4 = max(0, NH4
                    + soil.listOfSoilLayers[x].nMinAct + soil.freshMin
                    * 0.8 + (addedN*0.1))
        else:
            NH4 = max(0, NH4 + soil.listOfSoilLayers[x].nMinAct)

        soil.listOfSoilLayers[x].NH4 = NH4

        # UPDATE ACTIVE N POOL
        activeN = soil.listOfSoilLayers[x].activeN

        if x == 0:
            activeN = max(0, activeN - soil.activeNLoss)

        if x == 0:
            activeN -= soil.listOfSoilLayers[x].activeNPerc
        else:
            activeN -= soil.listOfSoilLayers[x].activeNPerc
            activeN += soil.listOfSoilLayers[x-1].activeNPerc

        activeN = max(0, activeN
                      - soil.listOfSoilLayers[x].nMinAct)

        activeN -= soil.listOfSoilLayers[x].nTrans

        if x == 0:
            activeN = (activeN + soil.freshMin*0.2 + addedN*0.9)

        soil.listOfSoilLayers[x].activeN = activeN

        # UPDATE STABLE N POOL
        stableN = soil.listOfSoilLayers[x].stableN
        if x == 0:
            stableN = max(0, stableN - soil.stableNLoss)

        stableN = max(0, stableN + soil.listOfSoilLayers[x].nTrans)

        if x == 0:
            stableN = max(0, stableN + 0)

        soil.listOfSoilLayers[x].stableN = stableN

        # UPDATE FRESH N POOL
        soil.topLayerFreshN = max(0, soil.topLayerFreshN - soil.freshMin
                                  - soil.freshDecomp - soil.freshNLoss)
