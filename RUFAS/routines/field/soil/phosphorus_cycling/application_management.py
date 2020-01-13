"""
RUFAS: Ruminant Farm Systems Model

File name: application_management.py

Author(s): Jacob Johnson, jacob8399@gmail.com

Description: This file checks if an application could be applied
             based off of certain conditions. If it cannot be applied,
             then it is moved to a different day.
"""


def check_conditions(time, weather, S, i, application):
    """Calculates if there will be rain within two days from a certain day
       or if the soil profile is too wet to have applications

    Input:
        time
        weather
        S: soil
        i: current iteration in the application
        application: type of application
    Returns:
        Bool: True being that the application could not be applied

    """
    day = time.day
    year = time.year

    # if soil profile is too wet to apply manure
    if S.soil_layers[0].soil_water > S.soil_layers[0].fc_water:
        return iterate_application(time, weather, S, i, application)

    # if it rains on the current day
    if weather.rainfall[year - 1][day - 1] >= 10.0:
        return iterate_application(time, weather, S, i, application)

    # if it rains on the following day
    if day >= len(weather.rainfall[year - 1]):
        if year < len(weather.rainfall):
            year += 1
            day = 0
        else:
            return False
    if weather.rainfall[year - 1][day] >= 10.0:
        return iterate_application(time, weather, S, i, application)

    # if it rains on the 2nd day
    if day + 1 >= len(weather.rainfall[year - 1]):
        if year < len(weather.rainfall):
            year += 1
            day = -1
        else:
            return False
    if weather.rainfall[year - 1][day + 1] >= 10.0:
        return iterate_application(time, weather, S, i, application)

    return False


def iterate_application(time, weather, S, i, application):
    """Moves an application to the next day after it is unable to be applied.

    Input:
        time
        weather
        S: soil
        i: current iteration in the application
        application: type of application
    Returns:
        Bool: always True meaning the application could not be applied
    """

    # the crop module calls the above method to determine if the crop can be planted
    # so the -1 is used to make sure this method is unused in that situation
    if application != -1:

        day = time.day
        year = time.year

        # each if statement must check that the day isn't the last
        # day in the year otherwise the year needs to be iterated also

        # manure
        if application == 'm':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    S.manure.year[i] += 1
                    S.manure.day[i] = 0
            else:
                S.manure.day[i] += 1
        # fertilizer
        elif application == 'f':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    S.fertilizer.year[i] += 1
                    S.fertilizer.day[i] = 0
            else:
                S.fertilizer.day[i] += 1
        # tillage
        elif application == 't':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    S.tillage.year[i] += 1
                    S.tillage.day[i] = 0
            else:
                S.tillage.day[i] += 1

    return True
