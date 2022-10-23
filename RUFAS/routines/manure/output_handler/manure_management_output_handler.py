import collections
from dataclasses import fields
from datetime import datetime
from typing import Dict
from typing import List
from typing import Tuple

import numpy as np
import pandas as pd

from RUFAS.routines.manure.manure.pen_manure import PenManure
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput
from RUFAS.routines.manure.units.units import Units

DailyOutputType = Tuple[ManureManagementPen,
                        ManureHandlerDailyOutput,
                        ReceptionPitDailyOutput,
                        ManureSeparatorDailyOutput,
                        ManureTreatmentDailyOutput]


class ManureManagementOutputHandler:
    def __init__(self):
        self.df = None

    @staticmethod
    def _append_daily_data(today_data,
                           data_fields,
                           accumulator: Dict[str, List[float]],
                           col_prefix: str = '',
                           delimiter: str = '') \
            -> None:
        """

        Args:
            today_data: A dataclass object
            data_fields: A list of dataclass fields
            col_prefix: prepend each column name with this prefix
            accumulator: A dictionary whose key is column name and value is a list of values
            delimiter: A delimiter to use between the prefix and the column name

        Returns:
            None

        """
        for field in data_fields:
            unit = vars(Units).get(field.name, '')
            col_name = f'{col_prefix}{delimiter}{field.name}{f"{delimiter}{unit}" if unit else ""}'
            value = getattr(today_data, field.name, np.nan)
            accumulator[col_name].append(round(value, 6))

    def append_last_output(self,
                           all_manure_management_data: Dict[int, List[DailyOutputType]],
                           simulation_day: int):
        pen_ids: List[int] = []
        sim_days: List[int] = []
        num_animals: List[int] = []
        num_cows: List[int] = []
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

        sorted_pen_ids = sorted(all_manure_management_data.keys())

        for pen_id in sorted_pen_ids:
            pen_ids.append(pen_id)
            sim_days.append(simulation_day)

            latest_data = all_manure_management_data[pen_id][-1]
            pen = latest_data[0]
            manure_handler_output = latest_data[1]
            reception_pit_output = latest_data[2]
            manure_separator_output = latest_data[3]
            treatment_output = latest_data[4]

            num_animals.append(pen.num_animals)
            num_cows.append(pen.num_cows)
            animal_types.append(
                    str(pen.classes_in_pen).strip("{}").replace("'", ""))
            housing_types.append(pen.housing_type)
            bedding_types.append(pen.bedding_type)
            handler_types.append(pen.manure_handler)
            separator_types.append(pen.manure_separator)
            treatment_types.append(pen.manure_treatment)

            delimiter = '__'
            self._append_daily_data(pen.manure, fields(PenManure),
                                    manure_cols, 'manure', delimiter)
            self._append_daily_data(manure_handler_output, fields(ManureHandlerDailyOutput),
                                    manure_handler_cols, 'handler', delimiter)
            self._append_daily_data(reception_pit_output, fields(ReceptionPitDailyOutput),
                                    reception_pit_cols, 'rp', delimiter)
            self._append_daily_data(manure_separator_output, fields(ManureSeparatorDailyOutput),
                                    manure_separator_cols, 'sep', delimiter)
            self._append_daily_data(treatment_output, fields(ManureTreatmentDailyOutput),
                                    treatment_cols, 'tx', delimiter)

        d = {
            'pen_id': pen_ids,
            'sim_day': sim_days,
            'num_animals': num_animals,
            'num_cows': num_cows,
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

    @staticmethod
    def _get_fields_of_dataclass(dataclass):
        return [field.name for field in fields(dataclass)]

    def sort_by(self, cols: List[str]):
        self.df.sort_values(by=cols, inplace=True)

    def move_columns_to_front_inplace(self, cols: List[str]):
        cols_to_move = [col for col in cols if col in self.df.columns]
        for i, col in enumerate(cols_to_move):
            self.df.insert(i, col, self.df.pop(col))

    def sort_by_pen_id_and_sim_day(self):
        self.sort_by(['pen_id', 'sim_day'])
        self.move_columns_to_front_inplace(['pen_id', 'sim_day'])

    def export_all_data_to_csv(self):
        # print(f'Exporting to csv')
        current_time = datetime.now().strftime('%m_%d_%Y__%H_00')
        self.df.to_csv(f'RUFAS/routines/manure/output/manure_management_output_{current_time}.csv',
                       index=False)
