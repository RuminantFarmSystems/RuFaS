class AnimalEvents:
    """
    A class to represent animal events in a farm simulation.

    This class tracks the events related to animals including birth and other significant
    occurrences.

    Attributes
    ----------
    events : dict[int, list[str]]
        A dictionary containing the events indexed by the animal's age in days. The values
        are lists of descriptions for the events on that day.
    """

    def __init__(self) -> None:
        """
        Initialize a new AnimalEvents object.
        """
        self.events: dict[int, list[str]] = {}

    def init_from_string(self, events_str: str) -> None:
        """
        Initialize event from a string

        Args:
                events_str: string representation of events
        """
        split_by_date = list(
            filter(
                lambda x: x != "",
                list(map(lambda x: x.strip(), events_str.lower().split("days born "))),
            )
        )

        for day in split_by_date:
            split = day.split(": ")
            date = int(split[0])
            events = list(filter(lambda x: (x != "[" and x != "]" and x != ", "), split[1].split("'")))
            for event in events:
                self.add_event(date, 0, event)

    def add_event(self, animal_age: int, simulation_day: int, description: str) -> None:
        """
        Add a cow life event

        Args:
                animal_age: the date counter for the cow (from birth)
                simulation_day: day in the simulation
                description: the event happened on that day
        """
        if animal_age in self.events:
            self.events[animal_age].append(description)
        else:
            if simulation_day == 0:
                self.events[animal_age] = [description]
            else:
                self.events[animal_age] = [
                    "simulation_day=" + str(simulation_day),
                    description,
                ]

    def __str__(self) -> str:
        res_str = ""
        for key, value in sorted(self.events.items()):
            res_str += "\tdays born {}: {} \n".format(key, value)

        return res_str

    def get_most_recent_date(self, event_description: str) -> int:
        """
        Return the most recent age at which the event_description happened

        Parameters
        ----------
        event_description : str
            The description of the event to search for.

        Returns
        -------
        int
            The most recent age at which the event_description happened, -1 if not found.
        """

        dates = list(self.events.keys())
        for i in range(-1, -len(dates) - 1, -1):
            if event_description in self.events[dates[i]]:
                return dates[i]
        return -1

    def __add__(self, other: "AnimalEvents") -> "AnimalEvents":
        """Method for adding two AnimalEvents objects."""
        for animal_age, event in other.events.items():
            if animal_age in self.events:
                self.events[animal_age] += event
            else:
                self.events[animal_age] = event
        return self
