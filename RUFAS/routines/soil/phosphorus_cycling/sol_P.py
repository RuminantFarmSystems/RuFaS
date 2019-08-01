
# calculates the amount of phosphorus lost from the soil
# profile in runoff

# convert soil P from KG/HA to MG/KG

from math import exp, log


def update_all(S, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall
    runoff = S.runoff

    S.soil_P[0] = S.listOfSoilLayers[0].labile_P / S.listOfSoilLayers[0].bulkDensity \
                  / S.thickness_cm[0] / 0.1
    S.soil_P[1] = S.listOfSoilLayers[1].labile_P / S.listOfSoilLayers[1].bulkDensity \
                  / S.thickness_cm[1] / 0.1

    S.slope[0] = 173.51 * (S.listOfSoilLayers[0].clay / 100.0) + 8.48
    S.slope[1] = 173.51 * (S.listOfSoilLayers[1].clay / 100.0) + 8.48
    S.inter[0] = 4.726 * S.slope[0] - 8.97
    S.inter[1] = 4.726 * S.slope[1] - 8.97

    S.DRP[0] = min(40.0, exp((S.soil_P[0] * 1.5 - S.inter[0] / S.slope[0])))
    S.DRP[1] = min(40.0, exp((S.soil_P[1] * 1.5 - S.inter[1] / S.slope[1])))

    S.water[0] = max(0.0, (-0.07 * log((S.listOfSoilLayers[0].bottom_depth_cm / 2.54) + 0.6))
                   * rainfall[year - 1][day - 1])
    S.water[1] = max(0.0, (-0.07 * log((S.listOfSoilLayers[1].bottom_depth_cm / 2.54) + 0.6))
                   * rainfall[year - 1][day - 1])

    # compute soluble P lost in surface runoff in KG/HA

    soil_runoff_P = min(S.listOfSoilLayers[0].labile_P,
                        S.soil_P[0] * 0.005 * runoff * 0.01)

    leach_P = min(S.listOfSoilLayers[0].labile_P, soil_runoff_P * S.water[0] * 0.01)

    seep_P = min(S.listOfSoilLayers[1].labile_P, S.DRP[1] * S.water[1] * 0.01)

    if soil_runoff_P < 0.0:
        soil_runoff_P = 0.0

    if leach_P < 0.0:
        leach_P = 0.0

    S.listOfSoilLayers[0].labile_P = S.listOfSoilLayers[0].labile_P - soil_runoff_P - leach_P
    S.listOfSoilLayers[1].labile_P += leach_P - seep_P
    S.listOfSoilLayers[2].labile_P += seep_P

    S.listOfSoilLayers[0].labile_P = max(0.0, S.listOfSoilLayers[0].labile_P)

    # compute soluble P lost in runoff in KG and add to running total

    soil_DRP = soil_runoff_P * S.area
    S.SRP_sum += soil_DRP
