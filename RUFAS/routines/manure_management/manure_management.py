"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
            Sadman Chowdhury, skc86@cornell.edu 
"""
from pprint import pprint
from typing import Dict, List

from RUFAS.routines.animal.animal_management import AnimalManagement
# TODO: figure out how to connect to csv values
from RUFAS.routines.manure_management.data_models.daily_variables import DailyVariables
from RUFAS.routines.manure_management.data_models.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_factory import ManureHandlerFactory
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.base_separator import BaseSeparator
from RUFAS.routines.manure_management.manure_separators.manure_separator_factory import ManureSeparatorFactory
from RUFAS.routines.manure_management.output.manure_management_output import ManureManagementOutput
from RUFAS.routines.manure_management.reception_pits.base_reception_pit import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_factory import ReceptionPitFactory
from RUFAS.routines.manure_management.treatments.treatment_classes.base_treatment import BaseTreatment
from RUFAS.routines.manure_management.treatments.treatment_factory import TreatmentFactory


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
        self.reception_pits: Dict[int, BaseReceptionPit] = {}
        self.manure_separators: Dict[int, BaseSeparator] = {}
        self.treatments: Dict[int, BaseTreatment] = {}

        self.daily_vars = DailyVariables()
        self.annual_vars = DailyVariables()
        self.total_vars = DailyVariables()

        self.all_data: Dict[int, List[List]] = {}

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
        if item in ['pens', 'storage', 'separators']:
            return {}
        obj = self.annual_vars if 'annual' in item else self.daily_vars
        if item in vars(obj):
            return getattr(obj, item)
        return 0

    def build(self, animal_management: SimpleAnimalManagement):
        """Set up all the components."""

        for pen in animal_management.all_pens:
            self.manure_handlers[pen.id] = ManureHandlerFactory.get_instance(pen=pen)

            # Reception pits are optional and take value of None when absent.
            # Reception pits and separators are either both present or both absent.
            self.reception_pits[pen.id] = \
                ReceptionPitFactory.get_instance(pen=pen, manure_handler=self.manure_handlers[pen.id])

            # Separators are optional and take value of None when absent.
            self.manure_separators[pen.id] = \
                ManureSeparatorFactory.get_instance(pen=pen, reception_pit=self.reception_pits[pen.id])

            self.treatments[pen.id] = TreatmentFactory.get_instance(
                pen=pen,
                manure_handler=self.manure_handlers[pen.id],
                manure_separator=self.manure_separators[pen.id]
            )

            self.all_data[pen.id] = []

    def update(self, animal_management: SimpleAnimalManagement):
        """
        Update all the components and subcomponents given
        new information from Animal Management.

        """
        # Only manure handlers need a pen when performing an update
        # The remaining downstream components can just extract whatever data they
        # need from the immediate upstream component.
        for pen in animal_management.all_pens:
            self.manure_handlers[pen.id].update(pen)
            pprint(f'manure handler for pen {pen.id}: {self.manure_handlers[pen.id].daily_output}')

            self.reception_pits[pen.id].update()
            # print(f'reception pit for pen {pen.id}: {self.reception_pits[pen.id].daily_vars}')

            self.manure_separators[pen.id].update()
            # print(f'manure separator for pen {pen.id}: {self.manure_separators[pen.id].daily_vars}')

            self.treatments[pen.id].update()
            # print(f'storage option for pen {pen.id}: {self.treatments[pen.id].daily_vars}')

            pen_daily_data = [
                self.reception_pits[pen.id].daily_vars,
                self.manure_separators[pen.id].daily_vars,
                self.treatments[pen.id].daily_vars
            ]

            self.all_data[pen.id].append(pen_daily_data)

            print()

    # TODO: Check logic
    def summarize_manure_management(self):
        # self.summarize_manure_handlers()
        # self.summarize_manure_separators()
        # self.summarize_reception_pits()
        self.summarize_treatments()

        print(f'Daily: {self.daily_vars}')

    # TODO: Check logic
    def summarize_manure_handlers(self):
        for handler in self.manure_handlers.values():
            h = handler.daily_vars
            self.daily_vars += DailyVariables(
                raw_manure=h.raw_manure,
                TS_loss=h.TS_loss,
                VS_loss=h.VS_loss
            )

    def summarize_manure_separators(self):
        for separator in self.manure_separators.values():
            s = separator.daily_vars
            self.daily_vars += DailyVariables(
                TS_DM_effluent=s.TS_DM_effluent
            )

    # TODO: Check logic
    def summarize_reception_pits(self):
        for reception_pit in self.reception_pits.values():
            r = reception_pit.daily_vars
            self.daily_vars += DailyVariables(
                TS=r.TS,
                VS=r.VS,
                N=r.N,
                P=r.P,
                K=r.K,
                CH4_emissions=r.CH4,
                WIP=r.WIP,
                WOP=r.WOP
            )

    # TODO: Check logic
    def summarize_treatments(self):
        for storage in self.treatments.values():
            s = storage.daily_vars
            self.daily_vars += DailyVariables(
                TS=s.TS,
                VS=s.VS,
                N=s.N,
                P=s.P,
                K=s.K,
                TS_liquid=s.TS_liquid,
                VS_liquid=s.VS_liquid,
                N_liquid=s.N_liquid,
                P_liquid=s.P_liquid,
                K_liquid=s.K_liquid,
                CH4_emissions=s.CH4
            )

    def summarize_annual_variables(self):
        self.annual_vars += self.daily_vars
        print(f'Annual: {self.annual_vars}')

    # TODO: Check logic
    def summarize_total_variables(self):
        self.total_vars += self.daily_vars
        print(f'Total: {self.total_vars}')

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
        for separator in self.manure_separators.values():
            separator.reset_daily_variables()
        for reception_pit in self.reception_pits.values():
            reception_pit.reset_daily_variables()
        for storage_option in self.treatments.values():
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
