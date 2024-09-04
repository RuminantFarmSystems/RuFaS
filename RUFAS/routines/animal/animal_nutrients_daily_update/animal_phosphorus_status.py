from RUFAS.routines.animal.animal_nutrients_daily_update.animal_phosphorus import AnimalPhosphorus
from RUFAS.routines.animal.animal_types import AnimalType


class AnimalPhosphorusStatus:
    """
    Calculator class representing the phosphorus status of the animal.
    Will be the avenue for communicating data between the Animal object and the animal's daily phosphorus update.
    """

    def __init__(self) -> None:
        """Starting list for attribute data needed from Animal object:"""
        self.animal_type: AnimalType = None
        self.body_weight: float = 0.0
        self.mature_body_weight: float = 0.0
        self.daily_growth: float = 0.0
        self.days_in_preg: int = 0
        self.milking: bool = False
        self.estimated_daily_milk_produced: float = 0.0
        self.phosphorus_excess: float = 0.0  # (p_excess)
        self.phosphorus_intake: float = 0.0  # (p_intake)
        self.phosphorus_requirement: float = 0.0  # (p_req)
        self.phosphorus_reserves: float = 0.0  # (dP_reserves)
        self.total_phosphorus: float = 0.0  # (p_animal)
        self.phosphorus_retained_for_growth: float = 0.0  # (p_growth)
        self.endogenous_loss_phosphorus: float = 0.0  # (p_maint_feces)
        self.ration_phosphorus_concentration: float = 0.0  # (p_conc_ration)
        self.gestational_phosphorus: float = 0.0  # (p_gest)
        self.gestational_phosphorus_for_calf: float = 0.0  # (p_gest_for_calf)

    def daily_phosphorus_routine(self, animal) -> None:
        """Manages animal's daily phosphorus update."""
        self._get_phosphorus_data(animal)
        dry_matter_intake = self._get_dry_matter_intake()
        phosphorus_updater = AnimalPhosphorus()
        phosphorus_updater.calculate_phosphorus_requirements(self, dry_matter_intake)
        phosphorus_updater.perform_daily_phosphorus_update(self)
        self._update_animal(animal)

    def _get_phosphorus_data(self, animal) -> None:
        """Gets the animal's current phosphorus-related attributes."""
        self.animal_type = animal.animal_type
        self.body_weight = animal.body_weight
        self.mature_body_weight = animal.mature_body_weight
        self.daily_growth = animal.daily_growth
        self.days_in_preg = animal.days_in_preg
        self.milking = animal.milking
        self.estimated_daily_milk_produced = animal.estimated_daily_milk_produced
        self.phosphorus_excess = animal.phosphorus_excess
        self.phosphorus_intake = animal.phosphorus_intake
        self.phosphorus_requirement = animal.phosphorus_requirement
        self.phosphorus_reserves = animal.phosphorus_reserves
        self.total_phosphorus = animal.total_phosphorus
        self.phosphorus_retained_for_growth = animal.phosphorus_retained_for_growth
        self.endogenous_loss_phosphorus = animal.endogenous_loss_phosphorus
        self.ration_phosphorus_concentration = animal.ration_phosphorus_concentration
        self.gestational_phosphorus = animal.gestational_phosphorus
        self.gestational_phosphorus_for_calf = animal.gestational_phosphorus_for_calf

    def _get_dry_matter_intake(self) -> float:
        """Get ration data for animal dry matter intake."""
        # Not sure where ration will be or how it will be tied to a particular animal (currently done by pen)
        # But assuming it's not an attribute of the animal, we will need this info from ration.
        return 0.0

    def _update_animal(self, animal) -> None:
        """Updates the animal's phosphorus-related attributes after the daily routine."""
        animal.endogenous_loss_phosphorus = self.endogenous_loss_phosphorus
        animal.phosphorus_retained_for_growth = self.phosphorus_retained_for_growth
        animal.phosphorus_requirement = self.phosphorus_requirement
        animal.gestational_phosphorus = self.gestational_phosphorus
        animal.gestational_phosphorus_for_calf = self.gestational_phosphorus_for_calf
        animal.phosphorus_excess = self.phosphorus_excess
        animal.phosphorus_reserves = self.phosphorus_reserves
        animal.total_phosphorus = self.total_phosphorus
