################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
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

    def __init__(self):

        self.reports = {
                        'soil_summary': SoilSummary()
                        }
        
    #---------------------------------------------------------------------------
    # Function: initialize_reports
    #
    #---------------------------------------------------------------------------
    def initialize_reports(self, state):
        
        self.reports['soil_summary'].initialize(state.soil)
    
    #---------------------------------------------------------------------------
    # Function: write_annual_reports
    #
    # Parameters: y - year of the report to be appended
    #---------------------------------------------------------------------------
    def write_annual_reports(self, y):

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
                
    #---------------------------------------------------------------------------
    # Function: handle_existing_files
    #           Sets all of the reports in the output object to the default
    #---------------------------------------------------------------------------
    def handle_existing_files(self):

        for _, report in self.reports.items():
            if report.active:
                report.handle_existing_file()

#-------------------------------------------------------------------------------
# Abstract Class: ReportHandler
#        Contains every all the information printed in a yearly report
#        Information is flushed at the beginning of every year
#-------------------------------------------------------------------------------
class ReportHandler(ABC):

    def __init__(self, reportName, fName):

        self.active = True
        self.reportName = reportName
        self.fName = fName
        self.path = "./Outputs/"

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
            print("Existing {} file detected and deleted".format(self.fName))
            self.get_fPath().unlink()
            
    #---------------------------------------------------------------------------
    # Abstract Methods
    #---------------------------------------------------------------------------
    @abstractmethod
    def initialize(self): pass
    @abstractmethod
    def daily_update(self): pass
    @abstractmethod  
    def write_annual_report(self): pass
    @abstractmethod
    def annual_flush(self): pass


from .soil_summary import SoilSummary
