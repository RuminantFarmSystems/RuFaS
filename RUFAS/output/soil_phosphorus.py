################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# soil_phosphorusn.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import csv
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: SoilPhosphorus
# Creates and prints to the file soil_nitrogen.csv
#-------------------------------------------------------------------------------
class SoilPhosphorus(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)
        self.fieldNames = None

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.year = []
        self.julianDay = []
        self.numSoilLayers = 0
        self.layersActiveP = []
        self.layersStableP = []


    #---------------------------------------------------------------------------
    # Function: get_header
    #           Writes the header (title and units) in the csvfile
    #---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'ActiveP/L1',
                          'ActiveP/L2', 'ActiveP/L3', 'StableP/L1',
                          'StableP/L2', 'StableP/L3']

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator = '\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': ''}
            for fieldname in fieldnames:
                if (fieldname.startswith("ActiveP/") or 
                    fieldname.startswith("StableP/")):
                    units[fieldname] = 'kg/ha'
            writer.writerow(units)

    #---------------------------------------------------------------------------
    # Function: get_data
    #           Transfers the needed data from Soil object to the report handler
    #---------------------------------------------------------------------------
    def get_data(self, state):

        soil = state.soil

        # initialize number of layer in soil summary report handler to get output
        # data pertaining to each soil layer
        # Initializes the output arrays for current soil water, Esoil, and
        # percolation for each soil layer
        self.numSoilLayers = len(soil.listOfSoilLayers)
        
        for _ in range (0, self.numSoilLayers):
            self.layersActiveP.append([])
            self.layersStableP.append([])


    #---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # csv file
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):

        soil = state.soil

        self.year.append(time.cal_year)
        self.julianDay.append(time.day)
        
        for x in range(0, len(soil.listOfSoilLayers)):
            self.layersActiveP[x].append(soil.listOfSoilLayers[x].activeP)
            self.layersStableP[x].append(soil.listOfSoilLayers[x].stableP)
            
    #---------------------------------------------------------------------------
    # Function: write_annual_report
    #           Appends the annual report to the output file
    # Soil Summary is a cvsfile
    #---------------------------------------------------------------------------
    def write_annual_report(self, y):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

        # Write data day by day
            for x in range(0, len(self.julianDay)):
                dailySoilPhosphorusData = {
                    'Year': str(self.year[x]),
                    'Julian Day': self.julianDay[x]}
                
                for y in range(0, self.numSoilLayers):
                    dailySoilPhosphorusData["ActiveP/L" + str(y+1)] = str(
                        round(self.layersActiveP[y][x], 3))
                    
                    dailySoilPhosphorusData["StableP/L" + str(y+1)] = str(
                        round(self.layersStableP[y][x], 3))                

                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator = '\n')
                writer.writerow(dailySoilPhosphorusData)

    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):

        self.year = []
        self.julianDay = []
        
        for x in range(0, self.numSoilLayers):
            self.layersActiveP[x] = []
            self.layersStableP[x] = []