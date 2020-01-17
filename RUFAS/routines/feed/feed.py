################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: feed.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com,
           Andy Achenreiner, achenreiner@wisc.edu
"""
################################################################################
from RUFAS import util
# -------------------------------------------------------------------------------
# Class: Feed
# -------------------------------------------------------------------------------
class Feed():
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
        self.feed_library = util.LibraryDatabase(data["feed_library"])

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

        NH3 = {}
        unavail_prot = {}

        # Loop over types of feed
        '''
        for feed_name in self.available_feed_names:

            CP = self.available_feeds[feed_name]['CP']
            ICP = self.available_feeds[feed_name]['ICP']

            # Use rumen degradable, total, and indigestible CP to estimate degradable and undegradable CP
            NH3[feed_name] = CP * self.available_feeds[feed_name]['RDP']

            if self.available_feeds[feed_name]['conc'] == "conc":
                unavail_prot[feed_name] = 0.4 * ICP
            else: # feed[feed_name]['conc'] == "rough"
                unavail_prot[feed_name] = 0.7 * ICP

            self.available_feeds[feed_name]['RDP'] = NH3[feed_name] + 0.15 * CP

            self.available_feeds[feed_name]['RUP'] = 0.87 * (CP - NH3[feed_name] -
                                     (unavail_prot[feed_name] * CP))
        '''

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
