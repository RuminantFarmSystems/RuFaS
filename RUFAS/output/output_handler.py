################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: output_handler.py
Description: Contains the definition of the OutputHandler object
Author(s): Kass Chupongstimun, kass_c@hotmail.com
"""
################################################################################
import shutil
from pathlib import Path

from RUFAS import util
from RUFAS.output.report_handler import BaseReportHandler

#
# Import report handlers here
#
from RUFAS.output.ration_report import RationReport
from RUFAS.output.feed_storage import FeedStorage
from RUFAS.output.field_summary import FieldSummary


# -------------------------------------------------------------------------------
# Class: OutputHandler
# -------------------------------------------------------------------------------


class OutputHandler:
    """Handles all output related interactions.

    Contains a list of all the report handlers, which handles all output-related
    functionalities. This object is the (only) bridge between the simulation
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
                        #'farm_summary': FarmSummary(data['farm_summary']),
                        'ration_report': RationReport(data['ration_report']),
                        'feed_storage': FeedStorage(data['feed_storage']),
                        }
        for field in state.fields:
            self.reports[field.field_name] = FieldSummary(field.field_name, data['field_summary'])

        self.final = False

    # ---------------------------------------------------------------------------
    # Method: initialize_output_dir
    # ---------------------------------------------------------------------------
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
            for output in output_dir.iterdir():
                if output.is_file():
                    output.unlink()
                else:
                    for file in output.iterdir():
                        file.unlink()
                    output.rmdir()
            output_dir.rmdir()

        output_dir.mkdir(exist_ok=True, parents=False)
        BaseReportHandler.set_dir(output_dir)

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.report_name.split('_')[0] == 'field':
                report_dir = util.get_base_dir() / output_dir / reportName
                report_dir.mkdir(exist_ok=True, parents=False)

    # ---------------------------------------------------------------------------
    # Method: initialize_diagnostic_dir
    # ---------------------------------------------------------------------------
    def initialize_diagnostic_dir(self, diagnostic_dir):
        diagnostic_dir = util.get_base_dir() / diagnostic_dir

        if diagnostic_dir.exists():
            for file in diagnostic_dir.iterdir():
                shutil.rmtree(file)
            diagnostic_dir.rmdir()

        diagnostic_dir.mkdir(exist_ok=True, parents=False)

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.produce_graphics:
                report_dir = util.get_base_dir() / diagnostic_dir / reportName
                report_dir.mkdir(exist_ok=True, parents=False)
                if report.report_name.split('_')[0] == 'field':
                    report.initialize_field_dir(report_dir)

    # ---------------------------------------------------------------------------
    # Method: initialize_reports
    # ---------------------------------------------------------------------------
    def initialize_reports(self, state):
        """Transfer needed (initial) data from state to report handlers."""

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.active:
                report.initialize(state)

    # ---------------------------------------------------------------------------
    # Method: daily_update
    # ---------------------------------------------------------------------------
    def daily_update(self, state, weather, time):
        """Updates the report handler with new daily values."""

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.active:
                report.daily_update(state, weather, time)

    # ---------------------------------------------------------------------------
    # Method: annual_update
    # ---------------------------------------------------------------------------
    def annual_updates(self, state, weather, time):
        """Updates the report handler with anuual output values."""

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.active:
                report.annual_update(state, weather, time)

    # ---------------------------------------------------------------------------
    # Method: write_annual_reports
    # ---------------------------------------------------------------------------
    def write_annual_reports(self):
        """Prints the annual report to file for all reports."""

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.active:
                report.write_annual_report()

    # ---------------------------------------------------------------------------
    # Method: annual_flush
    # ---------------------------------------------------------------------------s
    def annual_flushes(self):
        """Sets all of the reports in the output object to the default."""

        for reportName in self.reports:
            report = self.reports[reportName]
            if report.active:
                report.annual_flush()

    # ---------------------------------------------------------------------------
    # Method: produce_data_analysis
    # ---------------------------------------------------------------------------
    def produce_graphics(self):
        counter = 0
        for reportName in self.reports:
            report = self.reports[reportName]

            # if report.produce_graphics:
            if counter == len(self.reports) - 1:
                self.final = True
            report.produce_report_graphics(self.final)
            counter += 1
