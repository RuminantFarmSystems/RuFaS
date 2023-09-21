"""
RUFAS: Ruminant Farm Systems Model
File name: test_graph_generator.py
Description: Implements test cases for the GraphGenerator class
Author(s): Allister Liu, al2562@cornell.edu
"""
import pytest
from mock.mock import MagicMock, patch
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.figure, matplotlib.axes

from RUFAS.graph_generator import GraphGenerator


@pytest.fixture
def mock_graph_generator(mocker) -> GraphGenerator:
    graph_generator = GraphGenerator()
    return graph_generator


@pytest.fixture
def graph_generator_original_states(
        mock_graph_generator: GraphGenerator
) -> dict[str, callable]:
    """Fixture to store original methods of GraphGenerator"""
    return {
        "generate_graph": mock_graph_generator.generate_graph,
        "_line_graph": mock_graph_generator._line_graph,
        "_bar_graph": mock_graph_generator._bar_graph,
        "_customize_graph": mock_graph_generator._customize_graph,
    }


@pytest.mark.parametrize(
    "filtered_pool, graph_info, graph_path",
    [
        (
                {"dummy.variable": {"values": [1, 2, 3]}},
                {"graph_type": "Line graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"},
                "dummy\\path"),
        (
                {"a": {"values": 1}, "b": {"values": 2}, "c": {"values": 3}},
                {"graph_type": "Bar graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"},
                "dummy\\path"),
    ]
)
def test_generate_graph(mock_graph_generator: GraphGenerator,
                        graph_generator_original_states: dict[str, callable],
                        filtered_pool: dict,
                        graph_info: dict,
                        graph_path: str) -> None:
    mock_graph_generator._line_graph = MagicMock()
    mock_graph_generator._bar_graph = MagicMock()

    mock_graph_generator.generate_graph(filtered_pool, graph_info, graph_path)

    if graph_info["graph_type"] == "Line graph":
        mock_graph_generator._line_graph.assert_called_once_with(filtered_pool, graph_info, graph_path)
    elif graph_info["graph_type"] == "Bar graph":
        mock_graph_generator._bar_graph.assert_called_once_with(filtered_pool, graph_info, graph_path)

    mock_graph_generator._line_graph = graph_generator_original_states["_line_graph"]
    mock_graph_generator._bar_graph = graph_generator_original_states["_bar_graph"]


@pytest.mark.parametrize(
    "filtered_pool, graph_info, graph_path",
    [
        (
                {"dummy.variable": {"values": [1, 2, 3]}},
                {"graph_type": "Line graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"},
                "dummy\\path"),
        (
                {"dummy.variable_1": {"values": [1, 2, 3]}, "dummy.variable_2": {"values": [4, 5, 6]}},
                {"graph_type": "Line graph",
                 "filter": ["dummy.variable*"],
                 "title": "Dummy Variable"},
                "dummy\\path"),
    ]
)
def test_line_graph(mock_graph_generator: GraphGenerator,
                    graph_generator_original_states: dict[str, callable],
                    filtered_pool: dict,
                    graph_info: dict,
                    graph_path: str) -> None:

    mock_graph_generator._customize_graph = MagicMock()
    mock_fig = MagicMock(spec=matplotlib.figure.Figure)
    mock_ax = MagicMock(spec=matplotlib.axes.Axes)
    mock_savefig = MagicMock()

    with patch.object(matplotlib.pyplot, "subplots", return_value=(mock_fig, mock_ax)) as mock_subplots:
        with patch.object(matplotlib.pyplot, "savefig", mock_savefig):
            mock_graph_generator._line_graph(filtered_pool, graph_info, graph_path)

    mock_graph_generator._customize_graph.assert_called_once_with(mock_fig, graph_info)

    mock_subplots.assert_called_once()
    mock_ax.plot.assert_called()
    mock_savefig.assert_called_once_with(graph_path)

    mock_graph_generator._customize_graph = graph_generator_original_states["_customize_graph"]


@pytest.mark.parametrize(
    "filtered_pool, graph_info, graph_path",
    [
        (
                {"a": {"values": 1}, "b": {"values": 2}, "c": {"values": 3}},
                {"graph_type": "Bar graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"},
                "dummy\\path"),
    ]
)
def test_bar_graph(mock_graph_generator: GraphGenerator,
                    graph_generator_original_states: dict[str, callable],
                    filtered_pool: dict,
                    graph_info: dict,
                    graph_path: str) -> None:

    mock_graph_generator._customize_graph = MagicMock()
    mock_fig = MagicMock(spec=matplotlib.figure.Figure)
    mock_ax = MagicMock(spec=matplotlib.axes.Axes)
    mock_bar = MagicMock()
    mock_savefig = MagicMock()

    with patch.object(matplotlib.pyplot, "subplots", return_value=(mock_fig, mock_ax)) as mock_subplots:
        with patch.object(mock_ax, "bar", mock_bar):
            with patch.object(matplotlib.pyplot, "savefig", mock_savefig):
                mock_graph_generator._line_graph(filtered_pool, graph_info, graph_path)

    mock_graph_generator._customize_graph.assert_called_once_with(mock_fig, graph_info)

    mock_subplots.assert_called_once()
    # mock_ax.bar.assert_called()
    mock_savefig.assert_called_once_with(graph_path)

    mock_graph_generator._customize_graph = graph_generator_original_states["_customize_graph"]
