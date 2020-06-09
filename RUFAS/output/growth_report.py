################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: growth_report.py
Description:
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################

from pathlib import Path
import csv
from RUFAS.output.report_handler import BaseReportHandler
from RUFAS.output.graphics import daily_graphics, annual_graphics


# -------------------------------------------------------------------------------
# Class: GrowthReport
# -------------------------------------------------------------------------------
class GrowthReport(BaseReportHandler):
    """Creates and prints to the file growth_report.csv"""

    def __init__(self, data, pen_id):

        # Sets produce_csv, report_name, f_name using data
        self.set_properties(data)
        self.file_name = 'pen_' + str(pen_id) + '/' + self.file_name
        self.pen_id = pen_id

        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                'num_animals_in_pen': ['len(pen.animals_in_pen)', '', []],
                                'average_growth': ['pen.avg_growth', 'kg', []],
                                'average_milk': ['pen.avg_milk', 'kg', []],
                                'average_p_animal': ['pen.avg_p_animal', 'g', []],
                                'average_p_req': ['pen.avg_p_req', 'g', []]
                                }

        self.annual_variables = {'year': ['time.cal_year', '', 0]
                                 }

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

    # ---------------------------------------------------------------------------
    # Method: daily_update
    # ---------------------------------------------------------------------------
    def daily_update(self, feed, pen, weather, time):
        """Stores the daily values that need to be printed in the report."""
        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    #---------------------------------------------------------------------------
    # Method: annual_update
    #---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.daily_variables[variable][0], globals(), locals())

    #---------------------------------------------------------------------------
    # Method: write_annual_report
    #---------------------------------------------------------------------------
    def write_annual_report(self):
        """Appends the annual report to the output file."""

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

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
                    
    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        """Sets all of the values in the output object to the default value."""
        for variable in self.daily_variables:
            self.daily_variables[variable][2] = []

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = 0

    def produce_report_graphics(self, is_final):
        annual_file_name = str(self.file_name).split('.')[0] + "_annual.csv"
        annual_graphics(annual_file_name, self.display_graphics, self.produce_graphics, is_final)
        daily_graphics(self.file_name, self.display_graphics, self.produce_graphics, is_final)
