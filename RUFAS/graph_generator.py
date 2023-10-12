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
    "area": pyplt.fill_between,
    "bar": pyplt.bar,
    "barbs": pyplt.barbs,
    "boxplot": pyplt.boxplot,
    "broken_barh": pyplt.broken_barh,
    "contour": pyplt.contour,
    "filled_contour": pyplt.contourf,
    "hexbin": pyplt.hexbin,
    "hist2d": pyplt.hist2d,
    "histogram": pyplt.hist,
    "horizontal_bar": pyplt.barh,
    "horizontal_line": pyplt.axhline,
    "horizontal_lines": pyplt.hlines,
    "imshow": pyplt.imshow,
    "pcolor": pyplt.pcolor,
    "pcolormesh": pyplt.pcolormesh,
    "pie": pyplt.pie,
    "plot": pyplt.plot,
    "polar": pyplt.polar,
    "quiver": pyplt.quiver,
    "quiver_key": pyplt.quiverkey,
    "scatter": pyplt.scatter,
    "spy": pyplt.spy,
    "stacked_area": pyplt.stackplot,
    "step": pyplt.step,
    "stem": pyplt.stem,
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
        graphics_dir: str = "",
    ):
        """
        Generate a graph based on filtered data and graph details.

        Parameters
        ----------
        filtered_pool : Dict[str, Dict[str, List[Dict[str, Any]]]]
            The result pool after filtering with the provided RegEx filters.
        graph_details: Dict[str, str]
            A dictionary containing details/metadata about the graph.
        save_path: str
            The base folder path to save the output.
        filter_file_name: str
            The name of the filter file.
        graphics_dir : str, optional
            The directory for saving graphics, by default an empty string.

        Returns
        -------
        str
            The path to the saved graph.

        Raises
        ------
        Exception
            Generic exception raised by utility functions.
        """
        try:
            fig, _ = pyplt.subplots()
            self._draw_graph(graph_details["type"], filtered_pool)
            self._customize_graph(fig, graph_details)
            return self._save_graph(
                graph_details, filter_file_name, save_path, graphics_dir
            )
        except Exception as e:
            raise e

    def _draw_graph(
        self,
        graph_type: str,
        data: Dict[str, Dict[str, List[Dict[str, Any]]]],
    ) -> None:
        """
        Draw the graph based on the provided graph type and data.

        Parameters
        ----------
        graph_type : str
            The type of graph to draw.
        data : Dict[str, Dict[str, List[Dict[str, Any]]]]
            The data to use for plotting.

        """
        for key in data.keys():
            plot_function = MATPLOTLIB_PLOT_FUNCTIONS[graph_type]
            plot_function(data[key]["values"])

    def _customize_graph(
        self, fig: Figure, customization_details: Dict[str, Any]
    ) -> None:
        """
        Apply customizations to the graph.

        Parameters
        ----------
        fig : Figure
            The matplotlib Figure object to customize.
        customization_details : Dict[str, Any]
            A dictionary of customization details.

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
        graphics_dir: str = "",
    ) -> str:
        """
        Save the generated graph to a file.

        Parameters
        ----------
        graph_details : Dict[str, str]
            A dictionary containing details/metadata about the graph.
        filter_file_name : str
            The name of the filter file.
        save_path : str
            The base folder path to save the output.
        graphics_dir : str, optional
            The directory for saving graphics, by default an empty string.

        Returns
        -------
        str
            The path to the saved graph.

        Raises
        ------
        Exception
            Generic exception raised if saving the graph fails.

        """
        graph_path = self._generate_graph_path(
            save_path, graph_details, filter_file_name, graphics_dir
        )
        try:
            pyplt.savefig(graph_path)
            return graph_path
        except Exception as e:
            raise e

    def _generate_graph_path(
        self,
        save_path: str,
        graph_details: Dict[str, str],
        filter_file_name: str,
        graphics_dir: str = "",
    ) -> str:
        """
        Generate the full path for the output graph and create parent folders if necessary.

        Parameters
        ----------
        save_path : str
            The base folder path to save the output.
        graph_details : Dict[str, str]
            A dictionary containing details/metadata about the graph.
        filter_file_name : str
            The name of the filter file.
        graphics_dir : str, optional
            The directory for saving graphics, by default an empty string.

        Returns
        -------
        str
            The full path to the output graph file.

        Raises
        ------
        Exception
            Generic exception raised if directory creation fails.

        """
        graph_directory = os.path.join(save_path, graphics_dir)
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
