"""
RUFAS: Ruminant Farm Systems Model
File name: field_management.py

Description: This file constructs and maintains the class structure used by the
    field management model. Field management functions are distributed across
    the model.

Author(s): William Donovan, wmdonovan@wisc.edu
            Jacob Johnson, jacob8399@gmail.com
"""


class FieldManagement:

    def __init__(self, app_data, time):
        """
        Description:
            FieldManagement is an organizational object that aggregates the
            management objects for manure, fertilizer, and tillage by field.

        Args:
            app_data: data representing the field_management specified in the JSON file
                for a given field
            time: an instance of the Time class specified in classes.py
        """

        self.application_defaults = {
            "manure": {
                'type': "DAIRY",
                'year': -1,
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
            },
            "fertilizer": {
                'year': -1,
                'day': -1,
                'mass': 100,
                'depth': 0.0,
                'surface_percent': 1.0
            },
            "tillage": {
                'year': -1,
                'day': -1,
                'percent_incorporated': 0.8,
                'percent_mixed': 0.6,
                'depth': 25.0
            }
        }

        self.managed_applications = {}

        for application_name, default_data in self.application_defaults.items():
            self.managed_applications[application_name] = \
                self.BaseApplicationManagement(app_data[application_name], application_name, default_data, time)

        self.management_scheme = str(app_data['management_scheme']).lower()

    class BaseApplicationManagement:
        def __init__(self, management_data, application_type, default_data, time):
            """
            Description:
                BaseApplicationManagement is the super class for all other
                application management objects. The class methods,
                set_default_years, check_conditions, and iterate_application
                allow for dynamic application specification and management
                during the simulation.

            Args:
                management_data: data defining the application manager specified in
                    the input JSON
                application_type: the type of application
                default_data: default settings for an application of this type
                time: an instance of the Time class specified in classes.py
            """
            self.management_data = management_data
            self.years = self.management_data.pop('app_years')
            self.repeat = self.management_data.pop('repeat')

            self.application_type = application_type
            self.applications = {}

            application_no = len(management_data['year'])
            for application in range(application_no):
                app_data = {}
                for variable_name in management_data.keys():
                    app_data[variable_name] = management_data[variable_name][application]
                self.applications[(app_data['year'], app_data['day'])] = \
                    self.BaseApplication(app_data)

            self.default_years = []
            self.set_default_years(time)

            for app_year in self.default_years:
                self.applications[(app_year, -1)] = self.BaseApplication(default_data)

        def set_default_years(self, time):
            """
            Definition:
                Determine years in which each application occurs and construct list
                for module use.

            Args:
                time: an instance of the Time class specified in classes.py
            """

            # if there are years in which this application type occurs
            if len(self.years) != 0:
                for year in self.years:
                    # check specified application years against model boundaries
                    if year - time.start_year >= len(time.years) or year - time.start_year < 0:
                        print('\nCannot apply', self.application_type, 'in year', year,
                              'because', year, '\nis outside of the scope of the simulation.')
                    else:
                        # populate app_years with uniquely specified years
                        if year not in self.default_years:
                            self.default_years.append(year)
                            # populate app_years with repeat cycles
                            if self.repeat != 0:
                                temp_year = year + self.repeat
                                # until repeat hits model boundaries
                                while temp_year - time.start_year < len(time.years):
                                    if temp_year not in self.default_years:
                                        self.default_years.append(temp_year)
                                    temp_year += self.repeat

            self.default_years.sort()

        def schedule_application(self, time):
            """
            Description:
                Helper method for performing common function. Sets the year's
                default application to the current day
            Args:
                time: an instance of the Time class specified in classes.py
            """
            self.applications[(time.start_year + time.year - 1, time.day)] = self.applications.pop((time.start_year + time.year - 1, -1))

        def check_conditions_plant(self, soil, weather, time):
            """
            Description:
                Checks if environmental conditions are conducive to plant.
            Args:
                soil: an instance of the Soil class specified in soil.py
                weather: an instance of the Weather class specified in classes.py
                    contains information about the environment
                time: an instance of the Time class specified in classes.py

            Returns:
                bool: True if conditions are conducive,
                        False (and iterate application) if otherwise
            """
            # the time object begins indexing at 1, but curr is in
            # reference to the weather object which begins indexing at 0
            curr_day = time.day - 1
            curr_year = time.year - 1

            # if soil profile is too saturated for planting
            if soil.soil_layers[0].soil_water > soil.soil_layers[0].fc_water:
                return False

            # if it rains on the current day
            if weather.rainfall[curr_year][curr_day] >= 1.0:
                return False

            return True

        def check_conditions(self, soil, weather, time):
            """
            Description:
                Checks if environmental conditions are conducive to application.
                Iterates field_management scheduled for non-conducive dates
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

            # if soil profile is too saturated for application
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
                Moves field_management to the next day– called from check_conditions.
            Args:
                weather: an instance of the Weather class specified in classes.py
                    contains information about the environment
                time: an instance of the Time class specified in classes.py
            """
            day = time.day
            cal_year = time.start_year + time.year - 1

            # if it is the last day of the current year
            if day == len(weather.rainfall[time.year - 1]):
                if time.year < len(weather.rainfall):
                    self.applications[(cal_year + 1, 0)] = self.applications.pop((cal_year, day))
            else:
                self.applications[(cal_year, day + 1)] = self.applications.pop((cal_year, day))

        class BaseApplication:
            def __init__(self, app_data):
                """
                Description:
                    Superclass representing any application
                Args:
                    app_data: a dictionary containing the parameters of the application
                """

                self.data = {}
                for variable_name, variable_data in app_data.items():
                    self.data[variable_name] = variable_data
