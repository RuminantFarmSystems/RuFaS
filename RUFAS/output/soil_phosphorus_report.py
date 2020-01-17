"""
RUFAS: Ruminant Farm Systems Model
File name: soil_phosphorus_report.py

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
           William Donovan, wmdonovan@wisc.edu

Description: Output handler for Phosphorus cycling within the soil module
"""

import csv
from pathlib import Path

from RUFAS.output.graphics import daily_graphics, annual_graphics
from RUFAS.output.report_handler import BaseReportHandler


class SoilPhosphorus(BaseReportHandler):

    def __init__(self, data, field_name):

        # identifies report with a field
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

        self.daily_variables = {'year': ['time.calendar_year', '', []],
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
                                'sediment_P': ['soil.sed_P', 'kg/ha', []],
                                }

        self.annual_variables = {'year': ['time.calendar_year', '', 0]
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
            field: a soil phosphorus report is produced for each field simulated
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
            field: a soil phosphorus report is produced for each field simulated
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
