import copy
import datetime
import os
from pathlib import Path
from typing import Dict, List, Any, Callable, Tuple

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

    def __init__(self, metadata_prefix: str = "", time=None) -> None:
        self.metadata_prefix = metadata_prefix
        self.time = time

    def generate_graph(
        self,
        filtered_pool: Dict[str, Dict[str, List[Any]]],
        graph_details: Dict[str, str | List[str]],
        filter_file_name: str,
        graphics_dir: Path,
        produce_graphics: bool,
    ) -> List[Dict[str, str | Dict[str, str]]]:
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
        produce_graphics: bool
            Flag for whether or not the user wants to produce graphs at after the simulation.

        Returns
        -------
        log_pool : List[Dict[str, str | Dict[str, str]]]
            A list of log, warning, and error dictionaries containing all the components needed
            to log the information to the appropriate pool.

        Raises
        ------
        Exception
            Generic exception raised by utility functions.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.generate_graph.__name__,
        }
        if not produce_graphics:
            all_logs = [
                {
                    "error": f"Can't plot {graph_details.get('title')} data set",
                    "message": "'produce_graphics' set to False, no graphs will be produced.",
                    "info_map": info_map,
                }
            ]
            return all_logs
        try:
            graph_filter_validation_logs = self._validate_graph_filter(graph_details)
            prepared_data, log_pool = self._prepare_plot_data(filtered_pool, graph_details)
            all_logs = log_pool + graph_filter_validation_logs

            found_errors = any("error" in log for log in all_logs)
            if found_errors:
                return all_logs

            figure_width = 10
            figure_height = 6
            fig, ax = plt.subplots(figsize=(figure_width, figure_height))
            ratio_of_graph_to_legend = 0.65
            plt.subplots_adjust(right=ratio_of_graph_to_legend)
            self._draw_graph(graph_details, prepared_data)
            self._customize_graph(fig, ax, graph_details)
            self._save_graph(graph_details, filter_file_name, graphics_dir)
            matplotlib.pyplot.close()
            return all_logs
        except Exception as e:
            all_logs = {
                "error": f"Error plotting {graph_details.get('title')} data set",
                "message": f"Error: {e}",
                "info_map": info_map,
            }

        return all_logs

    def _validate_graph_filter(
        self, graph_details: Dict[str, str | List[str]]
    ) -> List[Dict[str, str | Dict[str, str]]]:
        """
        Ensures all the filter keys are valid and if not, raises an error and reports them back to Output Manager.
        Parameters
        ----------
        graph_details : Dict[str, str | List[str]]
            A dictionary containing details/metadata about the graph.
        Returns
        -------
        List[Dict[str, str | Dict[str, str]]]
            The logs, warnings, and errors to be reported to OutputManager.
        """
        required_graph_filter_keys = ["type", "filters"]
        optional_graph_filter_keys = (
            list(FIGURE_SETTERS.keys()) + list(AXES_SETTERS.keys()) + ["variables", "time_step_unit", "time_step_value"]
        )
        graph_filter_validation_logs: List[Dict[str, str | Dict[str, str]]] = []
        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_graph_filter.__name__,
        }
        for required_key in required_graph_filter_keys:
            if required_key not in graph_details.keys():
                graph_filter_validation_logs.append(
                    {
                        "error": f"Can't plot {graph_details.get('title')} data set",
                        "message": f"Required key '{required_key}' not in your graph " "filter file.",
                        "info_map": info_map,
                    }
                )
        if graph_filter_validation_logs:
            return graph_filter_validation_logs

        optional_graph_details_keys = [key for key in graph_details.keys() if key not in required_graph_filter_keys]
        for filter_key in optional_graph_details_keys:
            if filter_key not in optional_graph_filter_keys:
                graph_filter_validation_logs.append(
                    {
                        "warning": f"Can't plot data for {filter_key}",
                        "message": f"Invalid filter file key '{filter_key}' does not match"
                        "any optional keys. "
                        f"Please see Graph Generator wiki for a list of valid filter"
                        "keys.",
                        "info_map": info_map,
                    }
                )
        return graph_filter_validation_logs

    def _prepare_plot_data(  # noqa: C901
        self,
        filtered_pool: Dict[str, Dict[str, List[Any]]],
        graph_details: Dict[str, str | List[str]],
    ) -> Tuple[Dict[str, List[int | float]], List[Dict[str, str | Dict[str, str]]]]:
        """Extracts the values from the filtered_pool data and converts them a dictionary
        that graph_generator can more readily handle and records logs, warnings, and errors for
        Output Manager.

        Parameters
        ----------
        filtered_pool : Dict[str, pool_element_type]
            The filtered pool of variables that the user wants to graph.
        graph_details: Dict[str, str]
            A dictionary containing details/metadata about the graph.

        Returns
        -------
        Tuple[Dict[str, List[int | float]], List[Dict[str, str | Dict[str, str]]]]
            A tuple containing the formatted data that can more readily be plotted by
            graph_generator and the logs, warnings, and errors to be reported to OutputManager.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._prepare_plot_data.__name__,
        }
        selected_variables = graph_details.get("variables")
        title = graph_details.get("title")
        log_pool: List[Dict[str, str | Dict[str, str]]] = []
        prepared_pool: Dict[str, List[int | float]] = {}
        filter_by_exclusion = graph_details.get("filter_by_exclusion", False)
        for key in filtered_pool.keys():
            values: List[Any] = filtered_pool[key]["values"]
            info_maps = filtered_pool[key].get("info_maps", [])
            simulation_days = [info_map["simulation_day"] for info_map in info_maps if "simulation_day" in info_map]
            indices = list(range(len(values))) if not simulation_days else []

            is_data_in_dict = isinstance(values[0], dict)
            if is_data_in_dict:
                if not selected_variables:
                    log_pool.append(
                        {
                            "error": f"Can't plot {title} data set",
                            "message": f"No selected variables for {key}.",
                            "info_map": info_map,
                        }
                    )
                    continue
                data_dict = Utility.convert_list_of_dicts_to_dict_of_lists(values)
                filtered_data = Utility.filter_dictionary(data_dict, selected_variables, filter_by_exclusion)
                if not filtered_data:
                    log_pool.append(
                        {
                            "error": f"Can't plot {title} data set",
                            "message": "No variables found in data provided.",
                            "info_map": info_map,
                        }
                    )
                    continue
                non_int_float_keys = [
                    key
                    for key, value in filtered_data.items()
                    if not (
                        isinstance(value, (int, float))
                        or (isinstance(value, list) and all(isinstance(item, (int, float)) for item in value))
                    )
                ]
                for key in non_int_float_keys:
                    log_pool.append(
                        {
                            "error": f"Can't plot {title} data set",
                            "message": f"{key} key contains data that is non-numerical and can't be graphed.",
                            "info_map": info_map,
                        }
                    )
                else:
                    for filtered_key, filtered_value in filtered_data.items():
                        if filtered_key in prepared_pool:
                            prepared_pool[filtered_key].extend(filtered_value)
                            if simulation_days:
                                prepared_pool[f"{filtered_key}_simulation_days"].extend(simulation_days)
                            else:
                                prepared_pool[f"{filtered_key}_indices"].extend(indices)
                        else:
                            prepared_pool[filtered_key] = filtered_value
                            if simulation_days:
                                prepared_pool[f"{filtered_key}_simulation_days"] = copy.deepcopy(simulation_days)
                            else:
                                prepared_pool[f"{filtered_key}_indices"] = copy.deepcopy(indices)
            else:
                prepared_pool[key] = values
                if simulation_days:
                    prepared_pool[f"{key}_simulation_days"] = simulation_days
                else:
                    prepared_pool[f"{key}_indices"] = indices
                log_pool.append(
                    {
                        "log": f"Successfully added {title} data to prepared_pool",
                        "message": f"Data for {key} added.",
                        "info_map": info_map,
                    }
                )

        return prepared_pool, log_pool

    def _draw_graph(
        self,
        graph_details: Dict[str, str | List[str]],
        data: Dict[str, List[int | float]],
    ) -> None:
        """
        Draw the graph based on the provided graph type and data.

        Parameters
        ----------
        graph_details : Dict[str, str | List[str]]
            A dictionary containing details/metadata about the graph.
        data : Dict[str, List[int | float]]
            The data to use for plotting.

        Raises
        ------
        ValueError
            if there is no data to plot or if the graph_type is not found in MATPLOTLIB_PLOT_FUNCTIONS.
        """
        if not data:
            raise ValueError("No data to plot.")
        graph_type = graph_details["type"]
        if graph_type not in MATPLOTLIB_PLOT_FUNCTIONS:
            raise ValueError(f"Unsupported graph type: {graph_type}")
        if any([variable.endswith("_indices") for variable in data.keys()]) and (
            "time_step_unit" in graph_details or "time_step_value" in graph_details
        ):
            raise ValueError(
                "Because there is no information about simulation days in info maps, "
                "'time_step_unit' and 'time_step_value' are not supported."
            )

        plot_function = MATPLOTLIB_PLOT_FUNCTIONS[graph_type]
        if graph_type in TUPLE_BASED_FUNCTIONS:
            plotted_variables = [
                variable
                for variable in data.keys()
                if not variable.endswith("_simulation_days") and not variable.endswith("_indices")
            ]
            values_tuple = tuple(data[variable] for variable in plotted_variables)
            indices_list = list(range(len(values_tuple[0])))
            plot_function(indices_list, values_tuple)
        else:
            plotted_variables = []
            for key, value in data.items():
                if not key.endswith("_simulation_days") and not key.endswith("_indices"):
                    xaxis_data = (
                        data[f"{key}_simulation_days"] if f"{key}_simulation_days" in data else data[f"{key}_indices"]
                    )
                    if f"{key}_simulation_days" in data and self.time.add_formatted_time:
                        xaxis_data = [self.time.convert_simulation_day_to_date(sim_day) for sim_day in xaxis_data]
                    plot_function(xaxis_data, value)
                    plotted_variables.append(key)
        if "legend" not in graph_details:
            graph_details["legend"] = plotted_variables

    def _customize_graph(self, fig: Figure, ax: Axes, customization_details: Dict[str, Any]) -> None:
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
            elif attrib == "legend":
                legend_location = "upper left"
                placement_of_legend = (1, 1)
                AXES_SETTERS[attrib](fig.axes[0], value, loc=legend_location, bbox_to_anchor=placement_of_legend)
            elif attrib in AXES_SETTERS.keys():
                AXES_SETTERS[attrib](fig.axes[0], value)
            elif attrib == "time_step_unit":
                self._set_time_axis(
                    ax, customization_details.get("time_step_unit"), customization_details.get("time_step_value")
                )

    def _set_time_axis(self, ax: Axes, time_step_unit: str | None, time_step_value: int | None) -> None:
        """
        Set the time axis for the graph.

        Parameters
        ----------
        ax : Axes
            The matplotlib Axes object to customize.
        time_step_unit : str | None
            The time locator to use for the x-axis.
        time_step_value : int | None
            The time interval to use for the x-axis.
        """

        if not self.time.add_formatted_time or not self.time.time_format:
            return

        valid_time_step_units = ["month", "day", "year"]
        if time_step_unit not in valid_time_step_units:
            raise ValueError(
                f"Unsupported time step unit: {time_step_unit}. "
                f"Supported values are: {', '.join(valid_time_step_units)}"
            )

        if time_step_unit == "year" and time_step_value not in [None, 1]:
            raise ValueError(
                "When using 'year' as the time step unit, it is not required to provide a time step value. "
                "Default value is 1. For more granular control, please use 'month' or 'day' as the time step unit."
            )

        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(self.time.time_format))

        locator = None
        if time_step_unit == "month":
            locator = (
                matplotlib.dates.MonthLocator()
                if time_step_value is None
                else matplotlib.dates.MonthLocator(interval=time_step_value)
            )
        elif time_step_unit == "day":
            locator = (
                matplotlib.dates.DayLocator()
                if time_step_value is None
                else matplotlib.dates.DayLocator(interval=time_step_value)
            )
        elif time_step_unit == "year":
            locator = matplotlib.dates.YearLocator()

        if locator:
            ax.xaxis.set_major_locator(locator)

    def _save_graph(
        self,
        graph_details: Dict[str, str | List[str]],
        filter_file_name: str,
        graphics_dir: Path,
    ) -> str:
        """
        Save the generated graph to a file.

        Parameters
        ----------
        graph_details : Dict[str, str | List[str]]
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
        graph_path = self._generate_graph_path(graph_details, filter_file_name, graphics_dir)
        counter = 1
        while graph_path.exists():
            graph_path = graph_path.with_name(f"{graph_path.stem}({counter}){graph_path.suffix}")
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
