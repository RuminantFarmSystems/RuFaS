################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# application_management.py
#
# Authors: Jacob Johnson, jacob8399@gmail.com
#
################################################################################


# ---------------------------------------------------------------------------
# Function: check_conditions
# Calculates if there will be rain within two days from a certain day
# or if the soil profile is too wet to have applications
# ---------------------------------------------------------------------------
def check_conditions(time, weather, S, i, application):
    day = time.day
    year = time.year

    # if soil profile is too wet to apply manure
    if S.soil_layers[0].soil_water > S.soil_layers[0].fc_water:
        return iterate_application(time, weather, S, i, application)

    # if it rains on the current day
    if weather.rainfall[year - 1][day - 1] >= 1.0:
        return iterate_application(time, weather, S, i, application)

    # if it rains on the following day
    if day >= len(weather.rainfall[year - 1]):
        if year < len(weather.rainfall):
            year += 1
            day = 0
        else:
            return False
    if weather.rainfall[year - 1][day] >= 1.0:
        return iterate_application(time, weather, S, i, application)

    # if it rains on the 2nd day
    if day + 1 >= len(weather.rainfall[year - 1]):
        if year < len(weather.rainfall):
            year += 1
            day = -1
        else:
            return False
    if weather.rainfall[year - 1][day + 1] >= 1.0:
        return iterate_application(time, weather, S, i, application)

    return False


# ---------------------------------------------------------------------------
# Function: iterate_application
# Moves applications to the next day
# ---------------------------------------------------------------------------
def iterate_application(time, weather, S, i, application):

    if application != -1:

        day = time.day
        year = time.year

        if application == 'm':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    S.manure.year[i] += 1
                    S.manure.day[i] = 0
            else:
                S.manure.day[i] += 1
        elif application == 'f':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    S.fertilizer.year[i] += 1
                    S.fertilizer.day[i] = 0
            else:
                S.fertilizer.day[i] += 1
        elif application == 't':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    S.tillage.year[i] += 1
                    S.tillage.day[i] = 0
            else:
                S.tillage.day[i] += 1

    return True
