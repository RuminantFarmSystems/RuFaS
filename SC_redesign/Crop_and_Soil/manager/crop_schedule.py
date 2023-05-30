from typing import List, Any


class CropSchedule:

    def __init__(self, crop_reference: str, planting_years: int | List[int], planting_days: int | List[int],
                 harvest_years: int | List[int], harvest_days: int | List[int], harvest_operations: str | List[str],
                 use_heat_scheduling: bool = False, pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Creates a CropSchedule instance based on user input.

        Parameters
        ----------
        crop_reference : str
            Reference to name of the crop that will be used to identify the correct configuration.
        planting_years : int | List[int]
            Year(s) in which crop is planted.
        planting_days : int | List[int]
            Day(s) on which crop is planted.
        harvest_years : int | List[int]
            Year(s) in which crop is harvested.
        harvest_days : int | List[int]
            Day(s) on which crop is harvested.
        harvest_operations : str | List[str]
            Operation(s) with which a crop is harvested.
        use_heat_scheduling : bool, default=False
            Variable indicating if heat scheduling should be used to determine when crop is harvested.
        pattern_skip : int, default=0
            Number of days/years to skip between cycles.
        pattern_repeat : int, default=0
            Number of times the specified crop planting and harvesting pattern should be repeated.


        Notes
        -----
        If use_heat_scheduling is True, then this is the only variable used to determine whether a crop should be
        harvested on a given day.

        """
        self.crop_reference = crop_reference

        self.planting_years = self._convert_to_list(planting_years)
        self.planting_days = self._convert_to_list(planting_days)
        self.harvest_years = self._convert_to_list(harvest_years)
        self.harvest_days = self._convert_to_list(harvest_days)
        self.harvest_operations = self._convert_to_list(harvest_operations)

        if len(self.planting_days) == 1:
            self.planting_days *= len(self.planting_years)

        if len(self.harvest_days) == 1:
            self.harvest_days *= len(self.harvest_years)

        if len(self.harvest_operations) == 1:
            self.harvest_operations *= len(self.harvest_years)

        if len(self.planting_days) != len(self.planting_years):
            raise ValueError("Number of years that crops are planted in and days crops are planted on must be equal.")

        equal_harvest_parameters = len(self.harvest_years) == len(self.harvest_days) == len(self.harvest_operations)
        if not equal_harvest_parameters:
            raise ValueError("Number of values for harvest years, days, and operations must be equal.")

        if pattern_skip < 0:
            raise ValueError(f"Expected pattern skip to be >= 0, received '{pattern_skip}'.")
        elif pattern_repeat < 0:
            raise ValueError(f"Expected pattern repeat to be >= 0, received '{pattern_repeat}'.")
        self.pattern_skip = pattern_skip
        self.pattern_repeat = pattern_repeat

        self.heat_scheduled = use_heat_scheduling

    @staticmethod
    def _convert_to_list(to_be_converted: Any) -> List:
        """
        Converts any arbitrary data into a list that contains that data.

        Parameters
        ----------
        to_be_converted : Any
            Data to be converted.

        Returns
        -------
        List
            The data passed contained in a list.

        Notes
        -----
        If the data passed is already a list, it doesn't do anything to it.

        """
        if type(to_be_converted) == list:
            return to_be_converted
        return [to_be_converted]
