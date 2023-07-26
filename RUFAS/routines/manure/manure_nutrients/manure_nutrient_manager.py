from __future__ import annotations

import math

from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults


class ManureNutrientManager:
    def __init__(self):
        """Initialize the manure nutrient manager."""

        self._nutrients = ManureNutrients()

    @property
    def values(self) -> ManureNutrients:
        """
        Get the current nutrient values stored in the manager.

        Returns
        -------
        ManureNutrients
            The current nutrient values stored in the manager.

        """
        return self._nutrients

    def add_nutrients(self, nutrients: ManureNutrients) -> None:
        """
        Add nutrients to the manager from the manure module.

        Parameters
        ----------
        nutrients : ManureNutrients
            The nutrients to be added to the manager.

        Returns
        -------
        None

        """
        self._nutrients += nutrients

    def request_nutrients(self, request: NutrientRequest) -> NutrientRequestResults | None:
        """
        Handle the request for specific nutrients from the crop and soil module.

        This method evaluates the nutrient request made by considering both nitrogen and phosphorus
        quantities desired. It calculates the projected manure mass that would satisfy the request
        and checks against the nutrients available in the manager.

        If the request can be fulfilled either partially or wholly, the corresponding amount of nutrients
        is subtracted from the manager's internal bookkeeping. The method then returns the results of the nutrient request,
        which detail the amounts of nutrients that can be provided to fulfill the request. If the request
        cannot be fulfilled at all, the method will return None.

        Parameters
        ----------
        request : NutrientRequest
            The specific nutrient request, including quantities of nitrogen and phosphorus.

        Returns
        -------
        NutrientRequestResults | None
            The results of the nutrient request, detailed in a `NutrientRequestResults` object, which includes
            the amount of nitrogen, phosphorus, total manure mass, dry matter, and others that can be provided to fulfill the request.
            Returns None if the request cannot be fulfilled.

        """
        eval_results = self._evaluate_nutrient_request(request)
        if eval_results is not None:
            self._remove_nutrients(eval_results)
        return eval_results

    def _evaluate_nutrient_request(self, request: NutrientRequest) -> NutrientRequestResults | None:
        """
        Evaluate a nutrient request. The method calculates the projected manure mass
        based on the request for nitrogen and phosphorus. It then checks if the
        projected manure mass can be fulfilled by the available nutrients in the manager.

        Parameters
        ----------
        request : NutrientRequest
            The request for nutrients.

        Returns
        -------
        NutrientRequestResults | None
            The results of the nutrient request. See :class:`NutrientsRequestResults` for details.
            If the request is not fulfillable, the method will return None. Otherwise, it will
            return a NutrientRequestResults object.

        """
        nitrogen_derived_manure_mass = self._calculate_projected_manure_mass(request.nitrogen,
                                                                             self._nutrients.nitrogen_composition)
        phosphorus_derived_manure_mass = self._calculate_projected_manure_mass(request.phosphorus,
                                                                               self._nutrients.phosphorus_composition)
        projected_manure_mass = self._select_projected_manure_mass([nitrogen_derived_manure_mass,
                                                                    phosphorus_derived_manure_mass])

        if math.isclose(projected_manure_mass, 0.0, abs_tol=1e-6):
            # Unable to fulfill request
            return None
        elif projected_manure_mass <= self._nutrients.total_manure_mass:
            # Able to fulfill the whole request
            return self._create_nutrient_request_results(projected_manure_mass)
        else:
            # Partially fulfillable, return everything we have left
            return self._create_nutrient_request_results(self._nutrients.total_manure_mass)

    @staticmethod
    def _calculate_projected_manure_mass(request_nutrient: float, nutrient_composition: float) -> float:
        """
        Calculate the projected manure mass based on the nutrient requested and the nutrient's composition in the manure.

        The projected manure mass is calculated by dividing the nutrient request by the nutrient composition.
        This represents the total manure mass needed to fulfill the nutrient request.

        Parameters
        ----------
        request_nutrient : float
            The quantity of nutrient requested. Must be a non-negative value.
        nutrient_composition : float
            The proportion of the nutrient in the manure, represented as a fraction in the range [0, 1].

        Returns
        -------
        float
            The projected manure mass needed to fulfill the nutrient request. Returns 0.0 if the nutrient
            composition is zero (indicating that the nutrient is not present in the manure).

        Raises
        ------
        ValueError
            If the request for nutrient is negative, or if the nutrient composition is not in the range [0, 1].

        """
        if request_nutrient < 0.0:
            raise ValueError(f'Request for nutrient cannot be negative: {request_nutrient}')

        if nutrient_composition < 0.0 or nutrient_composition > 1.0:
            raise ValueError(f'Nutrient composition must be between 0 and 1 (inclusive): {nutrient_composition}')
        elif nutrient_composition > 0.0:
            return request_nutrient / nutrient_composition
        else:
            return 0.0

    @staticmethod
    def _select_projected_manure_mass(projected_manure_masses: list[float]) -> float:
        """
        Select the smallest positive projected manure mass from the given list of projected manure masses.

        This method works by first checking if any of the projected manure masses are negative and raises
        a ValueError if this is the case. However, if all values are zero, it returns zero. Otherwise,
        it returns the smallest positive value.

        Parameters
        ----------
        projected_manure_masses : list[float]
            The list of projected manure masses.

        Returns
        -------
        float
            The projected manure mass.

        Raises
        ------
        ValueError
            If any of the projected manure masses is negative.

        """
        min_positive = math.inf
        for mass in projected_manure_masses:
            if mass < 0:
                raise ValueError(f'Projected manure mass cannot be negative: {mass}')
            elif 0 < mass < min_positive:
                min_positive = mass

        return min_positive if min_positive != math.inf else 0.0

    def _create_nutrient_request_results(self, projected_manure_mass: float) -> NutrientRequestResults:
        """
        Create a NutrientRequestResults object based on the given projected manure mass.

        Note that this method does not check if what is currently available in the manager is enough
        to fulfill the projected manure mass. It simply creates a NutrientRequestResults object
        based on the projected manure mass by multiplying the projected manure mass with the
        nutrient compositions.

        Parameters
        ----------
        projected_manure_mass : float
            The projected manure mass.

        Returns
        -------
        NutrientRequestResults
            The results of the nutrient request. See :class:`NutrientsRequestResults` for details.

        Raises
        ------
        ValueError
            If the projected manure mass is negative.

        """
        if projected_manure_mass < 0.0:
            raise ValueError(f'Projected manure mass cannot be negative: {projected_manure_mass}')

        return NutrientRequestResults(
            nitrogen=projected_manure_mass * self._nutrients.nitrogen_composition,
            phosphorus=projected_manure_mass * self._nutrients.phosphorus_composition,
            total_manure_mass=projected_manure_mass,
            dry_matter=projected_manure_mass * self._nutrients.dry_matter_fraction,
            dry_matter_fraction=self._nutrients.dry_matter_fraction,
        )

    def _remove_nutrients(self, results: NutrientRequestResults) -> None:
        """
        Remove nutrients from the manager based on the results of a nutrient request.

        Parameters
        ----------
        results : NutrientRequestResults
            The results of a nutrient request. See :class:`NutrientsRequestResults` for details.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If any of the nutrients in the results is greater than what is currently available in the manager.

        """
        for attr in ['nitrogen', 'phosphorus', 'total_manure_mass', 'dry_matter']:
            if getattr(self._nutrients, attr) < getattr(results, attr):
                raise ValueError(f'Remove more nutrients than available: {attr}')

        self._nutrients -= ManureNutrients(
            nitrogen=results.nitrogen,
            phosphorus=results.phosphorus,
            total_manure_mass=results.total_manure_mass,
            dry_matter=results.dry_matter,
        )
