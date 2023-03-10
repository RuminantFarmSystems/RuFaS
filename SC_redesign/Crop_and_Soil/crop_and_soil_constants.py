"""
Description:
    These constants are globals that should be used for unit conversion.
Details:
    Please follow the proceeding best practices:
        1. Write names of constants in all caps, with words separated by underscores.
        2. Use the full name of units, not abbreviations. This avoids confusion in cases where case matters (for
            example, megagrams (Mg) and milligrams (mg).)
        3. For conversion constants, do not include the value for reverse conversion directions.
            To convert in the opposite direction, simply divide instead of multiply.
        4. Prefer constants that are greater than one.
"""
# Area
HECTARES_TO_SQUARE_MILLIMETERS = 10_000_000_000

# Volume
LITERS_TO_CUBIC_MILLIMETERS = 1_000_000

# Mass
KILOGRAMS_TO_MILLIGRAMS = 1_000_000
