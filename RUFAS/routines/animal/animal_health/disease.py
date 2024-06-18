from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase


class Disease:
    """
    Abstract class representing disease simulation.
    """

    def __init__(self) -> None:
        # im = InputManager()
        # self.duration = im.get_data("disease.specific.duration")
        # self.outcome_distribution = im.get_data("disease.specific.duration")
        # self.days_to_recovery = im.get_data("disease.specific.days_to_recovery")
        # other
        pass

    def start_disease(self, animal: AnimalBase, simulation_day: int) -> None:
        """Starts disease.

        Parameters
        ----------
        animal : AnimalBase
            The animal with the disease.
        start_day : int
            The date in the simulation when the disease is starting.
        """
        animal.disease_status = 'sick'
        animal.disease_start_day = simulation_day

    def _process_disease_day(self, animal: AnimalBase):
        """Processes animal disease for each day of the duration of the disease.

        Parameters
        ----------
        animal : AnimalBase
            _description_
        """
        # Update daily effects here
        pass

    def end_disease(self, animal: AnimalBase, outcome):
        animal.disease_status = 'recovered' if outcome == 'recovery' else outcome
