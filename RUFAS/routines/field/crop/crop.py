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
import pandas as pd
from math import acos, asin, sin, tan, pi
from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, growth_constraints
import importlib
from string import digits
import json

def daily_crop_routine(soil, crop, field_management, weather, time, croptime):
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
    try: 
        daily_crops_planted=croptime.crops['crops_planted'][time.index]
        daily_crops_growing=croptime.crops['crops_growing'][time.index]
        daily_crops_killed=croptime.crops['crops_killed'][time.index]
    
    except IndexError as e:
        """
        this exception deals with any index errors that take place. 
        """
        daily_crops_growing=[]    
        daily_crops_killed=[]    
        daily_crops_planted =[]
    
    if not daily_crops_growing:
        for crop_type_name in crop.croplist.keys():
            crop.current_crop[crop_type_name]=crop.setcrop('BaseCrop')
    
    for i in range(len(daily_crops_planted)):
        crop_type_name = daily_crops_planted[i]
        crop.current_crop[crop_type_name]=crop.setcrop(crop_type_name)
        crop_type= crop.current_crop[crop_type_name]
        plant_crops(crop_type,field_management,time,soil,weather,crop)
    
    for k in range(len(daily_crops_growing)):
        crop_type_name = daily_crops_growing[k]
        crop_type= crop.current_crop[crop_type_name]
        
        if not in_dormancy(crop, time):
        
            daily_reset(crop_type, soil)

            heat_units.update_all(crop_type, weather, time)

            root_development.update_all(crop_type)
            
            nitrogen_uptake.reallocate_nitrogen(crop_type,soil)

            phosphorus_uptake.update_all(soil, crop_type)

            growth_constraints.update_growth_factor(soil, crop_type, weather, time)

            leaf_area_index.update_all(crop_type)

            biomass.allocate_biomass(crop_type, soil, weather, time)
            
            kill_non_scheduled_crops(crop_type,soil,croptime,time)
            
            # "pseudocode_crop" C.10.A.1/2
        if crop_type.crop_name in daily_crops_killed:
            yields.update_all(soil, crop_type, field_management, time)
            print('killed it:', crop_type.crop_name, 'with:',crop_type.yield_actual)
            #del crop.current_crop[crop_type_name]
        
        annual_variable_update(crop_type)
        crop.current_crop[crop_type_name] = crop_type
        crop.crop_biomass_totals = crop_type.bio_AG
        crop.crop_yield_totals = crop_type.yield_actual

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
    crop_type.bio_BG = 0
    crop_type.water_act_up=0
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
    #crop.current_crop_year = crop.grow_regimen[time.year - 1]
    # current crop is the first crop to grow in the selected year
    #crop.current_crop = crop.current_crop_year

    #crop.current_crop[i].kill_year = is_kill_year(crop, time)




class Crop(object):
    def __init__(self, data):
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
        # dormancy for perennial crops
        self.latitude = abs(data['latitude'])
        """float: latitude of where the farm is located"""
        self.T_dl_min = calculate_minimum_day_length(self.latitude)
        """float: minimum day length given the latitude"""
        self.t_dorm = calculate_t_dorm(self.latitude)
        """float: the dormancy threshold given the latitude """
        self.solar_declination = 0.0
        """float: angle of the Sun relative to the equator, is a factor for day length"""
        
        spec = importlib.util.spec_from_file_location("crop_classes", "RUFAS/routines/field/crop/crop_types/crop_classes.py")
        self.crop_classes = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.crop_classes)

        self.current_crop = {}
        self.crops_data = data['crops']
        self.croplist = data['crops']
        self.crop_biomass_totals = 0
        self.crop_yield_totals= 0
    def setcrop(self, cropname):
        if (cropname== 'BaseCrop'): 
            return getattr(self.crop_classes, 'BaseCrop')()
        else: 
            remove_digits = str.maketrans('', '', digits)
            return getattr(self.crop_classes, cropname.translate(remove_digits))(cropname, self.crops_data)

    def annual_reset(self):
        for crop_types in self.current_crop.values():
            crop_types.N_yield_annual = 0.0
            crop_types.P_yield_annual = 0.0
            crop_types.NDF_yield_annual = 0.0
            crop_types.yield_annual = 0.0


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

def kill_non_scheduled_crops(crop_type,soil,field_management,time): 
    if crop_type.crop_type == 'perennial':
        fr_PHU_harvest_min = crop_type.fr_PHU_harvest_min
        # C.11.C.2
        
        if crop_type.fr_PHU > fr_PHU_harvest_min:
            yields.update_all(soil, crop_type, field_management, time)
            print('killed it:', crop_type.crop_name, 'with:',crop_type.yield_actual)
            crop_type.LAI_actual = max(0, min(crop_type.LAI_min, crop_type.LAI_actual))

            # C .11.C.3
            soil.residue += crop_type.biomass_actual * 0.1
            crop_type.biomass_actual -= crop_type.biomass_actual * 0.1
            crop_type.bio_N -= crop_type.bio_N * 0.1
            crop_type.bio_P -= crop_type.bio_P * 0.1

            crop_type.fr_LAI_max = 0
            crop_type.accumulated_HU = 0
            crop_type.fr_PHU = 0

def plant_crops(crop_type,field_management,time,soil,weather,crop): 
    yearly_T_avg = weather.T_avg[time.year - 1]
    fert_management = field_management.managed_applications['fertilizer']
    manure_management = field_management.managed_applications['manure']

    if crop_type.crop_type == 'annual':
        if check_conditions_plant(soil, weather, time): 
        
            fert_management = field_management.managed_applications['fertilizer']
            manure_management = field_management.managed_applications['manure']

            if time.calendar_year in manure_management.rotation_years:
                    manure_management.schedule_application(time)
            if time.calendar_year in fert_management.rotation_years:
                    fert_management.schedule_application(time)
        else: 
            if time.calendar_year in manure_management.rotation_years:
                manure_management.iterate_application(time)
            if time.calendar_year in fert_management.rotation_years:
                fert_management.iterate_application(time)
    elif not in_dormancy(crop, time) and yearly_T_avg[time.day - 1] > crop_type.T_base_min and \
    check_conditions_plant(soil, weather, time):
        if field_management.check_conditions(soil, weather, time):
            if time.calendar_year in manure_management.rotation_years:
                manure_management.schedule_application(time)
            if time.calendar_year in fert_management.rotation_years:
                fert_management.schedule_application(time)
        else:
            if time.calendar_year in manure_management.rotation_years:
                manure_management.iterate_application(time)
            if time.calendar_year in fert_management.rotation_years:
                fert_management.iterate_application(time)
    
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


class cropTime:
    
    def __init__(self,time, data,cropclass):
        """
        Description:
            This object is responsible for creating and tracking what crops are being planted, grown, and harvested in the simulation.
        Args:
            config: instance of the Config class containing information necessary
                to initialize time
        """
        # number of years
        
        
        years = time.years
        crop_list= data['crops']
        self.crop_list=crop_list
        start_year= time.start_year
        daily_year=[]
        
        for k in range(start_year,start_year+len(years)):
            x=[k for _ in range(len(years[k-start_year]))]
            daily_year.append(x)        
        
        crop_time={
            "year" : sum(daily_year,[]),
            "day" : sum(years,[])}
        
        crop_time['crops_killed'] = [[] for _ in range(len(crop_time['year']))]
    
        for day in range(len(crop_time['day'])):
            for crop in crop_list.keys():
                crop_class= cropclass.setcrop(crop)
                if (crop_class.crop_type == 'Perennial'): 
                    if crop_time['year'][day] ==  end_year:
                            if crop_time['day'][day] == harvest_day:
                                crop_time['crops_killed'][day].append(crop)
                else: 
                    for year in range(len(crop_list[crop]['plant_years'])):
                        if (crop_list[crop]['plant_years'][year] == crop_time['year'][day] and crop_list[crop]['harvest_day'] == crop_time['day'][day]):
                                crop_time['crops_killed'][day].append(crop)
    
        crop_time['crops_growing'] = [[] for _ in range(len(crop_time['year']))]
        for day in range(len(crop_time['day'])):
            for crop in crop_list.keys():
                crop_class= cropclass.setcrop(crop)
                if (crop_class.crop_type =='perennial'): 
                    grow_years=crop_list[crop]['plant_years']
                    grow_years_length=len(crop_list[crop]['plant_years'])
                    if grow_years_length>1:
                        start_year=grow_years[0]
                        end_year=grow_years[grow_years_length-1]
                        subtract=[start_year,end_year]
                        growing_years=[item for item in grow_years if item not in subtract]
                        planting= crop_list[crop]['planting_day']
                        harvest_day= crop_list[crop]['harvest_day']
                        
                        if crop_time['year'][day] ==  end_year:
                            if crop_time['day'][day] < harvest_day:
                                crop_time['crops_growing'][day].append(crop)
                        
                        if crop_time['year'][day] ==  start_year:
                            if crop_time['day'][day] > planting:
                                crop_time['crops_growing'][day].append(crop)
                        
                        if crop_time['year'][day] in growing_years:
                                crop_time['crops_growing'][day].append(crop)
                else:
                    for year in range(0,len(crop_list[crop]['plant_years'])):
                        if (crop_list[crop]['plant_years'][year] == crop_time['year'][day] and crop_list[crop]['planting_day'] <= crop_time['day'][day] and crop_list[crop]['harvest_day'] >= crop_time['day'][day]):
                            crop_time['crops_growing'][day].append(crop)

        crop_time['crops_planted'] = [[] for _ in range(len(crop_time['year']))]
        
        for day in range(len(crop_time['day'])):
            for crop in crop_list.keys():
                for year in range(len(crop_list[crop]['plant_years'])):
                    if (crop_list[crop]['plant_years'][year] == crop_time['year'][day] and crop_list[crop]['planting_day'] == crop_time['day'][day]):
                        crop_time['crops_planted'][day].append(crop)
                        
        self.crops = crop_time
        with open("sample.json", "w") as outfile:
            json.dump( crop_time, outfile)