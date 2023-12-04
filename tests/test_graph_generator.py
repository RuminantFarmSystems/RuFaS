from pathlib import Path
from freezegun import freeze_time
from typing import Dict, List
from unittest.mock import patch
from matplotlib import pyplot as plt
from mock.mock import MagicMock
import pytest
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

        with patch(
            "RUFAS.graph_generator.GraphGenerator._generate_graph_path"
        ) as mock_generate_graph_path:
            mock_generate_graph_path.return_value = Path("graph_path")

            result = graph_generator._save_graph(
                graph_details, filter_file_name, graphics_dir
            )

            mock_savefig.assert_called_once_with(mock_generate_graph_path.return_value)
            mock_generate_graph_path.assert_called_once_with(
                graph_details, filter_file_name, graphics_dir
            )
            assert result == mock_generate_graph_path.return_value


@pytest.mark.skip
def test_save_graph_exception(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    save_path = Path(r"/path/to/save")
    graphics_dir = Path("graphics")

    with patch("RUFAS.graph_generator.matplotlib.pyplot.savefig") as mock_savefig:
        mock_savefig.side_effect = Exception("test")
        with pytest.raises(Exception, match="test"):
            graph_generator._save_graph(
                graph_details, filter_file_name, save_path, graphics_dir
            )


def test_generate_graph_path_with_title(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir: str = "graphics"

    with freeze_time("2023-10-13 11:41:23"):
        result = graph_generator._generate_graph_path(
            graph_details, filter_file_name, graphics_dir
        )
        assert result == Path(
            r"graphics/metadata_name_test-graph-13-Oct-2023_Fri_11-41-23.png"
        )


def test_generate_graph_path_no_title(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    graphics_dir: str = "graphics"

    with freeze_time("2023-10-13 11:41:23"):
        result = graph_generator._generate_graph_path(
            graph_details, filter_file_name, graphics_dir
        )
        assert result == Path(
            r"graphics/metadata_name_test_filter.png-13-Oct-2023_Fri_11-41-23.png"
        )


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


def test_generate_graph_success(graph_generator: GraphGenerator) -> None:
    graph_generator._draw_graph = MagicMock()
    graph_generator._customize_graph = MagicMock()
    graph_generator._save_graph = MagicMock(return_value="graph path")
    filtered_pool = {}
    graph_details = {"type": "plot", "variables": ["var1", "var2"]}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    assert "graph path" == graph_generator.generate_graph(
        filtered_pool, graph_details, filter_file_name, graphics_dir
    )
    graph_generator._draw_graph.assert_called_once_with(
        "plot", filtered_pool, filtered_pool.keys()
    )
    graph_generator._customize_graph.assert_called_once()
    graph_generator._save_graph.assert_called_once_with(
        graph_details, filter_file_name, graphics_dir
    )


def test_generate_graph_exception(graph_generator: GraphGenerator) -> None:
    graph_generator._draw_graph = MagicMock()
    graph_generator._customize_graph = MagicMock()
    graph_generator._save_graph = MagicMock(side_effect=Exception)
    filtered_pool = {}
    graph_details = {"type": "plot", "variables": ["var1", "var2"]}
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    with pytest.raises(Exception):
        graph_generator.generate_graph(
            filtered_pool, graph_details, filter_file_name, graphics_dir
        )


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
    data = {"key1": [1, 2, 3, 4],
            "key2": [5, 6, 7, 8]
            }
    selected_variables = ["key1", "key2"]
    with patch.dict("RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS",
                    {"stackplot": MagicMock()}) as mock_plot_functions_dict:
        graph_generator._draw_graph(
            "stackplot", data, selected_variables
            )

        mock_plot_functions_dict["stackplot"].assert_called_once_with(list(range(len(data["key1"]))),
                                                                      (data["key1"], data["key2"]))


def test_draw_graph_success_plot(graph_generator: GraphGenerator) -> None:
    data = {"key1": [1, 2, 3, 4],
            "key2": [5, 6, 7, 8]
            }
    with patch.dict("RUFAS.graph_generator.MATPLOTLIB_PLOT_FUNCTIONS",
                    {"plot": MagicMock()}) as mock_plot_functions_dict:
        graph_generator._draw_graph(
            "plot", data
            )

        for value in data.values():
            mock_plot_functions_dict["plot"].assert_any_call(value)


@pytest.mark.parametrize(
    "filtered_pool,selected_variables,expected_result",
    [
        (
            {"variable1": {"values": [1, 2, 3]}, "variable2": {"values": [4, 5, 6]}},
            None,
            {"variable1": [1, 2, 3], "variable2": [4, 5, 6]},
        ),
        (
            {"variable1": {"values": [1, 2, 3]}, "variable2": {"values": [4, 5, 6]}},
            ["custom_var1", "custom_var2"],
            {"custom_var1": [1, 2, 3], "custom_var2": [4, 5, 6]},
        ),
        (
            {"variable1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
             "variable2": {"values": [{"a": 5, "b": 6}, {"a": 7, "b": 8}]}},
            None,
            {},
        ),
        (
            {"variable1": {"values": [{"a": 1, "b": 2, "c": 25}, {"a": 3, "b": 4, "c": 25}]},
             "variable2": {"values": [{"a": 5, "b": 6, "c": 25}, {"a": 7, "b": 8, "c": 25}]}},
            ["a", "b"],
            {"a": [1, 3, 5, 7], "b": [2, 4, 6, 8]},
        ),
    ],
)
def test_prepare_plot_data(graph_generator: GraphGenerator,
                           filtered_pool: Dict[str, Dict[str, List[int | float | Dict[str, int | float]]]],
                           selected_variables: List[str],
                           expected_result: Dict[str, List[int | float]],
                           ) -> None:
    result = graph_generator._prepare_plot_data(filtered_pool, selected_variables)
    assert result == expected_result
