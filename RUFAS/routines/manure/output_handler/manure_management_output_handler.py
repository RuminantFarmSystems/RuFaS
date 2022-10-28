import collections
import os
import re
import shutil
from dataclasses import fields
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

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
    HEADER_PREFIXES = {
        ManureManagementPen: 'pen',
        PenManure: 'manure',
        ManureHandlerDailyOutput: 'handler',
        ReceptionPitDailyOutput: 'rp',
        ManureSeparatorDailyOutput: 'sep',
        ManureTreatmentDailyOutput: 'tx'
    }
    HEADER_PRIMARY_DELIMITER = '__'
    HEADER_SECONDARY_DELIMITER = '_'

    def __init__(self):
        self.df = None
        self._delete_files_and_subdirectories(self._get_output_main_directory())

    def _convert_dataclass_obj_to_formatted_dict(self,
                                                 dataclass_obj,
                                                 data_fields,
                                                 prefix: str = '',
                                                 delimiter: str = ' ') \
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
            key_name = f'{prefix}{delimiter}' \
                       f'{self._capitalize_first_letters(field.name, "_")}' \
                       f'{f"{delimiter}({unit})" if unit else ""}'
            value = getattr(dataclass_obj, field.name, np.nan)
            d[key_name].append(round(value, 6))
        return d

    def _process_pen(self, pen: ManureManagementPen):
        """Returns a dictionary of important pen attributes to be converted to dataframe.

        Args:
            pen: A ManureManagementPen object.

        Returns:
            A dictionary of important pen attributes.

        """
        prefix = self.HEADER_PREFIXES.get(type(pen), '')
        temp = {
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
        return {f'{prefix}{self.HEADER_PRIMARY_DELIMITER}{k}': v for k, v in temp.items()}

    def _process_dataclass_output_obj(self, dataclass_obj, obj_fields):
        return self._convert_dataclass_obj_to_formatted_dict(
                dataclass_obj,
                obj_fields,
                prefix=self.HEADER_PREFIXES.get(type(dataclass_obj), ''),
                delimiter=self.HEADER_PRIMARY_DELIMITER
        )

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
            'pen_id': [pen.id],
            'sim_day': [simulation_day],
            **self._process_pen(pen),
            **self._process_dataclass_output_obj(pen.manure, fields(PenManure)),
            **self._process_dataclass_output_obj(manure_handler_output, fields(ManureHandlerDailyOutput)),
            **self._process_dataclass_output_obj(reception_pit_output, fields(ReceptionPitDailyOutput)),
            **self._process_dataclass_output_obj(manure_separator_output, fields(ManureSeparatorDailyOutput)),
            **self._process_dataclass_output_obj(treatment_output, fields(ManureTreatmentDailyOutput)),
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

    def export_all_data_to_csv(self) -> None:
        """Exports all data to a csv file."""
        output_path = f'{self._get_csv_dir()}/manure_management_output_{self._get_current_time_str()}.csv'
        self.df.to_csv(output_path, index=False)

    @staticmethod
    def _capitalize_first_letters(s: str, delimiter=' ') -> str:
        """Capitalizes the first letter of each word in a string."""
        return delimiter.join(word[0].upper() + word[1:] for word in s.split(delimiter))

    @staticmethod
    def _get_full_prefix(prefix: str) -> str:
        """Translates a prefix to a more readable version."""
        return {
            'pen': 'Pen Info',
            'manure': 'Input Manure',
            'handler': 'Handler',
            'rp': 'Reception Pit',
            'sep': 'Separator',
            'tx': 'Treatment',
        }.get(prefix, prefix)

    def _remove_prefix(self, header: str) -> str:
        """Removes the prefix from a string."""
        return header.split(self.HEADER_PRIMARY_DELIMITER, 1)[1]

    def _translate_prefix(self, header: str) -> str:
        """Formats the prefix of a string."""
        first, second = header.split(self.HEADER_PRIMARY_DELIMITER, 1)
        return self._get_full_prefix(first) + self.HEADER_PRIMARY_DELIMITER + second

    def _remove_units(self, header: str) -> str:
        """Removes units from a string."""
        return re.sub(rf"{self.HEADER_PRIMARY_DELIMITER}\(.*\)", '', header)

    def _replace_delimiters_with_spaces(self, header: str) -> str:
        """Replaces the delimiter with a space."""
        return re.sub(rf'{self.HEADER_SECONDARY_DELIMITER}+', ' ', header)

    @staticmethod
    def _squeeze_spaces(s: str) -> str:
        """Removes extra spaces from a string."""
        return re.sub(rf'\s+', ' ', s).strip()

    def _format_label(self, label: str) -> str:
        label = self._remove_prefix(label)
        label = self._replace_delimiters_with_spaces(label)
        return self._squeeze_spaces(label)

    def _format_title(self, title: str) -> str:
        title = self._translate_prefix(title)
        title = self._remove_units(title)
        title = re.sub(rf'{self.HEADER_PRIMARY_DELIMITER}+', ' - ', title)
        title = self._replace_delimiters_with_spaces(title)
        title = self._capitalize_first_letters(title)
        return self._squeeze_spaces(title)

    def _make_scatter_plot_with_anchor_column(self, output_dir: str, anchor_col: str,
                                              x: str, y: str, anchor_label: str, x_label: str, y_label: str,
                                              title: str):
        for val in self.df[anchor_col].unique():
            x_series = self.df.loc[self.df[anchor_col] == val, x]
            y_series = self.df.loc[self.df[anchor_col] == val, y]
            plot_name = f'{anchor_label} {val} - {title}'
            self._make_simple_scatter_plot_with_matplotlib(
                    output_path=f'{output_dir}/{plot_name}.png',
                    x=x_series,
                    y=y_series,
                    x_label=x_label,
                    y_label=y_label,
                    title=plot_name,
            )

    def _get_header_prefixes(self) -> List[str]:
        return list(self.HEADER_PREFIXES.values())

    @staticmethod
    def _get_excluded_attrs() -> List[str]:
        return ['pen_id', 'sim_day', 'simulation_day']

    def _get_headers(self) -> List[str]:
        headers = [col for col in self.df.columns
                   for prefix in self._get_header_prefixes()
                   if col.startswith(prefix + self.HEADER_PRIMARY_DELIMITER)]
        return [header for header in headers
                if all([attr.lower() not in header.lower() for attr in self._get_excluded_attrs()])]

    def produce_graphics(self):
        for header in self._get_headers():
            self._make_scatter_plot_with_anchor_column(
                    output_dir=self._get_graphics_dir(),
                    anchor_col='pen_id',
                    x='sim_day',
                    y=header,
                    anchor_label='Pen',
                    x_label='Simulation Day',
                    y_label=self._format_label(header),
                    title=self._format_title(header)
            )

    @staticmethod
    def _make_simple_scatter_plot_with_matplotlib(output_path: str,
                                                  x: pd.Series,
                                                  y: pd.Series,
                                                  x_label: str,
                                                  y_label: str,
                                                  title: str) -> None:
        """Makes a simple scatter plot with matplotlib."""
        if y.dtype.kind not in 'iuf' or y.hasnans:
            return
        small, medium, large = 10, 12, 16
        plt.style.use('fivethirtyeight')
        plt.figure()
        plt.scatter(x, y, alpha=0.7, c='#1746A2', s=25)
        plt.xlabel(x_label, fontsize=medium)
        plt.ylabel(y_label, fontsize=medium)
        plt.title(title, fontsize=large)

        locs, _ = plt.xticks()
        plt.xticks([int(loc) for loc in locs if loc >= 0], fontsize=medium)
        plt.yticks(fontsize=medium)
        plt.legend([f'{y_label}'], loc='best', frameon=False, fontsize=small)

        plt.savefig(output_path, dpi=400, bbox_inches='tight', pad_inches=0.3)
        plt.close()

    @staticmethod
    def _get_output_main_directory() -> str:
        """Returns the main output directory."""
        output_dir = 'RUFAS/routines/manure/output'
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _get_graphics_dir(self) -> str:
        """Returns the graphics output directory."""
        graphics_dir = f'{self._get_output_main_directory()}/graphics'
        os.makedirs(graphics_dir, exist_ok=True)
        return graphics_dir

    def _get_csv_dir(self) -> str:
        """Returns the csv output directory."""
        csv_dir = f'{self._get_output_main_directory()}/csv'
        os.makedirs(csv_dir, exist_ok=True)
        return csv_dir

    @staticmethod
    def _delete_files_and_subdirectories(path: str) -> None:
        """Deletes all files and subdirectories in the specified path."""
        if os.path.exists(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

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
    def _should_average(col: str) -> bool:
        """Returns True if the specified column should be averaged, False otherwise."""
        return any([marker in col for marker in ['/', 'frac', 'num_']])

    @staticmethod
    def _should_count(col: str) -> bool:
        """Returns True if the specified column should be counted, False otherwise."""
        return any([marker in col for marker in ['day']])

    @staticmethod
    def _should_first(col: str) -> bool:
        """Returns True if the specified column should be the first value, False otherwise."""
        return any([marker in col for marker in ['id', 'type']])

    def _get_agg_func(self, col: str) -> str:
        """Returns the aggregation function to use for the specified column."""
        if self._should_average(col):
            return 'mean'
        elif self._should_count(col):
            return 'count'
        elif self._should_first(col):
            return 'first'
        else:
            return 'sum'

    def group_by_pen_id(self) -> pd.DataFrame:
        """Groups the dataframe by pen id and aggregates the columns."""
        return self.group_by_and_aggregate(['pen_id'], {
            col: [self._get_agg_func(col)] for col in self.df.columns
        })

    def export_summary_to_csv(self) -> None:
        """Exports the summary of the dataframe to a csv file."""
        self.group_by_pen_id().to_csv(f'{self._get_csv_dir()}/manure_management_summary_'
                                      f'{self._get_current_time_str()}.csv',
                                      index=False)
