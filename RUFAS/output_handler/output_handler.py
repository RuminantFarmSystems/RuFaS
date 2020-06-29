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
    """Handles all output_handler related interactions.

    Contains a list of all the report handlers, which handles all output_handler-related
    functionality. This object is the (only) bridge between the simulation
    engine and the output_handler routines.

    Output values are updated at the end of each day, and the each report is
    printed at the end of each year, using the values (that are written daily)
    for the year period and also any yearly output_handler values. After each the report
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

    def initialize_csv_dir(self, csv_dir):
        """
        If a directory of the same name exists, it and its contents are deleted,
        then a directory for each output_handler report is created.
        Sets output_handler file path for all reports through the class attribute of the
        BaseReportHandler class.

        Args:
            csv_dir (Path): The path to the directory that will store all
                output_handler report files.
        """

        # Initialize path for reports
        csv_dir = util.get_base_dir() / csv_dir

        # Delete directory if previously exists
        if csv_dir.exists():
            shutil.rmtree(csv_dir)

        csv_dir.mkdir(exist_ok=True, parents=False)

        # TODO: Would really love to generalize directory creation for nested reports
        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                report.csv_dir = csv_dir / report_name
                report.csv_dir.mkdir(exist_ok=True, parents=False)
                report.initialize_csv_dir()

    def initialize_graphic_dir(self, graphic_dir):
        graphic_dir = util.get_base_dir() / graphic_dir

        if graphic_dir.exists():
            shutil.rmtree(graphic_dir)

        graphic_dir.mkdir(exist_ok=True, parents=False)

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_graphics:
                report.graphic_dir = graphic_dir / report_name
                report.graphic_dir.mkdir(exist_ok=True, parents=False)
                report.initialize_graphic_dir()

    def initialize_reports(self):
        """Transfer needed (initial) data from state to report handlers."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if not report.produce_csv and report.produce_graphics:
                print("Warning: Cannot produce graphics_1 for inactive report:", report.report_name,
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
        """Updates the report handler with annual output_handler values."""

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
        """Sets all of the reports in the output_handler object to the default."""

        for report_name in self.reports:
            report = self.reports[report_name]
            if report.produce_csv:
                report.annual_flush()

    def produce_graphics(self):
        for report_name in self.reports:
            report = self.reports[report_name]
            report.produce_report_graphics()
