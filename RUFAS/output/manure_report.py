################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: manure_report.py
Description:
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################

from pathlib import Path
import csv
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: ManureReport
#-------------------------------------------------------------------------------
class ManureReport(BaseReportHandler):
    """Creates and prints to the file manure_report.csv"""

    def __init__(self, data, toggle):

        # Sets active, report_name, f_name using data
        self.set_properties(data)
        if not toggle.animal and self.active:
            print('Animal Module set as not simulated in json file and manure_report is still active, setting manure_report to not active.')
            self.active = False

        # Daily Outputs
        self.year = []
        self.julian_day = []
        self.pen_ids = []
        self.num_animals_in_pen = {}
        self.U = {}
        self.TAN_s = {}
        self.MN = {}
        self.Mkg = {}
        self.VSd = {}
        self.VSnd = {}

        self.feed_info = {}

    #---------------------------------------------------------------------------
    # Method: write_header
    #         Writes the header (column titles and units) in the csvfile
    #---------------------------------------------------------------------------
    def write_header(self):

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as csvfile:

            # 1) Initialize the header of the cvsfile
            fieldnames = ['Year', 'Julian Day', 'Pen ID', 'Number of Animals in Pen', 'U', 'TAN_s', 'MN', 'Mkg', 'VSd', 'VSnd']
            self.fieldNames = fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    lineterminator = '\n')
            writer.writeheader()
            
            # 2) Write Units in 2nd row of cvsfile
            units = {'Year': '', 'Julian Day': '', 'Pen ID': '', 'Number of Animals in Pen': '',
                             'U': 'mol/L', 'TAN_s': 'mol/L', 'MN': 'g', 'Mkg': 'kg', 'VSd': 'g', 'VSnd': 'g'}

            writer.writerow(units)

    #---------------------------------------------------------------------------
    # Method: initialize
    #---------------------------------------------------------------------------
    def initialize(self, state):
        """Transfers the needed data from State object to the report handler."""        
        for pen in state.animal_management.all_pens:
            self.pen_ids.append(pen.id)
            self.num_animals_in_pen[pen.id] = []
            self.U[pen.id] = []
            self.TAN_s[pen.id] = []
            self.MN[pen.id] = []
            self.Mkg[pen.id] = []
            self.VSd[pen.id] = []
            self.VSnd[pen.id] = []
                
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
                    self.U[pen.id].append(round(pen.manure['U'], 3))
                    self.TAN_s[pen.id].append(round(pen.manure['TAN_s'], 3))
                    self.MN[pen.id].append(round(pen.manure['MN'], 3))
                    self.Mkg[pen.id].append(round(pen.manure['Mkg'], 3))
                    self.VSd[pen.id].append(round(pen.manure['VSd'], 3))
                    self.VSnd[pen.id].append(round(pen.manure['VSnd'], 3))
                else:
                    self.U[pen.id].append(0)
                    self.TAN_s[pen.id].append(0)
                    self.MN[pen.id].append(0)
                    self.Mkg[pen.id].append(0)
                    self.VSd[pen.id].append(0)
                    self.VSnd[pen.id].append(0)
                    
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
                    manure_data = {
                        'Year':
                            str(self.year[i]),
                        'Julian Day':
                            str(self.julian_day[i]),
                        'Pen ID':
                            str(pen_id),
                        'Number of Animals in Pen':
                            str(self.num_animals_in_pen[pen_id][i]),
                        'U':
                            str(self.U[pen_id][i]),
                        'TAN_s':
                            str(self.TAN_s[pen_id][i]),
                        'MN':
                            str(self.MN[pen_id][i]),
                        'Mkg':
                            str(self.Mkg[pen_id][i]),
                        'VSd':
                            str(self.VSd[pen_id][i]),
                        'VSnd':
                            str(self.VSnd[pen_id][i]),
                    }

                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames,
                                    lineterminator = '\n')
                    writer.writerow(manure_data)
                    
    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        """Sets all of the values in the output object to the default value."""
        self.year = []
        self.julian_day = []
        
        for pen_id in self.pen_ids:
            self.num_animals_in_pen[pen_id] = []
            self.U[pen_id] = []
            self.TAN_s[pen_id] = []
            self.MN[pen_id] = []
            self.Mkg[pen_id] = []
            self.VSd[pen_id] = []
            self.VSnd[pen_id] = []

        
