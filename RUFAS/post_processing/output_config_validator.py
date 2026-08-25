from pathlib import Path
from typing import Any


class OutputConfigValidator:
    """
    Class in charge of validating output filters including graphing and reporting.
    """

    def __init__(self) -> None:
        # TODO add logger when implemented
        pass

    def validate_filter_content(self, filters_dir_path: Path) -> None:
        """
        Validates the content of the filters, including keys and values.

        Parameters
        ----------
        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.
        """
        pass

    def validate_json_filters(self, filter_content: dict[Any, Any], filter_name: str) -> None:
        """
        Validate the JSON filter.

        Parameters
        ----------
        filter_content : dict[Any, Any]
            The report filter to validate.
        filter_name : str
            The name of the filter to validate.
        """
        pass

    def validate_csv_filters(self, filter_content: dict[Any, Any], filter_name: str) -> None:
        """
        Validate the CSV filter.

        Parameters=
        ----------
        filter_content : dict[Any, Any]
            The report filter to validate.
        filter_name : str
            The name of the filter to validate.
        """
        pass

    def validate_report_filters(self, filter_content: dict[Any, Any], filter_name: str) -> None:
        """
        Validate the report filter.

        Parameters
        ----------
        filter_content : dict[Any, Any]
            The report filter to validate.
        filter_name : str
            The name of the filter to validate.
        """
        pass

    def validate_filter_constant_content(self, filters_dir_path: Path) -> None:
        """
        Validates the content of the filters, including keys and values.

        Parameters
        ----------
        filters_dir_path : Path
            Path of the directory containing the files containing the keys for filtering.
        """
        pass

    def validate_direction(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validates the direction of CSV outputs.

        Parameters
        ----------
        value : Any
            The aggregator option to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        """
        pass

    def validate_graph_details(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the graph details provided.

        Parameters
        ----------
        value : Any
            The graph details to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        """
        pass

    def validate_type(self, value: Any, content_name: str, filter_name: str, expected: type, type_label: str) -> None:
        """
        Generic type checker.

        Parameters
        ----------
        value : Any
            The value to check.
        content_name : str
            Name of the field, for error messages.
        filter_name: str
            Name of the filter validated.
        expected : type
            A type or tuple of types that value must be an instance of.
        type_label : str
            A human-readable description of the type (used in the error message).
        """
        pass

    def validate_aggregator(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the aggregator option provided.

        Parameters
        ----------
        value : Any
            The aggregator option to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        """
        pass

    def validate_list_of_strings(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate filter content that should be a list of strings.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        filter_name : str
            The name of the filter to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        """
        pass

    def validate_dict_of_numbers(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate filter content that should be a dictionary with string type as keys and int or float as values.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        """
        pass

    def validate_graph_type(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the provided graph type in the filter contents.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        """
        pass

    def validate_customization_details(self, value: Any, content_name: str, filter_name: str) -> None:
        """
        Validate the graph customization details in the filter contents.

        Parameters
        ----------
        value : Any
            The filter content to validate.
        content_name : str
            The corresponding filter option to provide in error reporting.
        filter_name : str
            Name of the filter to validate.
        """
        pass
