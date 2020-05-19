"""
RUFAS: Ruminant Farm Systems Model
File name: application_management.py

Description:

Author(s): William Donovan, wmdonovan@wisc.edu
            Jacob Johnson, jacob8669@gmail.com
"""


class BaseApplication:
    def __init__(self, app_data, app_type):
        self.year = app_data['year']
        self.day = app_data['day']

        self.type = app_type


class ApplicationManagement:

    def __init__(self, app_data, time):
        """
        Description:
            ApplicationManagement is an organizational object that aggregates the
            management objects for manure, fertilizer, and tillage.

        Args:
            app_data: data representing the applications specified in the JSON file
            time: an instance of the Time class specified in classes.py
        """

        self.managed_applications = {
            "manure": ApplicationManagement.ManureManagement(app_data['manure'], time),
            "fertilizer": ApplicationManagement.Fertilizer(app_data['fertilizer'], time),
            "tillage": ApplicationManagement.TillageManagement(app_data['tillage'], time)
        }

        self.management_scheme = str(app_data['management_scheme']).lower()

    class BaseApplicationManagement:
        def __init__(self, app_data, application_type, time):
            """
            Description:
                BaseApplicationManagement is the super class for all other
                application management objects. The class methods,
                set_default_years, check_conditions, and iterate_application
                allow for dynamic application specification and management
                during the simulation.

            Args:
                app_data: data defining the application manager specified in
                    the input JSON
                application_type: the type of application being managed
                time: an instance of the Time class specified in classes.py
            """
            self.application_type = application_type

            self.applications = {}

            self.default_years = []
            self.set_default_years(app_data, time)

        def set_default_years(self, app_data, time):
            """
            Definition:
                Determine years in which each application occurs and construct list
                for module use.

            Args:
                app_data: data representing the given application set
                time: an instance of the Time class specified in classes.py
            """

            years = app_data['app_years']
            repeat = app_data['repeat']

            # if there are years in which this application type occurs
            if len(years) != 0:
                for year in years:
                    # check specified application years against model boundaries
                    if year - time.start_year >= len(time.years) or year - time.start_year < 0:
                        print('\nCannot apply', self.application_type, 'in year', year,
                              'because', year, '\nis outside of the scope of the simulation.')
                    else:
                        # populate app_years with uniquely specified years
                        if year not in self.default_years:
                            self.default_years.append(year)
                            # populate app_years with repeat cycles
                            if repeat != 0:
                                temp_year = year + repeat
                                # until repeat hits model boundaries
                                while temp_year - time.start_year < len(time.years):
                                    if temp_year not in self.default_years:
                                        self.default_years.append(temp_year)
                                    temp_year += repeat

            self.default_years.sort()

        def check_conditions(self, soil, weather, time):
            """
            Description:
                Checks if environmental conditions are conducive to application.
                Iterates applications scheduled for non-conducive dates
            Args:
                soil: an instance of the Soil class specified in soil.py
                weather: an instance of the Weather class specified in classes.py
                    contains information about the environment
                time: an instance of the Time class specified in classes.py

            Returns:
                bool: True if conditions are conducive,
                        False (and iterate application) if otherwise
            """

            # the time object begins indexing at 1, but curr, next, and second
            # are in reference to the weather object which begins indexing at 0
            curr_day = time.day - 1
            curr_year = time.year - 1

            next_day = curr_day + 1
            next_year = curr_day + 1

            second_day = next_day + 1

            # if soil profile is too for application
            if soil.soil_layers[0].soil_water > soil.soil_layers[0].fc_water:
                self.iterate_application(weather, time)
                return False

            # if it rains on the current day
            if weather.rainfall[curr_year][curr_day] >= 1.0:
                self.iterate_application(weather, time)
                return False

            # boundary check the next day against length of the current year
            if next_day >= len(weather.rainfall[curr_year]):
                # boundary check the next year against length of simulation
                if next_year < len(weather.rainfall):
                    # update year and day to the start of the next year
                    curr_year += 1
                    curr_day = 0

                    next_day = curr_day + 1

                # the next day and current year are outside of the scope of the simulation
                else:
                    return False

            # if it rains on the following day
            if weather.rainfall[curr_year][next_day] >= 1.0:
                self.iterate_application(weather, time)
                return False

            curr_year = time.year - 1

            # boundary check the second day against length of the current year
            if second_day >= len(weather.rainfall[curr_year]):
                # boundary check the next year against length of simulation
                if next_year < len(weather.rainfall):
                    # update current year and day to the start of the next year
                    curr_year += 1
                    curr_day = 0

                    second_day = curr_day + 2
                # the second day and current year are outside of the scope of the simulation
                else:
                    return False

            # if it rains on the second day
            if weather.rainfall[curr_year][second_day] >= 1.0:
                self.iterate_application(weather, time)
                return False

            return True

        def iterate_application(self, weather, time):
            """
            Description:
                Moves applications to the next day– called from check_conditions.
            Args:
                weather: an instance of the Weather class specified in classes.py
                    contains information about the environment
                time: an instance of the Time class specified in classes.py
            """
            day = time.day
            year = time.year

            if day == len(weather.rainfall[year - 1]):
                if year < len(weather.rainfall):
                    self.applications[(year + 1, 0)] = self.applications.pop((year, day))
                else:
                    self.applications[(year, day + 1)] = self.applications.pop((year, day))

    class ManureManagement(BaseApplicationManagement):
        def __init__(self, manure_data, time):
            """
            Description:
                An instance of this class represents a particular manure and
                the date of its application
            Args:
                manure_data: a dictionary which stores the information for this manure
                time: an instance of the Time class specified in classes.py
            """
            super().__init__(manure_data, "manure", time)

            self.applications = {}

            application_no = len(manure_data['year'])
            for application in range(application_no):
                app_data = {}
                for variable_name in manure_data:
                    app_data[variable_name] = manure_data[variable_name].pop()
                self.applications[(app_data['year'], app_data['day'])] = self.Manure(app_data)

            for app_year in self.default_years:
                # TODO: Need default data
                default_data = {
                    'type': "DAIRY",
                    'year': app_year,
                    'day': -1,
                    'mass': 1500,
                    'P_frac': 0.007,
                    'N_frac': 0,
                    'NH4_frac': 0,
                    'WIP_frac': 0.6,
                    'WOP_frac': 0.05,
                    'DM': 0.05,
                    'percent_cover': 0.95,
                    'depth': 0.0,
                    'surface_percent': 1.0
                }
                self.applications[(default_data['year'], default_data['day'])] = self.Manure(default_data)

        class Manure(BaseApplication):
            def __init__(self, app_data):
                super().__init__(app_data, "manure")
                self.type = app_data['type']
                self.year = app_data['year']
                self.day = app_data['day']
                self.mass = app_data['mass']
                self.P_frac = app_data['P_frac']
                self.N_frac = app_data['N_frac']
                self.NH4_frac = app_data['NH4_frac']
                self.WIP_frac = app_data['WIP_frac']
                self.WOP_frac = app_data['WOP_frac']
                self.DM = app_data['DM']
                self.percent_cover = app_data['percent_cover']
                self.depth = app_data['depth']
                self.surface_percent = app_data['surface_percent']

    class Fertilizer(BaseApplicationManagement):

        def __init__(self, fert_data, time):
            """
            Description:
                An instance of this class represents a particular application of fertilizer.
            Args:
                fert_data: a dictionary which holds the rest of the information
                 about this fertilizer
                time: an instance of the Time class specified in classes.py
            """
            super().__init__(fert_data, "fertilizer", time)
            self.applications = {}

            application_no = len(fert_data['year'])
            for application in range(application_no):
                app_data = {}
                for variable_name in fert_data:
                    app_data[variable_name] = fert_data[variable_name].pop()
                self.applications[(app_data['year'], app_data['day'])] = self.Fertilizer(app_data)

            for app_year in self.default_years:
                # TODO: Need default data
                default_data = {
                    'year': app_year,
                    'day': -1,
                    'mass': 100,
                    'depth': 0.0,
                    'surface_percent': 1.0
                }
                self.applications[(default_data['year'], default_data['day'])] = self.Fertilizer(default_data)

        class Fertilizer(BaseApplication):
            def __init__(self, app_data):
                super().__init__(app_data, "fertilizer")
                self.mass = app_data['mass']
                self.depth = app_data['depth']
                self.surface_percent = app_data['surface_percent']

    class TillageManagement(BaseApplicationManagement):

        def __init__(self, tillage_data, time):
            """
            Description:
                An instance of this class represents a particular tillage application
            Args:
                tillage_data: a dictionary which stores the information for this tillage
                time: an instance of the Time class specified in classes.py
            """
            super().__init__(tillage_data, "fertilizer", time)
            self.applications = {}

            application_no = len(tillage_data['year'])
            for application in range(application_no):
                app_data = {}
                for variable_name in tillage_data:
                    app_data[variable_name] = tillage_data[variable_name].pop()
                self.applications[(app_data['year'], app_data['day'])] = self.Tillage(app_data)

            for app_year in self.default_years:
                # TODO: Need default data
                default_data = {
                    'year': app_year,
                    'day': -1,
                    'percent_incorporated': 0.8,
                    'percent_mixed': 0.6,
                    'depth': 25.0
                }
                self.applications[(default_data['year'], default_data['day'])] = self.Tillage(default_data)

        class Tillage(BaseApplication):
            def __init__(self, app_data):
                super().__init__(app_data, "tillage")
                self.percent_incorporated = app_data['percent_incorporated']
                self.percent_mixed = app_data['percent_mixed']
                self.depth = app_data['depth']
