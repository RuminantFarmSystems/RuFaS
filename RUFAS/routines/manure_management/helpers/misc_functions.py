"""
Collection of miscellaneous helper functions.
"""

from enum import Enum


def format_enum_name(e: Enum, sep='_', joiner=' ', formatter=str.capitalize) -> str:
    """
    Format the name of an enum

    Args:
        e: Any enum type
        sep: The separator used in the enum name
        joiner: The delimiter to be used in the output to separate words in the enum name
        formatter: A function that will be applied to each word in the enum name

    Returns:
        A formatted string for the name of enum argument

    """
    return joiner.join(map(formatter, e.name.split(sep)))
