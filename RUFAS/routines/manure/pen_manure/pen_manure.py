from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional

from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.units import MeasurementUnits


@dataclass
class PenManure:
    """
    A class that represents the manure data extracted from the animal module.

    """

    urea: float = 0.0
    """Concentration of urea in manure (g/L)."""
    urea_unit: MeasurementUnits = MeasurementUnits.GRAMS_PER_LITER
    """Unit for urea"""

    urine: float = 0.0
    """Amount of urine in manure (kg)."""
    urine_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for urine"""

    urine_total_ammoniacal_nitrogen: float = 0.0
    """Amount of ammoniacal nitrogen concentration in urine (kg)."""
    urine_total_ammoniacal_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for urine_total_ammoniacal_nitrogen"""

    manure_total_ammoniacal_nitrogen: float = 0.0
    """Amount of total ammoniacal nitrogen in manure slurry (kg)."""
    manure_total_ammoniacal_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for manure_total_ammoniacal_nitrogen"""

    urine_nitrogen: float = 0.0
    """Amount of nitrogen in urine (kg)."""
    urine_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for urine_nitrogen"""

    nitrogen: float = 0.0
    """Amount of nitrogen in manure (kg)."""
    nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for nitrogen"""

    manure_mass: float = 0.0
    """Amount of manure (kg)."""
    manure_mass_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for manure_mass"""

    manure_volume: Optional[float] = None
    """Volume of manure (m^3)."""
    manure_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS
    """Unit for manure_volume"""

    total_solids: float = 0.0
    """Amount of total solids (kg)."""
    total_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for total_solids"""

    degradable_volatile_solids: float = 0.0
    """Amount of degradable volatile solids (kg)."""
    degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for degradable_volatile_solids"""

    non_degradable_volatile_solids: float = 0.0
    """Amount of non-degradable volatile solids (kg)."""
    non_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for non_degradable_volatile_solids"""

    inorganic_phosphorus_fraction: float = 0.0
    """Fraction of water extractable inorganic phosphorus (unitless)."""
    inorganic_phosphorus_fraction_unit: MeasurementUnits = MeasurementUnits.UNITLESS
    """Unit for inorganic_phosphorus_fraction"""

    organic_phosphorus_fraction: float = 0.0
    """Fraction of water extractable organic phosphorus (unitless)."""
    organic_phosphorus_fraction_unit: MeasurementUnits = MeasurementUnits.UNITLESS
    """Unit for organic_phosphorus_fraction"""

    non_water_inorganic_phosphorus_fraction: float = 0.0
    """Fraction of non-water extractable inorganic phosphorus (unitless)."""
    non_water_inorganic_phosphorus_fraction_unit: MeasurementUnits = MeasurementUnits.UNITLESS
    """Unit for non_water_inorganic_phosphorus_fraction"""

    non_water_organic_phosphorus_fraction: float = 0.0
    """Fraction of non-water extractable organic phosphorus (unitless)."""
    non_water_organic_phosphorus_fraction_unit: MeasurementUnits = MeasurementUnits.UNITLESS
    """Unit for non_water_organic_phosphorus_fraction"""

    phosphorus: float = 0.0
    """Amount of phosphorus excreted in manure (kg)."""
    phosphorus_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for phosphorus"""

    phosphorus_fraction: float = 0.0
    """Fraction of phosphorus in manure (unitless)."""
    phosphorus_fraction_unit: MeasurementUnits = MeasurementUnits.UNITLESS
    """Unit for phosphorus_fraction"""

    potassium: float = 0.0
    """Amount of potassium in manure (kg)."""
    potassium_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for potassium"""

    def __post_init__(self) -> None:
        """Performs any necessary unit conversion after initialization."""
        self.manure_volume = self.manure_mass / ManureConstants.SLURRY_MANURE_DENSITY

        for fld in fields(self):
            if not fld.name.endswith("_unit"):
                if getattr(self, fld.name) < 0:
                    setattr(self, fld.name, 0)
            else:
                pass

    @classmethod
    def get_instance(cls, animal_manure: AnimalManureExcretions, num_animals: int) -> PenManure:
        """
        Create a PenManure object based on the information given in the manure data.

        Parameters
        ----------
        animal_manure : AnimalManureExcretions
            The manure data extracted from the animal module.
        num_animals : int
            The number of animals in the pen.


        Returns
        -------
        PenManure
            A PenManure object.

        """
        if num_animals == 0:
            return cls()

        return cls(
            urea=animal_manure.urea / num_animals,
            urine=animal_manure.urine,
            urine_nitrogen=animal_manure.urine_nitrogen,
            urine_total_ammoniacal_nitrogen=animal_manure.urine_nitrogen,
            manure_total_ammoniacal_nitrogen=animal_manure.manure_total_ammoniacal_nitrogen,
            nitrogen=animal_manure.manure_nitrogen,
            manure_mass=animal_manure.manure_mass,
            total_solids=animal_manure.total_solids,
            degradable_volatile_solids=animal_manure.degradable_volatile_solids,
            non_degradable_volatile_solids=animal_manure.non_degradable_volatile_solids,
            inorganic_phosphorus_fraction=animal_manure.inorganic_phosphorus_fraction / num_animals,
            organic_phosphorus_fraction=animal_manure.organic_phosphorus_fraction / num_animals,
            non_water_inorganic_phosphorus_fraction=animal_manure.non_water_inorganic_phosphorus_fraction / num_animals,
            non_water_organic_phosphorus_fraction=animal_manure.non_water_organic_phosphorus_fraction / num_animals,
            phosphorus=animal_manure.phosphorus * GeneralConstants.GRAMS_TO_KG,
            phosphorus_fraction=animal_manure.phosphorus_fraction / num_animals,
            potassium=animal_manure.potassium * GeneralConstants.GRAMS_TO_KG,
        )
