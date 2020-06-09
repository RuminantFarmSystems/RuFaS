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

from RUFAS.util import DatabaseReader
import sqlite3
from . import nitrogen_loss, carbon_loss, protein_degradation


def daily_feed_routine(feed, crop):
    """
    Description:
        Runs the feed storage routine. Yield is stored at harvest in available storage.
        Once used, that storage receptacle is removed from the list of available storage.
        If insufficient storage is specified, a "standard" storage receptacle is generated.

    Args:
        feed: an instance of the Feed object specified in feed.py
        crop: an instance of the Crop object specified in crop.py
    """
    current_crop = crop.current_crop

    if current_crop.yield_actual != 0:
        if len(feed.available_storage) == 0:
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

            standard_name = 'standard_storage_' + str(feed.standard_storage_count)
            feed.available_storage[standard_name] = feed.Storage(standard_data)
            feed.storage_options[standard_name] = feed.available_storage[standard_name]

        storage_name, storage = feed.available_storage.popitem()
        feed.storage_options[storage_name].calibrate_storage(current_crop)
        feed.storage_options[storage_name].store_crop(current_crop)

        feed.summarize_feed_storage(feed.storage_options[storage_name])


def annual_feed_routine():
    pass


class Feed:
    """
    Description:
        Stores the information for the feeds managed by the farm, and the methods
        for storage.

    """

    def __init__(self, data):
        """
        Sets up the data for the feeds managed by the farm.

        Args:
            data: the feed information from the input JSON file
        """
        self.__feed_database = data["feed_database"]
        self.__feeds_table = 'user_feeds'
        self.__feed_quality_table = 'feed_quality'
        self.__nutrient_table = 'nutrients'

        self.entries_split_by_maturity = self.get_feeds_split_by_maturity()
        self.growing_feeds = data['growing_feeds']
        self.purchased_feeds = []  # set in the next method call

        self.all_feed_ids = self.get_all_feed_units(data['purchased_feeds'],
                                                    data['growing_feeds'])

        # dictionary of nutrients needed for this run
        # initially, this only contains information for purchased feeds as none
        # of the growing_feeds have been harvested yet
        self.available_feeds = \
            self.get_nutrient_vals(self.purchased_feeds, False)

        # The nutrient requirements used in the ration calculations.
        self.nutrient_rqmts = ['FU', 'RU', 'ME_DM', 'RDP_DM', 'RUP_DM']

        self.storage_options = {}

        for storage_name, storage_data in data['storage_options'].items():
            self.storage_options[storage_name] = self.Storage(storage_data)

        self.available_storage = dict(self.storage_options)
        self.standard_storage_count = 0

        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.CP = 0.0
        self.NPN = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

    class Storage:
        def __init__(self, data):
            """
            Description:
                A subclass of feed storage specifying a single storage receptacle.

            Args:
                data: a dictionary containing information to define the storage
                    receptacle
            """
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

            self.DM = data['initial_dry_matter']

            self.C_percent = 0.0

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

            self.error_1 = True
            self.error_2 = True
            self.error_3 = True

        def calibrate_storage(self, crop):
            """
            Description:
                Calibrates the feed storage loss model to the crop being stored in the receptacle.
                Based on information provided by Kevin Painke-Buisse of the DFRC 2019
                "pseudocode_feed" F.1.4
            Args:
                crop: The crop to be stored
            """
            self.crop_name = crop.crop_name

            if self.crop_name == 'corn':
                self.storage = True
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
                    if self.error_1:
                        print('"' + self.moisture + '"', 'is not a recognized moisture category for', self.crop_name)
                        self.error_1 = False

            elif self.crop_name == 'alfalfa':
                self.storage = True
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
                    if self.error_2:
                        print('"' + self.moisture + '"', 'is not a recognized moisture category for', self.crop_name)
                        self.error_2 = False
            else:
                if self.error_3:
                    print('"' + self.crop_name + '"', 'storage is not currently implemented')
                    self.storage = False
                    self.error_3 = False

        def store_crop(self, crop):
            """
            Description:
                Updates mineral components and losses as a crop is stored.
            Args:
                crop: The crop being stored.
            """

            if self.storage:
                # "pseudocode_feed" F.1.1
                self.DM += crop.yield_actual
                self.N += crop.yield_N
                self.P += crop.yield_P
                # TODO: no Carbon Cycle currently implemented
                self.C += crop.yield_actual * self.C_percent

                # "pseudocode_feed" F.1.2
                self.CP += 6.25 * self.N / self.DM

                # "pseudocode_feed" F.1.3
                carbon_loss.update_all(self)
                nitrogen_loss.update_all(self)
                # TODO: No protein degradation currently implemented
                protein_degradation.update_all()

        def reset_storage(self):
            """
            Description:
                Resets storage receptacle to initial settings.
            """
            reset_data = {
                "storage_type": self.storage_type,
                "moisture": self.moisture,
                "additive": self.additive,
                "packing_density": self.packing_density,
                "inoculation": self.inoculation,
                "bunk_type": self.bunk_type,
                "ventilation": self.ventilation,
                "removal_rate": self.removal_rate,
                "initial_dry_matter": 0
            }

            self.__init__(reset_data)

    def summarize_feed_storage(self, storage):
        """
        Description:
            Accumulates feed storage data as feed is stored in various receptacles
        Args:
            storage: The storage receptacle from which information is currently being aggregated
        """
        self.C += storage.C
        self.N += storage.N
        self.P += storage.P
        self.DM += storage.DM
        self.CP += storage.CP
        self.NPN += storage.NPN

        self.C_loss += storage.C_loss
        self.CP_loss += storage.CP_loss

    def annual_reset(self):
        """
        Description:
            Resets the accumulated data so they can be interpreted as annual sums.
            Option to reset feed storage model entirely each year.
        """
        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.CP = 0.0
        self.NPN = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

        # TODO: method for resetting storage allocation. Makes use of reset_storage helper method.
        #  Similar structure should be used in feed out
        # for storage in self.storage_options.values():
        #     storage.reset_storage()

    def get_feeds_split_by_maturity(self):
        """
        Returns the feed entries in the database which have different qualities
        based on nutrient values at harvest. Quits the program if an exception
        is raised when querying the database.

        Returns: a set-like list of the entries listed in the table which splits
            feeds by quality
        """
        try:
            result = []
            conn = sqlite3.connect(self.__feed_database)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "SELECT DISTINCT entry FROM " + self.__feed_quality_table

            c.execute(query)

            row = c.fetchone()
            while row is not None:
                result.append(dict(row)['entry'])
                row = c.fetchone()

            conn.close()
            return result

        except Exception as e:
            print("The program has encountered the following exception while"
                  "connecting to and querying the feed database:", e,
                  "\nExiting.")
            exit(1)

    def get_all_feed_units(self, purchased_feeds, grown_feeds):
        """
        Constructs and returns the list of tuples of the feed entries given by
        the user and their units.  Quits the program if an exception
        is raised when querying the database.

        Args:
            purchased_feeds: the list of entries (ints) of feeds that are
                purchased
            grown_feeds: the list of entries (ints) of feeds that will be grown

        Returns:
            a list of tuples of the form (ID, units) for each feed, where
            - if the feed is purchased, ID is the string form of the ID
            (e.g. '2')
            - if the feed is grown, ID is the string form of the ID plus 'g'
            (e.g. '8g')
            - units is the string representing the units for the feed
        """
        try:
            result = []
            conn = sqlite3.connect(self.__feed_database)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            combined_feeds = purchased_feeds + grown_feeds
            query = "SELECT units FROM " + self.__feeds_table + \
                    " WHERE entry IN " + str(tuple(combined_feeds))

            c.execute(query)

            row = c.fetchone()
            units = []
            while row is not None:
                units.append(dict(row)['units'])
                row = c.fetchone()

            self.purchased_feeds = self.get_purchased_feed_ids(purchased_feeds)

            purchased_feeds_str = [str(feed) for feed in self.purchased_feeds]
            grown_feeds_str = [str(feed) + 'g' for feed in grown_feeds]
            for feed, unit in zip(purchased_feeds_str + grown_feeds_str, units):
                result.append((feed, unit))

            conn.close()
            return result

        except Exception as e:
            print("The program has encountered the following exception while"
                  "connecting to and querying the feed database:", e,
                  "\nExiting.")
            exit(1)

    def get_purchased_feed_ids(self, entries):
        """
        Constructs and returns a list of the purchased feed IDs based on
        whether the quality of each feed can be determined at harvest. Quits
        the program if an exception is raised when querying the database.

        Args:
            entries: the purchased feed entries

        Returns:
            a list of the feed IDs that can be used to find nutrient values in
            the nutrients table
        """
        purchased_feed_ids = []
        for entry in entries:
            if entry in self.entries_split_by_maturity:
                # making the assumption that purchased feeds are at mid-maturity
                purchased_feed_ids.append(entry + 2)
            else:
                purchased_feed_ids.append(entry)
        return purchased_feed_ids

    def get_feed_id(self, grown_feed_entry, DM, NDF):
        """
        First queries the database to find which nutrient must be used to find
        the quality of the feed, then uses the feed's value for that nutrient
        to find the quality by finding which range it belongs to. Returns
        the feed ID associated with that quality. Quits the program if an
        exception is raised when querying the database.

        Args:
            grown_feed_entry: the entry of the feed that needs to be added to
                available_feeds
            DM: the dry matter percentage
            NDF: the NDF percentage

        Returns: the feed ID corresponding to the appropriate quality of the
        grown_feed_entry according to its specific differentiating nutrient
        """
        # round both values to the nearest integer
        rounded_DM = round(DM)
        rounded_NDF = round(NDF)
        try:
            conn = sqlite3.connect(self.__feed_database)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            nutrient_query = "SELECT DISTINCT differentiating_nutrient FROM " \
                             + self.__feed_quality_table + \
                             " WHERE entry = " + str(grown_feed_entry)

            c.execute(nutrient_query)
            rows = c.fetchall()

            nutrient = rows[0][0]

            if nutrient == 'DM':
                query = "SELECT quality_id FROM " + self.__feed_quality_table \
                        + " WHERE entry = " + str(grown_feed_entry) + \
                        " AND low_percent <= " + str(rounded_DM) + \
                        " AND high_percent >= " + str(rounded_DM)
            else:
                query = "SELECT quality_id FROM " + self.__feed_quality_table \
                        + " WHERE entry = " + str(grown_feed_entry) + \
                        " AND low_percent <= " + str(rounded_NDF) + \
                        " AND high_percent >= " + str(rounded_NDF)

            c.execute(query)
            rows = c.fetchall()

            return rows[0][0]

        except Exception as e:
            print("The program has encountered the following exception while"
                  "connecting to and querying the feed database:", e,
                  "\nExiting.")
            exit(1)

    def add_to_available_feeds(self, new_grown_feeds, DM_list, NDF_list):
        """
        Appends the nutrient values of new_grown_feeds to the available_feeds
        dictionary according to their quality (if applicable). If a feed is
        not split by quality, then the values at the respective indices of
        DM_list and NDF_list are ignored.

        Args:
            new_grown_feeds: the list of feed entries to be added to
                available_feeds with nutrient values based on their quality
            DM_list: the list of dry matter percentages for each feed in
                new_grown_feeds (indices match up)
            NDF_list: the list of NDF percentages for each feed in
                new_grown_feeds (indices match up)
        """
        new_feed_ids = []
        for i, new_feed in enumerate(new_grown_feeds):
            if new_feed in self.entries_split_by_maturity:
                new_feed_ids.append(
                    self.get_feed_id(new_feed, DM_list[i], NDF_list[i]))
            else:
                new_feed_ids.append(new_feed)
        self.available_feeds.update(self.get_nutrient_vals(new_feed_ids, True))

    def update_available_feed(self, feed_id, nutrient, new_val):
        """
        Updates the dictionary of available feeds with a particular nutrient
        value.

        Args:
            feed_id: the ID of the feed to be modified
            nutrient: the nutrient to be modified
            new_val: the new value of the nutrient
        """
        self.available_feeds[feed_id][nutrient] = new_val

    def remove_from_available_feeds(self, feeds_to_be_removed):
        """
        Removes the IDs in feeds_to_be_removed from available_feeds.

        Args:
            feeds_to_be_removed: a list of feed IDs
        """
        for feed_id in feeds_to_be_removed:
            self.available_feeds.pop(feed_id)

    def get_nutrient_vals(self, feed_ids, is_grown):
        """
        Constructs and returns the dictionary of nutrient values for the feeds
        represented by feed_ids. Quits the program if an exception
        is raised when querying the database.

        Args:
            feed_ids: list of feed IDs
            is_grown: boolean - true if the feeds represented by feed_ids are
                grown, false if purchased

        Returns: a dictionary where the keys are the the feed identifiers and
        the values are nutrient dictionaries
        """
        try:
            nutrient_vals = {}
            conn = sqlite3.connect(self.__feed_database)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "SELECT * FROM " + self.__nutrient_table + \
                    " WHERE feed_id IN " + str(tuple(feed_ids))

            c.execute(query)

            row = c.fetchone()
            while row is not None:
                vals = dict(row)
                feed_id = vals['feed_id']

                # the key in the available_feeds dictionary has a 'g' as the
                # suffix if it is a grown feed
                feed_key = str(feed_id)
                if is_grown:
                    feed_key += 'g'

                nutrient_vals[feed_key] = vals
                row = c.fetchone()

            conn.close()
            return nutrient_vals

        except Exception as e:
            print("The program has encountered the following exception while"
                  "connecting to and querying the feed database:", e,
                  "\nExiting.")
            exit(1)
