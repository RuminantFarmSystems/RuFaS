################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: ration_report.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################

from pathlib import Path
import csv
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: RationReport
#-------------------------------------------------------------------------------
class RationReport(BaseReportHandler):
    """Creates and prints to the file ration_report.csv"""

    def __init__(self, data, toggle):

        # Sets active, report_name, f_name using data
        self.set_properties(data)
        if not toggle.animal and self.active:
            print('Animal Module set as not simulated in json file and ration_report is still active, setting ration_report to not active.')
            self.active = False

        # Daily Outputs
        self.year = []
        self.julian_day = []
        self.pen_ids = []
        self.num_animals_in_pen = {}
        self.achieved_price = {}
        self.feed_amounts = {}

        self.feed_info = {}

    #---------------------------------------------------------------------------
    # Method: write_header
    #         Writes the header (column titles and units) in the csvfile
    #---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Pen ID', 'Number of Animals in Pen', 'Achieved Total Price']
            for key in self.feed_info.keys():
                fieldnames.append(key)
            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator = '\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '', 'Pen ID': '', 'Number of Animals in Pen': '',
                             'Achieved Total Price': "$"}
            for key in self.feed_info.keys():
                units[key] = self.feed_info[key]['Units']

            writer.writerow(units)

    #---------------------------------------------------------------------------
    # Method: initialize
    #---------------------------------------------------------------------------
    def initialize(self, state):
        """Transfers the needed data from State object to the report handler."""
        feed = state.feed
        # get static data like units associated with each feed type
        # store in Feed or Animal???????
        self.feed_info = feed.available_feeds

        for pen in state.animal_management.all_pens:
            self.pen_ids.append(pen.id)
            self.num_animals_in_pen[pen.id] = []
            self.achieved_price[pen.id] = []
            self.feed_amounts[pen.id] = []

        self.write_header()

    #---------------------------------------------------------------------------
    # Method: daily_update
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        """Stores the daily values that need to be printed in the report."""
        self.year.append(time.cal_year)

        animal_management = state.animal_management

        # for each day that a ration is calculated, appends the necessary information to the lists
        if animal_management.end_ration_interval():
            self.julian_day.append(time.day)

            for pen in animal_management.all_pens:
                self.num_animals_in_pen[pen.id].append(len(pen.animals_in_pen))

                if pen.pen_populated:
                    self.achieved_price[pen.id].append(round(pen.ration['objective'], 2))
                    self.feed_amounts[pen.id].append({feed_type: round(pen.ration[feed_type], 3) for feed_type in self.feed_info.keys()})
                else:
                    self.achieved_price[pen.id].append(0)
                    self.feed_amounts[pen.id].append({feed_type: 0 for feed_type in self.feed_info.keys()})

    #---------------------------------------------------------------------------
    # Method: annual_update
    #---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        """Stores the yearly values that need to be printed in the report."""
        pass

    #---------------------------------------------------------------------------
    # Method: write_annual_report
    #---------------------------------------------------------------------------
    def write_annual_report(self, y):
        """Appends the annual report to the output file."""

        print("printing ration report for year: " + str(y))
        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            for i in range(0, len(self.julian_day)):
                for pen_id in self.pen_ids:
                    ration_data = {
                        'Year':
                            str(self.year[i]),
                        'Julian Day':
                            str(self.julian_day[i]),
                        'Pen ID':
                            str(pen_id),
                        'Number of Animals in Pen':
                            str(self.num_animals_in_pen[pen_id][i]),
                        'Achieved Total Price':
                            str(self.achieved_price[pen_id][i])
                    }
                    for feed_type in sorted(self.feed_info.keys()):
                        ration_data[feed_type] = self.feed_amounts[pen_id][i][feed_type]

                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator = '\n')
                    writer.writerow(ration_data)

    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        """Sets all of the values in the output object to the default value."""
        self.year = []
        self.julian_day = []

        for pen_id in self.pen_ids:
            self.num_animals_in_pen[pen_id] = []
            self.achieved_price[pen_id] = []
            self.feed_amounts[pen_id] = []
