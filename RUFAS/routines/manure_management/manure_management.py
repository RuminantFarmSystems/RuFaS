"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
            Sadman Chowdhury, skc86@cornell.edu 
"""
from typing import Dict

from RUFAS.routines.animal.animal_management import AnimalManagement
# TODO figure out how to connect to csv values
from RUFAS.routines.manure_management.data_models.daily_variables import DailyVariables
from RUFAS.routines.manure_management.data_models.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_factory import ManureHandlerFactory
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.base_separator import BaseSeparator

from RUFAS.routines.manure_management.manure_separators.manure_separator_factory import ManureSeparatorFactory
from RUFAS.routines.manure_management.output.manure_management_output import ManureManagementOutput
from RUFAS.routines.manure_management.reception_pits.base_reception_pit import BaseReceptionPit
from RUFAS.routines.manure_management.storage_options.storage_option_classes.base_storage import BaseStorage
from RUFAS.routines.manure_management.storage_options.storage_option_factory import StorageOptionFactory


class ManureStorage:
    """Acts as a wrapper class for the ManureManagement class.

    Notes:
        After the references to `ManureStorage` in `simulation_engine.py`
        and `classes.py` and `manure_application.py` are changed to `ManureManagement`,
        this class should be removed.

    """

    def __init__(self, animal_management: AnimalManagement):
        self.manure_management = ManureManagement(animal_management)

    def __getattr__(self, item):
        return getattr(self.manure_management, item)

    def annual_reset(self):
        self.manure_management.annual_reset()

    def annual_mass_balance(self):
        self.manure_management.annual_mass_balance()


class ManureManagement:
    """A driver class for the manure module

    Notes:
        This class should replace the `ManureStorage` class used in
        `classes.py` and `simulation_engine.py` and
        `manure_application.py`.

    Attributes:
        manure_management_output: the final data returned by ManureManagement module.
            It is meant to be used by downstream modules (e.g., `field`).

    """

    def __init__(self, animal_management: AnimalManagement):
        self.manure_handlers: Dict[int, BaseManureHandler] = {}
        self.manure_separators: Dict[int, BaseSeparator] = {}
        self.reception_pits: Dict[int, BaseReceptionPit] = {}
        self.storage_options: Dict[int, BaseStorage] = {}

        self.daily_vars = DailyVariables()
        self.annual_vars = DailyVariables()
        self.total_vars = DailyVariables()

        self.manure_management_output = ManureManagementOutput()

        self.build(SimpleAnimalManagement(animal_management))

    def __getattr__(self, item):
        """
        Notes:
            This method is meant for those external clients (e.g.,
            `manure_application` in `field_management` package)
            that have been relying on the previous implementation.

            As soon as all those external clients agree on an export
            data model or interface that the manure module provides,
            this method will either be rewritten or removed.

        """
        if item in ['pens', 'storage']:
            return {}
        obj = self.annual_vars if 'annual' in item else self.daily_vars
        if item in vars(obj):
            return getattr(obj, item)
        return 0

    def build(self, animal_management: SimpleAnimalManagement):
        """Set up all the components."""

        for pen in animal_management.all_pens:
            self.storage_options[pen.id] = StorageOptionFactory.get_instance(pen=pen)
            self.manure_separators[pen.id] = ManureSeparatorFactory.get_instance(pen,
                                                                                 storage_option=self.storage_options[pen.id])
            # self.reception_pits[pen.id] = BaseReceptionPit(None, None, separator=self.separators[pen.id])
            # self.manure_handlers[pen.id] = ManureHandlerFactory.get_instance(pen=pen,
            #                                                                  reception_pit=self.reception_pits[
            #                                                                  pen.id])
            self.manure_handlers[pen.id] = ManureHandlerFactory.get_instance(pen=pen, reception_pit=None)

    def update(self, animal_management: SimpleAnimalManagement):
        """
        Update all the components and subcomponents given
        new information from Animal Management.

        """

        for pen in animal_management.all_pens:
            self.manure_handlers[pen.id].update(pen)
            self.manure_separators[pen.id].update(pen)
            self.storage_options[pen.id].update(pen)

        print(f'Daily: {self.daily_vars}')
        print(f'Annual: {self.annual_vars}')
        print(f'Total: {self.total_vars}')

    def summarize_manure_management(self):
        self.summarize_manure_handlers()
        self.summarize_manure_separators()
        self.summarize_reception_pits()
        self.summarize_storage_options()

    def summarize_manure_handlers(self):
        for handler in self.manure_handlers.values():
            h = handler.daily_vars
            self.daily_vars += DailyVariables(
                    raw_manure=h.raw_manure,
                    TS_loss=h.TS_loss,
                    VS_loss=h.VS_loss
            )

    def summarize_manure_separators(self):
        pass

    def summarize_reception_pits(self):
        pass

    # TODO: Check logic
    def summarize_storage_options(self):
        for storage in self.storage_options.values():
            s = storage.daily_vars
            self.daily_vars += DailyVariables(
                    CH4_emissions=s.CH4
            )

    def summarize_annual_variables(self):
        self.annual_vars += self.daily_vars

    # TODO: Check logic
    def summarize_total_variables(self):
        self.total_vars += self.daily_vars

    # TODO: Check logic
    def export_total_variables(self):
        tot = self.total_vars
        self.manure_management_output = ManureManagementOutput(
                tot_manure=tot.raw_manure,
                tot_N=tot.N,
                tot_P=tot.P,
                tot_K=tot.K,
                tot_DM=tot.TS_DM_effluent,
                WIP=tot.WIP,
                WOP=tot.WOP
        )

    # TODO: Simplify all the for-loops into one
    def reset_daily_variables(self):
        print('Reset daily variables')
        self.daily_vars = DailyVariables()
        for handler in self.manure_handlers.values():
            handler.reset_daily_variables()
        for storage_option in self.storage_options.values():
            storage_option.reset_daily_variables()

    def annual_reset(self):
        print('Annual reset===================================================')
        self.annual_vars = DailyVariables()

    # TODO: Check logic
    def annual_mass_balance(self):
        print('Annual mass balance')
        daily, annual = self.daily_vars, self.annual_vars
        manure = daily.TS + daily.TS_liquid
        annual.manure_delta = manure - annual.initial_manure
        annual.initial_manure = manure
        annual.manure_calc = sum([
            annual.manure_delta,
            annual.TS,
            annual.TS_liquid,
            annual.TS_DM_effluent,
            annual.manure_applied
        ])
        annual.manure_management_balance_difference = annual.raw_manure - annual.manure_calc
