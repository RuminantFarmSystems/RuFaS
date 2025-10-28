from math import exp, log, sqrt
from typing import List, Optional

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data import CropData


class LeafAreaIndex:
    """
    Manages the leaf area index (LAI) for crops, based on the 'Canopy Cover and Height' section of SWAT (5:2.1.2).

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        A `CropData` instance containing crop specifications and attributes. Defaults to a new instance of `CropData` if
        not provided.
    max_canopy_height : float, default None
        Maximum canopy height for the plant (m).
    lai_shapes : Optional[float], default None
        Shape coefficients for calculating leaf area index (unitless).
    optimal_leaf_area_fraction : Optional[float], default None
        Fraction of max leaf area index for current heat fraction (unitless).
    canopy_height : Optional[float], default None
        Current height of the plant (m).
    leaf_area_added : Optional[float], default None
        Leaf area index change during the day (unitless).
    optimal_leaf_area_change : Optional[float], default None
        Leaf area index added under ideal conditions (unitless).
    previous_leaf_area_index : Optional[float], default None
        Leaf area index on the previous day (unitless).
    previous_optimal_leaf_area_fraction : Optional[float], default None
        Optimal leaf area fraction on the previous day (unitless).

    Attributes
    ----------
    data : CropData
        Reference to the provided `CropData` instance or a new default instance.
    max_canopy_height : float
        Maximum canopy height for the plant (m).
    lai_shapes : Optional[float]
        Shape coefficients for calculating leaf area index (unitless).
    optimal_leaf_area_fraction : Optional[float]
        Fraction of max leaf area index for current heat fraction (unitless).
    canopy_height : Optional[float]
        Current height of the plant (m).
    leaf_area_added : Optional[float]
        Leaf area index change during the day (unitless).
    optimal_leaf_area_change : Optional[float]
        Leaf area index added under ideal conditions (unitless).
    previous_leaf_area_index : Optional[float]
        Leaf area index on the previous day (unitless).
    previous_optimal_leaf_area_fraction : Optional[float]
        Optimal leaf area fraction on the previous day (unitless).

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        lai_shapes: Optional[float] = None,
        optimal_leaf_area_fraction: Optional[float] = None,
        canopy_height: Optional[float] = None,
        leaf_area_added: Optional[float] = None,
        optimal_leaf_area_change: Optional[float] = None,
        previous_leaf_area_index: Optional[float] = None,
        previous_optimal_leaf_area_fraction: Optional[float] = None,
    ) -> None:
        self.data = crop_data or CropData()
        self.lai_shapes = lai_shapes
        self.optimal_leaf_area_fraction = optimal_leaf_area_fraction
        self.canopy_height = canopy_height
        self.leaf_area_added = leaf_area_added
        self.optimal_leaf_area_change = optimal_leaf_area_change
        self.previous_leaf_area_index = previous_leaf_area_index
        self.previous_optimal_leaf_area_fraction = previous_optimal_leaf_area_fraction

    def grow_canopy(self) -> None:
        """
        Main leaf area index function.

        """
        self.lai_shapes = self._determine_lai_shapes(
            self.data.first_heat_fraction_point,
            self.data.second_heat_fraction_point,
            self.data.first_leaf_fraction_point,
            self.data.second_leaf_fraction_point,
        )

        self.optimal_leaf_area_fraction = self._determine_optimal_leaf_area_fraction(
            self.data.heat_fraction,
            self.lai_shapes[0],
            self.lai_shapes[1],
        )

        self.canopy_height = self.determine_canopy_height(self.data.max_canopy_height, self.optimal_leaf_area_fraction)
        if self.data.is_in_senescence and not self.data.is_perennial:  # senescence
            self.data.leaf_area_index = self._determine_senescent_leaf_area_index(
                self.data.heat_fraction,
                self.data.senescent_heat_fraction,
                self.data.max_leaf_area_index,
            )

        elif self.data.is_in_senescence and self.data.is_perennial:
            self.shift_leaf_area_time()
            return
        else:  # normal growth
            self.check_previous_leaf_area_values()
            self.optimal_leaf_area_change = self._determine_max_leaf_area_change(
                self.optimal_leaf_area_fraction,
                self.previous_optimal_leaf_area_fraction,
                self.data.max_leaf_area_index,
                self.previous_leaf_area_index,
            )
            self.determine_leaf_area_added()
            self.add_leaf_area()
        self.shift_leaf_area_time()

    def shift_leaf_area_time(self) -> None:
        """
        Shifts the time window by one step for leaf area attributes.

        Notes
        -----
        This method updates the historical record of leaf area indices by shifting the current leaf area index
        and optimal leaf area fraction to their respective 'previous' attributes. This is typically done to
        prepare for a new day's growth calculations.

        """
        self.previous_leaf_area_index = self.data.leaf_area_index
        self.previous_optimal_leaf_area_fraction = self.optimal_leaf_area_fraction

    def check_previous_leaf_area_values(self) -> None:
        """
        Check for previous LAI values and set them to 0 if none are present.

        Notes
        -----
        This function is used to handle the initial time point in the simulation. It ensures that the previous LAI
        values are initialized to 0 if they haven't been set yet, providing a baseline for the start of the simulation.

        """
        if self.previous_optimal_leaf_area_fraction is None:
            self.previous_optimal_leaf_area_fraction = 0
        if self.previous_leaf_area_index is None:
            self.previous_leaf_area_index = 0

    def determine_leaf_area_added(self) -> None:
        """
        Sets the actual leaf area added, adjusted for the plant growth factor.

        References
        ----------
        SWAT 5:3.2.2

        """
        self.leaf_area_added = min(
            self.optimal_leaf_area_change * sqrt(self.data.growth_factor),
            self.optimal_leaf_area_change,
        )

    def add_leaf_area(self) -> None:
        """
        Adds new leaf area to the plant.

        References
        ----------
        SWAT 5:2.1.18

        """
        self.data.leaf_area_index = max(0.0, self.previous_leaf_area_index + self.leaf_area_added)

    @staticmethod
    def determine_canopy_height(max_canopy_height: float, optimal_leaf_area_fraction: float) -> float:
        """
        Sets the current height of the canopy, measured in meters.

        Parameters
        ----------
        max_canopy_height : float
            The maximum height that the canopy can reach (meters).
        optimal_leaf_area_fraction : float
            The fraction of the maximum leaf area index corresponding to the current heat fraction (unitless).

        Returns
        -------
        float
            The current height of the canopy (meters).

        References
        ----------
        SWAT 5:2.1.14

        Raises
        ------
        ValueError
            If negative Max_canopy_height is provided.
            If optimal_leaf_area_fraction is negative or greater than 1.

        """
        if max_canopy_height < 0:
            raise ValueError("max_canopy_height must be greater than 0")
        if not 0 <= optimal_leaf_area_fraction <= 1:
            raise ValueError("optimal_leaf_area_index must be >= 0 and <= 1")
        return min(max_canopy_height, max_canopy_height * sqrt(optimal_leaf_area_fraction))

    @staticmethod
    def _determine_lai_shapes(
        first_heat_fraction: float,
        second_heat_fraction: float,
        first_leaf_fraction: float,
        second_leaf_fraction: float,
    ) -> List[float]:
        """
        Calculates the shape coefficients for the optimal Leaf Area Index (LAI) formula.

        Parameters
        ----------
        first_heat_fraction : float
            Fraction of the growing season corresponding to the first point on the optimal leaf development curve.
        second_heat_fraction : float
            Fraction of the growing season corresponding to the second point on the optimal leaf development curve.
        first_leaf_fraction : float
            Fraction of maximum leaf area index corresponding to the first point on the optimal leaf development curve.
        second_leaf_fraction : float
            Fraction of maximum leaf area index corresponding to the second point on the optimal leaf development curve.

        Returns
        -------
        List[float]
            A list of shape coefficients used in the optimal LAI formula.

        """
        info_map = {
            "class": LeafAreaIndex.__class__.__name__,
            "function": LeafAreaIndex._determine_lai_shapes.__name__,
        }
        om = OutputManager()
        if first_heat_fraction <= 0:
            om.add_error(
                "Invalid first heat fraction",
                f"First heat fraction should be greater than 0, got: {first_heat_fraction}.",
                info_map,
            )
            raise ValueError("first_heat_fraction must be greater than 0")
        if second_heat_fraction <= 0:
            om.add_error(
                "Invalid second heat fraction",
                f"Second heat fraction should be greater than 0, got: {second_heat_fraction}.",
                info_map,
            )
            raise ValueError("second_heat_fraction must be greater than 0")
        if not 0 < first_leaf_fraction < 1:
            om.add_error(
                "Invalid first leaf fraction",
                f"'first_leaf_fraction' must be between 0 and 1 (exclusive), got: {first_leaf_fraction}.",
                info_map,
            )
            raise ValueError("first_leaf_fraction must not be greater than 0 or less than 1")
        if not 0 < second_leaf_fraction < 1:
            om.add_error(
                "Invalid second leaf fraction",
                f"'second_leaf_fraction' must be between 0 and 1 (exclusive), got: {second_leaf_fraction}.",
                info_map,
            )
            raise ValueError("second_leaf_fraction must not be greater than 0 or less than 1")
        if first_heat_fraction == second_heat_fraction:
            om.add_error(
                "Invalid first and second heat fraction combination.",
                f"First_heat_fraction cannot be exactly equal to second_heat_fractions,"
                f" got first heat fraction equal to second heat fraction: {second_heat_fraction}.",
                info_map,
            )
            raise ValueError("first_heat_fraction cannot be exactly equal to second_heat_fractions")

        first_log = LeafAreaIndex._calc_shape_log(first_heat_fraction, first_leaf_fraction)
        second_log = LeafAreaIndex._calc_shape_log(second_heat_fraction, second_leaf_fraction)

        second_shape = (first_log - second_log) / (second_heat_fraction - first_heat_fraction)
        first_shape = first_log + (second_shape * first_heat_fraction)

        return [first_shape, second_shape]

    @staticmethod
    def _determine_optimal_leaf_area_fraction(heat_fraction: float, shape1: float, shape2: float) -> float:
        """
        Calculates the leaf area index fraction from the optimal leaf area development curve for the initial period of
        plant growth.

        Parameters
        ----------
        heat_fraction : float
            Fraction of potential heat units accumulated by the plant.
        shape1 : float
            The first shape coefficient of the leaf area development curve.
        shape2 : float
            The second shape coefficient of the leaf area development curve.

        Returns
        -------
        float
            The fraction of the plant's maximum leaf area index corresponding to the given fraction of potential heat
            units, constrained to be bounded at zero.

        Notes
        -----
        This method is particularly focused on the initial growth period of the plant.

        References
        ----------
        SWAT 5:2.1.10

        """
        return max(heat_fraction / (heat_fraction + exp(shape1 - (shape2 * heat_fraction))), 0)

    @staticmethod
    def _determine_max_leaf_area_change(
        leaf_area_fraction: float,
        previous_leaf_area_fraction: float,
        max_leaf_area_index: float,
        previous_leaf_area_index: float,
    ) -> float:
        """
        Calculates the maximum leaf area added during the day.

        Parameters
        ----------
        leaf_area_fraction : float
            Optimal leaf area fraction for the day (unitless).
        previous_leaf_area_fraction : float
            Previous day's optimal leaf area fraction (unitless).
        max_leaf_area_index : float
            The maximum leaf area index achievable by the plant (unitless).
        previous_leaf_area_index : float
            The previous day's leaf area index (unitless).

        Returns
        -------
        float
            The maximum leaf area added during the day.

        Notes
        -----
        Actual leaf area index (LAI) is corrected for growth constraints, so the previous day's optimal leaf area
        fraction may not be the same as the previous day's LAI divided by the max LAI.
        This method replaces the 'calc_max_leaf_area_change' method and calculates the potential increase in
        leaf area index based on current and previous day's leaf area fractions and the maximum leaf area index
        achievable by the plant.

        References
        ----------
        SWAT 5:2.1.16

        """
        return (
            (leaf_area_fraction - previous_leaf_area_fraction)
            * max_leaf_area_index
            * (1 - exp(5 * (previous_leaf_area_index - max_leaf_area_index)))
        )

    @staticmethod
    def _determine_senescent_leaf_area_index(
        heat_fraction: float,
        senescent_heat_fraction: float,
        optimal_leaf_area_fraction: float,
    ) -> float:
        """
        Calculates a plant's leaf area index during senescence.

        Parameters
        ----------
        heat_fraction : float
            The current fraction of potential heat units accumulated by the plant (unitless).
        senescent_heat_fraction : float
            The fraction of potential heat units at which senescence begins for the plant (unitless).
        optimal_leaf_area_fraction : float
            The optimal leaf area fraction for the plant (unitless).

        Returns
        -------
        float
            The calculated leaf area index of the plant during its senescence phase.

        Notes
        -----
        This method replaces the 'calc_senescent_leaf_area_index' method. It determines the leaf area index
        for a plant as it undergoes senescence, based on the current heat unit accumulation and the onset of
        senescence in terms of heat units.

        References
        ----------
        SWAT 5:2.1.19

        """
        if senescent_heat_fraction >= 1:
            raise ValueError("Senescent heat fraction must be less than 1")
        else:
            prop = (1 - heat_fraction) / (1 - senescent_heat_fraction)

        return max(prop * optimal_leaf_area_fraction, 0)

    @staticmethod
    def _calc_shape_log(heat_fraction: float, leaf_area_fraction: float) -> float:
        """
        Calculates the logarithmic term of the LAI shape parameter function.

        Parameters
        ----------
        heat_fraction : float
            Fraction of heat units accumulated by the plant; must be greater than zero (unitless).
        leaf_area_fraction : float
            Fraction of the plant's maximum leaf area; must be greater than zero, less than one, and not
            equal to the heat_fraction (unitless).

        Notes
        -----
        This function is primarily used by the `determine_lai_shapes` method. Error handling for the input
        parameters is conducted within `determine_lai_shapes`.

        """
        return log((heat_fraction / leaf_area_fraction) - heat_fraction)
