import os
import datetime
from pathlib import Path
from typing import Dict, List, Any

import matplotlib
import matplotlib.pyplot as pyplt
from matplotlib.figure import Figure

"""
Agg rendering to a Tk canvas (requires TkInter). This backend can be activated in IPython with %matplotlib tk.
Ref: https://matplotlib.org/stable/users/explain/figure/backends.html
"""
matplotlib.use("TkAgg")

om_pool_element_type = Dict[str, List[Dict[str, Any]]]


class GraphGenerator:
    """
    Graph Generator is used to generate graphs from the simulation results.
    NOTE: This class is not multi-thread safe!!!
    """

    def generate_graph(
        self,
        filtered_pool: Dict[str, om_pool_element_type],
        graph_info: Dict[str, str],
        save_path: str,
        filter_file_name: str,
        **kwargs,
    ):
        """
        Function to generate graph. This function will route the input to the correct function according to the type
        of graph.

        Parameters
        ----------
        filtered_pool : Dict[str, om_pool_element_type]
            The result pool after filtering with the provided RegEx filters
        graph_info: Dict[str, str]
            A dictionary containing details/metadata about the graph
        save_path: str
            The base folder path to save the output
        filter_file_name: str
            The name of the filter file
        """

        graph_type_funcs = {
            "Line Graph": self._line_graph,
            "Bar Graph": self._bar_graph,
        }
        graph_type_funcs[graph_info["graph_type"]](filtered_pool, graph_info)

        graph_path = self._generate_graph_path(save_path, graph_info, filter_file_name)
        try:
            pyplt.savefig(graph_path)
        except Exception as e:
            raise e

    def _customize_graph(self, fig: Figure, graph_info: dict, **kwargs):
        """
        Function to apply customizations to the graph.
        """
        if "title" in graph_info.keys():
            fig.axes[0].set_title(graph_info["title"])
        if "x_label" in graph_info.keys():
            fig.axes[0].set_xlabel(graph_info["x_label"])
        if "y_label" in graph_info.keys():
            fig.axes[0].set_xlabel(graph_info["y_label"])
        if "legend" in graph_info.keys():
            fig.axes[0].legend(graph_info["legend"])

    def _generate_graph_path(
        self, save_path: str, graph_info: dict, filter_file_name: str
    ) -> str:
        """
        Function to generate the full path for the output graph, and create all the parenting folders.
        """
        graph_directory = os.path.join(save_path, "graphics", "om")
        try:
            Path(graph_directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise e

        timestamp: str = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")

        if "title" in graph_info.keys():
            title = "-".join(graph_info["title"].split()).lower()
            filename = title + "-" + timestamp + ".png"
        else:
            filename = f"saved_graph_{filter_file_name}-" + timestamp + ".png"

        graph_path = os.path.join(graph_directory, filename)
        return graph_path

    def _line_graph(self, filtered_pool: dict, graph_info: dict, **kwargs) -> Figure:
        """
        Function to generate a line graph.
        """
        fig, ax = pyplt.subplots()
        for key in filtered_pool.keys():
            ax.plot(filtered_pool[key]["values"])
        self._customize_graph(fig, graph_info)
        return fig

    def _bar_graph(self, filtered_pool: dict, graph_info: dict, **kwargs) -> Figure:
        """
        Function to generate a bar graph.
        """
        fig, ax = pyplt.subplots()
        category, count = [], []

        for key in filtered_pool.keys():
            category.append(key)
            count.append(filtered_pool[key]["values"])

        ax.bar(category, count)
        self._customize_graph(fig, graph_info)
        return fig
