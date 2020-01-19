################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: feed.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com,
           Andy Achenreiner, achenreiner@wisc.edu
"""
################################################################################
from enum import Enum, IntEnum
import sqlite3
from typing import List

from RUFAS import util


class Feeds(IntEnum):
    Corn_grain = 1
    Legume_hay = 2
    Cotton_seed = 3
    Roasted_soybean = 4
    Rye_hay = 5
    Corn_silage = 6
    Barley = 7
    Canola_meal = 8
    Corn_gluten = 9
    Blood_meal = 10
    Fish_meal = 11


class Nutrients(IntEnum):
    DM = 0
    Ash_DM = 1
    CP_DM = 2
    dFA_FA_base = 3
    dRUP_RUP = 4
    dStarch_Starch_base = 5
    FA_DM = 6
    IVNDFD_NDF = 7
    FU = 8
    RU = 9
    NDF_DM = 10
    NDIP_DM = 11
    RUP_CP = 12
    Starch_DM = 13
    sNPNCPE_DM = 14
    ADF_DM = 15
    LIG_DM = 16
    Price = 17
    Limits = 18
    Units = 19


class NutrientValues:
    def __init__(self, database_file, table_name, configured_feeds):
        # TODO error handling
        # TODO filter by list of available feeds
        conn = sqlite3.connect(database_file)
        conn.row_factory = sqlite3.Row

        c = conn.cursor()
        query = "SELECT * FROM " + \
                table_name + \
                " WHERE name IN " + \
                "({})".format(','.join(['?'] * len(configured_feeds)))
        c.execute(query, configured_feeds)

        self.values = []
        row = c.fetchone()
        while row is not None:
            self.values.append(dict(row))
            row = c.fetchone()

        conn.close()

    '''
        self.index = 0

    def get(self, nutrient: Nutrients):
        return self.values[self.index - 1][nutrient.name]

    def next(self) -> bool:
        if self.index < len(self.values):
            self.index += 1
            return True
        return False

    def reset(self):
        self.index = 0
        return self
    '''

# -------------------------------------------------------------------------------
# Class: Feed
# -------------------------------------------------------------------------------
class Feed:
    """
    TODO: Add DocString
    Description: Sorts all feeds by the contraints set in the Linear Program of rations.py

    Args: No arguments
    """

    def __init__(self, data):
        """
        TODO: Add DocString
        Description: This method takes the data specified in the feed Library
        populates the array available_feeds and loops through the keys of the
        array to sort them by the requirements set in the linear program.

        Args: self: references current instance of class Feed and is the first
        argument of every class method.
        """
        # The feed library contains all the types of feed described in the input
        # csv file specified for "feed_library" in the input json file.
        self.__feed_database = data["feed_database"]
        self.__table_name = data["table_name"]
        self.available_feed_names = data["managed_feeds"]
        self.feed_library = util.LibraryDatabase(self.__feed_database,
                                                 self.__table_name)

        # The available_feeds are the collection of feeds that are actually
        # available and should be used in calculations.
        #TODO erase available_feeds
        self.available_feeds = {}
        self.managed_feeds = []

        # Populate available_feeds. The key to retrieve a feed type from
        # available_feeds is the name of the feed as specified in the csv
        # library. The feed_keys are specified in the input json file. They
        # may be the Name or the ID of the feed type in the csv.
        for feed_key in self.available_feed_names:
            self.managed_feeds.append(Feeds[feed_key])


            feed_type = self.feed_library.checkout(feed_key)
            self.available_feeds[feed_type["Name"]] = feed_type

        # Sorted so that they are in a consistent order.
        #self.available_feed_names = sorted(list(self.available_feeds.keys()))
        #self.available_feed_names = self.__available_feed_data

        # Sorted so that is easier to ensure that the requirements calculated
        # in ration.py are zipped with the correct nutrient.
        self.nutrient_rqmts = ['FU', 'RU', 'ME_DM', 'RDP_DM', 'RUP_DM']

        self.__cached_values = NutrientValues(self.__feed_database,
                                              self.__table_name,
                                              self.available_feed_names)

    # doesn't support multithreading
    def initial_values(self) -> NutrientValues:
        return self.__cached_values#.reset()

    def current_values(self) -> NutrientValues:
        return NutrientValues(self.__feed_database,
                              self.__table_name,
                              self.available_feed_names)

    def values(self, feed: Feeds, current: bool):
        feeds = self.current_values() if current else self.initial_values()
        index = self.managed_feeds.index(feed)
        return feeds.values[index]

        # ---------------------------------------------------------------------------
    # Method: annual_reset
    # ---------------------------------------------------------------------------
    def annual_reset(self):
        """
        TODO: Add DocString
        Description: This method resets the data in the available_feeds array
        for another cycle.

        Args: self: references current instance of class Feed and is the first
        argument of every class method.
        """
        pass
