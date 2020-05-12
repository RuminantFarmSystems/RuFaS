"""
RUFAS: Ruminant Farm Systems Model
File name: feed.py


Description: Main driver for the feed storage module. Calibrates storage and models
                protein degradation as well as reductions in Carbon, Nitrogen, and
                Phosphorus content during harvest, storage, and feed out.

Author(s): Kass Chupongstimun, kass_c@hotmail.com,
           Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
           Militsa Sotirova, militsasotirova@gmail.com

"""

from enum import IntEnum
from RUFAS.util import DatabaseReader

from . import nitrogen_loss, carbon_loss, protein_degradation


# runs the feed routine. Daily is a misnomer here– this is called once per harvest.
def daily_feed_routine(feed, fields):

    for field in fields:
        crop = field.crop.current_crop
        if crop.yield_actual != 0:
            crop_name = crop.crop_name
            crop_quality = crop.harvest_quality

            stored = False

            for storage in feed.available_storage.values():
                if storage.crop_name == crop_name and storage.quality == crop_quality:
                    storage.store_crop(crop)

                    stored = True

            if not stored:
                for storage in feed.available_storage.values():
                    if storage.DM == 0:
                        storage.calibrate_storage(crop)
                        storage.store_crop(crop)

                        stored = True

            if not stored:
                print("Insufficient specified storage for yield. Simulating standard storage.")
                standard_data = {
                                    "storage_type": "bag",
                                    "moisture": "direct_cut",
                                    "additive": "preservative",
                                    "packing_density": 14,
                                    "inoculation": "heterofermentative",
                                    "bunk_type": "open_floor",
                                    "ventilation": True,
                                    "removal_rate": 6,
                                    "initial_dry_matter": 0
                }

                standard_storage = feed.Storage(standard_data)
                standard_storage_name = str('standard_storage_' + str(feed.standard_storage_count))

                feed.storage_options[standard_storage_name] = standard_storage
                feed.available_storage[standard_storage_name] = standard_storage

                feed.standard_storage_count += 1

                feed.available_storage[standard_storage_name].store_crop(crop)

        for storage_name, storage in feed.storage_options.items():
            if storage_name in feed.available_storage and storage.DM != 0:
                storage.calculate_losses()
                feed.available_storage.pop(storage_name)

    feed.summarize_feed_storage()


def annual_feed_routine():
    pass


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
        self.storage_options = {}
        self.standard_storage_count = 0

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

        self.storage_options = {}
        for storage_name, storage_data in data['storage_options'].items():
            self.storage_options[storage_name] = self.Storage(storage_data)

        self.available_storage = dict(self.storage_options)

        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.CP = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

        self.NPN = 0.0

    def summarize_feed_storage(self):
        for storage in self.storage_options.values():
            self.C += storage.C
            self.N += storage.C
            self.P += storage.C
            self.DM += storage.C
            self.CP += storage.C

            self.C_loss += storage.C_loss
            self.CP_loss += storage.CP_loss

            self.NPN += storage.NPN

    class Storage:
        def __init__(self, data):

            self.storage_type = data['storage_type']
            self.moisture = data['moisture']
            self.additive = data['additive']
            self.packing_density = data['packing_density']

            self.inoculation = data['inoculation']
            self.bunk_type = data['bunk_type']
            self.ventilation = data['ventilation']
            self.removal_rate = data['removal_rate']

            self.DM = data['initial_dry_matter']

            self.crop_name = 'null'
            self.storage_quality = 'null'

            self.storage = True

            self.CP_percent = 0.0
            self.C_percent = 0

            self.C = 0.0
            self.N = 0.0
            self.P = 0.0

            self.C_harvest_gas = 0.0
            self.C_harvest_particle = 0.0

            self.C_storage_gas = 0.0
            self.C_storage_leachate = 0.0

            self.C_feed_out_gas = 0.0
            self.C_feed_out_particle = 0.0

            self.C_loss = 0.0

            self.CP = 0.0

            self.CP_gas = 0.0
            self.CP_leachate = 0.0
            self.CP_loss = 0.0

            self.NPN = 0.0

            self.C_harvest_gas_percent = 0.0
            self.C_harvest_particle_percent = 0.0

            self.C_storage_gas_percent = 0.0
            self.C_storage_leachate_percent = 0.0

            self.C_feed_out_gas_percent = 0.0
            self.C_feed_out_particle_percent = 0.0

            self.CP_gas_percent = 0.0
            self.CP_leachate_percent = 0.0
            self.NPN_min_percent = 0.0

            self.error_flag_0 = True
            self.error_flag_1 = True
            self.error_flag_2 = True

        # Helper method for "storing" the specified crop
        def store_crop(self, crop):
            if self.storage:
                self.DM += crop.yield_actual
                self.CP += crop.yield_actual * self.CP_percent

                self.N += crop.yield_N
                self.P += crop.yield_P

                # TODO: C_percent is a temp work around. Update to yield_C when carbon model is implemented.
                self.C += crop.yield_actual * self.C_percent

                crop.harvest_quality = ''

        def calculate_losses(self):
            carbon_loss.update_all(self)
            nitrogen_loss.update_all(self)

            # TODO: no protein degradation is currently being simulated
            protein_degradation.update_all()

        # Parameterize the optimal empirical model based on crop and storage type
        def calibrate_storage(self, crop):
            """
            Description:
                calibrate_feed is the implementation of KPB's feed reduction table.
                Based on the feed and storage types, reduction percentages are set for
                use in the rest of the module. If the specified feed or storage type
                are not currently implemented, an error message is printed.
            """

            self.crop_name = crop.crop_name
            self.storage_quality = crop.harvest_quality

            if self.crop_name == 'corn':
                self.storage = True
                self.CP_percent = 0.08
                self.C_percent = 0.58
                if self.moisture == 'direct_cut':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0.02
                    self.NPN_min_percent = 0.50
                    self.C_harvest_gas_percent = 0.01
                    self.C_harvest_particle_percent = 0.005
                    self.C_storage_gas_percent = 0.08
                    self.C_storage_leachate_percent = 0.02
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == 'wilted':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.45
                    self.C_harvest_gas_percent = 0.015
                    self.C_harvest_particle_percent = 0.005
                    self.C_storage_gas_percent = 0.07
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == 'baleage':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.40
                    self.C_harvest_gas_percent = 0.015
                    self.C_harvest_particle_percent = 0.005
                    self.C_storage_gas_percent = 0.12
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                else:
                    if self.error_flag_0:
                        print('"' + self.moisture + '"', 'is not a recognized moisture category for', self.crop_name)
                        self.error_flag_0 = False

            elif self.crop_name == 'alfalfa':
                self.storage = True
                self.CP_percent = 0.22
                self.C_percent = 0.58
                if self.moisture == 'direct_cut':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0.025
                    self.NPN_min_percent = 0.40
                    self.C_harvest_gas_percent = 0.03
                    self.C_harvest_particle_percent = 0
                    self.C_storage_gas_percent = 0.095
                    self.C_storage_leachate_percent = 0.025
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == 'wilted':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.40
                    self.C_harvest_gas_percent = 0.035
                    self.C_harvest_particle_percent = 0.015
                    self.C_storage_gas_percent = 0.09
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == 'haylage':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.35
                    self.C_harvest_gas_percent = 0.045
                    self.C_harvest_particle_percent = 0.025
                    self.C_storage_gas_percent = 0.07
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == 'moist_hay':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.30
                    self.C_harvest_gas_percent = 0.07
                    self.C_harvest_particle_percent = 0.10
                    self.C_storage_gas_percent = 0.03
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0
                    self.C_feed_out_particle_percent = 0.01
                elif self.moisture == 'dry_hay':
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.20
                    self.C_harvest_gas_percent = 0.07
                    self.C_harvest_particle_percent = 0.16
                    self.C_storage_gas_percent = 0.02
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0
                    self.C_feed_out_particle_percent = 0.01
                else:
                    if self.error_flag_1:
                        print('"' + self.moisture + '"', 'is not a recognized moisture category for', self.crop_name)
                        self.error_flag_1 = False
            else:
                if self.error_flag_2:
                    print('"' + self.crop_name + '"', 'storage is not currently implemented. Crop is not being stored.')
                    self.storage = False
                    self.error_flag_2 = False

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
        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.CP = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

        self.NPN = 0.0

        for storage_name, storage in self.storage_options.items():
            self.storage_options[storage_name] = self.feed_out(storage)

        self.available_storage = dict(self.storage_options)

    def feed_out(self, storage):
        hold_over_data = {
            'storage_type': storage.storage_type,
            'moisture': storage.moisture,
            'additive': storage.additive,
            'packing_density': storage.packing_density,
            'inoculation': storage.inoculation,
            'bunk_type': storage.bunk_type,
            'ventilation': storage.ventilation,
            'removal_rate': storage.removal_rate,
            'initial_dry_matter': 0
        }

        return self.Storage(hold_over_data)
