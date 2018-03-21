################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# ration_report.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from pathlib import path
from RUFAS.output.output_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: RationReport
#        Creates and prints to the file ration_report.txt
#-------------------------------------------------------------------------------
class RationReport(BaseReportHandler):
    
    def __init__(self, data):
             
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
    # Function: get_data
    #           Transfers the needed data from Soil object to the report handler
    #---------------------------------------------------------------------------
    def get_data(self):
        
        # get static data like units associated with each feed type
        # store in Feed or Animal???????
        # feed_info = feed.feed_info
        pass

    #---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # csv file
    #--------------------------------------------------------------------------- 
    def daily_update(self, animal, time):
        
        pass
 
    #---------------------------------------------------------------------------
    # Function: write_annual_report
    #           Appends the annual report to the output file
    # Soil Summary is a cvsfile
    #---------------------------------------------------------------------------
    def write_annual_report(self):
        
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
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):

        self.achieved_price = [None]
        self.feed_amounts = [None]
        self.ration_LP_status = [None]
        #self.LP_text = ""

        self.julianDay = 0
        self.year = 0