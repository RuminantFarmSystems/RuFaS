################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# water_balance.py
#
# Authors: Jacob Johnson
#          William Donovan
#
################################################################################

import csv
from pathlib import Path

from RUFAS.output.data_analysis import data_analysis, annual_data_analysis
from RUFAS.output.report_handler import BaseReportHandler


# -------------------------------------------------------------------------------
# Class: SoilSummary
# Creates and prints to the file water_balance.csv
# -------------------------------------------------------------------------------
class WaterBalance(BaseReportHandler):

    def __init__(self, data):

        #
        # Sets active, report_name, file_name using data
        #

        self.set_properties(data)
        self.fieldNames = None
        self.show_annual = data['show_annual']
        

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.year = []
        self.julianDay = []

        self.delta_SW = []
        self.runoff = []
        self.Ea = []
        self.drainage = []

        self.p_act = []
        self.p_calc = []

        self.diff = []

        self.cal_year = []

        self.annual_delta_SW = 0.0
        self.runoff_sum = 0.0
        self.Ea_sum = 0.0
        self.drainage_sum = 0.0

        self.annual_p_act = 0.0
        self.annual_p_calc = 0.0
        self.annual_diff = 0.0

    # ---------------------------------------------------------------------------
    # Function: write_header
    #           Writes the header (title and units) in the csvfile
    # ---------------------------------------------------------------------------
    def write_headers(self, output_csv):

        mode = 'a+' if output_csv.exists() else 'w+'

        with output_csv.open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Change in SW', 'Runoff',
                          'Evapotranspiration (Ea)', 'Drainage',
                          'Actual Precipitation', 'Calculated Water',
                          'Difference']

            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator='\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile

            units = {}
            for fieldname in fieldnames:
                if fieldname == 'Year' or fieldname == 'Julian Day':
                    units[fieldname] = ''
                else:
                    units[fieldname] = 'mm H2O'

            writer.writerow(units)

    # ---------------------------------------------------------------------------
    # Function: initialize
    #           Transfers the needed data from Soil object to the report handler
    # ---------------------------------------------------------------------------
    def initialize(self, state):
        self.write_headers(self.get_fPath())
        annual_path = Path(str(self.get_fPath()).split('.')[0] + "_annual.csv")
        self.write_headers(annual_path)

    # ---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'water balance'
    # csv file
    # ---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):

        soil = state.soil

        self.year.append(time.cal_year)
        self.julianDay.append(time.day)

        self.delta_SW.append(soil.delta_SW)
        self.runoff.append(soil.runoff)
        self.Ea.append(soil.Ea)
        self.drainage.append(soil.drainage)

        self.p_act.append(soil.p_act)
        self.p_calc.append(soil.p_calc)

        self.diff.append(soil.water_balance)

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        soil = state.soil

        soil.calculate_annual_water_balance()

        self.cal_year = time.cal_year

        self.annual_delta_SW = soil.annual_delta_SW
        self.runoff_sum = soil.runoff_sum
        self.Ea_sum = soil.Ea_sum
        self.drainage_sum = soil.drainage_sum

        self.annual_p_act = soil.p_act_annual
        self.annual_p_calc = soil.p_calc_annual

        self.annual_diff = soil.annual_water_balance

    # ---------------------------------------------------------------------------
    # Function: write_annual_report
    #           Appends the annual report to the output file
    # Water Balance is a cvsfile
    # ---------------------------------------------------------------------------
    def write_annual_report(self, y):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # Write data day by day
            for x in range(0, len(self.julianDay)):
                daily_water_data = {
                    'Year':
                        str(self.year[x]),
                    'Julian Day':
                        str(self.julianDay[x]),
                    'Change in SW':
                        str(round(float(self.delta_SW[x]), 3)),
                    'Runoff':
                        str(round(float(self.runoff[x]), 3)),
                    'Evapotranspiration (Ea)':
                        str(round(float(self.Ea[x]), 3)),
                    'Drainage':
                        str(round(float(self.drainage[x]), 3)),
                    'Actual Precipitation':
                        str(round(float(self.p_act[x]), 3)),
                    'Calculated Water':
                        str(round(float(self.p_calc[x]), 3)),
                    'Difference':
                        str(round(float(self.diff[x]), 3))
                }

                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                        lineterminator='\n')
                writer.writerow(daily_water_data)

        annual_path = Path(str(self.get_fPath()).split('.')[0] + "_annual.csv")

        mode = 'a+' if annual_path.exists() else 'w+'

        with annual_path.open(mode) as csvfile:
            annual_water_data = {
                'Year':
                    str(self.cal_year),
                'Julian Day':
                    str(self.julianDay[-1]),
                'Change in SW':
                    str(round(float(self.annual_delta_SW), 3)),
                'Runoff':
                    str(round(float(self.runoff_sum), 3)),
                'Evapotranspiration (Ea)':
                    str(round(float(self.Ea_sum), 3)),
                'Drainage':
                    str(round(float(self.drainage_sum), 3)),
                'Actual Precipitation':
                    str(round(float(self.annual_p_act), 3)),
                'Calculated Water':
                    str(round(float(self.annual_p_calc), 3)),
                'Difference':
                    str(round(float(self.annual_diff), 3))

            }

            writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator='\n')
            writer.writerow(annual_water_data)

    # ---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    # ---------------------------------------------------------------------------
    def annual_flush(self):

        self.year = []
        self.julianDay = []

        self.delta_SW = []
        self.runoff = []
        self.Ea = []
        self.drainage = []

        self.p_act = []
        self.p_calc = []

        self.diff = []

        self.cal_year = []

        self.annual_delta_SW = 0.0
        self.runoff_sum = 0.0
        self.Ea_sum = 0.0
        self.drainage_sum = 0.0

        self.annual_p_act = 0.0
        self.annual_p_calc = 0.0
        self.annual_diff = 0.0

    def produce_data_analysis(self, is_final):
        annual_file_name = str(self.file_name).split('.')[0] + "_annual.csv"
        annual_data_analysis(annual_file_name, self.show_annual, self.produce_diagnostics)
        data_analysis(self.file_name, self.show_daily, self.produce_diagnostics, is_final)
