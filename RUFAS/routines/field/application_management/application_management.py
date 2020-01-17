"""
RUFAS: Ruminant Farm Systems Model
File name: application_management.py

Description:

Author(s): William Donovan, wmdonovan@wisc.edu
            Jacob Johnson, jacob8669@gmail.com
"""


class Application:

    def __init__(self, app_data, time):
        self.manure = Application.Manure(app_data["manure"], time)
        self.fertilizer = Application.Fertilizer(app_data["fertilizer"], time)
        self.tillage = Application.Tillage(app_data["tillage"], time)
        self.application_type = str(app_data['application_type']).lower()

        self.manure_day = False
        self.fertilizer_day = False
        self.tillage_day = False

    class Manure:
        """
        An instance of this class represents a particular manure and the date
        of its application
        """

        def __init__(self, manure_data, time):
            """
            Input:
                manure_data: a dictionary which stores the information for this manure
            """

            default_years = application_years(manure_data, time, "manure")

            self.type = manure_data['type']
            self.year = manure_data['year']
            self.day = manure_data['day']
            self.mass = manure_data['mass']
            self.P_frac = manure_data['P_frac']
            self.N_frac = manure_data['N_frac']
            self.NH4_frac = manure_data['NH4_frac']
            self.WIP_frac = manure_data['WIP_frac']
            self.WOP_frac = manure_data['WOP_frac']
            self.dry_matter = manure_data['dry_matter']
            self.percent_cover = manure_data['percent_cover']
            self.depth = [x / 10 for x in manure_data['depth']]
            self.surface_percent = manure_data['surf_perc']

            for app_year in default_years:
                # TODO: need default values
                self.type.append("DAIRY")
                self.year.append(app_year)
                self.day.append(-1)
                self.mass.append(1500)
                self.P_frac.append(0.007)
                self.N_frac.append(0)
                self.NH4_frac.append(0)
                self.WIP_frac.append(0.6)
                self.WOP_frac.append(0.05)
                self.dry_matter.append(0.05)
                self.percent_cover.append(0.95)
                self.depth.append(0)
                self.surface_percent.append(1)

    class Fertilizer:
        """
        An instance of this class represents a particular fertilizer and the date
        of its application
        """

        def __init__(self, fert_data, time):
            """
            Input:
                fert_data: a dictionary which holds the rest of the information about
                    this fertilizer
            """

            default_years = application_years(fert_data, time, "fertilizer")

            self.year = fert_data['year']
            self.day = fert_data['day']
            self.mass = fert_data['mass']
            self.depth = [x / 10 for x in fert_data['depth']]
            self.surface_percent = fert_data['surf_perc']

            for app_year in default_years:
                # TODO: need default values
                self.year.append(app_year)
                self.day.append(-1)
                self.mass.append(100)
                self.depth.append(0)
                self.surface_percent.append(1)

    class Tillage:
        """
        An instance of this class represents a particular tillage and the date
        of its application
        """

        def __init__(self, tillage_data, time):
            """
            Input:
                tillage_data: a dictionary which stores the information for this tillage
            """

            default_years = application_years(tillage_data, time, "tillage")

            self.year = tillage_data['year']
            self.day = tillage_data['day']
            self.percent_incorporated = tillage_data['perc_incorporated']
            self.percent_mixed = tillage_data['perc_mixed']
            self.depth = [x / 10 for x in tillage_data['depth']]

            for app_year in default_years:
                self.year.append(app_year)
                self.day.append(-1)
                self.percent_incorporated.append(.8)
                self.percent_mixed.append(.6)
                # in cm
                self.depth.append(25)


def application_years(app_data, time, application):
    """
    Definition:
        Determine years in which each application occurs and construct list
        for module use.

    Input:
        app_data: data representing the given application set
        application: the type of application represented by app_data
    """

    years = app_data['app_years']
    repeat = app_data['repeat']
    app_years = []

    # if years is not empty
    if len(years) != 0:
        for year in years:
            if year - time.start_year >= len(time.years) or year - time.start_year < 0:
                print('\nCannot apply', application, 'in year', year,
                      'because', year, '\nis outside of the scope of the simulation.')
            else:
                if year not in app_years:
                    app_years.append(year)
                    if repeat != 0:
                        temp_year = year + repeat
                        while temp_year - time.start_year < len(time.years):
                            if temp_year not in app_years:
                                app_years.append(temp_year)
                            temp_year += repeat

    app_years.sort()
    return app_years


def check_conditions(S, application, weather, time, i, application_type):
    """
    Description:
        Function: check_conditions
        Calculates if there will be rain within two days from a certain day
        or if the soil profile is too wet to have applications
    Input:
        S: the soil profile– abbreviated here from soil to reduce line length
        application: an instance of the application object
        weather:
        time:
        i: the number of the application for which conditions are being checked
        application_type: the type of application for which conditions are
                            being checked
    :return: recursively iterate application (move forward one or two days)
                until conditions are correct.

    """
    day = time.day
    year = time.year

    # if soil profile is too wet to apply manure
    if S.soil_layers[0].soil_water > S.soil_layers[0].fc_water:
        return iterate_application(application, weather, time, i, application_type)

    # if it rains on the current day
    if weather.rainfall[year - 1][day - 1] >= 1.0:
        return iterate_application(application, weather, time, i, application_type)

    # if it rains on the following day
    if day >= len(weather.rainfall[year - 1]):
        if year < len(weather.rainfall):
            year += 1
            day = 0
        else:
            return False
    if weather.rainfall[year - 1][day] >= 1.0:
        return iterate_application(application, weather, time, i, application_type)

    # if it rains on the 2nd day
    if day + 1 >= len(weather.rainfall[year - 1]):
        if year < len(weather.rainfall):
            year += 1
            day = -1
        else:
            return False
    if weather.rainfall[year - 1][day + 1] >= 1.0:
        return iterate_application(application, weather, time, i, application_type)

    return False


def iterate_application(application, weather, time, i, application_type):
    """
    Description:
        Moves applications to the next day– called from check_conditions.
    Input:
        application: an instance of the application object
        weather:
        time:
        i: the number of the application in the list being iterated
        application_type: the type of application being iterated
    """

    if application_type != -1:

        day = time.day
        year = time.year

        if application_type == 'm':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    application.manure.year[i] += 1
                    application.manure.day[i] = 0
            else:
                application.manure.day[i] += 1
        elif application_type == 'f':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    application.fertilizer.year[i] += 1
                    application.fertilizer.day[i] = 0
            else:
                application.fertilizer.day[i] += 1
        elif application_type == 't':
            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    application.tillage.year[i] += 1
                    application.tillage.day[i] = 0
            else:
                application.tillage.day[i] += 1

    return True
