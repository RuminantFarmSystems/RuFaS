class ReportGenerator:    
    def _generate_report(
        self,
        filtered_pool: Dict[str, pool_element_type],
        filter_content: Dict[str, str | int],
        filter_file: Path,
    ) -> List[Any]:
        info_map = {
            "class": self.__class__.__name__,
            "function": self._generate_report.__name__,
        }
        self.add_log("init_report_generation", "Report Generation Started", info_map)
        selected_variables = filter_content.get("variables")
        slice_start = filter_content.get("slice_start", 0)
        slice_end = filter_content.get("slice_end", 0)
        report_data = self._prepare_report_data(
            filtered_pool, selected_variables, slice_start, slice_end
        )
        if not report_data:
            self.add_error(
                "empty report data",
                f"filter {filter_content.get('filters')} in {filter_file} led to empty report data.",
            )
            return
        number_of_elements = len(report_data[next(iter(report_data))])

        horizontal_agg_key = filter_content.get("horizontal_aggregation")
        horizontal_aggregator = (
            aggregator_functions.get(horizontal_agg_key)
            if horizontal_agg_key in aggregator_functions
            else None
        )

        vertical_agg_key = filter_content.get("vertical_aggregation")
        vertical_aggregator = (
            aggregator_functions.get(vertical_agg_key)
            if vertical_agg_key in aggregator_functions
            else None
        )

        if horizontal_aggregator and vertical_aggregator:
            if filter_content.get("horizontal_first", True):
                horizontally_aggregated = [
                    horizontal_aggregator(
                        {key: report_data[key][i] for key in report_data}
                    )
                    for i in range(number_of_elements)
                ]
                return vertical_aggregator(horizontally_aggregated)
            else:
                vertically_aggregated = {
                    key: vertical_aggregator(data_series)
                    for key, data_series in report_data.items()
                }
                return horizontal_aggregator(vertically_aggregated)
        elif horizontal_aggregator:
            return [
                horizontal_aggregator({key: report_data[key][i] for key in report_data})
                for i in range(number_of_elements)
            ]
        elif vertical_aggregator:
            return {
                key: vertical_aggregator(data_series)
                for key, data_series in report_data.items()
            }

        return report_data

    def _prepare_report_data(
        self,
        filtered_pool: Dict[str, pool_element_type],
        selected_variables: List[str],
        slice_start: int,
        slice_end: int,
    ) -> Dict[str, List[Any]]:
        """
        Processes and structures a filtered data pool for report generation.

        This method organizes data from a filtered pool based on selected variables and slicing parameters.
        It caters to different data structures within the pool, ensuring data is formatted appropriately
        for report inclusion.

        Parameters
        ----------
        filtered_pool : Dict[str, pool_element_type]
            The filtered data pool with each key mapping to its respective data element.

        selected_variables : List[str]
            Variables to be included from the filtered pool.

        slice_start : int
            Starting index for slicing data elements.

        slice_end : int
            Ending index for slicing; slices to end if set to 0.

        Returns
        -------
        Dict[str, List[Any]]
            Processed data suitable for report generation, keyed by selected variables.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._prepare_report_data.__name__,
        }
        report_data: Dict[str, List[Any]] = {}
        for key in filtered_pool.keys():
            is_data_in_dict = isinstance(filtered_pool[key]["values"][0], dict)
            if is_data_in_dict:
                if selected_variables is None:
                    self.add_error(
                        "missing_variables_entry",
                        "Can't generate report, use 'variables' arg to select items from data",
                        info_map,
                    )
                report_data.update(
                    Utility.convert_list_of_dicts_to_dict_of_lists(
                        filtered_pool[key]["values"][
                            slice_start : slice_end
                            if slice_end != 0
                            else len(filtered_pool[key]["values"])
                        ]
                    )
                )
            else:
                report_data[key] = filtered_pool[key]["values"][
                    slice_start : slice_end
                    if slice_end != 0
                    else len(filtered_pool[key]["values"])
                ]
        return report_data
