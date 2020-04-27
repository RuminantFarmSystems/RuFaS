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
from RUFAS import util
from enum import IntEnum
from RUFAS.util import DatabaseReader

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
    Description:
        Stores the information for the feeds managed by the farm, and the methods
        for storage.

    """

    def __init__(self, data):
        """
        Sets up the data for the feeds managed by the farm.
        Currently stores and updates the Feed Inventory Information
        TODO: Oncce there is a function to modify data in the database we will
        use that to store inventory information, but for now we will store in the object

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
        #Initilizing a Dictionary that keeps track of the current Feed inventory in kg
        #currently hard coded values. TODO Link with crop module
        self.feed_inv = {'Corn_grain': 10000, 'Legume_hay': 3000000, 'Cotton_seed': 1200000, 'Roasted_soybean': 130000, 'Rye_hay': 1300000}


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
    #The Following Functions are used for Updating Feed Inventory and Feed allocation
    def feed_allocation(self):
        '''
        Allocates farm grown feeds to be used for single or multiple animal classes. Priority is to
        reserve high-quality forage for lactating cows.
        '''
        forage_quality_assesment()
        pass

    def forage_quality_assesment(self):
        '''
        Asseses quality of forage and populates lists of self.high_quality_forage
        and self.low_quality_forage
        '''
        pass

    def days_since_feedout(self):
        '''
        populations the days_since_feedout variable in Feed class
        '''
        pass

    def forage_inv_plan(self, animal_management):

        '''
        Assess farm grown forage stocks and plans maximum intake of each forage to ensure there is enough forage to last a FULL YEAR.
        Forage inventory is conducted at least 1x/year after harvest and then at a user specified number of times.
        Note that the inventory should be executed at the end of the ‘simulation day’, preferably on the last day of a ration formulation interval
        '''

        #Begingin by creating a dictionary of all the current animals and animal information
        animals = {'calves': animal_management.calves, 'heiferIs': animal_management.heiferIs, 'heiferIIs': animal_management.heiferIIs,
        'heiferIIIs' : animal_management.heiferIIIs}
        lactating_cows = []
        dry_cows = []
        for cow in animal_management.cows:
            if cow._milking:
                lactating_cows.append(cow)
            else:
                dry_cows.append(cow)

        animals['dry_cows'] = dry_cows
        animals['lactating_cows'] = lactating_cows

        #Computing Important values necessary for feed calculations for all cows
        avg_BW = {} #average bodyweight for each animal type
        animal_class_size_avg = {} #total number of this type of animal
        for key in animals:
            BW = 0
            for animal in animals[key]:
                BW += animal._body_weight
            animal_class_size_avg[key] = len(animals[key])
            if len(animals[key]) > 0:
                avg_BW[key] = BW / len(animals[key])
            else:
                avg_BW[key] = 0

        #This dictionary contains dictionaries of information for each forage; specifically the required
        #inventory for the corresponding animal class (in kg of DM)
        Req_Inv = {'calves': {}, 'heiferIs': {}, 'heiferIIs': {}, 'heiferIIIs': {}, 'dry_cows': {}, 'lactating_cows': {}}
        #the hard-coded input of recomended inclusion rate of Forage as a percent of bodyweight per animal
        #for now, base on the pseudo code these values are not unique to diff feeds
        Inclusion_pct = {'calves': 2.0, 'heiferIs': 2.0, 'heiferIIs': 2.0, 'heiferIIIs': 2.0, 'dry_cows': 1.7, 'lactating_cows': 2.0}
        #Estimated Inclusion rate to meet this type of animals requirments
        Inclusion_rate_est = {}
        for animal in Inclusion_pct:
            Inclusion_rate_est[animal] = {}
            for feed in self.new_forages:
                Inclusion_rate_est[animal][feed] = (Inclusion_pct[animal]/100) * avg_BW[animal]

        #the number of days until the expected start date for feedout of each forage from next harvest
        Days_remaining = {}
        for feed_key in self.new_forages:
            Days_remaining[feed_key] = 365 - self.days_since_feedout[feed_key]
        #total number of feeding days until next year's Forage begins to be fed out
        Cow_days = {'calves': {}, 'heiferIs': {}, 'heiferIIs': {}, 'heiferIIIs': {}, 'dry_cows': {}, 'lactating_cows': {}}
        for animal in Cow_days:
            for feed_key in self.new_forages:
                Cow_days[animal][feed_key] = animal_class_size_avg[animal] * Days_remaining[feed_key]
        #populating Req_Inv dictionary (key represents the type of feed)
        for animal in Cow_days:
            for feed_key in self.new_forages:
                Req_Inv[animal][feed_key] = Inclusion_rate_est[animal][feed_key] * Cow_days[animal][feed_key]
        ##Next, setting the max feed intake for each forage so it will be available all year##
        DMI_Forage_max = {'calves': {}, 'heiferIs': {}, 'heiferIIs': {}, 'heiferIIIs': {}, 'dry_cows': {}, 'lactating_cows': {}}     #for each type of feed
        for feed in self.new_forages:                   #for each type of animal
            if (feed in self.high_quality_forage):
                if 1.1*Req_Inv[feed] >= self.feed_inv[feed]:
                    DMI_Forage_max['lactating_cows'][feed] = self.feed_inv[feed] / Cow_days['lactating_cows'][feed]
                else:
                    DMI_Forage_max[animal][feed] = 1.1 * Inclusion_rate_est['lactating_cows'][feed]
            elif (feed not in self.high_quality_forage):
                Tot_Req_Inv = 0
                for animal in animals:                      #For-loop used to calculate sum of Required Inventory of this feed
                    Tot_Req_Inv += Req_Inv[animal][feed]    #Total Required inventory for this feed
                Tot_Req_Inv_nlcow = Tot_Req_Inv - Req_Inv['lactating_cows'][feed]  #All animals except lactating cows for this feed
                if Tot_Req_Inv <= self.feed_inv[feed]:
                    for animal in animals:
                        DMI_Forage_max[animal][feed] = Inclusion_rate_est[animal][feed]
                    Available_Forage = self.feed_inv[feed] - Tot_Req_Inv_nlcow
                    DMI_Forage_max['lactating_cows'][feed] = Available_Forage / Cow_days['lactating_cows'][feed]
                else:
                    Inv_delta = Tot_Req_Inv - self.feed_inv[feed]
                    denom = 0
                    for animal_key in animals:              #For-loop used to calculate sum of Reqired Inventory minus lac. Cows
                        if animal_key != 'lactating_cows':
                            denom += (avg_BW[animal_key] * Cow_days[animal_key][feed])
                    Inclusion_pct_delta = Inv_delta / denom
                    Available_Forage = self.feed_inv[feed]
                    for animal in animals:
                        if animal != 'lactating_cows':
                            Inclusion_rate_est[animal][feed] = Inclusion_pct[animal] - Inclusion_pct_delta
                            DMI_Forage_max[animal][feed] = Inclusion_rate_est[animal][feed]
                            Available_Forage -= Inclusion_rate_est[animal][feed]*Cow_days[animal][feed]
                    if Available_Forage > 0:
                        DMI_Forage_max['lactating_cows'][feed] = Available_Forage / Cow_days['lactating_cows'][feed]
                    else:
                        DMI_Forage_max['lactating_cows'][feed] = 0
        self.DMI_Forage_max = DMI_Forage_max

    def daily_updates(self, animal_management, time):

        if ('Time for Forage Plan'):
            self.forage_inv_plan(animal_management)


        if animal_management.end_ration_interval():
            pass


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
        #
        # self.available_storage = self.storage_options
