import os
import datetime
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Axes, Figure
from RUFAS.util import Utility

"""
Agg rendering to a Tk canvas (requires TkInter). This backend can be activated in IPython with %matplotlib tk.
Ref: https://matplotlib.org/stable/users/explain/figure/backends.html
"""
if "DISPLAY" not in os.environ:
    # If running in a headless environment, use the 'Agg' backend
    matplotlib.use("Agg")
else:
    # Use the 'TkAgg' backend when a display is available
    matplotlib.use("TkAgg")

FUNCTION_TYPE = Callable[..., None]

MATPLOTLIB_PLOT_FUNCTIONS: Dict[str, FUNCTION_TYPE] = {
    "area": plt.fill_between,
    "bar": plt.bar,
    "barbs": plt.barbs,
    "boxplot": plt.boxplot,
    "broken_barh": plt.broken_barh,
    "contour": plt.contour,
    "filled_contour": plt.contourf,
    "hexbin": plt.hexbin,
    "hist2d": plt.hist2d,
    "histogram": plt.hist,
    "horizontal_bar": plt.barh,
    "horizontal_line": plt.axhline,
    "horizontal_lines": plt.hlines,
    "imshow": plt.imshow,
    "pcolor": plt.pcolor,
    "pcolormesh": plt.pcolormesh,
    "pie": plt.pie,
    "plot": plt.plot,
    "polar": plt.polar,
    "quiver": plt.quiver,
    "quiver_key": plt.quiverkey,
    "scatter": plt.scatter,
    "spy": plt.spy,
    "stackplot": plt.stackplot,
    "step": plt.step,
    "stem": plt.stem,
    "streamplot": plt.streamplot,
    "tripcolor": plt.tripcolor,
    "vertical_line": plt.axvline,
    "vertical_lines": plt.vlines,
    "violin": plt.violinplot,
}

# Matplotlib has two types of functions: those who accept consecutive calls, and those who expect a single call with
# a tuple being passes. In the first type, to plot d1 and d2, you'd need to make 2 calls: func(d1), func(d2), however,
# in the second type, a single call like func(d1, d2) is expected. The list below contains the list of the latter.
TUPLE_BASED_FUNCTIONS: List[str] = ["stackplot"]

FIGURE_SETTERS: Dict[str, FUNCTION_TYPE] = {
    "align_labels": Figure.align_labels,
    "canvas": Figure.set_canvas,
    "constrained_layout": Figure.set_constrained_layout,
    "dpi": Figure.set_dpi,
    "edgecolor": Figure.set_edgecolor,
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

AXES_SETTERS: Dict[str, FUNCTION_TYPE] = {
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

    def __init__(self, metadata_prefix: str = "") -> None:
        self.metadata_prefix = metadata_prefix

    def generate_graph(
        self,
        filtered_pool: Dict[str, Dict[str, List[Any]]],
        graph_details: Dict[str, str | List[str]],
        filter_file_name: str,
        graphics_dir: Path,
    ) -> str:
        """
        Generate a graph based on filtered data and graph details.

        Parameters
        ----------
        filtered_pool : Dict[str, Dict[str, List[Any]]]
            The result pool after filtering with the provided RegEx filters.
        graph_details: Dict[str, str]
            A dictionary containing details/metadata about the graph.
        save_path: Path
            The base folder path to save the output.
        filter_file_name: str
            The name of the filter file.
        graphics_dir : Path
            The directory for saving graphics.

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
            fig, _ = plt.subplots()
            filtered_pool = {k: filtered_pool[k] for k in graph_details["filters"]
                             if k in filtered_pool.keys()}
            self._draw_graph(
                graph_details["type"], filtered_pool, graph_details.get("variables")
            )
            self._customize_graph(fig, graph_details)
            return self._save_graph(
                graph_details, filter_file_name, graphics_dir
            )
        except Exception as e:
            raise e

    def _draw_graph(
        self,
        graph_type: str,
        data: Dict[str, Dict[str, List[Any]] | Dict[str, List[Dict[str, List[Any]]]]],
        selected_variables: Optional[List[str]] = None,
    ) -> None:
        """
        Draw the graph based on the provided graph type and data.

        Parameters
        ----------
        graph_type : str
            The type of graph to draw.
        data : Dict[str, Dict[str, List[Any]] | Dict[str, List[Dict[str, List[Any]]]]]
            The data to use for plotting.
        selected_variables : Optional[List[str]]
            If it is present and the data is a list of dicts,
            it selects the variables to be plotted.

        Raises
        ------
        ValueError
            if graph_type is not found in MATPLOTLIB_PLOT_FUNCTIONS
        TypeError
            if data is Dict[str, List[Dict[str, List[Any]]]]] and selected_variables is None
        """
        if graph_type not in MATPLOTLIB_PLOT_FUNCTIONS:
            raise ValueError(f"Unsupported graph type: {graph_type}")

        plot_function = MATPLOTLIB_PLOT_FUNCTIONS[graph_type]
        for key in data.keys():
            values: List[Any] = data[key]["values"]
            is_data_in_dict = isinstance(values[0], dict)

            if is_data_in_dict:
                if selected_variables is None:
                    raise TypeError(
                        "Can't plot dictionary, use 'variables' arg to select items from data"
                    )
                data_dict = Utility.convert_list_of_dicts_to_dict_of_lists(values)
                if graph_type in TUPLE_BASED_FUNCTIONS:
                    self._handle_tuple_based_plot(
                        data_dict, selected_variables, plot_function
                    )
                else:
                    for variable in selected_variables:
                        plot_function(data_dict[variable])
            else:
                plot_function(values)

    def _handle_tuple_based_plot(
        self,
        data_dict: Dict[str, List[float | int]],
        selected_variables: List[str],
        plot_function: FUNCTION_TYPE,
    ) -> None:
        """
        Plot selected variables from data organized as a tuple.

        Parameters
        ----------
        data_dict : Dict[str, List[float | int]]
            Dictionary of variable data.
        selected_variables : List[str]
            List of variables to plot.
        plot_function : Callable[..., None]
            Matplotlib function for plotting.

        Returns: None
        """
        values_tuple = tuple(data_dict[variable] for variable in selected_variables)
        plot_function(list(range(len(values_tuple[0]))), values_tuple)

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
        graphics_dir: Path,
    ) -> str:
        """
        Save the generated graph to a file.

        Parameters
        ----------
        graph_details : Dict[str, str]
            A dictionary containing details/metadata about the graph.
        filter_file_name : str
            The name of the filter file.
        save_path : Path
            The base folder path to save the output.
        graphics_dir : Path
            The directory for saving graphics.

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
            graph_details, filter_file_name, graphics_dir
        )
        counter = 1
        while graph_path.exists():
            graph_path = graph_path.with_name(
                f"{graph_path.stem}({counter}){graph_path.suffix}"
            )
            counter += 1
        try:
            plt.savefig(graph_path)
            return graph_path
        except Exception:
            raise

    def _generate_graph_path(
        self,
        graph_details: Dict[str, str],
        filter_file_name: str,
        graphics_dir: Path,
    ) -> Path:
        """
        Generate the full path for the output graph and create parent folders if necessary.

        Parameters
        ----------
        graph_details : Dict[str, str]
            A dictionary containing details/metadata about the graph.
        filter_file_name : str
            The name of the filter file.
        graphics_dir : Path
            The directory for saving graphics.

        Returns
        -------
        Path
            The full path to the output graph file.

        """
        timestamp: str = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")

        if "title" in graph_details.keys():
            title = "-".join(graph_details["title"].split()).lower()
            filename = f"{self.metadata_prefix}_{title}-{timestamp}.png"
        else:
            filename = f"{self.metadata_prefix}_{filter_file_name}-{timestamp}.png"

        graph_path = os.path.join(graphics_dir, filename)
        return Path(graph_path)
