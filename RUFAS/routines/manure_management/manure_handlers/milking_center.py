from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


# TODO: Move the following function to Utility class
def calc_percent_of_day_from_minutes(minutes: float) -> float:
    minutes_in_a_day = 60.0 * 24.0
    return minutes * 100 / minutes_in_a_day


class MilkingCenter:
    def __init__(self,
                 num_milkings=3,
                 minutes_spent_per_milking=7.0,
                 minutes_spent_in_holding_area=30.0,
                 wash_water_use_rate=20.0,
                 fresh_water_use_rate=10.0):
        self.num_milkings = num_milkings  # milkings/animal/day
        self.minutes_spent_in_holding_area = minutes_spent_in_holding_area  # minutes/holding/animal/day
        self.minutes_spent_per_milking = minutes_spent_per_milking  # minutes/milking/animal/day
        self.wash_water_use_rate = wash_water_use_rate  # liters/animal/day (for holding area)
        self.fresh_water_use_rate = fresh_water_use_rate  # liters/animal/day (for milking)

    # In holding area
    @property
    def total_minutes_spent_in_holding_area(self) -> float:
        return self.num_milkings * self.minutes_spent_in_holding_area

    @property
    def percent_of_day_spent_in_holding(self) -> float:
        return calc_percent_of_day_from_minutes(self.total_minutes_spent_in_holding_area)

    def wash_water_volume_used_in_holding_area(self, pen: SimplePen) -> float:
        return pen.num_animals * self.wash_water_use_rate  # liters

    # Milking
    @property
    def total_minutes_spent_milking(self) -> float:
        return self.num_milkings * self.minutes_spent_per_milking

    @property
    def percent_of_day_spent_milking(self) -> float:
        return calc_percent_of_day_from_minutes(self.total_minutes_spent_milking)

    def fresh_water_volume_used_for_milking(self, pen: SimplePen) -> float:
        return pen.num_animals * self.fresh_water_use_rate  # liters

    # Overall
    @property
    def total_minutes_spent_in_milking_center(self) -> float:
        return self.total_minutes_spent_in_holding_area + self.total_minutes_spent_milking

    @property
    def total_percent_of_day_spent_in_milking_center(self) -> float:
        return self.percent_of_day_spent_in_holding + self.percent_of_day_spent_milking

    def total_water_volume_used_in_milking_center(self, pen: SimplePen) -> float:
        if 'Cow' in pen.classes_in_pen:
            return self.wash_water_volume_used_in_holding_area(pen) + \
                   self.fresh_water_volume_used_for_milking(pen)  # liters
        return 0.0

    def manure_mass_deposited_in_milking_center(self, pen: SimplePen) -> float:
        if 'Cow' in pen.classes_in_pen:
            return pen.manure_mass * self.total_percent_of_day_spent_in_milking_center / 100
        return 0.0

    def manure_volume_deposited_in_milking_center(self, pen: SimplePen) -> float:
        return self.manure_mass_deposited_in_milking_center(pen) / pen.manure_density
