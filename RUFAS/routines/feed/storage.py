"""
RUFAS: Ruminant Farm Systems Model
File name: storage.py


Description: Main driver for the feed storage module. Calibrates storage and models
                protein degradation as well as reductions in Carbon, Nitrogen, and
                Phosphorus content during harvest, storage, and feed out.

Author(s): Chris Vankerkhove, cjv47@cornell.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

"""

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
        self.feed_key = 'null'
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
        self.animal_avg_BW = 0

        self.C_percent = 0.0
        self.DM_percent = 0.0
        self.NDF_percent = 0.0

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

    def forage_quality_assesment(self, feed):
        """
        Description:
            Updates values in the storage object relevant to the quality of
            the feed utilizing feed database functions

        Args:
            feed: an instance of class Feed
        """
        if self.feed_id in feed.entries_split_by_maturity:
            quality_id = feed.get_feed_id(self.feed_id, self.DM_percent,
                                    self.NDF_percent)
            quality_status = feed.get_feed_quality(quality_id)
            self.feed_key = str(quality_id) + 'g'
            self.forage_quality = quality_status
        else:
            self.feed_key = str(self.feed_id) + 'g'
            self.forage_quality = 'null'

    def store_crop(self, feed, crop):
        """
        Description:
            Helper method for "storing" the specified crop
            Updates mineral components and losses as a crop is stored.
            "pseudocode_feed" F.1.1

        Args:
            crop: the crop to be stored, an instance of class Crop
        """
        print("Store that mfucjsahucsa!!!!!!!!!!!!!!")
        print(crop.raw_id)
        print(crop.yield_actual)
        if self.storage:
            if self.DM == 0:
                # forage to be fed out 30 days after harvest for new yield
                self.days_since_feedout = -30
            self.feed_id = crop.raw_id
            self.DM += crop.DM_yield
            self.NDF += crop.NDF_yield
            self.N += crop.N_yield
            self.P += crop.P_yield
            self.DM_percent = crop.DM_yield / crop.yield_actual
            self.NDF_percent = crop.NDF_yield / crop.yield_actual
            # TODO: no Carbon Cycle currently implemented
            self.C += crop.yield_actual * self.C_percent

            # "pseudocode_feed" F.1.2
            self.CP += 6.25 * self.N / self.DM

            # Reset harvest quality for the crop
            crop.harvest_quality = ''

        if self not in feed.new_forages:
            feed.new_forages.append(self)

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
