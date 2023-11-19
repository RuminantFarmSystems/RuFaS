from typing import Dict, List, Any, Callable
from RUFAS.util import Utility


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


AGGREGATION_FUNCTIONS: Dict[str, Callable[[List[float]], float]] = {
    "sum": sum_aggregator,
    "average": average_aggregator,
    "SD": sd_aggregator,
}


class ReportGenerator:
    def generate_report(
        self,
        filtered_pool: Dict[str, Dict[str, List[Any]]],
        filter_content: Dict[str, str | int],
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

        filter_content : Dict[str, str | int]
            A dictionary containing filter criteria and aggregation instructions.

        Returns
        -------
        List[float]
            The aggregated report data as a list.

        Raises
        ------
        ValueError
            If the report data is empty or if the necessary aggregation keys are not found in filter_content.
        """
        selected_variables = filter_content.get("variables")
        slice_start = filter_content.get("slice_start", 0)
        slice_end = filter_content.get("slice_end", 0)
        report_data = self._prepare_report_data(
            filtered_pool, selected_variables, slice_start, slice_end
        )
        if not report_data:
            raise ValueError(
                f"filter {filter_content.get('filters')} led to empty report data."
            )

        number_of_elements = len(report_data[next(iter(report_data))])

        horizontal_agg_key = filter_content.get("horizontal_aggregation")
        horizontal_aggregator = (
            AGGREGATION_FUNCTIONS.get(horizontal_agg_key)
            if horizontal_agg_key in AGGREGATION_FUNCTIONS
            else None
        )

        vertical_agg_key = filter_content.get("vertical_aggregation")
        vertical_aggregator = (
            AGGREGATION_FUNCTIONS.get(vertical_agg_key)
            if vertical_agg_key in AGGREGATION_FUNCTIONS
            else None
        )

        if horizontal_aggregator and vertical_aggregator:
            if filter_content.get("horizontal_first", True):
                horizontally_aggregated = [
                    horizontal_aggregator(
                        [report_data[key][i] for key in report_data.keys()]
                    )
                    for i in range(number_of_elements)
                ]
                return [vertical_aggregator(horizontally_aggregated)]
            else:
                vertically_aggregated = [
                    vertical_aggregator(data_series) for _, data_series in report_data
                ]
                return [horizontal_aggregator(vertically_aggregated)]
        elif horizontal_aggregator:
            return [
                horizontal_aggregator({key: report_data[key][i] for key in report_data})
                for i in range(number_of_elements)
            ]
        elif vertical_aggregator:
            return [vertical_aggregator(data_series) for _, data_series in report_data]

        raise ValueError(
            "Didn't find `horizontal_aggregation` or `vertical_aggregation` in the filter content."
        )

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
            Ending index for slicing; slices to end if set to 0.

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
            if is_data_in_dict:
                if selected_variables is None:
                    raise KeyError(
                        "Can't generate report, use 'variables' arg to select items from data"
                    )
                report_data.update(
                    Utility.convert_list_of_dicts_to_dict_of_lists(
                        filtered_pool[key]["values"][
                            slice_start: slice_end
                            if slice_end != 0
                            else len(filtered_pool[key]["values"])
                        ]
                    )
                )
            else:
                report_data[key] = filtered_pool[key]["values"][
                    slice_start: slice_end
                    if slice_end != 0
                    else len(filtered_pool[key]["values"])
                ]
        return report_data
