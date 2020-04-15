"""
RUFAS: Ruminant Farm Systems Model
File name: base_report_handler.py

Author(s): Kass Chupongstimun, kass_c@hotmail.com

Description: Abstract class defining a basic report.
"""

from pathlib import Path
from abc import ABC, abstractmethod


class BaseReportHandler(ABC):
    """
    Contains an interface for report handlers, each output report
    file implements this abstract class.
    When a Report Handler object that implements this abstract class is
    instantiated, set_properties() is called to set the properties that all
    report handlers must contain.
    """
    def __init__(self, data):
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.report_name = data['report_name']
        self.file_name = data['file_name']
        self.annual_file_name = self.file_name.split('.csv')[0] + '_annual.csv'
        self.output_dir = Path('')
        self.diagnostic_dir = Path('')

    def get_fPath(self):
        """
        Description:
            Gets the path to which the report handler will write the report.

        Returns:
            Path: path to which the report will be written.
        """
        return Path(self.output_dir) / Path(self.file_name)

    # abstract methods defined in each report
    @abstractmethod
    def write_headers(self, output_csv, variables): raise NotImplementedError()

    @abstractmethod
    def initialize(self, state_info): raise NotImplementedError()

    @abstractmethod
    def daily_update(self, state_info, weather, time): raise NotImplementedError()

    @abstractmethod
    def annual_update(self, state_info, weather, time): raise NotImplementedError()

    @abstractmethod
    def write_annual_report(self): raise NotImplementedError()

    @abstractmethod
    def annual_flush(self): raise NotImplementedError()

    @abstractmethod
    def produce_report_graphics(self): raise NotImplementedError()
