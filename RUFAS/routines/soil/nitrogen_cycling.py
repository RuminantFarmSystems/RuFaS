"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the content of three organic N pools (Fresh, Active, and
             Stable) and two inorganic pools (NO3 and NH4) associated with a
             soil profile on a given day 

Soil attribute definitions

    NO3 = initial NO3 levels (mg/kg)

    z = depth of the soil layer's lower boundary

    OrgN = initial Organic N (Active + Stable) (mg/kg)

    OrgC = Organic carbon in a soil layer (%, user input)

    NH4 = initial NO4 levels (0 mg/kg)
    
    tempfac = temperature factor
    
    waterfac = water factor
    
    soilTemp = temperature of the soil layer (ºC)
    
    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H2O)

    WP = soil water content held at wilting point (mm H2O)

    FC = field capacity (mm H2O)
    
    SAT = saturated water content of the soil layer (mm H2O)

    DepthFac = volatilization depth factor

    z_mid = 5mm (assuming a 10mm top layer)

    NitrReg = nitrification regulator

    VolatilReg = volatilization regulator

    CECFac = volatilization cation exchange factor (0.15)

    TotNitriVolatil = total combined nitrification and volatilization (kg/ha)

    FracNitr = fraction of total that is nitrification

    FracVolatil = fraction of total that is volatilization

    Nitrification = mass of nitrification (kg/ha)

    Volatilization = mass of Volatilization

    NO3/NH4Conc1 = concentration of NO3 or NH4 in the top soil layer (kg N/mm H2O)

    w = sum of runoff and soil water for the layer

    NO3/NH4Runoff = mass of NO3 or NH4 loss in runoff from soil layer 1 (kg/ha)

    Cr = coefficient of extraction for runoff (0.1)

    NConc = concentration of nitrogen loss in erosion for each pool except
                    NO3 (mg/kg)

    BD = soil layer bulk density (g/cm^3)

    depth = soil layer thickness (mm)

    Eros_N_Loss = N mass loss in erosion for each pool(kg/ha)

    Sed = daily soil loss (Metric Tons/ha)

    ER = enrichment ratio

    NO3/NH4Conc = concentration of NO3 or NH4 for leaching (kg N / mm H2O)

    NO3/NH4_perc = mass of NO3 or NH4 loss in percolation water from all soil layers
                (kg/ha)

    DenitrN = denitrification (kg/ha)

    deNrate = user defined denitrification rate coefficient (0.1)

    OrgC = soil organic matter content (%)

    Nminact = mineralization from active N pool (kg/ha)

    CN = daily rate constant, ratio of Carbon to Nitrogen

    CP = ratio of the residue

    Decay = decay rate constant defining the fraction of residue decomposed

    minCoeff = fresh residue mineralization coefficient (0.05)

    resComp = nutrient cycling residue decomposition factor

    FreshMin = mineralization of Fresh N (kg/ha)

    Ntrans = nitrogen transferred between the active and stable pools

    FracN = fraction of humic nitrogen in the active pool (0.02)


Soil values updated by calling update_all():

    soil_layers

    values updated in each soil layer:

        NO3
        NH4
        tempFac
        waterFac
        volatilization
        activeN
        orgN
        stableN


"""

###############################################################################

from math import exp, log, e


#
# This function calls all the necessary functions to update information related
# to nitrogen cycling. The order in which each method is called is significant
# and is still being worked out.
#
def update_all(soil, weather, time):

    calc_tempFactors(soil)

    calc_waterFactors(soil)

    nitrification_volatilization(soil)

    leaching_runoff_erosion(soil)

    leaching_update(soil)

    denitrification(soil)

    mineralization_decomp(soil)

    humus_mineralization(soil)

    added_manure_N(soil, weather, time)


#
# Helper method used to calculate the temperature factor used to
# calculate nitrification, volatilization, denitrification, and mineralization
# for each layer
# "pseudocode_soil" S.4.B.1
#
def calc_tempFactors(soil):
    for layer in soil.soil_layers:
        soilTemp = layer.temperature

        exp_part = exp(9.93 - 0.312 * soilTemp)
        tempFac = max(0, soilTemp / (soilTemp + exp_part))

        layer.tempFac = tempFac


#
# Helper method used to calculate the water factor used to
# calculate nitrification, volatilization, denitrification, and mineralization
# for each layer
# "pseudocode_soil" S.4.B.2
#
def calc_waterFactors(soil):
    for layer in soil.soil_layers:
        SW = layer.soil_water
        FC = layer.fcWater
        WP = layer.wiltingWater
        SAT = layer.satWater

        if SW > FC:
            waterFac = (SAT - SW) / (SAT - FC)
        else:
            waterFac = (SW - WP) / (FC - WP)

        layer.waterFac = waterFac


#
# Nitrification is the transfer of NH4 to NO3, this method determines when that
# transfer occurs and calculates the magnitude of that transfer.
# "pseudocode_soil" S.4.B
#
def nitrification_volatilization(soil):
    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]

        tempFac = layer.tempFac

        waterFac = layer.waterFac

        # "pseudocode_soil" S.4.B.3
        if x == 0:
            z_mid = 5
        else:
            z_mid = (layer.bottomDepth + soil.soil_layers[x - 1].bottomDepth) / 2

        exp_part = exp(4.706 - 0.0305 * z_mid)
        DepthFac = 1 - (z_mid / (z_mid + exp_part))

        # "pseudocode_soil" S.4.B.5
        CECFac = 0.15
        VolatilReg = tempFac * DepthFac * CECFac

        #
        # Nitrification only occurs when the soil temperature of a given layer
        # exceeds 5ºC
        #
        NitrReg = 0
        if layer.temperature >= 5:
            # "pseudocode_soil" S.4.B.4
            NitrReg = tempFac * waterFac

        # "pseudocode_soil" S.4.B.6
        exp_part = exp(-NitrReg - VolatilReg)
        TotNitriVolatil = layer.NH4 * (1 - exp_part)

        TotNitriVolatil = min(layer.NH4, TotNitriVolatil)
        layer.NH4 -= TotNitriVolatil

        # "pseudocode_soil" S.4.B.7
        FracNitr = 1 - exp(-NitrReg)

        # "pseudocode_soil" S.4.B.8
        FracVolatil = 1 - exp(-VolatilReg)

        # "pseudocode_soil" S.4.B.9/10
        if FracNitr + FracVolatil == 0:
            Nitrification = 0
            Volatilization = 0

        else:
            Nitrification = (FracNitr / (FracNitr + FracVolatil)) * \
                            TotNitriVolatil
            Volatilization = (FracVolatil / (FracNitr + FracVolatil)) * \
                             TotNitriVolatil

        layer.nitrification = Nitrification
        layer.volatilization = Volatilization
        layer.totNitriVolatil = TotNitriVolatil

        layer.NO3 += Nitrification


#
# Calculates/updates N lost in leaching, runoff, and erosion
# "pseudocode_soil" S.4.C
#
def leaching_runoff_erosion(soil):
    # prev_NO3_perc = 0
    # prev_NH4_perc = 0
    # prev_active_perc = 0

    for layer in soil.soil_layers:

        #
        # N in leaching is added to the next deeper layer. These values are
        # calculated as the last step of each iteration through the loop. They
        # are initialized at 0 because there is no nitrogen gained through
        # leaching for the first layer.
        #
        # Toggle these comments to change order
        # of operations + updates.
        #
        # layer.NO3 += prev_NO3_perc
        # layer.NH4 += prev_NH4_perc
        # layer.activeN += prev_active_perc

        SW = layer.soil_water
        FC = layer.fcWater
        SAT = layer.satWater

        BD = layer.bulkDensity
        depth = layer.depth

        #
        # the coefficient of extraction for leaching is calibrated to 2.5
        # for layers 2 and 3
        #
        Cl = 2.5

        #
        # All N lost in runoff and erosion is removed from layer 1
        #
        if layer.name == "Layer1":

            # "pseudocode_soil" S.4.C.1
            runoff = soil.runoff
            w = runoff + SW

            if w == 0:
                NO3RunoffConc = 0
                NH4RunoffConc = 0

            else:
                exp_part = exp(-w / SAT)
                NO3RunoffConc = layer.NO3 * (1 - exp_part) / w
                NH4RunoffConc = layer.NH4 * (1 - exp_part) / w

            Cr = 0.1

            # "pseudocode_soil" S.4.C.2
            NO3Runoff = NO3RunoffConc * Cr * runoff
            NH4Runoff = NH4RunoffConc * runoff

            # it is important for the order of operations that the pools are
            # updated after each process and that those updated values are used
            # thereafter
            soil.NO3_runoff = min(layer.NO3, NO3Runoff)
            layer.NO3 -= soil.NO3_runoff
            soil.NH4_runoff = min(layer.NH4, NH4Runoff)
            layer.NH4 -= soil.NH4_runoff

            # "pseudocode_soil" S.4.C.3
            activeNErosConc = (100 * layer.activeN) / (BD * depth)
            stableNErosConc = (100 * layer.stableN) / (BD * depth)
            freshNErosConc = (100 * layer.topLayerFreshN / (BD * depth))
            NH4ErosConc = (100 * layer.NH4 / (BD * depth))

            Eros_activeN_loss = 0
            Eros_stableN_loss = 0
            Eros_freshN_loss = 0
            Eros_NH4_loss = 0

            Sed = soil.sedimentYield

            if Sed > 0:
                # "pseudocode_soil" S.4.C.5
                ER = exp(1.21 - 0.16 * log(Sed * 1000))

                # "pseudocode_soil" S.4.C.4
                Eros_activeN_loss = 0.001 * activeNErosConc * Sed * ER
                Eros_stableN_loss = 0.001 * stableNErosConc * Sed * ER
                Eros_freshN_loss = 0.001 * freshNErosConc * Sed * ER
                Eros_NH4_loss = 0.001 * NH4ErosConc * Sed * ER

            soil.activeN_erosion = min(layer.activeN, Eros_activeN_loss)
            layer.activeN -= soil.activeN_erosion

            soil.stableN_erosion = min(layer.stableN, Eros_stableN_loss)
            layer.stableN -= soil.stableN_erosion

            soil.freshN_erosion = min(layer.topLayerFreshN, Eros_freshN_loss)
            layer.topLayerFreshN -= soil.freshN_erosion

            soil.NH4_erosion = min(layer.NH4, Eros_NH4_loss)
            layer.NH4 -= soil.NH4_erosion

            #
            # the coefficient of extraction for leaching is calibrated to 1.0
            # for layer 1
            #
            Cl = 1.0

        # "pseudocode_soil" S.4.C.6-8
        perc = layer.perc
        NO3_perc = 0
        NH4_perc = 0
        active_perc = 0

        if perc > 0:
            # "pseudocode_soil" S.4.C.6
            NO3_perc_conc = layer.NO3 / (FC + perc)
            NH4_perc_conc = layer.NH4 / (FC + perc)

            # "pseudocode_soil" S.4.C.7
            active_conc = layer.activeN / (FC + perc) / 50

            # "pseudocode_soil" S.4.C.8
            NO3_perc = NO3_perc_conc * perc / Cl
            NH4_perc = NH4_perc_conc * perc
            active_perc = active_conc * perc

        #
        # N in leaching is removed from a given soil layer and added to the
        # next deeper layer (note that prev_NO3/NH4/active_perc are added to the
        # current pools as the first step of the next iteration through the
        # loop. These values are set to 0 before the loop begins because there
        # is no N gained through leaching in the first layer)
        #

        layer.NO3_perc = min(layer.NO3, NO3_perc)
        layer.NH4_perc = min(layer.NH4, NH4_perc)
        layer.active_perc = min(layer.activeN, active_perc)

        # layer.NO3 -= NO3_perc
        # layer.NH4 -= NH4_perc
        # layer.activeN -= active_perc
        #
        # prev_NO3_perc = NO3_perc
        # prev_NH4_perc = NH4_perc
        # prev_active_perc = active_perc


#
# If leaching occurs separately for each layer, this helper method updates each
# pool after the fact
#
def leaching_update(soil):
    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]
        layer.NO3 -= layer.NO3_perc
        layer.NH4 -= layer.NH4_perc
        layer.activeN -= layer.active_perc

        if x != 0:
            prev_layer = soil.soil_layers[x - 1]
            layer.NO3 += prev_layer.NO3_perc
            layer.NH4 += prev_layer.NH4_perc
            layer.activeN += prev_layer.active_perc


#
# Calculates denitrification (the bacterial conversion of NO3 to gas under
# anaerobic conditions).
# "pseudocode_soil" S.4.D
#
def denitrification(soil):
    for layer in soil.soil_layers:
        OrgC = layer.orgC
        deNrate = layer.deNrate
        SW = layer.soil_water
        FC = layer.fcWater

        tempFac = layer.tempFac

        # "pseudocode_soil" S.4.D.1
        DenitrN = 0
        if SW > FC:
            exp_part = exp(-deNrate * tempFac * OrgC)
            DenitrN = layer.NO3 * (1 - exp_part)

        DenitrN = min(layer.NO3, DenitrN)
        layer.NO3 -= DenitrN

        layer.denitrification = DenitrN


#
# Calculates mineralization and decomposition processes for the nitrogen cycle.
# "pseudocode_soil" S.4.E
#
def mineralization_decomp(soil):
    minrate = 0.0003
    for layer in soil.soil_layers:
        activeN = layer.activeN
        tempFac = layer.tempFac
        waterFac = layer.waterFac

        # "pseudocode_soil" S.4.E.1
        nMinAct = 0
        if layer.temperature > 0:
            nMinAct = minrate * ((tempFac * waterFac) ** 0.5) * activeN

        nMinAct = min(layer.activeN, nMinAct)
        layer.activeN -= nMinAct
        layer.NH4 += nMinAct

        #
        # Decomposition and mineralization of Fresh N only occur in the first
        # soil layer.
        #
        if layer.name == "Layer1":
            FreshN = layer.topLayerFreshN
            NO3 = layer.NO3
            res = soil.residue
            BD = layer.bulkDensity
            depth = layer.bottomDepth

            # "pseudocode_soil" S.4.E.2
            CN = 0
            if FreshN + NO3 > 0:
                CN = (0.58 * res) / (FreshN + NO3)

            #
            # TODO: these values are taken from phosphorus_cycling.py which is incomplete
            #
            freshOrgP = (res * 0.0003) * BD * depth / 100
            labileP = layer.labileP

            # "pseudocode_soil" S.4.E.3
            CP = 0
            if freshOrgP + labileP > 0:
                CP = (0.58 * res) / (freshOrgP + labileP)

            minCoeff = 0.05

            # "pseudocode_soil" S.4.E.5
            term1 = exp(-0.693 * (CN - 25) / 25)
            term2 = exp(-0.693 * (CP - 200) / 200)
            term3 = 1.0

            resComp = min(term1, term2, term3)

            # "pseudocode_soil" S.4.E.4
            Decay = minCoeff * resComp * ((tempFac * waterFac) ** 0.5)

            # decay rate used in calculating residue for crop
            soil.decayRate = Decay

            # "pseudocode_soil" S.4.E.6
            FreshMin = Decay * FreshN

            FreshMin = min(layer.topLayerFreshN, FreshMin)
            layer.topLayerFreshN -= FreshMin

            layer.activeN += (0.2 * FreshMin)
            layer.NH4 += (0.8 * FreshMin)


#
# Nitrogen is allowed to move between the Active and Stable organic pools,
# representing humus mineralization. This method accounts for that process
# "pseudocode_soil" S.4.F
#
def humus_mineralization(soil):
    for layer in soil.soil_layers:
        activeN = layer.activeN
        stableN = layer.stableN
        FracN = 0.02

        # "pseudocode_soil" S.4.F.1
        Ntrans = 0.00001 * (activeN * ((1 / FracN) - 1) - stableN)

        layer.activeN -= Ntrans
        layer.stableN += Ntrans

        layer.nTrans = Ntrans


def added_manure_N(soil, weather, time):
    totalN = weather.manureN[time.year - 1][time.day - 1]

    activeN = totalN * 0.65
    stableN = totalN * 0.15
    NH4 = totalN * 0.20

    soil.soil_layers[0].activeN += activeN
    soil.soil_layers[0].stableN += stableN
    soil.soil_layers[0].NH4 += NH4

