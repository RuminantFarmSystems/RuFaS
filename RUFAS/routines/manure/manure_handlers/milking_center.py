from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen


class MilkingCenter:
    def __init__(self,
                 num_milkings=3,
                 minutes_spent_in_holding_area=30.0,
                 minutes_spent_per_milking=7.0,
                 wash_water_use_rate=20.0,
                 fresh_water_use_rate=10.0):
        """Initialize the milking center.

        Parameters
            num_milkings: Number of milkings per animal per day.
            minutes_spent_per_milking: Number of minutes spent per milking per animal.
            minutes_spent_in_holding_area: Number of minutes spent in holding area per animal per day.
            wash_water_use_rate: Wash water use rate in the holding area, liters/animal/day.
            fresh_water_use_rate: Fresh water use rate for milking, liters/animal/day.

        """

        self.num_milkings = num_milkings
        self.minutes_spent_in_holding_area = minutes_spent_in_holding_area
        self.minutes_spent_per_milking = minutes_spent_per_milking
        self.wash_water_use_rate = wash_water_use_rate
        self.fresh_water_use_rate = fresh_water_use_rate

    """A class that calculates the time spent and water usage in the milking center by cows.

    Note that only cows are considered in this class.

    Attributes
        num_milkings: Number of milkings per animal per day.
        minutes_spent_per_milking: Number of minutes spent per milking per animal.
        minutes_spent_in_holding_area: Number of minutes spent in holding area per animal per milking.
        wash_water_use_rate: Wash water use rate in the holding area, liters/animal/day.
        fresh_water_use_rate: Fresh water use rate for milking, liters/animal/day.

    """

    # In holding area
    @property
    def total_minutes_spent_in_holding_area(self) -> float:
        """Total number of minutes spent in holding area per animal per day.

        Returns
            Total number of minutes spent in holding area per animal per day.

        """

        return self.num_milkings * self.minutes_spent_in_holding_area

    @property
    def percent_of_day_spent_in_holding_area(self) -> float:
        """Percentage of day spent in holding area.

        Returns
            Percentage of day spent in holding area.

        """

        return self._calc_percent_of_day_from_minutes(self.total_minutes_spent_in_holding_area)

    def wash_water_volume_used_in_holding_area(self, pen: ManureManagementPen) -> float:
        """Volume of wash water used in holding area.

        Returns
            Volume of wash water used in holding area, liters.

        """

        if self._has_lac_cow_in_pen(pen):
            return pen.num_animals * self.wash_water_use_rate
        return 0.0

    # Milking
    @property
    def total_minutes_spent_milking(self) -> float:
        """Total number of minutes spent milking per animal per day.

        Returns
            Total number of minutes spent milking per animal per day.

        """

        return self.num_milkings * self.minutes_spent_per_milking

    @property
    def percent_of_day_spent_milking(self) -> float:
        """Percentage of day spent milking.

        Returns
            Percentage of day spent milking.

        """

        return self._calc_percent_of_day_from_minutes(self.total_minutes_spent_milking)

    def fresh_water_volume_used_for_milking(self, pen: ManureManagementPen) -> float:
        """Volume of fresh water used for milking.

        Returns
            Volume of fresh water used for milking, liters.

        """

        if self._has_lac_cow_in_pen(pen):
            return pen.num_animals * self.fresh_water_use_rate
        return 0.0

    # Overall
    @property
    def total_minutes_spent_in_milking_center(self) -> float:
        """Total number of minutes spent in the milking center per animal per day.

        Note that this includes both the time spent in the holding area
        and the time spent milking.

        Returns
            Total number of minutes spent in the milking center per animal per day.

        """

        return self.total_minutes_spent_in_holding_area + self.total_minutes_spent_milking

    @property
    def total_percent_of_day_spent_in_milking_center(self) -> float:
        """Total percentage of day spent in the milking center per animal.

        Returns
            Total percentage of day spent in the milking center per animal.

        """

        return self.percent_of_day_spent_in_holding_area + self.percent_of_day_spent_milking

    def total_water_volume_used_in_milking_center(self, pen: ManureManagementPen) -> float:
        """Total volume of water used in the milking center.

        Parameters
            pen: ManureManagementPen object.

        Returns
            Total volume of water used in the milking center, liters.

        """

        if self._has_lac_cow_in_pen(pen):
            return self.wash_water_volume_used_in_holding_area(pen) + \
                   self.fresh_water_volume_used_for_milking(pen)  # liters
        return 0.0

    def manure_mass_deposited_in_milking_center(self, pen: ManureManagementPen) -> float:
        """Total mass of manure deposited in the milking center by all cows in pen.

        Parameters
            pen: ManureManagementPen object.

        Returns
            Total mass of manure deposited in the milking center, kg.

        """

        if self._has_lac_cow_in_pen(pen):
            return pen.manure.Mkg * self.total_percent_of_day_spent_in_milking_center / 100
        return 0.0

    def manure_volume_deposited_in_milking_center(self, pen: ManureManagementPen) -> float:
        """Total volume of manure deposited in the milking center.

        Parameters
            pen: ManureManagementPen object.

        Returns
            Total volume of manure deposited in the milking center, liters.

        """

        if self._has_lac_cow_in_pen(pen):
            return self.manure_mass_deposited_in_milking_center(pen) / pen.manure_density
        return 0.0

    @staticmethod
    def _has_lac_cow_in_pen(pen: ManureManagementPen) -> bool:
        """Check if pen has lactating cows.

        Parameters
            pen: A ManureManagementPen object

        Returns
            True if pen has lactating cows, False otherwise.

        """

        return pen.animal_combination is Pen.AnimalCombination.LAC_COW

    @staticmethod
    def _calc_percent_of_day_from_minutes(minutes: float) -> float:
        """Convert minutes to percent of day.

        Parameters
            minutes: Number of minutes.

        Returns
            Percent of day from minutes.

        """

        minutes_in_a_day = 60.0 * 24.0
        return minutes * 100 / minutes_in_a_day
