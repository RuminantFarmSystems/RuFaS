"""
RUFAS: Ruminant Farm Systems Model
File name: output_handler.py

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: Contains the definition of the OutputHandler object
"""

import shutil
from pathlib import Path

from RUFAS import util

#
# Import report handlers here
#
from RUFAS.output.feed_storage_report import FeedStorage
from RUFAS.output.field_report import FieldSummary
from RUFAS.output.pen_report import PenReport


class OutputHandler:
    """Handles all output related interactions.

    Contains a list of all the report handlers, which handles all output-related
    functionality. This object should be the (only) bridge between the simulation
    engine and the output routines.

    Output values are updated at the end of each day, and the each report is
    printed at the end of each year, using the values (that are written daily)
    for the year period and also any yearly output values. After each the report
    for the year is printed, every single report handler object is flushed,
    leaving absolutely nothing. The report handler begins accumulating
    information again for the next year.

    We do not recommend doing any calculations inside the report handler.
    Report handlers should exist only to store RAW OUTPUT DATA. All calculations
    should be done within the routine, saved to the State object, then extracted
    from the state object to the report handler at the end of the day. However,
    it is OK to perform some calculations (it won't cause any bugs). This makes
    sense to do when you want some statistical values that aren't already
    calculated in the routine, and you do not want to mess with the routine
    directly.
    """

    def __init__(self, data, state):
        """Initializes the report handlers with the given data"""

        # Instantiate Report Handler Objects here
        self.reports = {
                        # 'farm_summary': FarmSummary(data['farm_summary']),
                        'feed_storage': FeedStorage(data['feed_storage']),
                        }

        for field in state.fields:
            self.reports[field.field_name] = FieldSummary(field.field_name, data['field_summary'])

        for pen in state.animal_management.all_pens:
            self.reports['pen_' + str(pen.id)] = PenReport(pen.id, data['pen_report'])

    def initialize_output_dir(self, output_dir):
        """
        If a directory of the same name exists, it and its contents are deleted,
        then a directory for each output report is created.
        Sets output file path for all reports through the class attribute of the
        BaseReportHandler class.

        Args:
            output_dir (Path): The path to the directory that will store all
                output report files.
        """

        # Initialize path for reports
        output_dir = util.get_base_dir() / output_dir

        # Delete directory if previously exists
        if output_dir.exists():
            shutil.rmtree(output_dir)

        output_dir.mkdir(exist_ok=True, parents=False)

        for report_name in self.reports:
            report = self.reports[report_name]
            report.output_dir = output_dir
            if report.report_name.startswith('field'):
                report.initialize_field_output_dir(output_dir)
            if report.report_name.startswith('pen'):
                report.initialize_pen_output_dir(output_dir)

    def initialize_diagnostic_dir(self, diagnostic_dir):
        """
        Description:
            If a directory of the same name exists, it and its contents are deleted,
            then a directory for each output report is created.
            Sets output file path for all diagnostics through the class attribute of the
            BaseReportHandler class.

        Args:
            diagnostic_dir (Path): The path to the directory that will store all
                output report files.
        """

        diagnostic_dir = util.get_base_dir() / diagnostic_dir

        if diagnostic_dir.exists():
            shutil.rmtree(diagnostic_dir)

        diagnostic_dir.mkdir(exist_ok=True, parents=False)

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.produce_graphics:
                report_dir = diagnostic_dir / reportName
                report_dir.mkdir(exist_ok=True, parents=False)
                report.diagnostic_dir = report_dir
                if report.report_name.split('_')[0] == 'field':
                    report.initialize_field_diagnostic_dir(report_dir)
                if report.report_name.startswith('pen'):
                    report.initialize_pen_diagnostic_dir(report_dir)

    def initialize_reports(self, state):
        """
        Description:
            Transfer needed (initial) data from state to report handlers.
        """

        for reportName in self.reports:
            report = self.reports[reportName]
            if not report.produce_csv and report.produce_graphics:
                print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                      ". Setting produce_graphics to False")
                report.produce_graphics = False
            if report.produce_csv:
                report.initialize(state)

    def daily_update(self, state, weather, time):
        """
        Description:
            Updates the report handler with new daily values.
        """

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.produce_csv:
                report.daily_update(state, weather, time)

    def annual_updates(self, state, weather, time):
        """
        Description:
            Updates the report handler with annual output values.
        """

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.produce_csv:
                report.annual_update(state, weather, time)

    def write_annual_reports(self):
        """
        Description:
            Prints the annual report to file for all reports.
        """

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.produce_csv:
                report.write_annual_report()

    def annual_flushes(self):
        """
        Description:
            Sets all of the reports in the output object to the default.
        """

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.produce_csv:
                report.annual_flush()

    def produce_graphics(self):
        """
        Description:
            Calls produce graphics for all of the reports.
        """
        for reportName in self.reports:
            report = self.reports[reportName]
            report.produce_report_graphics()
