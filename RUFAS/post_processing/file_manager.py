from enum import Enum
import json
import os
from pathlib import Path
from RUFAS.post_processing.rufas_logger import get_logger
from RUFAS.post_processing.shared_data_types import POOL_ELEMENT_TYPE
from RUFAS.util import Utility
from typing import Any, Callable, TextIO, Union

import pandas as pd

logger = get_logger(__name__)
DISCLAIMER_MESSAGE = "Under construction, use the results with caution."


class OriginLabel(Enum):
    """
    An enumeration representing the different labels for data origins when generating JSON output files.

    Attributes
    ----------
    TRUE_AND_REPORT_ORIGINS : str
        Indicates that both the true origin and report origin should be included.
    TRUE_ORIGIN : str
        Indicates that only the true origin should be included.
    REPORT_ORIGIN : str
        Indicates that only the report origin should be included.
    NONE : str
        Indicates that no origin information should be included.
    """

    TRUE_AND_REPORT_ORIGINS = "true and report origins"
    TRUE_ORIGIN = "true origin"
    REPORT_ORIGIN = "report origin"
    NONE = "none"


class FileManager:
    """
    Class overseeing file management activities in RuFaS.
    """

    JSON_OUTPUT_MAX_RECURSIVE_DEPTH = 4

    def __init__(self, metadata_prefix_getter: Callable[[], str], supported_prefixes: dict[str, str]) -> None:
        self._metadata_prefix_getter = metadata_prefix_getter
        self.supported_filter_types_prefixes = supported_prefixes

    @property
    def metadata_prefix(self) -> str:
        """Returns the current metadata prefix."""
        return self._metadata_prefix_getter()

    def dict_to_file_json(
        self,
        data_dict: dict[str, Any],
        path: Path,
        minify_output_file: bool = False,
        origin_label: OriginLabel = OriginLabel.NONE,
    ) -> None:
        """
        Saves a dictionary into a JSON file

        Parameters
        ----------
        data_dict : dict[str, Any]
            The dictionary to be saved

        path : Path
            The path to the file to be saved

        minify_output_file : bool
            Boolean flag indicating whether to minify the output JSON file.

        origin_label : OriginLabel, default ``OriginLabel.NONE``
            The origin label specifying the format of the detailed values string.

        Raises
        ------
        Exception
            If an error occurs while saving to the file.

        Notes
        -----
        The dictionary is first converted to a serializable format using
        ``Utility.make_serializable()``.

        The file is saved with no indentation.

        If you want to save time and space, limit the maximum depth of the
        serialized dictionary using the ``max_depth`` parameter. You can also set the
        ``minify_output_file`` flag to ``True`` to minimize the output JSON file size.
        """
        logger.info(
            f"Attempting to save to {path}.",
            extra={"rufas_log_name": "Save Dict To JSON Try"},
        )
        data_dict = {**{"DISCLAIMER": DISCLAIMER_MESSAGE}, **data_dict}
        try:
            with open(path, "w", encoding="utf-8") as json_file:
                data_dict = self._add_detailed_values(data_dict, origin_label)
                if minify_output_file:
                    json.dump(
                        Utility.make_serializable(data_dict, max_depth=self.JSON_OUTPUT_MAX_RECURSIVE_DEPTH),
                        json_file,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                else:
                    json.dump(
                        Utility.make_serializable(data_dict, max_depth=self.JSON_OUTPUT_MAX_RECURSIVE_DEPTH),
                        json_file,
                        indent=2,
                        ensure_ascii=False,
                    )
                logger.info(
                    f"Successfully saved to {path}.",
                    extra={"rufas_log_name": "Save Dict To Json Success"},
                )
        except Exception as e:
            raise type(e)(f"An error occurred while saving to {path}: {str(e)}") from e

    def _add_detailed_values(self, data_dict: dict[str, Any], origin_label: OriginLabel) -> dict[str, Any]:
        """
        Adds a ``detailed_values`` list to each sub-dictionary to replace the original ``values`` list.

        Parameters
        ----------
        data_dict : dict[str, Any]
            The input dictionary containing keys that may map to other dictionaries with ``info_maps`` and ``values``
            keys. ``info_maps`` should contain a list of dictionaries, each with a ``data_origin`` key indicating the
            source of the data. ``values`` should contain a list of values corresponding to these origins.
        origin_label : OriginLabel
            The origin label specifying the format of the detailed values string.

        Returns
        -------
        dict[str, Any]
            The modified dictionary with a ``detailed_values`` list added to each sub-dictionary that meets the
            criteria. This list provides detailed information on the origins and units of each value.

        Notes
        -----
        When the ``OriginLabel`` is set to anything other than ``NONE``, this method iterates over each key in the
        provided dictionary, and it will create a ``detailed_values`` list that integrates the data origins,
        values, and units. Depending on the ``origin_label`` parameter, the format of the detailed values will vary:

        - If ``origin_label`` is ``OriginLabel.TRUE_AND_REPORT_ORIGINS``, the format is:
          ``"[true_origin_class.true_origin_function]->[report_origin]: value (units)"``
          or ``"[true_origin_class.true_origin_function]->[report_origin]: subkey1 = value1 (units1),
           subkey2 = value2 (units2), ..."`` if the value is a dictionary.

        - If ``origin_label`` is ``OriginLabel.TRUE_ORIGIN``, the format is:
          ``"[true_origin_class.true_origin_function]: value (units)"``
          or ``"[true_origin_class.true_origin_function]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."``
          if the value is a dictionary.

        - If ``origin_label`` is ``OriginLabel.REPORT_ORIGIN``, the format is:
          ``"[report_origin]: value (units)"``
          or ``"[report_origin]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."``
          if the value is a dictionary.

        - If ``origin_label`` is ``OriginLabel.NONE``, there will be no ``detailed_values`` information added.

        Examples
        --------
        .. code-block:: python

            example_data_dict = {
                "AnimalModuleReporter.report_daily_animal_population.num_animals": {
                    "info_maps": [
                        {"data_origin": [["AnimalManager", "daily_updates"]], "units": "animals"},
                        {"data_origin": [["AnimalManager", "daily_updates"]], "units": "animals"}
                    ],
                    "values": [193, 194]
                },
                "WeatherModuleReporter.report_daily_weather.temperature": {
                    "info_maps": [
                        {"data_origin": [["WeatherManager", "daily_temperature"]],
                         "units": {"avg": "°C", "min": "°C", "max": "°C"}},
                        {"data_origin": [["WeatherManager", "daily_temperature"]],
                         "units": {"avg": "°C", "min": "°C", "max": "°C"}}
                    ],
                    "values": [
                        {"avg": 25.5, "min": 18.2, "max": 32.1},
                        {"avg": 26.1, "min": 19.7, "max": 33.4}
                    ]
                }
            }
            modified_data_dict = self._add_detailed_values(
                example_data_dict, OriginLabel.TRUE_AND_REPORT_ORIGINS
            )
            assert modified_data_dict[
                "AnimalModuleReporter.report_daily_animal_population.num_animals"]["detailed_values"
            ] == [
                "[AnimalManager.daily_updates]->[AnimalModuleReporter.report_daily_animal_population.num_animals]: "
                "193 (animals)",
                "[AnimalManager.daily_updates]->[AnimalModuleReporter.report_daily_animal_population.num_animals]: "
                "194 (animals)"
            ]
            assert modified_data_dict[
                "WeatherModuleReporter.report_daily_weather.temperature"]["detailed_values"
            ] == [
                "[WeatherManager.daily_temperature]->[WeatherModuleReporter.report_daily_weather.temperature]: "
                "avg = 25.5 (°C), min = 18.2 (°C), max = 32.1 (°C)",
                "[WeatherManager.daily_temperature]->[WeatherModuleReporter.report_daily_weather.temperature]: "
                "avg = 26.1 (°C), min = 19.7 (°C), max = 33.4 (°C)"
            ]

        """
        if origin_label is OriginLabel.NONE:
            return data_dict

        for key, sub_data_dict in data_dict.items():
            if not self._can_add_detailed_values(sub_data_dict):
                continue

            data_origins: list[list[tuple[str, str]]] = []
            units: list[str | dict[str, str]] = []
            for info_map in sub_data_dict["info_maps"]:
                if "data_origin" not in info_map:
                    break
                if "units" not in info_map:
                    break
                data_origins.append(info_map["data_origin"])
                units.append(info_map["units"])

            if len(data_origins) != len(sub_data_dict["values"]) or len(units) != len(sub_data_dict["values"]):
                continue

            detailed_values: list[str] = []
            for index, value in enumerate(sub_data_dict["values"]):
                for origin in data_origins[index]:
                    detailed_origin_data = {
                        "true_origin_class": origin[0],
                        "true_origin_function": origin[1],
                        "report_origin": key,
                        "value": value,
                        "units": units[index],
                    }
                    detailed_value = self._format_detailed_value_str(origin_label, detailed_origin_data)
                    detailed_values.append(detailed_value)

            sub_data_dict["detailed_values"] = detailed_values

        return data_dict

    def _format_detailed_value_str(self, origin_label: OriginLabel, data: dict[str, Any]) -> str:
        """
        Formats the detailed values string based on the provided origin label and data.

        Parameters
        ----------
        origin_label : OriginLabel
            The origin label specifying the format of the detailed values string.

        data : dict[str, Any]
            A dictionary containing the necessary data for formatting the detailed values string.
            It should have the following keys:
            - ``true_origin_class``: The class name of the true origin.
            - ``true_origin_function``: The function name of the true origin.
            - ``report_origin``: The report origin which already includes the class and function names.
            - ``value``: The value associated with the origin.
            - ``units``: The units associated with the value.

        Returns
        -------
        str
            The formatted detailed values string based on the provided origin label and data.

        Notes
        -----
        The format of the detailed values string depends on the ``origin_label`` parameter:
        - If ``origin_label`` is `OriginLabel.TRUE_AND_REPORT_ORIGINS`, the format is:
          ``"[true_origin_class.true_origin_function]->[report_origin]: value (units)"``
          or ``"[true_origin_class.true_origin_function]->[report_origin]: subkey1 = value1 (units1),
           subkey2 = value2 (units2), ..."`` if the value is a dictionary.

        - If ``origin_label`` is ``OriginLabel.TRUE_ORIGIN``, the format is:
          ``"[true_origin_class.true_origin_function]: value (units)"``
          or ``"[true_origin_class.true_origin_function]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."``
          if the value is a dictionary.

        - If ``origin_label`` is ``OriginLabel.REPORT_ORIGIN``, the format is:
          ``"[report_origin]: value (units)"``
          or ``"[report_origin]: subkey1 = value1 (units1), subkey2 = value2 (units2), ..."``
          if the value is a dictionary.

        - If ``origin_label`` is ``OriginLabel.NONE``, there will be no detailed_values information so no formatting
        will occur.
        """
        true_origin_class = data["true_origin_class"]
        true_origin_function = data["true_origin_function"]
        report_origin = data["report_origin"]
        value = data["value"]
        units = data["units"]

        origin_label_str = ""
        if origin_label is OriginLabel.TRUE_AND_REPORT_ORIGINS:
            origin_label_str = f"[{true_origin_class}.{true_origin_function}]->[{report_origin}]"
        elif origin_label is OriginLabel.TRUE_ORIGIN:
            origin_label_str = f"[{true_origin_class}.{true_origin_function}]"
        elif origin_label is OriginLabel.REPORT_ORIGIN:
            origin_label_str = f"[{report_origin}]"

        if isinstance(value, dict) and isinstance(units, dict):
            formatted_values = [f"{subkey} = {value[subkey]} ({units[subkey]})" for subkey in value.keys()]
            return (
                f"{origin_label_str}: {', '.join(formatted_values)}"
                if origin_label_str
                else f"{', '.join(formatted_values)}"
            )

        return f"{origin_label_str}: {value} ({units})" if origin_label_str else f"{value} ({units})"

    def _can_add_detailed_values(self, sub_data_dict: dict[str, Any]) -> bool:
        """
        Checks if the provided ``sub_data_dict`` has the necessary structure and data to add detailed values.

        Parameters
        ----------
        sub_data_dict : dict[str, Any]
            The dictionary to check for compatibility with adding detailed values.

        Returns
        -------
        bool
            ``True`` if the sub_data_dict meets the requirements for adding detailed values, ``False`` otherwise.

        Notes
        -----
        The ``sub_data_dict`` should meet the following requirements:
        - It must be a dictionary.
        - It must contain the keys ``info_maps`` and ``values``.
        - The length of the ``info_maps`` list and the ``values`` list must be equal.
        """
        if not isinstance(sub_data_dict, dict):
            return False
        if "info_maps" not in sub_data_dict or "values" not in sub_data_dict:
            return False
        if not sub_data_dict["info_maps"] or not sub_data_dict["values"]:
            return False
        if len(sub_data_dict["info_maps"]) != len(sub_data_dict["values"]):
            return False
        return True

    def _dict_to_csv_column_list(self, variable_name: str, data_dict: dict[str, list[Any]]) -> list[pd.Series]:
        """
        Turns a dictionary to a list of csv columns.

        Parameters
        ----------
        variable_name : str
            The name of the variable having its values written into a CSV column.
        data_dict : dict[str, list[Any]]
            The dictionary to read from

        Returns
        -------
        list[pd.Series]
            A list of ``(column_name, column_data)`` named series.
        """
        column_list = []
        units = data_dict["info_maps"][0]["units"] if data_dict.get("info_maps", []) else None
        data_list = data_dict["values"]
        if data_list and isinstance(data_list[0], dict):
            csv_column_lists: dict[str, list[Any]] = {subkey: [] for item in data_list for subkey in item.keys()}
            for nested_dictionary in data_list:
                for subkey, value in nested_dictionary.items():
                    csv_column_lists[subkey].append(value)

            for subkey in csv_column_lists.keys():
                column_title = f"{variable_name}.{subkey}{self._get_units_substr(variable_name, units, subkey)}"
                column_list.append(pd.Series(csv_column_lists[subkey], dtype=object, name=column_title))
        else:
            column_title = f"{variable_name}{self._get_units_substr(variable_name, units)}"
            column_list.append(pd.Series(data_list, dtype=object, name=column_title))

        return column_list

    def _get_units_substr(
        self, variable_name: str, units: str | dict[str, str] | None, subkey: str | None = None
    ) -> str:
        """
        Get the units substring for a column title.

        Parameters
        ----------
        variable_name : str
            The name of the variable or group of variables associated with the units.
        units : str | dict[str, str] | None
            The units associated with the data.
        subkey : str | None, optional
            The subkey to retrieve the units for, if units is a dictionary. Default is ``None``.

        Returns
        -------
        str
            The formatted units substring for the column title.

        Examples
        --------
        .. code-block:: python

            self._get_units_substr("temperature", "C")

        ' (C)'

        .. code-block:: python

            self._get_units_substr("velocity", {"magnitude": "m/s", "direction": "degrees"}, "magnitude")

        ' (m/s)'

        .. code-block:: python

            self._get_units_substr("velocity", {"magnitude": "m/s", "direction": "degrees"}, "direction")

        ' (degrees)'

        .. code-block:: python

            self._get_units_substr("coordinates", {"x": "m", "y": "m"})

        """
        if not isinstance(units, dict):
            return f" ({units})" if units else ""

        if variable_name in units:
            return f" ({units[variable_name]})"

        if subkey is None:
            logger.error(
                f"Variable {variable_name} has a dictionary for its 'units' property, "
                f"but the 'values' associated with this variable are not dictionaries themselves.",
                extra={"rufas_log_name": "Units Subkey Missing"},
            )
            return ""

        if subkey in units:
            return f" ({units[subkey]})"

        logger.error(
            f"Key '{subkey}' not found in the units dictionary for variable '{variable_name}'.",
            extra={"rufas_log_name": "Units Key Error"},
        )

        return ""

    def dict_to_file_csv(self, data_dict: dict[str, Any], path: Path, direction: str | None = "portrait") -> None:
        """
        Saves a dictionary to a csv file.

        Parameters
        ----------
        data_dict : dict[str, Any]
            The dictionary to be saved.
        path : Path
            The path to the file to be saved.
        direction : str | None
            The direction of the csv file, either portrait or landscape, default is portrait.
            If ``None`` is provided, the file will be saved in default portrait orientation.
        """
        logger.info(
            f"Attempting to save to {path}.",
            extra={"rufas_log_name": "Save Dict To CSV Try"},
        )

        if len(data_dict) == 0:
            logger.warning(
                f"Nothing to save to {path}. Data dictionary is empty.",
                extra={"rufas_log_name": "Dict To CSV Save Failure"},
            )
            return

        csv_columns = []
        for variable_name, variable_data in data_dict.items():
            csv_column_data = self._dict_to_csv_column_list(variable_name, variable_data)
            csv_columns.extend(csv_column_data)

        df = pd.concat(csv_columns, axis=1)
        disclaimer_column = [DISCLAIMER_MESSAGE] + [""] * (len(df) - 1)
        disclaimer_df = pd.DataFrame({"DISCLAIMER": disclaimer_column})
        df = pd.concat([disclaimer_df, df], axis=1)

        if direction == "portrait" or direction is None:
            df.to_csv(path, index=False, encoding="utf-8")
        elif direction == "landscape":
            df.T.to_csv(path, encoding="utf-8")
        else:
            logger.error(
                f"The provided direction '{direction}' is not recognized. "
                f"Saving the output in portrait direction as default.",
                extra={"rufas_log_name": "Unknown Direction for CSV Output"},
            )
            df.to_csv(path, index=False, encoding="utf-8")

        logger.info(
            f"Successfully saved to {path}.",
            extra={"rufas_log_name": "Save Dict To CSV Success"},
        )

    def _list_to_file_txt(self, data_list: list[str], path: Path) -> None:
        """
        Saves a list into a text file

        Parameters
        ----------
        data_list : list[str]
            The list of variable names to be saved
        path : Path
            The path to the file to be saved

        Raises
        ------
        Exception
            If an error occurs while saving to the file.
        """
        logger.info(
            f"Attempting to save to {path}.",
            extra={"rufas_log_name": "Save Text File Try"},
        )

        try:
            with open(path, "w") as var_names_file:
                self._write_disclaimer(var_names_file)
                var_names_file.writelines(data_list)
                logger.info(
                    f"Successfully saved to {path}.",
                    extra={"rufas_log_name": "Save Text File Success"},
                )
        except Exception as e:
            raise type(e)(f"An error occurred while saving to {path}: {str(e)}") from e

    def _write_disclaimer(self, file_pointer: TextIO) -> None:
        """
        Writes the predefined disclaimer message to a given file.

        Parameters
        ----------
        file_pointer: TextIO
            A file-like object (supporting the ``.write()`` method) that points to the file where the disclaimer should
            be written.

        Example
        -------
        .. code-block:: python

            output_manager = OutputManager()
            import io
            file_like_string = io.StringIO()
            output_manager._write_disclaimer(file_like_string)
            assert file_like_string.getvalue() == DISCLAIMER_MESSAGE + "\\n"

        """
        file_pointer.write(DISCLAIMER_MESSAGE + "\n")

    def generate_file_name(self, base_name: str, extension: str, include_millis: bool = False) -> str:
        """
        Generates a timestamped file name from a base name and extension.

        Parameters
        ----------
        base_name : str
            Base name for the file.
        extension : str
            File extension without the leading dot.
        include_millis : bool, optional
            Whether to include milliseconds in the timestamp. Defaults to ``False``.

        Returns
        -------
        str
            File name in the form ``{metadata_prefix}_{base_name}_{timestamp}.{extension}``.
        """
        timestamp: str = Utility.get_timestamp(include_millis=include_millis)
        return f"{self.metadata_prefix}_{base_name}_{timestamp}.{extension}"

    def load_filter_file_content(self, path: Path) -> tuple[list[dict[str, Any]], str | None]:
        """
        Loads and processes the content of a filter file from the specified path.

        Parameters
        ----------
        path : Path
            The path to the filter file (either .json or .txt).

        Returns
        -------
        tuple[list[dict[str, str|int]], str | None]
            - A list of dictionaries, each containing the loaded filter content, with keys and values depending on the
            file type.
            - A string representing the output CSV direction, either "portrait" or "landscape". If no direction is
            specified, ``None`` is returned.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.

        json.JSONDecodeError
            If there is an issue with parsing a JSON file.

        UnicodeDecodeError
            If there is an issue with decoding a text file.

        Exception
            If an unsupported file format is encountered; only .json and .txt are supported.

        Notes
        -----
        This method attempts to open and process a filter file located at the specified path.
        It supports two file formats: JSON and plain text (.txt). If the file is a JSON file,
        it loads the JSON content into a dictionary. If the file is a .txt file, it reads the
        lines and creates a dictionary with a "filters" key and a list of filter elements as values.
        Unsupported file formats will raise an exception.

        This method is used to handle loading filter content from external files, which are
        used to define filtering criteria for the ``variables_pool``.
        """
        logger.info(
            f"Attempting to open {path}.",
            extra={"rufas_log_name": "Opening Filter File Attempt"},
        )
        try:
            with open(path) as filter_file:
                direction: str | None = None
                if path.suffix == ".json":
                    json_content = json.load(filter_file)
                    direction = json_content.get("direction", None)
                    if "multiple" in json_content.keys():
                        result = json_content["multiple"]
                    else:
                        result = [json_content]
                elif path.suffix == ".txt":
                    list_of_elements = [element for element in filter_file.read().splitlines() if element]
                    filter_by_exclusion = list_of_elements[0] == "exclude"
                    if filter_by_exclusion:
                        list_of_elements.pop(0)
                    result = [{"filters": list_of_elements, "filter_by_exclusion": filter_by_exclusion}]
                else:
                    raise Exception(f"Unsupported file format {path.suffix}; only json and txt are supported.")
            logger.info(
                f"Successfully opened {path}.",
                extra={"rufas_log_name": "Filter File Opening Successful"},
            )
            return result, direction
        except FileNotFoundError:
            logger.error(
                f"The file '{path}' does not exist.",
                extra={"rufas_log_name": "Filter File Not Found Error"},
            )
            raise
        except json.JSONDecodeError as e:
            logger.error(
                str(e),
                extra={"rufas_log_name": "Filter File JSON Parsing Error"},
            )
            raise
        except UnicodeDecodeError as e:
            logger.error(
                str(e),
                extra={"rufas_log_name": "Filter File Text Decoding Error"},
            )
            raise
        except Exception as e:
            logger.error(
                str(e),
                extra={"rufas_log_name": "Filter File Unexpected Error"},
            )
            raise

    def save_to_json(
        self,
        filter_file: str,
        save_path: Path,
        filtered_pool: dict[str, POOL_ELEMENT_TYPE],
        filter_content: dict[str, Union[str, int]],
    ) -> None:
        """
        Saves the filtered pool to a JSON file.

        Parameters
        ----------
        filter_file : str
            The name of the filter file being processed.
        save_path : Path
            The directory path where the JSON file will be saved.
        filtered_pool : dict[str, POOL_ELEMENT_TYPE]
            The pool of filtered data to be saved.
        filter_content : dict[str, Union[str, int]]
            Additional content from the filter that might influence the file naming.
        """
        if "e2e_comparison" in filter_file:
            base_name = f"comparison_{filter_content['name']}"
        elif "name" in filter_content:
            base_name = f"saved_variables_{filter_content['name']}"
        else:
            base_name = f"saved_variables_{filter_file}"

        origin_label = self._get_origin_label(filter_content)
        file_name = self.generate_file_name(base_name, "json")
        file_path = save_path / file_name
        self.dict_to_file_json(filtered_pool, file_path, origin_label=origin_label)

    def read_variables_pool_file(
        self,
        file_path: Path,
    ) -> dict[str, list[Any]]:
        """Reads a ``variables_pool`` JSON file and returns its contents."""
        logger.info(
            f"Attempting to open {str(file_path)}.",
            extra={"rufas_log_name": "Reading JSON File Attempt"},
        )
        try:
            with open(file_path) as file:
                loaded_pool: dict[str, list[Any]] = json.load(file)
                loaded_pool.pop("DISCLAIMER", None)
                logger.info(
                    f"Successfully loaded pool data from {str(file_path)}.",
                    extra={"rufas_log_name": "Pool Load Successful"},
                )
                return loaded_pool
        except FileNotFoundError:
            logger.error(
                f"The file '{str(file_path)}' does not exist.", extra={"rufas_log_name": "Pool File Not Found Error"}
            )
            raise
        except json.JSONDecodeError as e:
            logger.error(str(e), extra={"rufas_log_name": "JSON Pool File Parsing Error"})
            raise

    def clear_output_dir(self, vars_file_path: Path, output_dir: Path) -> None:
        """
        Clears the output directory if ``vars_file_path`` not in output directory.

        Parameters
        ----------
        vars_file_path : Path
            Path to file used to load ``variables_pool``.
        output_dir : Path
            The directory for saving output.
        """
        is_file_found_in_dir = self.is_file_in_dir(output_dir, vars_file_path)
        if is_file_found_in_dir:
            logger.error(
                f"{vars_file_path} in output directory.", extra={"rufas_log_name": "Can't clear output directory"}
            )
        else:
            keep_list = [".keep", "output_filters"]
            Utility.empty_dir(output_dir, keep=keep_list)
            logger.info(
                "Provided variables-file path was not in output directory.",
                extra={"rufas_log_name": "Output directory successfully cleared"},
            )

    def is_file_in_dir(self, dir_path: Path, file_path: Path | None) -> bool:
        """
        Checks if a file path is in the provided directory.

        Parameters
        ----------
        dir_path : Path
            Path to the directory to be checked.
        file_path : Path | None
            Path to the file to be checked. If None, returns False.

        Returns
        -------
        bool
            Whether the file is in the provided directory.
        """
        if file_path is None:
            return False
        file_path = file_path.resolve()
        directory_path = dir_path.resolve()

        return directory_path == file_path or directory_path in file_path.parents

    def create_directory(self, path: Path) -> None:
        """
        Creates a directory from the provided path if it does not already exist.

        Parameters
        ----------
        path : Path
            The path where the directory will be created if it does not already exist.
        """
        logger.info(
            f"Attempting to create a new directory at {path}.",
            extra={"rufas_log_name": "Attempting to create a new directory"},
        )
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"Created a new directory at {path}.",
                extra={"rufas_log_name": "Directory successfully created."},
            )
        except PermissionError as e:
            logger.error(
                f"{path=}; Exception: {str(e)}",
                extra={"rufas_log_name": "Directory Creation Permissions Error"},
            )
        except Exception as e:
            logger.error(
                f"{path=}; Exception: {str(e)}",
                extra={"rufas_log_name": "Directory Creation mkdir Error"},
            )

    def _get_origin_label(self, filter_content: dict[str, str | int]) -> OriginLabel:
        """
        Retrieves the origin label from the provided filter content.

        Parameters
        ----------
        filter_content : dict[str, str | int]
            A dictionary containing filter information, which may include the ``origin_label`` key.

        Returns
        -------
        OriginLabel
            The origin label corresponding to the value in the filter content.
            If the ``origin_label`` key is not present or has an invalid value, ``OriginLabel.NONE`` is returned.

        Notes
        -----
        This method checks the value of the ``origin_label`` key in the provided ``filter_content`` dictionary.
        If the value is a valid string matching one of the supported options defined in the ``OriginLabel`` enum,
        the corresponding ``OriginLabel`` member is returned. If the value is invalid or the key is not present,
        ``OriginLabel.NONE`` is returned, and an error is logged.
        """
        if "origin_label" not in filter_content:
            return OriginLabel.NONE

        origin_label_value = filter_content["origin_label"]
        supported_options = [label.value for label in OriginLabel]

        if not isinstance(origin_label_value, str):
            logger.error(
                f"Origin label must be a string. Received '{origin_label_value}' of type {type(origin_label_value)}.",
                extra={"rufas_log_name": "Origin Label Error"},
            )
            return OriginLabel.NONE

        if origin_label_value not in supported_options:
            logger.error(
                f"Origin label must be one of {supported_options}. Received '{origin_label_value}'.",
                extra={"rufas_log_name": "Origin Label Error"},
            )
            return OriginLabel.NONE

        return OriginLabel(origin_label_value)

    @staticmethod
    def normalize_module_header(json_key: str) -> str:
        """Normalizes the module header from a JSON key."""
        module = json_key.split(".", 1)[0].lower()
        if module == "animal":
            return "Animal"
        if module == "crop_and_soil":
            return "CropAndSoil"
        if module == "manure":
            return "Manure"
        return json_key.split(".", 1)[0]

    def read_e2e_comparison_files(
        self,
        json_output_directory: Path,
        output_prefixes: list[str],
        failed_e2e_groups: list[str] | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Reads end-to-end test comparison files and groups their contents by output prefix.

        Parameters
        ----------
        json_output_directory : Path
            The directory containing the JSON comparison files.
        output_prefixes : list[str]
            The output prefixes used to identify relevant comparison files.
        failed_e2e_groups : list[str] | None, default None
            The output prefixes of failed tasks whose comparison files should
            be ignored because they may have been left by an earlier run.

        Returns
        -------
        dict[str, list[dict[str, Any]]]
            The contents of the comparison files grouped by output prefix.

        """
        failed_e2e_groups = failed_e2e_groups or []
        comparison_results: dict[str, list[dict[str, Any]]] = {}

        logger.info(
            f"Attempting to read E2E comparison files from {json_output_directory}.",
            extra={"rufas_log_name": "Reading E2E Comparison Files Attempt"},
        )

        for filename in os.listdir(json_output_directory):
            if "comparison" not in filename.lower() or not filename.endswith(".json"):
                continue

            matched_prefix = next(
                (prefix for prefix in output_prefixes if prefix.lower() in filename.lower()),
                None,
            )

            if matched_prefix is None:
                logger.error(
                    f"No matching output prefix found in filename: {filename}",
                    extra={"rufas_log_name": "Invalid E2E Output Prefix"},
                )
                continue

            if matched_prefix in failed_e2e_groups:
                continue

            file_path = json_output_directory / filename

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data: dict[str, Any] = json.load(file)
            except (OSError, ValueError) as exc:
                logger.error(
                    f"Failed to read {file_path}: {exc}",
                    extra={"rufas_log_name": "E2E Comparison File Reading Error"},
                )
                continue

            comparison_results.setdefault(matched_prefix, []).append(data)

        logger.info(
            f"Finished reading E2E comparison files from {json_output_directory}. "
            f"Successfully read {sum(len(files) for files in comparison_results.values())} files.",
            extra={"rufas_log_name": "E2E Comparison File Reading Complete"},
        )

        return comparison_results
