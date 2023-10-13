from freezegun import freeze_time
from typing import Dict
from unittest.mock import patch
import pytest
from RUFAS.graph_generator import GraphGenerator


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
            mock_generate_graph_path.return_value = "graph_path"

            result = graph_generator._save_graph(
                graph_details, filter_file_name, save_path, graphics_dir
            )

            mock_savefig.assert_called_once_with(mock_generate_graph_path.return_value)
            mock_generate_graph_path.assert_called_once_with(
                save_path, graph_details, filter_file_name, graphics_dir
            )
            assert result == mock_generate_graph_path.return_value


def test_save_graph_exception(graph_generator: GraphGenerator) -> None:
    graph_details: Dict[str, str] = {
        "title": "Test Graph",
        "x_label": "X Axis",
        "y_label": "Y Axis",
    }
    filter_file_name: str = "test_filter.png"
    save_path: str = "/path/to/save"
    graphics_dir: str = "graphics"

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
            assert (
                result
                == "/path/to/save\\graphics\\test-graph-13-Oct-2023_Fri_11-41-23.png"
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
            assert (
                result
                == "/path/to/save\\graphics\\saved_graph_test_filter.png-13-Oct-2023_Fri_11-41-23.png"
            )
