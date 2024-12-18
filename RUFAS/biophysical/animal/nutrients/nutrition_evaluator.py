from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionRequirements,
    NutritionSupply,
    NutritionEvaluationResults,
)
from RUFAS.general_constants import GeneralConstants


class NutritionEvaluator:
    """Checks if energy and nutrients supplied in a ration satisfy the demand for an individual animal."""

    @classmethod
    def evaluate_nutrition_supply(
        cls,
        requirements: NutritionRequirements,
        supply: NutritionSupply,
        is_cow: bool,
    ) -> tuple[bool, NutritionEvaluationResults]:
        """
        Calculates the difference between nutrient demand and supply, if any.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal against which the nutrient supply will be compared.
        supply : NutritionSupply
            Energy and nutrition supply against which an animal's nutrient requirements will be compared.
        is_cow : bool
            True if the animal consuming the ration is a cow, false if it is a heifer.

        Returns
        -------
        tuple[bool, NutritionEvaluationResults]
            Boolean indicating if the ration has an amount of energy and nutrients sufficient to meet the given
            requirements, and an object containing a summary of all energy and nutrient surpluses and deficiencies.

        """
        heifer_energy_nutrition_checkers = {
            "maintenance": cls._check_activity_maintenance_energy_supplied,
            "growth": cls._check_growth_energy_supplied,
            "calcium": cls._check_calcium_supplied,
            "phosphorus": cls._check_phosphorus_supplied,
            "protein": cls._check_protein_supplied,
            "ndf": cls._check_neutral_detergent_fiber_supplied,
            "fat": cls._check_fat_content,
            "dry_matter": cls._check_dry_matter_intake,
        }
        cow_energy_nutrition_checkers = heifer_energy_nutrition_checkers + {
            "total_energy": cls._check_total_energy_supplied,
            "lactation": cls._check_lactation_energy_supplied,
        }

        checkers = cow_energy_nutrition_checkers if is_cow else heifer_energy_nutrition_checkers
        results = {name: method(requirements, supply) for name, method in checkers.items()}

        evaluation = NutritionEvaluationResults(
            total_energy=results.get("total_energy"),
            maintenance=results["maintentance"],
            lactation=results.get("lactation"),
            growth=results["growth"],
            calcium=results["calcium"],
            phosphorus=results["phosphorus"],
            protein=results["protein"],
            ndf=results["ndf"],
            fat=results["fat"],
            dry_matter=results["dry_matter"],
        )

        is_valid_ration = evaluation.is_valid_cow_ration if is_cow else evaluation.is_valid_heifer_ration
        return is_valid_ration, evaluation

    @classmethod
    def _check_total_energy_supplied(requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts of total energy.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the total energy supplied and the total energy required (Mcal).

        """
        energy_supplied: float = max(supply.maintenance, supply.lactation, supply.growth)

        total_energy_requirement = sum(
            [
                requirements.lactation,
                requirements.growth,
                requirements.maintenance,
                requirements.activity,
                requirements.pregnancy,
            ]
        )

        return energy_supplied - total_energy_requirement

    @classmethod
    def _check_activity_maintenance_energy_supplied(
        requirements: NutritionRequirements, supply: NutritionSupply
    ) -> float:
        """
        Calculates difference between the supplied and required amounts energy for maintenance.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the maintenance energy supplied and the maintenance energy required (Mcal).

        """
        energy_requirement = requirements.activity + requirements.maintenance

        return supply.maintenance - energy_requirement

    @classmethod
    def _check_lactation_energy_supplied(requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts energy for lactation.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the lactation energy supplied and the lactation energy required (Mcal).

        """
        energy_requirement = requirements.lactation + requirements.pregnancy

        return supply.lactation - energy_requirement

    @classmethod
    def _check_growth_energy_supplied(requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts energy for growth.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the growth energy supplied and the growth energy required (Mcal).

        """
        return supply.growth - requirements.growth

    @classmethod
    def _check_calcium_supplied(requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts of calcium.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the calcium supplied and the calcium required (g).

        """
        return supply.calcium - requirements.calcium

    @classmethod
    def _check_phosphorus_supplied(requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts of phosphorus.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the phosphorus supplied and the phosphorus required (g).

        """
        requirement = max(requirements.phosphorus, requirements.secondary_phosphorus)

        return supply.phosphorus - requirement

    @classmethod
    def _check_protein_supplied(requirements: NutritionRequirements, supply: NutritionSupply) -> bool:
        """
        Calculates amount by which supplied protein under- or overshoots the required amount of protein.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Amount by which supplied protein under- or overshoots the required protein range (g).

        """
        upper_protein_limit = requirements.protein * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR

        if supply.protein < requirements.protein:
            return supply.protein - requirements.protein
        elif supply.protein > upper_protein_limit:
            return supply.protein - upper_protein_limit
        else:
            return 0.0

    @classmethod
    def _check_neutral_detergent_fiber_supplied(_: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates amount by which supplied neutral detergent fiber (NDF) under- or overshoots the required amount of
        NDF.

        Parameters
        ----------
        _ : NutritionRequirements
            This argument is provided to keep the method signature uniform with other helper methods.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Percentage by which supplied NDF under- or overshoots the required NDF range.

        """
        ndf_percentage = supply.ndf_content / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        if ndf_percentage < AnimalModuleConstants.MINIMUM_NDF:
            return ndf_percentage - AnimalModuleConstants.MINIMUM_NDF
        elif ndf_percentage > AnimalModuleConstants.MAXIMUM_NDF:
            return ndf_percentage - AnimalModuleConstants.MAXIMUM_NDF
        else:
            return 0.0

    @classmethod
    def _check_fat_content(_: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required percentages of fat in the ration.

        Parameters
        ----------
        _ : NutritionRequirements
            This argument is provided to keep the method signature uniform with other helper methods.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the phosphorus supplied and the phosphorus required (g).

        """
        fat_percentage = supply.fat_content / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        return fat_percentage - AnimalModuleConstants.MINIMUM_FAT

    @classmethod
    def _check_dry_matter_intake(requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """Checks that the dry matter supplied meets the requirement."""
        """
        Calculates amount by which supplied dry matter under- or overshoots the required amount dry matter.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements of an animal.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Amount by which supplied dry matter under- or overshoots the required dry matter range (kg).

        """
        lower_dry_matter_limit = requirements.dry_matter * (1.0 - AnimalModuleConstants.DMI_CONSTRAINT_FRACTION)
        upper_dry_matter_limit = requirements.dry_matter * (1.0 + AnimalModuleConstants.DMI_CONSTRAINT_FRACTION)

        if supply.dry_matter < lower_dry_matter_limit:
            return supply.dry_matter - lower_dry_matter_limit
        elif supply.dry_matter > upper_dry_matter_limit:
            return supply.dry_matter - upper_dry_matter_limit
        else:
            return 0.0
