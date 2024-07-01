from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase


class DiseaseRecovery:
    """
    Abstract class representing disease simulation.
    """

    def __init__(self) -> None:
        # im = InputManager()
        # im.get_data("disease.specific.intermediate_effects")
        # im.get_data("disease.specific.longterm_effects")
        pass

    def process_intermediate_effects(self, animal: AnimalBase) -> None:
        """Modifies animal values according to disease intermediate effects.

        Parameters
        ----------
        animal : AnimalBase
            The animal in recovery.
        """
        pass

    def process_longterm_effects(self, animal: AnimalBase) -> None:
        """Modifies animal values according to disease long-term effects.

        Parameters
        ----------
        animal : AnimalBase
            The animal in recovery.
        """
        pass
