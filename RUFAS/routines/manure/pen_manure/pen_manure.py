from __future__ import annotations

from dataclasses import dataclass, fields
from dataclasses import field

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.manure.constants_and_units.datatype_with_unit import FloatWithUnit
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


@dataclass
class PenManure:
    """
    A class that represents the manure data extracted from the animal module.

    """

    urea: FloatWithUnit = 0.0
    """Concentration of urea in manure (g/L)."""
    urea.unit = "g/L"

    urine: FloatWithUnit = 0.0
    """Amount of urine in manure (kg)."""
    urine.unit = "kg"

    urine_total_ammoniacal_nitrogen: FloatWithUnit = 0.0
    """Amount of ammoniacal nitrogen concentration in urine (kg)."""
    urine_total_ammoniacal_nitrogen.unit = "kg"

    manure_total_ammoniacal_nitrogen: FloatWithUnit = 0.0
    """Amount of total ammoniacal nitrogen in manure slurry (kg)."""
    manure_total_ammoniacal_nitrogen.unit = "kg"

    urine_nitrogen: FloatWithUnit = 0.0
    """Amount of nitrogen in urine (kg)."""
    urine_nitrogen.unit = "kg"

    nitrogen: FloatWithUnit = 0.0
    """Amount of nitrogen in manure (kg)."""
    nitrogen.unit = "kg"

    manure_mass: FloatWithUnit = 0.0
    """Amount of manure (kg)."""
    manure_mass.unit = "kg"

    manure_volume: FloatWithUnit = field(init=False)
    """Volume of manure (m^3)."""
    manure_volume.unit = "m^3"

    total_solids: FloatWithUnit = 0.0
    """Amount of total solids (kg)."""
    total_solids.unit = "kg"

    degradable_volatile_solids: FloatWithUnit = 0.0
    """Amount of degradable volatile solids (kg)."""
    degradable_volatile_solids.unit = "kg"

    non_degradable_volatile_solids: FloatWithUnit = 0.0
    """Amount of non-degradable volatile solids (kg)."""
    non_degradable_volatile_solids.unit = "kg"

    inorganic_phosphorus_fraction: FloatWithUnit = 0.0
    """Fraction of water extractable inorganic phosphorus (unitless)."""
    inorganic_phosphorus_fraction.unit = "unitless"

    organic_phosphorus_fraction: FloatWithUnit = 0.0
    """Fraction of water extractable organic phosphorus (unitless)."""
    organic_phosphorus_fraction.unit = "unitless"

    non_water_inorganic_phosphorus_fraction: FloatWithUnit = 0.0
    """Fraction of non-water extractable inorganic phosphorus (unitless)."""
    non_water_inorganic_phosphorus_fraction.unit = "unitless"

    non_water_organic_phosphorus_fraction: FloatWithUnit = 0.0
    """Fraction of non-water extractable organic phosphorus (unitless)."""
    non_water_organic_phosphorus_fraction.unit = "unitless"

    phosphorus: FloatWithUnit = 0.0
    """Amount of phosphorus excreted in manure (kg)."""
    phosphorus.unit = "kg"

    phosphorus_fraction: FloatWithUnit = 0.0
    """Fraction of phosphorus in manure (unitless)."""
    phosphorus_fraction.unit = "unitless"

    potassium: FloatWithUnit = 0.0
    """Amount of potassium in manure (kg)."""
    potassium.unit = "kg"

    enteric_methane_kg: FloatWithUnit = 0.0
    """Amount of methane emission (kg/day)."""
    enteric_methane_kg.unit = "kg/day"

    def __post_init__(self):
        """Performs any necessary unit conversion after initialization."""
        self.manure_volume = self.manure_mass / ManureConstants.SLURRY_MANURE_DENSITY

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
            urea=animal_manure["urea"] / num_animals,
            urine=animal_manure["urine"],
            urine_nitrogen=animal_manure["urine_nitrogen"],
            urine_total_ammoniacal_nitrogen=animal_manure["urine_nitrogen"] * ManureConstants.URINE_TAN_FACTOR,
            manure_total_ammoniacal_nitrogen=animal_manure["urine_nitrogen"] * ManureConstants.URINE_TAN_FACTOR,
            nitrogen=animal_manure["manure_nitrogen"],
            manure_mass=animal_manure["manure_mass"],
            total_solids=animal_manure["total_solids"],
            degradable_volatile_solids=animal_manure["degradable_volatile_solids"],
            non_degradable_volatile_solids=animal_manure["non_degradable_volatile_solids"],
            inorganic_phosphorus_fraction=animal_manure["inorganic_phosphorus_fraction"] / num_animals,
            organic_phosphorus_fraction=animal_manure["organic_phosphorus_fraction"] / num_animals,
            non_water_inorganic_phosphorus_fraction=animal_manure["non_water_inorganic_phosphorus_fraction"]
            / num_animals,
            non_water_organic_phosphorus_fraction=animal_manure["non_water_organic_phosphorus_fraction"] / num_animals,
            phosphorus=animal_manure["phosphorus"] * GeneralConstants.GRAMS_TO_KG,
            phosphorus_fraction=animal_manure["phosphorus_fraction"] / num_animals,
            potassium=animal_manure["potassium"] * GeneralConstants.GRAMS_TO_KG,
            enteric_methane_kg=animal_manure["enteric_methane_g"] * GeneralConstants.GRAMS_TO_KG,
        )
