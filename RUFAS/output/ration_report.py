################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: ration_report.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: RationReport
#-------------------------------------------------------------------------------
class RationReport(BaseReportHandler):
    '''Creates and prints to the file ration_report.txt'''

    def __init__(self, data):
        '''
        TODO: Add DocString
        '''

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.achieved_price = [None]*366
        self.feed_amounts = [None]*366
        self.milk_production_reduction = [None]*366
        #self.LP_text = ""

        # static
        self.feed_info = {}

    #---------------------------------------------------------------------------
    # Method: initialize
    #---------------------------------------------------------------------------
    def initialize(self, state):
        '''Transfers the needed data from Soil object to the report handler.'''
        feed = state.feed
        # get static data like units associated with each feed type
        # store in Feed or Animal???????
        self.feed_info = {**feed.purchased_feed, **feed.farm_feed}
        self.ration_interval = state.animal.ration_formulation_interval

    #---------------------------------------------------------------------------
    # Method: daily_update
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        '''Stores the daily values that need to be printed in the report.'''

        d = time.day
        if (d % self.ration_interval) == 1:
            animal = state.animal

            self.achieved_price[d] = animal.ration['objective']
            self.feed_amounts[d] = {feed_type: animal.ration[feed_type] for feed_type in self.feed_info.keys()}
            self.milk_production_reduction[d] = animal.ration['MP_reduction']

    #---------------------------------------------------------------------------
    # Method: annual_update
    #---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        '''Stores the yearly values that need to be printed in the report.'''
        pass

    #---------------------------------------------------------------------------
    # Method: write_annual_report
    #---------------------------------------------------------------------------
    def write_annual_report(self, y):
        '''Appends the annual report to the output file.'''

        print("printing ration report for year: " + str(y))
        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as f:
            f.write("RUFAS: Ration Formulation Report\n")
            f.write("Year {}:\n".format(y))

            for d in range(1, 366):
                if (d % self.ration_interval) == 1:
                    f.write("\tDay:{} \n".format(str(d)))
                    #f.write("\tRation Optimization Status: " + self.ration_LP_status[d])
                    f.write("\t\tAchieved Total Price: " +
                            str(self.achieved_price[d]))
                    f.write("\n\t\tMilk Production Reduction Factor: " +
                            str(self.milk_production_reduction[d]) + '\n')

                    for feed_type in self.feed_info.keys():
                        f.write("\t\t{}: {} {}".format(
                            feed_type,
                            self.feed_amounts[d][feed_type],
                            self.feed_info[feed_type]['units'])
                        )
                    f.write('\n')
    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        '''Sets all of the values in the output object to the default value.'''

        self.achieved_price = [None]*366
        self.feed_amounts = [None]*366
        self.milk_production_reduction = [None]*366
