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
        hash_value = self.__hash__()
        other_hash_value = other.__hash__()
        equal_hash_values = hash_value == other_hash_value
        return correct_type and equal_hash_values

    def __hash__(self):
        """Overrides the hash method for Event objects."""
        str_representation = str(self.year) + str(self.day)
        return hash(str_representation)

    def occurs_today(self, time: Time) -> bool:
        """
        Checks if the event occurs on the current day in the current year..

        Parameters
        ----------
        time : Time
            Time object that contains the current day and year.

        Returns
        -------
        bool
            True if event occurs on the current day and year, false if not.

        """
        return self.year == time.calendar_year and self.day == time.day


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


class ManureEvent(Event):
    def __init__(self, year: int, day: int, nitrogen_mass: float, phosphorus_mass: float, field_coverage: float,
                 application_depth: float, surface_remainder_fraction: float):
        """
        Creates a new ManureEvent instance, which defines how manure much manure such be requested and applied to a
        field.

        Parameters
        ----------
        year : int
            Year in which this manure application occurs.
        day : int
            Day in which this manure application occurs.
        nitrogen_mass : float
            Minimum mass of nitrogen that should be contained in this manure application (kg)
        phosphorus_mass : float
            Minimum mass of phosphorus that should be contained in this manure application (kg)
        field_coverage : float
            Fraction of the field covered by this manure application (unitless)
        application_depth : float
            Depth that manure is injected into the soil at (mm)
        surface_remainder_fraction
            Fraction of manure applied that remains on the soil surface (unitless)

        """
        super().__init__(year=year, day=day)
        self.nitrogen_mass = nitrogen_mass
        self.phosphorus_mass = phosphorus_mass
        self.field_coverage = field_coverage
        self.application_depth = application_depth
        self.surface_remainder_fraction = surface_remainder_fraction
