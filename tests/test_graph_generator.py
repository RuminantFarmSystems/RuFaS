from pathlib import Path
from freezegun import freeze_time
from typing import Dict
from unittest.mock import patch
from matplotlib import pyplot as plt
from mock.mock import MagicMock
import pytest
from RUFAS.graph_generator import GraphGenerator, TUPLE_BASED_FUNCTIONS


@pytest.fixture
def graph_generator() -> GraphGenerator:
    return GraphGenerator()


def test_save_graph_successful(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    save_path: str = "/path/to/save"
    graphics_dir: str = "graphics"

    with patch("RUFAS.graph_generator.matplotlib.pyplot.savefig") as mock_savefig:
        mock_savefig.return_value = None

        with patch(
            "RUFAS.graph_generator.GraphGenerator._generate_graph_path"
        ) as mock_generate_graph_path:
            mock_generate_graph_path.return_value = Path("graph_path")

            result = graph_generator._save_graph(
                graph_details, filter_file_name, save_path, graphics_dir
            )

            mock_savefig.assert_called_once_with(mock_generate_graph_path.return_value)
            mock_generate_graph_path.assert_called_once_with(
                save_path, graph_details, filter_file_name, graphics_dir
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


def test_generate_graph_path_exception(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    save_path: str = "/path/to/save"
    graphics_dir: str = "graphics"
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.side_effect = Exception("test")
        with pytest.raises(Exception, match="test"):
            graph_generator._generate_graph_path(
                save_path, graph_details, filter_file_name, graphics_dir
            )


def test_generate_graph_path_with_title(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    save_path: str = "/path/to/save"
    graphics_dir: str = "graphics"

    with freeze_time("2023-10-13 11:41:23"):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            result = graph_generator._generate_graph_path(
                save_path, graph_details, filter_file_name, graphics_dir
            )
            mock_mkdir.assert_called_once()
            assert result == Path(
                r"/path/to/save/graphics/_test-graph-13-Oct-2023_Fri_11-41-23.png"
            )


def test_generate_graph_path_no_title(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    save_path: str = "/path/to/save"
    graphics_dir: str = "graphics"

    with freeze_time("2023-10-13 11:41:23"):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            result = graph_generator._generate_graph_path(
                save_path, graph_details, filter_file_name, graphics_dir
            )
            mock_mkdir.assert_called_once()
            assert result == Path(
                r"/path/to/save/graphics/saved_graph_test_filter.png-13-Oct-2023_Fri_11-41-23.png"
            )


def test_handle_tuple_based_plot(graph_generator: GraphGenerator) -> None:
    data_dict = {
        "var1": [1, 2, 3],
        "var2": [4, 5, 6],
        "var3": [7, 8, 9],
        "var4": [10, 11, 12],
    }
    selected_variables = ["var1", "var2"]

    def mock_plot_function(x, y):
        assert x == [0, 1, 2]
        assert y == (data_dict["var1"], data_dict["var2"])

    graph_generator._handle_tuple_based_plot(
        data_dict, selected_variables, mock_plot_function
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
    save_path = Path("save")
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    assert "graph path" == graph_generator.generate_graph(
        filtered_pool, graph_details, save_path, filter_file_name, graphics_dir
    )
    graph_generator._draw_graph.assert_called_once_with(
        "plot", filtered_pool, ["var1", "var2"]
    )
    graph_generator._customize_graph.assert_called_once()
    graph_generator._save_graph.assert_called_once_with(
        graph_details, filter_file_name, save_path, graphics_dir
    )


def test_generate_graph_exception(graph_generator: GraphGenerator) -> None:
    graph_generator._draw_graph = MagicMock()
    graph_generator._customize_graph = MagicMock()
    graph_generator._save_graph = MagicMock(side_effect=Exception)
    filtered_pool = {}
    graph_details = {"type": "plot", "variables": ["var1", "var2"]}
    save_path = Path("save")
    filter_file_name = "filter_file"
    graphics_dir = Path("graphs")
    with pytest.raises(Exception):
        graph_generator.generate_graph(
            filtered_pool, graph_details, save_path, filter_file_name, graphics_dir
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


def test_draw_graph_success(graph_generator: GraphGenerator) -> None:
    graph_type = TUPLE_BASED_FUNCTIONS[0]
    data = {
        "key1": {"values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
        "key2": {"values": [{"a": 5, "b": 6}, {"a": 7, "b": 8}]},
    }
    graph_generator._handle_tuple_based_plot = MagicMock()
    with patch(
        "RUFAS.graph_generator.Utility.convert_list_of_dicts_to_dict_of_lists"
    ) as mock_utility:
        graph_generator._draw_graph(graph_type, data, ["a", "b"])
        assert graph_generator._handle_tuple_based_plot.call_count == 2
        assert mock_utility.call_count == 2
