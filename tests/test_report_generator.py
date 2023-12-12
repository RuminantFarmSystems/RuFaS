from typing import Dict, List, Any
import pytest
from RUFAS.report_generator import (
    average_aggregator,
    division_aggregator,
    product_aggregator,
    sd_aggregator,
    sum_aggregator,
    subtraction_aggregator,
    ReportGenerator,
)


def test_average_aggregator():
    assert average_aggregator([1, 2, 3, 4, 5]) == 3
    assert average_aggregator([-1, -2, -3, -4, -5]) == -3
    assert average_aggregator([]) == 0


def test_division_aggregator():
    assert division_aggregator([100, 2, 5]) == 10
    assert division_aggregator([100, -2, 5]) == -10
    assert division_aggregator([]) is None
    assert division_aggregator([10]) is None
    assert division_aggregator([10, 0]) is None


def test_product_aggregator():
    assert product_aggregator([1, 2, 3, 4, 5]) == 120
    assert product_aggregator([-1, 2, -3, 4, -5]) == -120
    assert product_aggregator([]) == 1


def test_sd_aggregator():
    assert sd_aggregator([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2)
    assert sd_aggregator([-2, -4, -4, -4, -5, -5, -7, -9]) == pytest.approx(2)
    assert sd_aggregator([]) == 0


def test_sum_aggregator():
    assert sum_aggregator([1, 2, 3, 4, 5]) == 15
    assert sum_aggregator([-1, -2, -3, -4, -5]) == -15
    assert sum_aggregator([]) == 0


def test_subtraction_aggregator():
    assert subtraction_aggregator([10, 2, 3]) == 5
    assert subtraction_aggregator([10, -2, -3]) == 15
    assert subtraction_aggregator([]) is None
    assert subtraction_aggregator([10]) is None


class MockUtility:
    @staticmethod
    def convert_list_of_dicts_to_dict_of_lists(
        data: List[Dict[str, Any]]
    ) -> Dict[str, List[Any]]:
        return {k: [dic[k] for dic in data] for k in data[0]}


Utility = MockUtility


@pytest.fixture
def report_generator() -> ReportGenerator:
    return ReportGenerator()


@pytest.fixture
def sample_filtered_pool() -> Dict[str, Dict[str, List[Dict[str, int]]]]:
    return {
        "data1": {"values": [{"a": 1, "b": 2, "c": 10}, {"a": 3, "b": 4, "c": 10}]},
        "data2": {"values": [{"a": 5, "b": 6, "c": 10}, {"a": 7, "b": 8, "c": 10}]},
    }


def test_generate_report_vertical_then_horizontal(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "average",
        "vertical_aggregation": "sum",
        "horizontal_first": False,
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {'ver_hor_agg': [18.0]}


def test_generate_report_horizontal_then_vertical(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
        "vertical_aggregation": "average",
        "horizontal_first": True,
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {'hor_ver_agg': [9.0]}


def test_generate_report_only_horizontal(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {'hor_agg': [3, 7, 11, 15]}


def test_generate_report_only_vertical(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "vertical_aggregation": "average",
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {'ver_agg': [4.0, 5.0]}


def test_generate_report_no_aggregation(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
    }
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {"a":[1,3,5,7],"b":[2,4,6,8]}


def test_generate_report_invalid_empty_data(report_generator: ReportGenerator) -> None:
    filtered_pool: Dict[str, Dict[str, List[Any]]] = {}
    filter_content: Dict[str, Any] = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
        "vertical_aggregation": "average",
    }
    with pytest.raises(ValueError):
        report_generator.generate_report(filtered_pool, filter_content)


def test_prepare_report_data_valid_list(report_generator: ReportGenerator) -> None:
    filtered_pool: Dict[str, Dict[str, List[int]]] = {
        "data1": {"values": [1, 2, 3, 4]},
        "data2": {"values": [5, 6, 7, 8]},
    }
    assert report_generator._prepare_report_data(filtered_pool, None, 1, 3) == {
        "data1": [2, 3],
        "data2": [6, 7],
    }


def test_prepare_report_data_valid_dict(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
) -> None:
    actual = report_generator._prepare_report_data(
        sample_filtered_pool, ["a", "b"], 1, 3
    )
    expected = {"a": [3, 7], "b": [4, 8]}
    assert actual == expected


def test_prepare_report_data_invalid_no_variables(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
) -> None:
    with pytest.raises(KeyError):
        report_generator._prepare_report_data(sample_filtered_pool, None, 0, 0)


def test_prepare_report_data_aggregate_values(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
) -> None:
    actual = report_generator._prepare_report_data(
        sample_filtered_pool, ["a", "b"], 0, None
    )
    expected = {
        "a": [1, 3, 5, 7],
        "b": [2, 4, 6, 8],
    }
    assert actual == expected


def test_generate_report_with_invalid_horizontal_order(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_order": ["invalid_key", "b"],
        "horizontal_aggregation": "average",
        "vertical_aggregation": "sum",
        "horizontal_first": True,
    }
    with pytest.raises(KeyError):
        report_generator.generate_report(sample_filtered_pool, filter_content)


def test_generate_report_with_valid_horizontal_order(
    report_generator: ReportGenerator,
    sample_filtered_pool: Dict[str, Dict[str, List[Dict[str, int]]]],
):
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "division",
        "vertical_aggregation": "sum",
        "horizontal_first": True,
    }
    filter_content["horizontal_order"] = ["a", "b"]
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {"hor_ver_agg":[        2.9583333333333335 ]}
    filter_content["horizontal_order"] = ["b", "a"]
    assert report_generator.generate_report(sample_filtered_pool, filter_content) == {"hor_ver_agg":[ 5.676190476190476    ]}
