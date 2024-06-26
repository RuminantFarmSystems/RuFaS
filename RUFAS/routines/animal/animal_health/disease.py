from RUFAS.routines.animal.animal_health.outcomes import DiseaseOutcome
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.time import Time


class Disease:
    """
    Class representing disease simulation.
    """

    def __init__(self) -> None:
        # get info about specific disease set by user
        # im = InputManager()
        # self.duration = im.get_data("disease.specific.duration")
        # self.outcome_distribution = im.get_data("disease.specific.outcome_distribution")
        # self.days_to_recovery = im.get_data("disease.specific.days_to_recovery")
        # other disease-specific data: risk factors, incidence factors, etc.
        pass

    def start_disease(self, animal: AnimalBase, time: Time) -> None:
        """Starts disease.

        Parameters
        ----------
        animal : AnimalBase
            The animal with the disease.
        time : Time
            An instance of the Time class to get the current point in the simulation.
        """
        # if adding disease status to animal, update the animal class to have this attribute.
        # animal.disease_status = 'sick'
        # animal.disease_start_day = Time.current_date

    def process_disease_day(self, animal: AnimalBase) -> None:
        """Processes animal disease for each day of the duration of the disease.

        Parameters
        ----------
        animal : AnimalBase
            The animal with the disease.
        """
        # Update daily effects here based on self.outcome_distribution (set in __init__)
        # death, recovery, cull, remain diseased
        # if animal is still sick:
        # self._process_disease_effects(animal)
        # if outcome is something other than "remain diseased":
        # self._end_disease(animal, outcome)
        pass

    def _process_disease_effects(self, animal: AnimalBase) -> None:
        """Modifies daily life values of animal based on disease immediate effects.

        Parameters
        ----------
        animal : AnimalBase
            The diseased animal.
        """
        # pass

    def _end_disease(self, animal: AnimalBase, outcome: DiseaseOutcome) -> None:
        """Processes end of the disease for the animal.

        Parameters
        ----------
        animal : AnimalBase
            The animal that had the disease.
        outcome : DiseaseOutcome
            The outcome for the animal.
        """
        # animal.disease_status = outcome
        # further processing for animal based on outcome
