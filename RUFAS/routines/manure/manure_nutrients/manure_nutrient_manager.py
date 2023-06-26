from __future__ import annotations

import math

from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults
from RUFAS.routines.manure.validators.general_validator import GeneralValidator


class ManureNutrientManager:
    def __init__(self):
        """Initialize the manure nutrient manager."""

        self._nutrients = ManureNutrients()

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
        Request nutrients from the crop and soil module.

        Parameters
        ----------
        request : NutrientRequest
            The request for nutrients.

        Returns
        -------
        NutrientRequestResults
            The results of the nutrient request. See :class:`NutrientsRequestResults` for details.

        Raises
        ------
        TypeError
            If the argument is not of type NutrientRequest.

        """
        GeneralValidator.check_type(request, NutrientRequest)

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

        Raises
        ------
        TypeError
            If the argument is not of type NutrientRequest.

        """
        GeneralValidator.check_type(request, NutrientRequest)

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
        Calculate the projected manure mass based on the request for a nutrient and the nutrient composition.

        Parameters
        ----------
        request_nutrient : float
            The request for a nutrient.
        nutrient_composition : float
            The nutrient composition.

        Returns
        -------
        float
            The projected manure mass.

        """
        if nutrient_composition > 0.0:
            return request_nutrient / nutrient_composition
        else:
            return 0.0

    @staticmethod
    def _select_projected_manure_mass(projected_manure_masses: list[float]) -> float:
        """
        Select the projected manure mass from a list of projected manure masses.

        Parameters
        ----------
        projected_manure_masses : list[float]
            The list of projected manure masses.

        Returns
        -------
        float
            The projected manure mass.

        """
        if all(mass > 0 for mass in projected_manure_masses):
            return min(projected_manure_masses)
        else:
            return max(projected_manure_masses)

    def _create_nutrient_request_results(self, projected_manure_mass: float) -> NutrientRequestResults:
        """
        Create a NutrientRequestResults object based on the given projected manure mass.

        Parameters
        ----------
        projected_manure_mass : float
            The projected manure mass.

        Returns
        -------
        NutrientRequestResults
            The results of the nutrient request. See :class:`NutrientsRequestResults` for details.

        """
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
        TypeError
            If the argument is not of type NutrientRequestResults.

        """
        GeneralValidator.check_type(results, NutrientRequestResults)

        self._nutrients -= ManureNutrients(
            nitrogen=results.nitrogen,
            phosphorus=results.phosphorus,
            total_manure_mass=results.total_manure_mass,
            dry_matter=results.dry_matter,
        )
