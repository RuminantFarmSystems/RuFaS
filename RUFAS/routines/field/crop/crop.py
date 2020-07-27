"""
RUFAS: Ruminant Farm Systems Model
File name: crop.py

Description:

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""

from math import acos, asin, sin, tan, pi
from .crop_types import base_crop, alfalfa, corn, soybean
from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, growth_constraints


def daily_crop_routine(soil, crop, field_management, weather, time):
    """
    Description:
        Executes all the daily crop routines.

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop: an instance of the Crop class specified in crop.py containing
            information relevant to simulating crop growth
        field_management: an instance of the FieldManagement class specified
            in field_management.py
        weather: an instance of the Weather class specified in classes.py
            containing environmental information
        time: an instance of the Time class specified in classes.py
    """

    # Current crop is set at the beginning of the year in annual_crop_routine
    crop_type = crop.current_crop

    # If there is no crop in rotation this year, current crop will be named
    # 'null'. The routine is skipped in this case
    if crop_type.crop_name != 'null':

        # yield is reset to 0 at the beginning of the next day so it can be
        # accessed by the output handler.
        crop_type.yield_actual = 0
        crop_type.yield_N = 0
        crop_type.yield_P = 0
        # If the crop is not planted yet, determine whether it is planted today
        if not crop_type.planted:
            calculate_start(soil, crop, field_management, weather, time)

        # Once the crop is planted:
        else:
            # If the crop is growing, run the routines
            if crop_type.growing:
                heat_units.update_all(crop_type, weather, time)

                root_development.update_all(crop_type)

                nitrogen_uptake.update_all(soil, crop_type)

                phosphorus_uptake.update_all(soil, crop_type)

                growth_constraints.update_all(soil, crop_type, weather, time)

                leaf_area_index.update_all(crop_type)

                biomass.update_all(soil, crop_type, weather, time)

                # "pseudocode_crop" C.10.A.1/2
                if crop_type.harvest_type == 'scheduled':
                    if time.day == crop_type.kill_day:
                        yields.update_all(soil, crop_type, field_management, time)

                elif crop_type.harvest_type == 'optimal':
                    if crop_type.fr_PHU >= crop_type.fr_PHU_harvest \
                            or (crop_type.fr_PHU <= crop_type.prev_fr_PHU and time.day > crop_type.harvest_date):
                        yields.update_all(soil, crop_type, field_management, time)
                else:
                    print('"' + crop_type.harvest_type + '"', 'is not a recognized harvest type.'
                                                              ' Harvesting on optimal date.')
                    crop_type.harvest_type = 'optimal'

            # if the crop is perennial, determine whether it is dormant
            if crop_type.crop_type == 'perennial':
                # if it is, run the dormancy routine and set growing to false
                # (This method is only called once on the first day when crop
                # enters dormancy)
                if in_dormancy(crop, time) and crop_type.growing:
                    dormancy_routine(soil, crop_type, field_management, time)
                    crop_type.growing = False
                elif not in_dormancy(crop, time):
                    if crop_type.growing is False and field_management.management_scheme == 'optimal':
                        # schedule a manure and fertilizer application
                        manure_management = field_management.managed_applications['manure']
                        fert_management = field_management.managed_applications['fertilizer']

                        # if manure is being applied to the field this year
                        if (time.start_year + time.year - 1, -1) in manure_management.applications:
                            # schedule the manure application for today
                            manure_management.schedule_application(time)

                        # if fertilizer is being applied to the field this year
                        if (time.start_year + time.year - 1, -1) in fert_management.applications:
                            # schedule the fertilizer application
                            fert_management.schedule_application(time)

                    crop_type.growing = True

        annual_variable_update(crop_type)


def annual_variable_update(crop_type):
    """
    Description:
        Update variables tracked on an annual scale and reset condition
        variables

    Args:
        crop_type: the crop for which annual variables are being updated
    """

    crop_type.yield_annual += crop_type.yield_actual


def annual_crop_routine(crop, time):
    """
    Description:
        Determines the current crop and whether it is a kill year for that crop
    
    Args:
        crop: an instance of the Crop class specified in crop.py on which the
            annual routine is running
        time: an instance of the Time class specified in classes.py
    """

    # current crop is set to the next crop in the regimen
    crop.current_crop = crop.grow_regimen[time.year - 1]
    crop.current_crop.kill_year = is_kill_year(crop, time)


def dormancy_routine(soil, crop_type, field_management, time):
    """
    Description:
        dormancy_routine runs on the first day of dormancy if there is a crop growing.
        LAI is set to minimum LAI, 10% of biomass is added to residue, and the crop
        is signalled to be dormant.
        "pseudocode_crop" C.11.C

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: the crop object which the dormancy routine is operating on
        field_management: an instance of the FieldManagement class
            specified in field_management.py
        time: an instance of the Time class specified in classes.py
    """

    # if crop is perennial and in it's final year, then call yields
    # to kill it
    # C.11.C.1
    if crop_type.kill_year:
        crop_type.kill_day = time.day
        yields.update_all(soil, crop_type, field_management, time)
    else:
        fr_PHU_harvest_min = crop_type.fr_PHU_harvest_min
        # C.11.C.2
        if crop_type.fr_PHU > fr_PHU_harvest_min:
            yields.update_all(soil, crop_type, field_management, time)
        crop_type.LAI_actual = max(0, min(crop_type.LAI_min, crop_type.LAI_actual))

        # C.11.C.3
        soil.residue += crop_type.biomass_actual * 0.1
        crop_type.biomass_actual -= crop_type.biomass_actual * 0.1
        crop_type.bio_N -= crop_type.bio_N * 0.1
        crop_type.bio_P -= crop_type.bio_P * 0.1

        crop_type.fr_LAI_max = 0
        crop_type.accumulated_HU = 0
        crop_type.fr_PHU = 0


def is_kill_year(crop, time):
    """
    Description:
        Determines whether the crop is killed at harvest
    
    Args:
        crop: an instance of the Crop class specified in crop.py containing
            information relevant to simulating crop growth
        time: an instance of the Time class specified in classes.py
    """

    if crop.current_crop.crop_type == 'annual' or len(crop.grow_regimen) == time.year or \
            crop.current_crop.crop_name != crop.grow_regimen[time.year].crop_name:
        crop.current_crop.kill_day = crop.current_crop.harvest_date
        return True
    return False


class Crop:

    def __init__(self, data, time):
        """
        Description:
            An instance of the Crop class represents the crop module and contains
            information relevant to running that module. It does not, itself,
            represent the crop that is actually growing but contains a set of
            available crop types from which current_crop (the object representing
            the growing crop) is selected based on the information specified by
            the user.

        Args:
            data: data object containing information from the input JSON file
                relevant to crop growth
            time: an instance of the Time class specified in classes.py
        """

        self.alfalfa = alfalfa.Alfalfa(data)
        self.corn = corn.Corn(data)
        self.soy = soybean.Soybean(data)

        self.crops_list = [self.alfalfa, self.corn, self.soy]
        self.current_crop = base_crop.BaseCrop()

        self.grow_regimen = [self.current_crop for _ in range(0, len(time.years))]
        self.set_grow_regimen(time)

        # dormancy for perennial crops
        self.latitude = abs(data['latitude'])
        self.T_dl_min = calculate_minimum_day_length(self.latitude)
        self.t_dorm = calculate_t_dorm(self.latitude)
        self.solar_declination = 0.0

    def set_grow_regimen(self, time):
        """
        Description:
            Resolves conflicts in the specified grow_regimen and finalizes
            the years in which each crop is growing in this field
            "pseudocode_crop" C.1.A
        Args:
            time: an instance of the Time class specified in classes.py
        """
        for crop_type in self.crops_list:
            for year in crop_type.grow_years:
                # checks requested grow years against model boundaries
                if year - time.start_year >= len(self.grow_regimen) or year - time.start_year < 0:
                    print('\nCannot grow', crop_type.crop_name, 'in year', year,
                          'because', year, '\nis outside of the scope of the simulation.')
                else:
                    # specified grow years have priority over cycles (specified by repeat)
                    if crop_type.repeat == 0:
                        curr_year = year - time.start_year
                        self.grow_regimen[curr_year] = crop_type
                    # populate grow regimen based on repeat if another crop is
                    # not already set for those years
                    elif crop_type.repeat > 0:
                        curr_year = year - time.start_year
                        while curr_year < len(self.grow_regimen):
                            if self.grow_regimen[curr_year].crop_name == 'null':
                                self.grow_regimen[curr_year] = crop_type
                            else:
                                print('Cannot grow', crop_type.crop_name, 'in', str(year + curr_year) + ',',
                                      self.grow_regimen[curr_year].crop_name, 'is already growing.')
                            curr_year += crop_type.repeat

        list(filter(lambda crop: crop.crop_name != 'null', self.grow_regimen))

    def annual_reset(self):
        """
        Description:
            Resets the annual values for the next year.
        """

        self.current_crop.yield_annual = 0


def calculate_start(soil, crop, field_management, weather, time):
    """
    Description:
        Calculates the start day for the crop
       "pseudocode_crop" section C.1.B

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop: an instance of the Crop class specified in crop.py containing
            information relevant to simulating crop growth
        field_management: an instance of the FieldManagement class
            specified in field_management.py
        weather: an instance of the Weather class specified in classes.py
            containing environmental information
        time: an instance of the Time class specified in classes.py
    """

    crop_type = crop.current_crop
    yearly_T_avg = weather.T_avg[time.year - 1]

    manure_management = field_management.managed_applications['manure']
    fert_management = field_management.managed_applications['fertilizer']

    # if the management scheme is optimal
    if field_management.management_scheme == 'optimal':
        # and the crop is annual
        # C.1.B.1
        if crop_type.crop_type == 'annual':
            # and it is the planting date
            if time.day == crop_type.planting_date:
                # check conditions for applying manure and fertilizer
                if manure_management.check_conditions_plant(soil, weather, time) and \
                        fert_management.check_conditions_plant(soil, weather, time):

                    # if there is an optimal manure application scheduled for this year
                    if (time.start_year + time.year - 1, -1) in manure_management.applications:
                        # schedule manure application for today
                        manure_management.schedule_application(time)

                    # if there is an optimal fertilizer application scheduled for this year
                    if (time.start_year + time.year - 1, -1) in fert_management.applications:
                        # schedule manure application for today
                        fert_management.schedule_application(time)

                    # schedule crop planting
                    crop_type.planted = True
                    crop_type.growing = True

                # conditions were not conducive to fertilizer and manure application
                else:
                    # iterate the planting date to try again tomorrow
                    crop_type.planting_date = time.day + 1
        # the crop is perennial
        # C.1.B.2
        else:
            # edge case for when a planting date that occurs before the
            # simulation begins (usually the result of a rotation)
            if time.year == 1 and time.day > crop_type.planting_date:
                pass
            # check growing conditions for the perennial
            elif not in_dormancy(crop, time) and yearly_T_avg[time.day - 1] > crop_type.T_base_min:
                # check conditions for applying manure and fertilizer
                if manure_management.check_conditions_plant(soil, weather, time) and \
                        fert_management.check_conditions_plant(soil, weather, time):

                    # if there is an optimal manure application scheduled for this year
                    if (time.start_year + time.year - 1, -1) in manure_management.applications:
                        # schedule manure application for today
                        manure_management.schedule_application(time)

                    # if there is an optimal fertilizer application scheduled for this year
                    if (time.start_year + time.year - 1, -1) in fert_management.applications:
                        # schedule manure application for today
                        fert_management.schedule_application(time)

                    # schedule crop planting
                    crop_type.planted = True
                    crop_type.growing = True

                # conditions were not conducive to fertilizer and manure application

                else:
                    # iterate the planting date to try again tomorrow
                    crop_type.planting_date = time.day + 1

    # if application type is scheduled
    elif field_management.management_scheme == 'scheduled':
        # and the crop is annual
        # C.1.B.3
        if crop_type.crop_type == 'annual':
            # and it is the planting date
            if time.day == crop_type.planting_date:
                # plant the crop
                crop_type.planted = True
                crop_type.growing = True
        # the crop is perennial
        # C.1.B.4
        else:
            # edge case for when a planting date that occurs before the
            # simulation begins (usually the result of a rotation)
            if time.year == 1 and time.day > crop_type.planting_date:
                pass
            # check growing conditions for perennial
            elif not in_dormancy(crop, time) and yearly_T_avg[time.day - 1] > crop_type.T_base_min:
                # plant the crop
                crop_type.planted = True
                crop_type.growing = True
    # input management scheme is not currently implemented
    else:
        print('"' + field_management.management_scheme + '"',
              "is not a valid application management scheme, setting type to optimal.")
        field_management.management_scheme = 'optimal'

    # current_crop object is updated
    crop.current_crop = crop_type


def calculate_minimum_day_length(latitude):
    """
    Description:
        Calculates minimum day length for the given watershed based on latitude and
        solar declination during the winter solstice
        "pseudocode_crop" C.11.B.1

    Args:
        latitude: the latitudinal position of the farm

    Returns:
        float: minimum day length
    """

    angular_velocity = 0.2618
    solar_declination = -0.4102
    latitude_radians = latitude * pi / 180

    T_dl_min = 2 * acos(-tan(solar_declination) * tan(latitude_radians)) / angular_velocity

    return T_dl_min


def calculate_t_dorm(latitude):
    """
    Description:
        Calculates the dormancy threshold given the latitude of the given watershed
        "pseudocode_crop" C.11.A.2

    Args:
        latitude: the latitudinal position of the farm

    Returns:
        float: a dormancy threshold
    """

    if latitude > 40:
        return 1.0
    elif 20 <= latitude <= 40:
        return (latitude - 20) / 20
    else:
        return 0.0


def in_dormancy(crop, time):
    """
    Description:
        Returns a boolean indicating whether the given day is within the dormant
        period for the watershed.
        "pseudocode_crop" C.11.A.1/C.11.B.2

    Args:
        crop: an instance of the Crop class specified in crop.py containing
            information relevant to simulating crop growth
        time: an instance of the Time class specified in classes.py

    Returns:
        bool: True if a day is within the crop's dormant period, False otherwise
    """

    year_length = get_year_length(time)

    # C.11.B.2
    solar_declination = asin(0.4 * sin(2 * pi / year_length * (time.day - 82)))

    angular_velocity = 0.2618
    latitude_radians = crop.latitude * pi / 180

    T_dl = 2 * acos(-tan(solar_declination) * tan(latitude_radians)) / angular_velocity

    T_dl_thr = crop.T_dl_min + crop.t_dorm

    # The current day length is less than the day length threshold for dormancy
    if T_dl < T_dl_thr:
        return True

    return False


def get_year_length(time):
    """
    Description:
        Helper method to determine year lengths accounting for leap years

    Args:
        time: an instance of the Time class specified in classes.py

    Returns:
        int: amount of days in the current year
    """

    calendar_year = time.calendar_year

    if calendar_year % 400 == 0:
        return time.leap_year_length
    elif calendar_year % 100 == 0:
        return time.year_length
    elif calendar_year % 4 == 0:
        return time.leap_year_length
    else:
        return time.year_length
