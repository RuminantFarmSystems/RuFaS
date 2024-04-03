from enum import Enum


class AcceptableUnits(Enum):
    """
    A list of acceptable units used within the RuFaS model.

    """

    UNITLESS: str = "unitless"
    KILOGRAMS: str = "kg"
    SIMULATION_DAY: str = "simulation day"
    ORDINAL_DAYS: str = "ordinal days"
    SIMULATION_YEAR: str = "simulation year"
    CALENDAR_YEAR: str = "calendar year"
    DEGREES_CELSIUS: str = "°C"
    MILLIMETERS: str = "millimeters"
    HOURS: str = "hours"
    MEGAJOULES_PER_SQUARE_METER: str = "MJ/m^2"
    ANIMALS: str = "animals"
    ARTIFICIAL_INSEMINATIONS: str = "AIs"
    CONCEPTIONS: str = "conceptions"
    CONCEPTIONS_PER_SERVICE: str = "conceptions per service"
    COWS: str = "cows"
    KILOGRAMS_PER_DAY: str = "kg/day"
    KILOGRAMS_PER_ANIMAL: str = "kg/animal"
    PERCENT_OF_DRY_MATTER: str = "percent of DM"
    MEGACALORIES: str = "Mcal"
    GRAMS: str = "g"
    MEGACALORIES_PER_KILOGRAM: str = "MCcal"
    PERCENT: str = "percent"
    KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER: str = "kg CO2 / kg DM"
    GRAMS_PER_LITER: str = "g/L"
    GRAMS_PER_DAY: str = "g/day"
    INJECTIONS: str = "injections"
    PREGNANCY_CHECKS: str = "preg checks"
    DAYS: str = "days"
