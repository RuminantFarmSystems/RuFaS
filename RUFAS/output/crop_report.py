################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: crop_report.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: CropReport
#-------------------------------------------------------------------------------
class CropReport(BaseReportHandler):
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
        self.LAI = [None]*366
        self.dBiomass_max = [None]*366

        # static

    #---------------------------------------------------------------------------
    # Method: get_data
    #---------------------------------------------------------------------------
    def get_data(self, state):
        '''Transfers the needed data from Crop object to the report handler.'''
        pass

    #---------------------------------------------------------------------------
    # Method: daily_update
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        '''Stores the daily values that need to be printed in the report.'''

        d = time.day
        crop = state.crop

        self.LAI[d] = crop.LAI
        self.dBiomass_max[d] = crop.dBiomass_max

    #---------------------------------------------------------------------------
    # Method: write_annual_report
    #---------------------------------------------------------------------------
    def write_annual_report(self, y):
        '''Appends the annual report to the output file.'''

        print("printing crop report for year: " + str(y))
        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as f:
            f.write("RUFAS: Crop Report\n")
            f.write("Year {}:".format(y))

            for d in range(1, 366):
                f.write("\tDay: " + str(d))
                f.write("\tLeaf Area Index: " + str(self.LAI[d]))
                f.write("\tMax Potential Biomass Change: " + str(self.dBiomass_max[d]))
                f.write('\n')

    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        '''Sets all of the values in the output object to the default value.'''

        self.LAI = [None]*366
        self.dBiomass_max = [None]*366
