from __future__ import annotations

import collections
import re
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from typing import List
from typing import Type

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput
from RUFAS.routines.manure.units.units import Units


class ManureManagerOutputHandler:
    """
    This class manages the output processing for the ManureManager simulation model.

    It is responsible for transforming simulation output data into more user-friendly formats such as
    csv files and scatter plots. The data could be from different components of the ManureManager
    like ManureManagerPen, PenManure, ManureHandlerDailyOutput, ReceptionPitDailyOutput,
    ManureSeparatorDailyOutput, and ManureTreatmentDailyOutput.

    """
    _DEFAULT_OUTPUT_DIR_NAME = 'manure_module_reports'
    _HEADER_PREFIXES = {
        ManureManagerPen: 'pen',
        PenManure: 'manure',
        ManureHandlerDailyOutput: 'handler',
        ReceptionPitDailyOutput: 'rp',
        ManureSeparatorDailyOutput: 'sep',
        ManureTreatmentDailyOutput: 'tx'
    }
    _HEADER_PRIMARY_DELIMITER = '__'
    _HEADER_SECONDARY_DELIMITER = '_'

    @classmethod
    def _convert_dataclass_obj_into_formatted_dict(cls, dataclass_obj, data_fields, prefix='',
                                                   delimiter=' ') -> dict[str, list[Any]]:
        """
        Convert a dataclass object into a formatted dictionary with values stored in lists.

        This method converts a dataclass object from any manure component into a dictionary with keys
        formatted as "<prefix><delimiter><field_name><delimiter><unit>". The values are stored in lists to ease the
        conversion to a pandas dataframe. The method uses a prefix, delimiter and field names from the dataclass fields to
        construct the dictionary keys.

        Parameters
        ----------
        dataclass_obj : Any
            A dataclass object from any manure component.
        data_fields: tuple[Field]
            A list of dataclass fields of the dataclass object. This is needed because the dataclass object may be None.
        prefix : str, optional
            A prefix to prepend to each field name, by default ''.
        delimiter : str, optional
            A delimiter to use between the prefix and the field name, by default ' '.

        Returns
        -------
        dict[str, list[Any]]
            A dictionary with keys formatted as per the above scheme and values encapsulated in lists.

        """
        dataframe_dict = collections.defaultdict(list)
        for field in data_fields:
            unit = vars(Units).get(field.name, '')
            key_name_parts = [prefix, cls._capitalize_first_letters(field.name, "_"), f"({unit})" if unit else ""]
            key_name = delimiter.join(part for part in key_name_parts if part)
            value = getattr(dataclass_obj, field.name, np.nan)
            dataframe_dict[key_name].append(round(value, 6))
        return dataframe_dict

    @classmethod
    def _process_pen(cls, pen: ManureManagerPen) -> dict[str, List[Any]]:
        """
        Extract and format key attributes of a ManureManagerPen object for conversion to a dataframe.

        This method extracts important attributes from a ManureManagerPen object, encapsulates them in lists and
        stores them in a dictionary with keys formatted as "<prefix><delimiter><attribute_name>".

        Parameters
        ----------
        pen : ManureManagerPen
            The ManureManagerPen object to process.

        Returns
        -------
        dict[str, list[Any]]
            A dictionary of important pen attributes, formatted for conversion to a dataframe.

        """
        prefix = cls._HEADER_PREFIXES.get(ManureManagerPen, '')
        pen_data = {
            'pen_id': [pen.id],
            'num_animals': [pen.num_animals],
            'num_lactating_cows': [pen.num_lactating_cows],
            'animal_types': [str(pen.classes_in_pen).strip("{}").replace("'", "")],
            'housing_type': [pen.housing_type],
            'pen_type': [pen.pen_type],
            'bedding_type': [pen.bedding_type],
            'handler_type': [pen.manure_handler],
            'separator_type': [pen.manure_separator],
            'treatment_type': [pen.manure_treatment],
        }
        return {f'{prefix}{cls._HEADER_PRIMARY_DELIMITER}{k}': v for k, v in pen_data.items()}

    @classmethod
    def _process_dataclass_output_obj(cls,
                                      dataclass_obj: PenManure | ManureHandlerDailyOutput | ReceptionPitDailyOutput | ManureSeparatorDailyOutput | ManureTreatmentDailyOutput,
                                      obj_type: Type[PenManure] | Type[ManureHandlerDailyOutput] | Type[
                                          ReceptionPitDailyOutput] | Type[ManureSeparatorDailyOutput] | Type[
                                                    ManureTreatmentDailyOutput],
                                      extra_prefix: str = '') -> dict[str, list[Any]]:

        """
        Process a dataclass object of a specified type and convert it into a dictionary suitable for dataframe conversion.

        This method takes a dataclass object of a specified type and converts it into a dictionary with keys formatted as
        "<prefix><delimiter><field_name><delimiter><unit>", where the prefix includes an optional extra prefix. The values
        are stored in lists to facilitate conversion to a pandas dataframe.

        Parameters
        ----------
        dataclass_obj : PenManure | ManureHandlerDailyOutput | ReceptionPitDailyOutput | ManureSeparatorDailyOutput | ManureTreatmentDailyOutput
            The dataclass object to be processed.
        obj_type : Type[PenManure] | Type[ManureHandlerDailyOutput] | Type[ReceptionPitDailyOutput] | Type[ManureSeparatorDailyOutput] | Type[ManureTreatmentDailyOutput]
            The type of the dataclass object.
        extra_prefix : str, optional
            An additional prefix to prepend to the field names, by default ''.

        Returns
        -------
        dict[str, list[Any]]
            A dictionary of dataclass attributes, formatted for conversion to a dataframe.

        """
        return cls._convert_dataclass_obj_into_formatted_dict(
            dataclass_obj=dataclass_obj,
            data_fields=fields(obj_type),
            prefix=(cls._HEADER_PREFIXES.get(obj_type, '') +
                    f'{cls._HEADER_SECONDARY_DELIMITER + extra_prefix if extra_prefix else ""}'),
            delimiter=cls._HEADER_PRIMARY_DELIMITER
        )

    @classmethod
    def _create_dataframe_from_manure_manager_data(cls, manure_manager):
        """
        Create a DataFrame from a given manure manager's data.

        This method takes a manure manager, processes its data and generates a DataFrame from it.

        Parameters
        ----------
        manure_manager :
            The manure manager containing data to be converted to a DataFrame.

        Returns
        -------
        pd.DataFrame
            A DataFrame representation of the manure manager's data.

        """
        dataframe_dict = collections.defaultdict(list)

        processes = [
            {'key': 'pen'},
            {'key': 'animal_manure_excretions', 'class': PenManure},
            {'key': 'manure_handler_daily_output', 'class': ManureHandlerDailyOutput},
            {'key': 'reception_pit_daily_output', 'class': ReceptionPitDailyOutput},
            {'key': 'manure_separator_daily_output', 'class': ManureSeparatorDailyOutput},
            {'key': 'manure_treatment_daily_output', 'class': ManureTreatmentDailyOutput},
            {'key': 'manure_treatment_accumulated_output', 'class': ManureTreatmentDailyOutput, 'prefix': 'acc'},
            {'key': 'anaerobic_digestion_daily_output', 'class': ManureTreatmentDailyOutput, 'prefix': 'ad'},
        ]

        for daily_output_per_pen in manure_manager.data:
            dataframe_dict['pen_id'].append(daily_output_per_pen['pen'].id)
            dataframe_dict['simulation_day'].append(daily_output_per_pen['simulation_day'])

            for process in processes:
                prefix = process.get('prefix', None)
                if process['key'] == 'pen':
                    items = cls._process_pen(daily_output_per_pen[process['key']]).items()
                else:
                    items = cls._process_dataclass_output_obj(daily_output_per_pen[process['key']],
                                                              process['class'],  # type: ignore
                                                              extra_prefix=prefix).items()

                for k, v in items:
                    dataframe_dict[k].append(*v)

        return pd.DataFrame(dataframe_dict)

    @classmethod
    def produce_csv(cls, csv_dir: str | Path, manure_manager) -> None:
        """
        Generate a series of CSV files from the given manure manager's data.

        This method takes a manure manager and a directory path. It processes the manure manager's data,
        creates a DataFrame, and then writes the DataFrame to CSV files in the provided directory.

        Each CSV file contains two fixed columns 'pen_id' and 'simulation_day'. The rows in each CSV
        are sorted first by 'pen_id' and then by 'simulation_day'.

        Parameters
        ----------
        csv_dir : str or pathlib.Path
            The directory where the CSV files will be written.

        manure_manager :
            The manure manager containing data to be converted to CSV files.

        Returns
        -------
        None

        """
        df = cls._create_dataframe_from_manure_manager_data(manure_manager)
        sorting_cols = ['pen_id', 'simulation_day']
        df.sort_values(by=sorting_cols, inplace=True)
        df = cls._drop_all_zeros_nan_none_columns(df)

        non_sorting_cols = [col for col in df.columns if not any(sorting_col.lower() in col.lower() for sorting_col in sorting_cols)]
        df = df[sorting_cols + non_sorting_cols]

        csv_dir = Path(csv_dir) / cls._DEFAULT_OUTPUT_DIR_NAME
        csv_dir.mkdir(parents=True, exist_ok=True)
        all_data_file_path = csv_dir / f'all_manure_module_data_{cls._get_formatted_current_time()}.csv'
        df.to_csv(all_data_file_path, index=False)

        for col in non_sorting_cols:
            temp_df = df[[*sorting_cols, col]]
            temp_df.columns = [*sorting_cols, cls._format_col_name(col)]
            sub_dir_path = csv_dir / f'{cls._extract_dir_name_from_col_name(col)}'
            sub_dir_path.mkdir(parents=True, exist_ok=True)
            file_path = sub_dir_path / f'{cls._format_csv_filename(col)}.csv'
            temp_df.to_csv(file_path, index=False)

    @classmethod
    def _apply_pipeline_to_col_name(cls, col_name: str, pipeline: list[Callable[[str], str]]) -> str:
        """
        Apply a sequence of operations to a column name.

        Parameters
        ----------
        col_name : str
            The column name to be processed.
        pipeline : list[Callable[[str], str]]
            The list of methods to apply to the column name.

        Returns
        -------
        str
            The processed column name.

        """
        for method in pipeline:
            col_name = method(col_name)
        return col_name

    @classmethod
    def _extract_dir_name_from_col_name(cls, col_name: str) -> str:
        """
        Extract a directory name from a column name.

        This method converts a column name into a directory name by translating
        the prefix, removing units, and then extracting the prefix part of the
        string (the part before the primary delimiter).

        Parameters
        ----------
        col_name : str
            The column name from which to extract the directory name.

        Returns
        -------
        str
            The directory name extracted from the column name.

        """
        pipeline = [cls._translate_prefix, cls._remove_units, str.lower,
                    lambda s: s.split(cls._HEADER_PRIMARY_DELIMITER)[0]]
        return cls._apply_pipeline_to_col_name(col_name, pipeline)

    @classmethod
    def _format_csv_filename(cls, col_name: str) -> str:
        """
        Format a column name into a CSV filename.

        This method formats a column name into a CSV filename by removing the
        prefix and units, replacing secondary header delimiters with spaces,
        squeezing spaces, and converting the result to lowercase.

        Parameters
        ----------
        col_name : str
            The column name to be formatted.

        Returns
        -------
        str
            The CSV filename formatted from the column name.

        """
        pipeline = [cls._remove_prefix, cls._remove_units,
                    cls._replace_secondary_header_delimiters_with_spaces,
                    cls._squeeze_spaces, str.lower]
        return cls._apply_pipeline_to_col_name(col_name, pipeline)

    @classmethod
    def _format_col_name(cls, col_name: str) -> str:
        """
        Format a column name by removing its prefix and units and converting
        the result to lowercase.

        Parameters
        ----------
        col_name : str
            The column name to be formatted.

        Returns
        -------
        str
            The formatted column name.

        """
        pipeline = [cls._remove_prefix, cls._remove_units, str.lower]
        return cls._apply_pipeline_to_col_name(col_name, pipeline)

    @classmethod
    def _drop_all_zeros_nan_none_columns(cls, df: DataFrame) -> DataFrame:
        """
        Drop all columns from a DataFrame that only contain zeros, NaNs, or None.

        This method checks each column of the input DataFrame and drops any
        columns that contain only zeros, NaNs, or None.

        Parameters
        ----------
        df : DataFrame
            The DataFrame from which to drop columns.

        Returns
        -------
        DataFrame
            The DataFrame with the specified columns dropped.

        """
        temp_df = df.fillna(value=np.nan)
        cols_to_drop = (temp_df == 0).all(axis=0) | temp_df.isna().all(axis=0)
        return temp_df.loc[:, ~cols_to_drop]

    @staticmethod
    def _capitalize_first_letters(s: str, delimiter=' ') -> str:
        """
        Capitalize the first letter of each word in a string.

        This method splits a string at each occurrence of a specified delimiter,
        capitalizes the first letter of each resulting word, and then reassembles
        the string.

        Parameters
        ----------
        s : str
            The string whose words are to be capitalized.
        delimiter : str, optional
            The delimiter to use for splitting and rejoining the string, by
            default ' '.

        Returns
        -------
        str
            The string with each word capitalized.

        """
        if not s:
            return s
        return delimiter.join(word[0].upper() + word[1:] for word in s.split(delimiter))

    @classmethod
    def _get_formatted_current_time(cls) -> str:
        """
        Get the current time and format it into a string.

        This method retrieves the current date and time, and formats it into a
        string in the format `yyyy_mm_dd__hh_00`.

        Returns
        -------
        str
            A string representation of the current time in the specified format.

        """
        return datetime.now().strftime('%Y_%m_%d__%H_00')

    @classmethod
    def _get_full_prefix(cls, prefix: str) -> str:
        """
        Translate a short prefix to its more descriptive version.

        This method maps a given prefix to its more descriptive version. If no
        match is found in the predefined mapping, the original prefix is returned.

        Parameters
        ----------
        prefix : str
            The short prefix to be translated.

        Returns
        -------
        str
            The translated (more descriptive) version of the given prefix.

        """
        return {
            'pen': 'Pen Info',
            'manure': 'Input Manure',
            'handler': 'Handler',
            'rp': 'Reception Pit',
            'sep': 'Separator',
            'tx': 'Treatment',
            'tx_acc': 'Treatment Accumulated',
            'tx_ad': 'Digester',
        }.get(prefix, prefix)

    @classmethod
    def _remove_prefix(cls, header: str) -> str:
        """
        Remove the prefix from a string.

        This method splits the input string at the first occurrence of the primary
        delimiter and returns the second part of the split.

        Parameters
        ----------
        header : str
            The string from which the prefix is to be removed.

        Returns
        -------
        str
            The string with the prefix removed.

        """
        if cls._HEADER_PRIMARY_DELIMITER not in header:
            return header
        return header.split(cls._HEADER_PRIMARY_DELIMITER, 1)[1]

    @classmethod
    def _translate_prefix(cls, header: str) -> str:
        """
        Translate the prefix of a string to its more descriptive version.

        This method first checks if the primary delimiter is in the input string.
        If so, it splits the string at the delimiter, translates the prefix (first
        part of the split), and then reassembles the string.

        Parameters
        ----------
        header : str
            The string whose prefix is to be translated.

        Returns
        -------
        str
            The string with the prefix translated to its more descriptive version.

        """
        if cls._HEADER_PRIMARY_DELIMITER not in header:
            return header
        first, second = header.split(cls._HEADER_PRIMARY_DELIMITER, 1)
        return cls._get_full_prefix(first) + cls._HEADER_PRIMARY_DELIMITER + second

    @classmethod
    def _remove_units(cls, header: str) -> str:
        """
        Remove any units from the input string, which are assumed to be enclosed in parentheses.

        This function uses a regular expression to find and remove anything
        enclosed in parentheses, including the parentheses themselves, from the
        input string. This is intended to remove units from a header string.

        Parameters
        ----------
        header : str
            The header string from which units will be removed.

        Returns
        -------
        str
            The processed header string with units removed.

        """
        return re.sub(rf"{cls._HEADER_PRIMARY_DELIMITER}\(.*\)", '', header)

    @classmethod
    def _replace_secondary_header_delimiters_with_spaces(cls, header: str) -> str:
        """
        Replace consecutive occurrences of the secondary header delimiter with a single space.

        This function uses a regular expression to find and replace any instances
        of one or more consecutive secondary header delimiters in the input string
        with a single space.

        Parameters
        ----------
        header : str
            The header string in which the secondary header delimiters will be replaced with spaces.

        Returns
        -------
        str
            The processed header string with secondary header delimiters replaced by spaces.

        """
        return re.sub(rf'{cls._HEADER_SECONDARY_DELIMITER}+', ' ', header)

    @staticmethod
    def _squeeze_spaces(s: str) -> str:
        """
        Remove consecutive spaces in a string and trim leading/trailing spaces.

        This function uses a regular expression to replace instances of one or
        more consecutive spaces with a single space, and then removes leading
        and trailing spaces from the resulting string.

        Parameters
        ----------
        s : str
            Input string that may contain extra spaces.

        Returns
        -------
        str
            The processed string with consecutive spaces squeezed to single
            spaces and leading/trailing spaces removed.

        """
        return re.sub(rf'\s+', ' ', s).strip()

    @classmethod
    def _format_label(cls, label: str) -> str:
        """
        Format a label by removing prefix, replacing delimiters with spaces and squeezing spaces.

        Parameters
        ----------
        label : str
            The label to format.

        Returns
        -------
        str
            The formatted label.

        """
        pipeline = [cls._remove_prefix, cls._replace_secondary_header_delimiters_with_spaces, cls._squeeze_spaces]
        return cls._apply_pipeline_to_col_name(label, pipeline)

    @classmethod
    def _format_title(cls, title: str) -> str:
        """
        Formats a title by translating prefix, removing units, replacing primary delimiter with ' - ',
        replacing other delimiters with spaces, capitalizing first letters and squeezing spaces.

        Parameters
        ----------
        title : str
            The title to format.

        Returns
        -------
        str
            The formatted title.

        """
        pipeline = [
            cls._translate_prefix,
            cls._remove_units,
            lambda s: re.sub(rf'{cls._HEADER_PRIMARY_DELIMITER}+', ' - ', s),
            cls._replace_secondary_header_delimiters_with_spaces,
            cls._capitalize_first_letters,
            cls._squeeze_spaces
        ]
        return cls._apply_pipeline_to_col_name(title, pipeline)

    @classmethod
    def produce_graphics(cls, graphics_dir: str | Path, manure_manager) -> None:
        """
        Generate a series of scatter plots from the given DataFrame's data.

        This method takes a DataFrame and a directory path. It processes the DataFrame's data,
        and creates and saves scatter plots for each column in the provided directory.

        Each scatter plot is made with respect to an anchor column and sorted by it.

        Parameters
        ----------
        graphics_dir : str or pathlib.Path
            The directory where the graphics files will be saved.
        manure_manager
            The manure manager object.

        Returns
        -------
        None

        """
        df = cls._create_dataframe_from_manure_manager_data(manure_manager)
        graphics_dir = Path(graphics_dir) / cls._DEFAULT_OUTPUT_DIR_NAME
        graphics_dir.mkdir(parents=True, exist_ok=True)
        pen_id = 'pen_id'
        simulation_day = 'simulation_day'
        plot_file_extension = '.png'
        fixed_cols = [pen_id, simulation_day]
        non_fixed_cols = [col for col in df.columns if all(fixed_col.lower() not in col.lower() for fixed_col in fixed_cols)]

        for col in non_fixed_cols:
            output_dir = graphics_dir / cls._extract_dir_name_from_col_name(col)
            output_dir.mkdir(parents=True, exist_ok=True)
            for val in df['pen_id'].unique():
                output_sub_dir = output_dir / ('Pen' + str(val))
                output_sub_dir.mkdir(parents=True, exist_ok=True)
                x_series = df.loc[df[pen_id] == val, simulation_day]
                y_series = df.loc[df[pen_id] == val, col]
                plot_name = f'Pen {val} - {cls._format_title(col)}'
                output_path = output_sub_dir / f'{plot_name}{plot_file_extension}'
                cls._make_simple_scatter_plot_with_matplotlib(
                    output_path=output_path,
                    x=x_series,
                    y=y_series,
                    x_label='Simulation Day',
                    y_label=cls._format_label(col),
                    title=plot_name,
                )

    @classmethod
    def _make_simple_scatter_plot_with_matplotlib(cls, output_path: Path, x: pd.Series, y: pd.Series, x_label: str,
                                                  y_label: str, title: str) -> None:
        """
        Create a scatter plot from two data series using matplotlib.

        This method takes two data series, labels, a title, and an output path,
        creates a scatter plot, and saves the plot to the output path.

        Parameters
        ----------
        output_path : pathlib.Path
            The path where the scatter plot will be saved.
        x : pandas.Series
            The data series for the x-axis.
        y : pandas.Series
            The data series for the y-axis.
        x_label : str
            The label for the x-axis.
        y_label : str
            The label for the y-axis.
        title : str
            The title of the scatter plot.

        Returns
        -------
        None

        """
        if y.dtype.kind not in 'iuf' or y.hasnans:
            return
        small, medium, large = 10, 12, 16
        plt.style.use('ggplot')
        plt.scatter(x, y, alpha=0.7, c='#1746A2', s=25)
        plt.xlabel(x_label, fontsize=small)
        plt.ylabel(y_label, fontsize=small)
        plt.title(title, fontsize=medium)
        locs, _ = plt.xticks()
        plt.xticks([int(loc) for loc in locs if loc >= 0], fontsize=small)
        plt.yticks(fontsize=small)
        # plt.legend([f'{y_label}'], loc='best', frameon=False, fontsize=small)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0.2)
        plt.close()
