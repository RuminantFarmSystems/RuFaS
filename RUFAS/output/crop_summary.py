################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: crop_summary.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
#############################################
import csv
from pathlib import Path

from RUFAS.output.data_analysis import data_analysis
from RUFAS.output.report_handler import BaseReportHandler


class CropSummary(BaseReportHandler):

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
                                'fr_PHU': ['crop_type.fr_PHU', '%', []],
                                'biomass': ['crop_type.biomass_actual', 'kg ha^-1', []],
                                'LAI_actual': ['crop_type.LAI_actual', 'm^2/m^2', []],
                                'Bio_N': ['crop_type.bio_N', 'kg N ha^-1', []],
                                'Bio_P': ['crop_type.bio_P', 'kg P ha^-1', []],
                                'rooting_depth': ['crop_type.z_root', 'mm', []],
                                'yield_actual': ['crop_type.yield_actual', 'kg ha^-1', []]
                                }

        self.annual_variables = {'year': ['time.cal_year', '', 0],
                                 'yield_annual': ['crop_type.yield_annual', 'kg ha^-1', 0]
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
        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + '_annual.csv')
        self.write_headers(annual_path, self.annual_variables)

    #
    # stores specified daily values. NOTE: the eval() method is limited
    # to the scope of variables. If a specified output is not a soil
    # variable, this will throw an error. See comment at the top of the file.
    #
    def daily_update(self, field, weather, time):
        """Stores the daily values that need to be printed in the report."""

        crop_type = field.crop.current_crop
        # Copy daily output values here

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, field, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        crop_type = field.crop.current_crop

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())
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

        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + '_annual.csv')

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
        """Sets all of the values in the output object to the default value."""

        for variable in self.daily_variables:
            self.daily_variables[variable][2] = []

        for variable in self.annual_variables:
            self.annual_variables[variable][2] = 0

    def produce_data_analysis(self, is_final):
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)
