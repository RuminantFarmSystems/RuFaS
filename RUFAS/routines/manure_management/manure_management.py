"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
            Sadman Chowdhury, skc86@cornell.edu 
"""
import collections
import json
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler, ManureHandlerFactory
from RUFAS.routines.manure_management.manure_handlers.manure_handler_output import ManureHandlerOutput
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseManureSeparator, \
    ManureSeparatorFactory
from RUFAS.routines.manure_management.manure_separators.manure_separator_output import ManureSeparatorOutput
from RUFAS.routines.manure_management.misc.daily_variables import DailyVariables
from RUFAS.routines.manure_management.misc.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.misc.units import Units
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit, ReceptionPitFactory
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.manure_treatments.treatment_classes import BaseManureTreatment, TreatmentFactory
from RUFAS.routines.manure_management.manure_treatments.treatment_output import TreatmentOutput
from RUFAS.weather import Weather
from RUFAS.time import Time

DailyOutputType = Tuple[SimplePen,
                        ManureHandlerOutput,
                        ReceptionPitOutput,
                        ManureSeparatorOutput,
                        TreatmentOutput]


class ManureManagement:
    """A driver class for the manure module

    Notes:
        This class should replace the `ManureStorage` class used in
        `classes.py` and `simulation_engine.py` and
        `manure_application.py`.

    """

    def __init__(self, animal_management: AnimalManagement, weather: Weather, time: Time):
        self.manure_handlers: Dict[int, BaseManureHandler] = {}
        self.reception_pits: Dict[int, BaseReceptionPit] = {}
        self.manure_separators: Dict[int, BaseManureSeparator] = {}
        self.treatments: Dict[int, BaseManureTreatment] = {}

        self.weather = weather
        self.time = time
        self.all_data: Dict[int, List[DailyOutputType]] = {}
        self.df = None

        self.daily_vars = DailyVariables()
        self.annual_vars = DailyVariables()
        self.total_vars = DailyVariables()

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
            self.manure_handlers[pen.id] = ManureHandlerFactory.get_instance(
                    pen=pen)

            self.reception_pits[pen.id] = \
                ReceptionPitFactory.get_instance(
                        manure_handler=self.manure_handlers[pen.id])

            self.manure_separators[pen.id] = \
                ManureSeparatorFactory.get_instance(
                        pen=pen, reception_pit=self.reception_pits[pen.id])

            self.treatments[pen.id] = TreatmentFactory.get_instance(
                    pen=pen,
                    manure_separator=self.manure_separators[pen.id],
                    weather=self.weather,
                    time=self.time,
            )

            self.all_data[pen.id]: List[DailyOutputType] = []

    def update(self, animal_management: SimpleAnimalManagement):
        """
        Update all the components and subcomponents given
        new information from Animal Management.

        """
        print(f'Day {animal_management.sim_day}=======================================')

        for pen in animal_management.all_pens:
            print(f'Pen {pen.id}----------------------------------------------')
            manure_handler_daily_output = self.manure_handlers[pen.id].update(pen)
            reception_pit_daily_output = self.reception_pits[pen.id].update()
            manure_separator_daily_output = self.manure_separators[pen.id].update()
            treatment_daily_output = self.treatments[pen.id].update()

            pen_daily_update_data = (
                pen,
                manure_handler_daily_output,
                reception_pit_daily_output,
                manure_separator_daily_output,
                treatment_daily_output
            )
            self.all_data[pen.id].append(pen_daily_update_data)

        self.update_last_output_to_df()
        self.export_output_to_csv()
        self.export_output_to_json()

    @staticmethod
    def append_daily_data(output_obj, prefix: str, cols: Dict):
        """

        Args:
            output_obj: A dataclass object
            prefix: prepend each column name with this prefix
            cols: A dictionary whose key is column name and value is a list of values

        Returns:

        """
        delimiter = '__'
        for variable, value in asdict(output_obj).items():
            key = prefix + delimiter + variable
            if variable in vars(Units):
                key += delimiter + vars(Units)[variable]
            cols[key].append(round(value, 2))

    def update_last_output_to_df(self):
        pen_ids: List[int] = []
        sim_days: List[int] = []
        num_animals: List[int] = []
        animal_types: List[str] = []
        housing_types: List[str] = []
        bedding_types: List[str] = []
        handler_types: List[str] = []
        separator_types: List[str] = []
        treatment_types: List[str] = []

        manure_cols = collections.defaultdict(list)
        manure_handler_cols = collections.defaultdict(list)
        reception_pit_cols = collections.defaultdict(list)
        manure_separator_cols = collections.defaultdict(list)
        treatment_cols = collections.defaultdict(list)
        for pen_id in sorted(self.all_data.keys()):
            idx = len(self.all_data[pen_id])
            latest_data = self.all_data[pen_id][-1]
            pen_ids.append(pen_id)
            sim_days.append(idx)
            pen, *outputs = latest_data
            manure_handler_output, reception_pit_output = outputs[:2]
            manure_separator_output, treatment_output = outputs[2:]

            num_animals.append(pen.num_animals)
            animal_types.append(
                    str(pen.classes_in_pen).strip("{}").replace("'", ""))
            housing_types.append(pen.housing_type)
            bedding_types.append(pen.bedding_type)
            handler_types.append(pen.manure_handler)
            separator_types.append(pen.manure_separator)
            treatment_types.append(pen.manure_storage)

            self.append_daily_data(pen.manure, 'manure', manure_cols)
            self.append_daily_data(manure_handler_output,
                                   'handler', manure_handler_cols)
            self.append_daily_data(reception_pit_output,
                                   'rp', reception_pit_cols)
            self.append_daily_data(
                    manure_separator_output, 'sep', manure_separator_cols)
            self.append_daily_data(treatment_output, 'tx', treatment_cols)

        d = {
            'pen_id': pen_ids,
            'sim_day': sim_days,
            'num_animals': num_animals,
            'animal_types': animal_types,
            'housing_type': housing_types,
            'bedding_type': bedding_types,
            'handler_type': handler_types,
            'separator_type': separator_types,
            'treatment_type': treatment_types,
            **manure_cols,
            **manure_handler_cols,
            **reception_pit_cols,
            **manure_separator_cols,
            **treatment_cols
        }
        temp_df = pd.DataFrame(data=d)
        if self.df is None:
            self.df = temp_df
        else:
            self.df = pd.concat([self.df, temp_df], ignore_index=True)
            self.df.reset_index()
            self.df.sort_values(by=['pen_id', 'sim_day'], inplace=True)

    def export_output_to_csv(self):
        print(f'Exporting to csv')
        current_time = datetime.now().strftime('%m_%d_%Y__%H_00')
        self.df.to_csv(f'RUFAS/routines/manure_management/output/manure_management_output_{current_time}.csv',
                       index=False)

    def export_output_to_excel(self, sheet_name='Manure_Management'):
        print(f'Exporting to Excel')
        current_time = datetime.now().strftime('%m_%d_%Y__%H_00')
        file_path = f'RUFAS/routines/manure_management/output/manure_management_output_{current_time}.xlsx'

        with pd.ExcelWriter(file_path) as writer:
            self.df.to_excel(writer, sheet_name=sheet_name, index=False)

    def export_output_to_json(self):
        print('Exporting to json')
        json_output = self.df.to_json(orient='records')
        json_parsed = json.loads(json_output)
        current_time = datetime.now().strftime('%m_%d_%Y__%H_00')
        file_path = f'RUFAS/routines/manure_management/output/manure_management_output_{current_time}.json'
        with open(file_path, 'w') as outfile:
            json.dump(json_parsed, outfile)

    def summarize_manure_management(self):
        pass

    def summarize_annual_variables(self):
        pass

    def summarize_total_variables(self):
        pass

    # TODO: Check logic
    def export_total_variables(self):
        pass

    def reset_daily_variables(self):
        pass

    def annual_reset(self):
        pass

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
