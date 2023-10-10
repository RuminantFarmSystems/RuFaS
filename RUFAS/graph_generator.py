import os
import datetime
from pathlib import Path
from typing import Dict, List, Any

import matplotlib
import matplotlib.pyplot as pyplt
from matplotlib.figure import Axes, Figure

"""
Agg rendering to a Tk canvas (requires TkInter). This backend can be activated in IPython with %matplotlib tk.
Ref: https://matplotlib.org/stable/users/explain/figure/backends.html
"""
matplotlib.use("TkAgg")

MATPLOTLIB_PLOT_FUNCTIONS = {
    "3d_contour": pyplt.contour,
    "3d_heatmap": pyplt.imshow,
    "3d_line": pyplt.plot,
    "3d_scatter": pyplt.scatter,
    "3dhistogram": pyplt.hist,
    "area": pyplt.fill_between,
    "bar": pyplt.bar,
    "barbs": pyplt.barbs,
    "boxplot": pyplt.boxplot,
    "broken_barh": pyplt.broken_barh,
    "contour": pyplt.contour,
    "filled_barh": pyplt.broken_barh,
    "filled_contour": pyplt.contourf,
    "hexbin": pyplt.hexbin,
    "hexbin_plot": pyplt.hexbin,
    "hist2d": pyplt.hist2d,
    "histogram": pyplt.hist,
    "horizontal_bar": pyplt.barh,
    "horizontal_line": pyplt.axhline,
    "horizontal_lines": pyplt.hlines,
    "image": pyplt.imshow,
    "imshow": pyplt.imshow,
    "line": pyplt.plot,
    "pcolor": pyplt.pcolor,
    "pcolormesh": pyplt.pcolormesh,
    "pie": pyplt.pie,
    "polar": pyplt.polar,
    "quiver": pyplt.quiver,
    "quiver_key": pyplt.quiverkey,
    "scatter": pyplt.scatter,
    "spy": pyplt.spy,
    "stacked_area": pyplt.stackplot,
    "step": pyplt.step,
    "stepfilled": pyplt.step,
    "stem": pyplt.stem,
    "stream_plot": pyplt.streamplot,
    "streamplot": pyplt.streamplot,
    "tripcolor": pyplt.tripcolor,
    "vertical_line": pyplt.axvline,
    "vertical_lines": pyplt.vlines,
    "violin": pyplt.violinplot,
}

FIGURE_SETTERS = {
    "align_labels": Figure.align_labels,
    "canvas": Figure.set_canvas,
    "constrained_layout": Figure.set_constrained_layout,
    "dpi": Figure.set_dpi,
    "edgecolor": Figure.set_edgecolor,
    "figdpi": Figure.set_dpi,
    "figheight": Figure.set_figheight,
    "figsize": Figure.set_size_inches,
    "figwidth": Figure.set_figwidth,
    "facecolor": Figure.set_facecolor,
    "frameon": Figure.set_frameon,
    "snap": Figure.set_snap,
    "subplot_adjust": Figure.subplots_adjust,
    "tight_layout": Figure.set_tight_layout,
    "zorder": Figure.set_zorder,
}

AXES_SETTERS = {
    "aspect": Axes.set_aspect,
    "grid": Axes.grid,
    "legend": Axes.legend,
    "transform": Axes.set_transform,
    "xlabel": Axes.set_xlabel,
    "xticklabels": Axes.set_xticklabels,
    "xticks": Axes.set_xticks,
    "xlim": Axes.set_xlim,
    "ylabel": Axes.set_ylabel,
    "yticklabels": Axes.set_yticklabels,
    "yticks": Axes.set_yticks,
    "ylim": Axes.set_ylim,
    "yscale": Axes.set_yscale,
    "xscale": Axes.set_xscale,
    "title": Axes.set_title,
}


class GraphGenerator:
    """
    Graph Generator is used to generate graphs from the simulation results.
    NOTE: This class is not multi-thread safe!!!
    """

    def generate_graph(
        self,
        filtered_pool: Dict[str, Dict[str, List[Dict[str, Any]]]],
        graph_details: Dict[str, str],
        save_path: str,
        filter_file_name: str,
    ):
        """
        Function to generate graph. This function will route the input to the correct function according to the type
        of graph.

        Parameters
        ----------
        filtered_pool : Dict[str, Dict[str, List[Dict[str, Any]]]]
            The result pool after filtering with the provided RegEx filters
        graph_details: Dict[str, str]
            A dictionary containing details/metadata about the graph
        save_path: str
            The base folder path to save the output
        filter_file_name: str
            The name of the filter file


        Raises
        ------
            Generic Exception raised by utility functions

        Returns
        -------
        str
            The path to the saved graph

        """
        try:
            fig, _ = pyplt.subplots()
            self._draw_graph(graph_details["type"], filtered_pool)
            self._customize_graph(fig, graph_details)
            return self._save_graph(graph_details, filter_file_name, save_path)
        except Exception as e:
            raise e

    def _draw_graph(
        self,
        graph_type: str,
        data: Dict[str, Dict[str, List[Dict[str, Any]]]],
    ):
        for key in data.keys():
            plot_function = MATPLOTLIB_PLOT_FUNCTIONS[graph_type]
            plot_function(data[key]["values"])

    def _customize_graph(self, fig: Figure, customization_details: Dict[str, Any]):
        """
        Function to apply customizations to the graph.
        """
        for attrib, value in customization_details.items():
            if attrib in FIGURE_SETTERS.keys():
                FIGURE_SETTERS[attrib](fig, value)
            elif attrib in AXES_SETTERS.keys():
                AXES_SETTERS[attrib](fig.axes[0], value)

    def _save_graph(
        self,
        graph_details: Dict[str, str],
        filter_file_name: str,
        save_path: str,
    ) -> str:
        graph_path = self._generate_graph_path(
            save_path, graph_details, filter_file_name
        )
        try:
            pyplt.savefig(graph_path)
            return graph_path
        except Exception as e:
            raise e

    def _generate_graph_path(
        self, save_path: str, graph_details: Dict[str, str], filter_file_name: str
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

        if "title" in graph_details.keys():
            title = "-".join(graph_details["title"].split()).lower()
            filename = f"{title}-{timestamp}.png"
        else:
            filename = f"saved_graph_{filter_file_name}-{timestamp}.png"

        graph_path = os.path.join(graph_directory, filename)
        return graph_path
