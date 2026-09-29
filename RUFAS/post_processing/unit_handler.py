import logging
import re
from typing import Any

from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits


class UnitHandler:
    """
    Handles the measurement units of the data reported by ReportGenerator.

    Parameters
    ----------
    metadata_prefix : str, default ""
        The identifier for the metadata task being run, used for logging.

    Attributes
    ----------
    metadata_prefix : str
        The identifier for the metadata task being run, used for logging.
    """

    def __init__(self, metadata_prefix: str = "") -> None:
        """Initializes the UnitHandler."""
        self.metadata_prefix: str = metadata_prefix
        # TODO use the RuFaS logger helpers once the new logging system is merged (#3192)
        self._logger: logging.Logger = logging.getLogger(f"RUFAS.{self.__class__.__name__}")

    def _log(self, level: int, name: str, message: str, function_name: str) -> None:
        """
        Logs a message directly to Python's logging system.

        Parameters
        ----------
        level : int
            The Python logging level of the message.
        name : str
            The name of the log, warning, or error.
        message : str
            The message to be logged.
        function_name : str
            The name of the function logging the message.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": function_name,
            "metadata_prefix": self.metadata_prefix,
        }
        self._logger.log(level, message, extra={"rufas_name": name, "rufas_info_map": info_map})

    @staticmethod
    def add_var_units(report_data: dict[str, dict[str, list[Any]]]) -> dict[str, dict[str, list[Any]]]:
        """
        Adds variable units to variable name.

        Parameters
        ----------
        report_data : dict[str, dict[str, list[Any]]]
            The data to be reported.

        Returns
        -------
        dict[str, dict[str, list[Any]]]
            The updated data with units added.
        """
        updated_data: dict[str, dict[str, list[Any]]] = {}
        if not any("info_maps" in details for details in report_data.values()):
            return report_data
        for var_name, details in report_data.items():
            unit_info = details["info_maps"][0]["units"]
            if isinstance(unit_info, dict):
                unit = unit_info.get(var_name, "not available")
            else:
                unit = unit_info

            new_var_name = f"{var_name} ({unit})"
            updated_data[new_var_name] = details

        return updated_data

    def add_units_to_constants(self, constants_config: dict[str, int | float]) -> dict[str, int | float]:
        """
        Checks constants provided in the filter file against ``GeneralConstants`` and adds appropriate measurement
        units.

        Parameters
        ----------
        constants_config : dict[str, int | float]
            A dictionary containing the names and values of the constants to be added to the report data.

        Returns
        -------
        dict[str, int | float]
            The updated constants configuration.
        """
        updated_constants_config: dict[str, int | float] = {}
        for name in constants_config.keys():
            normalized_provided_name = self._normalize_constant_name(name)
            matching_constant = ""
            for attribute in dir(GeneralConstants):
                if attribute.startswith("__"):
                    continue
                normalized_attribute_name = self._normalize_constant_name(attribute)
                if normalized_attribute_name == normalized_provided_name:
                    matching_constant = str(attribute)
                    break
            else:
                self._log(
                    logging.WARNING,
                    "report_generation_warning",
                    f"No matching GeneralConstant found for filter constant {name}.",
                    self.add_units_to_constants.__name__,
                )
            unit_for_constant = GeneralConstants.CONSTANTS_TO_UNITS.get(matching_constant, "unit_not_found")
            constant_with_units = f"{name}_({unit_for_constant})"
            updated_constants_config[constant_with_units] = constants_config[name]

        return updated_constants_config if len(updated_constants_config) > 0 else constants_config

    @staticmethod
    def _normalize_constant_name(name: str) -> str:
        """Normalizes the constant name by converting to lowercase and removing underscores and spaces."""
        return re.sub(r"[\s_]", "", name).lower()

    def aggregate_units(
        self,
        report_data: dict[str, list[Any]],
        operation: str | None,
        simplify_units: bool,
    ) -> str:
        """
        Creates the appropriate units for the associated aggregator function used.

        Parameters
        ----------
        report_data : dict[str, list[Any]]
            The data pool to be aggregated, structured as a dictionary of lists.
        operation : str | None
            The key of the aggregation function to be used, or ``None`` if the aggregation function is not one of the
            supported aggregation functions.
        simplify_units : bool
            Whether to simplify and reduce the units.

        Returns
        -------
        str
            The expected units of aggregating the report data using the accompanying aggregator function.

        Raises
        ------
        ValueError
            If there is no report data to extract units from.
        """
        if len(report_data) == 0:
            raise ValueError("Report Generator error: No report data available to aggregate units from.")
        elif len(report_data) == 1 or len(report_data) > 2:
            var_units_match = re.search(r"\((.*?)\)", next(iter(report_data)))
            if var_units_match:
                return var_units_match.group(1)
            else:
                return ""
        else:
            first_key, second_key = list(report_data.keys())[:2]
            first_key_numerator_units, first_key_denominator_units = MeasurementUnits.extract_units(first_key)
            second_key_numerator_units, second_key_denominator_units = MeasurementUnits.extract_units(second_key)
            combined_numerator, combined_denominator = self.combine_units(
                first_key_numerator_units,
                first_key_denominator_units,
                second_key_numerator_units,
                second_key_denominator_units,
                operation,
                simplify_units,
            )
            stringified_combined_units = MeasurementUnits.units_to_string(combined_numerator, combined_denominator)

        return stringified_combined_units

    def combine_units(
        self,
        numerator1: dict[str, int],
        denominator1: dict[str, int],
        numerator2: dict[str, int],
        denominator2: dict[str, int],
        operation: str | None,
        simplify_units: bool,
    ) -> tuple[dict[str, int], dict[str, int]]:
        """
        Combines two sets of units (numerator and denominator) based on the specified operation.

        Parameters
        ----------
        numerator1 : dict[str, int]
            First set of numerator units, where keys are unit names (str) and values are exponents (int).
        denominator1 : dict[str, int]
            First set of denominator units, where keys are unit names (str) and values are exponents (int).
        numerator2 : dict[str, int]
            Second set of numerator units, where keys are unit names (str) and values are exponents (int).
        denominator2 : dict[str, int]
            Second set of denominator units, where keys are unit names (str) and values are exponents (int).
        operation : str | None
            The operation to combine the units. Can be one of ``product``, ``division``, ``sum``, ``subtraction``,
            ``average``, or ``SD``.
        simplify_units : bool
            Whether to simplify and reduce the units.

        Returns
        -------
        tuple[dict[str, int], dict[str, int]]
            - Combined numerator units.
            - Combined denominator units.
        """
        if operation in ["product", "division"]:
            if operation == "product":
                combined_numerator = MeasurementUnits.adjust_unit_exponents(numerator1, numerator2)
                combined_denominator = MeasurementUnits.adjust_unit_exponents(denominator1, denominator2)
            elif operation == "division":
                combined_numerator = MeasurementUnits.adjust_unit_exponents(numerator1, denominator2)
                combined_denominator = MeasurementUnits.adjust_unit_exponents(denominator1, numerator2)
            if simplify_units:
                combined_numerator, combined_denominator = MeasurementUnits.simplify_units(
                    combined_numerator, combined_denominator
                )

        else:
            if numerator1 != numerator2 or denominator1 != denominator2:
                self._log(
                    logging.WARNING,
                    "Report Generator Units Warning",
                    f"Report units do not match for operation {operation}.",
                    self.combine_units.__name__,
                )
            combined_numerator = numerator1.copy()
            combined_denominator = denominator1.copy()

        return combined_numerator, combined_denominator
