"""
RUFAS: Ruminant Farm Systems Model
File name: output.py
Description: Contains the definition of the OutputHandler object
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
import shutil
import sys
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
                        'feed_storage_report': FeedStorageReport(data['feed_storage_report'], state),
                        'manure_storage_report': ManureStorageReport(data['manure_storage_report'], state),
                        'custom_report': CustomReport(data['custom_report']),
                        'fields_report': FieldsReport(data['fields_report'], state),
                        'pens_report': PensReport(data['pens_report'], state),
                        'mass_balance': MassBalanceReport(data['mass_balance']),
                        'life_cycle_report': LifeCycleReport(data['life_cycle_report']),
                        }

    def initialize_dir(self, csv_dir, graphic_dir):
        """
        If a directory of the same name exists, it and its contents are deleted,
        then a directory for each output report is created.
        Sets output file path for all reports through the class attribute of the
        BaseReportHandler class.

        Args:
            csv_dir (Path): The path to the directory that will store all
                output report csv files.
            graphic_dir (Path): The path to the directory that will store
                all the output report graphics
        """
        # Initialize path for reports
        base_csv_dir = util.get_base_dir() / csv_dir
        base_graphic_dir = util.get_base_dir() / graphic_dir

        # Delete directory if previously exists
        if base_csv_dir.exists():
            shutil.rmtree(base_csv_dir)
        if base_graphic_dir.exists():
            shutil.rmtree(base_graphic_dir)

        base_csv_dir.mkdir(exist_ok=True, parents=False)
        base_graphic_dir.mkdir(exist_ok=True, parents=False)

        for report in self.reports.values():
            report.initialize_dir(base_csv_dir, base_graphic_dir)

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
        report_count = 0
        for report_name in self.reports:
            case = report_count % 4
            if case == 0:
                sys.stdout.write("—")
            elif case == 1:
                sys.stdout.write("\\")
            elif case == 2:
                sys.stdout.write("|")
            else:
                sys.stdout.write("/")
                
            report = self.reports[report_name]
            report.produce_report_graphics()
            sys.stdout.write("\b")
            report_count += 1

    def finalize(self, state, weather, time):
        for report_name in self.reports:
            report = self.reports[report_name]
            report.finalize(state, weather, time)
