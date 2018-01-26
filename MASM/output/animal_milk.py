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

from .output_handler import ReportHandler

#-------------------------------------------------------------------------------
# Class: SampleOutput1
#        
#-------------------------------------------------------------------------------
class AnimalMilk(ReportHandler):
    
    def __init__(self):
             
        super().__init__("Animal & Milk", "Default_Animal_Milk_Report.txt")
                 
        #
        # Yearly Output
        # Single values
        #
        self.sampleYearly = None
        
        #
        # Monthly Outputs
        # 1D Lists [m]
        #
        self.sampleMonthly = [None]*12
        
        #
        # Daily Outputs
        # 2D Lists [m][d]
        #
        self.sampleDaily = [[None]*31]*12
        
    #---------------------------------------------------------------------------
    # Function: compile_annual_report
    #           Appends the annual report to the output file
    # Parameters: t - time object
    #---------------------------------------------------------------------------
    def compile_annual_report(self, t):

        rpt = self.reportName + " Report for year: {}\n".format(t.y)
        
        return rpt
    
    #---------------------------------------------------------------------------
    # Function: annual_flush
    #           Sets all of the values in the output object to the default value
    #---------------------------------------------------------------------------
    def annual_flush(self):
        pass
    