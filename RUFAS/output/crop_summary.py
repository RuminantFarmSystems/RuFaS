################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: crop_summary.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
'''
#############################################
import csv
from RUFAS.output.report_handler import BaseReportHandler

class CropSummary(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)
        self.fieldNames = None

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #

        self.year = []
        self.julianDay = []
        self.daily_fr_PHU = []
        self.daily_biomass_actual = []
        self.daily_LAI_actual = []
        self.daily_bio_N = []
        self.daily_bio_P = []
        self.daily_z_root = []
        self.daily_yield_actual = []

        #
        # Yearly Outputs **NOT YET IMPLEMENTED**
        # 1D Lists [julianDay]
        #

    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            fieldnames = ['Year', 'Julian Day', 'frPHU (fr_PHU)',
                          'Biomass (biomass_actual)', 'LAI (LAI_actual)',
                          'BioN (bio_N)', 'BioP (bio_P)',
                          'Rooting Depth (z_root)',
                          'Yield (yield_actual)']

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator='\n')
            writer.writeheader()

            units = {'Year': '', 'Julian Day': '', 'frPHU (fr_PHU)': '%',
                     'Biomass (biomass_actual)': 'kg ha^-1',
                     'LAI (LAI_actual)': 'm^2 / m^2',
                     'BioN (bio_N)': 'kg N ha^-1',
                     'BioP (bio_P)': 'kg P ha^-1',
                     'Rooting Depth (z_root)': 'mm',
                     'Yield (yield_actual)': 'kg ha^-1'}

            writer.writerow(units)


    # ---------------------------------------------------------------------------
    # Method: initialize
    # ---------------------------------------------------------------------------
    def initialize(self, state):
        '''Transfers the needed data from state object to the report handler.'''
        # d = 1

        # Copy daily output values here
        # self.daily_fr_PHU[d] = cropType.fr_PHU
        # self.daily_biomass_actual[d] = cropType.biomass_actual
        # self.daily_LAI_actual[d] = cropType.LAI_actual
        # self.daily_bio_N[d] = cropType.bio_N
        # self.daily_bio_P[d] = cropType.bio_P
        # self.daily_z_root[d] = cropType.z_root
        # self.daily_yield_actual[d] = cropType.yield_actual

        self.write_header()

    # ---------------------------------------------------------------------------
    # Method: daily_update
    # ---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        '''Stores the daily values that need to be printed in the report.'''

        cropType = state.crop.crops_list["corn"]
        # Copy daily output values here
        self.year.append(time.year)
        self.julianDay.append(time.day)

        self.daily_fr_PHU.append(cropType.fr_PHU)
        self.daily_biomass_actual.append(cropType.biomass_actual)
        self.daily_LAI_actual.append(cropType.LAI_actual)
        self.daily_bio_N.append(cropType.bio_N)
        self.daily_bio_P.append(cropType.bio_P)
        self.daily_z_root.append(cropType.z_root)
        self.daily_yield_actual.append(cropType.yield_actual)

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        '''Stores the yearly values that need to be printed in the report.'''
        pass

    # ---------------------------------------------------------------------------
    # Method: write_annual_report
    # ---------------------------------------------------------------------------
    def write_annual_report(self, y):
        '''Appends the annual report to the output file.'''

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            for x in range(0, len(self.julianDay)):
                dailyCropData = {
                    'Year':
                        str(self.year[x]),
                    'Julian Day':
                        str(self.julianDay[x]),
                    'frPHU (fr_PHU)':
                        str(self.daily_fr_PHU[x]),
                    'Biomass (biomass_actual)':
                        str(self.daily_biomass_actual[x]),
                    'LAI (LAI_actual)':
                        str(self.daily_LAI_actual[x]),
                    'BioN (bio_N)':
                        str(self.daily_bio_N[x]),
                    'BioP (bio_P)':
                        str(self.daily_bio_P[x]),
                    'Rooting Depth (z_root)':
                        str(self.daily_z_root[x]),
                    'Yield (yield_actual)':
                        str(self.daily_yield_actual[x])
                }

                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                        lineterminator='\n')
                writer.writerow(dailyCropData)

    # ---------------------------------------------------------------------------
    # Method: annual_flush
    # ---------------------------------------------------------------------------
    def annual_flush(self):
        '''Sets all of the values in the output object to the default value.'''

        self.year = []
        self.julianDay = []

        self.daily_fr_PHU = []
        self.daily_biomass_actual = []
        self.daily_LAI_actual = []
        self.daily_bio_N = []
        self.daily_bio_P = []
        self.daily_z_root = []
        self.daily_yield_actual = []
