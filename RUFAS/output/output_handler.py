################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: output_handler.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path
from abc import ABC, abstractmethod
from RUFAS import util

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
                        'soil_summary': SoilSummary(data['soil_summary'])
                        }
        
    #---------------------------------------------------------------------------
    # Method: initialize_reports
    #---------------------------------------------------------------------------
    def initialize_reports(self, state):
    '''Transfer needed (initial) data from state to report handlers.'''
        
        #self.reports['farm_summary'].get_data(state)
        self.reports['soil_summary'].get_data(state.soil)
        
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
        output_full_path.mkdir(exist_ok = True, parents = False)
        BaseReportHandler.path = output_full_path
        
        # Deletes existing output files of the same name
        for _, report in self.reports.items():
            if report.active:
                report.handle_existing_file()
    
    #---------------------------------------------------------------------------
    # Method: write_annual_reports
    #---------------------------------------------------------------------------
    def write_annual_reports(self):
        '''Prints the annual report to file for all reports.'''

        for _, report in self.reports.items():
            if report.active:
                report.write_annual_report()

    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        '''Sets all of the reports in the output object to the default.'''

        for _, report in self.reports.items():
            if report.active:
                report.annual_flush()
            
#-------------------------------------------------------------------------------
# Abstract Class: BaseReportHandler
#-------------------------------------------------------------------------------
class BaseReportHandler(ABC):
    '''
    Contains an interface for report handlers, each output report
    file implements this abstract class.
    '''
    
    # Default path for output report files
    path = Path("Outputs/Default_Output_Dir")

    def set_properties(self, data):
        self.active = data['active']
        self.report_name = data['report_name']
        self.fName = data['file_name']

    #---------------------------------------------------------------------------
    # Method: get_fPath
    #---------------------------------------------------------------------------        
    def get_fPath(self):
        '''Gets the path to which the report handler will write the report.

        Returns:
            Path: path to which the report will be written.
        '''
        return self.path / self.fName
    
    #---------------------------------------------------------------------------
    # Method: handle_existing_file
    #---------------------------------------------------------------------------
    def handle_existing_file(self):
        '''Deletes the existing output file of the same name if exists.''' 
        
        if self.get_fPath().exists():
            self.get_fPath().unlink()
            print("Existing {} file detected and deleted".format(self.fName))
            
    #---------------------------------------------------------------------------
    # Abstract Methods
    #---------------------------------------------------------------------------
    @abstractmethod
    def get_data(self): raise NotImplementedError()
    @abstractmethod
    def daily_update(self): raise NotImplementedError()
    @abstractmethod  
    def write_annual_report(self): raise NotImplementedError()
    @abstractmethod
    def annual_flush(self): raise NotImplementedError()


#
# Imports are down here to prevent circular imports
#
from RUFAS.output.farm_summary import FarmSummary
from RUFAS.output.soil_summary import SoilSummary
