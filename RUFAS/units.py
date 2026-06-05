import re
from enum import Enum, unique


@unique
class MeasurementUnits(Enum):
    """
    A list of acceptable units used within the RuFaS model.

    """

    ANIMALS = "animals"
    ARTIFICIAL_INSEMINATIONS = "AI"
    BYTES = "bytes"
    CALENDAR_YEAR = "calendar year"
    MCAL_PER_MJ = "Mcal/MJ"
    CENTIMETERS = "cm"
    CENTIMETERS_PER_MILLIMETER = "cm/mm"
    CONCEPTIONS = "conception"
    CONCEPTIONS_PER_SERVICE = "conceptions per service"
    COWS = "cows"
    CUBIC_METERS = "m^3"
    CUBIC_METERS_PER_DAY = "m^3/day"
    CUBIC_METERS_PER_KILOGRAM = "m^3/kg"
    CUBIC_METERS_PER_LITER = "m^3/L"
    CUBIC_METERS_PER_CUBIC_MILLIMETER = "m^3/mm^3"
    CUBIC_MILLIMETERS_PER_LITER = "mm^3/L"
    CUBIC_MILLIMETERS_PER_CUBIC_METER = "mm^3/m^3"
    DAYS = "day"
    DAYS_PER_LEAP_YEAR = "day/leap year"
    DAYS_PER_YEAR = "day/year"
    DEGREES_CELSIUS = "°C"
    DRY_KILOGRAMS = "dry kg"
    DRY_KILOGRAMS_PER_HECTARE = "dry kg/ha"
    DOLLARS = "$"
    FRACTION = "fraction"
    GRAMS = "g"
    GRAMS_PER_DAY = "g/day"
    GRAMS_PER_KILOGRAM = "g/kg"
    GRAMS_PER_LITER = "g/L"
    HECTARE = "ha"
    HECTARES_PER_SQUARE_CENTIMETER = "ha/cm^2"
    HECTARES_PER_SQUARE_KILOMETER = "ha/km^2"
    HECTARES_PER_SQUARE_METER = "ha/m^2"
    HECTARES_PER_SQUARE_MILLIMETER = "ha/mm^2"
    HOURS = "hour"
    INJECTIONS = "injection"
    J_PER_K_PER_MOL = "J/K/mol"
    JULIAN_DAY = "julian day"
    KILOMETERS_PER_METER = "km/m"
    KILOGRAMS = "kg"
    KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER = "kg CO2 / kg DM"
    KILOGRAMS_PER_ANIMAL = "kg/animal"
    KILOGRAMS_CARBON_DIOXIDE_EQ = "kg CO2-eq"
    KILOGRAMS_PER_CUBIC_METER = "kg/m^3"
    KILOGRAMS_PER_DAY = "kg/day"
    KILOGRAMS_PER_GRAM = "kg/g"
    KILOGRAMS_PER_HECTARE = "kg/ha"
    KILOGRAMS_PER_LITER = "kg/L"
    KILOGRAMS_PER_MEGAGRAM = "kg/Mg"
    KILOGRAMS_PER_MILLIGRAM = "kg/mg"
    KILOMETERS = "km"
    L_ATM_PER_MOL_K = "L atm/mol/K"
    LITERS = "L"
    LITERS_PER_CUBIC_METER = "L/m^3"
    LITERS_PER_CUBIC_MILLIMETER = "L/mm^3"
    LITERS_PER_TON = "L/ton"
    LITERS_PER_HA = "L/ha"
    LITERS_PER_KILOWATTS_PER_HOUR = "L/kWhr"
    MEGACALORIES = "Mcal"
    MEGACALORIES_PER_KILOGRAM = "Mcal/kg"
    MEGAGRAMS_PER_KILOGRAM = "Mg/kg"
    MEGAJOULES = "MJ"
    MEGAJOULES_PER_CUBIC_METER = "MJ/m^3"
    MEGAJOULES_PER_SQUARE_METER = "MJ/m^2"
    METERS = "m"
    METERS_PER_KILOMETER = "m/km"
    METERS_PER_MILLIMETER = "m/mm"
    METRIC_TONS = "metric ton"
    MILLIGRAMS_PER_KILOGRAM = "mg/kg"
    MILLIMETERS = "mm"
    MILLIMETERS_PER_CENTIMETER = "mm/cm"
    MILLIMETERS_PER_HECTARE = "mm/ha"
    MJ_CH4_PER_G_CH4 = "MJ/g"
    ORDINAL_DAY = "ordinal day"
    PERCENT = "percent"
    PERCENT_OF_DRY_MATTER = "percent of DM"
    PREGNANCY_CHECKS = "preg check"
    RADIANS_PER_HOUR = "rad/h"
    SECONDS = "s"
    SECONDS_PER_DAY = "s/day"
    HOURS_PER_DAY = "h/day"
    SIMULATION_DAY = "simulation day"
    SIMULATION_YEAR = "simulation year"
    SQUARE_CENTIMETERS_PER_HECTARE = "cm^2/ha"
    SQUARE_KILOMETERS_PER_HECTARE = "km^2/ha"
    SQUARE_METERS_PER_HECTARE = "m^2/ha"
    SQUARE_METERS = "m^2"
    SQUARE_MILLIMETERS_PER_HECTARE = "mm^2/ha"
    UNITLESS = "unitless"
    WET_KILOGRAMS_PER_HECTARE = "wet kg/ha"

    def __str__(self) -> str:
        """
        Returns the value of the enum member as its string representation.
        """

        return self.value

    @staticmethod
    def _parse_unit(unit: str) -> dict[str, int]:
        """Parses a unit string to handle units with exponents.

        Parameters
        ----------
        unit : str
            A string representing measurement units.

        Returns
        -------
        dict
            A dictionary where the keys are unit names (str) and the values are their exponents (int).
        """
        unit_dict = {}
        for part in unit.split("*"):
            if "^" in part:
                u, exp = part.split("^")
                unit_dict[u.strip()] = int(exp)
            else:
                unit_dict[part.strip()] = 1
        return unit_dict

    @staticmethod
    def extract_units(key: str) -> tuple[dict[str, int], dict[str, int]]:
        """Extracts the units from a key.

        Parameters
        ----------
        key : str
            The key from which the units are extracted.

        Returns
        -------
        tuple[dict, dict]
            A tuple of the numerator and denominator units. If there is no denominator, the first element of tuple will
            have the units and the second will be an empty string. If no units are found, it will return a tuple with
            two empty strings.
        """
        match = re.search(r"\((.*?)\)", key)
        if match:
            units = match.group(1)
            if "/" in units:
                numerator, denominator = units.split("/")
                numerator_units = MeasurementUnits._parse_unit(numerator)
                denominator_units = MeasurementUnits._parse_unit(denominator)
                return numerator_units, denominator_units
            else:
                numerator_units = MeasurementUnits._parse_unit(units)
                return numerator_units, {}
        else:
            return {}, {}

    @staticmethod
    def adjust_unit_exponents(units1: dict[str, int], units2: dict[str, int]) -> dict[str, int]:
        """Combines two unit dictionaries by adding or subtracting their exponents.

        Parameters
        ----------
        units1 : dict[str, int]
            A dictionary representing the first set of units with keys as unit names and values as exponents.
        units2 : dict[str, int]
            A dictionary representing the second set of units with keys as unit names and values as exponents.

        Returns
        -------
        dict[str, int]
            The combined units dictionary.
        """
        result_units = units1.copy()
        for unit, exponent in units2.items():
            if unit == "unitless" or unit == "1":
                continue
            if unit in result_units:
                result_units[unit] += exponent
            else:
                result_units[unit] = exponent
        return {unit: exp for unit, exp in result_units.items() if exp != 0}

    @staticmethod
    def simplify_units(numerator: dict[str, int], denominator: dict[str, int]) -> tuple[dict[str, int], dict[str, int]]:
        """
        Simplify the units by cancelling out common units in the numerator and denominator.

        Parameters
        ----------
        numerator : dict[str, int]
            A dictionary representing the units in the numerator with keys as unit names and values as exponents.
        denominator : dict[str, int]
            A dictionary representing the units in the denominator with keys as unit names and values as exponents.

        Returns
        -------
        tuple[dict[str, int], dict[str, int]]
            A tuple containing two dictionaries:
            - The first dictionary represents the simplified numerator units with non-zero exponents.
            - The second dictionary represents the simplified denominator units with non-zero exponents.
        """
        combined_numerator = numerator.copy()
        combined_denominator = denominator.copy()

        for unit in list(combined_numerator.keys()):
            if unit in combined_denominator:
                new_exponent = combined_numerator[unit] - combined_denominator[unit]
                if new_exponent == 0:
                    del combined_numerator[unit]
                    del combined_denominator[unit]
                else:
                    combined_numerator[unit] = new_exponent
                    del combined_denominator[unit]

        return combined_numerator, combined_denominator

    @staticmethod
    def units_to_string(numerator: dict[str, int], denominator: dict[str, int]) -> str:
        """
        Converts two dictionaries of units (numerator and denominator) back to a single string format.

        Parameters
        ----------
        numerator : dict
            A dictionary where the keys are unit names (str) and the values are their exponents (int) for the numerator.
        denominator : dict
            A dictionary where the keys are unit names (str) and the values are their exponents (int) for the
            denominator.

        Returns
        -------
        str
            A string representing the units.
        """
        numerator_units = []
        denominator_units = []

        for unit, exponent in numerator.items():
            if unit == "unitless":
                continue
            if exponent == 1:
                numerator_units.append(unit)
            else:
                numerator_units.append(f"{unit}^{exponent}")

        for unit, exponent in denominator.items():
            if unit == "unitless":
                continue
            if exponent == 1:
                denominator_units.append(unit)
            else:
                denominator_units.append(f"{unit}^{exponent}")

        numerator_str = "*".join(numerator_units)
        denominator_str = "*".join(denominator_units)

        if numerator_str and denominator_str:
            return f"{numerator_str}/{denominator_str}"
        elif numerator_str:
            return numerator_str
        elif denominator_str:
            return f"1/{denominator_str}"
        else:
            return "unitless"
