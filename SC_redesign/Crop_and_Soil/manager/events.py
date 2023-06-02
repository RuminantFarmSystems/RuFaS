from typing import List
from copy import deepcopy


from RUFAS.classes import Time

"""This module defines the various Event classes and helper functions

Events are simple classes that will facilitate scheduling of different management operations. At their core, they
are simply pairs of attributes (`year` and `day`), indicating when particular operations should occur. Children of
the main `Event` class can extend the functionality by adding additional attributes specific to the type of management
operation. For example, the `HarvestEvent` contains the `operation` attribute, which specifies which specific harvest
method will be used when harvesting a crop, and a `crop_reference` attribute, which specifies which crop that is
presently growing in a field will be harvested.
"""


class Event:
    def __init__(self, year: int = 1, day: int = 120):
        """Creates a new Event instance.

        An Event object determines when an event should occur, relative to the start of the RuFaS simulation.
        An event can specify when a crop is planted or harvested, when a manure/fertilizer amendment should occur.

        Parameters
        ----------
        year : int, default=1
            Year of the simulation on which the event should occur
        day : int, default=120
            (julian) day of the year on which the event should occur

        Returns
        -------
        event : Event
            an Event instance
        """
        self.year = year
        self.day = day

    def __eq__(self, other):
        """Overrides the equality operator for Event objects."""
        correct_type = isinstance(other, Event)
        equal_fields = other.year == self.year and other.day == self.day
        return correct_type and equal_fields

    def occurs_today(self, time: Time) -> bool:
        """
        Checks if the event occurs on the current day.

        Parameters
        ----------
        time : Time
            Time object that contains the current day.

        Returns
        -------
        bool
            True if event occurs on the current day, false if not.

        """
        return self.year == time.year and self.day == time.day

    @staticmethod
    def repeat_pattern(pattern: List[int], skip: int = 0, repeat: int = 0) -> List[int]:
        """
        Takes a pattern of numbers and repeats it a specified number of times, skipping over specified gaps between
        repetitions.

        Parameters
        ----------
        pattern : List[int]
            The pattern to be repeated.
        skip : int
            Number of steps to skip between repeats.
        repeat : int
            Number of times patter should be repeated.

        Returns
        -------
        List[int]
            The full repeated pattern of numbers.

        Raises
        ------
        ValueError
            If the skip is less than 0.
        ValueError
            If the number of times to repeat is less than 0.
        ValueError
            If the values in the pattern descend.

        Examples
        --------
        >>> repeat_pattern([1, 3, 5], 1, 2)
        [1, 3, 5, 7, 9, 11, 13, 15, 17]

        >>> repeat_pattern([1, 3, 5], 0, 1)
        [1, 3, 5, 6, 8, 10]

        >>> repeat_pattern([2, 3, 7], 3, 2)
        [2, 3, 7, 11, 12, 16, 20, 21, 24]

        """
        if skip < 0:
            raise ValueError(f"Expected skip to be >= 0, received '{skip}'.")
        if repeat < 0:
            raise ValueError(f"Expected repeat to be >= 0, received '{repeat}'.")

        differences = [skip + 1]
        in_pattern_differences = range(1, len(pattern[1:]) + 1)
        for difference in in_pattern_differences:
            if pattern[difference] < pattern[difference - 1]:
                raise ValueError(f"Values in pattern cannot be descending, received '{pattern}'.")
            differences.append(pattern[difference] - pattern[difference - 1])

        full_pattern = deepcopy(pattern)
        differences_index = 0
        number_of_new_values = range(repeat * len(pattern))
        for _new_value in number_of_new_values:
            full_pattern.append(full_pattern[-1] + differences[differences_index])
            differences_index += 1
            differences_index %= len(pattern)
        return full_pattern


class PlantingEvent(Event):
    def __init__(self, crop_reference: str, year: int = 1, day: int = 120, heat_scheduled_harvest: bool = False):
        """
        Initializes a Planting Event, which dictates when a crop will be planted and tells the plant how it will
        eventually be harvested.

        Parameters
        ----------
        crop_reference : str
            Name of the crop to be planted in the ground.
        heat_scheduled_harvest : bool, default=False
            Flag indicating if the crop will be harvested when it has a certain amount of heat units.

        """
        super().__init__(year=year, day=day)
        self.crop_reference = crop_reference
        self.use_heat_scheduled_harvest = heat_scheduled_harvest


class HarvestEvent(Event):
    def __init__(self, crop_reference: str, year: int = 1, day: int = 240, operation: str = "default"):
        """Creates a new HarvestEvent instance, which is a child of the Event class.

        A HarvestEvent object determines when (and how) a harvest operation should occur for a crop.

        Parameters
        ----------
        crop_reference : str
            Name of the crop to be harvested.
        operation : str, default="default"
            the name of an accepted harvest operation (see HarvestOperation)

        """
        super().__init__(year=year, day=day)
        self.crop_reference = crop_reference
        self.operation = operation


class TillageEvent(Event):
    def __init__(self, tillage_depth: float, incorporation_fraction: float, mixing_fraction: float, year: int = 1,
                 day: int = 160):
        """
        Creates a new TillageEvent instance, which defines a tillage application to be applied on a specific day of a
        year.

        Parameters
        ----------
        tillage_depth : float
            The lowest depth the tilling implement reaches (mm)
        incorporation_fraction : float
            Fraction of soil surface pool incorporated into the soil profile (unitless)
        mixing_fraction : float
            Fraction of pool in each layer mixed and redistributed back into the soil profile (unitless)

        """
        super().__init__(year=year, day=day)
        self.tillage_depth = tillage_depth
        self.incorporation_fraction = incorporation_fraction
        self.mixing_fraction = mixing_fraction
