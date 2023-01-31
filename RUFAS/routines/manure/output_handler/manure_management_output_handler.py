import collections
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
from pandas import DataFrame

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput

PenDailyUpdateDataType = Tuple[ManureManagementPen,
                               ManureHandlerDailyOutput,
                               ReceptionPitDailyOutput,
                               ManureSeparatorDailyOutput,
                               ManureTreatmentDailyOutput,
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
            # unit = vars(Units).get(field.name, '')  # TODO: Add a Units class later
            # unit = ''
            key_name = f'{prefix}{delimiter}' \
                       f'{self._capitalize_first_letters(field.name, "_")}' \
                # f'{f"{delimiter}({unit})" if unit else ""}'
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
                                      dataclass_obj: Union[PenManure, ManureHandlerDailyOutput,
                                                           ReceptionPitDailyOutput, ManureSeparatorDailyOutput,
                                                           ManureTreatmentDailyOutput],
                                      obj_type: Union[Type[PenManure], Type[ManureHandlerDailyOutput],
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
                prefix=self.HEADER_PREFIXES.get(obj_type, '') + self.HEADER_SECONDARY_DELIMITER + extra_prefix,
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
        (pen, manure_handler_daily_output, reception_pit_daily_output,
         manure_separator_daily_output, manure_treatment_daily_output, anaerobic_digestion_daily_output) = data
        row_data = {
            'pen_id': [pen.id],
            'sim_day': [simulation_day],
            **self._process_pen(pen),
            **self._process_dataclass_output_obj(pen.manure, PenManure),
            **self._process_dataclass_output_obj(manure_handler_daily_output, ManureHandlerDailyOutput),
            **self._process_dataclass_output_obj(reception_pit_daily_output, ReceptionPitDailyOutput),
            **self._process_dataclass_output_obj(manure_separator_daily_output, ManureSeparatorDailyOutput),
            **self._process_dataclass_output_obj(manure_treatment_daily_output, ManureTreatmentDailyOutput),
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
        self._df.sort_values(by=cols, inplace=True)

    def move_columns_to_front(self, cols: List[str]) -> None:
        """Moves the specified columns to the front of the instance dataframe.

        Parameters
        ----------
        cols : List[str]
            A list of column names to move to the front.

        """
        cols_to_move = [col for col in cols if col in self._df.columns]
        for i, col in enumerate(cols_to_move):
            self._df.insert(i, col, self._df.pop(col))

    def sort_by_pen_id_and_simulation_day(self) -> None:
        """Sorts in-place the instance dataframe by pen id and simulation day and moves those columns to the front."""
        self.sort_by(['pen_id', 'sim_day'])
        self.move_columns_to_front(['pen_id', 'sim_day'])

    def export_to_csv(self) -> Path:
        """Exports all data to a csv file."""
        output_path = self.get_csv_output_file_path()
        self._df.to_csv(output_path, index=False)
        return output_path

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

    # ----------------------------------------------------------------------------------
    # The following aggregation are not currently used or unit-tested, but may be useful in the future.

    def group_by_and_aggregate(self, group_by_cols: List[str], agg_dict: Dict[str, List[str]]):
        """Groups the instance dataframe by the specified columns and aggregates the specified columns.

        Args:
            group_by_cols: A list of columns to group by.
            agg_dict: A dictionary of columns to aggregate and the aggregation functions to use.

        Returns:
            A dataframe with the specified columns aggregated.

        """
        return self._df.groupby(group_by_cols).agg(agg_dict)

    @classmethod
    def _should_average(cls, col: str) -> bool:
        """Returns True if the specified column should be averaged, and False otherwise.

        When the specified column contains any of the following markers, it should be averaged:
            - forward slash (/)
            - fraction
            - num_

        Parameters
        ----------
        col : str
            The column name to check.

        Returns
        -------
        bool
            True if the specified column should be averaged, and False otherwise.

        """
        return any([marker in col for marker in ['/', 'fraction', 'num_']])

    @classmethod
    def _should_count(cls, col: str) -> bool:
        """Returns True if the specified column should be counted, and False otherwise.

        When the specified column contains any of the following markers, it should be counted:
            - day

        Parameters
        ----------
        col : str
            The column name to check.

        Returns
        -------
        bool
            True if the specified column should be counted, and False otherwise.

        """
        return any([marker in col for marker in ['day']])

    @classmethod
    def _should_first(cls, col: str) -> bool:
        """Returns True if the specified column should be aggregated simply by the first value, and False otherwise.

        When the specified column contains any of the following markers, it should be aggregated by the first value:
            - id
            - type

        The assumption here is that all the values in the specified column are the same,
        so it doesn't matter which one is used.

        Parameters
        ----------
        col : str
            The column name to check.

        Returns
        -------
        bool
            True if the specified column should be the first value, False otherwise.

        """
        return any([marker in col for marker in ['id', 'type']])

    def _get_agg_func(self, col: str) -> str:
        """Returns the aggregation function to use for the specified column.

        Parameters
        ----------
        col : str
            The column name to get the aggregation function for.

        Returns
        -------
        str
            The aggregation function to use for the specified column.

        """
        if self._should_average(col):
            return 'mean'
        elif self._should_count(col):
            return 'count'
        elif self._should_first(col):
            return 'first'
        else:
            return 'sum'

    def group_by_pen_id(self) -> DataFrame:
        """Groups the instance dataframe by pen id and aggregates the columns.

        Returns
        -------
        DataFrame
            A dataframe with the columns aggregated by pen id.

        """
        return self.group_by_and_aggregate(['pen_id'], {
            col: [self._get_agg_func(col)] for col in self._df.columns
        })
