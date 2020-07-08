################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: soil_carbon.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################

import csv
from pathlib import Path
from RUFAS.output.graphics import daily_graphics, annual_graphics
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilCarbon
# Creates and prints to the file soil_carbon.csv
# -------------------------------------------------------------------------------
class SoilCarbon(BaseReportHandler):

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
        # Sets produce_csv, report_name, f_name using data
        #
        self.set_properties(data)

        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                'total_carbon_L1': ['soil.soil_layers[0].total_carbon', 'kg/ha', []],
                                'total_carbon_L2': ['soil.soil_layers[1].total_carbon', 'kg/ha', []],
                                'total_carbon_L3': ['soil.soil_layers[2].total_carbon', 'kg/ha', []],
                                'active_L1': ['soil.soil_layers[0].carbon_active', 'kg/ha', []],
                                'active_L2': ['soil.soil_layers[1].carbon_active', 'kg/ha', []],
                                'active_L3': ['soil.soil_layers[2].carbon_active', 'kg/ha', []],
                                'slow_L1': ['soil.soil_layers[0].carbon_slow', 'kg/ha', []],
                                'slow_L2': ['soil.soil_layers[1].carbon_slow', 'kg/ha', []],
                                'slow_L3': ['soil.soil_layers[2].carbon_slow', 'kg/ha', []],
                                'passive_L1': ['soil.soil_layers[0].carbon_passive', 'kg/ha', []],
                                'passive_L2': ['soil.soil_layers[1].carbon_passive', 'kg/ha', []],
                                'passive_L3': ['soil.soil_layers[2].carbon_passive', 'kg/ha', []],
                                'metabolic_AG_L1': ['soil.soil_layers[0].metabolic_AG', 'kg/ha', []],
                                'metabolic_AG_L2': ['soil.soil_layers[1].metabolic_AG', 'kg/ha', []],
                                'metabolic_AG_L3': ['soil.soil_layers[2].metabolic_AG', 'kg/ha', []],
                                'metabolic_BG_L1': ['soil.soil_layers[0].metabolic_BG', 'kg/ha', []],
                                'metabolic_BG_L2': ['soil.soil_layers[1].metabolic_BG', 'kg/ha', []],
                                'metabolic_BG_L3': ['soil.soil_layers[2].metabolic_BG', 'kg/ha', []],
                                'structural_AG_L1': ['soil.soil_layers[0].structural_AG', 'kg/ha', []],
                                'structural_AG_L2': ['soil.soil_layers[1].structural_AG', 'kg/ha', []],
                                'structural_AG_L3': ['soil.soil_layers[2].structural_AG', 'kg/ha', []],
                                'structural_BG_L1': ['soil.soil_layers[0].structural_BG', 'kg/ha', []],
                                'structural_BG_L2': ['soil.soil_layers[1].structural_BG', 'kg/ha', []],
                                'structural_BG_L3': ['soil.soil_layers[2].structural_BG', 'kg/ha', []],

                                }

        self.annual_variables = {'year': ['time.cal_year', '', 0]
                                 }

    #
    # writes header names and units to the csv
    #
    def write_headers(self, output_csv, variables):

        mode = 'a+' if output_csv.exists() else 'w+'

        with output_csv.open(mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=variables.keys(),
                                    lineterminator='\n')

            writer.writeheader()

            units = {}
            for variable in variables:
                units[variable] = variables[variable][1]

            writer.writerow(units)

    def initialize(self, state):
        self.write_headers(self.get_fPath(), self.daily_variables)
        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")
        self.write_headers(annual_path, self.annual_variables)

    #
    # stores specified daily values. NOTE: the eval() method is limited
    # to the scope of variables. If a specified output is not a soil
    # variable, this will throw an error. See comment at the top of the file.
    #
    def daily_update(self, state, weather, time):
        soil = state.soil

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        soil = state.soil

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())

    #
    # writes stored values to the csv at the end of the year
    #
    def write_annual_report(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            # Write data day by day
            writer = csv.DictWriter(csvfile, fieldnames=self.daily_variables.keys(),
                                    lineterminator='\n')

            for day in range(len(self.daily_variables['j_day'][2])):
                row = {}
                for variable in self.daily_variables:
                    row[variable] = self.daily_variables[variable][2][day]
                writer.writerow(row)

        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")

        mode = 'a+' if annual_path.exists() else 'w+'

        with annual_path.open(mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.annual_variables.keys(),
                                    lineterminator='\n')
            row = {}
            for variable in self.annual_variables:
                row[variable] = self.annual_variables[variable][2]
            writer.writerow(row)

    #
    # clears stored values at the end of the year
    #
    def annual_flush(self):
        for variable in self.daily_variables:
            self.daily_variables[variable][2] = []

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = 0

    def produce_report_graphics(self, is_final):
        annual_file_name = str(self.file_name).split('.')[0] + "_annual.csv"
        annual_graphics(annual_file_name, self.display_graphics, self.produce_graphics, is_final)
        daily_graphics(self.file_name, self.display_graphics, self.produce_graphics, is_final)
