from __future__ import annotations

from dataclasses import dataclass, fields

from RUFAS.routines.manure.manure_treatments.manure_types import ManureType


@dataclass(kw_only=True, frozen=True)
class ManureNutrients:
    """A class to store the relevant manure nutrient information to be passed to the crop and soil module"""

    nitrogen: float = 0.0
    """Amount of accumulated manure nitrogen derived from the manure module, kg."""

    phosphorus: float = 0.0
    """Amount of accumulated manure phosphorus derived from the manure module, kg."""

    potassium: float = 0.0
    """Amount of accumulated manure potassium derived from the manure module, kg."""

    dry_matter: float = 0.0
    """Amount of accumulated dry matter derived from the manure module, kg."""

    total_manure_mass: float = 0.0
    """Amount of accumulated manure mass derived from the manure module, kg."""

    manure_type: ManureType
    """Type of manure."""

    def __post_init__(self):
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
            if field.name != "manure_type":
                if value < 0:
                    raise ValueError(f"Field {field.name} must be non-negative.")
            else:
                if not isinstance(value, ManureType):
                    raise ValueError(f"Field {field.name} must be an instance of ManureType.")

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
            f.name: getattr(self, f.name) + getattr(other, f.name) for f in fields(self) if f.name != "manure_type"
        }
        summed_attributes['manure_type'] = self.manure_type

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

        multiplied_attributes = {}
        for f in fields(self):
            if f.name != 'manure_type':
                multiplied_attributes[f.name] = getattr(self, f.name) * scalar
        multiplied_attributes['manure_type'] = self.manure_type

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

        """
        if not isinstance(other, ManureNutrients):
            raise TypeError(f"Cannot subtract {type(other)} from {type(self)}.")

        if self.manure_type != other.manure_type:
            raise TypeError(f"Cannot subtract {other.manure_type} nutrients from {self.manure_type} nutrients.")

        subtracted_attributes = {
            f.name: getattr(self, f.name) - getattr(other, f.name) for f in fields(self) if f.name != "manure_type"
        }
        subtracted_attributes["manure_type"] = self.manure_type

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
