################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# soil_phosphorusn.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#          Jacob Johnson
#          William Donovan
#
################################################################################

import csv

from RUFAS.output.data_analysis import data_analysis
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilPhosphorus
# Creates and prints to the file soil_nitrogen.csv
# -------------------------------------------------------------------------------
class SoilPhosphorus(BaseReportHandler):

    def __init__(self, data):

        #
        # Outputs can be added in this single place in the following format:
        # 'output_name': ['variable_name', 'unit', []],
        # 'output_name' is a user defined key that will show up in outputs/graphs.
        # avoid spaces.
        # 'variable_name' is very important. This has to be a variable defined
        # and initialized in the object. If you are interested in tracking
        # a variable not defined in the class, you need to create it there
        # first. The output handler will not work if the variable is incorrect.
        # 'unit' is user defined but will, again, show up in outputs/graphs.
        # [] is an empty list
        #

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)

        self.variables = {'year': ['time.cal_year', '', []],
                          'j_day': ['time.day', '', []],
                          'soil_runoff_DRP': ['soil.SRP_MGL', 'mgL', []],
                          'manure_runoff_DRP': ['soil.runoff_IP', 'mgL', []],
                          'fert_runoff_DRP': ['soil.runoff_IP', 'mgL', []],
                          'runoff_DIP': ['soil.T_runoff_IP', 'mgL', []],
                          'manure_runoff_DOP': ['soil.runoff_OP', 'mgL', []],
                          'manure_runoff_NH4': ['soil.runoff_NH4', 'mgL', []],
                          'PSP': ['soil.soil_layers[0].PSP', '', []],
                          'labile_p1': ['soil.soil_layers[0].labile_P', 'kg/ha', []],
                          'labile_p2': ['soil.soil_layers[1].labile_P', 'kg/ha', []],
                          'labile_p3': ['soil.soil_layers[2].labile_P', 'kg/ha', []],
                          'available_fert_P': ['soil.fert_P_available', 'kg', []],
                          'released_fert_P': ['soil.fert_P_released', 'kg', []],
                          'manure_WIP': ['soil.WIP', 'kg', []],
                          'manure_WOP': ['soil.WOP', 'kg', []],
                          'manure_SIP': ['soil.SIP', 'kg', []],
                          'manure_SOP': ['soil.SOP', 'kg', []],
                          'manure_NH4': ['soil.NH4', 'kg', []],
                          'manure_SON': ['soil.SON', 'kg', []],
                          'manure_mass': ['soil.manure_mass', 'kg', []],
                          'manure_cover': ['soil.manure_cov', 'HA', []],
                          }

    #
    # writes header names and units to the csv
    #
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

    def initialize(self, state):
        self.write_header()

    #
    # stores specified daily values. NOTE: the eval() method is limited
    # to the scope of soil variables. If a specified output is not a soil
    # variable, this will throw an error. See comment at the top of the file.
    #
    def daily_update(self, state, weather, time):
        soil = state.soil

        for variable in self.variables:
            self.variables[variable][2].append(eval(self.variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    #
    # writes stored values to the csv at the end of the year
    #
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

    #
    # clears stored values at the end of the year
    #
    def annual_flush(self):
        for variable in self.variables:
            self.variables[variable][2] = []

    def produce_data_analysis(self, is_final):
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)
