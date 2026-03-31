import datetime
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import pytest
from freezegun import freeze_time
from matplotlib import pyplot as plt
from pytest_mock import MockerFixture
from RUFAS.graph_generator import GraphGenerator


@pytest.fixture
def graph_generator() -> GraphGenerator:
    return GraphGenerator("metadata_name")


def test_save_graph_successful(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir: str = "graphics"

    mock_savefig = mocker.patch("RUFAS.graph_generator.matplotlib.pyplot.savefig", return_value=None)

    mock_generate_graph_path = mocker.patch(
        "RUFAS.graph_generator.GraphGenerator._generate_graph_path", return_value=Path("graph_path")
    )

    result = graph_generator._save_graph(graph_details, filter_file_name, graphics_dir)

    mock_savefig.assert_called_once_with(mock_generate_graph_path.return_value, bbox_inches="tight")
    mock_generate_graph_path.assert_called_once_with(graph_details, filter_file_name, graphics_dir)
    assert result == mock_generate_graph_path.return_value


def test_save_graph_exception(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir = Path("graphics")

    mocker.patch("RUFAS.graph_generator.matplotlib.pyplot.savefig", side_effect=Exception("test"))
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


@pytest.mark.parametrize(
    ["graph_details", "expected_output", "produce_graphics"],
    [
        (
            {"title": "Example Graph"},
            [
                {
                    "error": "Can't plot Example Graph data set",
                    "message": "'produce_graphics' set to False, no graphs will be produced.",
                    "info_map": {
                        "class": "GraphGenerator",
                        "function": "generate_graph",
                    },
                }
            ],
            False,
        ),
        (
            {"title": "Quiver Fail Graph", "type": "quiver_key"},
            [
                {
                    "error": "Can't plot Quiver Fail Graph data set",
                    "message": "Graph type 'quiver_key' not supported at this time.",
                    "info_map": {
                        "class": "GraphGenerator",
                        "function": "generate_graph",
                    },
                }
            ],
            True,
        ),
    ],
)
def test_generate_graph_without_producing_graphics(
    graph_generator: GraphGenerator,
    graph_details: list[dict[str, str]],
    expected_output: dict[str, str | dict[str, Any]],
    produce_graphics: bool,
) -> None:
    """Tests function generate_graph when it doesn't produce graphics."""
    filtered_pool = {"dummy_key": {"dummy_data": [1, 2, 3]}}
    filter_file_name = "dummy_filter"
    graphics_dir = Path("/tmp")

    result = graph_generator.generate_graph(
        filtered_pool=filtered_pool,
        graph_details=graph_details,
        filter_file_name=filter_file_name,
        graphics_dir=graphics_dir,
        produce_graphics=produce_graphics,
    )

    assert result == expected_output, "Function did not return expected log message when produce_graphics is False."


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


def test_generate_graph_error_found(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    graph_generator._draw_graph = mocker.MagicMock()
    graph_generator._customize_graph = mocker.MagicMock()
    graph_generator._save_graph = mocker.MagicMock(return_value="graph path")
    filtered_pool = {"var1": {"values": [1, 2, 3]}}
    mock_non_numerical_log_pool = [{"error": "mock_error_message"}]
    mock_add_units_log_pool = [{"warning": "mock_warning_message"}]
    full_mock_pool = mock_non_numerical_log_pool + mock_add_units_log_pool
    graph_generator._log_non_numerical_data = mocker.MagicMock(return_value=mock_non_numerical_log_pool)
    graph_generator._add_var_units = mocker.MagicMock(return_value=({}, mock_add_units_log_pool))
    graph_details = {"type": "plot", "variables": ["var1", "var2"]}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    assert full_mock_pool == graph_generator.generate_graph(
        filtered_pool, graph_details, filter_file_name, graphics_dir, True
    )
    graph_generator._draw_graph.assert_not_called()
    graph_generator._customize_graph.assert_not_called()
    graph_generator._save_graph.assert_not_called()


def test_generate_graph_success(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    mocker.patch.object(graph_generator, "_draw_graph")
    mocker.patch.object(graph_generator, "_customize_graph")
    mocker.patch.object(graph_generator, "_save_graph", return_value="graph path")
    filtered_pool = {"var1": {"values": [1, 2, 3]}}
    updated_pool = {"var1": {"values": [1, 2, 3], "units": "units"}}
    var_units_logs = []
    mocker.patch.object(graph_generator, "_add_var_units", return_value=(updated_pool, var_units_logs))
    prepared_data = {"var1": [1, 2, 3]}
    mock_remove_special_chars = mocker.patch("RUFAS.util.Utility.remove_special_chars", return_value="cleaned_title")

    mock_log_pool = [
        {"log": "mock_log_message"},
        {
            "log": "Variable mapping for cleaned_title: {'Legend Key': 'Original Var Name'}",
            "message": "{'var1': 'var1'}",
            "info_map": {"class": "GraphGenerator", "function": "generate_graph"},
        },
    ]
    mocker.patch.object(graph_generator, "_log_non_numerical_data", return_value=[{"log": "mock_log_message"}])
    graph_details = {"type": "plot", "filters": ["var1", "var2"], "title": "dummy.graph/title", "display_units": True}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    mock_ax = mocker.MagicMock()
    mocker.patch("matplotlib.pyplot.subplots", return_value=(mocker.MagicMock(), mock_ax))

    assert (
        graph_generator.generate_graph(filtered_pool, graph_details, filter_file_name, graphics_dir, True)
        == mock_log_pool
    )

    graph_generator._draw_graph.assert_called_once_with(
        "plot", prepared_data, list(prepared_data.keys()), mock_ax, False, False, None, None, None
    )
    graph_generator._customize_graph.assert_called_once()
    graph_generator._save_graph.assert_called_once_with(graph_details, filter_file_name, graphics_dir)
    mock_remove_special_chars.assert_called_once()
    graph_generator._add_var_units.assert_called_once_with(filtered_pool, "dummy.graph/title")


def test_generate_graph_with_custom_legend(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    mocker.patch.object(graph_generator, "_draw_graph")
    mocker.patch.object(graph_generator, "_customize_graph")
    mocker.patch.object(graph_generator, "_save_graph")
    mock_generate_legend_keys = mocker.patch.object(
        graph_generator,
        "_generate_legend_keys",
        side_effect=lambda k, **kwargs: f"legend_{k}",
    )
    mocker.patch.object(
        graph_generator,
        "_add_var_units",
        return_value=({"var1": {"values": [1, 2, 3]}, "var2": {"values": [4, 5, 6]}}, []),
    )
    mocker.patch.object(graph_generator, "_log_non_numerical_data", return_value=[])
    mock_ax = mocker.MagicMock()
    mocker.patch("matplotlib.pyplot.subplots", return_value=(mocker.MagicMock(), mock_ax))

    filtered_pool = {"var1": {"values": [1, 2, 3]}, "var2": {"values": [4, 5, 6]}}
    graph_details = {
        "type": "plot",
        "filters": ["var1", "var2"],
        "title": "dummy graph",
        "legend": True,
    }
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")

    graph_generator.generate_graph(filtered_pool, graph_details, filter_file_name, graphics_dir, True)

    mock_generate_legend_keys.assert_any_call("var1", omit_legend_prefix=True, omit_legend_suffix=False)
    mock_generate_legend_keys.assert_any_call("var2", omit_legend_prefix=True, omit_legend_suffix=False)

    sorted_keys = ["var1", "var2"]
    expected_prepared_data = {"var1": [1, 2, 3], "var2": [4, 5, 6]}
    graph_generator._draw_graph.assert_called_once_with(
        "plot", expected_prepared_data, sorted_keys, mock_ax, False, False, None, None, None
    )

    graph_generator._customize_graph.assert_called_once()
    graph_generator._save_graph.assert_called_once_with(graph_details, filter_file_name, graphics_dir)


def test_generate_graph_exception(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    mocker.patch.object(graph_generator, "_draw_graph")
    mocker.patch.object(graph_generator, "_customize_graph")
    mocker.patch.object(graph_generator, "_save_graph", side_effect=Exception)
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
        ("RufasTime.dummy_var", False, True, "dummy_var"),
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
        (
            "dummy_prefix.dummy_method.dummy_var=dummy_value (units)",
            True,
            True,
            "dummy_method (units)",
        ),
        (
            "",
            False,
            False,
            "",
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


@pytest.mark.parametrize(
    "graph_details, prepared_data, expected_legend",
    [
        ({"variables": ["Temperature"]}, {"Temperature": [20, 22, 21], "Humidity": [30, 45, 65]}, ["Temperature"]),
        (
            {"omit_legend_prefix": True, "omit_legend_suffix": True},
            {"prefix.temp.suffix=suffix": [20, 22, 21]},
            ["temp"],
        ),
        ({}, {"Temperature": [20, 22, 21], "Humidity": [30, 45, 65]}, ["Temperature", "Humidity"]),
        ({}, {}, []),
    ],
)
def test_set_graph_legend(graph_generator: GraphGenerator, graph_details, prepared_data, expected_legend) -> None:
    result = graph_generator._set_graph_legend(graph_details, prepared_data)
    assert result["legend"] == expected_legend


def test_draw_graph_exception(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    mock_ax = mocker.MagicMock()
    mocker.patch("matplotlib.pyplot.subplots", return_value=(mocker.MagicMock(), mock_ax))
    mock_time = mocker.MagicMock()
    mock_time.start_date = datetime.datetime(2020, 1, 1)
    graph_generator.time = mock_time
    with pytest.raises(ValueError):
        graph_generator._draw_graph(
            graph_type="invalid graph type",
            data={},
            selected_variables=["var1", "var2"],
            mask_values=False,
            ax=mock_ax,
            use_calendar_dates=False,
        )
    with pytest.raises(TypeError):
        graph_generator._draw_graph(
            graph_type="plot",
            data={
                "key1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
                "key2": {"values": [{"a": 5, "b": 6}, {"a": 7, "b": 8}]},
            },
            selected_variables=None,
            mask_values=False,
            ax=mock_ax,
            use_calendar_dates=False,
        )


def test_draw_graph_success_tuple_plot(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    data: dict[str, list[int | float]] = {"key1": [1, 2, 3, 4], "key2": [5, 6, 7, 8]}
    selected_variables = ["key1", "key2"]
    mock_ax = mocker.MagicMock()
    mocker.patch("matplotlib.pyplot.subplots", return_value=(mocker.MagicMock(), mock_ax))
    mock_time = mocker.MagicMock()
    mock_time.start_date = datetime.datetime(2020, 1, 1)
    graph_generator.time = mock_time
    mock_stackplot = mocker.MagicMock()
    mock_plot_functions_dict = mocker.patch.dict(
        "RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS", {"stackplot": mock_stackplot}
    )
    graph_generator._draw_graph("stackplot", data, selected_variables, mock_ax, False, False)
    mock_plot_functions_dict["stackplot"].assert_called_once_with(
        list(range(len(data["key1"]))), (data["key1"], data["key2"])
    )


def test_draw_graph_success_plot(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    data: dict[str, list[int | float]] = {"key1": [1, 2, 3, 4], "key2": [5, 6, 7, 8]}
    indices = [0, 1, 2, 3]
    masked_indices = indices
    masked_values = [1, 2, 3, 4]
    mock_time = mocker.MagicMock()
    mock_time.start_date = datetime.datetime(2020, 1, 1)
    graph_generator.time = mock_time
    mock_ax = mocker.MagicMock()
    mocker.patch("matplotlib.pyplot.subplots", return_value=(mocker.MagicMock(), mock_ax))
    masker = mocker.patch(
        "RUFAS.graph_generator.GraphGenerator._mask_values", return_value=(masked_indices, masked_values)
    )

    mock_plot_functions_dict = mocker.patch.dict(
        "RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS", {"plot": mocker.MagicMock()}
    )
    graph_generator._draw_graph(
        "plot", data, list(data.keys()), mask_values=False, ax=mock_ax, use_calendar_dates=False
    )

    for key, value in data.items():
        mock_plot_functions_dict["plot"].assert_any_call(indices, value)

    graph_generator._draw_graph("plot", data, list(data.keys()), mask_values=True, ax=mock_ax, use_calendar_dates=False)

    for key, value in data.items():
        mock_plot_functions_dict["plot"].assert_any_call(masked_indices, masked_values)

    assert masker.call_count == 2


def test_draw_graph_sliced_data(graph_generator: GraphGenerator, mocker: MockerFixture) -> None:
    """Tests _draw_graph with in the GraphGenerator with sliced data."""
    data: dict[str, list[int | float]] = {
        "key1": [2, 3, 4],
        "key2": [8, 9, 10],
    }
    slice_start = 1
    slice_end = 4
    expected_indices = [
        datetime.datetime(2020, 1, 2),
        datetime.datetime(2020, 1, 3),
        datetime.datetime(2020, 1, 4),
    ]

    mock_time = mocker.MagicMock()
    mock_time.start_date = datetime.datetime(2020, 1, 1)
    mock_time.convert_slice_to_simulation_day.side_effect = lambda x: x
    mock_time.convert_simulation_day_to_date.side_effect = lambda x: mock_time.start_date + datetime.timedelta(days=x)
    graph_generator.time = mock_time

    mock_ax = mocker.MagicMock()
    mocker.patch("matplotlib.pyplot.subplots", return_value=(mocker.MagicMock(), mock_ax))
    masker = mocker.patch(
        "RUFAS.graph_generator.GraphGenerator._mask_values",
        side_effect=lambda values: (expected_indices, values),
    )

    mock_plot_functions_dict = mocker.patch.dict(
        "RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS", {"plot": mocker.MagicMock()}
    )
    graph_generator._draw_graph(
        "plot",
        data,
        list(data.keys()),
        mask_values=False,
        ax=mock_ax,
        use_calendar_dates=True,
        slice_start=slice_start,
        slice_end=slice_end,
    )

    mock_plot_functions_dict["plot"].assert_any_call(expected_indices, data["key1"])
    mock_plot_functions_dict["plot"].assert_any_call(expected_indices, data["key2"])

    graph_generator._draw_graph(
        "plot",
        data,
        list(data.keys()),
        mask_values=True,
        ax=mock_ax,
        use_calendar_dates=True,
        slice_start=slice_start,
        slice_end=slice_end,
    )

    mock_plot_functions_dict["plot"].assert_any_call(expected_indices, data["key1"])
    mock_plot_functions_dict["plot"].assert_any_call(expected_indices, data["key2"])

    assert masker.call_count == 2


def test_mask_values(graph_generator: GraphGenerator) -> None:
    """Tests _mask_values in the GraphGenerator."""
    values_one = [1, 2, 3, 4]

    actual_indices, actual_values = graph_generator._mask_values(values_one)

    assert list(actual_indices) == [0, 1, 2, 3]
    assert list(actual_values) == [1, 2, 3, 4]

    values_two = [np.nan, 8, 9, np.nan, np.nan]

    actual_indices, actual_values = graph_generator._mask_values(values_two)

    assert list(actual_indices) == [1, 2]
    assert list(actual_values) == [8, 9]


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
def test_log_non_numerical_data(
    filtered_pool: Dict[str, Dict[str, List[int | float | Dict[str, int | float]]]],
    graph_details: Dict[str, str | List[str]],
    expected_util_convert_list_return: Dict[str, List[int | float]],
    expected_util_filter_dict: Dict[str, List[int | float]],
    expected_result: List[int | float],
    mocker: MockerFixture,
) -> None:
    # Arrange
    mock_filter_dict = mocker.patch("RUFAS.util.Utility.filter_dictionary", return_value={"filtered": "data"})
    mock_convert_list = mocker.patch(
        "RUFAS.util.Utility.convert_list_of_dicts_to_dict_of_lists", return_value={"converted": "data"}
    )

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
    "filtered_pool, graph_title, expected_output, expected_logs",
    [
        (
            {"wind_speed": {"values": [5, 6], "info_maps": [{"units": {"wind_speed": "m/s"}}]}},
            "Wind Test",
            {"wind_speed (m/s)": {"values": [5, 6], "info_maps": [{"units": {"wind_speed": "m/s"}}]}},
            [],
        ),
        (
            {"wind_speed": {"values": [5, 6], "info_maps": [{"units": {"speed": "m/s"}}]}},
            "Wind Test",
            {"wind_speed (not available)": {"values": [5, 6], "info_maps": [{"units": {"speed": "m/s"}}]}},
            [
                {
                    "warning": "Missing unit information",
                    "message": "Unit for 'wind_speed' not found in units dictionary. Using default 'not available'.",
                    "info_map": {"class": "GraphGenerator", "function": "_add_var_units"},
                }
            ],
        ),
        (
            {"temperature": {"values": [20, 21]}},
            "Temperature Test",
            {"temperature": {"values": [20, 21]}},
            [
                {
                    "warning": "Can't add units to variables for graphing Temperature Test",
                    "message": "'info_maps' unavailable to get units, check setting for exclude_info_maps.",
                    "info_map": {"class": "GraphGenerator", "function": "_add_var_units"},
                }
            ],
        ),
        (
            {"temperature": {"values": [20, 21], "info_maps": [{"units": "Celsius"}]}},
            "Temperature Test",
            {"temperature (Celsius)": {"values": [20, 21], "info_maps": [{"units": "Celsius"}]}},
            [],
        ),
    ],
)
def test_add_var_units(
    graph_generator: GraphGenerator,
    filtered_pool: dict[str, dict[str, list[Any]]],
    graph_title: str,
    expected_output: dict[str, dict[str, list[Any]]],
    expected_logs: list[dict[str, str | dict[str, str]]],
) -> None:
    """Test for the _add_var_units() method in graph_generator.py"""
    updated_pool, logs = graph_generator._add_var_units(filtered_pool, graph_title)
    assert updated_pool == expected_output
    assert logs == expected_logs
