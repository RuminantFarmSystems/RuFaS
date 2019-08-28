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
                          'precip': ['weather.rainfall[time.year - 1][time.day - 1]', 'mm', []],
                          'runoff': ['soil.runoff', 'mm', []],
                          'ET_max': ['soil.ET_max', 'mm d^-1', []],
                          'ET_act': ['soil.ET_act', 'mm H20', []],
                          'trans_max': ['soil.trans_max', 'mm H20', []],
                          'evap_max': ['soil.evap_max', 'mm H20', []],
                          'surface_temp': ['soil.Tsurf', 'C', []],
                          'sediment_yield': ['soil.sedimentYield', 'metric tons', []],
                          'residue': ['soil.residue', 'kg/ha', []],
                          'trans_act_L1': ['soil.soil_layers[0].trans_act', 'mm H20', []],
                          'trans_act_L2': ['soil.soil_layers[1].trans_act', 'mm H20', []],
                          'trans_act_L3': ['soil.soil_layers[2].trans_act', 'mm H20', []],
                          'soil_water_L1': ['soil.soil_layers[0].soil_water', 'mm', []],
                          'soil_water_L2': ['soil.soil_layers[1].soil_water', 'mm', []],
                          'soil_water_L3': ['soil.soil_layers[2].soil_water', 'mm', []],
                          'evap_L1': ['soil.soil_layers[0].evap', 'mm H20', []],
                          'evap_L2': ['soil.soil_layers[1].evap', 'mm H20', []],
                          'evap_L3': ['soil.soil_layers[2].evap', 'mm H20', []],
                          'perc_L1': ['soil.soil_layers[0].perc', 'mm H20', []],
                          'perc_L2': ['soil.soil_layers[1].perc', 'mm H20', []],
                          'perc_L3': ['soil.soil_layers[2].perc', 'mm H20', []],
                          'temperature_L1': ['soil.soil_layers[0].temperature', 'C', []],
                          'temperature_L2': ['soil.soil_layers[1].temperature', 'C', []],
                          'temperature_L3': ['soil.soil_layers[2].temperature', 'C', []],
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
    def daily_update(self, field, weather, time):
        soil = field.soil

        for variable in self.variables:
            self.variables[variable][2].append(eval(self.variables[variable][0], globals(), locals()))

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, field, weather, time):
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

