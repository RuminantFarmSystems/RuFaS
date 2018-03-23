################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: ration_report.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import path
from RUFAS.output.output_handler import BaseReportHandler

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
        self.achieved_price = [None]
        self.feed_amounts = [None]
        self.ration_LP_status = [None]
        #self.LP_text = ""

        self.julianDay = 0
        self.year = 0

        # static
        self.feed_info = {}

    #---------------------------------------------------------------------------
    # Method: get_data
    #---------------------------------------------------------------------------
    def get_data(self):
        '''Transfers the needed data from Soil object to the report handler.'''
        
        # get static data like units associated with each feed type
        # store in Feed or Animal???????
        # feed_info = feed.feed_info
        pass

    #---------------------------------------------------------------------------
    # Method: daily_update
    #--------------------------------------------------------------------------- 
    def daily_update(self, animal, time):
        '''Stores the daily values that need to be printed in the report.'''
        
        pass
 
    #---------------------------------------------------------------------------
    # Method: write_annual_report
    #---------------------------------------------------------------------------
    def write_annual_report(self):
        '''Appends the annual report to the output file.'''
        
        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath.open() as f:
            f.write("RUFAS: Ration Formulation Report\n")
            f.write("Year {}:".format(self.year))
            
            for d in range(1, len(self.julianDay)+1):
                f.write("\tDay: " str(self.julianDay[d]))
                f.write("\tRation Optimization Status: " + self.ration_LP_status[d])
                f.write("\tAchieved Total Price: " + str(self.achieved_price[d]))

                for feed in feed_info.keys():
                    f.write("\t{}: {} {}".format(feed,
                                                 self.feed_amounts[d][feed][amount],
                                                 self.feed_info[feed]['units'])
                            )
            f.write('\n')                    
    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        '''Sets all of the values in the output object to the default value.'''

        self.achieved_price = [None]
        self.feed_amounts = [None]
        self.ration_LP_status = [None]
        #self.LP_text = ""

        self.julianDay = 0
        self.year = 0