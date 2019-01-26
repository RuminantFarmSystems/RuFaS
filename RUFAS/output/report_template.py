################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: report_template.py
Description: Gives users an idea of how to create a report in RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path
from RUFAS.output.report_handler import BaseReportHandler

#-------------------------------------------------------------------------------
# Class: Report Template
#-------------------------------------------------------------------------------
class ReportTemplate(BaseReportHandler):
    '''This serves as an example of how to print out a report in RUFAS.

    * All code here is only for mocking, adding this report to the output
      handler will cause runtime errors

    To create your own report, copy this file and perform the following steps:

    1) in the __init__() method of this class, define the values you want
       printed. Daily outputs will initially be a list of "Nones" and yearly
       outputs will simply start off as a "None".
       In the "static" section, define values that will not change, but are
       needed in the report printing. This might be constants for equations or
       unit names of the variables. For example, it could contain the list of
       headers if printing csv files and the list of units for each column.
       Please do not hard-code any values here.
       * Do not modify the line self.set_properties(data)

    2) In the get_data() method of this class, extract any other information
       your report handler depends on from the state. Think of this as an
       "initialization" of your report. Typically, this method should write to
       the variables in the "static" variables. For example, if you want the
       csv file to have the same number of columns as there is the number of
       feed types, you can extract the feed data from the state object and
       get the number of feed types from there and assign to a variable.

    3) In the daily_update() method of this class, copy values from the state
       object to variables of this object. This is for daily output values only.
       Generally, no calculations should be perform here, but it is OK to do so.
       * DO NOT MODIFY ANY VALUES OF THE STATE OBJECT HERE, COPY ONLY

    4) In the annual_update() method of this class, do the same things as you
       did for the daily update, but with annual output values.
       Performing some statistical calculations (for values that aren't
       available in the state) would make sense if you need those values.
       * DO NOT MODIFY ANY VALUES OF THE STATE OBJECT HERE, COPY ONLY

    5) In the write_annual_report() method, write your report writing routine.
       this is totally up to you to implement. The report could be in any format
       you want.

    6) In the annual_flush() method, you should reset all variables to None or
       lists of Nones. The next year will fill in the values.

    7) Import this report handler at the top of the output_handler.py file

    8) Add an instance of this report handler to the "reports" dictionary in
       the output handler object. Don't forget to also give the input json
       file the data for this report in the outputs section.
    '''

    def __init__(self, data):
        ''' Initializes an instace of the report handler.

        data contains:
            {
                "active": is this report activated?,
                "report_name": name of the report,
                "file_name": file name of the report
            }
        '''

        #
        # Sets active, report_name, f_name using data
        #
        self.set_properties(data)

        #
        # Daily Outputs
        # 1D Lists [julianDay]
        #
        self.sample_daily_output_1 = [None]*366
        self.sample_daily_output_2 = [None]*366

        #
        # Yearly Outputs
        # 1D Lists [julianDay]
        #
        self.average_val = None

        #
        # static
        #
        self.units = None

    #---------------------------------------------------------------------------
    # Method: initialize
    #---------------------------------------------------------------------------
    def initialize(self, state):
        '''Transfers the needed data from state object to the report handler.'''

        self.units = [state.dummy_object.units]
        self.num_values = [state.dummy_object.some_list.length]

    #---------------------------------------------------------------------------
    # Method: daily_update
    #---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        '''Stores the daily values that need to be printed in the report.'''

        d = time.day
        dummy_object = state.dummy_object

        # Copy daily output values here
        self.sample_daily_output_1[d] = dummy_object.some_list[0]
        self.sample_daily_output_2[d] = dummy_object.some_list[1]

    #---------------------------------------------------------------------------
    # Method: annual_update
    #---------------------------------------------------------------------------
    def annual_update(self, state, weather, time):
        '''Stores the yearly values that need to be printed in the report.'''

        dummy_object = state.dummy_object

        # Copy daily output values here
        self.average_val = dummy_object.average_val

        # perform statistical calculations here if necessary


    #---------------------------------------------------------------------------
    # Method: write_annual_report
    #---------------------------------------------------------------------------
    def write_annual_report(self, y):
        '''Appends the annual report to the output file.'''

        mode = 'a+' if self.get_fPath().exists() else 'w+'

        with self.get_fPath().open(mode) as f:
            # Write year header here

            for d in range(1, 366):
                # Write values to output file here
                pass # get rid of this pass when implemented

    #---------------------------------------------------------------------------
    # Method: annual_flush
    #---------------------------------------------------------------------------
    def annual_flush(self):
        '''Sets all of the values in the output object to the default value.'''

        self.sample_daily_output_1 = [None]*366
        self.sample_daily_output_2 = [None]*366

        self.average_val = None
