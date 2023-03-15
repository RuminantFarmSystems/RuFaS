import collections
import re
import shutil
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput
from RUFAS.routines.manure.units.units import Units

PenDailyUpdateDataType = Tuple[
    ManureManagementPen,
    ManureHandlerDailyOutput,
    ReceptionPitDailyOutput,
    ManureSeparatorDailyOutput,
    ManureTreatmentDailyOutput,
    ManureTreatmentDailyOutput,
    ManureTreatmentDailyOutput
]


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

    # TODO: Add an overwrite=True option
    def __init__(self) -> None:
        """Initializes a ManureManagementOutputHandler object."""
        self._df: Optional[DataFrame] = None
        self.empty_main_output_directory()

    @property
    def data(self) -> Optional[DataFrame]:
        """Returns the dataframe stored in the output handler.

        Returns
        -------
        Optional[DataFrame]
            A pandas dataframe with the output data. None if there is no data.

        """
        return self._df

    def _get_manure_handler_name(self, pen_id: int) -> str:
        """Returns the name of the manure handler associated with the pen.

        Parameters
        ----------
        pen_id : int
            The ID of the pen.

        Returns
        -------
        str
            The name of the manure handler associated with the pen.

        """
        manure_handler_type_col = self._df.columns.str.contains('handler_type')
        return self._df[manure_handler_type_col][self._df['pen_id'] == pen_id].values[0][0]

    def _convert_dataclass_obj_into_formatted_dict(self,
                                                   dataclass_obj,
                                                   data_fields,
                                                   prefix: str = '',
                                                   delimiter: str = ' ') \
            -> Dict[str, List[Any]]:
        """Converts a dataclass object from any manure component to a dictionary with formatted keys and values in
        lists.

        Parameters
        ----------
        dataclass_obj : Any
            A dataclass object from any manure component.
        data_fields: Tuple[Field]
            A list of dataclass fields of the dataclass object.
            This is needed because the dataclass object may be None.
        prefix : str, optional
            Prepend each field name with this prefix, by default ''
        delimiter : str, optional
            A delimiter to use between the prefix and the field name, by default ' '

        Returns
        -------
        Dict[str, List[Any]]
            A dictionary with keys formatted as <prefix><delimiter><field_name><delimiter><unit>. Values are stored in
            lists. This structure facilitates the conversion to a pandas dataframe.

        """
        dataframe_dict = collections.defaultdict(list)
        for field in data_fields:
            unit = vars(Units).get(field.name, '')
            # unit = ''
            key_name = f'{prefix + delimiter if prefix else ""}' \
                       f'{self._capitalize_first_letters(field.name, "_")}' \
                       f'{f"{delimiter}({unit})" if unit else ""}'
            value = getattr(dataclass_obj, field.name, np.nan)
            dataframe_dict[key_name].append(round(value, 6))
        return dataframe_dict

    def _process_pen(self, pen: ManureManagementPen) -> Dict[str, List[Any]]:
        """Returns a properly formatted dictionary of important pen attributes to be converted to dataframe.

        Parameters
        ----------
        pen : ManureManagementPen
            A ManureManagementPen object to be processed.

        Returns
        -------
        Dict[str, List[Any]]
            A dictionary of important pen attributes that is properly formatted to be converted to dataframe.

        """
        prefix = self.HEADER_PREFIXES.get(ManureManagementPen, '')
        pen_data = {
            'pen_id': [pen.id],
            'num_animals': [pen.num_animals],
            'num_lactating_cows': [pen.num_lactating_cows],
            'animal_types': [str(pen.classes_in_pen).strip("{}").replace("'", "")],
            'housing_type': [pen.housing_type],
            'bedding_type': [pen.bedding_type],
            'handler_type': [pen.manure_handler],
            'separator_type': [pen.manure_separator],
            'treatment_type': [pen.manure_treatment],
        }
        return {f'{prefix}{self.HEADER_PRIMARY_DELIMITER}{k}': v for k, v in pen_data.items()}

    def _process_dataclass_output_obj(self,
                                      dataclass_obj: Union[
                                          PenManure, ManureHandlerDailyOutput,
                                          ReceptionPitDailyOutput, ManureSeparatorDailyOutput,
                                          ManureTreatmentDailyOutput],
                                      obj_type: Union[
                                          Type[PenManure], Type[ManureHandlerDailyOutput],
                                          Type[ReceptionPitDailyOutput], Type[ManureSeparatorDailyOutput],
                                          Type[ManureTreatmentDailyOutput]],
                                      extra_prefix='') \
            -> Dict[str, List[Any]]:
        """Returns a properly formatted dictionary of important dataclass attributes to be converted to dataframe.

        Parameters
        ----------
        dataclass_obj : Union[PenManure, ManureHandlerDailyOutput, ReceptionPitDailyOutput, ManureSeparatorDailyOutput,
                                ManureTreatmentDailyOutput]
            A dataclass object of the expected type to be processed.
        obj_type : Union[Type[PenManure], Type[ManureHandlerDailyOutput], Type[ReceptionPitDailyOutput],
                    Type[ManureSeparatorDailyOutput], Type[ManureTreatmentDailyOutput]]
            The type of the dataclass object.
        extra_prefix : str, optional
            An extra prefix to prepend to the field names, by default ''

        Returns
        -------
        Dict[str, List[Any]]
            A dictionary of important dataclass attributes that is properly formatted to be converted to dataframe.

        """
        return self._convert_dataclass_obj_into_formatted_dict(
            dataclass_obj=dataclass_obj,
            data_fields=fields(obj_type),
            prefix=(self.HEADER_PREFIXES.get(obj_type, '') +
                    f'{self.HEADER_SECONDARY_DELIMITER + extra_prefix if extra_prefix else ""}'),
            delimiter=self.HEADER_PRIMARY_DELIMITER
        )

    def append_daily_update_output_for_pen(self, simulation_day: int, data: PenDailyUpdateDataType) -> None:
        """Appends daily update data for a pen to the dataframe.

        Each daily update of a pen corresponds to a row in the dataframe.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        data : PenDailyUpdateDataType
            A tuple of dataclass objects containing daily update data for a pen.

        """
        pen = data[0]
        manure_handler_daily_output = data[1]
        reception_pit_daily_output = data[2]
        manure_separator_daily_output = data[3]
        manure_treatment_daily_output = data[4]
        manure_treatment_accumulated_output = data[5]
        anaerobic_digestion_daily_output = data[6]

        row_data = {
            'pen_id': [pen.id],
            'sim_day': [simulation_day],
            **self._process_pen(pen),
            **self._process_dataclass_output_obj(pen.manure, PenManure),
            **self._process_dataclass_output_obj(manure_handler_daily_output, ManureHandlerDailyOutput),
            **self._process_dataclass_output_obj(reception_pit_daily_output, ReceptionPitDailyOutput),
            **self._process_dataclass_output_obj(manure_separator_daily_output, ManureSeparatorDailyOutput),
            **self._process_dataclass_output_obj(manure_treatment_daily_output, ManureTreatmentDailyOutput),
            **self._process_dataclass_output_obj(manure_treatment_accumulated_output, ManureTreatmentDailyOutput,
                                                 'acc'),
            **self._process_dataclass_output_obj(anaerobic_digestion_daily_output, ManureTreatmentDailyOutput, 'ad'),
        }

        self._df = self._append_row(row_data)

    def _append_row(self, row_data: Dict[str, List[Any]]) -> DataFrame:
        """Appends row data to the internal dataframe and returns the updated dataframe.

        Parameters
        ----------
        row_data : Dict[str, List[Any]]
            A dictionary of row data to be appended to the dataframe.

        Returns
        -------
        DataFrame
            The updated dataframe. If the dataframe is empty, it will be initialized with the row data.
            Otherwise, the row data will be appended to the dataframe.

        """
        temp_df = pd.DataFrame(row_data)

        if self._df is None:
            return temp_df

        return pd.concat([self._df, temp_df], ignore_index=True)

    def sort_by(self, cols: List[str]) -> None:
        """Sorts in-place the instance dataframe by the specified columns.

        Parameters
        ----------
        cols : List[str]
            A list of column names to sort by.

        """
        if self._df is None:
            return
        self._df.sort_values(by=cols, inplace=True)

    def move_columns_to_front(self, cols: List[str]) -> None:
        """Moves the specified columns to the front of the instance dataframe.

        Parameters
        ----------
        cols : List[str]
            A list of column names to move to the front.

        """
        if self._df is None:
            return
        cols_to_move = [col for col in cols if col in self._df.columns]
        for i, col in enumerate(cols_to_move):
            self._df.insert(i, col, self._df.pop(col))

    def sort_by_pen_id_and_simulation_day(self) -> None:
        """Sorts in-place the instance dataframe by pen id and simulation day and moves those columns to the front."""
        self.sort_by(['pen_id', 'sim_day'])
        self.move_columns_to_front(['pen_id', 'sim_day'])

    def export_to_csv(self) -> Optional[Path]:
        """Exports all data to a csv file.

        Returns
        -------
        Optional[Path]
            The path to the csv file if there is data to be exported, None otherwise.

        """
        if self._df is None:
            return None
        csv_output_file_path = self.get_csv_output_file_path()
        self._df.to_csv(csv_output_file_path, index=False)
        return csv_output_file_path

    @classmethod
    def _capitalize_first_letters(cls, s: str, delimiter=' ') -> str:
        """Capitalizes the first letter of each word in a string.

        Parameters
        ----------
        s : str
            The string to capitalize each constituent word.
        delimiter : str, optional
            The delimiter to use to split the string and rejoin the parts, by default ' '.

        Returns
        -------
        str
            The string with each constituent word capitalized.

        """
        if not s:
            return s
        return delimiter.join(word[0].upper() + word[1:] for word in s.split(delimiter))

    # TODO: Move to a more general folder of a location specified in the config file
    @classmethod
    def get_main_output_directory_path(cls) -> Path:
        """Returns the path of the main output directory for the manure module.

        Returns
        -------
        Path
            The path of the main output directory for the manure module.

        """
        main_output_dir_path = Path('RUFAS/routines/manure/output')
        main_output_dir_path.mkdir(parents=True, exist_ok=True)
        return main_output_dir_path

    def get_csv_output_directory_path(self) -> Path:
        """Returns the path of the csv output directory.

        Returns
        -------
        Path
            The path of the csv output directory.

        """
        csv_dir_path = self.get_main_output_directory_path() / 'csv'
        csv_dir_path.mkdir(parents=True, exist_ok=True)
        return csv_dir_path

    def get_csv_output_file_path(self) -> Path:
        """Returns the path of the csv output file.

        Returns
        -------
        Path
            The path of the csv output file.

        """
        file_name = f'manure_management_output_{self._get_formatted_current_time()}'
        file_extension = '.csv'
        return self.get_csv_output_directory_path() / (file_name + file_extension)

    def empty_main_output_directory(self) -> None:
        """Empties the main output directory."""
        self._delete_files_and_subdirectories(self.get_main_output_directory_path())

    @classmethod
    def _delete_files_and_subdirectories(cls, path: Path) -> None:
        """Deletes all files and subdirectories in the specified path."""
        if path.exists():
            for file in path.iterdir():
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)

    @classmethod
    def _get_formatted_current_time(cls) -> str:
        """Returns a string representation of the current time.

        Returns
        -------
        str
            A string representation of the current time in the format `mm_dd_yyyy__hh_00`.

        """
        return datetime.now().strftime('%Y_%m_%d__%H_00')

    @classmethod
    def _get_full_prefix(cls, prefix: str) -> str:
        """Translates a prefix to a more readable version.

        Parameters
        ----------
        prefix : str
            The prefix to translate.

        Returns
        -------
        str
            The translated prefix.

        """
        return {
            'pen': 'Pen Info',
            'manure': 'Input Manure',
            'handler': 'Handler',
            'rp': 'Reception Pit',
            'sep': 'Separator',
            'tx': 'Treatment',
            'tx_acc': 'Treatment Acc',
            'tx_ad': 'Digester',
        }.get(prefix, prefix)

    def _remove_prefix(self, header: str) -> str:
        """Removes the prefix from a string.

        Parameters
        ----------
        header : str
            The string to remove the prefix from.

        Returns
        -------
        str
            The string with the prefix removed.

        """
        # We stop at the first occurrence of the delimiter and return the second part of the split.
        return header.split(self.HEADER_PRIMARY_DELIMITER, 1)[1]

    def _translate_prefix(self, header: str) -> str:
        """Formats the prefix of a string.

        Parameters
        ----------
        header : str
            The string to format the prefix of.

        Returns
        -------
        str
            The string with the formatted prefix.

        """
        first, second = header.split(self.HEADER_PRIMARY_DELIMITER, 1)
        return self._get_full_prefix(first) + self.HEADER_PRIMARY_DELIMITER + second

    def _remove_units(self, header: str) -> str:
        """Removes units from a string.

        Parameters
        ----------
        header : str
            The string to remove units from.

        Returns
        -------
        str
            The string with units removed.

        """
        return re.sub(rf"{self.HEADER_PRIMARY_DELIMITER}\(.*\)", '', header)

    def _replace_delimiters_with_spaces(self, header: str) -> str:
        """Replaces the occurrence of consecutive secondary header delimiters with a space.

        Parameters
        ----------
        header : str
            The string to replace the secondary header delimiters with a space.

        Returns
        -------
        str
            The string with the secondary header delimiters replaced with a space.

        """
        return re.sub(rf'{self.HEADER_SECONDARY_DELIMITER}+', ' ', header)

    @classmethod
    def _squeeze_spaces(cls, s: str) -> str:
        """Removes extra spaces from a string.

        Parameters
        ----------
        s : str
            The string to remove extra spaces from.

        Returns
        -------
        str
            The string with extra spaces removed.

        """
        return re.sub(rf'\s+', ' ', s).strip()

    def _format_label(self, label: str) -> str:
        """Formats a label.

        Parameters
        ----------
        label : str
            The label to format.

        Returns
        -------
        str
            The formatted label.

        """
        label = self._remove_prefix(label)
        label = self._replace_delimiters_with_spaces(label)
        return self._squeeze_spaces(label)

    def _format_title(self, title: str) -> str:
        """Formats a title.

        Parameters
        ----------
        title : str
            The title to format.

        Returns
        -------
        str
            The formatted title.

        """
        title = self._translate_prefix(title)
        title = self._remove_units(title)
        title = re.sub(rf'{self.HEADER_PRIMARY_DELIMITER}+', ' - ', title)
        title = self._replace_delimiters_with_spaces(title)
        title = self._capitalize_first_letters(title)
        return self._squeeze_spaces(title)

    def _make_scatter_plot_with_anchor_column(self, output_dir: Path, anchor_col: str,
                                              x: str, y: str, anchor_label: str, x_label: str, y_label: str,
                                              title: str):
        for val in self._df[anchor_col].unique():
            x_series = self._df.loc[self._df[anchor_col] == val, x]
            y_series = self._df.loc[self._df[anchor_col] == val, y]
            plot_name = f'{anchor_label} {val} - {title}'
            self._make_simple_scatter_plot_with_matplotlib(
                output_path=output_dir / f'{plot_name}.png',
                x=x_series,
                y=y_series,
                x_label=x_label,
                y_label=y_label,
                title=plot_name,
            )

    def _get_header_prefixes(self) -> List[str]:
        """Returns a list of all header prefixes."""
        return list(self.HEADER_PREFIXES.values())

    @staticmethod
    def _get_excluded_attrs() -> List[str]:
        """Returns a list of attributes to exclude from the output."""
        return ['pen_id', 'sim_day', 'simulation_day']

    def _get_headers(self) -> List[str]:
        """Returns a list of all headers."""
        headers = [col for col in self._df.columns
                   for prefix in self._get_header_prefixes() + ['tx_acc', 'tx_ad']  # move these two to somewhere else
                   if col.startswith(prefix + self.HEADER_PRIMARY_DELIMITER)]
        return [header for header in headers
                if all([attr.lower() not in header.lower() for attr in self._get_excluded_attrs()])]

    def produce_graphics(self):
        """Produces graphics from the data."""
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

    @classmethod
    def _make_simple_scatter_plot_with_matplotlib(cls,
                                                  output_path: Path,
                                                  x: pd.Series,
                                                  y: pd.Series,
                                                  x_label: str,
                                                  y_label: str,
                                                  title: str) -> None:
        """Makes a simple scatter plot with matplotlib."""
        if y.dtype.kind not in 'iuf' or y.hasnans:
            return
        small, medium, large = 10, 12, 16
        # plt.style.use('fivethirtyeight')
        plt.style.use('ggplot')
        # plt.figure()
        plt.scatter(x, y, alpha=0.7, c='#1746A2', s=25)
        # plt.plot(x, y, c='#1746A2', linewidth=2)
        # fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
        # ax[0].scatter(x, y, alpha=0.7, c='#1746A2', s=25)
        # ax[1].plot(x, y, c='#1746A2', linewidth=2)
        # ax.scatter(x, y, alpha=0.7, c='#1746A2', s=25)
        # ax.plot(x, y, c='#1746A2', linewidth=2)        ax[0].set_xlabel(x_label, fontsize=medium)
        # ax[1].set_xlabel(x_label, fontsize=medium)
        # ax[0].set_ylabel(y_label, fontsize=medium)
        # ax[1].set_ylabel(y_label, fontsize=medium)
        # ax[0].set_title(title, fontsize=large)
        # ax.tick_params(axis='both', which='major', labelsize=small)
        # set integer x-axis ticks        ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))
        # ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))

        plt.xlabel(x_label, fontsize=small)
        plt.ylabel(y_label, fontsize=small)
        plt.title(title, fontsize=medium)
        locs, _ = plt.xticks()
        plt.xticks([int(loc) for loc in locs if loc >= 0], fontsize=small)
        plt.yticks(fontsize=small)
        plt.legend([f'{y_label}'], loc='best', frameon=False, fontsize=small)
        # ax[0].legend([f'{y_label}'], loc='best', frameon=False, fontsize=small)
        # ax[1].legend([f'{y_label}'], loc='best', frameon=False, fontsize=small)
        plt.savefig(output_path, dpi=400, bbox_inches='tight', pad_inches=0.2)
        plt.close()

    def _get_graphics_dir(self) -> Path:
        """Returns the graphics output directory."""
        graphics_dir = self.get_main_output_directory_path() / 'graphics'
        graphics_dir.mkdir(parents=True, exist_ok=True)
        return graphics_dir
