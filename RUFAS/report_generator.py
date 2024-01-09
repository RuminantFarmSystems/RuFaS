from typing import Dict, List, Any, Callable
from RUFAS.util import Utility


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


AGGREGATION_FUNCTIONS: Dict[str, Callable[[List[float]], float]] = {
    "average": average_aggregator,
    "division": division_aggregator,
    "product": product_aggregator,
    "SD": sd_aggregator,
    "sum": sum_aggregator,
    "subtraction": subtraction_aggregator,
}


class ReportGenerator:
    def generate_report(
        self,
        filtered_pool: Dict[str, Dict[str, List[Any]]],
        filter_content: Dict[str, str | int | List[str]],
    ) -> Dict[str, List[float]]:
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
        Dict[str, List[float]]
            The sliced and aggregated data.

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

        horizontal_agg_key = filter_content.get("horizontal_aggregation")
        horizontal_aggregator = AGGREGATION_FUNCTIONS.get(horizontal_agg_key)

        vertical_agg_key = filter_content.get("vertical_aggregation")
        vertical_aggregator = AGGREGATION_FUNCTIONS.get(vertical_agg_key)

        if horizontal_aggregator:
            loop_list = filter_content.get("horizontal_order", report_data.keys())
            number_of_elements = len(report_data[next(iter(report_data))])
            try:
                horizontally_aggregated = [
                    horizontal_aggregator([report_data[key][i] for key in loop_list])
                    for i in range(number_of_elements)
                ]
            except KeyError as e:
                raise KeyError(
                    f"{e.args[0]} not found in filtered pool. Check the `horizontal_order` entry in the filter file."
                )
            if not vertical_aggregator:
                return {"hor_agg": horizontally_aggregated}

        if vertical_aggregator:
            vertically_aggregated = [
                vertical_aggregator(data_series)
                for _, data_series in report_data.items()
            ]
            if not horizontal_aggregator:
                return {"ver_agg": vertically_aggregated}

            if filter_content.get("horizontal_first", False):
                return {"hor_ver_agg": [vertical_aggregator(horizontally_aggregated)]}
            return {"ver_hor_agg": [horizontal_aggregator(vertically_aggregated)]}

        return report_data

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
                filtered_data = Utility.filter_pool(temp_data, selected_variables, False)
                for filtered_key, filtered_value in filtered_data.items():
                    if filtered_key in report_data:
                        report_data[filtered_key].extend(filtered_value)
                    else:
                        report_data[filtered_key] = filtered_value
            else:
                report_data[key] = filtered_pool[key]["values"][slice_start:slice_end]
        return report_data
