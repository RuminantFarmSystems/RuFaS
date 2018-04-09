################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: output_handler.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path

from RUFAS import util
from RUFAS.output.report_handler import BaseReportHandler
from RUFAS.output.farm_summary import FarmSummary
from RUFAS.output.soil_summary import SoilSummary
from RUFAS.output.ration_report import RationReport
from RUFAS.output.crop_report import CropReport

#-------------------------------------------------------------------------------
# Class: OutputHandler
#-------------------------------------------------------------------------------
class OutputHandler():
    '''
    Contains a dictionary of all the report handlers.
    Handles output related interactions.
    '''

    def __init__(self, data):
        '''
        TODO: Add DocString
        '''

        self.reports = {
                        'farm_summary': FarmSummary(data['farm_summary']),
                        'soil_summary': SoilSummary(data['soil_summary']),
                        'ration_report': RationReport(data['ration_report']),
                        'crop_report': CropReport(data['crop_report']),
                        'soil_nitrogen': SoilNitrogen(data['soil_nitrogen'])
                        }

    #---------------------------------------------------------------------------
    # Method: initialize_reports
    #---------------------------------------------------------------------------
    def initialize_reports(self, state):
        '''Transfer needed (initial) data from state to report handlers.'''

        for _, report in self.reports.items():
            if report.active:
                report.get_data(state)
            if report.getfPath().suffix == '.csv':
                report.write_header()

    #---------------------------------------------------------------------------
    # Method: initialize_output_dir
    #---------------------------------------------------------------------------
    def initialize_output_dir(self, output_dir):
        '''
        Creates the directory to store output files (if doesn't exist)
        Sets output file path for all reports (through ReportHandler class
        attribute)
        '''

        # Initialize path for reports
        output_full_path = util.get_base_dir() / output_dir

        # Delete directory if previously exists
        for file in output_full_path.iterdir():
            file.unlink()
        output_full_path.rmdir()

        output_full_path.mkdir(exist_ok = True, parents = False)
        BaseReportHandler.path = output_full_path

        # Deletes existing output files of the same name
        for _, report in self.reports.items():
            if report.active:
                report.handle_existing_file()

    #---------------------------------------------------------------------------
    # Method: daily_update
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        '''Sets all of the reports in the output object to the default.'''

        for _, report in self.reports.items():
            if report.active:
                report.daily_update(state, weather, time)


    #---------------------------------------------------------------------------
    # Method: write_annual_reports
    #---------------------------------------------------------------------------
    def write_annual_reports(self, y):
        '''Prints the annual report to file for all reports.'''

        for _, report in self.reports.items():
            if report.active:
                report.write_annual_report(y)

    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------s
    def annual_flush(self):
        '''Sets all of the reports in the output object to the default.'''

        for _, report in self.reports.items():
            if report.active:
                report.annual_flush()
