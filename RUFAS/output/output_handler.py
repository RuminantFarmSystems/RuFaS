################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# output_handler.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from pathlib import Path
from abc import ABC, abstractmethod

#-------------------------------------------------------------------------------
# Class: OutputHandler
#        Contains a dictionary of all the report handlers
#        Handles output related interactions
#-------------------------------------------------------------------------------
class OutputHandler():

    def __init__(self, data):

        self.reports = {
                        'farm_summary': FarmSummary(data['farm_summary']),
                        'soil_summary': SoilSummary(data['soil_summary'])
                        }
        
    #---------------------------------------------------------------------------
    # Function: initialize_reports
    #
    #---------------------------------------------------------------------------
    def initialize_reports(self, state):
        
        self.reports['soil_summary'].get_data(state.soil)
        
    #---------------------------------------------------------------------------
    # Function: make_output_dir
    #           Creates the directory to store output files (if doesn't exist)
    #           Sets output file path for all reports (through ReportHandler
    #           class attribute)
    #---------------------------------------------------------------------------
    def initialize_output_dir(self, output_dir):
        
        Path(output_dir).mkdir(exist_ok = True, parents = False)
        BaseReportHandler.path = output_dir
        
        # Deletes existing output files of the same name
        for _, report in self.reports.items():
            if report.active:
                report.handle_existing_file()
    
    #---------------------------------------------------------------------------
    # Function: write_annual_reports
    #
    #---------------------------------------------------------------------------
    def write_annual_reports(self):

        for _, report in self.reports.items():
            if report.active:
                report.write_annual_report()

    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the reports in the output object to the default
    #---------------------------------------------------------------------------
    def annual_flush(self):

        for _, report in self.reports.items():
            if report.active:
                report.annual_flush()
            
#-------------------------------------------------------------------------------
# Abstract Class: BaseReportHandler
#                 Contains an interface for report handlers, each output report
#                 file implements this abstract class
#-------------------------------------------------------------------------------
class BaseReportHandler(ABC):
    
    # Default path for output report files
    path = "./Outputs/Default_Output_Dir/"

    def set_properties(self, data):

        self.active = data['active']
        self.report_name = data['report_name']
        self.fName = data['file_name']

    #---------------------------------------------------------------------------
    # Function: get_fPath
    #           Gets the path to which the report handler will write the report
    # Returns: A path object to which the report will be writtens
    #---------------------------------------------------------------------------        
    def get_fPath(self):
        return Path(self.path + self.fName)
    
    #---------------------------------------------------------------------------
    # Function: handle_existing_file
    #           deletes the existing output file of the same name if exists
    #---------------------------------------------------------------------------
    def handle_existing_file(self):
        
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

from .farm_summary import FarmSummary
from .soil_summary import SoilSummary
