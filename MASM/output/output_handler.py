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
import os

#-------------------------------------------------------------------------------
# Class: OutputHandler
#        Contains every all the information printed in a yearly report
#        Information is flushed at the beginning of every year
#-------------------------------------------------------------------------------
class OutputHandler():

    def __init__(self):

        self.report_handlers = {
                                'soil_summary': SoilSummary()
                                }
        
    #---------------------------------------------------------------------------
    # Function: write_annual_reports
    #
    # Parameters: y - year of the report to be appended
    #---------------------------------------------------------------------------
    def write_annual_reports(self, y):

        for _, handler in self.report_handlers.items():
            if handler.active:
                mode = 'a+' if os.path.exists(handler.path) else 'w+'
                if isinstance(handler, SoilSummary):
                    handler.compile_annual_report()
                else:
                    with open(handler.path, mode) as f:
                        f.write(handler.compile_annual_report(y))

    #---------------------------------------------------------------------------
    # Function: update_fNames
    #           Adds a suffix of "_Iteration_i_" to the end of the output file
    #           name where i is the iteration number
    # Parameters: i - iteration number
    #---------------------------------------------------------------------------
    def update_fNames(self, i):

        for _, handler in self.report_handlers.items():
            if handler.active:
                handler.update_fName(i)

    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the reports in the output object to the default report
    #---------------------------------------------------------------------------
    def annual_flush(self):

        for _, handler in self.report_handlers.items():
            if handler.active:
                handler.annual_flush()

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
        self.path = Path("./Outputs/" + self.fName)

    #---------------------------------------------------------------------------
    # Function: get_fPath
    #           Gets the path to which the report handler will write the report
    # Returns: A path object to which the report will be writtens
    #---------------------------------------------------------------------------        
    def get_fPath(self):
        return Path(self.path + self.fName)

    #---------------------------------------------------------------------------
    # Function: update_fName
    #           Adds a suffix of "_Iteration_i_" to the end of the output file
    #           name where i is the iteration number
    # Parameters: i - iteration number
    #---------------------------------------------------------------------------
    def update_fName(self, i):

        # For first iteration
        if i == 1:
            index = self.fName.index('.')
            self.fname = self.fName[:index] + "_Iteration_1_" + self.fName[index:]

        # For other iterations, replace only iteration number
        else:
            index = self.fName.rfind(str(i - 1))
            self.fname = self.fName[:index] + str(i) + self.fName [index + 1:]
            
    #---------------------------------------------------------------------------
    # Abstract Methods
    #---------------------------------------------------------------------------
    @abstractmethod
    def daily_update(self): pass
    @abstractmethod
    def compile_annual_report(self): pass
    @abstractmethod
    def annual_flush(self): pass


from .soil_summary import SoilSummary
