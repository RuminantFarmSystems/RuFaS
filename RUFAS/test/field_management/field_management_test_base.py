"""
RUFAS: Ruminant Farm Systems Model
File name: field_management_test_base.py
Description: establishes the environment in which field management tests run
Author(s): William Donovan, william.m.donovan@gmail.com
"""

from RUFAS.routines.field.field_management.field_management import FieldManagement
from RUFAS.classes import Config, Weather, Time
import unittest


class FMSoil:
    """
    Description:
        pared down version of the Soil class for the purposes of FieldManagement
        testing. Defaults to uninitialized, dry soil – modifiable to emulate
        nutrient rich and water saturated soil conditions.
    """
    def __init__(self, soil_water=20, fc_water=30, fert_P_available=0, fert_P_released=0, WIP=0, SIP=0):
        self.soil_layers = [self.FMSoilLayer(soil_water, fc_water)]
        self.area = 1
        self.no_rains = 0
        self.fert_CNT = 0
        self.depth_fact = 0

        self.manure_type = "DAIRY"

        self.WIP_applied = 0
        self.WOP_applied = 0
        self.WIP = WIP
        self.WOP = 0
        self.SOP = 0
        self.SIP = SIP

        self.manure_moisture = 0.5
        self.manure_cov = 0
        self.manure_mass = 0

        self.fert_P_available = fert_P_available
        self.fert_P_released = fert_P_released

    class FMSoilLayer:
        """
        Description:
            pared down version of SoilLayer class used to test field management.
            Subclass of FMSoil. Set up to emulate a single layer profile.
        """
        def __init__(self, soil_water, fc_water):
            self.soil_water = soil_water
            self.fc_water = fc_water
            self.labile_P = 0
            self.bottom_depth_cm = 150
            self.NH4 = 0
            self.K = 0

            self.mass = self.bottom_depth_cm * 10000

            self.active_P = 0

            self.active_N = 0
            self.stable_N = 0


class FMManureStorage:
    """
    Description:
        pared down version of the ManureStorage object used to test field
        management. The only component of manure storage used in field
        management is the list of storage receptacles from which manure is drawn
        for a manure application.
    """
    def __init__(self):
        self.storage = {}

    class FMStorage:
        """
        Description:
            pared down version of manure Storage object used to testmanure
            application. Initialized to be empty.
        """
        def __init__(self):
            self.TS = 0
            self.N = 0
            self.P = 0
            self.TS_liquid = 0
            self.N_liquid = 0
            self.P_liquid = 0

            self.WIP_frac = 0.05
            self.WOP_frac = 0.06


class FieldManagementTest(unittest.TestCase):
    """
    Description:
        parent class for all field management tests. Establishes the
        environment in which tests are run and provides multiple field
        management objects to test
    """
    def setUp(self):
        """
        Description:
            establishes the field management test environment prior to every
            test. Make changes here to alter all test circumstances.
        """
        self.FM_config_data = {
            "start_date": "2010:1",
            "end_date": "2012:365",
            "csv_dir": "output/CSVs/",
            "graphic_dir": "output/graphics/",
            "run_tests": False,
            "set_seed": False,
            "seed": 0
        }
        self.weather_file = "barnyard_weather.csv"
        self.FM_config = Config(self.FM_config_data, self.weather_file)
        self.FM_weather = Weather(self.weather_file, self.FM_config)
        self.FM_time = Time(self.FM_config)

        self.scheduled_fert_base = {
            "mixes": {
                "0_24_24": {
                    "N": 0.00,
                    "P": 0.24,
                    "K": 0.24,
                },
                "24_0_24": {
                    "N": 0.24,
                    "P": 0.0,
                    "K": 0.24
                },
                "24_24_0": {
                    "N": 0.24,
                    "P": 0.24,
                    "K": 0.24
                },
                "5_10_15":{
                    "N": 0.05,
                    "P": 0.1,
                    "K": 0.15
                }
            },
            "rotation_years": [],
            "repeat": 0,
            "mix": ["5_10_15", "0_24_24", "24_0_24", "24_24_0"],
            "year": [2010, 2010, 2011, 2012],
            "day": [10, 90, 90, 90],
            "N_mass": [100, 0, 24, 24],
            "P_mass": [100,24, 0, 24],
            "K_mass": [100, 24, 24, 0],
            "depth": [0.0, 0.0, 0.0, 0.0],
            "surface_percent": [0.95, 1.0, 1.0, 1.0]
        }
        self.scheduled_manure_base = {
            "rotation_years": [],
            "repeat": 0,
            "year": [2010, 2011, 2012],
            "day": [100, 100, 100],
            "N_mass": [200, 200, 200],
            "P_mass": [100, 100, 100],
            "K_mass": [50, 50, 50],
            "cover_percent": [0.95, 0.95, 0.95],
            "depth": [0.0, 0.0, 0.0],
            "surface_percent": [1.0, 1.0, 1.0]
        }
        self.scheduled_till_base = {
            "rotation_years": [],
            "repeat": 0,
            "year": [2010, 2011, 2012],
            "day": [300, 300, 300],
            "percent_incorporated": [0.3, 0.3, 0.3],
            "percent_mixed": [0.6, 0.6, 0.6],
            "depth": [150, 150, 150]
        }
        self.scheduled_management_data = {'fertilizer': self.scheduled_fert_base, 'manure': self.scheduled_manure_base,
                                          'tillage': self.scheduled_till_base}
        self.scheduled_management_obj = FieldManagement(self.scheduled_management_data, self.FM_time)

        self.repeat_fert_base = {
            "mixes": {
                "0_24_24": {
                    "N": 0.00,
                    "P": 0.24,
                    "K": 0.24,
                },
                "24_0_24": {
                    "N": 0.24,
                    "P": 0.0,
                    "K": 0.24
                },
                "24_24_0": {
                    "N": 0.24,
                    "P": 0.24,
                    "K": 0.24
                }
            },
            "rotation_years": [2010],
            "repeat": 1,
            "mix": [],
            "year": [],
            "day": [],
            "N_mass": [],
            "P_mass": [],
            "K_mass": [],
            "depth": [],
            "surface_percent": []
        }
        self.repeat_manure_base = {
            "rotation_years": [2010],
            "repeat": 1,
            "year": [],
            "day": [],
            "N_mass": [],
            "P_mass": [],
            "K_mass": [],
            "cover_percent": [],
            "depth": [],
            "surface_percent": []
        }
        self.repeat_till_base = {
            "rotation_years": [2010],
            "repeat": 1,
            "year": [],
            "day": [],
            "percent_incorporated": [],
            "percent_mixed": [],
            "depth": []
        }
        self.repeat_management_data = {'fertilizer': self.repeat_fert_base, 'manure': self.repeat_manure_base,
                                       'tillage': self.repeat_till_base}
        self.repeat_management_obj = FieldManagement(self.repeat_management_data, self.FM_time)

        self.mixed_fert_base = {
            "mixes": {
                "0_24_24": {
                    "N": 0.00,
                    "P": 0.24,
                    "K": 0.24,
                },
                "24_0_24": {
                    "N": 0.24,
                    "P": 0.0,
                    "K": 0.24
                },
                "24_24_0": {
                    "N": 0.24,
                    "P": 0.24,
                    "K": 0.24
                }
            },
            "rotation_years": [2010],
            "repeat": 2,
            "mix": ["24_0_24"],
            "year": [2011],
            "day": [90],
            "N_mass": [24],
            "P_mass": [24],
            "K_mass": [24],
            "depth": [0.0],
            "surface_percent": [1.0]
        }
        self.mixed_manure_base = {
            "manure": {
                "rotation_years": [2010],
                "repeat": 2,
                "year": [2011],
                "day": [100],
                "N_mass": [200],
                "P_mass": [100],
                "K_mass": [50],
                "cover_percent": [0.95],
                "depth": [0.0],
                "surface_percent": [1.0]
            }
        }['manure']
        self.mixed_till_base = {
            "tillage": {
                "rotation_years": [2010],
                "repeat": 2,
                "year": [2011],
                "day": [300],
                "percent_incorporated": [0.3],
                "percent_mixed": [0.6],
                "depth": [150]
            }
        }['tillage']
        self.mixed_management_data = {'fertilizer': self.mixed_fert_base, 'manure': self.mixed_manure_base,
                                      'tillage': self.mixed_till_base}
        self.mixed_management_obj = FieldManagement(self.mixed_management_data, self.FM_time)

        self.FM_soil = FMSoil()
        self.FM_manure_storage = FMManureStorage()
