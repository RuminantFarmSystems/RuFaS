################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# Output.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from pathlib import Path

#-------------------------------------------------------------------------------
# Class: OutputHandler
#        Contains every all the information printed in a yearly report
#        Information is flushed at the beginning of every year
#-------------------------------------------------------------------------------
class OutputHandler():
    
    def __init__(self):
    
        self.outputList = [AnimalMilk(),
                           CarbonLoss(),
                           NitrogenLoss(),
                           PhosphorusLoss()]
        
    #---------------------------------------------------------------------------
    # Function: write_annual_reports
    #           
    # Parameters: y - year of the report to be appended
    #---------------------------------------------------------------------------
    def write_annual_reports(self, y):

        for outputObject in self.outputList:
            if outputObject.active:
                with outputObject.path.open('a+') as f:
                    f.write(outputObject.compile_annual_report(y))
        
    #---------------------------------------------------------------------------
    # Function: update_fNames
    #           Adds a suffix of "_Rep_i_" to the end of the output file name
    #           where r is the iteration number
    # Parameters: i - iteration number
    #---------------------------------------------------------------------------
    def update_fNames(self, i):
        
        for outputObject in self.outputList:
            if outputObject.active:
                outputObject.update_fName(i)
            
    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):
        
        for outputObject in self.outputList:
            if outputObject.active:
                outputObject.annual_flush()

#-------------------------------------------------------------------------------
# Class: OutputObject
#        Contains every all the information printed in a yearly report
#        Information is flushed at the beginning of every year
#-------------------------------------------------------------------------------
class OutputObject():
    
    def __init__(self, outputName, fName):
        
        self.active = True
        self.outputName = outputName
        self.fName = fName
        self.path = Path("../Outputs/" + self.fName)
    
    #---------------------------------------------------------------------------
    # Function: set_fName
    #           Adds a suffix of "_Iteration_i_" to the end of the output file
    #           name where i is the iteration number
    # Parameters: i - iteration number
    #---------------------------------------------------------------------------
    def set_fName(self, fName):
        self.fName = fName
        self.path = Path("../Outputs/" + self.fName)
    
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
from .carbon_loss import CarbonLoss
from .nitrogen_loss import NitrogenLoss
from .phosphorus_loss import PhosphorusLoss