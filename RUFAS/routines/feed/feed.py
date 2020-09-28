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
           Chris Vankerkhove, cjv47@cornell.edu
"""

from RUFAS.util import DatabaseReader
from . import nitrogen_loss, carbon_loss, protein_degradation
from RUFAS.routines.animal.ration import hardcoded_ration


def daily_feed_routine(feed, fields, animal_management):
    """
    Description:
        Runs the feed storage routine. Yield is stored at harvest in available
        storage grouped by crop type and quality. Once used, that storage
        receptacle is removed from the list of available storage. If insufficient
        storage is specified, a "standard" storage receptacle is generated.

    Args:
        feed: an instance of the Feed object
        fields: an instance of the Field object (contains harvest information)
        animal_management: an instance of the AnimalManagement object
    """

    # aggregate crop yield across fields
    for field in fields:
        crop = field.crop.current_crop
        # there is forage to be stored
        if crop.yield_actual != 0:
            stored = False
            # search for matching storage profile
            for storage in feed.available_storage.values():
                if storage.feed_id == crop.feed_id and storage.storage is True \
                        and storage.storage_quality == crop.harvest_quality \
                        and not stored:
                    storage.store_crop(crop)
                    if storage not in feed.new_forages:
                        feed.new_forages.append(storage)
                    stored = True

            # search for available, empty storage
            if not stored:
                for storage in feed.available_storage.values():
                    if storage.DM == 0 and not stored:
                        storage.calibrate_storage(crop)
                        storage.store_crop(crop)
                        if storage not in feed.new_forages:
                            feed.new_forages.append(storage)
                        stored = True

            # generate standard storage
            if not stored:
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

                    feed.standard_storage_count += 1

                storage_name, storage = feed.available_storage.popitem()
                feed.storage_options[storage_name].calibrate_storage(crop)
                feed.storage_options[storage_name].store_crop(crop)
                if storage not in feed.new_forages:
                    feed.new_forages.append(storage)

    # calculate losses and update storage options after crop allocation
    for storage_name, storage in feed.storage_options.items():
        if storage_name in feed.available_storage and storage.DM != 0:
            storage.calculate_losses()
            feed.available_storage.pop(storage_name)

        feed.summarize_feed_storage()

    # feed management routines to be run daily
    feed.daily_feed_management(animal_management)


def annual_feed_routine(feed):
    feed.reset_feed()


class Feed:
    def __init__(self, data):
        """
        Description:
            Stores the information for the feeds managed by the farm, and the methods
            for storage.
            TODO: Store inventory information in database once write function is implemented

        Args:
            data: the feed information from the input JSON file
        """
        self.feed_database = data['feed_database']
        self.feeds_table = data['feeds_table']
        self.feed_quality_table = data['feed_quality_table']
        self.nutrient_table = data['nutrient_table']

        self.db_reader = DatabaseReader(self.feed_database)

        self.entries_split_by_maturity = self.get_feeds_split_by_maturity()
        self.growing_feeds = data['growing_feeds']
        self.purchased_feeds_entries = data['purchased_feeds']
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

        # Storage receptacles managed by the feed module
        self.storage_options = {}

        for storage_name, storage_data in data['storage_options'].items():
            self.storage_options[storage_name] = self.Storage(storage_data)

        self.available_storage = dict(self.storage_options)
        self.standard_storage_count = 0

        # Summary variables tracked for output
        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.NDF = 0.0
        self.CP = 0.0
        self.NPN = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

        # a list of storage objects with new crops
        self.new_forages = []
        # this variable is a placeholder for average body weight of animals for
        # max intake calculations
        self.animal_avg_BW = {}

    def summarize_feed_storage(self):
        """
        Description:
            Summarize nutrients and losses over the managed storage receptacles
        """
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

            self.DM = data['initial_dry_matter']

            self.crop_name = 'null'

            self.storage_quality = 'null'

            self.storage = True

            self.CP_percent = 0.0
            self.C_percent = 0

            self.feed_id = 'null'
            self.forage_quality = 'null'

            self.DMI_forage_max = {'calves': 0,
                                   'heiferIs': 0,
                                   'heiferIIs': 0,
                                   'heiferIIIs': 0,
                                   'dry_cows': 0,
                                   'lactating_cows': 0
                                   }

            self.days_since_feedout = -1
            self.req_inv = {}
            self.cow_days = {}
            self.inclusion_rate_est = {}
            self.inclusion_pct = {}

            self.C_percent = 0.0

            self.NDF = 0.0
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
            self.storage_quality = crop.harvest_quality
            self.feed_id = crop.feed_id

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

        def store_crop(self, crop):
            """
            Description:
                Helper method for "storing" the specified crop
                Updates mineral components and losses as a crop is stored.
                "pseudocode_feed" F.1.1

            Args:
                crop: the crop to be stored
            """
            if self.storage:
                if self.DM == 0:
                    # forage to be fed out 30 days after harvest for new yield
                    self.days_since_feedout = -30
                self.feed_id = crop.feed_id
                self.DM += crop.yield_actual
                self.NDF += crop.NDF_yield
                self.N += crop.N_yield
                self.P += crop.P_yield
                # TODO: no Carbon Cycle currently implemented
                self.C += crop.yield_actual * self.C_percent

                # "pseudocode_feed" F.1.2
                self.CP += 6.25 * self.N / self.DM

                # Reset harvest quality for the crop
                crop.harvest_quality = ''

        def calculate_losses(self):
            """
            Description:
                Calculates mineral losses for the storage method once all crops are stored
                "pseudocode_feed" F.1.3
            """
            carbon_loss.update_all(self)
            nitrogen_loss.update_all(self)
            # TODO: No protein degradation currently implemented
            protein_degradation.update_all()

        def reset_storage(self):
            """
            Description:
                Storage class method resets receptacle to initial settings.
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

    def required_inventory(self, storage, animal_management):
        """
        Description:
            Computes the required inventory necessary across all animals for a
            given forage based on the count of the animals, the body weight,
            and inclusion percent associated with the input forage. This class
            method for the feed class updates feed class variables along with class
            variables associated with the input storage object. Each calculation
            has a reference to the respective calculation in the pseudocode

        Args:
            storage: a storage object that contains forage being assessed
            animal_management: the class object Animal Management which tracks the state of the animals
        """
        # animals = dictionary with animals as keys and animal objects as values
        animals = {'calves': animal_management.calves,
                   'heiferIs': animal_management.heiferIs,
                   'heiferIIs': animal_management.heiferIIs,
                   'heiferIIIs': animal_management.heiferIIIs
                   }
        lactating_cows = []
        dry_cows = []
        for cow in animal_management.cows:
            if cow.milking:
                lactating_cows.append(cow)
            else:
                dry_cows.append(cow)

        animals['dry_cows'] = dry_cows
        animals['lactating_cows'] = lactating_cows

        avg_BW = {}
        animal_class_size_avg = {}
        # avg_BW = Average bodyweight of specified Animal Class (kg)
        for key in animals:
            BW = 0
            for animal in animals[key]:
                BW += animal.body_weight
            animal_class_size_avg[key] = len(animals[key])
            if len(animals[key]) > 0:
                avg_BW[key] = BW / len(animals[key])
            else:
                avg_BW[key] = 0

        # inclusion_pct = recommended inclusion rate as a percentage of
        # bodyweight for Animal Class
        # (currently not unique across different feeds)
        inclusion_pct = {'calves': 2.0,
                         'heiferIs': 2.0,
                         'heiferIIs': 2.0,
                         'heiferIIIs': 2.0,
                         'dry_cows': 1.7,
                         'lactating_cows': 2.0
                         }

        # inclusion_rate_est = Estimated inclusion rate to meet Animal Class
        # requirements (kg DM)
        # [F.2.A.5]
        inclusion_rate_est = {}
        for animal in inclusion_pct:
            inclusion_rate_est[animal] = (inclusion_pct[animal] / 100) * avg_BW[animal]

        # days_remaining = the number of days until the expected start date for
        # feedout from the next harvest
        days_remaining = 365 - storage.days_since_feedout

        # cow_days = total number of feeding days until next year’s forage
        # begins to be fed out
        cow_days = {'calves': {},
                    'heiferIs': {},
                    'heiferIIs': {},
                    'heiferIIIs': {},
                    'dry_cows': {},
                    'lactating_cows': {}
                    }

        for animal in cow_days:
            cow_days[animal] = animal_class_size_avg[animal] * days_remaining

        # req_inv = required inventory for corresponding animal class (kg DM)
        req_inv = {'calves': 0,
                   'heiferIs': 0,
                   'heiferIIs': 0,
                   'heiferIIIs': 0,
                   'dry_cows': 0,
                   'lactating_cows': 0
                   }

        # [F.2.A.4]
        for animal in cow_days:
            req_inv[animal] = inclusion_rate_est[animal] * cow_days[animal]

        # updating class variables for input storage object input
        storage.req_inv = req_inv
        storage.cow_days = cow_days
        storage.inclusion_rate_est = inclusion_rate_est
        storage.inclusion_pct = inclusion_pct
        self.animal_avg_BW = avg_BW

    def forage_inv_plan(self, storage):
        """
        Description:
            Assess farm grown forage stocks and plan maximum intake of each
            forage to ensure there is enough forage to last a FULL YEAR.
            Forage inventory is conducted at least 1x/year after harvest and
            then at a user specified number of times. This function calculates
            those values and stores it in the input storage object. Each calculation
            has a reference to its respective calculation in the pseduocode

        Args:
            storage: the storage object containing the forage being assessed
        """
        # TODO: Incorporate user specified input for frequency of inventory plan
        # TODO: Raise warning for when additional forage needs to be purchased
        # TODO: Add remaining forage to other silos with same forage type

        # HIGH QUALITY FORAGE
        # Calculating DMI for Lactating Cows only
        # ------------------------------
        if storage.forage_quality == 'immature' or storage.forage_quality == 'mid_mature':
            # [F.2.A.6]
            if 1.1 * storage.req_inv['lactating_cows'] >= storage.DM:
                storage.DMI_forage_max['lactating_cows'] = storage.DM / \
                                                           storage.cow_days['lactating_cows']
            else:
                storage.DMI_forage_max['lactating_cows'] = 1.1 * \
                                                           storage.inclusion_rate_est['lactating_cows']

        # LOW QUALITY FORAGE
        # Calculating DMI for all EXCEPT Lactating Cows
        # ------------------------------
        elif storage.forage_quality == 'mature':
            tot_req_inv_non_lactating_cows = 0
            # updating required inventory for non lactating cows
            for animal in storage.req_inv:
                if animal != 'lactating_cows':
                    tot_req_inv_non_lactating_cows += storage.req_inv[animal]
            # Assigning DMI when there is sufficient inventory
            # [F.2.A.9]
            if tot_req_inv_non_lactating_cows <= storage.DM:
                storage.DMI_forage_max = storage.inclusion_rate_est
                storage.DMI_forage_max['lactating_cows'] = 0
            # updating inclusion rate estimate until inventory is sufficient to
            # satisfy the newly calculated inclusion rate estimate
            # [F.2.A.10]
            else:
                while round(tot_req_inv_non_lactating_cows) > round(storage.DM):
                    inv_delta = tot_req_inv_non_lactating_cows - storage.DM
                    denominator = 0

                    for animal in self.animal_avg_BW:
                        if animal != 'lactating_cows':
                            denominator += (self.animal_avg_BW[animal] * storage.cow_days[animal])

                    inclusion_pct_delta = inv_delta / denominator

                    for animal in storage.inclusion_rate_est:
                        storage.inclusion_pct[animal] = max(
                            storage.inclusion_pct[animal] / 100 - inclusion_pct_delta, 0) * \
                                                        100
                        storage.inclusion_rate_est[animal] = (storage.inclusion_pct[animal] / 100) * \
                                                             self.animal_avg_BW[animal]
                        storage.req_inv[animal] = storage.inclusion_rate_est[animal] * \
                                                  storage.cow_days[animal]

                    tot_req_inv_non_lactating_cows = 0

                    for animal in storage.req_inv:
                        if animal != 'lactating_cows':
                            tot_req_inv_non_lactating_cows += storage.req_inv[animal]

                storage.DMI_forage_max = storage.inclusion_rate_est
                storage.DMI_forage_max['lactating_cows'] = 0

        # NO QUALITY ASSESSMENT
        # Calculating DMI for all animal classes
        # -----------------------------
        else:
            # calculating total required inventory across all animal classes
            tot_req_inv = sum(storage.req_inv.values())
            # assigning DMI when there is sufficient inventory
            # [F.2.A.7]
            if tot_req_inv <= storage.DM:
                tot_req_inv_non_lactating_cows = 0

                for animal in storage.DMI_forage_max:
                    if animal != 'lactating_cows':
                        storage.DMI_forage_max[animal] = storage.inclusion_rate_est[animal]
                        tot_req_inv_non_lactating_cows += storage.inclusion_rate_est[animal]

                available_forage = storage.DM - tot_req_inv_non_lactating_cows
                if storage.cow_days['lactating_cows'] > 0:
                    storage.DMI_forage_max['lactating_cows'] = available_forage \
                                                               / storage.cow_days['lactating_cows']
            # updating inclusion rate estimate until inventory is sufficient to
            # satisfy that newly calculated inclusion rate estimate
            # [F.2.A.8]
            else:
                while round(tot_req_inv) > round(storage.DM):
                    inv_delta = tot_req_inv - storage.DM
                    denominator = 0
                    for animal in self.animal_avg_BW:
                        if animal != 'lactating_cows':
                            denominator += (self.animal_avg_BW[animal] * storage.cow_days[animal])

                    inclusion_pct_delta = inv_delta / denominator

                    for animal in storage.inclusion_rate_est:
                        storage.inclusion_pct[animal] = max(storage.inclusion_pct[animal] / 100 - inclusion_pct_delta,
                                                            0) * 100
                        storage.inclusion_rate_est[animal] = (storage.inclusion_pct[animal] / 100) * \
                                                             self.animal_avg_BW[animal]
                        storage.req_inv[animal] = storage.inclusion_rate_est[animal] * storage.cow_days[animal]

                    tot_req_inv = sum(storage.req_inv.values())

                tot_req_inv_non_lactating_cows = 0
                for animal in storage.DMI_forage_max:
                    if animal != 'lactating_cows':
                        storage.DMI_forage_max[animal] = storage.inclusion_rate_est[animal]
                        tot_req_inv_non_lactating_cows += storage.inclusion_rate_est[animal]

                available_forage = storage.DM - tot_req_inv_non_lactating_cows

                storage.DMI_forage_max['lactating_cows'] = 0
                if storage.cow_days['lactating_cows'] != 0:
                    storage.DMI_forage_max['lactating_cows'] = available_forage / storage.cow_days['lactating_cows']

                storage.DMI_forage_max = storage.inclusion_rate_est

    def daily_feed_management(self, animal_management):
        """
        Description:
            Executes daily routines relating to feed management, specifcally a
            daily feedout process and checking for new forages that need an
            inventory plan. If the list new_forages contains a forage which
            had been harvested at least 30 days ago, forage_inv_plan will be called.

        Args:
            animal_management: The state of the AnimalManagement class object
        """
        # Daily feedout for silos with farm grown forages in them per pen based on ration formulated
        for silo in self.storage_options:
            if self.storage_options[silo].days_since_feedout >= 0 and self.storage_options[silo].DM > 0:
                # TODO: change for when ration formulation is implemented
                ration = hardcoded_ration.get_ration()
                if self.storage_options[silo].feed_id in ration:
                    for pen in animal_management.all_pens:
                        if (self.storage_options[silo].DM - pen.ration[str(self.storage_options[silo].feed_id)]) > 0:
                            self.storage_options[silo].DM -= pen.ration[str(self.storage_options[silo].feed_id)]
                        else:
                            self.storage_options[silo].DM = 0
                            self.storage_options[silo].reset_storage()
                            break
                self.storage_options[silo].days_since_feedout += 1
            elif self.storage_options[silo] not in self.new_forages:
                self.storage_options[silo].days_since_feedout += 1
        # inventory plan for new forages
        for silo in self.new_forages:
            if silo.days_since_feedout >= -1 and animal_management.end_ration_interval():
                self.required_inventory(silo, animal_management)
                self.forage_inv_plan(silo)
                self.add_to_available_feeds(silo.feed_id, silo.DM, silo.NDF)
                silo.days_since_feedout += 1
                self.new_forages.pop(self.new_forages.index(silo))
            else:
                silo.days_since_feedout += 1
        # yearly reset of silos
        # TODO: modify when ration formulation is implemented
        # When ration formulation is in, the silos will automatically be fedout
        for silo in self.storage_options:
            if self.storage_options[silo].days_since_feedout > 365:
                self.storage_options[silo].reset_storage()
                self.available_storage[silo] = self.storage_options[silo]

    def reset_feed(self):
        """
        Description:
            Resets the accumulated data so they can be interpreted as annual sums.
            Option to reset feed storage model entirely each year.
        """

        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.NDF = 0.0
        self.CP = 0.0
        self.NPN = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

    def get_feeds_split_by_maturity(self):
        """
        Description:
            Returns the feed entries in the database which have different qualities
            based on nutrient values at harvest.

        Returns: a set-like list (no duplicates) of the entries listed in the
            table which splits feeds by quality
        """
        column = 'entry'
        dict_list = self.db_reader.query(self.feed_quality_table,
                                         distinct=True, cols=[column])
        return [result[column] for result in dict_list]

    def get_all_feed_units(self, purchased_feeds, grown_feeds):
        """
        Description:
            Constructs and returns a dictionary of where the keys are the feed IDs
            and the values are dictionaries containing the name and the units of
            the feed.

        Args:
            purchased_feeds: the list of entries (ints) of feeds that are
                purchased
            grown_feeds: the list of entries (ints) of feeds that will be grown

        Returns:
            a dictionary where the keys are the feed IDs and the values are
            dictionaries with feed information:
            - if the feed is purchased, ID is the string form of the ID
            (e.g. '2')
            - if the feed is grown, ID is the string form of the ID plus 'g'
            (e.g. '8g')
            - feed name is as it is in the user_feeds table
            - units is the string representing the units for the feed
            (e.g. 'kg')
        """
        columns = ['entry', 'feed_name', 'units']
        all_feeds = purchased_feeds + grown_feeds
        dict_list = self.db_reader.query(self.feeds_table, cols=columns,
                                         identifier='entry',
                                         desired_rows=tuple(all_feeds))

        all_feed_info = {str(result['entry']): {
            'feed_name': result['feed_name'],
            'units': result['units']
        }
            for result in dict_list}

        purchased_mapping = self.get_purchased_feed_ids(purchased_feeds)
        self.purchased_feeds = list(purchased_mapping.values())

        grown_feeds_mapping = {str(feed): str(feed) + 'g'
                               for feed in grown_feeds}

        all_feeds_mapping = purchased_mapping.copy()
        all_feeds_mapping.update(grown_feeds_mapping)

        for entry in all_feeds_mapping:
            if not entry == all_feeds_mapping[entry]:
                all_feed_info[all_feeds_mapping[entry]] = \
                    all_feed_info.pop(entry)

        return all_feed_info

    def get_purchased_feed_ids(self, entries):
        """
        Description:
            Constructs and returns a dictionary of the purchased feed IDs based on
            whether the quality of each feed can be determined at harvest.

        Args:
            entries: the purchased feed entries

        Returns:
            a dictionary where the keys are the feed entries and the keys are
            the feed IDs that can be used to find nutrient values in
            the nutrients table
        """
        purchased_feed_ids = {}
        for entry in entries:
            if entry in self.entries_split_by_maturity:
                # making the assumption that purchased feeds are at mid-maturity
                purchased_feed_ids[str(entry)] = str(entry + 2)
            else:
                purchased_feed_ids[str(entry)] = str(entry)
        return purchased_feed_ids

    def get_feed_id(self, grown_feed_entry, DM, NDF):
        """
        Description:
            First queries the database to find which nutrient must be used to find
            the quality of the feed, then uses the feed's value for that nutrient
            to find the quality by finding which range it belongs to. Returns
            the feed ID associated with that quality.

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
        column = 'differentiating_nutrient'
        dict_list = self.db_reader.query(self.feed_quality_table,
                                         distinct=True, cols=[column],
                                         identifier='entry',
                                         desired_rows=(grown_feed_entry,))
        nutrient = dict_list[0][column]

        column = 'quality_id'
        rounded_nutrient = rounded_DM if nutrient == 'DM' else rounded_NDF
        dict_list = self.db_reader.query(self.feed_quality_table,
                                         cols=[column], identifier='entry',
                                         desired_rows=(str(grown_feed_entry),),
                                         compare_val=str(rounded_nutrient),
                                         low_col='low_percent',
                                         high_col='high_percent', )

        return dict_list[0][column]

    def add_to_available_feeds(self, new_grown_feeds, DM_list, NDF_list):
        """
        Description:
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
        Description:
            Updates the dictionary of available feeds with a particular nutrient
            value.

        Args:
            feed_id: string - the ID of the feed to be modified (string should
                end in 'g' if it is a grown feed
            nutrient: the nutrient to be modified
            new_val: the new value of the nutrient
        """
        self.available_feeds[feed_id][nutrient] = new_val

    def remove_from_available_feeds(self, feeds_to_be_removed):
        """
        Description:
            Removes the IDs in feeds_to_be_removed from available_feeds.

        Args:
            feeds_to_be_removed: a list of feed IDs
        """
        for feed_id in feeds_to_be_removed:
            self.available_feeds.pop(feed_id)

    def get_nutrient_vals(self, feed_ids, is_grown):
        """
        Description:
            Constructs and returns the dictionary of nutrient values for the feeds
            represented by feed_ids.

        Args:
            feed_ids: list of feed IDs
            is_grown: boolean - true if the feeds represented by feed_ids are
                grown, false if purchased

        Returns: a dictionary where the keys are the the feed identifiers and
        the values are nutrient dictionaries
        """
        dict_list = self.db_reader.query(self.nutrient_table,
                                         identifier='feed_id',
                                         desired_rows=tuple(feed_ids))
        nutrient_vals = {}
        for dictionary in dict_list:
            feed_id = dictionary['feed_id']
            # the key in the available_feeds dictionary has a 'g' as the
            # suffix if it is a grown feed
            feed_key = str(feed_id)

            if is_grown:
                feed_key += 'g'

            nutrient_vals[feed_key] = dictionary

        return nutrient_vals
