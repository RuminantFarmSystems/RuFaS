"""
Description:
    These constants are globals that should be used for unit conversion.

Details:
    Please follow the proceeding best practices:
        1. Write names of constants in all caps, with words separated by underscores.
        2. Use the full name of units, not abbreviations. This avoids confusion in cases where case matters (for
            example, megagrams (Mg) and milligrams (mg).)
        3. For conversion constants, include the value for the reverse conversion direction. The reverse direction
            value should be expressed as 1 divided the non-reverse direction value.
        4. The non-reverse conversion direction value should be greater than one.
"""
# Area
HECTARES_TO_SQUARE_MILLIMETERS = 10_000_000_000
SQUARE_MILLIMETERS_TO_HECTARES = 1 / HECTARES_TO_SQUARE_MILLIMETERS
HECTARES_TO_SQUARE_CENTIMETERS = 100_000_000
SQUARE_CENTIMETERS_TO_HECTARES = 1 / HECTARES_TO_SQUARE_CENTIMETERS

# Volume
LITERS_TO_CUBIC_MILLIMETERS = 1_000_000
CUBIC_MILLIMETERS_TO_LITERS = 1 / LITERS_TO_CUBIC_MILLIMETERS
CUBIC_METERS_TO_CUBIC_MILLIMETERS = 1_000_000_000
CUBIC_MILLIMETERS_TO_CUBIC_METERS = 1 / CUBIC_METERS_TO_CUBIC_MILLIMETERS

# Mass
KILOGRAMS_TO_MILLIGRAMS = 1_000_000
MILLIGRAMS_TO_KILOGRAMS = 1 / KILOGRAMS_TO_MILLIGRAMS
KILOGRAMS_TO_GRAMS = 1_000
GRAMS_TO_KILOGRAMS = 1 / KILOGRAMS_TO_GRAMS
KILOGRAMS_TO_MEGAGRAMS = 1_000
MEGAGRAMS_TO_KILOGRAMS = 1 / KILOGRAMS_TO_MEGAGRAMS

# Length
CENTIMETERS_TO_MILLIMETERS = 10
MILLIMETERS_TO_CENTIMETERS = 1 / CENTIMETERS_TO_MILLIMETERS
