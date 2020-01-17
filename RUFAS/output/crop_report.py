"""
RUFAS: Ruminant Farm Systems Model
File name: crop_report.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: Output handler for the crop module. Operates on daily and annual
                simulation scale.
"""

import csv
from pathlib import Path
from RUFAS.output.graphics import daily_graphics, annual_graphics
from RUFAS.output.report_handler import BaseReportHandler


class CropSummary(BaseReportHandler):

    def __init__(self, data, field_name):

        # identifies report with a field
        self.field_name = field_name

        # sets produce_csv, report_name, file_name using report data
        self.set_properties(data, self.field_name)
        self.field_names = None

        #
        # Outputs can be added in this single place in the following format:
        # 'output_name': ['variable_name', 'unit', []],
        # 'output_name' is a user defined key that will show up in outputs/graphs.
        # avoid spaces.
        # 'variable_name' is very important. This has to be a variable defined
        # and initialized in the object. If you are interested in tracking
        # a variable not defined in the class, you need to define it in the class first.
        # The output handler will not work if the variable is incorrect.
        # 'unit' is user defined but will, again, show up in outputs/graphs.
        # [] is an empty list
        #

        # daily outputs
        self.daily_variables = {'year': ['time.calendar_year', '', []],
                                'j_day': ['time.day', '', []],
                                'fr_PHU': ['crop_type.fr_PHU', '%', []],
                                'biomass': ['crop_type.biomass_actual', 'kg/ha', []],
                                'LAI_act': ['crop_type.LAI_actual', 'm^2/m^2', []],
                                'Bio_N': ['crop_type.bio_N', 'kg N/ha', []],
                                'Bio_P': ['crop_type.bio_P', 'kg P/ha', []],
                                'z_root': ['crop_type.z_root', 'mm', []],
                                'yield_act': ['crop_type.yield_actual', 'kg/ha', []],
                                'N_fix': ['crop_type.N_fix', 'units / Jacob', []]
                                }

        # annual outputs
        self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                 'yield': ['crop_type.yield_annual', 'kg/ha', 0]
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
            field: each field in the simulation has a separate crop report
        """

        crop_type = field.crop.current_crop

        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, field, weather, time):
        """
        Description:
            Called at the end of each simulation year to store annual values
        Inputs:
            field: each field in the simulation has a separate crop report
        """

        crop_type = field.crop.current_crop

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

        annual_path = Path(str(self.get_fPath()).split('.csv')[0] + '_annual.csv')

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
        annual_graphics(annual_file_name, self.display_graphics, self.produce_graphics, is_final)
        daily_graphics(self.file_name, self.produce_graphics, self.display_graphics, is_final)
