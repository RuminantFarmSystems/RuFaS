from typing import List

from RUFAS.classes import Time

"""This module defines the various Event classes and helper functions

Events are simple classes that will facilitate scheduling of different management operations. At their core, they
are simply pairs of attributes (`year` and `day`), indicating when particular operations should occur. Children of
the main `Event` class can extend the functionality by adding additional attributes specific to the type of management
operation. For example, the `HarvestEvent` contains the `operation` attribute, which specifies which specific harvest
method will be used when harvesting a crop. By contrast no `PlantingEvent` class needs to occur, since there are no
additional specifications required to plant a crop beyond `year` and `day`
"""


class Event:
    def __init__(self, year=0, day=120):
        """Creates a new Event instance

        an Event object determines when an event should occur, relative to the start of the RuFaS simulation.
        An event can specify when a crop is planted or harvested, when a manure/fertilizer amendment should occur

        Parameters
        ----------
        year : int
            years after the start of the simulation on which the event should occur
        day : int
            (julian) day of the year on which the event should occur

        Returns
        -------
        event : Event
            an Event instance
        """
        self.year = year
        self.day = day

    def occurs_today(self, time: Time) -> bool:
        """returns true if the event should take place today, false otherwise"""
        years_since_start = (time.year - 1)
        return self.year == years_since_start and self.day == time.day

    def project_next(self, years: int = 1, days: int = 0):  # Pycharm dislikes the return type hint
        """creates the next Event in the sequence, projected forward by `years` and `days`

        Parameters
        ----------
        years : int
            the number of years to add to this instance's `year` attribute
        days : int
            the number of days to add to this instance's `day` attribute

        Returns
        -------
        next : Event
            the next Event, with days and years incremented as appropriate

        Raises
        ------
        Exception
            if days > 366
        """
        if days > 366:
            raise Exception("days must not be greater than total number of days in a year")
        return Event(self.year + years, self.day + days)

    @staticmethod
    def project_sequence(start: int | List[int] = 0, repeat: int = 0, skip: int = 0, cycles: int = 1) -> List[int]:
        """Generates a sequence of integers from a starting point, based on pattern rules. This method was created with
        temporal sequences specifically in mind.

        Parameters
        ----------
        start : int | list[int], default: 0
            the starting point of the sequence: either a single number or a sequence of number that will be projected
            forward. If multiple values are given, it is expected that the values are in ascending order; other formats
            may yield unexpected behavior.
        repeat : int, default: 0
            the number of times `start` should be repeated sequentially within a cycle
        skip : int, default: 0
            the number of steps to skip between cycles (if applicable)
        cycles : int, default: 1
            the number of cycles in the final sequence

        Returns
        -------
        seq : list[int]
            the resulting sequence.

        Raises
        ------
        Exception
            if repeat is negative
        Exception
            if cycles is negative

        Examples
        --------
        >>> project_sequence(start=0, repeat=1, skip=1, cycles=3)
        [0, 1, 3, 4, 6, 7]

        >>> project_sequence(start=[1, 2, 4], skip=1, cycles=3)
        [1, 2, 4, 6, 7, 9, 11, 12, 14]

        >>> project_sequence(start=[1, 2, 4], repeat=1, skip=2, cycles=3)
        [1, 2, 4, 5, 6, 8, 11, 12, 14, 15, 16, 18, 21, 22, 24, 25, 26, 28]

        >>> project_sequence(start=1, cycles=10)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        Equivalently:

        >>> project_sequence(start=[1, 2, 3, 4, 5], repeat=1)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        Equivalently:

        >>> project_sequence(start=[1, 2, 3, 4, 5], cycles=2)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        >>> project_sequence(start=1, repeat=3, skip=3, cycles=4)
        [1, 2, 3, 4, 8, 9, 10, 11, 15, 16, 17, 18, 22, 23, 24, 25]

        Equivalently:

        >>> project_sequence(start=[1, 2, 3, 4], skip=3, cycles=4)
        [1, 2, 3, 4, 8, 9, 10, 11, 15, 16, 17, 18, 22, 23, 24, 25]

        Notes
        -----
        Unlike `repeat` and `cycles`, `skip` can be negative, but the behaviour may not be as expected.
        """
        if repeat < 0:
            raise Exception("repeat must not be negative")
        if cycles < 0:
            raise Exception("cycles must not be negative")

        if type(start) is int:
            start = [start]
            span = 0
        else:
            span = max(start) - min(start)

        increment = span + 1
        pattern_base = start.copy()
        if repeat > 0:
            for i in range(repeat):
                replicate = i + 1
                pattern_base += [val + (increment * replicate) for val in start]
            span = max(pattern_base) - min(pattern_base)

        out_list = pattern_base.copy()
        for j in range(cycles - 1):
            cycle = j + 1
            out_list += [val + (cycle * span) + (cycle * (skip + 1)) for val in pattern_base]

        return out_list


class HarvestEvent(Event):
    def __init__(self, year: int = 0, day: int = 120, operation: str = "default"):
        """Creates a new HarvestEvent instance, which is a child of the Event class

        a HarvestEvent object determines when (and how) a harvest operation should occur for a crop.

        Parameters
        ----------
        operation : str
            the name of an accepted harvest operation (see HarvestOperation)

        Returns
        -------
        harvest_event : HarvestEvent
            a HarvestEvent instance
        """
        super().__init__(year=year, day=day)
        self.operation = operation
