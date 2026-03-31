from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Optional

from RUFAS.data_structures.manure_types import ManureType
from RUFAS.units import MeasurementUnits


@dataclass(kw_only=True, frozen=True)
class ManureNutrients:
    """A class to store the relevant manure nutrient information to be passed to the crop and soil module"""

    manure_type: Optional[ManureType] = None
    """Type of manure."""
    manure_type_unit: MeasurementUnits = MeasurementUnits.UNITLESS
    """Unit for manure_type"""

    nitrogen: float = 0.0
    """Amount of accumulated manure nitrogen derived from the manure module, kg."""
    nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for nitrogen"""

    phosphorus: float = 0.0
    """Amount of accumulated manure phosphorus derived from the manure module, kg."""
    phosphorus_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for phosphorus"""

    potassium: float = 0.0
    """Amount of accumulated manure potassium derived from the manure module, kg."""
    potassium_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for potassium"""

    dry_matter: float = 0.0
    """Amount of accumulated dry matter derived from the manure module, kg."""
    dry_matter_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for dry_matter"""

    total_manure_mass: float = 0.0
    """Amount of accumulated manure mass derived from the manure module, kg."""
    total_manure_mass_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS
    """Unit for total_manure_mass"""

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields.

        Raises
        ------
        ValueError
            If any numerical field is negative.
            If manure type is not a valid ManureType.

        """
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name.endswith("_unit"):
                pass
            elif field.name == "manure_type":
                if not isinstance(value, ManureType):
                    raise ValueError(f"Field {field.name} must be an instance of ManureType.")
            else:
                if value < 0:
                    raise ValueError(f"Field {field.name} must be non-negative.")

    @property
    def units_dict(self) -> dict[str, MeasurementUnits]:
        """
        Creates a dictionary of unit labels for each property in the ManureNutrients class.

        This method iterates over all attributes of the instance, filtering for those ending with "_unit", and
        constructs a dictionary where each key corresponds to the name of a nutrient or property (e.g., 'nitrogen_unit',
        'phosphorus_unit', etc.), and each value is the unit of measurement (e.g., 'kg', 'unitless').

        Returns
        -------
        dict[MeasurementUnits, MeasurementUnits]
            A dictionary where keys are the names of attributes representing the units of nutrients and properties,
            and values are the respective units of measurement.
        """
        units_vars_list = list(key for (key, value) in self.__dict__.items() if key.endswith("_unit"))
        return {unit_key: getattr(self, unit_key) for unit_key in units_vars_list}

    @property
    def dry_matter_fraction(self) -> float:
        """
        Calculate the dry matter fraction of the manure.

        Returns
        -------
        float
            The dry matter fraction of the manure, unitless, between 0 and 1.

        """
        if self.total_manure_mass == 0.0:
            return 0.0
        return self.dry_matter / self.total_manure_mass

    @property
    def nitrogen_composition(self) -> float:
        """
        Calculate the nitrogen composition of the manure.

        Returns
        -------
        float
            The nitrogen composition of the manure, unitless, between 0 and 1.

        """
        if self.total_manure_mass == 0.0:
            return 0.0
        return self.nitrogen / self.total_manure_mass

    @property
    def phosphorus_composition(self) -> float:
        """
        Calculate the phosphorus composition of the manure.

        Returns
        -------
        float
            The phosphorus composition of the manure, unitless, between 0 and 1.

        """
        if self.total_manure_mass == 0.0:
            return 0.0
        return self.phosphorus / self.total_manure_mass

    def reset_values(self) -> "ManureNutrients":
        """
        Return a new ManureNutrients with all numeric nutrient/mass
        fields zeroed out, but keeping the manure‐type and units unchanged.
        """
        return replace(
            self,
            nitrogen=0.0,
            phosphorus=0.0,
            potassium=0.0,
            dry_matter=0.0,
            total_manure_mass=0.0,
        )

    def __add__(self, other: ManureNutrients) -> ManureNutrients:
        """
        Add two ManureNutrients objects together.

        Parameters
        ----------
        other : ManureNutrients
            The other ManureNutrients object to add to this one.

        Returns
        -------
        ManureNutrients
            The sum of the two ManureNutrients objects.

        Raises
        ------
        TypeError
            If the other object is not a ManureNutrients object.
            If the other object is not the same ManureType as the self.

        """
        if not isinstance(other, ManureNutrients):
            raise TypeError(f"Cannot add {type(self)} to {type(other)}.")

        if self.manure_type != other.manure_type:
            raise TypeError(f"Cannot add {self.manure_type} nutrients to {other.manure_type} nutrients.")

        summed_attributes = {
            field.name: getattr(self, field.name) + getattr(other, field.name)
            for field in fields(self)
            if field.name != "manure_type" and not field.name.endswith("_unit")
        }
        summed_attributes["manure_type"] = self.manure_type
        summed_attributes.update(self.units_dict)

        return ManureNutrients(**summed_attributes)

    def __mul__(self, scalar: int | float) -> ManureNutrients:
        """
        Multiply a ManureNutrients object by a scalar (left multiplication, i.e. ManureNutrients * scalar).

        Parameters
        ----------
        scalar : int | float
            The scalar to multiply by.

        Returns
        -------
        ManureNutrients
            The product of the ManureNutrients object and the scalar.

        Raises
        ------
        TypeError
            If the other object is not an int or a float.
        ValueError
            If the scalar is negative.

        """
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot multiply {type(self)} by {type(scalar)}.")

        if scalar < 0.0:
            raise ValueError(f"Cannot multiply {type(self)} by a negative scalar.")

        multiplied_attributes = {
            field.name: getattr(self, field.name) * scalar
            for field in fields(self)
            if (field.name != "manure_type" and not field.name.endswith("_unit"))
        }
        multiplied_attributes["manure_type"] = self.manure_type
        multiplied_attributes.update(self.units_dict)

        return ManureNutrients(**multiplied_attributes)

    def __sub__(self, other: ManureNutrients) -> ManureNutrients:
        """
        Subtract two ManureNutrients objects.

        Parameters
        ----------
        other : ManureNutrients
            The other ManureNutrients object to subtract from this one.

        Returns
        -------
        ManureNutrients
            The difference of the two ManureNutrients objects.

        Raises
        ------
        TypeError
            If the other object is not a ManureNutrients object.
            If the other object is not the same ManureType as the self.
        ValueError
            If amount of any nutrient other object wants to subtract is greater than what is available in self.

        """
        if not isinstance(other, ManureNutrients):
            raise TypeError(f"Cannot subtract {type(other)} from {type(self)}.")

        if self.manure_type != other.manure_type:
            raise TypeError(f"Cannot subtract {other.manure_type} nutrients from {self.manure_type} nutrients.")

        subtracted_attributes = {}
        for field in fields(self):
            if field.name != "manure_type" and not field.name.endswith("_unit"):
                self_value = getattr(self, field.name)
                other_value = getattr(other, field.name)
                if other_value > self_value:
                    raise ValueError(f"The amount of {field.name} in other object is greater than what is available.")
                subtracted_attributes[field.name] = self_value - other_value
        subtracted_attributes["manure_type"] = self.manure_type
        subtracted_attributes.update(self.units_dict)

        return ManureNutrients(**subtracted_attributes)

    def __rmul__(self, scalar: int | float) -> ManureNutrients:
        """
        Multiply a ManureNutrients object by a scalar (right multiplication, i.e., scalar * ManureNutrients).

        Parameters
        ----------
        scalar : int | float
            The scalar to multiply by.

        Returns
        -------
        ManureNutrients
            The product of the ManureNutrients object and the scalar.

        """
        return self.__mul__(scalar)
