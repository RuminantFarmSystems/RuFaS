"""
RUFAS: Ruminant Farm Systems Model
File name: base_report_handler.py

Author(s): Kass Chupongstimun, kass_c@hotmail.com

Description: Abstract class defining a basic report.
"""

from pathlib import Path
from abc import ABC, abstractmethod

from RUFAS import util


class BaseReportHandler(ABC):
    """
    Contains an interface for report handlers, each output report
    file implements this abstract class.
    When a Report Handler object that implements this abstract class is
    instantiated, set_properties() is called to set the properties that all
    report handlers must contain.
    """

    # Private Property
    # Default directory for output report files
    # overwritten by the directory given in json file
    __output_dir = util.get_base_dir() / Path("Outputs/Default_Output_Dir")

    def set_properties(self, data, field_name):
        """
        Sets the properties of each report handler initialized.

        This is called in the report handler's __init__() method, and takes in
        the data passed to it and assigns the properties below.
        """

        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.display_graphics = data['display_graphics']
        self.report_name = data['report_name']
        self.file_name = data['file_name']
        if field_name != 'null':
            self.file_name = field_name + '/' + self.file_name

    def get_fPath(self):
        """
        Description:
            Gets the path to which the report handler will write the report.

        Returns:
            Path: path to which the report will be written.
        """
        return BaseReportHandler.__output_dir / self.file_name

    @classmethod
    def set_dir(cls, new_dir):
        """Sets the base path to write the output report files to"""
        cls.__output_dir = new_dir

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
    def produce_report_graphics(self, is_final): raise NotImplementedError()
