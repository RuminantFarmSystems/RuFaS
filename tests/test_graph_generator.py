from typing import Dict
from unittest.mock import patch
import pytest
from RUFAS.graph_generator import GraphGenerator


@pytest.fixture
def graph_generator() -> GraphGenerator:
    return GraphGenerator()


def test_save_graph_successful(graph_generator):
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


# @patch("GraphGenerator.plt.savefig")
# def test_save_graph_exception(graph_generator, mock_savefig):
#     # Mock plt.savefig to raise an exception
#     mock_savefig.side_effect = Exception("Failed to save")

#     graph_details: Dict[str, str] = {
#         "title": "Test Graph",
#         "x_label": "X Axis",
#         "y_label": "Y Axis",
#     }
#     filter_file_name: str = "test_filter.png"
#     save_path: str = "/path/to/save"
#     graphics_dir: str = "graphics"

#     with pytest.raises(Exception, match="Failed to save"):
#         graph_generator._save_graph(
#             graph_details, filter_file_name, save_path, graphics_dir
#         )


# @pytest.fixture
# def graph_generator():
#     return GraphGenerator()


# @pytest.fixture
# def mock_plt(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr(plt, "subplots", mock)
#     return mock


# @pytest.fixture
# def mock_plt_savefig(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr(plt, "savefig", mock)
#     return mock


# def test_draw_graph(graph_generator, mock_plt):
#     graph_type = "plot"
#     data = {
#         "key1": {"values": [1, 2, 3]},
#         "key2": {"values": [4, 5, 6]},
#     }
#     graph_generator._draw_graph(graph_type, data)
#     mock_plt.plot.assert_called_once_with(data["key1"]["values"])
#     mock_plt.plot.assert_called_once_with(data["key2"]["values"])


# def test_customize_graph_figure_setters(graph_generator):
#     fig = MagicMock(name="Figure")
#     fig.set_dpi = MagicMock()
#     fig.set_size_inches = MagicMock()
#     fig.set_facecolor = MagicMock()

#     customization_details = {
#         "dpi": 150,
#         "figsize": (6, 4),
#         "facecolor": "white",
#     }

#     with patch("matplotlib.figure.Figure", return_value=fig):
#         graph_generator._customize_graph(fig, customization_details)

#     fig.set_dpi.assert_called_once_with(150)
#     fig.set_size_inches.assert_called_once_with(6, 4)
#     fig.set_facecolor.assert_called_once_with("white")


# def test_customize_graph_axes_setters(graph_generator, mock_plt):
#     fig = Figure()
#     fig.add_subplot(111)
#     customization_details = {
#         "xlabel": "X Label",
#         "ylabel": "Y Label",
#         "title": "Graph Title",
#     }
#     graph_generator._customize_graph(fig, customization_details)
#     mock_plt.set_xlabel.assert_called_once_with("X Label")
#     mock_plt.set_ylabel.assert_called_once_with("Y Label")
#     mock_plt.set_title.assert_called_once_with("Graph Title")


# def test_save_graph(graph_generator, mock_plt_savefig):
#     graph_details = {
#         "title": "My Graph",
#     }
#     filter_file_name = "filter_file"
#     save_path = "path/to/save"
#     graphics_dir = "graphs"
#     result = graph_generator._save_graph(
#         graph_details, filter_file_name, save_path, graphics_dir
#     )
#     timestamp = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")
#     expected_filename = (
#         f"{graph_details['title'].replace(' ', '-').lower()}-{timestamp}.png"
#     )
#     expected_path = os.path.join(save_path, graphics_dir, expected_filename)
#     mock_plt_savefig.assert_called_once_with(expected_path)
#     assert result == expected_path


# def test_generate_graph(graph_generator, mock_plt_savefig, mock_plt):
#     filtered_pool = {
#         "key1": {"values": [1, 2, 3]},
#         "key2": {"values": [4, 5, 6]},
#     }
#     graph_details = {
#         "type": "line",
#         "title": "My Graph",
#         "dpi": 150,
#         "figsize": (6, 4),
#     }
#     filter_file_name = "filter_file"
#     save_path = "path/to/save"
#     graphics_dir = "graphs"
#     result = graph_generator.generate_graph(
#         filtered_pool, graph_details, save_path, filter_file_name, graphics_dir
#     )
#     timestamp = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-M-%S")
#     expected_filename = (
#         f"{graph_details['title'].replace(' ', '-').lower()}-{timestamp}.png"
#     )
#     expected_path = os.path.join(save_path, graphics_dir, expected_filename)
#     mock_plt.set_dpi.assert_called_once_with(150)
#     mock_plt.set_size_inches.assert_called_once_with(6, 4)
#     mock_plt_savefig.assert_called_once_with(expected_path)
#     assert result == expected_path
