"""
RUFAS: Ruminant Farm Systems Model
File name: field_management.py

Description: This file constructs and maintains the class structure used by the
    field management model. Field management functions are distributed across
    the model.

Author(s): William Donovan, wmdonovan@wisc.edu
            Jacob Johnson, jacob8399@gmail.com
"""

from . import fertilizer_application, manure_application, tillage_application


def daily_field_management_routine(soil, manure_storage, field_management, weather, time):
    """
    Description:
        Manages the function calls for simulating field management

    Args:
        soil: an instance of the Soil class defined in soil.py representing
            the soil profile of the field being managed
        manure_storage: an instance of the ManureStorage class defined in
            manure_storage.py representing available manure
        field_management: an instance of the FieldManagement class defined in
            field_management.py
        weather: an instance of the Weather class defined in classes.py
        time: an instance of the Time class defined in classes.py
    """

    daily_field_management_reset(field_management)

    fert_management = field_management.managed_applications['fertilizer']
    if (time.calendar_year, time.day) in fert_management.applications:
        fertilizer_application.update_all(soil, field_management,
                                          fert_management.applications[(time.calendar_year, time.day)].data)

    manure_management = field_management.managed_applications['manure']
    if (time.calendar_year, time.day) in manure_management.applications:
        manure_application.update_all(soil, field_management, manure_storage,
                                      manure_management.applications[(time.calendar_year, time.day)].data)

    till_management = field_management.managed_applications['tillage']
    if (time.calendar_year, time.day) in till_management.applications:
        tillage_application.update_all(soil, till_management.applications[(time.calendar_year, time.day)].data)

    field_management.update_annual_variables(manure_storage)


def daily_field_management_reset(field_management):
    field_management.fert_applied = 0.0
    field_management.fert_N_applied = 0.0
    field_management.fert_P_applied = 0.0
    field_management.fert_K_applied = 0.0

    field_management.manure_applied = 0.0
    field_management.manure_N_applied = 0.0
    field_management.manure_P_applied = 0.0


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
                'year': -1,
                'day': -1,
                'N_mass': 520,
                'P_mass': 300,
                'cover_percent': 0.95,
                'depth': 0.0,
                'surface_fraction': 1.0
            },
            "fertilizer": {
                'composition': {
                    'N': 0.13,
                    'P': 0.13,
                    'K': 0.13
                },
                'mix': "default",
                'year': -1,
                'day': -1,
                'N_mass': 100,
                'P_mass': 100,
                'K_mass': 100,
                'depth': 0.0,
                'surface_fraction': 1.0
            },
            "tillage": {
                'year': -1,
                'day': -1,
                'percent_nutrient_incorporated': 0.8, 
                'percent_nutrient_mixed': 0.6, 
                'depth': 25.0
            }
        }

        self.managed_applications = {}

        for application_name, default_data in self.application_defaults.items():
            if application_name.startswith('fert'):
                self.managed_applications[application_name] = \
                    self.FertApplicationManagement(app_data[application_name], application_name, default_data, time)
            else:
                self.managed_applications[application_name] = \
                    self.BaseApplicationManagement(app_data[application_name], application_name, default_data, time)

        self.manure_applied = 0.0
        self.manure_N_applied = 0.0
        self.manure_P_applied = 0.0

        self.manure_applied_annual = 0.0
        self.manure_N_applied_annual = 0.0
        self.manure_P_applied_annual = 0.0

        self.fert_applied = 0.0
        self.fert_N_applied = 0.0
        self.fert_P_applied = 0.0
        self.fert_K_applied = 0.0

        self.fert_applied_annual = 0.0
        self.fert_N_applied_annual = 0.0
        self.fert_P_applied_annual = 0.0
        self.fert_K_applied_annual = 0.0

    @staticmethod
    def check_conditions(soil, weather, time):
        """
        Description:
            Checks if environmental conditions are conducive to application.
            Iterates field_management scheduled for non-conducive dates
            "pseudocode_field_management" FM.2.3

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
        next_year = curr_year + 1

        second_day = next_day + 1

        # if soil profile is too saturated for application
        if soil.soil_layers[0].soil_water > soil.soil_layers[0].fc_water:
            return False

        # if it rains on the current day
        if (weather.rainfall[curr_year][curr_day] + weather.irrigation[curr_year][curr_day]) >= 1.0:
            return False

        # boundary check the next day against length of the current year
        if next_day >= len(time.years[curr_year]):
            # boundary check the next year against length of simulation
            if next_year < len(time.years):
                # update year and day to the start of the next year
                curr_year += 1
                curr_day = 0

                next_day = curr_day + 1
            # the next day and current year are outside of the scope of the simulation
            else:
                return False

        # if it rains on the following day
        if (weather.rainfall[curr_year][next_day] + weather.irrigation[curr_year][next_day]) >= 1.0:
            return False

        # boundary check the second day against length of the current year
        if second_day >= len(time.years[curr_year]):
            # boundary check the next year against length of simulation
            if next_year < len(time.years):
                # update current year and day to the start of the next year
                curr_year += 1
                curr_day = 0

                second_day = curr_day + 2
            # the second day and current year are outside of the scope of the simulation
            else:
                return False

        # if it rains on the second day
        if (weather.rainfall[curr_year][second_day] + weather.irrigation[curr_year][second_day]) >= 1.0:
            return False

        return True

    def update_annual_variables(self, manure_storage):
        self.manure_applied_annual += self.manure_applied
        self.manure_N_applied_annual += self.manure_N_applied
        self.manure_P_applied_annual += self.manure_P_applied

        self.fert_applied_annual += self.fert_applied
        self.fert_N_applied_annual += self.fert_N_applied
        self.fert_P_applied_annual += self.fert_P_applied
        self.fert_K_applied_annual += self.fert_K_applied

    def annual_reset(self):
        self.fert_applied_annual = 0.0
        self.fert_N_applied_annual = 0.0
        self.fert_P_applied_annual = 0.0
        self.fert_K_applied_annual = 0.0

        self.manure_applied_annual = 0.0
        self.manure_N_applied_annual = 0.0
        self.manure_P_applied_annual = 0.0

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
            self.default_data = default_data
            self.management_data = management_data

            self.rotation_years = self.management_data.pop('rotation_years')
            self.repeat = self.management_data.pop('repeat')

            self.application_type = application_type
            self.applications = {}

            self.populate_scheduled_applications()
            self.populate_rotations(time)

        def populate_scheduled_applications(self):
            application_no = len(self.management_data['year'])
            for application in range(application_no):
                app_data = {}
                for variable_name in self.management_data.keys():
                    app_data[variable_name] = self.management_data[variable_name][application]

                self.applications[(app_data['year'], app_data['day'])] = \
                    self.BaseApplication(app_data)

        def populate_rotations(self, time):
            # if there are years in which this application type occurs
            if len(self.rotation_years) != 0:
                for year in self.rotation_years:
                    self.applications[(year, -1)] = self.BaseApplication(self.default_data)
                    # populate rotation_years with repeat cycles
                    if self.repeat != 0:
                        temp_year = year + self.repeat
                        # until repeat hits model boundaries
                        while temp_year - time.start_year < len(time.years):
                            if temp_year not in self.rotation_years:
                                self.rotation_years.append(temp_year)
                                self.applications[(temp_year, -1)] = self.BaseApplication(self.default_data)
                            temp_year += self.repeat

        def schedule_application(self, time):
            """
            Description:
                Helper method for performing common function. Sets the year's
                default application to the current day
            Args:
                time: an instance of the Time class specified in classes.py
            """
            if time.day >= len(time.years[time.year - 1]):
                pass
            else:
                if (time.calendar_year, -1) in self.applications:
                    new_date = (time.calendar_year, -1)
                elif (time.calendar_year, time.day) in self.applications:
                    new_date = (time.calendar_year, time.day)
                else:
                    # installed to handle double cropping + default applications
                    new_date = None

                if new_date is not None:
                    self.applications[(time.calendar_year, time.day + 1)] = \
                        self.applications.pop(new_date)

        def iterate_application(self, time):
            """
            Description:
                Moves field_management to the next day– called from check_conditions.
            Args:
                time: an instance of the Time class specified in classes.py
            """
            # if it is the last day of the current year
            if time.day == len(time.years[time.year - 1]):
                if time.year < len(time.years):

                    if (time.calendar_year, -1) in self.applications:
                        new_date = (time.calendar_year, -1)
                    elif (time.calendar_year, time.day) in self.applications:
                        new_date = (time.calendar_year, time.day)
                    else:
                        # installed to handle double cropping + default applications
                        new_date = None

                    if new_date is not None:
                        self.applications[(time.calendar_year + 1, 1)] = \
                            self.applications.pop(new_date)
            else:
                if (time.calendar_year, -1) in self.applications:
                    new_date = (time.calendar_year, -1)
                elif (time.calendar_year, time.day) in self.applications:
                    new_date = (time.calendar_year, time.day)
                else:
                    # installed to handle double cropping + default applications
                    new_date = None

                if new_date is not None:
                    self.applications[(time.calendar_year, time.day + 1)] = \
                        self.applications.pop(new_date)

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

    class FertApplicationManagement(BaseApplicationManagement):
        def __init__(self, management_data, application_type, default_data, time):
            self.mixes = management_data.pop('mixes')
            super().__init__(management_data, application_type, default_data, time)

            for application in self.applications.values():
                if application.data['mix'] != 'default':
                    application.data['composition'] = self.mixes[application.data['mix']]
