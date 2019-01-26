################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: base_report_handler.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from pathlib import Path
from abc import ABC, abstractmethod

from RUFAS import util

#-------------------------------------------------------------------------------
# Abstract Class: BaseReportHandler
#-------------------------------------------------------------------------------
class BaseReportHandler(ABC):
    '''
    Contains an interface for report handlers, each output report
    file implements this abstract class.
    When a Report Handler object that implements this abstract class is
    instantiated, set_properties() is called to set the properties that all
    report handlers must contain.
    '''

    # Private Property
    # Default directory for output report files
    # overwritten by the directory given in json file
    __output_dir = util.get_base_dir() / Path("Outputs/Default_Output_Dir")

    #---------------------------------------------------------------------------
    # Method: set_properties
    #---------------------------------------------------------------------------
    def set_properties(self, data):
        '''Sets the properties of each report handler initialized.

        This is called in the report handler's __init__() method, and takes in
        the data passed to it and assigns the properties below.
        '''

        self.active = data['active']
        self.report_name = data['report_name']
        self.fName = data['file_name']

    #---------------------------------------------------------------------------
    # Method: get_fPath
    #---------------------------------------------------------------------------
    def get_fPath(self):
        '''Gets the path to which the report handler will write the report.

        Returns:
            Path: path to which the report will be written.
        '''
        return BaseReportHandler.__output_dir / self.fName

    #---------------------------------------------------------------------------
    # Class Method: set_dir
    #---------------------------------------------------------------------------
    @classmethod
    def set_dir(cls, new_dir):
        '''Sets the base path to write the output report files to'''
        cls.__output_dir = new_dir

    #---------------------------------------------------------------------------
    # Abstract Methods
    #---------------------------------------------------------------------------
    @abstractmethod
    def initialize(self): raise NotImplementedError()
    @abstractmethod
    def daily_update(self): raise NotImplementedError()
    @abstractmethod
    def annual_update(self): raise NotImplementedError()
    @abstractmethod
    def write_annual_report(self): raise NotImplementedError()
    @abstractmethod
    def annual_flush(self): raise NotImplementedError()
