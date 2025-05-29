from __future__ import annotations

import math

from RUFAS.output_manager import OutputManager
from RUFAS.data_structures.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType, ManureStorageType


class ManureNutrientManager:
    def __init__(self) -> None:
        """Initialize the manure nutrient manager."""
        self.om = OutputManager()

        self.nutrients_by_storage_category: [ManureStorageType, ManureNutrients] = {
            ManureStorageType.ANAEROBIC_LAGOON: ManureNutrients(manure_type=ManureType.LIQUID,
                                                                manure_storage_type=ManureStorageType.ANAEROBIC_LAGOON),
            ManureStorageType.COMPOSTING: ManureNutrients(manure_type=ManureType.SOLID,
                                                          manure_storage_type=ManureStorageType.COMPOSTING),
            ManureStorageType.COMPOST_BEDDED_PACK_BARN: ManureNutrients(
                manure_type=ManureType.SOLID,
                manure_storage_type=ManureStorageType.COMPOST_BEDDED_PACK_BARN),
            ManureStorageType.OPEN_LOT: ManureNutrients(manure_type=ManureType.SOLID,
                                                        manure_storage_type=ManureStorageType.OPEN_LOT),
            ManureStorageType.SLURRY_STORAGE_OUTDOOR: ManureNutrients(
                manure_type=ManureType.LIQUID,
                manure_storage_type=ManureStorageType.SLURRY_STORAGE_OUTDOOR),
            ManureStorageType.SLURRY_STORAGE_UNDERFLOOR: ManureNutrients(
                manure_type=ManureType.LIQUID,
                manure_storage_type=ManureStorageType.SLURRY_STORAGE_UNDERFLOOR)
        }

        self.nutrients_by_manure_category: [ManureType, ManureNutrients] = {
            ManureType.LIQUID: ManureNutrients(manure_type=ManureType.LIQUID),
            ManureType.SOLID: ManureNutrients(manure_type=ManureType.SOLID),
        }

    def get_values(self, manure_type: ManureType) -> ManureNutrients:
        """
        Get the current nutrient values stored in the manager by manure type.

        Parameters
        ----------
        manure_type : ManureType
            The type of manure.

        Returns
        -------
        ManureNutrients
            The current nutrient values stored in the manager for the provided ManureType.

        Raises
        ------
        KeyError
            If the manure type is not in the list of acceptable manure types.
        """
        if manure_type not in self.nutrients_by_manure_category:
            raise KeyError(f"Manure type {manure_type} is not managed by this manager.")
        return self.nutrients_by_manure_category[manure_type]

    def update_nutrients(self, nutrients: ManureNutrients) -> None:
        """
        Add or update nutrients to the manager from the manure module by manure type.

        Parameters
        ----------
        nutrients : ManureNutrients
            The nutrients to be added to or updated in the manager.

        Returns
        -------
        None

        """
        current_storage_nutrients = self.nutrients_by_storage_category.get(nutrients.manure_storage_type)
        current_categorical_nutrients = self.nutrients_by_manure_category.get(current_storage_nutrients.manure_type)

        updated_nutrients = ManureNutrients(
            nitrogen=current_storage_nutrients.nitrogen + nutrients.nitrogen,
            phosphorus=current_storage_nutrients.phosphorus + nutrients.phosphorus,
            potassium=current_storage_nutrients.potassium + nutrients.potassium,
            dry_matter=current_storage_nutrients.dry_matter + nutrients.dry_matter,
            total_manure_mass=current_storage_nutrients.total_manure_mass + nutrients.total_manure_mass,
            manure_storage_type=nutrients.manure_storage_type,
            manure_type=current_storage_nutrients.manure_type
        )

        updated_categorical_nutrients = ManureNutrients(
            nitrogen=current_categorical_nutrients.nitrogen + nutrients.nitrogen,
            phosphorus=current_categorical_nutrients.phosphorus + nutrients.phosphorus,
            potassium=current_categorical_nutrients.potassium + nutrients.potassium,
            dry_matter=current_categorical_nutrients.dry_matter + nutrients.dry_matter,
            total_manure_mass=current_categorical_nutrients.total_manure_mass + nutrients.total_manure_mass,
            manure_type=current_storage_nutrients.manure_type,
        )

        self.nutrients_by_storage_category[nutrients.manure_storage_type] = updated_nutrients
        self.nutrients_by_manure_category[current_storage_nutrients.manure_type] = updated_categorical_nutrients



    def request_nutrients(self, request: NutrientRequest) -> tuple[NutrientRequestResults | None, bool]:
        """
        Handle the request for specific nutrients from the crop and soil module.

        This method evaluates the nutrient request made by considering both nitrogen and phosphorus
        quantities desired for the specified manure type. It calculates the projected manure mass that
        would satisfy the request and checks against the nutrients available in the manager.

        If the request can be fulfilled either partially or wholly, the corresponding amount of nutrients
        is subtracted from the manager's internal bookkeeping for the manure type. The method then returns
        the results of the nutrient request, which detail the amounts of nutrients that can be provided to
        fulfill the request. If the request cannot be fulfilled at all, the method will return None.

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
        if eval_results is not None:
            self._remove_nutrients(eval_results, request.manure_type)
        return eval_results, is_nutrient_request_fulfilled

    def _evaluate_nutrient_request(self, request: NutrientRequest) -> tuple[NutrientRequestResults | None, bool]:
        """
        Evaluate a nutrient request. The method calculates the projected manure mass
        based on the request for nitrogen and phosphorus for a specific manure type. It then checks if the
        projected manure mass can be fulfilled by the available nutrients for that manure type in the manager.

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
        if math.isclose(projected_manure_mass, 0.0, abs_tol=1e-6):
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

    def _remove_nutrients(self, results: NutrientRequestResults, manure_type: ManureType) -> None:
        """
        Remove nutrients from the manager based on the results of a nutrient request by manure type.

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

        if manure_type not in self.nutrients_by_manure_category:
            raise ValueError(f"Invalid manure type: {manure_type}. Supported types are: {ManureType}")

        info_map = {
            "class": self.__class__.__name__,
            "function": self._remove_nutrients.__name__,
        }
        current_nutrients = self.nutrients_by_manure_category[manure_type]
        attrs_list = ["nitrogen", "phosphorus", "total_manure_mass", "dry_matter"]
        updated_results_data = {attr: 0.0 for attr in attrs_list}

        for attr in attrs_list:
            requested_amount = getattr(results, attr)
            available_amount = getattr(current_nutrients, attr)
            if requested_amount > available_amount:
                self.om.add_warning(
                    "Remove more nutrients than available",
                    f"Requested {attr} ({requested_amount}) is more than available ({available_amount})",
                    info_map,
                )
                updated_results_data[attr] = available_amount
            else:
                updated_results_data[attr] = requested_amount

        updated_results = NutrientRequestResults(**updated_results_data)

        updated_nutrients = ManureNutrients(
            nitrogen=current_nutrients.nitrogen - updated_results.nitrogen,
            phosphorus=current_nutrients.phosphorus - updated_results.phosphorus,
            dry_matter=current_nutrients.dry_matter - updated_results.dry_matter,
            total_manure_mass=current_nutrients.total_manure_mass - updated_results.total_manure_mass,
            manure_type=manure_type,
        )

        self.nutrients_by_manure_category[manure_type] = updated_nutrients
