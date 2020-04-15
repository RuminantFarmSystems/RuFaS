"""
RUFAS: Ruminant Farm Systems Model
File name: water_balance.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: Output handler for the water balance report.
"""

import csv
from pathlib import Path

from RUFAS.output.graphics import daily_graphics, annual_water_balance_graphic, annual_graphics
from RUFAS.output.report_handler import BaseReportHandler


class WaterBalance(BaseReportHandler):

    def __init__(self, data, field_name):

        # identifies the report with a field
        self.field_name = field_name

        # sets produce_csv, report_name, file_name using data
        BaseReportHandler.__init__(self, data)

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
        self.daily_variables = {'year': ['time.calendar_year', '', []],
                                'j_day': ['time.day', '', []],
                                'change in sw': ['soil.delta_SW', 'mmH2O', []],
                                'runoff': ['soil.runoff', 'mmH2O', []],
                                'evaporation': ['soil.evap_sum', 'mmH2O', []],
                                'transpiration': ['soil.trans_sum', 'mmH2O', []],
                                'drainage': ['soil.drainage', 'mmH2O', []],
                                'precipitation': ['soil.p_act', 'mmH2O', []],
                                'calculated water': ['soil.p_calc', 'mmH2O', []],
                                'difference': ['soil.water_balance_difference', 'mmH2O', []]}

        # annual outputs
        self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                 'delta_SW': ['round(soil.delta_SW_annual, 3)', 'mmH2O', 0],
                                 'runoff': ['round(soil.runoff_annual, 3)', 'mmH2O', 0],
                                 'evaporation': ['round(soil.evap_annual, 3)', 'mmH2O', 0],
                                 'transpiration': ['round(soil.trans_annual, 3)', 'mmH2O', 0],
                                 'drainage': ['round(soil.drainage_annual, 3)', 'mmH2O', 0],
                                 # new variables need to be added below here

                                 # new variables need to be added above here
                                 'precipitation': ['round(soil.p_act_annual, 3)', 'mmH2O', 0],
                                 'calculated water': ['round(soil.p_calc_annual, 3)', 'mmH2O', 0],
                                 'difference': ['round(soil.annual_water_balance_difference, 3)', 'mmH2O', 0]}

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
            field: a water balance report is produced for each field simulated
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
            field: a water balance report is produced for each field simulated
        """

        soil = field.soil

        # calculate annual water balance at the end of the year before reset
        soil.calculate_annual_water_balance()

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

    def produce_report_graphics(self):
        """
        Description:
            Calls functions in graphics.py
        Inputs:
            is_final: flag indicating that this is the last report being
                        produced
        """
        annual_water_balance_graphic(self)
        annual_graphics(self)
        daily_graphics(self)
