from __future__ import annotations

from typing import Dict, List, Any, Callable, Optional

from RUFAS.util import Utility


def apply_scalar_operation(value: float, constant: float, operation: str) -> float:
    """
    Applies a scalar operation to a value and a constant.

    Parameters
    ----------
    value : float
        The value to which the scalar operation is to be applied.
    constant : float
        The constant to be used in the scalar operation.
    operation : str
        The scalar operation to be applied.

    Returns
    -------
    float
        The result of the scalar operation.
    """

    if operation == "sum":
        return value + constant
    if operation == "subtraction":
        return value - constant
    if operation == "product":
        return value * constant
    if operation == "division":
        return value / constant
    if operation == "exponent":
        return value ** constant
    raise ValueError(f"Unsupported scalar operation: {operation}")


def average_aggregator(data: List[float]) -> float:
    """
    Calculates the average of a list of numbers.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose average is to be calculated.

    Returns
    -------
    float
        The average of the input numbers.
    """
    return sum(data) / len(data) if data else 0


def division_aggregator(data: List[float]) -> float:
    """
    Divides the first number in the list by each of the subsequent numbers.

    Parameters
    ----------
    data : List[float]
        A list of numbers for the division operation.

    Returns
    -------
    float
        The result of dividing the first number by each subsequent number.
        Returns None if the list is empty or has only one element.
    """
    if len(data) < 2:
        return None
    result = data[0]
    for num in data[1:]:
        if num == 0:  # Avoid division by zero
            return None
        result /= num
    return result


def division_aggregator_with_scalar_op(data: List[float], scalar: float = 1,
                                       operation: str = "division") -> Optional[float]:
    """
    Returns the result of dividing the first number in the list by the product of the remaining numbers
    after applying a scalar operation to each number. Returns None for division by zero or if list length is less than 2.

    Parameters
    ----------
    data : List[float]
        A list of numbers for the division operation.
    scalar : float
        A constant to be used in the scalar operation.
    operation : str
        The scalar operation to be applied.

    Returns
    -------
    Optional[float]
        The result of the division operation, or None if division by zero occurs or list length is less than 2.
    """

    if len(data) < 2 or 0 in data[1:]:
        return None

    numerator = apply_scalar_operation(data[0], scalar, operation)
    denominator = product_aggregator_with_scalar_op(data[1:], scalar, operation)

    if denominator == 0:
        return None

    return numerator / denominator


def product_aggregator(data: List[float]) -> float:
    """
    Returns the product of a list of numbers.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose product is to be calculated.

    Returns
    -------
    float
        The product of the input numbers. Returns 1 for an empty list.
    """
    product = 1
    for num in data:
        product *= num
    return product


def product_aggregator_with_scalar_op(data: List[float], scalar: float = 1,
                                      operation: str = "product") -> float:
    """
    Returns the product of a list of numbers after applying a scalar operation to each number.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose product is to be calculated.
    scalar : float
        A constant to be used in the scalar operation.
    operation : str
        The scalar operation to be applied.

    Returns
    -------
    float
        The product of the input numbers after applying the scalar operation.
    """

    return product_aggregator([apply_scalar_operation(value, scalar, operation) for value in data])


def sd_aggregator(data: List[float]) -> float:
    """
    Calculates the standard deviation of a list of numbers.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose standard deviation is to be calculated.

    Returns
    -------
    float
        The standard deviation of the input numbers.
    """
    mean = average_aggregator(data)
    return (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5 if data else 0


def sum_aggregator(data: List[float]) -> float:
    """
    Returns the sum of a list of numbers.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose sum is to be calculated.

    Returns
    -------
    float
        The sum of the input numbers.
    """
    return sum(data)


def sum_aggregator_with_scalar_op(data: List[float], scalar: float = 0,
                                  operation: str = "sum") -> float:
    """
    Returns the sum of a list of numbers after applying a scalar operation to each number.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose sum is to be calculated.
    scalar : float
        A constant to be used in the scalar operation.
    operation : str
        The scalar operation to be applied.

    Returns
    -------
    float
        The sum of the input numbers after applying the scalar operation.
    """

    return sum(apply_scalar_operation(value, scalar, operation) for value in data)


def subtraction_aggregator(data: List[float]) -> float:
    """
    Subtracts each subsequent number in the list from the first number.

    Parameters
    ----------
    data : List[float]
        A list of numbers for the subtraction operation.

    Returns
    -------
    float
        The result of subtracting each subsequent number from the first number.
        Returns None if the list is empty or has only one element.
    """
    if len(data) < 2:
        return None
    result = data[0]
    for num in data[1:]:
        result -= num
    return result


def subtraction_aggregator_with_scalar_op(data: List[float], scalar: float = 0,
                                          operation: str = "subtraction") -> float:
    """
    Returns the result of subtracting the product of the remaining numbers from the first number
    after applying a scalar operation to each number. Returns None if list length is less than 2.

    Parameters
    ----------
    data : List[float]
        A list of numbers for the subtraction operation.
    scalar : float
        A constant to be used in the scalar operation.
    operation : str
        The scalar operation to be applied.

    Returns
    -------
    float
        The result of the subtraction operation, or None if list length is less than 2.
    """


AGGREGATION_FUNCTIONS: Dict[str, Callable[[List[float]], float]] = {
    "average": average_aggregator,
    # "division": division_aggregator,
    "division": division_aggregator_with_scalar_op,
    # "product": product_aggregator,
    "product": product_aggregator_with_scalar_op,
    "SD": sd_aggregator,
    # "sum": sum_aggregator,
    "sum": sum_aggregator_with_scalar_op,
    # "subtraction": subtraction_aggregator,
    "subtraction": subtraction_aggregator_with_scalar_op,
}

PADDING_METHODS = {
    "first": lambda lst: lst[0] if lst else None,
    "last": lambda lst: lst[-1] if lst else None,
    "avg": average_aggregator,
    "min": min,
    "max": max,
    "zero": lambda _: 0,
    "one": lambda _: 1,
    "null": lambda _: None,
}


class ReportGenerator:
    def generate_report(
            self,
            filtered_pool: Dict[str, Dict[str, List[Any]]],
            filter_content: Dict[str, str | int | List[str]],
    ) -> List[float]:
        """
        Generates a report based on filtered data and aggregation criteria.

        This method processes filtered data and performs specified horizontal and/or vertical aggregations
        based on the instructions provided in filter_content.

        Parameters
        ----------
        filtered_pool : Dict[str, Dict[str, List[Any]]]
            The data pool from which the report is to be generated, structured as a dictionary.
            Has the same structure of OutputManager's variables pool.

        filter_content : Dict[str, str | int | List[str]]
            A dictionary containing filter criteria and aggregation instructions.

        Returns
        -------
        List[float]
            The aggregated report data as a list.

        Raises
        ------
        ValueError
            If the report data is empty or if the necessary aggregation keys are not found in filter_content.
        KeyError
            If a key specified in the `horizontal_order` of `filter_content` is not found in the `report_data`.
            This usually indicates a mismatch between the expected structure of `filtered_pool` and its actual content.
        """
        report_data = self._prepare_report_data(
            filtered_pool,
            selected_variables=filter_content.get("variables"),
            slice_start=filter_content.get("slice_start", 0),
            slice_end=filter_content.get("slice_end"),
        )
        if not report_data:
            raise ValueError(
                f"filter {filter_content.get('filters')} in {filter_content.get('name')} led to empty report data."
            )

        number_of_elements = len(report_data[next(iter(report_data))])

        horizontal_agg_key = filter_content.get("horizontal_aggregation")
        horizontal_aggregator = AGGREGATION_FUNCTIONS.get(horizontal_agg_key)

        vertical_agg_key = filter_content.get("vertical_aggregation")
        vertical_aggregator = AGGREGATION_FUNCTIONS.get(vertical_agg_key)

        if horizontal_aggregator:
            loop_list = filter_content.get("horizontal_order", report_data.keys())
            try:
                horizontally_aggregated = [
                    horizontal_aggregator([report_data[key][i] for key in loop_list])
                    for i in range(number_of_elements)
                ]
            except KeyError as e:
                raise KeyError(
                    f"{e.args[0]} not found in filtered pool. Check the `horizontal_order` entry in the filter file."
                )

        if vertical_aggregator:
            vertically_aggregated = [
                vertical_aggregator(data_series)
                for _, data_series in report_data.items()
            ]

        if horizontal_aggregator and vertical_aggregator:
            if filter_content.get("horizontal_first", True):
                return [vertical_aggregator(horizontally_aggregated)]
            return [horizontal_aggregator(vertically_aggregated)]

        if horizontal_aggregator:
            return horizontally_aggregated

        if vertical_aggregator:
            return vertically_aggregated

        raise ValueError(
            f"Didn't find `horizontal_aggregation` or `vertical_aggregation` in {filter_content.get('name')}."
        )

    def generate_aggregate_report(
            self,
            filtered_pool: Dict[str, Dict[str, List[Any]]],
            filter_content: Dict[str, Any]
    ) -> List[float]:
        """
        Generates a report based on filtered data and aggregation criteria, including scalar operations and constants.

        Parameters
        ----------
        filtered_pool : Dict[str, Dict[str, List[Any]]]
            The data pool from which the report is to be generated, structured as a dictionary.
        filter_content : Dict[str, Any]
            A dictionary containing filter criteria, aggregation instructions, and scalar operation details.

        Returns
        -------
        List[float]
            The aggregated report data as a list.
        """

        # Prepare the data
        report_data = self._prepare_report_data(
            filtered_pool,
            selected_variables=filter_content.get("variables"),
            slice_start=filter_content.get("slice_start", 0),
            slice_end=filter_content.get("slice_end"),
        )
        if not report_data:
            raise ValueError(
                f"filter {filter_content.get('filters')} in {filter_content.get('name')} led to empty report data."
            )

        horizontal_scalar = filter_content.get("horizontal_constant", 1)
        horizontal_operation = filter_content.get("horizontal_scalar_operation", "product")
        vertical_scalar = filter_content.get("vertical_constant", 1)
        vertical_operation = filter_content.get("vertical_scalar_operation", "product")

        # Aggregate data
        horizontal_agg_key = filter_content.get("horizontal_aggregation")
        vertical_agg_key = filter_content.get("vertical_aggregation")

        # Handle horizontal aggregation
        if horizontal_agg_key:
            horizontal_aggregator = AGGREGATION_FUNCTIONS.get(horizontal_agg_key)
            if not horizontal_aggregator:
                raise ValueError(f"Unsupported horizontal aggregation type: {horizontal_agg_key}")

            loop_list = filter_content.get("horizontal_order", report_data.keys())
            horizontally_aggregated = self._horizontal_aggregate(
                report_data, loop_list, horizontal_aggregator, horizontal_scalar, horizontal_operation)

        # Handle vertical aggregation
        if vertical_agg_key:
            vertical_aggregator = AGGREGATION_FUNCTIONS.get(vertical_agg_key)
            if not vertical_aggregator:
                raise ValueError(f"Unsupported vertical aggregation type: {vertical_agg_key}")

            vertically_aggregated = self._vertical_aggregate(
                report_data, vertical_aggregator, vertical_scalar, vertical_operation)

        if horizontal_agg_key and vertical_agg_key:
            horizontal_first = filter_content.get("horizontal_first", True)
            return [vertical_aggregator(horizontally_aggregated, vertical_scalar, vertical_operation)] \
                if horizontal_first else [
                horizontal_aggregator(vertically_aggregated, horizontal_scalar, horizontal_operation)]

        if horizontal_agg_key:
            return horizontally_aggregated

        if vertical_agg_key:
            return vertically_aggregated

        raise ValueError(
            f"Didn't find `horizontal_aggregation` or `vertical_aggregation` in {filter_content.get('name')}.")

    @staticmethod
    def _horizontal_aggregate(report_data: Dict[str, List[float]], loop_list: List[str],
                              aggregator: Callable[[List[float], float, str], float],
                              scalar: float, operation: str) -> List[float]:
        """
        Perform horizontal aggregation on report data using a specified aggregator function.

        Parameters
        ----------
        report_data : Dict[str, List[float]]
            The data pool to be aggregated, structured as a dictionary of lists.
        loop_list : List[str]
            List of keys indicating the order in which to aggregate data.
        aggregator : Callable[[List[float], float, str], float]
            The aggregation function to be used.
        scalar : float
            A constant to be used in the scalar operation.
        operation : str
            The scalar operation to be applied.

        Returns
        -------
        List[float]
            The horizontally aggregated data as a list.
        """

        number_of_elements = len(report_data[next(iter(report_data))])
        return [aggregator([report_data[key][i] for key in loop_list], scalar, operation)
                for i in range(number_of_elements)]

    @staticmethod
    def _vertical_aggregate(report_data: Dict[str, List[float]],
                            aggregator: Callable[[List[float], float, str], float],
                            scalar: float, operation: str) -> List[float]:
        """
        Perform vertical aggregation on report data using a specified aggregator function.

        Parameters
        ----------
        report_data : Dict[str, List[float]]
            The data pool to be aggregated, structured as a dictionary of lists.
        aggregator : Callable[[List[float], float, str], float]
            The aggregation function to be used.
        scalar : float
            A constant to be used in the scalar operation.
        operation : str
            The scalar operation to be applied.

        Returns
        -------
        List[float]
            The vertically aggregated data as a list.
        """

        return [aggregator(data, scalar, operation)
                for _, data in report_data.items()]

    @staticmethod
    def generate_derived_report(referenced_data: List[List[float]], filter_content: Dict[str, Any]) -> List[float]:
        """
        Generates a derived report based on referenced data and aggregation criteria.

        Notes
        -----
        Assume that each list in referenced_data is a column of data.

        Parameters
        ----------
        referenced_data : List[List[float]]
            A list of lists, where each sublist contains the data of a referenced report.

        filter_content : Dict[str, Any]
            A dictionary containing the configuration for the derived report,
            including the aggregation type.

        Returns
        -------
        List[float]
            The aggregated report data as a list.

        Raises
        ------
        ValueError
            If the aggregation type is not supported or referenced data is invalid.
        """

        ReportGenerator._apply_padding(referenced_data, filter_content.get("padding", {}))

        horizontal_agg_type = filter_content.get("horizontal_aggregation")
        vertical_agg_type = filter_content.get("vertical_aggregation")
        horizontal_first = filter_content.get("horizontal_first", True)

        if horizontal_agg_type and vertical_agg_type:
            return ReportGenerator._apply_both_aggregations(
                referenced_data, horizontal_agg_type, vertical_agg_type, horizontal_first
            )
        elif horizontal_agg_type:
            return ReportGenerator._apply_horizontal_aggregation_only(referenced_data, horizontal_agg_type)
        elif vertical_agg_type:
            return ReportGenerator._apply_vertical_aggregation_only(referenced_data, vertical_agg_type)
        else:
            raise ValueError("No aggregation type provided")

    @staticmethod
    def _apply_both_aggregations(referenced_data: List[List[float]],
                                 horizontal_agg_type: str,
                                 vertical_agg_type: str,
                                 horizontal_first: bool) -> List[float]:
        """
        Applies both horizontal and vertical aggregations to referenced data.

        Parameters
        ----------
        referenced_data : List[List[float]]
            A list of lists, where each sublist contains the data of a referenced report.
        horizontal_agg_type : str
            The type of horizontal aggregation to be applied.
        vertical_agg_type : str
            The type of vertical aggregation to be applied.
        horizontal_first : bool
            Whether to apply horizontal aggregation before vertical aggregation.
            If False, vertical aggregation is applied before horizontal aggregation.

        Returns
        -------
        List[float]
            The aggregated report data as a list.
        """

        horizontal_aggregator = AGGREGATION_FUNCTIONS.get(horizontal_agg_type)
        vertical_aggregator = AGGREGATION_FUNCTIONS.get(vertical_agg_type)

        if not horizontal_aggregator or not vertical_aggregator:
            raise ValueError("Unsupported aggregation type")

        if horizontal_first:
            # Apply horizontal then vertical
            transposed_data = list(zip(*referenced_data))
            horizontally_aggregated = [horizontal_aggregator(list(filter(None.__ne__, row)))
                                       for row in transposed_data]
            return [vertical_aggregator(horizontally_aggregated)]
        else:
            # Apply vertical then horizontal
            vertically_aggregated = [vertical_aggregator(list(filter(None.__ne__, column)))
                                     for column in referenced_data]
            return [horizontal_aggregator(vertically_aggregated)]

    @staticmethod
    def _apply_horizontal_aggregation_only(referenced_data: List[List[float]],
                                           horizontal_agg_type: str) -> List[float]:
        """
        Applies horizontal aggregation to referenced data.

        Notes
        -----
        Assume that each list in referenced_data is a column of data.

        Parameters
        ----------
        referenced_data : List[List[float]]
            A list of lists, where each sublist contains the data of a referenced report.
        horizontal_agg_type : str
            The type of horizontal aggregation to be applied.

        Returns
        -------
        List[float]
            The aggregated report data as a list.
        """

        horizontal_aggregator = AGGREGATION_FUNCTIONS.get(horizontal_agg_type)
        if not horizontal_aggregator:
            raise ValueError(f"Unsupported horizontal aggregation type: {horizontal_agg_type}")

        transposed_data = list(zip(*referenced_data))
        return [horizontal_aggregator(list(filter(None.__ne__, row))) for row in transposed_data]

    @staticmethod
    def _apply_vertical_aggregation_only(referenced_data: List[List[float]],
                                         vertical_agg_type: str) -> List[float]:
        """
        Applies vertical aggregation to referenced data.

        Notes
        -----
        Assume that each list in referenced_data is a column of data.

        Parameters
        ----------
        referenced_data : List[List[float]]
            A list of lists, where each sublist contains the data of a referenced report.
        vertical_agg_type : str
            The type of vertical aggregation to be applied.

        Returns
        -------
        List[float]
            The aggregated report data as a list.
        """

        vertical_aggregator = AGGREGATION_FUNCTIONS.get(vertical_agg_type)
        if not vertical_aggregator:
            raise ValueError(f"Unsupported vertical aggregation type: {vertical_agg_type}")
        return [vertical_aggregator(list(filter(None.__ne__, column)))
                for column in referenced_data]

    @staticmethod
    def _apply_padding(referenced_data: List[List[float]], padding_config: Dict[str, Any]) -> None:
        """
        Applies padding to the referenced data based on the provided padding configuration.

        Parameters
        ----------
        referenced_data : List[List[float]]
            The list of lists to which padding needs to be applied.
        padding_config : Dict[str, Any]
            Configuration for padding, including method and custom value if applicable.
        """

        padding_method = padding_config.get("method", "none")
        if padding_method == "none":
            return

        max_length = max([len(lst) for lst in referenced_data])
        for lst in referenced_data:
            if padding_method in PADDING_METHODS:
                ReportGenerator._pad_list_with_value(lst, max_length, PADDING_METHODS[padding_method](lst))
            elif padding_method == "custom":
                ReportGenerator._pad_list_with_value(lst, max_length, padding_config.get("value", None))
            elif padding_method == "cycle":
                ReportGenerator._pad_list_with_cycle(lst, max_length)

    @staticmethod
    def _pad_list_with_value(lst: List[float], length: int, value: float | None) -> None:
        """
        Pads a list with a specified value until it reaches the specified length.

        Parameters
        ----------
        lst : List[float]
            The list to be padded.
        length : int
            The length to which the list should be padded.
        value : float | None
            The value to be used for padding.

        Returns
        -------
        None
        """

        lst_to_extend = [value] * (length - len(lst))
        lst.extend(lst_to_extend)

    @staticmethod
    def _pad_list_with_cycle(lst: List[float], length: int) -> None:
        """
        Pads a list by cycling its elements until it reaches the specified length.

        Parameters
        ----------
        lst : List[float]
            The list to be padded.
        length : int
            The length to which the list should be padded.

        Returns
        -------
        None
        """

        current_length = len(lst)
        if current_length == 0 or current_length >= length:
            return

        full_repeats = (length - current_length) // current_length
        lst.extend(lst * full_repeats)

        remaining_elements = length - len(lst)
        lst.extend(lst[:remaining_elements])

    def _prepare_report_data(
            self,
            filtered_pool: Dict[str, Dict[str, List[Any]]],
            selected_variables: List[str],
            slice_start: int,
            slice_end: int,
    ) -> Dict[str, List[Any]]:
        """
        Processes and structures a filtered data pool for report generation.

        This method organizes data from a filtered pool based on selected variables and slicing parameters.
        It caters to different data structures within the pool, ensuring data is formatted appropriately
        for report inclusion.

        Parameters
        ----------
        filtered_pool : Dict[str, pool_element_type]
            The filtered data pool with each key mapping to its respective data element.

        selected_variables : List[str]
            Variables to be included from the filtered pool.

        slice_start : int
            Starting index for slicing data elements.

        slice_end : int
            Ending index for slicing.

        Returns
        -------
        Dict[str, List[Any]]
            Processed data suitable for report generation, keyed by selected variables.

        Raises
        ------
        KeyError
            If selected_variables is None and the data within the pool requires variable selection.
        """
        report_data: Dict[str, List[Any]] = {}
        for key in filtered_pool.keys():
            is_data_in_dict = isinstance(filtered_pool[key]["values"][0], dict)
            if is_data_in_dict and selected_variables is None:
                raise KeyError(
                    "Can't generate report, use 'variables' arg to select items from data"
                )
            if is_data_in_dict:
                temp_data = Utility.convert_list_of_dicts_to_dict_of_lists(
                    filtered_pool[key]["values"][slice_start:slice_end]
                )
                for temp_key, temp_values in temp_data.items():
                    if temp_key not in selected_variables:
                        continue
                    if temp_key in report_data:
                        report_data[temp_key].extend(temp_values)
                    else:
                        report_data[temp_key] = temp_values
            else:
                report_data[key] = filtered_pool[key]["values"][slice_start:slice_end]
        return report_data
