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

        self.soil_runoff_DRP = []
        self.manure_runoff_DRP = []
        self.fert_runoff_DRP = []
        self.runoff_DIP = []
        self.manure_runoff_DOP = []
        self.manure_runoff_NH4 = []
        self.PSP = []
        self.labile_p1 = []
        self.labile_p2 = []
        self.labile_p3 = []
        self.available_fert_P = []
        self.released_fert_P = []
        self.manure_WIP = []
        self.manure_WOP = []
        self.manure_SIP = []
        self.manure_SOP = []
        self.manure_NH4 = []
        self.manure_SON = []
        self.manure_mass = []
        self.manure_cover = []

    #---------------------------------------------------------------------------
    # Function: get_header
    #           Writes the header (title and units) in the csvfile
    #---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'soil_runoff_DRP',
                          'manure_runoff_DRP', 'fert_runoff_DRP', 'runoff_DIP',
                          'manure_runoff_DOP', 'manure_runoff_NH4', 'PSP',
                          'Labile_P1', 'Labile_P2', 'Labile_P3', 'Available_Fert_P',
                          'Released_Fert_P', 'manure_WIP', 'manure_WOP', 'manure_SIP',
                          'manure_SOP', 'manure_NH4', 'manure_SON', 'manure_mass',
                          'manure_cover']

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator='\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '', 'soil_runoff_DRP': 'mgL',
                     'manure_runoff_DRP': 'mgL', 'fert_runoff_DRP': 'mgL',
                     'runoff_DIP': 'mgL', 'manure_runoff_DOP': 'mgL',
                     'manure_runoff_NH4': 'mgL', 'PSP': '', 'Labile_P1': 'kg/ha',
                     'Labile_P2': 'kg/ha', 'Labile_P3': 'kg/ha', 'Available_Fert_P': 'kg',
                     'Released_Fert_P': 'kg', 'manure_WIP': 'kg', 'manure_WOP': 'kg',
                     'manure_SIP': 'kg', 'manure_SOP': 'kg', 'manure_NH4': 'kg',
                     'manure_SON': 'kg', 'manure_mass': 'kg', 'manure_cover': 'HA'}
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

        # TODO: still needs to be implemented

        self.soil_runoff_DRP.append()
        self.manure_runoff_DRP.append()
        self.fert_runoff_DRP.append()
        self.runoff_DIP.append()
        self.manure_runoff_DOP.append()
        self.manure_runoff_NH4.append()
        self.PSP.append()
        self.labile_p1.append()
        self.labile_p2.append()
        self.labile_p3.append()
        self.available_fert_P.append()
        self.released_fert_P.append()
        self.manure_WIP.append()
        self.manure_WOP.append()
        self.manure_SIP.append()
        self.manure_SOP.append()
        self.manure_NH4.append()
        self.manure_SON.append()
        self.manure_mass.append()
        self.manure_cover.append()

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
                    'Julian Day': self.julianDay[x],
                    'soil_runoff_DRP': self.soil_runoff_DRP[x],
                    'manure_runoff_DRP': self.manure_runoff_DRP[x],
                    'fert_runoff_DRP': self.fert_runoff_DRP[x],
                    'runoff_DIP': self.runoff_DIP[x],
                    'manure_runoff_DOP': self.manure_runoff_DOP[x],
                    'manure_runoff_NH4': self.manure_runoff_NH4[x],
                    'PSP': self.PSP[x],
                    'Labile_P1': self.labile_p1[x],
                    'Labile_P2': self.labile_p2[x],
                    'Labile_P3': self.labile_p3[x],
                    'Available_Fert_P': self.available_fert_P[x],
                    'Released_Fert_P': self.released_fert_P[x],
                    'manure_WIP': self.manure_WIP[x],
                    'manure_WOP': self.manure_WOP[x],
                    'manure_SIP': self.manure_SIP[x],
                    'manure_SOP': self.manure_SOP[x],
                    'manure_NH4': self.manure_NH4[x],
                    'manure_SON': self.manure_SON[x],
                    'manure_mass': self.manure_mass[x],
                    'manure_cover': self.manure_cover[x]
                }

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

        self.year = []
        self.julianDay = []

        self.soil_runoff_DRP = []
        self.manure_runoff_DRP = []
        self.fert_runoff_DRP = []
        self.runoff_DIP = []
        self.manure_runoff_DOP = []
        self.manure_runoff_NH4 = []
        self.PSP = []
        self.labile_p1 = []
        self.labile_p2 = []
        self.labile_p3 = []
        self.available_fert_P = []
        self.released_fert_P = []
        self.manure_WIP = []
        self.manure_WOP = []
        self.manure_SIP = []
        self.manure_SOP = []
        self.manure_NH4 = []
        self.manure_SON = []
        self.manure_mass = []
        self.manure_cover = []