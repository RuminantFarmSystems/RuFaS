def convert_minutes_to_hours(minutes: float) -> float:
    return minutes / 60.0


def calc_percent_of_day_from_minutes(minutes: float) -> float:
    minutes_in_a_day = 60.0 * 24.0
    return minutes * 100 / minutes_in_a_day


class MilkingCenter:
    wash_water_use_rate = 20.0  # liters/animal/day (for holding area)
    fresh_water_use_rate = 10.0  # liters/animal/day (for milking)

    def __init__(self,
                 num_milkings: int = 3,
                 minutes_spent_per_milking: float = 7.0,
                 minutes_spent_in_holding_area: float = 30.0):
        self.num_milkings = num_milkings  # milkings/animal/day
        self.minutes_spent_in_holding_area = minutes_spent_in_holding_area  # minutes/holding/animal/day
        self.minutes_spent_per_milking = minutes_spent_per_milking  # minutes/milking/animal/day

    # In holding area
    @property
    def total_minutes_spent_in_holding_area(self) -> float:
        return self.num_milkings * self.minutes_spent_in_holding_area

    @property
    def total_hours_spent_in_holding_area(self) -> float:
        return convert_minutes_to_hours(self.total_minutes_spent_in_holding_area)

    @property
    def percent_of_day_spent_in_holding(self) -> float:
        return calc_percent_of_day_from_minutes(self.total_minutes_spent_in_holding_area)

    # Milking
    @property
    def total_minutes_spent_milking(self) -> float:
        return self.num_milkings * self.minutes_spent_per_milking

    @property
    def total_hours_spent_milking(self) -> float:
        return convert_minutes_to_hours(self.total_minutes_spent_milking)

    @property
    def percent_of_day_spent_milking(self) -> float:
        return calc_percent_of_day_from_minutes(self.total_minutes_spent_milking)

    # Overall
    @property
    def total_minutes_spent_in_milking_center(self) -> float:
        return self.total_minutes_spent_in_holding_area + self.total_minutes_spent_milking

    @property
    def total_hours_spent_in_milking_center(self) -> float:
        return convert_minutes_to_hours(self.total_minutes_spent_in_milking_center)

    @property
    def total_percent_of_day_spent_in_milking_center(self) -> float:
        return self.percent_of_day_spent_in_holding + self.percent_of_day_spent_milking
