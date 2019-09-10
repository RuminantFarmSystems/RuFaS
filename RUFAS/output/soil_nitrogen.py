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

    def __init__(self, data, field_name):

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
        # Sets active, report_name, file_name using data
        #
        self.field_name = field_name
        self.set_properties(data, self.field_name)
        self.fieldNames = None

        self.variables = {'year': ['time.cal_year', '', []],
                          'j_day': ['time.day', '', []],
                          'NO3_L1': ['soil.soil_layers[0].NO3', 'kg', []],
                          'NO3_L2': ['soil.soil_layers[1].NO3', 'kg', []],
                          'NO3_L3': ['soil.soil_layers[2].NO3', 'kg', []],
                          'NH4_L1': ['soil.soil_layers[0].NH4', 'kg', []],
                          'NH4_L2': ['soil.soil_layers[1].NH4', 'kg', []],
                          'NH4_L3': ['soil.soil_layers[2].NH4', 'kg', []],
                          'ActiveN_L1': ['soil.soil_layers[0].activeN', 'kg', []],
                          'ActiveN_L2': ['soil.soil_layers[1].activeN', 'kg', []],
                          'ActiveN_L3': ['soil.soil_layers[2].activeN', 'kg', []],
                          'StableN_L1': ['soil.soil_layers[0].stableN', 'kg', []],
                          'StableN_L2': ['soil.soil_layers[1].stableN', 'kg', []],
                          'StableN_L3': ['soil.soil_layers[2].stableN', 'kg', []],
                          'FreshN': ['soil.topLayerFreshN', 'kg', []],
                          'Nitri_L1': ['soil.soil_layers[0].nitrification', 'kg/ha', []],
                          'Nitri_L2': ['soil.soil_layers[1].nitrification', 'kg/ha', []],
                          'Nitri_L3': ['soil.soil_layers[2].nitrification', 'kg/ha', []],
                          'Volati_L1': ['soil.soil_layers[0].volatilization', 'kg/ha', []],
                          'Volati_L2': ['soil.soil_layers[1].volatilization', 'kg/ha', []],
                          'Volati_L3': ['soil.soil_layers[2].volatilization', 'kg/ha', []],
                          'Denitri_L1': ['soil.soil_layers[0].denitrification', 'kg/ha', []],
                          'Denitri_L2': ['soil.soil_layers[1].denitrification', 'kg/ha', []],
                          'Denitri_L3': ['soil.soil_layers[2].denitrification', 'kg/ha', []],
                          'Tot_Nitri_Vol_L1': ['soil.soil_layers[0].totNitriVolatil', 'kg/ha', []],
                          'Tot_Nitri_Vol_L2': ['soil.soil_layers[1].totNitriVolatil', 'kg/ha', []],
                          'Tot_Nitri_Vol_L3': ['soil.soil_layers[2].totNitriVolatil', 'kg/ha', []],
                          'N_trans_L1': ['soil.soil_layers[0].nTrans', 'kg', []],
                          'N_trans_L2': ['soil.soil_layers[1].nTrans', 'kg', []],
                          'N_trans_L3': ['soil.soil_layers[2].nTrans', 'kg', []],
                          'NO3_runoff': ['soil.NO3_runoff', 'kg/ha', []],
                          'NH4_runoff': ['soil.NH4_runoff', 'kg/ha', []],
                          'NO3_perc_L1': ['soil.soil_layers[0].NO3_perc', 'kg/ha', []],
                          'NO3_perc_L2': ['soil.soil_layers[1].NO3_perc', 'kg/ha', []],
                          'NO3_perc_L3': ['soil.soil_layers[2].NO3_perc', 'kg/ha', []],
                          'NH4_perc_L1': ['soil.soil_layers[0].NH4_perc', 'kg/ha', []],
                          'NH4_perc_L2': ['soil.soil_layers[1].NH4_perc', 'kg/ha', []],
                          'NH4_perc_L3': ['soil.soil_layers[2].NH4_perc', 'kg/ha', []],
                          'active_perc_L1': ['soil.soil_layers[0].active_perc', 'kg/ha', []],
                          'active_perc_L2': ['soil.soil_layers[1].active_perc', 'kg/ha', []],
                          'active_perc_L3': ['soil.soil_layers[2].active_perc', 'kg/ha', []],
                          'NH4_erosion': ['soil.NH4_erosion', 'kg/ha', []],
                          'activeN_erosion': ['soil.activeN_erosion', 'kg/ha', []],
                          'stableN_erosion': ['soil.stableN_erosion', 'kg/ha', []],
                          'freshN_erosion': ['soil.freshN_erosion', 'kg/ha', []]
                          }

    #
    # writes header names and units to the csv
    #
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

    def initialize(self, state):

        self.write_header()

    #
    # stores specified daily values. NOTE: the eval() method is limited
    # to the scope of soil variables. If a specified output is not a soil
    # variable, this will throw an error. See comment at the top of the file.
    #
    def daily_update(self, field, weather, time):

        soil = field.soil

        for variable in self.variables:
            self.variables[variable][2].append(eval(self.variables[variable][0], globals(), locals()))

    def annual_update(self, field, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    #
    # writes stored values to the csv at the end of the year
    #
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

    #
    # clears stored values at the end of the year
    #
    def annual_flush(self):
        for variable in self.variables:
            self.variables[variable][2] = []

    def produce_data_analysis(self, is_final):
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)
