"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
            Sadman Chowdhury, skc86@cornell.edu 
"""
import collections
from dataclasses import asdict
from typing import Dict, List, Tuple
import pandas as pd
from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler, ManureHandlerFactory
# TODO: figure out how to connect to csv values
from RUFAS.routines.manure_management.manure_handlers.manure_handler_output import ManureHandlerOutput
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseSeparator, \
    ManureSeparatorFactory
from RUFAS.routines.manure_management.manure_separators.manure_separator_output import ManureSeparatorOutput
from RUFAS.routines.manure_management.misc.daily_variables import DailyVariables
from RUFAS.routines.manure_management.misc.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.output.manure_management_output import ManureManagementOutput
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit, ReceptionPitFactory
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.treatments.treatment_classes import BaseTreatment, TreatmentFactory
from RUFAS.routines.manure_management.treatments.treatment_output import TreatmentOutput

DailyOutputType = Tuple[ManureHandlerOutput, ReceptionPitOutput, ManureSeparatorOutput, TreatmentOutput]


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

        self.all_data: Dict[int, List[DailyOutputType]] = {}
        self.update_count = 0

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
        if item in ['pens', 'storage', 'separators']:
            return {}
        obj = self.annual_vars if 'annual' in item else self.daily_vars
        if item in vars(obj):
            return getattr(obj, item)
        return 0

    @property
    def all_output_data(self) -> Dict[int, List[DailyOutputType]]:
        """
        Return all the data generated during the whole simulation.

        Structure of the returned data dictionary:
            key: pen.id
            value: list of 4-tuples
                Each of these 4-tuples contains daily output from
                manure handler, reception pit, manure separator, and treatment.

        For example, if there are 10 pens and the simulation is run for 365 days,
        then the data dictionary should have 10 keys that correspond to 10 pen ids
        and each key is associated with a list of 365 elements where
        each element is a tuple of size 4.

        """
        return self.all_data

    def build(self, animal_management: SimpleAnimalManagement):
        """Set up all the components."""

        for pen in animal_management.all_pens:
            self.manure_handlers[pen.id] = ManureHandlerFactory.get_instance(pen=pen)

            self.reception_pits[pen.id] = \
                ReceptionPitFactory.get_instance(manure_handler=self.manure_handlers[pen.id])

            self.manure_separators[pen.id] = \
                ManureSeparatorFactory.get_instance(pen=pen, reception_pit=self.reception_pits[pen.id])

            # TODO: When implementing treatments, check to see if they need to
            # know about both handler and separator
            # To access the manure handler, either pass it in directly or use chaining
            # as follows: manure_separator.reception_pit.manure_handler.some_attr_or_method
            self.treatments[pen.id] = TreatmentFactory.get_instance(
                    pen=pen,
                    manure_handler=self.manure_handlers[pen.id],
                    manure_separator=self.manure_separators[pen.id]
            )

            self.all_data[pen.id]: List[DailyOutputType] = []

    def update(self, animal_management: SimpleAnimalManagement):
        """
        Update all the components and subcomponents given
        new information from Animal Management.

        """
        self.update_count += 1
        print(f'Day {self.update_count}=======================================')

        for pen in animal_management.all_pens:
            print(f'Pen {pen.id}----------------------------------------------')
            manure_handler_daily_output = self.manure_handlers[pen.id].update(pen)
            print(f'manure_handler_daily_output: \n{manure_handler_daily_output}\n')

            reception_pit_daily_output = self.reception_pits[pen.id].update()
            print(f'reception_pit_daily_output: \n{reception_pit_daily_output}\n')

            manure_separator_daily_output = self.manure_separators[pen.id].update(pen)
            print(f'manure_separator_daily_output: \n{manure_separator_daily_output}\n')

            treatment_daily_output = self.treatments[pen.id].update(pen)
            print(f'treatment_daily_output: \n{treatment_daily_output}\n')

            pen_daily_update_data = (
                manure_handler_daily_output,
                reception_pit_daily_output,
                manure_separator_daily_output,
                treatment_daily_output
            )

            self.all_data[pen.id].append(pen_daily_update_data)

            print()

        self.export_output_to_csv()

    def export_output_to_csv(self):
        print(f'Exporting to csv')
        pen_ids = []
        sim_days = []
        manure_handler_cols = collections.defaultdict(list)
        reception_pit_cols = collections.defaultdict(list)
        manure_separator_cols = collections.defaultdict(list)
        treatment_cols = collections.defaultdict(list)
        cols_list = [manure_handler_cols, reception_pit_cols, manure_separator_cols,
                     treatment_cols]
        for pen_id in sorted(self.all_data.keys()):
            for idx, data in enumerate(self.all_data[pen_id]):
                pen_ids.append(pen_id)
                sim_days.append(idx + 1)
                for obj, cols, prefix in zip(data, cols_list,
                                             ['handler_', 'rp_', 'sep_', 'tx_']):
                    for k, v in asdict(obj).items():
                        cols[prefix + k].append(v)
        d = {
            'pen_id': pen_ids,
            'sim_day': sim_days,
            **manure_handler_cols,
            **reception_pit_cols,
            **manure_separator_cols,
            **treatment_cols
        }
        df = pd.DataFrame(data=d)
        df.to_csv('RUFAS/routines/manure_management/output/manure_management_output.csv',
                  index=False)

    def summarize_manure_management(self):
        pass

    def summarize_annual_variables(self):
        pass

    def summarize_total_variables(self):
        pass

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
