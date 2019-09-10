################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: feed_storage.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
#############################################
import csv

from RUFAS.output.graphics import daily_graphics
from RUFAS.output.report_handler import BaseReportHandler


class FeedStorage(BaseReportHandler):

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
        # Sets active, report_name, file_name using data
        #
        self.set_properties(data)
        self.fieldNames = None

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                'dry_matter': ['feed.dry_matter', 'kg', []],
                                'carbon': ['feed.carbon', 'kg', []],
                                'nitrogen': ['feed.nitrogen', 'kg', []],
                                'phosphorus': ['feed.phosphorus', 'kg', []],
                                'crude_protein': ['feed.crude_protein', 'kg', []],
                                'C_harvest_gas': ['feed.C_harvest_gas', 'kg', []],
                                'C_harvest_particle': ['feed.C_harvest_particle', 'kg', []],
                                'C_storage_gas': ['feed.C_storage_gas', 'kg', []],
                                'C_storage_leachate': ['feed.C_storage_leachate', 'kg', []],
                                'C_feedout_gas': ['feed.C_feedout_gas', 'kg', []],
                                'C_feedout_particle': ['feed.C_feedout_particle', 'kg', []],
                                'CP_gas': ['feed.CP_gas', 'kg', []],
                                'CP_leachate': ['feed.CP_leachate', 'kg', []],
                                'NPN': ['feed.NPN', 'idk lol', []]
                                }

    #
    # writes header names and units to the csv
    #
    def write_header(self, output_csv, variables):

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

        self.write_header(self.get_fPath(), self.daily_variables)

    #
    # stores specified daily values. NOTE: the eval() method is limited
    # to the scope of variables. If a specified output is not a soil
    # variable, this will throw an error. See comment at the top of the file.
    #
    def daily_update(self, state, weather, time):
        """Stores the daily values that need to be printed in the report."""

        feed = state.feed
        # Copy daily output values here

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    #
    # writes stored values to the csv at the end of the year
    #
    def write_annual_report(self):
        """Appends the annual report to the output file."""

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.daily_variables,
                                    lineterminator='\n')
            for day in range(len(self.daily_variables['j_day'][2])):
                row = {}
                for variable in self.daily_variables:
                    row[variable] = self.daily_variables[variable][2][day]
                writer.writerow(row)

    #
    # clears stored values at the end of the year
    #
    def annual_flush(self):
        """Sets all of the values in the output object to the default value."""

        for variable in self.daily_variables:
            self.daily_variables[variable][2] = []

    def produce_report_graphics(self, is_final):
        daily_graphics(self.file_name, self.display_graphics, self.produce_graphics, is_final)
