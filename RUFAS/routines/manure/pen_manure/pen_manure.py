from __future__ import annotations

from dataclasses import dataclass, fields
from dataclasses import field
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.manure.constants_and_units.datatype_with_unit import FloatWithUnit
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


@dataclass
class PenManure:
    """
    A class that represents the manure data extracted from the animal module.

    """

    urea: FloatWithUnit = FloatWithUnit(0.0, unit="g/L")
    """Concentration of urea in manure (g/L)."""

    urine: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of urine in manure (kg)."""

    urine_total_ammoniacal_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of ammoniacal nitrogen concentration in urine (kg)."""

    manure_total_ammoniacal_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of total ammoniacal nitrogen in manure slurry (kg)."""

    urine_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of nitrogen in urine (kg)."""

    nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of nitrogen in manure (kg)."""

    manure_mass: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of manure (kg)."""

    manure_volume: Optional[FloatWithUnit] = FloatWithUnit(None, unit="m^3")
    """Volume of manure (m^3)."""

    total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of total solids (kg)."""

    degradable_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of degradable volatile solids (kg)."""

    non_degradable_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of non-degradable volatile solids (kg)."""

    inorganic_phosphorus_fraction: FloatWithUnit = FloatWithUnit(0.0, unit="unitless")
    """Fraction of water extractable inorganic phosphorus (unitless)."""

    organic_phosphorus_fraction: FloatWithUnit = FloatWithUnit(0.0, unit="unitless")
    """Fraction of water extractable organic phosphorus (unitless)."""

    non_water_inorganic_phosphorus_fraction: FloatWithUnit = FloatWithUnit(0.0, unit="unitless")
    """Fraction of non-water extractable inorganic phosphorus (unitless)."""

    non_water_organic_phosphorus_fraction: FloatWithUnit = FloatWithUnit(0.0, unit="unitless")
    """Fraction of non-water extractable organic phosphorus (unitless)."""

    phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of phosphorus excreted in manure (kg)."""

    phosphorus_fraction: FloatWithUnit = FloatWithUnit(0.0, unit="unitless")
    """Fraction of phosphorus in manure (unitless)."""

    potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    """Amount of potassium in manure (kg)."""

    enteric_methane_kg: FloatWithUnit = FloatWithUnit(0.0, unit="kg/day")
    """Amount of methane emission (kg/day)."""

    def __post_init__(self):
        """Performs any necessary unit conversion after initialization."""
        self.manure_volume = FloatWithUnit(self.manure_mass / ManureConstants.SLURRY_MANURE_DENSITY,
                                           unit="m^3")

        # Zero out any negative field
        # TODO: This is a temporary fix. Need to find out why negative values are being generated
        # from the animal module. Later, we should raise an exception if a negative value is found.  - Issue #609
        # ***Note*** this issue is mostly resolved by PR #1133 but the code below should be updated to
        # to raise an exception as noted above rather than zeroing out the negative values because it means there's
        # a bigger issue that needs to be addressed somewhere else in the code.
        for fld in fields(self):
            if getattr(self, fld.name) < 0:
                setattr(self, fld.name, 0)

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
            urea=FloatWithUnit(animal_manure["urea"] / num_animals, unit=PenManure.urea.unit),
            urine=FloatWithUnit(animal_manure["urine"], unit=PenManure.urine.unit),
            urine_nitrogen=FloatWithUnit(animal_manure["urine_nitrogen"], unit=PenManure.urine_nitrogen.unit),
            urine_total_ammoniacal_nitrogen=FloatWithUnit(
                animal_manure["urine_nitrogen"] * ManureConstants.URINE_TAN_FACTOR,
                unit="kg"
            ),
            manure_total_ammoniacal_nitrogen=FloatWithUnit(
                animal_manure["urine_nitrogen"] * ManureConstants.URINE_TAN_FACTOR,
                unit="kg"
            ),
            nitrogen=FloatWithUnit(animal_manure["manure_nitrogen"], unit=PenManure.nitrogen.unit),
            manure_mass=FloatWithUnit(animal_manure["manure_mass"], unit=PenManure.manure_mass.unit),
            total_solids=FloatWithUnit(animal_manure["total_solids"], unit=PenManure.total_solids.unit),
            degradable_volatile_solids=FloatWithUnit(animal_manure["degradable_volatile_solids"],
                                                     unit=PenManure.degradable_volatile_solids.unit),
            non_degradable_volatile_solids=FloatWithUnit(animal_manure["non_degradable_volatile_solids"],
                                                         unit=PenManure.non_degradable_volatile_solids.unit),
            inorganic_phosphorus_fraction=FloatWithUnit(animal_manure["inorganic_phosphorus_fraction"] / num_animals,
                                                        unit=PenManure.inorganic_phosphorus_fraction.unit),
            organic_phosphorus_fraction=FloatWithUnit(animal_manure["organic_phosphorus_fraction"] / num_animals,
                                                      unit=PenManure.organic_phosphorus_fraction.unit),
            non_water_inorganic_phosphorus_fraction=FloatWithUnit(
                animal_manure["non_water_inorganic_phosphorus_fraction"] / num_animals,
                unit=PenManure.non_water_inorganic_phosphorus_fraction.unit
            ),
            non_water_organic_phosphorus_fraction=FloatWithUnit(
                animal_manure["non_water_organic_phosphorus_fraction"] / num_animals,
                unit=PenManure.non_water_organic_phosphorus_fraction.unit),
            phosphorus=FloatWithUnit(animal_manure["phosphorus"] * GeneralConstants.GRAMS_TO_KG,
                                     unit=PenManure.phosphorus.unit),
            phosphorus_fraction=FloatWithUnit(animal_manure["phosphorus_fraction"] / num_animals,
                                              unit=PenManure.phosphorus_fraction.unit),
            potassium=FloatWithUnit(animal_manure["potassium"] * GeneralConstants.GRAMS_TO_KG,
                                    unit=PenManure.potassium.unit),
            enteric_methane_kg=FloatWithUnit(animal_manure["enteric_methane_g"] * GeneralConstants.GRAMS_TO_KG,
                                             unit=PenManure.enteric_methane_kg.unit),
        )
