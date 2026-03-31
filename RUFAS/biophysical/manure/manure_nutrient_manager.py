from __future__ import annotations

import math
from typing import Any

from RUFAS.output_manager import OutputManager
from RUFAS.data_structures.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType


class ManureNutrientManager:
    def __init__(self) -> None:
        """Initialize the manure nutrient manager."""
        self.om = OutputManager()

        self.nutrients_by_manure_category: dict[ManureType, ManureNutrients] = {
            ManureType.LIQUID: ManureNutrients(manure_type=ManureType.LIQUID),
            ManureType.SOLID: ManureNutrients(manure_type=ManureType.SOLID),
        }

    def reset_nutrient_pools(self) -> None:
        """Resets all the pools."""
        for manure_type, pool in self.nutrients_by_manure_category.items():
            self.nutrients_by_manure_category[manure_type] = pool.reset_values()

    def add_nutrients(self, nutrients: ManureNutrients) -> None:
        """
        Add or update nutrients to the manager from the manure module by manure type.

        Parameters
        ----------
        nutrients : ManureNutrients
            The nutrients to be added to or updated in the manager.

        """
        current_nutrients = self.nutrients_by_manure_category.get(nutrients.manure_type)

        updated_categorical_nutrients = ManureNutrients(
            nitrogen=current_nutrients.nitrogen + nutrients.nitrogen,
            phosphorus=current_nutrients.phosphorus + nutrients.phosphorus,
            potassium=current_nutrients.potassium + nutrients.potassium,
            dry_matter=current_nutrients.dry_matter + nutrients.dry_matter,
            total_manure_mass=current_nutrients.total_manure_mass + nutrients.total_manure_mass,
            manure_type=nutrients.manure_type,
        )

        self.nutrients_by_manure_category[nutrients.manure_type] = updated_categorical_nutrients

    def remove_nutrients(self, removal_details: dict[str, Any]) -> None:
        """
        Removes the nutrients from both categorical and type nutrient pool.

        Parameters
        ----------
        removal_details : dict[str, Any]
            The details of nutrients removed from each storage

        """
        current_pool_by_category = self.nutrients_by_manure_category[removal_details.get("manure_type")]

        nitrogen_amount_after_renewal = current_pool_by_category.nitrogen - removal_details.get("nitrogen", 0.0)
        phosphorus_amount_after_renewal = current_pool_by_category.phosphorus - removal_details.get("phosphorus", 0.0)
        potassium_amount_after_renewal = current_pool_by_category.potassium - removal_details.get("potassium", 0.0)
        total_manure_mass_after_renewal = (
            current_pool_by_category.total_manure_mass
            - removal_details.get("water", 0.0)
            - removal_details.get("total_solids", 0.0)
        )
        dry_matter_after_renewal = current_pool_by_category.dry_matter - removal_details.get("total_solids", 0.0)
        category_amount_after_renewal = ManureNutrients(
            manure_type=current_pool_by_category.manure_type,
            nitrogen=nitrogen_amount_after_renewal if nitrogen_amount_after_renewal > 1e-3 else 0.0,
            phosphorus=phosphorus_amount_after_renewal if phosphorus_amount_after_renewal > 1e-3 else 0.0,
            potassium=potassium_amount_after_renewal if potassium_amount_after_renewal > 1e-3 else 0.0,
            total_manure_mass=total_manure_mass_after_renewal if total_manure_mass_after_renewal > 1e-3 else 0.0,
            dry_matter=dry_matter_after_renewal if dry_matter_after_renewal > 1e-3 else 0.0,
        )

        self.nutrients_by_manure_category[current_pool_by_category.manure_type] = category_amount_after_renewal

    def handle_nutrient_request(self, request: NutrientRequest) -> tuple[NutrientRequestResults | None, bool]:
        """
        Attempts to fulfill a nutrient request using available manure in the manager.
        This method evaluates the given nutrient request (including nitrogen, phosphorus, and manure type)
        and checks if the available nutrient pool can satisfy it. If the request can be met fully or partially,
        the corresponding nutrients are removed from the manager and a result is returned.

        Parameters
        ----------
        request : NutrientRequest
            The specific nutrient request, including quantities of nitrogen and phosphorus and manure type.

        Returns
        -------
        tuple[NutrientRequestResults | None, bool]
            A tuple containing the results of the nutrient request and a boolean indicating whether additional
            manure would be needed to fulfill the request. If the request cannot be fulfilled at all, the first
            element of the tuple will be None.

        """
        eval_results, is_nutrient_request_fulfilled = self._evaluate_nutrient_request(request)
        return eval_results, is_nutrient_request_fulfilled

    def _evaluate_nutrient_request(self, request: NutrientRequest) -> tuple[NutrientRequestResults | None, bool]:
        """
        The method calculates the projected manure mass.

        Parameters
        ----------
        request : NutrientRequest
            The request for nutrients.

        Returns
        -------
        tuple[NutrientRequestResults | None, bool]
            A tuple containing the results of the nutrient request and a boolean indicating whether additional
            manure would be needed to fulfill the request. If the request cannot be fulfilled at all, the first
            element of the tuple will be None.
        """
        is_nutrient_request_fulfilled = False
        nitrogen_derived_manure_mass = self.calculate_projected_manure_mass(
            request.nitrogen,
            self.nutrients_by_manure_category[request.manure_type].nitrogen_composition,
        )
        phosphorus_derived_manure_mass = self.calculate_projected_manure_mass(
            request.phosphorus,
            self.nutrients_by_manure_category[request.manure_type].phosphorus_composition,
        )
        projected_manure_mass = self._select_projected_manure_mass(
            [nitrogen_derived_manure_mass, phosphorus_derived_manure_mass]
        )
        info_map = {"class": self.__class__.__name__, "function": self._evaluate_nutrient_request.__name__}
        if math.isclose(projected_manure_mass, 0.0, abs_tol=1e-5):
            self.om.add_warning(
                "Unable to fulfill request with on-farm manure", "Projected manure mass is zero kg.", info_map
            )
            return None, is_nutrient_request_fulfilled
        elif projected_manure_mass <= self.nutrients_by_manure_category[request.manure_type].total_manure_mass:
            is_nutrient_request_fulfilled = True
            self.om.add_log("Request fulfilled", f"Projected manure mass: {projected_manure_mass} kg.", info_map)
            return (
                self._create_nutrient_request_results(projected_manure_mass, request.manure_type),
                is_nutrient_request_fulfilled,
            )
        else:
            self.om.add_warning(
                "Partial request fulfilled",
                "Not adequate manure on farm to fulfill request. "
                f"Projected manure mass: {projected_manure_mass} kg.",
                info_map,
            )
            return (
                self._create_nutrient_request_results(
                    self.nutrients_by_manure_category[request.manure_type].total_manure_mass,
                    request.manure_type,
                ),
                is_nutrient_request_fulfilled,
            )

    @staticmethod
    def calculate_projected_manure_mass(request_nutrient: float, nutrient_composition: float) -> float:
        """
        Calculate the projected manure mass based on the nutrient requested and the nutrient's composition
        in the manure.

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
            If the request for nutrient is negative.
            If the nutrient composition is not in the range [0, 1].

        """
        if request_nutrient < 0.0:
            raise ValueError(f"Request for nutrient cannot be negative: {request_nutrient}")

        if nutrient_composition < 0.0 or nutrient_composition > 1.0:
            raise ValueError(f"Nutrient composition must be between 0 and 1 (inclusive): {nutrient_composition}")
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
                raise ValueError(f"Projected manure mass cannot be negative: {mass}")
            elif 0 < mass < min_positive:
                min_positive = mass

        return min_positive if min_positive != math.inf else 0.0

    def _create_nutrient_request_results(
        self, projected_manure_mass: float, manure_type: ManureType
    ) -> NutrientRequestResults:
        """
        Create a NutrientRequestResults object based on the given projected manure mass and manure type.

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
            raise ValueError(f"Projected manure mass cannot be negative: {projected_manure_mass}")

        return NutrientRequestResults(
            nitrogen=projected_manure_mass * self.nutrients_by_manure_category[manure_type].nitrogen_composition,
            phosphorus=projected_manure_mass * self.nutrients_by_manure_category[manure_type].phosphorus_composition,
            total_manure_mass=projected_manure_mass,
            dry_matter=projected_manure_mass * self.nutrients_by_manure_category[manure_type].dry_matter_fraction,
            dry_matter_fraction=self.nutrients_by_manure_category[manure_type].dry_matter_fraction,
        )
