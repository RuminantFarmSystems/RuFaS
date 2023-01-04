from math import exp, log, sqrt
from typing import List, Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


"""
This module is based off of the 'Canopy Cover and Height' section of SWAT
"""


class LeafAreaIndex:
    def __init__(self, crop_data: Optional[CropData] = None):
        data = crop_data or CropData()  # initialize with defaults, if not given
        # TODO replace attributes with reference to data - GitHub Issue #255
        #  in various methods
        # fixed attributes (unchanged during simulations)
        self.first_heat_fraction_point = 0.15
        self.second_heat_fraction_point = 0.50
        self.first_leaf_fraction_point = 0.01
        self.second_leaf_fraction_point = 0.95
        self.max_canopy_height = 2.5  # m
        self.growth_factor = 1.0
        self.max_leaf_area_index = 3.0
        self.senescent_heat_fraction = 0.9
        # variable attributes (change throughout simulations)
        self.leaf_area_index = 0
        self.heat_fraction = 0.73
        # empty variables
        self._lai_shapes = None
        self.optimal_leaf_area_fraction = None
        self.canopy_height = None
        self.leaf_area_added = None
        self.max_leaf_area_change = None
        self.previous_leaf_area_index = None
        self.previous_optimal_leaf_area_fraction = None

    def grow_canopy(self) -> None:
        """main leaf area index function"""
        self._lai_shapes = self._determine_lai_shapes(self.first_heat_fraction_point, self.second_heat_fraction_point,
                                                      self.first_leaf_fraction_point, self.second_leaf_fraction_point)

        self.optimal_leaf_area_fraction = self.determine_optimal_leaf_area_fraction(self.heat_fraction,
                                                                                    self._lai_shapes[0],
                                                                                    self._lai_shapes[1])

        self.canopy_height = self.determine_canopy_height(self.max_canopy_height, self.optimal_leaf_area_fraction)
        if self.is_in_senescence:  # senescence
            self.leaf_area_index = self.determine_senescent_leaf_area_index(self.heat_fraction,
                                                                            self.senescent_heat_fraction,
                                                                            self.optimal_leaf_area_fraction)
        else:  # normal growth
            self.check_previous_leaf_area_values()
            self.max_leaf_area_change = self.determine_max_leaf_area_change(self.optimal_leaf_area_fraction,
                                                                            self.previous_optimal_leaf_area_fraction,
                                                                            self.max_leaf_area_index,
                                                                            self.previous_leaf_area_index)
            self.determine_leaf_area_added()
            self.add_leaf_area()
        self.shift_leaf_area_time()

    def shift_leaf_area_time(self) -> None:
        """shifts the time window by one step for leaf area attributes"""
        self.previous_leaf_area_index = self.leaf_area_index
        self.previous_optimal_leaf_area_fraction = self.optimal_leaf_area_fraction

    def check_previous_leaf_area_values(self) -> None:
        """check for previous LAI values and set them to 0 if none are present. This function handles the
        initial time point in the simulation"""
        if self.previous_optimal_leaf_area_fraction is None:
            self.previous_optimal_leaf_area_fraction = 0
        if self.previous_leaf_area_index is None:
            self.previous_leaf_area_index = 0

    def determine_leaf_area_added(self) -> None:
        """sets actual leaf area added, by adjusting for the plant growth factor
        SWAT Reference: 5:3.2.2
        """
        self.leaf_area_added = min(self.max_leaf_area_change * sqrt(self.growth_factor), self.max_leaf_area_change)

    def add_leaf_area(self) -> None:
        """add new leaf area to the plant
        SWAT Reference: 5:2.1.18"""
        self.leaf_area_index = max(0, self.previous_leaf_area_index + self.leaf_area_added)

    @property
    def is_in_senescence(self) -> bool:
        """check if the plant is in senescence"""
        return self.heat_fraction > self.senescent_heat_fraction

    @staticmethod
    def determine_canopy_height(max_canopy_height: float, optimal_leaf_area_fraction: float) -> float:
        """sets the current height of the canopy, in meters
        SWAT Reference: 5:2.1.14"""
        if max_canopy_height < 0:
            raise ValueError("max_canopy_height must be greater than 0")
        if not 0 <= optimal_leaf_area_fraction <= 1:
            raise ValueError("optimal_leaf_area_index must be >= 0 and <= 1")
        return min(max_canopy_height, max_canopy_height * sqrt(optimal_leaf_area_fraction))

    @staticmethod
    def _determine_lai_shapes(first_heat_fraction: float, second_heat_fraction: float,
                              first_leaf_fraction: float, second_leaf_fraction: float) -> List[float]:
        """
        calculates the shape coefficients for optimal LAI formula
        """
        if first_heat_fraction <= 0:
            raise ValueError("first_heat_fraction must be greater than 0")
        if second_heat_fraction <= 0:
            raise ValueError("second_heat_fraction must be greater than 0")
        if not 0 < first_leaf_fraction < 1:
            raise ValueError("first_leaf_fraction must not be greater than 0 or less than 1")
        if not 0 < second_leaf_fraction < 1:
            raise ValueError("second_leaf_fraction must not be greater than 0 or less than 1")
        if first_heat_fraction == second_heat_fraction:
            # TODO: perhaps a way to handle this instead of throwing an error would be better
            #   something like: second_heat_fraction += 1e-9
            raise ValueError("first_heat_fraction cannot be exactly equal to second_heat_fractions")

        # TODO: need to add any of these errors that get thrown when RuFaS runs to the  `OutputManager`.
        #    This should probably be done in the `grow_canopy()` function
        #    I'm still unsure how to do this effectively with warnings raised by static functions. - morrowcj

        first_log = LeafAreaIndex.calc_shape_log(first_heat_fraction, first_leaf_fraction)
        second_log = LeafAreaIndex.calc_shape_log(second_heat_fraction, second_leaf_fraction)

        second_shape = (first_log - second_log) / (second_heat_fraction - first_heat_fraction)
        first_shape = first_log + (second_shape * first_heat_fraction)

        return [first_shape, second_shape]

    @staticmethod
    def determine_optimal_leaf_area_fraction(heat_fraction: float, shape1: float, shape2: float) -> float:
        """calculates leaf area index fraction, from the optimal leaf area development curve, for the initial period of
        plant growth

        Args:
            heat_fraction: fraction of potential heat units
            shape1: first shape coefficient
            shape2: second shape coefficient

        Returns:
            fraction of the plant's maximum leaf area index

        Details: specifically, the calculated value is the 'fraction of the plant's maximum leaf area index
        corresponding to a given fraction of potential heat units for the plant' (heat_fraction), constrained to be
        bounded at zero.

        SWAT Reference: 5:2.1.10
        """
        return max(heat_fraction / (heat_fraction + exp(shape1 - (shape2 * heat_fraction))), 0)

    @staticmethod
    def determine_max_leaf_area_change(leaf_area_fraction: float, previous_leaf_area_fraction: float,
                                       max_leaf_area_index: float, previous_leaf_area_index: float) -> float:
        """
        calculates the maximum leaf area added during the day

        replaces method calc_max_leaf_area_change

        Args:
            leaf_area_fraction: optimal leaf area fraction for the day
            previous_leaf_area_fraction: previous day's optimal leaf area fraction
            max_leaf_area_index: the maximum leaf area index achievable by the plant
            previous_leaf_area_index: the previous day's leaf area index

        Returns:
            the maximum leaf area added during the day

        Details: because actual leaf area index (LAI) is corrected for growth constraints, the previous
        day's optimal leaf area fraction may not be the same as the previous day's LAI divided by the
        max LAI.

        SWAT Reference: 5:2.1.16
        """
        return (leaf_area_fraction - previous_leaf_area_fraction) * max_leaf_area_index * \
            (1 - exp(5 * previous_leaf_area_index - max_leaf_area_index))

    @staticmethod
    def determine_senescent_leaf_area_index(heat_fraction: float, senescent_heat_fraction: float,
                                            optimal_leaf_area_fraction: float) -> float:
        """calculates a plant's leaf area index during senescence

        replaces method calc_senescent_leaf_area_index

        Args:
            heat_fraction: the current fraction of potential heat units
            senescent_heat_fraction: the fraction of potential heat units at which senescence begins
            optimal_leaf_area_fraction: the optimal leaf area fraction for the plant

        Returns: the plant's leaf area index

        SWAT Reference: 5:2.1.19
        """
        if senescent_heat_fraction >= 1:
            raise ValueError("Senescent heat fraction must be less than 1")
        else:
            prop = (1 - heat_fraction) / (1 - senescent_heat_fraction)

        return max(prop * optimal_leaf_area_fraction, 0)

    @staticmethod
    def calc_shape_log(heat_fraction: float, leaf_area_fraction: float) -> float:
        """calculates the log term of LAI shape parameter function

        Args:
            heat_fraction: fraction of heat units accumulated; must be greater than zero
            leaf_area_fraction: fraction of max leaf area; must be greater than zero, less than one, and not
                equal to heat_fraction

        Details: used by determine_lai_shapes, where errors are handled
        """
        return log((heat_fraction / leaf_area_fraction) - heat_fraction)
