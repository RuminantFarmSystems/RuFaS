################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: feed.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com,
           Andy Achenreiner, achenreiner@wisc.edu
           Militsa Sotirova, militsasotirova@gmail.com
           William Donovan, william.m.donovan@gmail.com
           Jacob Johnson, jacob8339@gmail.com
"""
################################################################################

from enum import IntEnum
from RUFAS.util import DatabaseReader

from . import nitrogen_loss, carbon_loss, protein_degradation


# runs the feed routine. Daily is a misnomer here– this is called once per harvest.
def daily_feed_routine(feed, crop):
    if feed.storage:
        feed.dry_matter += crop.current_crop.yield_actual

        if crop.current_crop.yield_actual != 0:
            feed.nitrogen += crop.current_crop.yield_N
            feed.phosphorus += crop.current_crop.yield_P
            # TODO: no Carbon Cycle currently implemented
            feed.carbon += crop.current_crop.yield_actual * feed.carbon_percent

            carbon_loss.update_all(feed)

            nitrogen_loss.update_all(feed)

            protein_degradation.update_all(feed)

        if feed.dry_matter != 0:
            feed.crude_protein += 6.25 * feed.nitrogen / feed.dry_matter


# Determine the current crop
def annual_feed_routine(feed, crop):
    feed.prev_crop_name = feed.crop_name
    feed.crop_name = crop.current_crop.crop_name

    if feed.crop_name != 'null':
        calibrate_feed(feed)


# Parameterize the optimal empirical model based on crop and storage types generated in input
def calibrate_feed(feed):
    if feed.crop_name == 'corn':
        feed.storage = True
        feed.carbon_percent = 0.58
        if feed.moisture == 'direct_cut':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0.02
            feed.NPN_min_percent = 0.50
            feed.C_harvest_gas_percent = 0.01
            feed.C_harvest_particle_percent = 0.005
            feed.C_storage_gas_percent = 0.08
            feed.C_storage_leachate_percent = 0.02
            feed.C_feedout_gas_percent = 0.02
            feed.C_feedout_particle_percent = 0
        elif feed.moisture == 'wilted':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0
            feed.NPN_min_percent = 0.45
            feed.C_harvest_gas_percent = 0.015
            feed.C_harvest_particle_percent = 0.005
            feed.C_storage_gas_percent = 0.07
            feed.C_storage_leachate_percent = 0
            feed.C_feedout_gas_percent = 0.02
            feed.C_feedout_particle_percent = 0
        elif feed.moisture == 'baleage':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0
            feed.NPN_min_percent = 0.40
            feed.C_harvest_gas_percent = 0.015
            feed.C_harvest_particle_percent = 0.005
            feed.C_storage_gas_percent = 0.12
            feed.C_storage_leachate_percent = 0
            feed.C_feedout_gas_percent = 0.02
            feed.C_feedout_particle_percent = 0
        else:
            if feed.prev_crop_name != feed.crop_name:
                print('"' + feed.moisture + '"', 'is not a recognized moisture category for', feed.crop_name)
    elif feed.crop_name == 'alfalfa':
        feed.storage = True
        feed.carbon_percent = 0.58
        if feed.moisture == 'direct_cut':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0.025
            feed.NPN_min_percent = 0.40
            feed.C_harvest_gas_percent = 0.03
            feed.C_harvest_particle_percent = 0
            feed.C_storage_gas_percent = 0.095
            feed.C_storage_leachate_percent = 0.025
            feed.C_feedout_gas_percent = 0.02
            feed.C_feedout_particle_percent = 0
        elif feed.moisture == 'wilted':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0
            feed.NPN_min_percent = 0.40
            feed.C_harvest_gas_percent = 0.035
            feed.C_harvest_particle_percent = 0.015
            feed.C_storage_gas_percent = 0.09
            feed.C_storage_leachate_percent = 0
            feed.C_feedout_gas_percent = 0.02
            feed.C_feedout_particle_percent = 0
        elif feed.moisture == 'haylage':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0
            feed.NPN_min_percent = 0.35
            feed.C_harvest_gas_percent = 0.045
            feed.C_harvest_particle_percent = 0.025
            feed.C_storage_gas_percent = 0.07
            feed.C_storage_leachate_percent = 0
            feed.C_feedout_gas_percent = 0.02
            feed.C_feedout_particle_percent = 0
        elif feed.moisture == 'moist_hay':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0
            feed.NPN_min_percent = 0.30
            feed.C_harvest_gas_percent = 0.07
            feed.C_harvest_particle_percent = 0.10
            feed.C_storage_gas_percent = 0.03
            feed.C_storage_leachate_percent = 0
            feed.C_feedout_gas_percent = 0
            feed.C_feedout_particle_percent = 0.01
        elif feed.moisture == 'dry_hay':
            feed.CP_gas_percent = 0
            feed.CP_leachate_percent = 0
            feed.NPN_min_percent = 0.20
            feed.C_harvest_gas_percent = 0.07
            feed.C_harvest_particle_percent = 0.16
            feed.C_storage_gas_percent = 0.02
            feed.C_storage_leachate_percent = 0
            feed.C_feedout_gas_percent = 0
            feed.C_feedout_particle_percent = 0.01
        else:
            if feed.prev_crop_name != feed.crop_name:
                print('"' + feed.moisture + '"', 'is not a recognized moisture category for', feed.crop_name)
    else:
        if feed.prev_crop_name != feed.crop_name:
            print('"' + feed.crop_name + '"', 'storage is not currently implemented')
            feed.storage = False


class FeedNames(IntEnum):
    """
    Each enum member is the name of a feed in the feed information database. The
    values correspond to the ID column in the database table.

    Note: if a feed is added to the database source of feed information, the
    name of the feed along with its ID must be added here.
    """
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
    """
    Each enum member is the name of either a nutrient or characteristic of a
    feed in the database source of feed information.

    Note: if a nutrient or characteristic column is added to the database
    source of feed information, the nutrient or characteristic must be added
    here.
    """
    # TODO change names in the enum
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
    """
    Description: Stores the information from the database source of feed
    information for the feeds listed as managed in the input JSON file.
    """
    def __init__(self, database_file: str, table_name, configured_feeds):
        """
        Connects to the @database_file and queries from the @table_name for the
        nutrient and characteristic information of the list of
        @configured_feeds. If an exception is raised, the method prints a
        message and the program exits.

        Args:
            database_file: the name of the database file
            table_name: the name of the table in the database which is queried
            configured_feeds: a list of the feeds provided by the input JSON
                file as feeds managed by the farm, and therefore the feeds
                for which information will be stored
        """
        # To obtain data from a database table, we form and execute a query
        # through the DatabaseReader class.
        # The table we are querying from with the following code looks like:
        # ID    Name    Nutrient1   Nutrient2   ...
        # 0     Feed1   value       value       ...
        # 1     Feed2   value       value       ...
        # ...
        #
        # The query will be in the following format:
        # SELECT * FROM table_name WHERE name IN [list_of_feed_names]
        #
        # SELECT * FROM table_name:
        #       The * indicates that information from all of the columns in
        #       "table_name" are desired (otherwise, the names of specific
        #       columns would be provided).
        #
        # WHERE name IN [list_of_feed_names]:
        #       If we do not specify which rows we want information from, we
        #       will get information from every row. We specify which feeds
        #       (rows) we want information from by filtering. We specify
        #       that we want each in the result to have a "name" that is in
        #       list_of_feed_names. (Note that the column in the table is
        #       "Name" - this is case insensitive.)
        #
        # Thus, the query selects all of the columns from the database with
        # the additional specification that we only obtain information from
        # the rows that correspond to the feeds listed in the input JSON
        # file as managed by the farm (specified by the argument
        # configured_feeds).
        reader = DatabaseReader(database_file, table_name, identifier="name",
                                desired_rows=configured_feeds)
        self.values = reader.values


class Feed:
    """
    Description: Stores the information for the feeds managed by the farm.
    """

    def __init__(self, data):
        self.storage_type = data['storage_type']
        self.moisture = data['moisture']
        self.additive = data['additive']
        self.packing_density = data['packing_density']

        self.inoculation = data['inoculation']
        self.bunk_type = data['bunk_type']
        self.ventilation = data['ventilation']
        self.removal_rate = data['removal_rate']

        self.crop_name = 'null'
        self.prev_crop_name = 'null'

        self.storage = True

        self.dry_matter = data['initial_dry_matter']

        self.carbon_percent = 0.0

        self.carbon = 0.0
        self.nitrogen = 0.0
        self.phosphorus = 0.0

        self.C_harvest_gas = 0.0
        self.C_harvest_particle = 0.0

        self.C_storage_gas = 0.0
        self.C_storage_leachate = 0.0

        self.C_feedout_gas = 0.0
        self.C_feedout_particle = 0.0

        self.crude_protein = 0.0

        self.CP_gas = 0.0
        self.CP_leachate = 0.0
        self.NPN = 0.0

        self.C_harvest_gas_percent = 0.0
        self.C_harvest_particle_percent = 0.0

        self.C_storage_gas_percent = 0.0
        self.C_storage_leachate_percent = 0.0

        self.C_feedout_gas_percent = 0.0
        self.C_feedout_particle_percent = 0.0

        self.CP_gas_percent = 0.0
        self.CP_leachate_percent = 0.0
        self.NPN_min_percent = 0.0
        """
        Sets up the data for the feeds managed by the farm.

        Args:
            data: the feed information from the input JSON file
        """
        self.__feed_database = data["feed_database"]
        self.__table_name = data["table_name"]
        self.managed_feed_names = data["managed_feeds"]

        # The managed_feeds are the collection of feeds should be used
        # in calculations.
        self.managed_feeds = []

        # Populate managed_feeds. The key to retrieve a feed type from
        # available_feeds is the name of the feed as specified in the database
        # table. The feed_keys are specified in the input json file.
        for feed_key in self.managed_feed_names:
            self.managed_feeds.append(FeedNames[feed_key])

        # The nutrient requirements used in the ration calculations.
        self.nutrient_rqmts = ['FU', 'RU', 'ME_DM', 'RDP_DM', 'RUP_DM']

        # The values in the database at the time of this object's
        # initialization.
        self.__cached_values = NutrientValues(self.__feed_database,
                                              self.__table_name,
                                              self.managed_feed_names)

    def initial_values(self) -> NutrientValues:
        """
        Returns: a NutrientValues object which holds the values in the database
        table at the time of program initialization.
        """
        return self.__cached_values

    def current_values(self) -> NutrientValues:
        """
        Returns: a new NutrientValues object which holds the values in the
        database table at the time of the method call.
        """
        return NutrientValues(self.__feed_database,
                              self.__table_name,
                              self.managed_feed_names)

    def values(self, desired_feed: FeedNames, current: bool = False):
        """
        Args:
            desired_feed: a member of the FeedNames enum
            current: if the values should be taken from the database at the time
                of the method call, this value is true. The default value is
                False, which means the cached values will be returned (stored at
                the time of program initialization)
                
        Returns: the dictionary which represents the characteristics and
        nutrients of the @desired_feed
        """
        feeds = self.current_values() if current else self.initial_values()
        index = self.managed_feeds.index(desired_feed)
        return feeds.values[index]

    def annual_reset(self):
        """
        This method resets the data in the available_feeds array
        for another cycle.
        """
        pass
