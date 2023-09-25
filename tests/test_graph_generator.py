"""
RUFAS: Ruminant Farm Systems Model
File name: test_graph_generator.py
Description: Implements test cases for the GraphGenerator class
Author(s): Allister Liu, al2562@cornell.edu
"""
import os
from pathlib import Path

import matplotlib
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import pytest
from freezegun import freeze_time
from mock.mock import MagicMock, patch, call

import RUFAS
from RUFAS.graph_generator import GraphGenerator

matplotlib.use('TkAgg')


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
        "_generate_graph_path": mock_graph_generator._generate_graph_path,
    }


@pytest.mark.parametrize(
    "filtered_pool, graph_info, save_path, filter_file_name",
    [
        (
                {"dummy.variable": {"values": [1, 2, 3]}},
                {"graph_type": "Line Graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"},
                "dummy\\path",
                "dummy_filter"
        ),
        (
                {"a": {"values": 1}, "b": {"values": 2}, "c": {"values": 3}},
                {"graph_type": "Bar Graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"},
                "dummy\\path",
                "dummy_filter"
        ),
        (
                {"dummy.variable": {"values": [1, 2, 3]}},
                {"graph_type": "Line Graph",
                 "filter": ["dummy.variable"]},
                "dummy\\path",
                "dummy_filter"
        ),

    ]
)
def test_generate_graph(mock_graph_generator: GraphGenerator,
                        graph_generator_original_states: dict[str, callable],
                        filtered_pool: dict,
                        graph_info: dict,
                        save_path: str,
                        filter_file_name: str) -> None:
    mock_graph_generator._line_graph = MagicMock()
    mock_graph_generator._bar_graph = MagicMock()
    mock_graph_generator._generate_graph_path = MagicMock()
    mock_savefig = MagicMock()

    with patch.object(matplotlib.pyplot, "savefig", mock_savefig):
        mock_graph_generator.generate_graph(filtered_pool, graph_info, save_path, filter_file_name)

    if graph_info["graph_type"] == "Line graph":
        mock_graph_generator._line_graph.assert_called_once_with(filtered_pool, graph_info, save_path, filter_file_name)
    elif graph_info["graph_type"] == "Bar graph":
        mock_graph_generator._bar_graph.assert_called_once_with(filtered_pool, graph_info, save_path, filter_file_name)
    mock_graph_generator._generate_graph_path.assert_called_once_with(save_path, graph_info, filter_file_name)
    mock_savefig.assert_called_once()

    mock_graph_generator._line_graph = graph_generator_original_states["_line_graph"]
    mock_graph_generator._bar_graph = graph_generator_original_states["_bar_graph"]
    mock_graph_generator._generate_graph_path = graph_generator_original_states["_generate_graph_path"]


@pytest.mark.parametrize(
    "filtered_pool, graph_info",
    [
        (
                {
                    "dummy.variable": {
                        "values": [1, 2, 3]
                    }
                },
                {
                    "graph_type": "Line Graph",
                    "filter": ["dummy.variable"],
                    "title": "Dummy Variable"
                }
        ),
        (
                {
                    "dummy.variable_1":
                        {
                            "values": [1, 2, 3]
                        },
                    "dummy.variable_2":
                        {
                            "values": [4, 5, 6]
                        }
                },
                {
                    "graph_type": "Line Graph",
                    "filter": ["dummy.variable*"],
                    "title": "Dummy Variable"
                }
        ),
    ]
)
def test_line_graph(mock_graph_generator: GraphGenerator,
                    graph_generator_original_states: dict[str, callable],
                    filtered_pool: dict,
                    graph_info: dict) -> None:
    mock_graph_generator._customize_graph = MagicMock()
    mock_fig = MagicMock(spec=matplotlib.figure.Figure)
    mock_ax = MagicMock(spec=matplotlib.axes.Axes)
    mock_plot = MagicMock()

    with patch.object(matplotlib.pyplot, "subplots", return_value=(mock_fig, mock_ax)) as mock_subplots:
        with patch.object(mock_ax, "plot", mock_plot):
            mock_graph_generator._line_graph(filtered_pool, graph_info)

    expected_plot_calls = []
    mock_subplots.assert_called_once()
    for key in filtered_pool.keys():
        expected_plot_calls.append(call(filtered_pool[key]['values']))
    assert (mock_plot.call_args_list == expected_plot_calls)

    mock_graph_generator._customize_graph.assert_called_once_with(mock_fig, graph_info)

    mock_graph_generator._customize_graph = graph_generator_original_states["_customize_graph"]


@pytest.mark.parametrize(
    "filtered_pool, graph_info",
    [
        (
                {"a": {"values": 1}, "b": {"values": 2}, "c": {"values": 3}},
                {"graph_type": "Bar Graph",
                 "filter": ["dummy.variable"],
                 "title": "Dummy Variable"}),
    ]
)
def test_bar_graph(mock_graph_generator: GraphGenerator,
                   graph_generator_original_states: dict[str, callable],
                   filtered_pool: dict,
                   graph_info: dict) -> None:
    mock_graph_generator._customize_graph = MagicMock()
    mock_fig = MagicMock(spec=matplotlib.figure.Figure)
    mock_ax = MagicMock(spec=matplotlib.axes.Axes)
    mock_bar = MagicMock()

    with patch.object(matplotlib.pyplot, "subplots", return_value=(mock_fig, mock_ax)) as mock_subplots:
        with patch.object(mock_ax, "bar", mock_bar):
            mock_graph_generator._bar_graph(filtered_pool, graph_info)

    mock_graph_generator._customize_graph.assert_called_once_with(mock_fig, graph_info)

    mock_subplots.assert_called_once()
    mock_bar.assert_called_once_with(["a", "b", "c"], [1, 2, 3])

    mock_graph_generator._customize_graph = graph_generator_original_states["_customize_graph"]


@pytest.mark.parametrize(
    "save_path, graph_info, filter_file_name",
    [
        (
                "dummy\\path",
                {
                    "graph_type": "Line Graph",
                    "filter": ["dummy.variable"],
                    "title": "Dummy Variable"
                },
                "dummy_filter"
        ),
        (
                "dummy\\path",
                {
                    "graph_type": "Line Graph",
                    "filter": ["dummy.variable"]
                },
                "dummy_filter"
        )
    ]
)
def test_generate_graph_path(mock_graph_generator: GraphGenerator,
                             graph_generator_original_states: dict[str, callable],
                             save_path: str,
                             graph_info: dict,
                             filter_file_name: str) -> None:
    mock_graph_generator._generate_graph_path = MagicMock()
    mock_mkdir = MagicMock()
    with freeze_time("2023-09-21"):
        with patch.object(Path, "mkdir", mock_mkdir):
            graph_path = RUFAS.graph_generator.GraphGenerator._generate_graph_path(mock_graph_generator, save_path,
                                                                                   graph_info, filter_file_name)

    graph_directory = os.path.join(save_path, "graphics", "om")
    timestamp = "21-Sep-2023_Thu_00-00-00"
    if 'title' in graph_info.keys():
        title = '-'.join(graph_info['title'].split()).lower()
        filename = title + '-' + timestamp + ".png"
    else:
        filename = f"saved_graph_{filter_file_name}-" + timestamp + ".png"
    expected_graph_path = os.path.join(graph_directory, filename)

    assert expected_graph_path == graph_path

    mock_graph_generator._generate_graph_path = graph_generator_original_states["_generate_graph_path"]


# @pytest.mark.parametrize(
#     "fig_ax, graph_info",
#     [
#         (
#                 plt.subplots(),
#                 {
#                     "graph_type": "Line Graph",
#                     "filter": ["dummy.variable"],
#                     "title": "Dummy Variable",
#                     "x_label": "Dummy x",
#                     "y_label": "Dummy y",
#                     "legend": "Dummy legend",
#                 }
#         ),
#         # (
#         #         matplotlib.figure.Figure(),
#         #         {
#         #             "graph_type": "Line Graph",
#         #             "filter": ["dummy.variable"],
#         #             "title": "Dummy Variable"
#         #         }
#         # )
#     ]
# )
# def test_customize_graph(mock_graph_generator: GraphGenerator,
#                          fig_ax: matplotlib.figure.Figure,
#                          graph_info: dict) -> None:
#     mock_graph_generator._customize_graph = MagicMock()
#
#     mock_fig = MagicMock(spec=matplotlib.figure.Figure)
#     mock_ax = MagicMock(spec=matplotlib.axes.Axes)
#     mock_set_title = MagicMock(spec=matplotlib.axes.Axes.set_title)
#     mock_set_xlabel = MagicMock()
#     mock_set_ylabel = MagicMock()
#     mock_legend = MagicMock()
#
#     # (fig, ax) = fig_ax
#     # ax.plot([1, 2, 3])
#     # print(fig.axes)
#
#     with patch.object(matplotlib.axes.Axes, "set_title", mock_set_title):
#         # print(fig.axes[0].set_title)
#         mock_graph_generator._customize_graph(mock_fig, graph_info)
#
#     # mock_set_title.assert_called_with(graph_info['title'])
#     mock_set_title.assert_called()
