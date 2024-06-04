from pathlib import Path
from freezegun import freeze_time
from typing import Any, Dict, List
from unittest.mock import patch
from matplotlib import pyplot as plt
from mock.mock import MagicMock
import pytest
from pytest_mock import MockerFixture
from RUFAS.graph_generator import GraphGenerator


@pytest.fixture
def graph_generator() -> GraphGenerator:
    return GraphGenerator("metadata_name")


def test_save_graph_successful(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir: str = "graphics"

    with patch("RUFAS.graph_generator.matplotlib.pyplot.savefig") as mock_savefig:
        mock_savefig.return_value = None

        with patch("RUFAS.graph_generator.GraphGenerator._generate_graph_path") as mock_generate_graph_path:
            mock_generate_graph_path.return_value = Path("graph_path")

            result = graph_generator._save_graph(graph_details, filter_file_name, graphics_dir)

            mock_savefig.assert_called_once_with(mock_generate_graph_path.return_value)
            mock_generate_graph_path.assert_called_once_with(graph_details, filter_file_name, graphics_dir)
            assert result == mock_generate_graph_path.return_value


def test_save_graph_exception(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir = Path("graphics")

    with patch("RUFAS.graph_generator.matplotlib.pyplot.savefig") as mock_savefig:
        mock_savefig.side_effect = Exception("test")
        with pytest.raises(Exception, match="test"):
            graph_generator._save_graph(graph_details, filter_file_name, graphics_dir)


def test_generate_graph_path_with_title(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir: str = "graphics"

    with freeze_time("2023-10-13 11:41:23"):
        result = graph_generator._generate_graph_path(graph_details, filter_file_name, graphics_dir)
        assert result == Path(r"graphics/metadata_name_test-graph-13-Oct-2023_Fri_11-41-23.png")


def test_generate_graph_path_no_title(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir: str = "graphics"

    with freeze_time("2023-10-13 11:41:23"):
        result = graph_generator._generate_graph_path(graph_details, filter_file_name, graphics_dir)
        assert result == Path(r"graphics/metadata_name_test_filter.png-13-Oct-2023_Fri_11-41-23.png")


def test_generate_graph_without_producing_graphics(graph_generator: GraphGenerator) -> None:
    filtered_pool = {"dummy_key": {"dummy_data": [1, 2, 3]}}
    graph_details = {"title": "Example Graph"}
    filter_file_name = "dummy_filter"
    graphics_dir = Path("/tmp")
    produce_graphics = False

    expected_output = [
        {
            "error": "Can't plot Example Graph data set",
            "message": "'produce_graphics' set to False, no graphs will be produced.",
            "info_map": {
                "class": graph_generator.__class__.__name__,
                "function": "generate_graph",
            },
        }
    ]

    result = graph_generator.generate_graph(
        filtered_pool=filtered_pool,
        graph_details=graph_details,
        filter_file_name=filter_file_name,
        graphics_dir=graphics_dir,
        produce_graphics=produce_graphics,
    )

    assert result == expected_output, "Function did not return expected log message when produce_graphics is False."


def test_generate_graph_with_exception(graph_generator: GraphGenerator) -> None:
    filtered_pool = {"example": {"data": [1, 2, 3]}}
    graph_details = {"title": "Example Graph", "type": "line", "filters": ["example"]}
    filter_file_name = "example_filter"
    graphics_dir = Path("/tmp")
    produce_graphics = True

    with patch.object(graph_generator, "_validate_graph_filter", side_effect=Exception("Test Exception")):
        expected_output = [
            {
                "error": "Error plotting 'Example Graph' data set",
                "message": "Unforeseen error Test Exception when trying to graph data.",
                "info_map": {
                    "class": graph_generator.__class__.__name__,
                    "function": "generate_graph",
                },
            }
        ]

        result = graph_generator.generate_graph(
            filtered_pool=filtered_pool,
            graph_details=graph_details,
            filter_file_name=filter_file_name,
            graphics_dir=graphics_dir,
            produce_graphics=produce_graphics,
        )

        assert result == expected_output


def test_customize_graph_figure_setters(graph_generator: GraphGenerator) -> None:
    customization_details = {
        "figsize": (6, 4),
        "facecolor": "red",
        "dpi": 100,
    }
    fig = plt.figure()
    graph_generator._customize_graph(fig, customization_details)
    assert (fig.get_size_inches() == (6, 4)).all()
    assert fig.get_facecolor() == (1.0, 0.0, 0.0, 1.0)  # RGBA
    assert fig.get_dpi() == 100


def test_customize_graph_axes_setters(graph_generator: GraphGenerator) -> None:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    customization_details = {
        "title": "Test Plot",
        "xlabel": "X-axis Label",
        "ylabel": "Y-axis Label",
    }
    graph_generator._customize_graph(fig, customization_details)
    assert ax.get_title() == "Test Plot"
    assert ax.get_xlabel() == "X-axis Label"
    assert ax.get_ylabel() == "Y-axis Label"


def test_generate_graph_error_found(graph_generator: GraphGenerator) -> None:
    graph_generator._draw_graph = MagicMock()
    graph_generator._customize_graph = MagicMock()
    graph_generator._validate_graph_filter = MagicMock(return_value=[])
    graph_generator._save_graph = MagicMock(return_value="graph path")
    filtered_pool = {"var1": {"values": [1, 2, 3]}}
    mock_log_pool = [{"error": "mock_error_message"}]
    graph_generator._log_non_numerical_data = MagicMock(return_value=mock_log_pool)
    graph_details = {"type": "plot", "variables": ["var1", "var2"]}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    assert mock_log_pool == graph_generator.generate_graph(
        filtered_pool, graph_details, filter_file_name, graphics_dir, True
    )
    graph_generator._draw_graph.assert_not_called()
    graph_generator._customize_graph.assert_not_called()
    graph_generator._save_graph.assert_not_called()


def test_generate_graph_success(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    graph_generator._draw_graph = MagicMock()
    graph_generator._customize_graph = MagicMock()
    graph_generator._validate_graph_filter = MagicMock(return_value=[])
    graph_generator._save_graph = MagicMock(return_value="graph path")
    filtered_pool = {"var1": {"values": [1, 2, 3]}}
    updated_pool = {"var1": {"values": [1, 2, 3], "units": "units"}}
    var_units_logs = []
    graph_generator._add_var_units = MagicMock(return_value=(updated_pool, var_units_logs))
    prepared_data = {"var1": [1, 2, 3]}
    mock_log_pool = [{"log": "mock_log_message"}]
    mock_remove_special_chars = mocker.patch("RUFAS.util.Utility.remove_special_chars")
    graph_generator._log_non_numerical_data = MagicMock(return_value=[{"log": "mock_log_message"}])
    graph_details = {"type": "plot", "filters": ["var1", "var2"], "title": "dummy.graph/title", "display_units": True}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    assert mock_log_pool == graph_generator.generate_graph(
        filtered_pool, graph_details, filter_file_name, graphics_dir, True
    )
    graph_generator._draw_graph.assert_called_once_with("plot", prepared_data, list(prepared_data.keys()))
    graph_generator._customize_graph.assert_called_once()
    graph_generator._save_graph.assert_called_once_with(graph_details, filter_file_name, graphics_dir)
    mock_remove_special_chars.assert_called_once()
    graph_generator._add_var_units.assert_called_once_with(filtered_pool)


def test_generate_graph_exception(graph_generator: GraphGenerator) -> None:
    graph_generator._draw_graph = MagicMock()
    graph_generator._customize_graph = MagicMock()
    graph_generator._validate_graph_filter = MagicMock(return_value=[])
    graph_generator._save_graph = MagicMock(side_effect=Exception)
    filtered_pool = {}
    graph_details = {"type": "plot", "variables": ["var1", "var2"]}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    with pytest.raises(Exception):
        graph_generator.generate_graph(filtered_pool, graph_details, filter_file_name, graphics_dir)


@pytest.mark.parametrize(
    ["combined_var_input", "omit_legend_prefix", "omit_legend_suffix", "expected_output"],
    [
        ("dummy_var", True, True, "dummy_var"),
        ("dummy_prefix.dummy_var", True, True, "dummy_var"),
        ("DummyClass.dummy_method.dummy_var", True, True, "dummy_var"),
        ("dummy_prefix.dummy_var.dummy_var2", True, True, "dummy_var.dummy_var2"),
        ("dummy_prefix.dummy_var.field='field'", True, True, "dummy_var"),
        ("DummyClass.dummy_method.dummy_var.field='field'", True, True, "dummy_var"),
        ("dummy_prefix.dummy_var.dummy_var2.dummy_var3", True, True, "dummy_var.dummy_var2.dummy_var3"),
        ("dummy_prefix.dummy_var.dummy_var2.field='field'", True, True, "dummy_var.dummy_var2"),
        ("DummyClass.dummy_method.dummy_var.dummy_var2.field='field'", True, True, "dummy_var.dummy_var2"),
        ("DummyClass.dummy_method.dummy_var.dummy_var2.dummy_var3", True, True, "dummy_var.dummy_var2.dummy_var3"),
        (
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3.dummy_var4",
            True,
            True,
            "dummy_var.dummy_var2.dummy_var3.dummy_var4",
        ),
        ("dummy_prefix.dummy_var.dummy_var2.dummy_var3.field='field'", True, True, "dummy_var.dummy_var2.dummy_var3"),
        ("dummy_var", True, False, "dummy_var"),
        ("dummy_prefix.dummy_var", True, False, "dummy_var"),
        ("DummyClass.dummy_method.dummy_var", True, False, "dummy_var"),
        ("dummy_prefix.dummy_var.dummy_var2", True, False, "dummy_var.dummy_var2"),
        ("dummy_prefix.dummy_var.field='field'", True, False, "dummy_var.field='field'"),
        ("DummyClass.dummy_method.dummy_var.field='field'", True, False, "dummy_var.field='field'"),
        ("dummy_prefix.dummy_var.dummy_var2.dummy_var3", True, False, "dummy_var.dummy_var2.dummy_var3"),
        ("dummy_prefix.dummy_var.dummy_var2.field='field'", True, False, "dummy_var.dummy_var2.field='field'"),
        (
            "DummyClass.dummy_method.dummy_var.dummy_var2.field='field'",
            True,
            False,
            "dummy_var.dummy_var2.field='field'",
        ),
        ("DummyClass.dummy_method.dummy_var.dummy_var2.dummy_var3", True, False, "dummy_var.dummy_var2.dummy_var3"),
        (
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3.dummy_var4",
            True,
            False,
            "dummy_var.dummy_var2.dummy_var3.dummy_var4",
        ),
        (
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3.field='field'",
            True,
            False,
            "dummy_var.dummy_var2.dummy_var3.field='field'",
        ),
        ("dummy_var", False, True, "dummy_var"),
        ("Time.dummy_var", False, True, "dummy_var"),
        ("DummyClass.dummy_method.dummy_var", False, True, "DummyClass.dummy_method.dummy_var"),
        ("dummy_prefix.dummy_var.dummy_var2", False, True, "dummy_prefix.dummy_var.dummy_var2"),
        ("dummy_prefix.dummy_var.field='field'", False, True, "dummy_prefix.dummy_var"),
        ("DummyClass.dummy_method.dummy_var.field='field'", False, True, "DummyClass.dummy_method.dummy_var"),
        ("dummy_prefix.dummy_var.dummy_var2.dummy_var3", False, True, "dummy_prefix.dummy_var.dummy_var2.dummy_var3"),
        ("dummy_prefix.dummy_var.dummy_var2.field='field'", False, True, "dummy_prefix.dummy_var.dummy_var2"),
        (
            "DummyClass.dummy_method.dummy_var.dummy_var2.field='field'",
            False,
            True,
            "DummyClass.dummy_method.dummy_var.dummy_var2",
        ),
        (
            "DummyClass.dummy_method.dummy_var.dummy_var2.dummy_var3",
            False,
            True,
            "DummyClass.dummy_method.dummy_var.dummy_var2.dummy_var3",
        ),
        (
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3.dummy_var4",
            False,
            True,
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3.dummy_var4",
        ),
        (
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3.field='field'",
            False,
            True,
            "dummy_prefix.dummy_var.dummy_var2.dummy_var3",
        ),
    ],
)
def test_generate_legend_keys(
    combined_var_input: str,
    omit_legend_prefix: bool,
    omit_legend_suffix: bool,
    expected_output: str,
    graph_generator: GraphGenerator,
) -> None:
    actual_output = graph_generator._generate_legend_keys(combined_var_input, omit_legend_prefix, omit_legend_suffix)
    assert actual_output == expected_output


def test_draw_graph_exception(graph_generator: GraphGenerator) -> None:
    with pytest.raises(ValueError):
        graph_generator._draw_graph(
            graph_type="invalid graph type",
            data={},
            selected_variables=["var1", "var2"],
        )
    with pytest.raises(TypeError):
        graph_generator._draw_graph(
            graph_type="plot",
            data={
                "key1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
                "key2": {"values": [{"a": 5, "b": 6}, {"a": 7, "b": 8}]},
            },
            selected_variables=None,
        )


def test_draw_graph_success_tuple_plot(graph_generator: GraphGenerator) -> None:
    data = {"key1": [1, 2, 3, 4], "key2": [5, 6, 7, 8]}
    selected_variables = ["key1", "key2"]
    with patch.dict(
        "RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS", {"stackplot": MagicMock()}
    ) as mock_plot_functions_dict:
        graph_generator._draw_graph("stackplot", data, selected_variables)

        mock_plot_functions_dict["stackplot"].assert_called_once_with(
            list(range(len(data["key1"]))), (data["key1"], data["key2"])
        )


def test_draw_graph_success_plot(graph_generator: GraphGenerator) -> None:
    data = {"key1": [1, 2, 3, 4], "key2": [5, 6, 7, 8]}
    with patch.dict(
        "RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS", {"plot": MagicMock()}
    ) as mock_plot_functions_dict:
        graph_generator._draw_graph("plot", data)

        for value in data.values():
            mock_plot_functions_dict["plot"].assert_any_call(value)


@pytest.mark.parametrize(
    "filtered_pool,graph_details,expected_util_convert_list_return,expected_util_filter_dict,expected_result",
    [
        (
            {"variable1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": "ungraphable string"}]}},
            {"variables": ["a", "b"], "title": "Test_6"},
            [{"a": [1, 3], "b": [2, "ungraphable string"]}],
            [{"a": [1, 3], "b": [2, "ungraphable string"]}],
            [
                {
                    "error": "Can't plot Test_6 data set",
                    "message": "variable1 key contains non-numerical data that are {<class 'dict'>} and "
                    "can't be graphed.",
                    "info_map": {
                        "class": "GraphGenerator",
                        "function": "_log_non_numerical_data",
                    },
                }
            ],
        ),
        (
            {"variable1": {"values": "a"}},
            {"title": "Test_6"},
            ["ungraphable string"],
            ["ungraphable string"],
            [
                {
                    "error": "Can't plot Test_6 data set",
                    "message": "variable1 key contains non-numerical data that are <class 'str'> and "
                    "can't be graphed.",
                    "info_map": {
                        "class": "GraphGenerator",
                        "function": "_log_non_numerical_data",
                    },
                }
            ],
        ),
    ],
)
@patch("RUFAS.util.Utility.convert_list_of_dicts_to_dict_of_lists")
@patch("RUFAS.util.Utility.filter_dictionary")
def test_log_non_numerical_data(
    mock_filter_dict,
    mock_convert_list,
    filtered_pool: Dict[str, Dict[str, List[int | float | Dict[str, int | float]]]],
    graph_details: Dict[str, str | List[str]],
    expected_util_convert_list_return: Dict[str, List[int | float]],
    expected_util_filter_dict: Dict[str, List[int | float]],
    expected_result: List[int | float],
) -> None:
    # Arrange
    filtered_pool = filtered_pool
    graph_details = graph_details
    mock_graph_generator = GraphGenerator()
    mock_convert_list.side_effect = expected_util_convert_list_return
    mock_filter_dict.side_effect = expected_util_filter_dict

    # Act
    log_pool = mock_graph_generator._log_non_numerical_data(filtered_pool, graph_details)

    # Assert
    assert log_pool == expected_result


@pytest.mark.parametrize(
    "graph_details, expected_length, expected_message",
    [
        (
            {
                "type": "plot",
                "title": "Valid Graph",
                "filters": ["a", "b"],
                "variables": ["a", "b"],
            },
            0,
            None,
        ),
        (
            {
                "type": "stackplot",
                "title": "Valid Graph",
                "bad_filters": ["a", "b"],
                "variables": ["a", "b"],
            },
            1,
            "Required key 'filters' not in your graph filter file.",
        ),
        (
            {
                "type": "scatter",
                "tightle": "Valid Graph",
                "filters": ["a", "b"],
                "variables": ["a", "b"],
            },
            1,
            "Invalid filter file key 'tightle' does not matchany optional keys. "
            "Please see Graph Generator wiki for a list of valid filterkeys.",
        ),
    ],
)
def test_validate_graph_filter(
    graph_generator: GraphGenerator,
    graph_details: Dict[str, str],
    expected_length: int,
    expected_message: str,
) -> None:
    """Test for the _validate_graph_filter() method in graph_generator.py"""
    result = graph_generator._validate_graph_filter(graph_details)
    assert len(result) == expected_length

    if expected_length > 0:
        assert expected_message in result[0]["message"]


@pytest.mark.parametrize(
    "filtered_pool, expected_output, expected_logs",
    [
        (
            {
                "temperature": {"values": [20, 21], "info_maps": [{"units": "Celsius"}]},
                "pressure": {"values": [1, 2], "info_maps": [{"units": "Bar"}]},
            },
            {
                "temperature ('Celsius')": {"values": [20, 21], "info_maps": [{"units": "Celsius"}]},
                "pressure ('Bar')": {"values": [1, 2], "info_maps": [{"units": "Bar"}]},
            },
            [],
        ),
        (
            {"temperature": {"values": [20, 21]}},
            {"temperature": {"values": [20, 21]}},
            [
                {
                    "error": "Can't add units to variables for graphing",
                    "message": "'info_maps' unavailable to get units, check setting for exclude_info_maps.",
                    "info_map": {"class": "GraphGenerator", "function": "_add_var_units"},
                }
            ],
        ),
    ],
)
def test_add_var_units(
    graph_generator: GraphGenerator,
    filtered_pool: dict[str, dict[str, list[Any]]],
    expected_output: dict[str, dict[str, list[Any]]],
    expected_logs: list[dict[str, str | dict[str, str]]],
):
    updated_pool, logs = graph_generator._add_var_units(filtered_pool)
    assert updated_pool == expected_output
    assert logs == expected_logs
