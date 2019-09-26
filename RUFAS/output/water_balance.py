################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# water_balance.py
#
# Authors: Jacob Johnson, jacob8399@gmail.com
#          William Donovan, wmdonovan@wisc.edu
#
################################################################################

import csv
from pathlib import Path

from RUFAS.output.graphics import daily_graphics, annual_water_balance_graphic, annual_graphics
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilSummary
# Creates and prints to the file water_balance.csv
# -------------------------------------------------------------------------------
class WaterBalance(BaseReportHandler):

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

        #
        # Daily Outputs
        #
        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                'change in sw': ['soil.delta_SW', 'mmH2O', []],
                                'runoff': ['soil.runoff', 'mmH2O', []],
                                'evaporation': ['soil.evap_sum', 'mmH2O', []],
                                'transpiration': ['soil.trans_sum', 'mmH2O', []],
                                'drainage': ['soil.drainage', 'mmH2O', []],
                                'precipitation': ['soil.p_act', 'mmH2O', []],
                                'calculated water': ['soil.p_calc', 'mmH2O', []],
                                'difference': ['soil.water_balance_difference', 'mmH2O', []]}

        #
        # Annual outputs
        #
        self.annual_variables = {'year': ['time.cal_year', '', 0],
                                 'delta_SW': ['round(soil.delta_SW_annual, 3)', 'mmH2O', 0],
                                 'runoff': ['round(soil.runoff_annual, 3)', 'mmH2O', 0],
                                 'evaporation': ['round(soil.evap_annual, 3)', 'mmH2O', 0],
                                 'transpiration': ['round(soil.trans_annual, 3)', 'mmH2O', 0],
                                 'drainage': ['round(soil.drainage_annual, 3)', 'mmH2O', 0],
                                 # new variables need to be added below here in the gap

                                 # new variables need to be added above here
                                 'precipitation': ['round(soil.p_act_annual, 3)', 'mmH2O', 0],
                                 'calculated water': ['round(soil.p_calc_annual, 3)', 'mmH2O', 0],
                                 'difference': ['round(soil.annual_water_balance_difference, 3)', 'mmH2O', 0]}

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
    def daily_update(self, field, weather, time):

        soil = field.soil
        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, field, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        soil = field.soil

        soil.calculate_annual_water_balance()

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
        annual_water_balance_graphic(annual_file_name, self.display_graphics, self.produce_graphics)
        annual_graphics(annual_file_name, self.display_graphics, self.produce_graphics, is_final)
        daily_graphics(self.file_name, self.display_graphics, self.produce_graphics, is_final)
