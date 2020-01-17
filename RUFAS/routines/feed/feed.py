"""
RUFAS: Ruminant Farm Systems Model
File name: feed.py

Author(s): Kass Chupongstimun, kass_c@hotmail.com,
           Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: Main driver for the feed storage module. Calibrates storage and models
                protein degradation as well as reductions in Carbon, Nitrogen, and
                Phosphorus content during harvest, storage, and feedout.
"""

from RUFAS import util
from . import nitrogen_loss, carbon_loss, protein_degradation


def daily_feed_routine(feed, crop):
    """
    Description:
        The daily feed routine involves updating stored feed and nutrient
        content information.
    Inputs:
        crop: when multiple fields are growing crops but only one storage
                mechanism is specified, all feed goes to the same location.
                Degradations vary by crop type so this portion of the module
                is called once for each field with crop as the differentiating
                parameter.
    """

    if feed.storage:
        feed.dry_matter += crop.current_crop.yield_actual
        feed.crude_protein += crop.current_crop.yield_actual * feed.crude_protein_percent

        if crop.current_crop.yield_actual != 0:
            feed.nitrogen += crop.current_crop.yield_N
            feed.phosphorus += crop.current_crop.yield_P

            # TODO: Carbon Cycle implementation
            feed.carbon += crop.current_crop.yield_actual * feed.carbon_percent

            carbon_loss.update_all(feed)

            nitrogen_loss.update_all(feed)

            protein_degradation.update_all(feed)


def annual_feed_routine(feed, crop):
    """
    Description:
        Feed is calibrated every time there is a crop to be stored (i.e. crop != null)
    """

    feed.prev_crop_name = feed.crop_name
    feed.crop_name = crop.current_crop.crop_name

    if feed.crop_name != 'null':
        calibrate_feed(feed)


def calibrate_feed(feed):
    """
    Description:
        calibrate_feed is the implementation of KPB's feed reduction table.
        Based on the feed and storage types, reduction percentages are set for
        use in the rest of the module. If the specified feed or storage type
        are not currently implemented, an error message is printed.
    """

    if feed.crop_name == 'corn':
        feed.storage = True
        feed.crude_protein_percent = 0.08
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
        feed.crude_protein_percent = 0.22
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


class Feed:
    """
    Description:
        Sorts all feeds by the constraints set in the Linear Program of rations.py

        Object storing information about the feed storage method

        TODO: Phase out feed library
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

        self.crude_protein_percent = 0.0
        self.carbon_percent = 0

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

        # TODO: Feed library code starts here
        # The feed library contains all the types of feed described in the input
        # csv file specified for "feed_library" in the input json file.
        self.feed_library = util.Library('Inputs/feed_storage/' + data["feed_library"])

        # The available_feeds are the collection of feeds that are actually
        # available and should be used in calculations.
        self.available_feeds = {}

        # Populate available_feeds. The key to retrieve a feed type from
        # available_feeds is the name of the feed as specified in the csv
        # library. The feed_keys are specified in the input json file. They
        # may be the Name or the ID of the feed type in the csv.
        for feed_key in data["available_feeds"]:
            feed_type = self.feed_library.checkout(feed_key)
            self.available_feeds[feed_type["Name"]] = feed_type

        # Sorted so that they are in a consistent order.
        self.available_feed_names = sorted(list(self.available_feeds.keys()))

        # Sorted so that is easier to ensure that the requirements calculated
        # in ration.py are zipped with the correct nutrient.
        self.nutrient_rqmts = ['FU', 'RU', 'ME_DM', 'RDP_DM', 'RUP_DM']

    def annual_reset(self):
        """
        Description:
            TODO: No annual reset currently implemented
        """

        pass
