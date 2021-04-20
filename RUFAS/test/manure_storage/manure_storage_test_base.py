"""
RUFAS: Ruminant Farm Systems Model
File name: field_management_test_base.py
Description: establishes the environment in which field management tests run
Author(s): William Donovan, william.m.donovan@gmail.com
"""
from RUFAS.routines.manure_storage.manure_storage import ManureStorage
import unittest


class MSAnimalManagement:

    def __init__(self, pen_data, cow_num, manure):
        """
        Description:
            pared down version of the AnimalManagement class for the purposes
            of testing manure storage. Accepts

        Args:
            pen_data: pared down dictionary describing components of pen
                structure relevant to manure management
            cow_num: number of cows in each pen
                (not currently variable from pen to pen)
            manure: dictionary artificially reproducing daily manure production
                from each pen (not currently variable pen to pen)
        """
        self.all_pens = []
        for pen in pen_data.values():
            self.all_pens.append(self.MSPen(pen, cow_num, manure))

    class MSPen:
        """
        Description:
            pared down version of the Pen class for the purposes of testing
            manure management
        """
        def __init__(self, pen, cow_num, manure):
            self.id = pen['id']
            self.bedding_type = pen['bedding_type']
            self.manure_handling = pen['manure_handling']
            self.manure_separator = pen['manure_separator']
            self.manure_storage = pen['manure_storage']
            self.animals_in_pen = [_ for _ in range(0, cow_num)]
            self.manure = manure


class ManureStorageTest(unittest.TestCase):
    """
    Description:
        parent class for all manure storage tests. Establishes the
        environment in which tests are run and provides a manure storage
        object to test.
    """
    def setUp(self, pen_data=None, cow_num=100, manure=None):
        """
        Description:
            establishes the field management test environment prior to every
            test. Make changes here to alter all test circumstances.
        Args:
            pen_data: dictionary containing pen data relevant to manure management
            cow_num: number of cows in each pen
            manure: dictionary containing artificial manure production for each
                pen
        """
        if pen_data is None:
            pen_data = {'pen0': {'id': 0,
                                 'bedding_type': 'organic',
                                 'manure_handling': 'manual_scraping',
                                 'manure_separator': 'sedimentation',
                                 'manure_storage': 'storage_pit'}
                        }
        if manure is None:
            manure = {'U': 0.34007492378760407,
                      'TAN_s': 0.1400150775776793,
                      'TSd': 8.24163244,
                      'MN': 532.4074003089993,
                      'Mkg': 70.82359257209554,
                      'VSd': 7087.427669573749,
                      'VSnd': 859.3916402321569,
                      'WIP_frac': 1.4119588737072899e-05,
                      'WOP_frac': 1.4119588737072899e-06,
                      'p_excrt_manure': 21.3465366,
                      'p_frac': 0.00031381,
                      'K_manure': 94.56725,
                      'CH4_manure': 529.229415,
                      }
        self.pen_data = pen_data
        self.cow_num = cow_num
        self.manure = manure
        self.animal_management = MSAnimalManagement(self.pen_data, self.cow_num, self.manure)
        self.manure_storage = ManureStorage(self.animal_management)

    def tearDown(self):
        """
        Description:
            called after each test. Resets daily manure separator values
        """
        for separator in self.manure_storage.separators.values():
            separator.reset_daily_variables()
