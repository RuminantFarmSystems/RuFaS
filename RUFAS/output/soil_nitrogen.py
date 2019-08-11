################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# soil_nitrogen.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#          William Donovan
#
################################################################################

import csv

from RUFAS.output.data_analysis import data_analysis
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilNitrogen
# Creates and prints to the file soil_nitrogen.csv
# -------------------------------------------------------------------------------
class SoilNitrogen(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, file_name using data
        #
        self.set_properties(data)
        self.fieldNames = None

        self.variables = {'year': ['time.cal_year', '', []],
                          'j_day': ['time.day', '', []],
                          'NO3_L1': ['soil.listOfSoilLayers[0].NO3', 'kg', []],
                          'NO3_L2': ['soil.listOfSoilLayers[1].NO3', 'kg', []],
                          'NO3_L3': ['soil.listOfSoilLayers[2].NO3', 'kg', []],
                          'NH4_L1': ['soil.listOfSoilLayers[0].NH4', 'kg', []],
                          'NH4_L2': ['soil.listOfSoilLayers[1].NH4', 'kg', []],
                          'NH4_L3': ['soil.listOfSoilLayers[2].NH4', 'kg', []],
                          'ActiveN_L1': ['soil.listOfSoilLayers[0].activeN', 'kg', []],
                          'ActiveN_L2': ['soil.listOfSoilLayers[1].activeN', 'kg', []],
                          'ActiveN_L3': ['soil.listOfSoilLayers[2].activeN', 'kg', []],
                          'StableN_L1': ['soil.listOfSoilLayers[0].stableN', 'kg', []],
                          'StableN_L2': ['soil.listOfSoilLayers[1].stableN', 'kg', []],
                          'StableN_L3': ['soil.listOfSoilLayers[2].stableN', 'kg', []],
                          'FreshN': ['soil.topLayerFreshN', 'kg', []],
                          'Nitri_L1': ['soil.listOfSoilLayers[0].nitrification', 'kg/ha', []],
                          'Nitri_L2': ['soil.listOfSoilLayers[1].nitrification', 'kg/ha', []],
                          'Nitri_L3': ['soil.listOfSoilLayers[2].nitrification', 'kg/ha', []],
                          'Volati_L1': ['soil.listOfSoilLayers[0].volatilization', 'kg/ha', []],
                          'Volati_L2': ['soil.listOfSoilLayers[1].volatilization', 'kg/ha', []],
                          'Volati_L3': ['soil.listOfSoilLayers[2].volatilization', 'kg/ha', []],
                          'Denitri_L1': ['soil.listOfSoilLayers[0].denitrification', 'kg/ha', []],
                          'Denitri_L2': ['soil.listOfSoilLayers[1].denitrification', 'kg/ha', []],
                          'Denitri_L3': ['soil.listOfSoilLayers[2].denitrification', 'kg/ha', []],
                          'Tot_Nitri_Vol_L1': ['soil.listOfSoilLayers[0].totNitriVolatil', 'kg/ha', []],
                          'Tot_Nitri_Vol_L2': ['soil.listOfSoilLayers[1].totNitriVolatil', 'kg/ha', []],
                          'Tot_Nitri_Vol_L3': ['soil.listOfSoilLayers[2].totNitriVolatil', 'kg/ha', []],
                          'N_trans_L1': ['soil.listOfSoilLayers[0].nTrans', 'kg', []],
                          'N_trans_L2': ['soil.listOfSoilLayers[1].nTrans', 'kg', []],
                          'N_trans_L3': ['soil.listOfSoilLayers[2].nTrans', 'kg', []],
                          'NO3_runoff': ['soil.NO3_runoff', 'kg', []],
                          'NH4_runoff': ['soil.NH4_runoff', 'kg', []],
                          'NO3_perc_L1': ['soil.listOfSoilLayers[0].NO3_perc', 'kg', []],
                          'NO3_perc_L2': ['soil.listOfSoilLayers[1].NO3_perc', 'kg', []],
                          'NO3_perc_L3': ['soil.listOfSoilLayers[2].NO3_perc', 'kg', []],
                          'NH4_perc_L1': ['soil.listOfSoilLayers[0].NH4_perc', 'kg', []],
                          'NH4_perc_L2': ['soil.listOfSoilLayers[1].NH4_perc', 'kg', []],
                          'NH4_perc_L3': ['soil.listOfSoilLayers[2].NH4_perc', 'kg', []],
                          'active_perc_L1': ['soil.listOfSoilLayers[0].active_perc', 'kg', []],
                          'active_perc_L2': ['soil.listOfSoilLayers[1].active_perc', 'kg', []],
                          'active_perc_L3': ['soil.listOfSoilLayers[2].active_perc', 'kg', []]
                          }

    # ---------------------------------------------------------------------------
    # Function: get_header
    #           Writes the header (title and units) in the csvfile
    # ---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.variables.keys(),
                                    lineterminator='\n')
            writer.writeheader()

            units = {}
            for variable in self.variables:
                units[variable] = self.variables[variable][1]

            writer.writerow(units)

    # ---------------------------------------------------------------------------
    # Function: initialize
    #           Transfers the needed data from Soil object to the report handler
    # ---------------------------------------------------------------------------
    def initialize(self, state):

        self.write_header()

    # ---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # csv file
    # ---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):

        soil = state.soil

        for variable in self.variables:
            self.variables[variable][2].append(eval(self.variables[variable][0], globals(), locals()))

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    # ---------------------------------------------------------------------------
    # Function: write_annual_report
    #           Appends the annual report to the output file
    # Soil Summary is a cvsfile
    # ---------------------------------------------------------------------------
    def write_annual_report(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.variables.keys(),
                                    lineterminator='\n')

            for day in range(len(self.variables['j_day'][2])):
                row = {}
                for variable in self.variables:
                    row[variable] = self.variables[variable][2][day]
                writer.writerow(row)

    # ---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    # ---------------------------------------------------------------------------
    def annual_flush(self):
        for variable in self.variables:
            self.variables[variable][2] = []

    def produce_data_analysis(self, is_final):
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)
