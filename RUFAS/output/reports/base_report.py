"""
RUFAS: Ruminant Farm Systems Model
File name: base_report_handler.py
Description:
Author(s): William Donovan wmdonovan@wisc.edu
"""

import csv
from pathlib import Path

from .. import graphics


class BaseReport:
    """
    Interface for report handlers
    """
    def __init__(self, data):
        """Sets the properties of each report handler initialized.

        This is called in the report handler's __init__() method, and takes in
        the data passed to it and assigns the properties below.
        """

        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.report_name = data['report_name']
        self.file_name = self.report_name + '.csv'
        self.annual_file_name = self.report_name + '_annual.csv'
        self.csv_dir = ''
        self.diagnostic_dir = ''

        self.daily_variables = {
            'year': ['time.cal_year', '', []],
            'j_day': ['time.day', '', []]
        }

        self.annual_variables = {
            'year': ['time.cal_year', '', 0]
        }

    @staticmethod
    def write_headers(output_csv, variables):

        mode = 'a+' if output_csv.exists() else 'w+'

        with output_csv.open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=variables.keys(),
                                    lineterminator='\n')

            writer.writeheader()

            units = {}
            for variable in variables:
                units[variable] = variables[variable][1]

            writer.writerow(units)

    def initialize(self):
        self.write_headers(Path(str(self.csv_dir) + '/' + self.file_name), self.daily_variables)
        self.write_headers(Path(str(self.csv_dir) + '/' + self.annual_file_name), self.annual_variables)

    # stores specified daily values. NOTE: the eval() method is limited
    # to the scope of variables. If a specified output is not a soil
    # variable, this will throw an error.
    def daily_update(self, state, weather, time):

        soil = state.soil
        crop_type = state.crop.current_crop
        animal_management = state.animal_management
        feed = state.feed

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        soil = state.soil
        crop_type = state.crop.current_crop
        animal_management = state.animal_management
        feed = state.feed

        soil.annual_mass_balance()

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())

    #
    # writes stored values to the csv at the end of the year
    #
    def write_annual_report(self):

        mode = 'a+' if Path(str(self.csv_dir) + '/' + self.file_name).exists() else 'w+'

        with Path(str(self.csv_dir) + '/' + self.file_name).open(mode) as csv_file:
            # Write data day by day
            writer = csv.DictWriter(csv_file, fieldnames=self.daily_variables.keys(),
                                    lineterminator='\n')

            for day in range(len(self.daily_variables['j_day'][2])):
                row = {}
                for variable in self.daily_variables:
                    row[variable] = self.daily_variables[variable][2][day]
                writer.writerow(row)

        mode = 'a+' if Path(str(self.csv_dir) + '/' + self.annual_file_name).exists() else 'w+'

        with Path(str(self.csv_dir) + '/' + self.annual_file_name).open(mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.annual_variables.keys(),
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

    def produce_report_graphics(self):
        graphics.annual_graphics(self)
        graphics.daily_graphics(self)
