################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: growth_report.py
Description:
Author(s): Militsa Sotirova, militsasotirova@gmail.com    
"""
################################################################################

from pathlib import Path
import csv
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: GrowthReport
#-------------------------------------------------------------------------------
class GrowthReport(BaseReportHandler):
    """Creates and prints to the file growth_report.csv"""

    def __init__(self, data):

        # Sets active, report_name, f_name using data
        self.set_properties(data)

        # Daily Outputs
        self.year = []
        self.julian_day = []
        self.pen_ids = []
        self.num_animals_in_pen = {}
        self.avg_growth = {}
        self.avg_milk = {}

        self.feed_info = {}

    #---------------------------------------------------------------------------
    # Method: write_header
    #         Writes the header (column titles and units) in the csvfile
    #---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Pen ID', 'Number of Animals in Pen', 'Average Growth', 'Average Milk']
            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator = '\n')
            writer.writeheader()

            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '', 'Pen ID': '', 'Number of Animals in Pen': '',
                             'Average Growth': 'kg', 'Average Milk': 'kg'}
            writer.writerow(units)

    #---------------------------------------------------------------------------
    # Method: initialize
    #---------------------------------------------------------------------------
    def initialize(self, state):
        """Transfers the needed data from State object to the report handler."""
        for pen in state.animal_management.all_pens:
            self.pen_ids.append(pen.id)
            self.num_animals_in_pen[pen.id] = []
            self.avg_growth[pen.id] = []
            self.avg_milk[pen.id] = []
                
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
                    self.avg_growth[pen.id].append(round(pen.avg_growth, 3))
                    self.avg_milk[pen.id].append(round(pen.avg_milk, 3))
                else:
                    self.avg_growth[pen.id].append(0)
                    self.avg_milk[pen.id].append(0)
    
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

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:
            for i in range(0, len(self.julian_day)):
                for pen_id in self.pen_ids:
                    growth_data = {
                        'Year':
                            str(self.year[i]),
                        'Julian Day':
                            str(self.julian_day[i]),
                        'Pen ID':
                            str(pen_id),
                        'Number of Animals in Pen':
                            str(self.num_animals_in_pen[pen_id][i]),
                        'Average Growth':
                            str(self.avg_growth[pen_id][i]),
                        'Average Milk':
                            str(self.avg_milk[pen_id][i])
                    }

                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator = '\n')
                    writer.writerow(growth_data)
                    
    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        """Sets all of the values in the output object to the default value."""
        self.year = []
        self.julian_day = []
        
        for pen_id in self.pen_ids:
            self.num_animals_in_pen[pen_id] = []
            self.avg_growth[pen_id] = []
            self.avg_milk[pen_id] = []
