"""
RUFAS: Ruminant Farm Systems Model
File name: soil_report.py

Description: Output handler

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
"""

import csv
from pathlib import Path

from RUFAS.output.report_handler import BaseReportHandler
from RUFAS.output.graphics import daily_graphics, annual_graphics


class SoilSummary(BaseReportHandler):

    def __init__(self, data, field_name):

        # identifies the report with a field
        self.field_name = field_name

        # sets produce_csv, report_name, f_name using data
        self.set_properties(data, self.field_name)

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

        # daily outputs
        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                'precip': ['weather.rainfall[time.year - 1][time.day - 1]', 'mm', []],
                                'runoff': ['soil.runoff', 'mm', []],
                                'ET_max': ['soil.ET_max', 'mm d^-1', []],
                                'ET_act': ['soil.ET_act', 'mm H20', []],
                                'trans_max': ['soil.trans_max', 'mm H20', []],
                                'evap_max': ['soil.evap_max', 'mm H20', []],
                                'surface_temp': ['soil.T_surf', 'C', []],
                                'sediment_yield': ['soil.sed', 'metric tons', []],
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

        # annual outputs
        self.annual_variables = {'year': ['time.cal_year', '', 0],
                                 'ET_max': ['soil.ET_max_annual', 'mm H20', 0],
                                 'ET': ['soil.ET_annual', 'mm H20', 0]
                                 }

    def write_headers(self, output_csv, variables):
        """
        Description:
            Writes variable names and units to the header of the csv

        Inputs:
            output_csv: csv to be written to
            variables: list of variables being reported
        """

        mode = 'a+' if output_csv.exists() else 'w+'

        with output_csv.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=variables.keys(),
                                    lineterminator='\n')

            writer.writeheader()

            units = {}
            for variable in variables:
                units[variable] = variables[variable][1]

            writer.writerow(units)

    def initialize(self, state):
        """
        Description:
            Initialize report
        """

        self.write_headers(self.get_fPath(), self.daily_variables)
        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")
        self.write_headers(annual_path, self.annual_variables)

    def daily_update(self, field, weather, time):
        """
        Description:
            Called daily from the output handler to store simulation values for
             reporting at the end of the year
        Inputs:
            field: a soil report is produced for each field simulated
        """

        soil = field.soil

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, field, weather, time):
        """
        Description:
            Called daily from the output handler to store simulation values for
             reporting at the end of the year
        Inputs:
            field: a soil report is produced for each field simulated
        """

        soil = field.soil

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())

    def write_annual_report(self):
        """
        Description:
            Called at the end of each simulation year to write stored values to
            the csv
        """

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csv_file:
            # Write data day by day
            writer = csv.DictWriter(csv_file, fieldnames=self.daily_variables.keys(),
                                    lineterminator='\n')

            for day in range(len(self.daily_variables['j_day'][2])):
                row = {}
                for variable in self.daily_variables:
                    row[variable] = self.daily_variables[variable][2][day]
                writer.writerow(row)

        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")

        mode = 'a+' if annual_path.exists() else 'w+'

        with annual_path.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.annual_variables.keys(),
                                    lineterminator='\n')
            row = {}
            for variable in self.annual_variables:
                row[variable] = self.annual_variables[variable][2]
            writer.writerow(row)

    def annual_flush(self):
        """
        Description:
            Clears stored values after reporting
        """

        for variable in self.daily_variables:
            self.daily_variables[variable][2] = []

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = 0

    def produce_report_graphics(self, is_final):
        """
        Description:
            Calls functions in graphics.py
        Inputs:
            is_final: flag indicating that this is the last report being
                        produced
        """

        annual_file_name = str(self.file_name).split('.')[0] + "_annual.csv"
        annual_graphics(annual_file_name, self.produce_graphics, self.display_graphics, is_final)
        daily_graphics(self.file_name, self.produce_graphics, self.display_graphics, is_final)
