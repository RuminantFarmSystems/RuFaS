"""
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
           Michael Tang, mstang2@wisc.edu
"""

from math import acos, asin, sin, tan, pi
from .crop_types import base_crop, alfalfa, corn, soybean, tall_fescue, spring_barley,\
potato, sugar_beet, spring_wheat,winter_wheat, cereal_rye, triticale, fall_oats
from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, growth_constraints


def daily_crop_routine(soil, crop, field_management, weather, time):
    """
    Description:
        Calls the functions necessary to simulate crop growth.

    Args:
        soil: an instance of the Soil class defined in soil.py
        crop: an instance of the Crop class
        field_management: an instance of the FieldManagement class defined
            in field_management.py
        weather: an instance of the Weather class defined in classes.py
        time: an instance of the Time class defined in classes.py
    """

    # Current crop is set at the beginning of the year in annual_crop_routine
    crop_type = crop.current_crop

    # If there is no crop in rotation, current crop will be named

    daily_reset(crop_type, soil)
    # 'null'. The routine is skipped in this case
    if crop_type.crop_name != 'null':

        crop_was_killed_yesterday = crop_type.killed
        if crop_was_killed_yesterday:
            # set the next crop to grow in a double cropping rotation
            if crop_type.harvest_day > crop_type.planting_day:
                if crop_type.planting_order == '1st':
                    if crop.current_crop_year[0].crop_name != 'null':
                        crop_type.killed = False
                        crop.current_crop = crop.current_crop_year[0]
                        crop.current_crop.kill_year = is_kill_year(crop, time)

            # current crop year will be this years current crop, the current crop will be last years latter crop, 
            # replaced with this years first crop when applicable
            elif crop_type.harvest_day <= crop_type.planting_day:
                if crop.current_crop_year[0].crop_name != 'null':
                    crop_type.killed = False
                    crop.current_crop = crop.current_crop_year[0]
                    crop.current_crop.kill_year = is_kill_year(crop, time)

        # yield is reset to 0 at the beginning of the next day so it can be
        # accessed by the output handler.
        crop_type.yield_actual = 0
        crop_type.yield_N = 0
        crop_type.yield_P = 0

        crop_type.HI_actual = 0
        crop_type.bio_BG = 0
        soil.residue_harvest = 0
        soil.soil_layers[0].fr_tillage = 0

        if not crop_type.planted:
            calculate_start(soil, crop, field_management, weather, time)

        else:

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

                # harvests when the crop has grown more than the required harvest PHU or
                # when it is past the harvest day
                elif crop_type.harvest_type == 'optimal':
                    if crop_type.fr_PHU >= crop_type.fr_PHU_harvest \
                            or time.day == crop_type.harvest_day:
                        yields.update_all(soil, crop_type, field_management, time)

                else:
                    print('"' + crop_type.harvest_type + '"', 'is not a recognized harvest type.'
                                                              ' Harvesting on optimal date.')
                    crop_type.harvest_type = 'optimal'

            # If the crop is perennial, determine whether it is dormant
            if crop_type.crop_type == 'perennial':
                # If it is, run the dormancy routine and set growing to false
                # (This method is only called once on the first day when crop
                # enters dormancy)
                if in_dormancy(crop, time) and crop_type.growing:
                    dormancy_routine(soil, crop_type, field_management, time)
                    crop_type.growing = False
                elif not in_dormancy(crop, time):
                    crop_type.growing = True

        annual_variable_update(crop_type)


def daily_reset(crop_type, soil):
    """
    Description:
        Some variables are reset at the beginning of next day instead of at the
        end of the previous one so that they can be accessed by the output handler.
    Args:
        crop_type: the crop for which attributes are being reset
        soil: an instance of the Soil class defined in soil.py
    """
    crop_type.HI_actual = 0
    crop_type.yield_actual = 0
    crop_type.N_yield = 0
    crop_type.P_yield = 0

    crop_type.HI_actual = 0
    #crop_type.bio_BG = 0
    soil.residue_harvest = 0
    soil.soil_layers[0].fr_tillage = 0


def annual_variable_update(crop_type):
    """
    Description:
        Update variables tracked on an annual scale and reset condition
        variables

    Args:
        crop_type: the crop for which annual variables are being updated
    """

    crop_type.yield_annual += crop_type.yield_actual
    crop_type.N_yield_annual += crop_type.N_yield
    crop_type.P_yield_annual += crop_type.P_yield
    crop_type.NDF_yield_annual += crop_type.NDF_yield


def annual_crop_routine(crop, time):
    """
    Description:
        Determines the current crop and whether it is a kill year for that crop

    Args:
        crop: an instance of the Crop class specified in crop.py on which the
            annual routine is running
        time: an instance of the Time class specified in classes.py
    """

    # current crop year is set to the next year of crops in the regimen
    crop.current_crop_year = crop.grow_regimen[time.year - 1]
    # current crop is the first crop to grow in the selected year
    crop.current_crop = crop.current_crop_year[0]

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

    # the following code checks if the crop is annually grown,
    # if the crop is growing in the last year of the simulation,
    # if the crop is not grown the next year,
    # or if the crop is growing in a double cropping routine
    if crop.current_crop.crop_type == 'annual' or len(crop.grow_regimen) == time.year or \
            crop.current_crop.crop_name != crop.grow_regimen[time.year][0].crop_name or \
            crop.current_crop_year[1].crop_name != 'null':
        crop.current_crop.kill_day = crop.current_crop.harvest_day
        return True
    else:
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

        self.crops_list = []
        self.crops_data = data['crops']
        # TODO: this needs refactoring, perhaps list comprehension - GitHub Issue #180
        #  see supported_species in base_crop.py
        for crop_name, crop_data in self.crops_data.items():
            if crop_name.startswith("alfalfa"):
                crop = alfalfa.Alfalfa(crop_name, crop_data)
            elif crop_name.startswith("corn"):
                crop = corn.Corn(crop_name, crop_data)
            elif crop_name.startswith("soybean"):
                crop = soybean.Soybean(crop_name, crop_data)
            elif crop_name.startswith("tall_fescue"):
                crop = tall_fescue.TallFescue(crop_name, crop_data)
            elif crop_name.startswith("spring_barley"):
                crop = spring_barley.SpringBarley(crop_name, crop_data)
            elif crop_name.startswith("potato"):
                crop = potato.Potato(crop_name, crop_data)
            elif crop_name.startswith("sugar_beet"):
                crop = sugar_beet.SugarBeet(crop_name, crop_data)
            elif crop_name.startswith("spring_wheat"):
                crop = spring_wheat.SpringWheat(crop_name, crop_data)
            elif crop_name.startswith("winter_wheat"):
                crop = winter_wheat.WinterWheat(crop_name, crop_data)
            elif crop_name.startswith("cereal_rye"):
                crop = cereal_rye.CerealRye(crop_name, crop_data)
            elif crop_name.startswith("triticale"):
                crop = triticale.Triticale(crop_name, crop_data)
            elif crop_name.startswith("fall_oats"):
                crop = fall_oats.FallOats(crop_name, crop_data)
            else:
                print(crop_name, "is an invalid crop_type. Please consult the list of crop_types")
                continue

            # list of the crops to run during this simulation, not ordered
            self.crops_list.append(crop)

        # default setting
        self.current_crop = base_crop.BaseCrop()
        self.current_crop_year = []

        # list of the order the crops are growing in, originally set to default
        double_cropping_limit = 2

        self.grow_regimen = \
            [[self.current_crop for _ in range(0, double_cropping_limit)]
             for _ in range(0, len(time.years))]

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

            planting_order = 0
            if crop_type.planting_order == "2nd" or crop_type.harvest_day <= crop_type.planting_day:
                planting_order = 1

            for year in crop_type.plant_years:
                # checks requested grow years against model boundaries
                if year - time.start_year >= len(self.grow_regimen) or year - time.start_year < 0:
                    print('\nCannot grow', crop_type.crop_name, 'in year', year,
                          'because', year, '\nis outside of the scope of the simulation.')
                else:
                    # specified grow years have priority over cycles (specified by repeat)
                    if crop_type.repeat == 0:
                        curr_year = year - time.start_year

                        # if the crop is cold, set it to the latter year slot, if it is warm or
                        # null then it belongs in the initial year slot
                        self.grow_regimen[curr_year][planting_order] = crop_type

                    # populate grow regimen based on repeat if another crop is
                    # not already set for those years
                    elif crop_type.repeat > 0:
                        curr_year = year - time.start_year
                        while curr_year < len(self.grow_regimen):
                            if self.grow_regimen[curr_year][planting_order].crop_name == 'null':
                                self.grow_regimen[curr_year][planting_order] = crop_type

                            # crop slot already full
                            else:
                                print('Cannot grow', crop_type.crop_name, 'in', str(year + curr_year) + ',',
                                      self.grow_regimen[curr_year][planting_order].crop_name,
                                      'is already growing.')
                            curr_year += crop_type.repeat

        # list(filter(lambda crop: crop.crop_name != 'null', self.grow_regimen))

    def annual_reset(self):
        self.current_crop.N_yield_annual = 0.0
        self.current_crop.P_yield_annual = 0.0
        self.current_crop.NDF_yield_annual = 0.0
        self.current_crop.yield_annual = 0.0

    def iterate_planting_day(self, time):
        if time.day >= len(time.years[time.year - 1]):
            pass
        else:
            self.current_crop.planting_day = time.day + 1


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

    fert_management = field_management.managed_applications['fertilizer']
    manure_management = field_management.managed_applications['manure']
    # C.1.B.1/2
    if crop_type.harvest_type == 'scheduled':
        if time.day == crop_type.planting_day:
            if time.calendar_year in manure_management.rotation_years:
                manure_management.schedule_application(time)
            if time.calendar_year in fert_management.rotation_years:
                fert_management.schedule_application(time)
            crop_type.planted = True
            crop_type.growing = True
    else:
        if crop_type.crop_type == 'annual':
            if time.day == crop_type.planting_day and check_conditions_plant(soil, weather, time):
                # C.1.B.1
                if time.calendar_year in manure_management.rotation_years or \
                        time.calendar_year in fert_management.rotation_years:
                    if field_management.check_conditions(soil, weather, time):
                        if time.calendar_year in manure_management.rotation_years:
                            manure_management.schedule_application(time)
                        if time.calendar_year in fert_management.rotation_years:
                            fert_management.schedule_application(time)
                        crop_type.planted = True
                        crop_type.growing = True
                    else:
                        if time.calendar_year in manure_management.rotation_years:
                            manure_management.iterate_application(time)
                        if time.calendar_year in fert_management.rotation_years:
                            fert_management.iterate_application(time)
                        crop.iterate_planting_day(time)
                # C.1.B.2
                else:
                    crop_type.planted = True
                    crop_type.growing = True
            elif time.day == crop_type.planting_day:
                if time.calendar_year in manure_management.rotation_years:
                    manure_management.iterate_application(time)
                if time.calendar_year in fert_management.rotation_years:
                    fert_management.iterate_application(time)
                crop.iterate_planting_day(time)
        # C.1.B.3/4
        else:
            if time.year == 1 and time.day > crop_type.planting_day:
                pass
            # C.1.B.3
            elif not in_dormancy(crop, time) and \
                    yearly_T_avg[time.day - 1] > crop_type.T_base_min and \
                    check_conditions_plant(soil, weather, time):
                if time.calendar_year in manure_management.rotation_years or \
                        time.calendar_year in fert_management.rotation_years:
                    if field_management.check_conditions(soil, weather, time):
                        if time.calendar_year in manure_management.rotation_years:
                            manure_management.schedule_application(time)
                        if time.calendar_year in fert_management.rotation_years:
                            fert_management.schedule_application(time)
                        crop_type.planted = True
                        crop_type.growing = True
                    else:
                        if time.calendar_year in manure_management.rotation_years:
                            manure_management.iterate_application(time)
                        if time.calendar_year in fert_management.rotation_years:
                            fert_management.iterate_application(time)
                # C.1.B.4
                else:
                    crop_type.planted = True
                    crop_type.growing = True
            else:
                if time.calendar_year in manure_management.rotation_years:
                    manure_management.iterate_application(time)

                if time.calendar_year in fert_management.rotation_years:
                    fert_management.iterate_application(time)

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
    else:
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


def check_conditions_plant(soil, weather, time):
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
    if (weather.rainfall[curr_year][curr_day] + weather.irrigation[curr_year][curr_day]) >= 1.0:
        return False

    else:
        return True
