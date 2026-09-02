from enum import Enum
from pathlib import Path
from shared_data_types import POOL_ELEMENT_TYPE
from typing import Any, Union

import pandas as pd


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

    def __init__(self, metadata_prefix: str, supported_prefixes: dict[str, str]) -> None:
        self.metadata_prefix = metadata_prefix
        # TODO Since this can be 1 of 2 things based on whether it's an e2e run or regular simulation, maybe this should
        # not be passed in as an argjust and instead be done via a setter function depending on the use case?
        self.supported_filter_types_prefixes = supported_prefixes

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
        pass

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
            output_manager = OutputManager()
            modified_data_dict = output_manager._add_detailed_values(
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
        pass

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
        pass

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
        pass

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
        pass

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

            output_manager = OutputManager()
            output_manager._get_units_substr("temperature", "C")

        ' (C)'

        .. code-block:: python

            output_manager._get_units_substr("velocity", {"magnitude": "m/s", "direction": "degrees"}, "magnitude")

        ' (m/s)'

        .. code-block:: python

            output_manager._get_units_substr("velocity", {"magnitude": "m/s", "direction": "degrees"}, "direction")

        ' (degrees)'

        .. code-block:: python

            output_manager._get_units_substr("coordinates", {"x": "m", "y": "m"})

        """
        pass

    def _dict_to_file_csv(self, data_dict: dict[str, Any], path: Path, direction: str | None = "portrait") -> None:
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
        pass

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
        pass

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
        pass

    def _load_filter_file_content(self, path: Path) -> tuple[list[dict[str, Any]], str | None]:
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
        pass

    def _save_to_json(
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
        pass

    def _read_variables_pool_file(
        self,
        file_path: Path,
        info_map: dict[str, Any],
    ) -> dict[str, list[Any]]:
        """Reads a ``variables_pool`` JSON file and returns its contents."""
        pass

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
        pass

    def is_file_in_dir(self, dir_path: Path, file_path: Path) -> bool:
        """
        Checks if a file path is in the provided directory.

        Parameters
        ----------
        dir_path : Path
            Path to the directory to be checked.
        file_path : Path
            Path to file to be checked.

        Returns
        -------
        bool
            Whether the file is in the provided directory.
        """
        pass

    def create_directory(self, path: Path) -> None:
        """
        Creates a directory from the provided path if it does not already exist.

        Parameters
        ----------
        path : Path
            The path where the directory will be created if it does not already exist.
        """
        pass

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
        ``OriginLabel.NONE`` is returned, and an error is added to the Output Manager's errors pool.
        """
        pass

    def _normalize_module_header(json_key: str) -> str:
        """Normalizes the module header from a JSON key."""
        pass
