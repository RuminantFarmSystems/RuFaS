"""
RUFAS: Ruminant Farm Systems Model
File name: ration_report.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Militsa Sotirova, militsasotirova@gmail.com
           William Donovan, wmdonovan@wisc.edu
"""

import csv
from pathlib import Path

from RUFAS.output.report_handler import BaseReportHandler
from RUFAS.output.graphics import daily_graphics, annual_graphics


class RationReport(BaseReportHandler):
    """Creates and prints to the file ration_report.csv"""

    def __init__(self, data, pen_id):

        # sets active, report_name, file_name using data
        self.set_properties(data, 'null')

        # identifies report with a pen
        self.pen_id = pen_id
        self.file_name = 'pen_' + str(pen_id) + '/' + self.file_name

        self.feed_info = {}

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

        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                'num_animals': ['len(pen.animals_in_pen)', '', []],
                                'achieved_price': ['pen.ration[\'objective\'] if pen.pen_populated else 0', '', []]
                                }

        self.annual_variables = {'year': ['time.cal_year', '', 0]}

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

        self.feed_info = state.feed.available_feeds

        for feed_type in self.feed_info.keys():
            self.daily_variables[feed_type] = ['pen.ration[\'%s\'] if pen.pen_populated else 0' % feed_type,
                                               self.feed_info[feed_type]['Units'], []]

        self.write_headers(self.get_fPath(), self.daily_variables)
        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + "_annual.csv")
        self.write_headers(annual_path, self.annual_variables)

    def daily_update(self, pen, weather, time):
        """
        Description:
            Called daily from the output handler to store simulation values for
             reporting at the end of the year
        Inputs:
            pen: a ration report is produced for each pen simulated
        """

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        """
        Description:
            Called at the end of each simulation year to store annual values
        Inputs:
            pen: a ration report is produced for each pen simulated
        """

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.daily_variables[variable][0], globals(), locals())

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
