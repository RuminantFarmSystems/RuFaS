################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# Output.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#          William Donovan
#
################################################################################

import csv
from RUFAS.output.report_handler import BaseReportHandler
from RUFAS.output.data_analysis import data_analysis


# -------------------------------------------------------------------------------
# Class: SoilSummary
# Creates and prints to the file soil_summary.csv
# -------------------------------------------------------------------------------
class SoilSummary(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)

        self.variables = {'year': ['time.cal_year', '', []],
                          'j_day': ['time.day', '', []],
                          'precip': ['weather.rainfall[time.year - 1][time.day - 1]', 'mm', []],
                          'runoff': ['soil.runoff', 'mm', []],
                          'ET_max': ['soil.ET_max', 'mm d^-1', []],
                          'ET_act': ['soil.ET_act', 'mm H20', []],
                          'trans_max': ['soil.trans_max', 'mm H20', []],
                          'evap_max': ['soil.evap_max', 'mm H20', []],
                          'surface_temp': ['soil.Tsurf', 'C', []],
                          'sediment_yield': ['soil.sedimentYield', 'metric tons', []],
                          'residue': ['soil.residue', 'kg/ha', []],
                          'trans_act_L1': ['soil.listOfSoilLayers[0].trans_act', 'mm H20', []],
                          'trans_act_L2': ['soil.listOfSoilLayers[1].trans_act', 'mm H20', []],
                          'trans_act_L3': ['soil.listOfSoilLayers[2].trans_act', 'mm H20', []],
                          'soil_water_L1': ['soil.listOfSoilLayers[0].currentSoilWaterMM', 'mm', []],
                          'soil_water_L2': ['soil.listOfSoilLayers[1].currentSoilWaterMM', 'mm', []],
                          'soil_water_L3': ['soil.listOfSoilLayers[2].currentSoilWaterMM', 'mm', []],
                          'evap_L1': ['soil.listOfSoilLayers[0].layer_evap', 'mm H20', []],
                          'evap_L2': ['soil.listOfSoilLayers[1].layer_evap', 'mm H20', []],
                          'evap_L3': ['soil.listOfSoilLayers[2].layer_evap', 'mm H20', []],
                          'perc_L1': ['soil.listOfSoilLayers[0].perc', 'mm H20', []],
                          'perc_L2': ['soil.listOfSoilLayers[1].perc', 'mm H20', []],
                          'perc_L3': ['soil.listOfSoilLayers[2].perc', 'mm H20', []],
                          'temperature_L1': ['soil.listOfSoilLayers[0].temperature', 'C', []],
                          'temperature_L2': ['soil.listOfSoilLayers[1].temperature', 'C', []],
                          'temperature_L3': ['soil.listOfSoilLayers[2].temperature', 'C', []],
                          }

    # ---------------------------------------------------------------------------
    # Function: write_header
    #           Writes the header (title and units) in the csvfile
    # ---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.variables.keys(),
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

        with self.get_fPath().open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.variables.keys(),
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

