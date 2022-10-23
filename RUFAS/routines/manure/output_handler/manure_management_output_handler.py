import collections
from dataclasses import fields
from datetime import datetime
from typing import Any
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

PenDailyUpdateDataType = Tuple[ManureManagementPen,
                               ManureHandlerDailyOutput,
                               ReceptionPitDailyOutput,
                               ManureSeparatorDailyOutput,
                               ManureTreatmentDailyOutput]


class ManureManagementOutputHandler:
    def __init__(self):
        self.df = None

    @staticmethod
    def _convert_dataclass_obj_to_formatted_dict(dataclass_obj,
                                                 data_fields,
                                                 prefix: str = '',
                                                 delimiter: str = '') \
            -> Dict[str, List[Any]]:
        """Converts a dataclass object to a dictionary with formatted keys and values in lists.

        Args:
            dataclass_obj: A dataclass object
            data_fields: A list of dataclass fields
            prefix: prepend each field name with this prefix
            delimiter: A delimiter to use between the prefix and the field name

        Returns:
            A dictionary with keys formatted as
            <prefix><delimiter><field_name><delimiter><unit>. Values are stored in
            lists. This structure facilitates the conversion to a pandas dataframe.

        """
        d = collections.defaultdict(list)
        for field in data_fields:
            unit = vars(Units).get(field.name, '')
            key_name = f'{prefix}{delimiter}{field.name}{f"{delimiter}{unit}" if unit else ""}'
            value = getattr(dataclass_obj, field.name, np.nan)
            d[key_name].append(round(value, 6))
        return d

    @staticmethod
    def _process_pen(pen: ManureManagementPen):
        """Returns a dictionary of important pen attributes to be converted to dataframe.

        Args:
            pen: A ManureManagementPen object.

        Returns:
            A dictionary of important pen attributes.

        """
        return {
            'pen_id': [pen.id],
            'num_animals': [pen.num_animals],
            'num_cows': [pen.num_cows],
            'animal_types': [str(pen.classes_in_pen).strip("{}").replace("'", "")],
            'housing_type': [pen.housing_type],
            'bedding_type': [pen.bedding_type],
            'handler_type': [pen.manure_handler],
            'separator_type': [pen.manure_separator],
            'treatment_type': [pen.manure_treatment],
        }

    def _process_input_manure_data(self, manure: PenManure):
        """Returns a dictionary of important manure attributes to be converted to dataframe."""
        return self._convert_dataclass_obj_to_formatted_dict(manure, fields(PenManure), 'manure', '__')

    def _process_manure_handler_daily_output(self, manure_handler: ManureHandlerDailyOutput):
        """Returns a dictionary of manure handler daily output attributes to be converted to dataframe."""
        return self._convert_dataclass_obj_to_formatted_dict(manure_handler, fields(ManureHandlerDailyOutput),
                                                             'handler', '__')

    def _process_reception_pit_daily_output(self, reception_pit: ReceptionPitDailyOutput):
        """Returns a dictionary of reception pit daily output attributes to be converted to dataframe."""
        return self._convert_dataclass_obj_to_formatted_dict(reception_pit, fields(ReceptionPitDailyOutput), 'rp', '__')

    def _process_manure_separator_daily_output(self, manure_separator: ManureSeparatorDailyOutput):
        """Returns a dictionary of manure separator daily output attributes to be converted to dataframe."""
        return self._convert_dataclass_obj_to_formatted_dict(manure_separator, fields(ManureSeparatorDailyOutput),
                                                             'sep', '__')

    def _process_manure_treatment_daily_output(self, treatment: ManureTreatmentDailyOutput):
        """Returns a dictionary of manure treatment daily output attributes to be converted to dataframe."""
        return self._convert_dataclass_obj_to_formatted_dict(treatment, fields(ManureTreatmentDailyOutput), 'tx', '__')

    def append_daily_update_data_for_pen(self, simulation_day: int, data: PenDailyUpdateDataType) -> None:
        """Appends daily update data for a pen to the dataframe.

        Each daily update of a pen corresponds to a row in the dataframe.

        Args:
            simulation_day: The simulation day.
            data: A tuple of dataclass objects containing daily update data for a pen.

        Returns:
            None

        """
        pen, manure_handler_output, reception_pit_output, \
        manure_separator_output, treatment_output = data
        d = {
            'sim_day': [simulation_day],
            **self._process_pen(pen),
            **self._process_input_manure_data(pen.manure),
            **self._process_manure_handler_daily_output(manure_handler_output),
            **self._process_reception_pit_daily_output(reception_pit_output),
            **self._process_manure_separator_daily_output(manure_separator_output),
            **self._process_manure_treatment_daily_output(treatment_output)
        }
        self._append_df(d)

    def _append_df(self, data: Dict[str, List[Any]]) -> None:
        """Appends data to the dataframe."""
        temp_df = pd.DataFrame(data)
        if self.df is None:
            self.df = temp_df
        else:
            self.df = pd.concat([self.df, temp_df], ignore_index=True)

    def sort_by(self, cols: List[str]):
        """Sorts the dataframe by the specified columns."""
        self.df.sort_values(by=cols, inplace=True)

    def move_columns_to_front_inplace(self, cols: List[str]):
        """Moves the specified columns to the front of the dataframe."""
        cols_to_move = [col for col in cols if col in self.df.columns]
        for i, col in enumerate(cols_to_move):
            self.df.insert(i, col, self.df.pop(col))

    def sort_by_pen_id_and_sim_day(self):
        """Sorts the dataframe by pen id and simulation day."""
        self.sort_by(['pen_id', 'sim_day'])
        self.move_columns_to_front_inplace(['pen_id', 'sim_day'])

    def export_all_data_to_csv(self):
        """Exports all data to a csv file."""
        self.df.to_csv(f'RUFAS/routines/manure/output/manure_management_output_'
                       f'{self._get_current_time_str()}.csv',
                       index=False)

    @staticmethod
    def _get_current_time_str():
        """Returns a string representation of the current time."""
        return datetime.now().strftime('%m_%d_%Y__%H_00')

    def group_by_and_aggregate(self, group_by_cols: List[str], agg_dict: Dict[str, List[str]]):
        """Groups the dataframe by the specified columns and aggregates the specified columns.

        Args:
            group_by_cols: A list of columns to group by.
            agg_dict: A dictionary of columns to aggregate and the aggregation functions to use.

        Returns:
            A dataframe with the specified columns aggregated.

        """
        return self.df.groupby(group_by_cols).agg(agg_dict)

    @staticmethod
    def _should_average(col: str):
        """Returns True if the specified column should be averaged, False otherwise."""
        return any([marker in col for marker in ['/', 'frac', 'num_']])

    @staticmethod
    def _should_count(col: str):
        """Returns True if the specified column should be counted, False otherwise."""
        return any([marker in col for marker in ['day']])

    @staticmethod
    def _should_first(col: str):
        """Returns True if the specified column should be the first value, False otherwise."""
        return any([marker in col for marker in ['id', 'type']])

    def _get_agg_func(self, col: str):
        """Returns the aggregation function to use for the specified column."""
        if self._should_average(col):
            return 'mean'
        elif self._should_count(col):
            return 'count'
        elif self._should_first(col):
            return 'first'
        else:
            return 'sum'

    def group_by_pen_id(self):
        """Groups the dataframe by pen id and aggregates the columns."""
        return self.group_by_and_aggregate(['pen_id'], {
            col: [self._get_agg_func(col)] for col in self.df.columns
        })

    def export_summary_to_csv(self):
        """Exports the summary of the dataframe to a csv file."""
        self.group_by_pen_id().to_csv(f'RUFAS/routines/manure/output/manure_management_summary_'
                                      f'{self._get_current_time_str()}.csv',
                                      index=False)
