'''
RUFAS: Ruminant Farm Systems Model

File name: evapotranspiration.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating water evapotranspiration on a given day by calculating:
                1. Potential Evapotranspiration
                2. Crop transpiration
                3. Sublimation and Soil Evaporation.
                4. Soil Evaporation by soil layer
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.

Soil attribute definitions

    LHV = latent heat of vaporization (MJ kg^-1)

    E0 = potential evotranspiration (mm d^-1)

    H0 = extraterrestrial radiation (mm m^-2d^-1)

    Tmax = maximum air temperature for a given day (ºC)

    Tmin = minimum air temperature for a given day (ºC)

    Tavg = mean air temperature for a given day (ºC)

    Etrans = maximum transpiration on a given day (mm H20)

    LAI = Leaf Area Index (calculated in Crop Routine)

    Esoil = maximum soil evaporation/sublimation on a given day (mm H20)

    SoilCov = soil cover index

    BioMass = aboveground biomass and residue (kg ha^-1)

    Esoil_z = evaporation demand at depth z (mm H20)

    z = depth below soil surface (mm)

    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H20)

    WP = soil water content held at wilting point (mm H20)

    FC = field capacity (mm H20)

Soil values updated by calling update_all():
    soil.E0
    soil.E0_sum
    soil.Etrans
    soil.Esoil
    soil.listOfSoilLayers.topEsoil
    soil.listOfSoilLayers.bottomEsoil
    soil.listOfSoilLayers.layerEsoil

'''
###############################################################################

from math import exp


#
# This function calls all the necessary functions to update information related
# to evapotranspiration
#
def update_all(soil, crop, weather, time):
    calc_potential_evap(soil, crop, weather, time)

    calc_crop_transpiration(soil, crop)

    calc_soil_evap(soil, crop)

    update_Esoil_z(soil)


#
# Calculates potential evapotranspiration E0 using the Hargreaves method
# "pseudocode_SC_soilhydrology.docx" 2.B.1
#
def calc_potential_evap(soil, crop, weather, time):
    H0 = weather.radiation[time.year-1][time.day-1]

    Tmax = weather.T_max[time.year-1][time.day-1]
    Tmin = weather.T_min[time.year-1][time.day-1]
    Tavg = weather.T_avg[time.year-1][time.day-1]

    LHV = calc_LHV(Tavg)

    E0 = (0.0023 * H0 * ((Tmax - Tmin) ** 0.5) * (Tavg + 17.8)) / LHV

    soil.E0 = max(0.001, E0)

    if crop.crops_list["corn"].planting_date <= time.day <= crop.crops_list["corn"].harvest_date:
        soil.E0_sum += soil.E0


#
# Calculates LHV (latent heat of vaporization (MJ kg^-1)) for use in
# determining potential evapotranspiration
# "pseudocode_SC_soilhydrology.docx" 2.B.2
#
def calc_LHV(Tavg):
    return 2.501 - (2.361 * (10 ** (-3)) * Tavg)


#
# Calculates crop transpiration as a function of maximum transpiration on a
# given day and Leaf Area Index (calculated in the Crop Routine file
# leaf_area_index.py)
# "pseudocode_SC_soilhydrology.docx" 2.B.3
#
def calc_crop_transpiration(soil, crop):
    LAI = crop.crops_list["corn"].LAI_actual  # TODO: Crop Flag
    if 0 <= LAI <= 3.0:
        soil.Etrans = (soil.E0 * LAI) / 3.0
    else:
        soil.Etrans = soil.E0


#
# Calculates sublimation and soil evaporation
# "pseudocode_SC_soilhydrology.docx" 2.B.4/6
#
def calc_soil_evap(soil, crop):
    SoilCov = calc_soil_cov(crop)

    # "pseudocode_SC_soilhydrology.docx" 2.B.4
    Esoil = soil.E0 * SoilCov

    # "pseudocode_SC_soilhydrology.docx" 2.B.6
    soil.Esoil = min(Esoil, ((Esoil * soil.E0) / (Esoil + soil.Etrans)))


#
# Calculates soil cover for use in calculating soil evaporation
# "pseudocode_SC_soilhydrology.docx" 2.B.5
#
def calc_soil_cov(crop):
    bio_AG = crop.crops_list["corn"].bio_AG  #TODO: Crop Flag
    residue = crop.crops_list["corn"].residue
    BioMass = bio_AG + residue

    return exp(-5.0 * (10 ** -5) * BioMass)


#
# Calculates the Esoil for each layer of soil in a given profile as a function
# of the evaporation demand between the soil layers above and below.
# "pseudocode_SC_soilhydrology.docx" 2.B.7-10
#
def update_Esoil_z(soil):
    for x in range(0, len(soil.listOfSoilLayers)):
        curr_layer = soil.listOfSoilLayers[x]
        FC = curr_layer.fcWater
        SW = curr_layer.currentSoilWaterMM
        WP = curr_layer.wiltingWater

        #
        # Calculate Esoil at a given depth
        # "pseudocode_SC_soilhydrology.docx" 2.B.7
        #
        if x == 0:
            curr_layer.topEsoil = 0
            z = curr_layer.bottomDepth
            exp_part = exp(2.374 - 0.00713 * z)

            curr_layer.bottomEsoil = soil.Esoil * (z / (z + exp_part))

        else:
            curr_layer.topEsoil = soil.listOfSoilLayers[x-1].bottomEsoil
            z = curr_layer.bottomDepth
            exp_part = exp(2.374 - 0.00713 * z)

            curr_layer.bottomEsoil = soil.Esoil * (z / (z + exp_part))

        #
        # Evaporation demand for a given soil layer is the difference between
        # evaporation demands at the top and bottom of the layer
        # "pseudocode_SC_soilhydrology.docx" 2.B.8
        #
        if SW > FC:
            layerEsoil = curr_layer.bottomEsoil - curr_layer.topEsoil
        #
        # When the water content of a soil layer is below field capacity, the
        # evaporative demand for the layer is reduced
        # "pseudocode_SC_soilhydrology.docx" 2.B.9
        #
        else:
            exp_part = exp(2.5 * (SW - FC) / (FC - WP))
            layerEsoil = (curr_layer.bottomEsoil - curr_layer.topEsoil) * exp_part

        #
        # In addition, the daily amount of water removed by evaporation is
        # limited to 80% of plant available water (SW - WP)
        # "pseudocode_SC_soilhydrology.docx" 2.B.10
        #
        curr_layer.layerEsoil = min(layerEsoil, 0.8 * (SW - FC))

        soil.listOfSoilLayers[x] = curr_layer
