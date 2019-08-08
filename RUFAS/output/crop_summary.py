################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: crop_summary.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
#############################################
import csv

from RUFAS.output.data_analysis import data_analysis
from RUFAS.output.report_handler import BaseReportHandler


class CropSummary(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, file_name using data
        #
        self.set_properties(data)
        self.fieldNames = None

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.variables = {'year': ['time.cal_year', '', []],
                          'j_day': ['time.day', '', []],
                          'fr_PHU': ['cropType.fr_PHU', '%', []],
                          'biomass': ['cropType.biomass_act', 'kg ha^-1', []],
                          'LAI_act': ['cropType.LAI_act', 'm^2/m^2', []],
                          'Bio_N': ['cropType.bio_N', 'kg N ha^-1', []],
                          'Bio_P': ['cropType.bio_P', 'kg P ha^-1', []],
                          'z_root': ['cropType.z_root', 'mm', []],
                          'yield_act': ['cropType.yield_act', 'kg ha^-1', []]
                          }

        #
        # Yearly Outputs **NOT YET IMPLEMENTED**
        # 1D Lists [julianDay]
        #

    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            writer = csv.DictWriter(csvfile, fieldnames=self.variables.keys(),
                                    lineterminator='\n')

            writer.writeheader()

            units = {}
            for variable in self.variables:
                units[variable] = self.variables[variable][1]

            writer.writerow(units)

    # ---------------------------------------------------------------------------
    # Method: initialize
    # ---------------------------------------------------------------------------
    def initialize(self, state):

        self.write_header()

    # ---------------------------------------------------------------------------
    # Method: daily_update
    # ---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        """Stores the daily values that need to be printed in the report."""

        cropType = state.crop.crops_list["corn"]
        # Copy daily output values here

        for variable in self.variables:
            self.variables[variable][2].append(eval(self.variables[variable][0], globals(), locals()))

        # self.year.append(time.cal_year)
        # self.julianDay.append(time.day)
        #
        # self.daily_fr_PHU.append(cropType.fr_PHU)
        # self.daily_biomass_act.append(cropType.biomass_act)
        # self.daily_LAI_act.append(cropType.LAI_act)
        # self.daily_bio_N.append(cropType.bio_N)
        # self.daily_bio_P.append(cropType.bio_P)
        # self.daily_z_root.append(cropType.z_root)
        # self.daily_yield_act.append(cropType.yield_act)

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    # ---------------------------------------------------------------------------
    # Method: write_annual_report
    # ---------------------------------------------------------------------------
    def write_annual_report(self):
        """Appends the annual report to the output file."""

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.variables,
                                    lineterminator='\n')
            for day in range(len(self.variables['j_day'][2])):
                row = {}
                for variable in self.variables:
                    row[variable] = self.variables[variable][2][day]
                writer.writerow(row)

    # ---------------------------------------------------------------------------
    # Method: annual_flush
    # ---------------------------------------------------------------------------
    def annual_flush(self):
        """Sets all of the values in the output object to the default value."""

        for variable in self.variables:
            self.variables[variable][2] = []

    def produce_data_analysis(self, is_final):
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)
