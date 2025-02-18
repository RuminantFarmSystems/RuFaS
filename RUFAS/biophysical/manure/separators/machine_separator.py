from RUFAS.biophysical.manure.separators.separator import Separator, SeparatorConfig
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


class MachineSeparator(Separator):
    """
    A separator that uses a machine to separate solids from liquids.

    Parameters
    ----------
    config : SeparatorConfig
        Configuration for the separator.
    """

    def __init__(self, config: SeparatorConfig) -> None:
        """Initializes a new MachineSeparator."""
        super().__init__(config)

    def _separate_manure(self) -> dict[str, ManureStream]:
        """
        Separates the solids from the liquids in the manure.

        Returns
        -------
        dict
            A dictionary containing:
            - "solid" : ManureStream
                The solid portion of the separated manure.
            - "liquid" : ManureStream
                The liquid portion of the separated manure.
        """
        if not self.held_manure:
            raise ValueError("Cannot separate manure when 'held_manure' is None.")

        solid_manure = ManureStream(
            water=self.held_manure.water * self.config.water_efficiency,
            ammoniacal_nitrogen=self.held_manure.ammoniacal_nitrogen * self.config.ammoniacal_nitrogen_efficiency,
            nitrogen=self.held_manure.nitrogen * self.config.nitrogen_efficiency,
            phosphorus=self.held_manure.phosphorus * self.config.phosphorus_efficiency,
            potassium=self.held_manure.potassium * self.config.potassium_efficiency,
            ash=self.held_manure.ash * self.config.ash_efficiency,
            non_degradable_volatile_solids=self.held_manure.non_degradable_volatile_solids
            * self.config.non_degradable_volatile_solids_efficiency,
            degradable_volatile_solids=self.held_manure.degradable_volatile_solids
            * self.config.degradable_volatile_solids_efficiency,
            total_solids=self.held_manure.total_solids * self.config.total_solids_efficiency,
            volume=self.held_manure.volume * ManureConstants.SOLID_MANURE_DENSITY,  # TODO: Check if this is correct
        )
        liquid_manure = ManureStream(
            water=self.held_manure.water * (1 - self.config.water_efficiency),
            ammoniacal_nitrogen=self.held_manure.ammoniacal_nitrogen * (1 - self.config.ammoniacal_nitrogen_efficiency),
            nitrogen=self.held_manure.nitrogen * (1 - self.config.nitrogen_efficiency),
            phosphorus=self.held_manure.phosphorus * (1 - self.config.phosphorus_efficiency),
            potassium=self.held_manure.potassium * (1 - self.config.potassium_efficiency),
            ash=self.held_manure.ash * (1 - self.config.ash_efficiency),
            non_degradable_volatile_solids=self.held_manure.non_degradable_volatile_solids
            * (1 - self.config.non_degradable_volatile_solids_efficiency),
            degradable_volatile_solids=self.held_manure.degradable_volatile_solids
            * (1 - self.config.degradable_volatile_solids_efficiency),
            total_solids=self.held_manure.total_solids * (1 - self.config.total_solids_efficiency),
            volume=self.held_manure.volume * ManureConstants.LIQUID_MANURE_DENSITY,  # TODO: Check if this is correct
        )
        return {"solid": solid_manure, "liquid": liquid_manure}
