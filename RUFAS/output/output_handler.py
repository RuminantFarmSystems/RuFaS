"""
RUFAS: Ruminant Farm Systems Model
File name: output_handler.py
Description: Contains the definition of the OutputHandler object
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
import shutil
from pathlib import Path

from RUFAS import util
from .reports import *


class OutputHandler:
    """Handles all output related interactions.

    Contains a list of all the report handlers, which handles all output-related
    functionality. This object is the (only) bridge between the simulation
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
                        'field_report': FieldReport(data['field_report']),
                        'feed_storage_report': FeedStorageReport(data['feed_storage_report']),
                        'mass_balance_report': MassBalanceReport(data['mass_balance_report']),
                        'custom_report': CustomReport(data['custom_report'])
                        }

        # TODO: move field report to loop in dj_fields
        for pen in state.animal_management.all_pens:
            self.reports['pen_' + str(pen.id)] = PenReport(data['pen_report'], pen.id)

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

        # TODO: Would really love to generalize directory creation for nested reports
        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                csv_dir = util.get_base_dir() / output_dir / report_name
                csv_dir.mkdir(exist_ok=True, parents=False)
                report.csv_dir = csv_dir
                if report_name.startswith('pen'):
                    report.initialize_pen_csv_dir(csv_dir)
                elif report_name.startswith('mass'):
                    report.initialize_mass_balance_csv_dir(csv_dir)
                elif report_name.startswith('field'):
                    report.initialize_field_csv_dir(csv_dir)

    def initialize_diagnostic_dir(self, diagnostic_dir):
        diagnostic_dir = util.get_base_dir() / diagnostic_dir

        if diagnostic_dir.exists():
            shutil.rmtree(diagnostic_dir)

        diagnostic_dir.mkdir(exist_ok=True, parents=False)

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_graphics:
                diagnostic_dir = util.get_base_dir() / diagnostic_dir / report_name
                diagnostic_dir.mkdir(exist_ok=True, parents=False)
                report.diagnostic_dir = diagnostic_dir
                if report_name.startswith('pen'):
                    report.initialize_pen_diagnostic_dir(diagnostic_dir)
                elif report_name.startswith('mass'):
                    report.initialize_mass_balance_diagnostic_dir(diagnostic_dir)
                elif report_name.startswith('field'):
                    report.initialize_field_diagnostic_dir(diagnostic_dir)

    def initialize_reports(self):
        """Transfer needed (initial) data from state to report handlers."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if not report.produce_csv and report.produce_graphics:
                print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                      ". Setting produce_graphics to False")
                report.produce_graphics = False
            if report.produce_csv:
                report.initialize()

    def daily_update(self, state, weather, time):
        """Updates the report handler with new daily values."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                report.daily_update(state, weather, time)

    def annual_updates(self, state, weather, time):
        """Updates the report handler with annual output values."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                report.annual_update(state, weather, time)

    def write_annual_reports(self):
        """Prints the annual report to file for all reports."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                report.write_annual_report()

    def annual_flushes(self):
        """Sets all of the reports in the output object to the default."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                report.annual_flush()

    def produce_graphics(self):
        for report_name in self.reports:
            report = self.reports[report_name]
            report.produce_report_graphics()
