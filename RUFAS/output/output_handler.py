################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: output_handler.py
Description: Contains the definition of the OutputHandler object
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path

from RUFAS import util
from RUFAS.output.report_handler import BaseReportHandler

#
# Import report handlers here
#
from RUFAS.output.soil_summary import SoilSummary
from RUFAS.output.soil_nitrogen import SoilNitrogen
from RUFAS.output.ration_report import RationReport

#-------------------------------------------------------------------------------
# Class: OutputHandler
#-------------------------------------------------------------------------------
class OutputHandler():
    '''Handles all output related interactions.

    Contains a list of all the report handlers, which handles all output-related
    functionalities. This object is the (only) bridge between the simulation
    engine and the output routines.

    Output values are updated at the end of each day, and the each report is
    printed at the end of each year, using the values (that are written daily)
    for the year period and also any yearly output values. After each the report
    for the year is printed, every single report handler object is flushed,
    leaving absolutely nothing. The report handler begins accumulating
    information again for the next year.

    We do not recommend doing any calculations inside the report handler.
    Report handlers should exist only to store RAW OUTPUT DATA. All calculations
    should be done within the routine, saved to the State object, then extracted
    from the state object to the report handler at the end of the day. However,
    it is OK to perform some calculations (it won't cause any bugs). This makes
    sense to do when you want some statistical values that aren't already
    calculated in the routine, and you do not want to mess with the routine
    directly.
    '''

    def __init__(self, data):
        '''Initializes the report handlers with the given data'''

        # Instantiate Report Handler Objects here
        self.reports = [
                            SoilSummary(data['soil_summary']),
                            SoilNitrogen(data['soil_nitrogen']),
                            RationReport(data['ration_report'])
                       ]

    #---------------------------------------------------------------------------
    # Method: initialize_output_dir
    #---------------------------------------------------------------------------
    def initialize_output_dir(self, output_dir):
        '''
        If a directory of the same name exists, it and its contents is deleted,
        then creates the directory for all output report files as specified.
        Sets output file path for all reports through the class attribute of the
        BaseReportHandler class.

        Args:
            output_dir (Path): The path to the directory that will store all
                output report files.
        '''

        # Initialize path for reports
        output_dir = util.get_base_dir() / output_dir

        # Delete directory if previously exists
        if output_dir.exists():
            for file in output_dir.iterdir():
                file.unlink()
            output_dir.rmdir()

        output_dir.mkdir(exist_ok = True, parents = False)
        BaseReportHandler.set_dir(output_dir)

    #---------------------------------------------------------------------------
    # Method: initialize_reports
    #---------------------------------------------------------------------------
    def initialize_reports(self, state):
        '''Transfer needed (initial) data from state to report handlers.'''

        for report in self.reports:
            if report.active:
                report.initialize(state)

    #---------------------------------------------------------------------------
    # Method: daily_update
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        '''Updates the report handler with new daily values.'''

        for report in self.reports:
            if report.active:
                report.daily_update(state, weather, time)

    #---------------------------------------------------------------------------
    # Method: annual_update
    #---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        '''Updates the report handler with anuual output values.'''

        for report in self.reports:
            if report.active:
                report.annual_update(state, weather, time)

    #---------------------------------------------------------------------------
    # Method: write_annual_reports
    #---------------------------------------------------------------------------
    def write_annual_reports(self, y):
        '''Prints the annual report to file for all reports.'''

        for report in self.reports:
            if report.active:
                report.write_annual_report(y)

    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------s
    def annual_flush(self):
        '''Sets all of the reports in the output object to the default.'''

        for report in self.reports:
            if report.active:
                report.annual_flush()
