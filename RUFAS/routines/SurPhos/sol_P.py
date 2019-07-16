
# calculates the amount of phosphorus lost from the soil
# profile in runoff

# convert soil P from KG/HA to MG/KG

from math import exp, log


def update_all(S, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall
    runoff = weather.runoff

    S.soil_P[1] = S.labile_P_layer[1] / S.bulk_density_layer[1] \
                  / S.thick_layer[1] / 0.1
    S.soil_P[2] = S.labile_P_layer[2] / S.bulk_density_layer[2] \
                  / S.thick_layer[2] / 0.1

    slope = [0, 0, 0]
    inter = [0, 0, 0]
    DRP = [0, 0, 0]
    water = [0, 0, 0]

    slope[1] = 173.51 * (S.clay_layer[1] / 100.0) + 8.48
    slope[2] = 173.51 * (S.clay_layer[2] / 100.0) + 8.48
    inter[1] = 4.726 * slope[1] - 8.97
    inter[2] = 4.726 * slope[2] - 8.97

    DRP[1] = min(40.0, exp((S.soil_P[1] * 1.5 - inter[1] / slope[1])))
    DRP[2] = min(40.0, exp((S.soil_P[2] * 1.5 - inter[2] / slope[2])))

    water[1] = max(0.0, (-0.07 * log(S.depths_layer[1] / 2.54 + 0.6))
                   * rainfall[year][day])
    water[2] = max(0.0, (-0.07 * log(S.depths_layer[2] / 2.54 + 0.6))
                   * rainfall[year][day])

    # compute soluble P lost in surface runoff in KG/HA

    soil_runoff_P = min(S.labile_P_layer[1],
                        S.soil_P[1] * 0.005 * runoff[year][day] * 0.01)

    leach_P = min(S.labile_P_layer[1], soil_runoff_P * water[1] * 0.01)

    seep_P = min(S.labile_P_layer[2], DRP[2] * water[2] * 0.01)

    if soil_runoff_P < 0.0:
        soil_runoff_P = 0.0

    if leach_P < 0.0:
        leach_P = 0.0

    S.labile_P_layer[1] -= soil_runoff_P - leach_P
    S.labile_P_layer[2] += leach_P - seep_P
    S.labile_P_layer[3] += seep_P

    if S.labile_P_layer[1] < 0.0:
        S.labile_P_layer[1] = 0.0

    # compute soluble P lost in runoff in KG and add to running total

    soil_DRP = soil_runoff_P * S.area
    S.SRP_sum += soil_DRP
