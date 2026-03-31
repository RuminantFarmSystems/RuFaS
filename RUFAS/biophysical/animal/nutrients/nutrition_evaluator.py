from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionRequirements,
    NutritionSupply,
    NutritionEvaluationResults,
)
from RUFAS.general_constants import GeneralConstants


class NutritionEvaluator:
    """Checks if energy and nutrients supplied in a ration satisfy the demand of an animal or a pen's average demand."""

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
            Energy and nutrition requirements against which the nutrient supply will be compared.
        supply : NutritionSupply
            Energy and nutrition supply against which nutrient requirements will be compared.
        is_cow : bool
            True if the requirements are for a cow or cows, false if they are for a heifer or heifer pen.

        Returns
        -------
        tuple[bool, NutritionEvaluationResults]
            Boolean indicating if the ration has an amount of energy and nutrients sufficient to meet the given
            requirements, and an object containing a summary of all energy and nutrient surpluses and deficiencies.

        """
        heifer_energy_nutrition_checkers = {
            "maintenance": cls._calculate_activity_maintenance_energy_supplied,
            "growth": cls._calculate_growth_energy_supplied,
            "calcium": cls._calculate_calcium_supplied,
            "phosphorus": cls._calculate_phosphorus_supplied,
            "protein": cls._calculate_protein_supplied,
            "ndf_supplied": cls._calculate_neutral_detergent_fiber_supplied,
            "forage_ndf_supplied": cls._calculate_forage_neutral_detergent_fiber_supplied,
            "fat_supplied": cls._calculate_fat_supplied,
            "dry_matter": cls._calculate_dry_matter_intake,
        }
        cow_energy_nutrition_checkers = heifer_energy_nutrition_checkers | {
            "total_energy": cls._calculate_total_energy_supplied,
            "lactation": cls._calculate_lactation_energy_supplied,
        }

        checkers = cow_energy_nutrition_checkers if is_cow else heifer_energy_nutrition_checkers
        results = {name: method(requirements, supply) for name, method in checkers.items()}

        evaluation = NutritionEvaluationResults(
            total_energy=results.get("total_energy"),
            maintenance_energy=results["maintenance"],
            lactation_energy=results.get("lactation"),
            growth_energy=results["growth"],
            calcium=results["calcium"],
            phosphorus=results["phosphorus"],
            metabolizable_protein=results["protein"],
            ndf_percent=results["ndf_supplied"],
            forage_ndf_percent=results["forage_ndf_supplied"],
            fat_percent=results["fat_supplied"],
            dry_matter=results["dry_matter"],
        )

        is_valid_ration = evaluation.is_valid_cow_ration if is_cow else evaluation.is_valid_heifer_ration
        return is_valid_ration, evaluation

    @classmethod
    def _calculate_total_energy_supplied(cls, requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts of total energy.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the total energy supplied and the total energy required (Mcal).

        """
        energy_supplied: float = max(supply.maintenance_energy, supply.lactation_energy, supply.growth_energy)

        return energy_supplied - requirements.total_energy_requirement

    @classmethod
    def _calculate_activity_maintenance_energy_supplied(
        cls, requirements: NutritionRequirements, supply: NutritionSupply
    ) -> float:
        """
        Calculates difference between the supplied and required amounts energy for maintenance.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the maintenance energy supplied and the maintenance energy required (Mcal).

        """
        energy_requirement = requirements.activity_energy + requirements.maintenance_energy

        return supply.maintenance_energy - energy_requirement

    @classmethod
    def _calculate_lactation_energy_supplied(
        cls, requirements: NutritionRequirements, supply: NutritionSupply
    ) -> float:
        """
        Calculates difference between the supplied and required amounts energy for lactation.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the lactation energy supplied and the lactation energy required (Mcal).

        """
        energy_requirement = requirements.lactation_energy + requirements.pregnancy_energy

        return supply.lactation_energy - energy_requirement

    @classmethod
    def _calculate_growth_energy_supplied(cls, requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts energy for growth.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the growth energy supplied and the growth energy required (Mcal).

        """
        return supply.growth_energy - requirements.growth_energy

    @classmethod
    def _calculate_calcium_supplied(cls, requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts of calcium.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the calcium supplied and the calcium required (g).

        """
        return supply.calcium - requirements.calcium

    @classmethod
    def _calculate_phosphorus_supplied(cls, requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates difference between the supplied and required amounts of phosphorus.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Difference between the phosphorus supplied and the phosphorus required (g).

        """
        requirement = max(requirements.phosphorus, requirements.process_based_phosphorus)

        return supply.phosphorus - requirement

    @classmethod
    def _calculate_protein_supplied(cls, requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates amount by which supplied protein under- or overshoots the required amount of protein.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
        supply : NutritionSupply
            Energy and nutrition supplied by a ration.

        Returns
        -------
        float
            Amount by which supplied protein under- or overshoots the required protein range (g).

        """
        upper_protein_limit = requirements.metabolizable_protein * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR

        if supply.metabolizable_protein < requirements.metabolizable_protein:
            return supply.metabolizable_protein - requirements.metabolizable_protein
        elif supply.metabolizable_protein > upper_protein_limit:
            return supply.metabolizable_protein - upper_protein_limit
        else:
            return 0.0

    @classmethod
    def _calculate_neutral_detergent_fiber_supplied(cls, _: NutritionRequirements, supply: NutritionSupply) -> float:
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
            Percentage by which supplied NDF under- or overshoots the required NDF range (percent).

        """
        if supply.dry_matter == 0.0:
            return 0.0
        ndf_percentage = supply.ndf_supply / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        if ndf_percentage < AnimalModuleConstants.MINIMUM_RATION_NDF:
            return ndf_percentage - AnimalModuleConstants.MINIMUM_RATION_NDF
        elif ndf_percentage > AnimalModuleConstants.MAXIMUM_RATION_NDF:
            return ndf_percentage - AnimalModuleConstants.MAXIMUM_RATION_NDF
        else:
            return 0.0

    @classmethod
    def _calculate_forage_neutral_detergent_fiber_supplied(
        cls, _: NutritionRequirements, supply: NutritionSupply
    ) -> float:
        """
        Calculates amount by which supplied neutral detergent fiber (NDF) from forage undershoots the required amount of
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
            Percentage by which supplied NDF undershoots the required NDF range (percent).

        """
        if supply.dry_matter == 0.0:
            return 0.0
        forage_ndf_percentage = supply.forage_ndf_supply / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        return forage_ndf_percentage - AnimalModuleConstants.MINIMUM_RATION_FORAGE_NDF

    @classmethod
    def _calculate_fat_supplied(cls, _: NutritionRequirements, supply: NutritionSupply) -> float:
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
            Percentage by which supplied fat under- or overshoots the required fat range (percent).

        """
        if supply.dry_matter == 0.0:
            return 0.0
        fat_percentage = supply.fat_supply / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        return AnimalModuleConstants.MAXIMUM_RATION_FAT - fat_percentage

    @classmethod
    def _calculate_dry_matter_intake(cls, requirements: NutritionRequirements, supply: NutritionSupply) -> float:
        """
        Calculates amount by which supplied dry matter under- or overshoots the required amount dry matter.

        Parameters
        ----------
        requirements : NutritionRequirements
            Energy and nutrition requirements.
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
