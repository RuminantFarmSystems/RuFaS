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
import os

#-------------------------------------------------------------------------------
# Class: OutputHandler
#        Contains every all the information printed in a yearly report
#        Information is flushed at the beginning of every year
#-------------------------------------------------------------------------------
class OutputHandler():

    def __init__(self):

        self.report_handlers = {'animal_milk': AnimalMilk(),
                                'forage': Forage(),
                                'grain': Grain(),
                                'carbon_loss': CarbonLoss(),
                                'nitrogen_loss': NitrogenLoss(),
                                'phosphorus_loss': PhosphorusLoss(),
                                'soil_Summary': SoilSummary()}

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
# Class: ReportHandler
#        Contains every all the information printed in a yearly report
#        Information is flushed at the beginning of every year
#-------------------------------------------------------------------------------
class ReportHandler():

    def __init__(self, reportName, fName):

        self.active = True
        self.reportName = reportName
        self.fName = fName
        self.path = Path("./Outputs/" + self.fName)

    #---------------------------------------------------------------------------
    # Function: set_fName
    #           Adds a suffix of "_Iteration_i_" to the end of the output file
    #           name where i is the iteration number
    # Parameters: i - iteration number
    #---------------------------------------------------------------------------
    def set_fName(self, fName):
        self.fName = fName
        self.path = Path("./Outputs/" + self.fName)

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
            newfName = self.fName[:index] + "_Iteration_1_" + self.fName[index:]

        # For other iterations, replace only iteration number
        else:
            index = self.fName.rfind(str(i - 1))
            newfName = self.fName[:index] + str(i) + self.fName [index + 1:]

        self.set_fName(newfName)


from .animal_milk import AnimalMilk
from .forage import Forage
from .grain import Grain
from .carbon_loss import CarbonLoss
from .nitrogen_loss import NitrogenLoss
from .phosphorus_loss import PhosphorusLoss
from .soil_summary import SoilSummary
