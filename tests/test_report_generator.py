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
    def convert_list_of_dicts_to_dict_of_lists(data):
        return {k: [dic[k] for dic in data] for k in data[0]}


Utility = MockUtility


@pytest.fixture
def report_generator():
    return ReportGenerator()


def test_generate_report_valid_horizontal_vertical(report_generator):
    filtered_pool = {
        "data1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
        "data2": {"values": [{"a": 5, "b": 6}, {"a": 7, "b": 8}]},
    }
    filter_content = {
        "variables": ["a", "b"],
        "slice_start": 0,
        "slice_end": 0,
        "horizontal_aggregation": "sum",
        "vertical_aggregation": "average",
        "horizontal_first": True,
    }
    assert report_generator.generate_report(filtered_pool, filter_content) == [13]


def test_generate_report_invalid_empty_data(report_generator):
    filtered_pool = {}
    filter_content = {
        "variables": ["a", "b"],
        "horizontal_aggregation": "sum",
        "vertical_aggregation": "average",
    }
    with pytest.raises(ValueError):
        report_generator.generate_report(filtered_pool, filter_content)


def test_prepare_report_data_valid(report_generator):
    filtered_pool = {
        "data1": {"values": [1, 2, 3, 4]},
        "data2": {"values": [5, 6, 7, 8]},
    }
    selected_variables = ["data1", "data2"]
    assert report_generator._prepare_report_data(
        filtered_pool, selected_variables, 1, 3
    ) == {"data1": [2, 3], "data2": [6, 7]}


def test_prepare_report_data_invalid_no_variables(report_generator):
    filtered_pool = {
        "data1": {"values": [{"a": 1}, {"a": 2}]},
        "data2": {"values": [{"b": 3}, {"b": 4}]},
    }
    with pytest.raises(KeyError):
        report_generator._prepare_report_data(filtered_pool, None, 0, 0)
