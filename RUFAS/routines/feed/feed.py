################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: feed.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com,
           Andy Achenreiner, achenreiner@wisc.edu
'''
################################################################################
from RUFAS import util
#-------------------------------------------------------------------------------
# Class: Feed
#-------------------------------------------------------------------------------
class Feed():
    '''
    TODO: Add DocString
    '''

    def __init__(self, data):
        '''
        TODO: Add DocString
        '''

        self.feed_library = util.Library(data["feed_library"])

        self.available_feeds = {}
        for feed_key in data["available_feeds"]:
            feed_type = self.feed_library.checkout(feed_key)
            self.available_feeds[feed_type["Name"]] = feed_type

        self.available_feed_names = sorted(list(self.available_feeds.keys()))

        self.nutrients_in_LP = sorted(['FI', 'RV', 'NE', 'RDP', 'RUP'])

        # RDP -> Rumen degradable protein
        # NE --> Net Energy
        # CP --> Crude Protein
        #

        NH3 = {}
        unavail_prot = {}

        # Loop over types of feed
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


    #---------------------------------------------------------------------------
    # Method: annual_reset
    #---------------------------------------------------------------------------
    def annual_reset(self):
        '''
        TODO: Add DocString
        '''
        pass
