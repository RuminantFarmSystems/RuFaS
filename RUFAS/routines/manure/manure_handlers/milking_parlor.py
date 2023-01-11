from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.constants.manure_constants import ManureConstants

om = OutputManager()


class MilkingParlor:
    """A class that calculates the time spent and water usage in the milking parlor by cows.

    Note that only lactating cows are considered in this class.

    Attributes
        num_milkings: Number of milkings per animal per day.
        minutes_spent_per_milking: Number of minutes spent per milking per animal.
        minutes_spent_in_holding_area: Number of minutes spent in holding area per animal per milking.
        wash_water_use_rate: Wash water use rate in the holding area, liters/animal/day.
        fresh_water_use_rate: Fresh water use rate for milking, liters/animal/day.

    """

    def __init__(self,
                 num_milkings=3,
                 minutes_spent_in_holding_area=30.0,
                 minutes_spent_per_milking=7.0,
                 wash_water_use_rate=20.0,
                 fresh_water_use_rate=10.0):
        """Initialize the milking parlor.

        Parameters
            num_milkings: Number of milkings per animal per day.
            minutes_spent_per_milking: Number of minutes spent per milking per animal.
            minutes_spent_in_holding_area: Number of minutes spent in holding area per animal per day.
            wash_water_use_rate: Wash water use rate in the holding area, liters/animal/day.
            fresh_water_use_rate: Fresh water use rate for milking, liters/animal/day.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.__init__.__name__,
                    "num_milkings": num_milkings,
                    "minutes_spent_in_holding_area": minutes_spent_in_holding_area,
                    "minutes_spent_per_milking": minutes_spent_per_milking,
                    "wash_water_use_rate": wash_water_use_rate,
                    }

        self.num_milkings = num_milkings
        self.minutes_spent_in_holding_area = minutes_spent_in_holding_area
        self.minutes_spent_per_milking = minutes_spent_per_milking
        self.wash_water_use_rate = wash_water_use_rate
        self.fresh_water_use_rate = fresh_water_use_rate

        om.add_variable("fresh_water_use_rate",
                        self.fresh_water_use_rate, info_map)

    # In holding area

    @property
    def total_minutes_spent_in_holding_area(self) -> float:
        """Total number of minutes spent in holding area per animal per day.

        Returns
            Total number of minutes spent in holding area per animal per day.

        """
        info_map = {"class": self.__class__.__name__}

        total_minutes_spent_in_holding_area = self.num_milkings * \
            self.minutes_spent_in_holding_area

        om.add_variable("total_minutes_spent_in_holding_area",
                        total_minutes_spent_in_holding_area, info_map)
        return total_minutes_spent_in_holding_area

    @property
    def fraction_of_day_spent_in_holding_area(self) -> float:
        """Returns fraction of day spent in holding area.

        Returns:
            Fraction of day spent in holding area.

        """
        info_map = {"class": self.__class__.__name__}
        fraction_of_day_spent_in_holding_area = self._calc_fraction_of_day_from_minutes(
            self.fraction_of_day_spent_in_holding_area)

        om.add_variable("fraction_of_day_spent_in_holding_area",
                        fraction_of_day_spent_in_holding_area, info_map)

        return fraction_of_day_spent_in_holding_area

    def calc_wash_water_volume_used_in_holding_area(self, num_cows: int) -> float:
        """Calculates the volume of wash water used in holding area.

        Args:
            num_cows: Number of cows in the pen.

        Returns:
            Volume of wash water used in holding area, liters.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_wash_water_volume_used_in_holding_area.__name__}
        wash_water_volume_used_in_holding_area = num_cows * self.wash_water_use_rate

        om.add_variable("wash_water_volume_used_in_holding_area",
                        wash_water_volume_used_in_holding_area, info_map)

        return wash_water_volume_used_in_holding_area

    # Milking

    @property
    def total_minutes_spent_milking(self) -> float:
        """Total number of minutes spent milking per animal per day.

        Returns
            Total number of minutes spent milking per animal per day.

        """
        info_map = {"class": self.__class__.__name__}
        total_minutes_spent_milking = self.num_milkings * \
            self.minutes_spent_per_milking

        om.add_variable("total_minutes_spent_milking",
                        total_minutes_spent_milking, info_map)

        return total_minutes_spent_milking

    @property
    def fraction_of_day_spent_milking(self) -> float:
        """Returns fraction of day spent milking.

        Returns:
            Fraction of day spent milking.

        """
        info_map = {"class": self.__class__.__name__}
        fraction_of_day_spent_milking = self._calc_fraction_of_day_from_minutes(
            self.fraction_of_day_spent_milking)

        om.add_variable("fraction_of_day_spent_milking",
                        fraction_of_day_spent_milking, info_map)

        return fraction_of_day_spent_milking

    def calc_fresh_water_volume_used_for_milking(self, num_cows: int) -> float:
        """Returns volume of fresh water used for milking.

        Args:
            num_cows: Number of cows in the pen.

        Returns:
            Volume of fresh water used for milking, liters.

        """
        return num_cows * self.fresh_water_use_rate

    # Overall
    @property
    def total_minutes_spent_in_milking_parlor(self) -> float:
        """Total number of minutes spent in the milking parlor per animal per day.

        Note that this includes both the time spent in the holding area
        and the time spent milking.

        Returns
            Total number of minutes spent in the milking parlor per animal per day.

        """
        info_map = {"class": self.__class__.__name__}
        total_minutes_spent_in_milking_parlor = self.total_minutes_spent_in_holding_area + \
            self.total_minutes_spent_milking

        om.add_variable("total_minutes_spent_in_milking_parlor",
                        total_minutes_spent_in_milking_parlor, info_map)

        return total_minutes_spent_in_milking_parlor

    @property
    def total_fraction_of_day_spent_in_milking_parlor(self) -> float:
        """Returns total fraction of day spent in the milking parlor per animal.

        Returns:
            Total fraction of day spent in the milking parlor per animal.

        """
        info_map = {"class": self.__class__.__name__}
        total_fraction_of_day_spent_in_milking_parlor = self.fraction_of_day_spent_in_holding_area + \
            self.fraction_of_day_spent_milking

        om.add_variable("total_fraction_of_day_spent_in_milking_parlor",
                        total_fraction_of_day_spent_in_milking_parlor, info_map)

        return total_fraction_of_day_spent_in_milking_parlor

    def calc_total_water_volume_used_in_milking_parlor(self, num_cows: int) -> float:
        """Calculates total volume of water used in the milking parlor.

        Args:
            num_cows: Number of cows in the pen.

        Returns:
            Total volume of water used in the milking parlor, L.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_total_water_volume_used_in_milking_parlor.__name__}
        total_water_volume_used_in_milking_parlor = (self.calc_wash_water_volume_used_in_holding_area(num_cows) +
                                                     self.calc_fresh_water_volume_used_for_milking(num_cows))

        om.add_variable("total_water_volume_used_in_milking_parlor",
                        total_water_volume_used_in_milking_parlor, info_map)

        return total_water_volume_used_in_milking_parlor

    def calc_manure_mass_deposited_in_milking_parlor(self, num_cows: int, manure_mass: float) -> float:
        """Calculates total mass of manure deposited in the milking parlor by all cows in pen.

        Args:
            num_cows: Number of cows in the pen.
            manure_mass: Manure mass in the pen, kg.

        Returns
            Total mass of manure deposited in the milking parlor, kg.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_manure_mass_deposited_in_milking_parlor.__name__}
        manure_mass_deposited_in_milking_parlor = manure_mass * \
            self.total_fraction_of_day_spent_in_milking_parlor if num_cows > 0 else 0.0

        om.add_variable("manure_mass_deposited_in_milking_parlor",
                        manure_mass_deposited_in_milking_parlor, info_map)

        return manure_mass_deposited_in_milking_parlor

    def calc_manure_volume_deposited_in_milking_parlor(self, num_cows: int, manure_mass: float) -> float:
        """Calculates total volume of manure deposited in the milking parlor.

        Args:
            num_cows: Number of cows in the pen.
            manure_mass: Manure mass in the pen, kg.

        Returns:
            Total volume of manure deposited in the milking parlor, m^3.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_manure_volume_deposited_in_milking_parlor.__name__}
        manure_volume_deposited_in_milking_parlor = self.calc_manure_mass_deposited_in_milking_parlor(
            num_cows, manure_mass) / ManureConstants.MANURE_DENSITY

        om.add_variable("manure_volume_deposited_in_milking_parlor",
                        manure_volume_deposited_in_milking_parlor, info_map)

        return manure_volume_deposited_in_milking_parlor

    @classmethod
    def _calc_fraction_of_day_from_minutes(cls, minutes: float) -> float:
        """Converts minutes to fraction of day.

        Args:
            minutes: Number of minutes.

        Returns:
            Fraction of day from minutes.

        """
        info_map = {"class": cls.__name__,
                    "function": cls._calc_fraction_of_day_from_minutes.__name__}

        minutes_in_a_day = 60.0 * 24.0
        minutes_of_a_day_frac = minutes / minutes_in_a_day

        om.add_variable("minutes_of_a_day_frac",
                        minutes_of_a_day_frac, info_map)

        return minutes_of_a_day_frac
