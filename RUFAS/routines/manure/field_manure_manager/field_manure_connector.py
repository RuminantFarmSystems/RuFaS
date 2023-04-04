from __future__ import annotations

from dataclasses import dataclass, astuple
from typing import Protocol

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class FieldManureDataLiquidNutrients(Protocol):
    liquid_manure_nitrogen: float
    liquid_manure_phosphorus: float
    liquid_manure_potassium: float


class FieldManureDataLiquidPortion(FieldManureDataLiquidNutrients):
    liquid_manure_volume: float


class FieldManureDataSludgeNutrients(Protocol):
    sludge_manure_nitrogen: float
    sludge_manure_phosphorus: float
    sludge_manure_potassium: float


class FieldManureDataSludgePortion(FieldManureDataSludgeNutrients):
    sludge_manure_volume: float


@dataclass(frozen=True)
class FieldManureData(FieldManureDataLiquidPortion, FieldManureDataSludgePortion):
    """Class to hold data for field manure."""

    liquid_manure_nitrogen: float = 0.0
    """Amount of nitrogen in the liquid portion of the manure, kg."""

    liquid_manure_phosphorus: float = 0.0
    """Amount of phosphorus in the liquid portion of the manure, kg."""

    liquid_manure_potassium: float = 0.0
    """Amount of potassium in the liquid portion of the manure, kg."""

    liquid_manure_volume: float = 0.0
    """Total volume of liquid manure, m^3."""

    sludge_manure_nitrogen: float = 0.0
    """Amount of nitrogen in the sludge portion of the manure, kg."""

    sludge_manure_phosphorus: float = 0.0
    """Amount of phosphorus in the sludge portion of the manure, kg."""

    sludge_manure_potassium: float = 0.0
    """Amount of potassium in the sludge portion of the manure, kg."""

    sludge_manure_volume: float = 0.0
    """Total volume of sludge manure, m^3."""

    @property
    def liquid_manure_mass(self) -> float:
        """Returns the mass of the liquid portion of the manure, kg."""
        return self.liquid_manure_volume * ManureConstants.MANURE_DENSITY

    @property
    def sludge_manure_mass(self) -> float:
        """Returns the mass of the sludge portion of the manure, kg."""
        return self.sludge_manure_volume * ManureConstants.MANURE_DENSITY

    @classmethod
    def get_instance_from_manure_treatment_daily_output(cls,
                                                        manure_treatment_daily_output: ManureTreatmentDailyOutput) -> FieldManureData:
        """Creates a FieldManureData object from a ManureTreatmentDailyOutput object.

        Parameters
        ----------
        manure_treatment_daily_output : ManureTreatmentDailyOutput
                    The ManureTreatmentDailyOutput object to create a FieldManureData object from.
        Returns
        -------
        FieldManureData
        The FieldManureData object created from the ManureTreatmentDailyOutput object.

        """

        return cls(
            liquid_manure_nitrogen=manure_treatment_daily_output.liquid_manure_nitrogen,
            liquid_manure_phosphorus=manure_treatment_daily_output.liquid_manure_phosphorus,
            liquid_manure_potassium=manure_treatment_daily_output.liquid_manure_potassium,
            liquid_manure_volume=manure_treatment_daily_output.liquid_manure_daily_volume,
            sludge_manure_nitrogen=manure_treatment_daily_output.sludge_manure_nitrogen,
            sludge_manure_phosphorus=manure_treatment_daily_output.sludge_manure_phosphorus,
            sludge_manure_potassium=manure_treatment_daily_output.sludge_manure_potassium,
            sludge_manure_volume=manure_treatment_daily_output.sludge_manure_daily_volume,
        )

    def __add__(self, other: FieldManureData) -> FieldManureData:
        """Adds two FieldManureData objects together.

        Parameters
        ----------
        other : FieldManureData
        The FieldManureData object to add to the current object.

        Returns
        -------
        FieldManureData
        The sum of the two FieldManureData objects.

        """

        if type(other) != FieldManureData:
            raise TypeError(f'Cannot add {type(other)} to {type(self)}')

        return FieldManureData(*[field_from_self + field_from_other
                                 for field_from_self, field_from_other in zip(astuple(self), astuple(other))])

    def __mul__(self, scalar: float) -> FieldManureData:
        """Multiplies a FieldManureData object by a scalar.

        Parameters
        ----------
        scalar : float
        The scalar to multiply the FieldManureData object by.

        Returns
        -------
        FieldManureData
        The product of the FieldManureData object and the scalar.

        """

        if type(scalar) not in [int, float]:
            raise TypeError(f'Cannot multiply {type(self)} by {type(scalar)}')

        return FieldManureData(*[field_from_self * scalar
                                 for field_from_self in astuple(self)])

    def __rmul__(self, scalar: float) -> FieldManureData:
        """Multiplies a FieldManureData object by a scalar when the scalar is on the left side of the multiplication.

        Parameters
        ----------
        scalar : float
        The scalar to multiply the FieldManureData object by.

        Returns
        -------
        FieldManureData
        The product of the FieldManureData object and the scalar.

        """

        return self * scalar

    def __sub__(self, other: FieldManureData) -> FieldManureData:
        """Subtracts two FieldManureData objects.

        Parameters
        ----------
        other : FieldManureData
        The FieldManureData object to subtract from the current object.

        Returns
        -------
        FieldManureData

        The difference of the two FieldManureData objects.

        """

        if type(other) != FieldManureData:
            raise TypeError(f'Cannot subtract {type(other)} from {type(self)}')

        return self + (-1 * other)

    @property
    def is_valid(self) -> bool:
        """Returns whether the FieldManureData object is valid where all attributes are non-negative.

        Returns
        -------
        bool
            Whether the FieldManureData object is valid.

        """

        return all([field >= 0 for field in astuple(self)])

    def zero_out_negative_attributes(self) -> FieldManureData:
        """Zeroes out any negative attributes in the FieldManureData object.

        Returns
        -------
        FieldManureData
            The FieldManureData object with all negative attributes set to zero.

        """

        return FieldManureData(*[0 if field < 0 else field for field in astuple(self)])

    def extract_liquid_manure_portion(self) -> FieldManureData:
        """Extracts the liquid manure portion of the FieldManureData object.

        Returns
        -------
        FieldManureData
            The liquid manure portion of the FieldManureData object.

        """

        return FieldManureData(
            liquid_manure_nitrogen=self.liquid_manure_nitrogen,
            liquid_manure_phosphorus=self.liquid_manure_phosphorus,
            liquid_manure_potassium=self.liquid_manure_potassium,
            liquid_manure_volume=self.liquid_manure_volume,
            sludge_manure_nitrogen=0,
            sludge_manure_phosphorus=0,
            sludge_manure_potassium=0,
            sludge_manure_volume=0,
        )

    def extract_sludge_manure_portion(self) -> FieldManureData:
        """Extracts the sludge manure portion of the FieldManureData object.

        Returns
        -------
        FieldManureData
            The sludge manure portion of the FieldManureData object.

        """

        return FieldManureData(
            liquid_manure_nitrogen=0,
            liquid_manure_phosphorus=0,
            liquid_manure_potassium=0,
            liquid_manure_volume=0,
            sludge_manure_nitrogen=self.sludge_manure_nitrogen,
            sludge_manure_phosphorus=self.sludge_manure_phosphorus,
            sludge_manure_potassium=self.sludge_manure_potassium,
            sludge_manure_volume=self.sludge_manure_volume,
        )


class FieldManureManager:
    """Class to handler calculations for field manure data when working with the crop and soil module."""

    def __init__(self, field_manure_data: FieldManureData) -> None:
        """Initializes the FieldManureManager object.  

        Parameters
        ----------
        field_manure_data : FieldManureData
            The FieldManureData object to use for calculations.

        """

        self._field_manure_data = field_manure_data

    @property
    def field_manure_data(self) -> FieldManureData:
        """Returns the current FieldManureData object.  

        Returns
        -------
        FieldManureData
            The current FieldManureData object.

        """

        return self._field_manure_data

    def add(self, field_manure_data: FieldManureData) -> None:
        """Adds a FieldManureData object to the current FieldManureData object.  

        Parameters
        ----------
        field_manure_data : FieldManureData
            The FieldManureData object to add to the current FieldManureData object.

        """

        self._field_manure_data += field_manure_data

    def _use(self, field_manure_data: FieldManureData) -> None:
        """Subtracts a FieldManureData object from the current FieldManureData object.  

        Any negative attributes in the FieldManureData object as a result of usage are set to zero.

        Parameters
        ----------
        field_manure_data : FieldManureData
            The FieldManureData object to subtract from the current FieldManureData object.

        """

        self._field_manure_data -= field_manure_data
        self._field_manure_data = self._field_manure_data.zero_out_negative_attributes()

    def use_fraction(self, fraction: float) -> None:
        """Uses a fraction of the current FieldManureData object.  

        Any negative attributes in the FieldManureData object as a result of usage are set to zero.

        Parameters
        ----------
        fraction : float
            The fraction to subtract from the current FieldManureData object.

        """

        self._use(fraction * self._field_manure_data)

    def use_all(self) -> None:
        """Uses all the current FieldManureData object."""
        self._use(self._field_manure_data)

    @classmethod
    def calc_minimum_fraction_needed_to_meet_liquid_nutrient_requirements(
            cls, nutrients: FieldManureDataLiquidNutrients) -> float:
        """Calculates the minimum fraction of the liquid manure needed to meet the given nutrient requirements."""
        # TODO: Implement the logic
        pass

    @classmethod
    def calc_minimum_fraction_needed_to_meet_sludge_nutrient_requirements(
            cls, nutrients: FieldManureDataSludgeNutrients) -> float:
        """Calculates the minimum fraction of the sludge manure needed to meet the given nutrient requirements."""
        pass

    def use_liquid_manure_nutrients(self, nutrients: FieldManureDataLiquidNutrients) -> None:
        """Uses the given liquid manure nutrients.  

        Parameters
        ----------
        nutrients : FieldManureDataLiquidNutrients
            The liquid manure nutrients to use.

        """

        self.use_fraction(self.calc_minimum_fraction_needed_to_meet_liquid_nutrient_requirements(nutrients))

    def use_sludge_manure_nutrients(self, nutrients: FieldManureDataSludgeNutrients) -> None:
        """Uses the given sludge manure nutrients.  

        Parameters
        ----------
        nutrients : FieldManureDataSludgeNutrients
            The sludge manure nutrients to use.

        """

        self.use_fraction(self.calc_minimum_fraction_needed_to_meet_sludge_nutrient_requirements(nutrients))
