from enum import Enum, unique


@unique
class MeasurementUnits(Enum):
    """
    A list of acceptable units used within the RuFaS model.

    """

    ANIMALS = "animals"
    ARTIFICIAL_INSEMINATIONS = "AIs"
    CALENDAR_YEAR = "calendar year"
    CONCEPTIONS = "conceptions"
    CONCEPTIONS_PER_SERVICE = "conceptions per service"
    COWS = "cows"
    CUBIC_METERS = "m^3"
    CUBIC_METERS_PER_DAY = "m^3/day"
    DAYS = "days"
    DEGREES_CELSIUS = "°C"
    DRY_KILOGRAMS = "dry kg"
    DRY_KILOGRAMS_PER_HECTARE = "dry kg/ha"
    FRACTION = "fraction"
    GRAMS = "g"
    GRAMS_PER_DAY = "g/day"
    GRAMS_PER_LITER = "g/L"
    HECTARE = "ha"
    HOURS = "hours"
    INJECTIONS = "injections"
    KILOGRAMS = "kg"
    KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER = "kg CO2 / kg DM"
    KILOGRAMS_PER_ANIMAL = "kg/animal"
    KILOGRAMS_PER_DAY = "kg/day"
    KILOGRAMS_PER_HECTARE = "kg/ha"
    MEGACALORIES = "Mcal"
    MEGACALORIES_PER_KILOGRAM = "Mcal/kg"
    MEGAJOULES = "MJ"
    MEGAJOULES_PER_CUBIC_METER = "MJ/m^3"
    MEGAJOULES_PER_SQUARE_METER = "MJ/m^2"
    METERS = "m"
    METRIC_TONS = "metric tons"
    MILLIMETERS = "mm"
    MILLIMETERS_PER_HECTARE = "mm/ha"
    ORDINAL_DAY = "ordinal day"
    PERCENT = "percent"
    PERCENT_OF_DRY_MATTER = "percent of DM"
    PREGNANCY_CHECKS = "preg checks"
    SIMULATION_DAY = "simulation day"
    SIMULATION_YEAR = "simulation year"
    UNITLESS = "unitless"
    WET_KILOGRAMS_PER_HECTARE = "wet kg/ha"
    KILOGRAMS_CARBON_DIOXIDE_EQ = "kg CO2-eq"

    def __str__(self) -> str:
        """
        Returns the value of the enum member as its string representation.
        """

        return self.value
