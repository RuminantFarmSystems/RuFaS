################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: feed.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

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

    #***************************************************************************
    # WARNING: EXTREMELY MESSY CODE AND BAD INFORMATION ARRANGEMENT BELOW
    #   I'M SORRY IF YOU HAVE TO TRY TO READ THIS
    #   WILL REFACTOR WHEN I HAVE TIME
    #   - Kass C.
    #***************************************************************************

        self.purchased_feed = data['purchased_feed']
        self.farm_feed = data['farm_feed']

        # merge feed from farm and purchased
        self.all_feed = {**self.farm_feed, **self.purchased_feed}

        self.feed_nutrition = { 'FI': {}, 'RV': {}, 'NE': {}, 'RDP': {}, 'RUP': {}}

        # RDP -> Rumen degradable protein
        # NE --> Net Energy
        # CP --> Crude Protein
        #

        NH3 = {}
        unavail_prot = {}

        # Loop over types of feed
        for feed_type in self.all_feed.keys():
            #set FI, rumen volume, and MEIt eMEIrgy
            self.feed_nutrition['FI'][feed_type] = self.all_feed[feed_type]['nutrition']['FI']
            self.feed_nutrition['RV'][feed_type] = self.all_feed[feed_type]['nutrition']['RV']
            self.feed_nutrition['NE'][feed_type] = self.all_feed[feed_type]['nutrition']['NE']

            CP = self.all_feed[feed_type]['nutrition']['CP']
            ICP = self.all_feed[feed_type]['nutrition']['ICP']

            # Use rumen degradable, total, and indigestible CP to estimate degradable and undegradable CP
            NH3[feed_type] = CP * self.all_feed[feed_type]['nutrition']['RDP']

            if self.all_feed[feed_type]['nutrition']['conc'] == "conc":
                unavail_prot[feed_type] = 0.4 * ICP
            else: # feed[feed_type]['conc'] == "rough"
                unavail_prot[feed_type] = 0.7 * ICP

            self.feed_nutrition['RDP'][feed_type] = NH3[feed_type] + 0.15 * CP
            self.feed_nutrition['RUP'][feed_type] = 0.87 * (CP - NH3[feed_type] -
                                     (unavail_prot[feed_type] * CP))

    #---------------------------------------------------------------------------
    # Method: annual_reset
    #---------------------------------------------------------------------------
    def annual_reset(self):
        '''
        TODO: Add DocString
        '''
        pass
