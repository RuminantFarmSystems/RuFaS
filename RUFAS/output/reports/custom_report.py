"""
RUFAS: Ruminant Farm Systems Model
File name: custom_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
from RUFAS.output.reports.base_report import BaseReport


class CustomReport(BaseReport):

    def __init__(self, data):
        super().__init__(data)
        # Output can be added in this single place in the following format:
        # 'output_name': ['variable_name', 'unit', []],
        # 'output_name' is a user defined key that will show up in outputs/graphs.
        # avoid spaces.
        # 'variable_name' is very important. This has to be a variable defined
        # and initialized in the object. If you are interested in tracking
        # a variable not defined in the class, you need to create it there
        # first. The output handler will not work if the variable is incorrect.
        # 'unit' is user defined but will, again, show up in outputs/graphs.
        # [] is an empty list

        self.daily_variables = {'year': ['time.cal_year', '', []],
                                'j_day': ['time.day', '', []],
                                }

        self.annual_variables = {'year': ['time.cal_year', '', 0]
                                 }
