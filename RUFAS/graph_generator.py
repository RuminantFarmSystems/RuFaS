import datetime
import os
import re
from pathlib import Path
from typing import Any, Callable

import matplotlib
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.figure import Figure

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

FUNCTION_TYPE = Callable[..., Any]

MATPLOTLIB_PLOT_FUNCTIONS: dict[str, FUNCTION_TYPE] = {
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
TUPLE_BASED_FUNCTIONS: list[str] = ["stackplot", "scatter", "barbs", "hexbin", "quiver", "spy"]

# Unsupported Matplotlib functions don't work in our current setup of Graph Generator either as consecutive call
# functions or TUPLE_BASED_FUNCTIONS. There are multiple reasons for each function not working documented here:
# https://docs.google.com/spreadsheets/d/10fPdoS5YejYPidYvAmEBkMNq0X9nMqYdta-qduOk42s/edit#gid=0
UNSUPPORTED_GRAPH_FUNCTIONS: list[str] = [
    "area",
    "bar",
    "broken_barh",
    "contour",
    "filled-contour",
    "hist2d",
    "horizontal_bar",
    "horizontal_line",
    "horizontal_lines",
    "imshow",
    "pcolor",
    "pcolormesh",
    "quiver_key",
    "step",
    "streamplot",
    "tripcolor",
    "vertical_line",
    "vertical_lines",
]

FIGURE_SETTERS: dict[str, FUNCTION_TYPE] = {
    "align_labels": Figure.align_labels,
    "canvas": Figure.set_canvas,
    "dpi": Figure.set_dpi,
    "edgecolor": Figure.set_edgecolor,
    "figheight": Figure.set_figheight,
    "figsize": Figure.set_size_inches,
    "figwidth": Figure.set_figwidth,
    "facecolor": Figure.set_facecolor,
    "frameon": Figure.set_frameon,
    "snap": Figure.set_snap,
    "subplot_adjust": Figure.subplots_adjust,
    "zorder": Figure.set_zorder,
}

AXES_SETTERS: dict[str, FUNCTION_TYPE] = {
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

    Attributes
    ----------
    metadata_prefix : str
        A string to prefix the metadata of the graph.
    time : RufasTime
        A RufasTime object used to track the simulation time
    """

    def __init__(self, metadata_prefix: str = "", time=None) -> None:
        self.metadata_prefix = metadata_prefix
        self.time = time

    def generate_graph(
        self,
        filtered_pool: dict[str, dict[str, list[Any]]],
        graph_details: dict[str, Any],
        filter_file_name: str,
        graphics_dir: Path,
        produce_graphics: bool,
    ) -> list[dict[str, str | dict[str, str]]] | list[dict[str, str | dict[str, str]]]:
        """
        Generate a graph based on filtered data and graph details.

        Parameters
        ----------
        filtered_pool : dict[str, dict[str, list[Any]]]
            The result pool after filtering with the provided RegEx filters.
        graph_details: dict[str, str]
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
        log_pool : list[dict[str, str | dict[str, str]]] | list[dict[str, str | dict[str, str]]]
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
            all_logs: list[dict[str, str | dict[str, str]]] = [
                {
                    "error": f"Can't plot {graph_details.get('title')} data set",
                    "message": "'produce_graphics' set to False, no graphs will be produced.",
                    "info_map": info_map,
                }
            ]
            return all_logs
        if graph_details.get("type") in UNSUPPORTED_GRAPH_FUNCTIONS:
            all_logs = [
                {
                    "error": f"Can't plot {graph_details.get('title')} data set",
                    "message": f"Graph type '{graph_details.get('type')}' not supported at this time.",
                    "info_map": info_map,
                }
            ]
            return all_logs
        try:
            var_units_logs: list[dict[str, str | dict[str, str]]] = []
            updated_pool = filtered_pool
            if graph_details.get("display_units", True) or graph_details.get("is_aggregated_report_data", False):
                updated_pool, var_units_logs = self._add_var_units(
                    filtered_pool, graph_details.get("title", "Untitled graph")
                )
                graph_details["variables"] = list(updated_pool.keys())
            prepared_data: dict[str, list[Any]] = {key: updated_pool[key]["values"] for key in updated_pool.keys()}
            non_numeric_data_logs = self._log_non_numerical_data(updated_pool, graph_details)
            all_logs = non_numeric_data_logs + var_units_logs

            found_errors = any("error" in log for log in all_logs)
            if found_errors:
                return all_logs

            figure_width = 10
            figure_height = 6
            fig, ax = plt.subplots(figsize=(figure_width, figure_height))
            ratio_of_graph_to_legend = 0.65
            plt.subplots_adjust(right=ratio_of_graph_to_legend)

            mask_values = graph_details.get("mask_values", False)
            use_calendar_dates = graph_details.get("use_calendar_dates", False)
            date_format = graph_details.get("date_format", None)
            if graph_details.get("title"):
                corrected_graph_title = Utility.remove_special_chars(graph_details.get("title", "Untitled graph"))
                graph_details["title"] = corrected_graph_title
            log_message = f"Variable mapping for {graph_details.get("title")}: {{'Legend Key': 'Original Var Name'}}"
            if graph_details.get("legend", False):
                legend_mapping = {
                    k: self._generate_legend_keys(k, omit_legend_prefix=True, omit_legend_suffix=False)
                    for k in prepared_data.keys()
                }
                sorted_keys = sorted(legend_mapping.keys(), key=lambda k: legend_mapping[k])
                all_logs.append(
                    {
                        "log": log_message,
                        "message": str({legend_mapping[k]: k for k in sorted_keys}),
                        "info_map": info_map,
                    }
                )
                prepared_data = {key: prepared_data[key] for key in sorted_keys}
            else:
                all_logs.append(
                    {
                        "log": log_message,
                        "message": str({key: key for key in prepared_data.keys()}),
                        "info_map": info_map,
                    }
                )
                graph_details = self._set_graph_legend(graph_details, prepared_data)
            self._draw_graph(
                graph_details["type"],
                prepared_data,
                list(prepared_data.keys()),
                ax,
                mask_values,
                use_calendar_dates,
                date_format,
                graph_details.get("slice_start", None),
                graph_details.get("slice_end", None),
            )

            self._customize_graph(fig, graph_details)
            self._save_graph(graph_details, filter_file_name, graphics_dir)
            matplotlib.pyplot.close()
            return all_logs
        except Exception as e:
            all_logs = [
                {
                    "error": f"Error plotting '{graph_details.get('title')}' data set",
                    "message": f"Unforeseen error {e} when trying to graph data.",
                    "info_map": info_map,
                }
            ]

        return all_logs

    def _set_graph_legend(
        self,
        graph_details: dict[str, str | list[str]],
        prepared_data: dict[str, list[Any]],
    ) -> dict[str, str | list[str]]:
        """Sets the graph legend if there is no legend present in the graph details.

        Parameters
        ----------
        graph_details : dict[str, str]
            A dictionary containing details/metadata about the graph.
        prepared_data: dict[str, list[Any]]
            The data to be graphed that's been prepared for graphing.

        Returns
        -------
        dict[str, str]
            A dictionary containing details/metadata about the graph with the legend field populated.
        """
        omit_legend_prefix = graph_details.get("omit_legend_prefix", False)
        omit_legend_suffix = graph_details.get("omit_legend_suffix", False)

        if omit_legend_prefix or omit_legend_suffix:
            graph_details["legend"] = list(
                self._generate_legend_keys(key, omit_legend_prefix, omit_legend_suffix) for key in prepared_data.keys()
            )
        elif selected_variables := graph_details.get("variables"):
            graph_details["legend"] = selected_variables
        else:
            graph_details["legend"] = list(prepared_data.keys())

        return graph_details

    def _add_var_units(
        self,
        filtered_pool: dict[str, dict[str, list[Any]]],
        graph_title: str | list[str],
    ) -> tuple[dict[str, dict[str, list[Any]]], list[dict[str, str | dict[str, str]]]]:
        """Adds variable units to variable name for graphing.

        Parameters
        ----------
        filtered_pool : dict[str, list[Any]]
            The data to be graphed.

        Returns
        -------
        list[dict[str, list[Any]], list[dict[str, str | dict[str, str]]]]
            The updated data with units added and logs if info_maps aren't found to get units.
        """
        updated_data = {}
        info_map = {
            "class": self.__class__.__name__,
            "function": self._add_var_units.__name__,
        }
        logs: list[dict[str, str | dict[str, str]]] = []
        if not any("info_maps" in details for details in filtered_pool.values()):
            logs.append(
                {
                    "warning": f"Can't add units to variables for graphing {graph_title}",
                    "message": "'info_maps' unavailable to get units, check setting for exclude_info_maps.",
                    "info_map": info_map,
                }
            )
            return filtered_pool, logs
        for var_name, details in filtered_pool.items():
            unit_info = details["info_maps"][0]["units"]
            if isinstance(unit_info, dict):
                unit = unit_info.get(var_name, "not available")
                if unit == "not available":
                    logs.append(
                        {
                            "warning": "Missing unit information",
                            "message": f"Unit for '{var_name}' not found in units dictionary. "
                            "Using default 'not available'.",
                            "info_map": info_map,
                        }
                    )
            else:
                unit = unit_info

            new_var_name = f"{var_name} ({unit})"
            updated_data[new_var_name] = details

        return updated_data, logs

    def _generate_legend_keys(
        self,
        combined_var_name: str,
        omit_legend_prefix: str | list[str] | bool = False,
        omit_legend_suffix: str | list[str] | bool = False,
    ) -> str:
        """
        Strip out the prefix and suffix (if exists) in the combined variable name, and return the variable name.

        Parameters
        ----------
        combined_var_name: str
            The combined variable name to be processed.

        Returns
        -------
        str
            The stripped variable name.

        Notes
        -----
            This function identifies prefix and suffix according to the following logic:
                prefix:
                    All combined variable names are guaranteed to have a prefix of the following types:
                        - a custom defined prefix (e.g. Accumulated_ManureTreatmentDailyOutput_Pen_0_CALF)
                        - default-pattern prefix (class.method e.g. AnimalModuleReporter.report_pen_manure_properties)
                        - special cases => variables from the RufasTime and Weather classes (e.g. RufasTime.day,
                            Weather.rainfall)
                    For the special cases of variables from the RufasTime and Weather classes, they do not have any
                    suffixes, resulting in `len(combined_var_name_list) == 2`. Therefore, we can just return the second
                    element after splitting the combined variable name by ".".

                     We distinguish whether the prefix is a custom defined prefix or following the default pattern by
                     string parsing:
                     The class name in the default pattern prefixes follow the camel case pattern, a way to separate
                     the words in a phrase by making the first letter of each word capitalized and not using spaces
                     e.g. CamelCase. While the custom defined prefixes follow the snake case pattern, where each word is
                     separated by underscores.
                     Therefore, by checking if `combined_var_name_list[0]` follows the camel case pattern
                     ("([A-Z][a-z0-9]+)+"), we are able to find out if the variable is using the default pattern.

                     * `if len(combined_var_name_list) == 1` this check is here just for error proofing, this condition
                     is unlikely to appear.

                 suffix:
                    Currently, only the Crop and Soil module is utilizing the suffix feature while reporting variables.
                    After some investigation, we found that all suffixes from the Crop and Soil module follows the
                    pattern of field='*', for example:
                        - FieldDataReporter.send_annual_variables.annual_runoff_ammonium_total.field='field'
                        - FieldDataReporter.send_annual_variables.annual_carbon_CO2_lost.field='field',layer='2'
                    Therefore, by checking if hte last element in combined_var_name_list contains "=", we are able to
                    check if the variable name has suffix.
        """
        combined_var_name_list: list[str] = combined_var_name.split(".")
        slice_start: int = 0
        slice_end: int = len(combined_var_name_list)

        if len(combined_var_name_list) == 1:
            return combined_var_name_list[0]
        elif len(combined_var_name_list) == 2:
            return combined_var_name_list[1]

        else:
            if omit_legend_prefix:
                slice_start = 2 if re.match("([A-Z][a-z0-9]+)+", combined_var_name_list[0]) else 1

            if omit_legend_suffix:
                slice_end = -1 if "=" in combined_var_name_list[-1] else len(combined_var_name_list)

            updated_var_name = ".".join(combined_var_name_list[slice_start:slice_end])
            units = re.search(r"\(.*\)", combined_var_name_list[-1])
            if units and omit_legend_suffix:
                return f"{updated_var_name} {units.group()}"
            return updated_var_name

    def _log_non_numerical_data(
        self,
        filtered_pool: dict[str, dict[str, list[Any]]],
        graph_details: dict[str, str | list[str]],
    ) -> list[dict[str, str | dict[str, str]]]:
        """
        Identifies and logs entries in a filtered data pool that contain non-numeric data
        which cannot be used for plotting in a graph.

        Parameters
        ----------
        filtered_pool : dict[str, pool_element_type]
            The filtered pool of variables that the user wants to graph.
        graph_details: dict[str, str]
            A dictionary containing details/metadata about the graph.

        Returns
        -------
        list[dict[str, str | dict[str, str]]]
            A list of logs, warnings, and errors to be reported to OutputManager.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._log_non_numerical_data.__name__,
        }
        title = graph_details.get("title")
        log_pool: list[dict[str, str | dict[str, str]]] = []
        for key, value in filtered_pool.items():
            if isinstance(value["values"], list):
                if non_numerical_data := [item for item in value["values"] if not isinstance(item, (int, float))]:
                    non_numerical_data_types = set(
                        [type(non_numerical_item) for non_numerical_item in non_numerical_data]
                    )
                    log_pool.append(
                        {
                            "error": f"Can't plot {title} data set",
                            "message": f"{key} key contains non-numerical data that are {non_numerical_data_types} "
                            "and can't be graphed.",
                            "info_map": info_map,
                        }
                    )
            elif not isinstance(value["values"], (int, float)):
                log_pool.append(
                    {
                        "error": f"Can't plot {title} data set",
                        "message": f"{key} key contains non-numerical data that are {type(value['values'])} "
                        "and can't be graphed.",
                        "info_map": info_map,
                    }
                )
        return log_pool

    def _draw_graph(
        self,
        graph_type: str,
        data: dict[str, list[int | float]],
        selected_variables: list[str],
        ax: Axes,
        mask_values: bool = False,
        use_calendar_dates: bool = False,
        date_format: str | None = None,
        slice_start: int | None = None,
        slice_end: int | None = None,
    ) -> None:
        """
        Draw the graph based on the provided graph type and data.

        Parameters
        ----------
        graph_type : str
            The type of graph to draw.
        data : dict[str, list[int | float]]
            The data to use for plotting.
        selected_variables : list[str]
            The variables selected to be plotted.
        mask_values : bool, default False
            Whether data that will be plotted with non-tuple based functions should be masked to remove None or NaN
            values.
        ax : Axes
            The matplotlib Axes object to plot the graph on.
        use_calendar_dates : bool, default False
            Whether to use calendar dates on the x-axis.
        date_format : str, default None
            The user-requested format to use for the date on the x-axis.
        slice_start : int, default None
            The starting index of the data to plot.
        slice_end : int, default None
            The ending index of the data to plot.

        Raises
        ------
        ValueError
            if graph_type is not found in MATPLOTLIB_PLOT_FUNCTIONS.
        """
        if graph_type not in MATPLOTLIB_PLOT_FUNCTIONS:
            raise ValueError(f"Unsupported graph type: {graph_type}")
        plot_function = MATPLOTLIB_PLOT_FUNCTIONS[graph_type]
        max_data_length = max(len(v) for v in data.values())
        if slice_start is not None:
            slice_start_sim_day = self.time.convert_slice_to_simulation_day(slice_start)
            slice_end_sim_day = self.time.convert_slice_to_simulation_day(slice_end)
            dates_in_data_range = [
                self.time.convert_simulation_day_to_date(i) for i in range(slice_start_sim_day, slice_end_sim_day)
            ]
        else:
            dates_in_data_range = [self.time.start_date + datetime.timedelta(days=i) for i in range(max_data_length)]

        get_x_values: Callable[[int], list[int]] = lambda values_length: (
            dates_in_data_range[:values_length] if use_calendar_dates else list(range(values_length))
        )

        if graph_type in TUPLE_BASED_FUNCTIONS:
            values_tuple = tuple(data[variable] for variable in selected_variables)
            x_values = get_x_values(len(values_tuple[0]))
            plot_function(x_values, values_tuple)
        else:
            for value in data.values():
                if mask_values:
                    indices, masked_values = self._mask_values(value)
                    x_values = get_x_values(len(indices))
                    plot_function(x_values, masked_values)
                else:
                    x_values = get_x_values(len(value))
                    plot_function(x_values, value)
        if use_calendar_dates:
            ax.xaxis.set_major_formatter(Utility.get_date_formatter(date_format))
            plt.xlabel("Calendar Date")
            plt.xticks(rotation=45)
        else:
            plt.xlabel("Simulation Day")

    def _mask_values(self, values: list[Any]) -> tuple[npt.NDArray[Any], npt.NDArray[np.float32]]:
        """
        Masks values to remove None and NaN values.

        Parameters
        ----------
        values : list[Any]
            list of data to be masked.

        Returns
        -------
        tuple[NDArray[Any], NDArray[np.float32]]
            list of NumPy arrays, the first containing the indices of the masked data and the second containing the
            actual masked data.

        """
        np_values = np.array(values)
        mask = ~np.isnan(np_values)
        indices = np.arange(len(np_values))
        return (indices[mask], np_values[mask])

    def _customize_graph(self, fig: Figure, customization_details: dict[str, Any]) -> None:
        """
        Apply customizations to the graph.

        Parameters
        ----------
        fig : Figure
            The matplotlib Figure object to customize.
        customization_details : dict[str, Any]
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

    def _save_graph(
        self,
        graph_details: dict[str, str | list[str]],
        filter_file_name: str,
        graphics_dir: Path,
    ) -> Path:
        """
        Save the generated graph to a file.

        Parameters
        ----------
        graph_details : dict[str, str]
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
            plt.savefig(graph_path, bbox_inches="tight")
            return graph_path
        except Exception as e:
            raise Exception(f"An error occurred while trying to save the graph: {e}") from e

    def _generate_graph_path(
        self,
        graph_details: dict[str, str],
        filter_file_name: str,
        graphics_dir: Path,
    ) -> Path:
        """
        Generate the full path for the output graph and create parent folders if necessary.

        Parameters
        ----------
        graph_details : dict[str, str]
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
