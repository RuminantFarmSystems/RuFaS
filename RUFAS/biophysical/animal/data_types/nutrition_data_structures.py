from dataclasses import dataclass, field

from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants


@dataclass
class NutritionRequirements:
    """
    Energy and nutrition requirements.

    Attributes
    ----------
    maintenance_energy : float
        Net energy requirement for maintenance (Mcal).
    growth_energy : float
        Net energy requirement for growth (Mcal).
    pregnancy_energy : float
        Net energy requirement for pregnancy (Mcal).
    lactation_energy : float
        Net energy requirement for lactation (Mcal).
    metabolizable_protein : float
        Metabolizable protein requirement (g).
    calcium : float
        Calcium requirement (g).
    phosphorus : float
        Phosphorus requirement calculated with either the NASEM or NRC methodologies (g).
    process_based_phosphorus : float
        Phosphorus requirement calculated with the dedicated animal phosphorus submodule (g).
    dry_matter : float
        Dry matter intake requirement (kg).
    activity_energy : float
        Net energy requirement for activity (Mcal).
    essential_amino_acids : EssentialAminoAcidRequirements
        Essential amino acid requirements.

    """

    maintenance_energy: float
    growth_energy: float
    pregnancy_energy: float
    lactation_energy: float
    metabolizable_protein: float
    calcium: float
    phosphorus: float
    process_based_phosphorus: float
    dry_matter: float
    activity_energy: float
    essential_amino_acids: EssentialAminoAcidRequirements

    UNITS = {
        "NEmaint_requirement": MeasurementUnits.MEGACALORIES,
        "NEa_requirement": MeasurementUnits.MEGACALORIES,
        "NEg_requirement": MeasurementUnits.MEGACALORIES,
        "NEpreg_requirement": MeasurementUnits.MEGACALORIES,
        "NEl_requirement": MeasurementUnits.MEGACALORIES,
        "MP_requirement": MeasurementUnits.GRAMS,
        "Ca_requirement": MeasurementUnits.GRAMS,
        "P_req": MeasurementUnits.GRAMS,
        "P_req_process": MeasurementUnits.GRAMS,
        "DMIest_requirement": MeasurementUnits.KILOGRAMS,
        "avg_BW": MeasurementUnits.KILOGRAMS,
        "avg_milk_production_reduction_pen": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "avg_essential_amino_acid_requirement": MeasurementUnits.GRAMS_PER_DAY,
    }

    def __add__(self, other: "NutritionRequirements") -> "NutritionRequirements":
        """Add two NutritionRequirements objects together."""
        return NutritionRequirements(
            maintenance_energy=self.maintenance_energy + other.maintenance_energy,
            growth_energy=self.growth_energy + other.growth_energy,
            pregnancy_energy=self.pregnancy_energy + other.pregnancy_energy,
            lactation_energy=self.lactation_energy + other.lactation_energy,
            metabolizable_protein=self.metabolizable_protein + other.metabolizable_protein,
            calcium=self.calcium + other.calcium,
            phosphorus=self.phosphorus + other.phosphorus,
            process_based_phosphorus=self.process_based_phosphorus + other.process_based_phosphorus,
            dry_matter=self.dry_matter + other.dry_matter,
            activity_energy=self.activity_energy + other.activity_energy,
            essential_amino_acids=self.essential_amino_acids + other.essential_amino_acids,
        )

    def __truediv__(self, divisor: float) -> "NutritionRequirements":
        """Divide all NutritionRequirements values by a scalar."""
        if divisor == 0.0:
            raise ZeroDivisionError("Cannot divide NutritionRequirements by zero.")
        return NutritionRequirements(
            maintenance_energy=self.maintenance_energy / divisor,
            growth_energy=self.growth_energy / divisor,
            pregnancy_energy=self.pregnancy_energy / divisor,
            lactation_energy=self.lactation_energy / divisor,
            metabolizable_protein=self.metabolizable_protein / divisor,
            calcium=self.calcium / divisor,
            phosphorus=self.phosphorus / divisor,
            process_based_phosphorus=self.process_based_phosphorus / divisor,
            dry_matter=self.dry_matter / divisor,
            activity_energy=self.activity_energy / divisor,
            essential_amino_acids=self.essential_amino_acids / divisor,
        )

    @property
    def total_energy_requirement(self) -> float:
        """Total energy requirement for an animal (Mcal)."""
        return (
            self.maintenance_energy
            + self.growth_energy
            + self.pregnancy_energy
            + self.lactation_energy
            + self.activity_energy
        )

    @classmethod
    def make_empty_nutrition_requirements(cls) -> "NutritionRequirements":
        """Makes an empty NutritionRequirements instance."""
        return NutritionRequirements(
            maintenance_energy=0.0,
            growth_energy=0.0,
            pregnancy_energy=0.0,
            lactation_energy=0.0,
            metabolizable_protein=0.0,
            calcium=0.0,
            phosphorus=0.0,
            process_based_phosphorus=0.0,
            dry_matter=0.0,
            activity_energy=0.0,
            essential_amino_acids=EssentialAminoAcidRequirements(
                histidine=0.0,
                isoleucine=0.0,
                leucine=0.0,
                lysine=0.0,
                methionine=0.0,
                phenylalanine=0.0,
                threonine=0.0,
                thryptophan=0.0,
                valine=0.0,
            ),
        )


@dataclass
class NutritionSupply:
    """
    Energy and nutrition supply for a ration.

    Attributes
    ----------
    metabolizable_energy : float
        Total metabolizable energy in a ration (Mcal).
    maintenance_energy : float
        Energy available for maintenance in a ration (Mcal).
    lactation_energy : float
        Energy available for lactation in a ration (Mcal).
    growth_energy : float
        Energy available for growth in a ration (Mcal).
    metabolizable_protein : float
        Metabolizable protein supplied in a ration (g).
    calcium : float
        Calcium supplied in a ration (g).
    phosphorus : float
        Phosphorus supplied in a ration (g).
    dry_matter : float
        Total dry matter supply of a ration (kg).
    wet_matter : float
        Total wet matter or fresh mass supply of a ration (kg).
    ndf_supply : float
        Total neutral detergent fiber (NDF) supplied by the ration (kg).
    forage_ndf_supply : float
        Total NDF supplied by forages in the ration (kg).
    fat_supply : float
        Total fat supplied by the ration (kg).
    crude_protein : float
        Total crude protein supplied by the ration (kg).
    adf_supply : float
        Total Acid Detergent Fiber (ADF) supplied by the ration (kg).
    digestible_energy_supply : float
        Total amount of digestible energy (DE) supplied by the ration (Mcal). This value is calculated with the "DE"
        attribute of a Feed when using the NRC methodology, and "DE_Base" when using NASEM.
    tdn_supply : float
        Total Digestible Nutrients (TDN) supplied by the ration (kg).
    lignin_supply : float
        Total lignin supplied by the ration (kg).
    ash_supply : float
        Total ash supplied by the ration (kg).
    potassium_supply : float
        Total potassium supplied by the ration (kg).
    starch_supply : float
        Total starch supplied by the ration (kg).
    byproduct_supply : float
        Total dry matter in the matter made up of byproducts (kg).
    nitrogen_supply : float
        Total nitrogen supplied by the ration (kg). This value is derived from the crude protein supply.

    """

    metabolizable_energy: float
    maintenance_energy: float
    lactation_energy: float
    growth_energy: float
    metabolizable_protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    wet_matter: float
    ndf_supply: float
    forage_ndf_supply: float
    fat_supply: float
    crude_protein: float
    adf_supply: float
    digestible_energy_supply: float
    tdn_supply: float
    lignin_supply: float
    ash_supply: float
    potassium_supply: float
    starch_supply: float
    byproduct_supply: float
    nitrogen_supply: float = field(init=False)

    UNITS = {
        "dm": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "CP": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "ADF": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "NDF": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "lignin": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "ash": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "phosphorus": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "potassium": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "N": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "as_fed": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "EE": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "starch": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "TDN": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "DE": MeasurementUnits.MEGACALORIES,
        "calcium": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
        "fat": MeasurementUnits.GRAMS,
        "fat_percentage": MeasurementUnits.PERCENT,
        "forage_ndf": MeasurementUnits.KILOGRAMS,
        "forage_ndf_percent": MeasurementUnits.PERCENT_OF_DRY_MATTER,
        "ME": MeasurementUnits.MEGACALORIES,
        "NE_maintenance_and_activity": MeasurementUnits.MEGACALORIES,
        "NE_lactation": MeasurementUnits.MEGACALORIES,
        "NE_growth": MeasurementUnits.MEGACALORIES,
        "metabolizable_protein": MeasurementUnits.GRAMS,
    }

    def __post_init__(self) -> None:
        """Sets the nitrogen supply of a ration based on the crude protein supply."""
        self.nitrogen_supply = self.crude_protein * UserConstants.PROTEIN_TO_NITROGEN

    def __add__(self, other: "NutritionSupply") -> "NutritionSupply":
        """Add two NutritionSupply objects together."""
        return NutritionSupply(
            metabolizable_energy=self.metabolizable_energy + other.metabolizable_energy,
            maintenance_energy=self.maintenance_energy + other.maintenance_energy,
            lactation_energy=self.lactation_energy + other.lactation_energy,
            growth_energy=self.growth_energy + other.growth_energy,
            metabolizable_protein=self.metabolizable_protein + other.metabolizable_protein,
            calcium=self.calcium + other.calcium,
            phosphorus=self.phosphorus + other.phosphorus,
            dry_matter=self.dry_matter + other.dry_matter,
            wet_matter=self.wet_matter + other.wet_matter,
            ndf_supply=self.ndf_supply + other.ndf_supply,
            fat_supply=self.fat_supply + other.fat_supply,
            crude_protein=self.crude_protein + other.crude_protein,
            adf_supply=self.adf_supply + other.adf_supply,
            digestible_energy_supply=self.digestible_energy_supply + other.digestible_energy_supply,
            tdn_supply=self.tdn_supply + other.tdn_supply,
            lignin_supply=self.lignin_supply + other.lignin_supply,
            ash_supply=self.ash_supply + other.ash_supply,
            potassium_supply=self.potassium_supply + other.potassium_supply,
            starch_supply=self.starch_supply + other.starch_supply,
            byproduct_supply=self.byproduct_supply + other.byproduct_supply,
            forage_ndf_supply=self.forage_ndf_supply + other.forage_ndf_supply,
        )

    def __truediv__(self, divisor: float | int) -> "NutritionSupply":
        """Divides a NutritionSupply object by a scalar."""
        if divisor == 0.0:
            raise ZeroDivisionError("Cannot divide NutritionSupply by zero.")

        return NutritionSupply(
            metabolizable_energy=self.metabolizable_energy / divisor,
            maintenance_energy=self.maintenance_energy / divisor,
            lactation_energy=self.lactation_energy / divisor,
            growth_energy=self.growth_energy / divisor,
            metabolizable_protein=self.metabolizable_protein / divisor,
            calcium=self.calcium / divisor,
            phosphorus=self.phosphorus / divisor,
            dry_matter=self.dry_matter / divisor,
            wet_matter=self.wet_matter / divisor,
            ndf_supply=self.ndf_supply / divisor,
            fat_supply=self.fat_supply / divisor,
            crude_protein=self.crude_protein / divisor,
            adf_supply=self.adf_supply / divisor,
            digestible_energy_supply=self.digestible_energy_supply / divisor,
            tdn_supply=self.tdn_supply / divisor,
            lignin_supply=self.lignin_supply / divisor,
            ash_supply=self.ash_supply / divisor,
            potassium_supply=self.potassium_supply / divisor,
            starch_supply=self.starch_supply / divisor,
            byproduct_supply=self.byproduct_supply / divisor,
            forage_ndf_supply=self.forage_ndf_supply / divisor,
        )

    @property
    def adf_percentage(self) -> float:
        """Acid Detergent Fiber (ADF) concentration of the dry matter content (percent)."""
        return self.adf_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def ash_percentage(self) -> float:
        """Ash concentration of the dry matter content (percent)."""
        return self.ash_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def crude_protein_percentage(self) -> float:
        """Crude protein concentration of the dry matter content (percent)."""
        return self.crude_protein / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def dry_matter_percentage(self) -> float:
        """Dry matter concentration of the nutrition supply's wet or fresh mass (percent)."""
        return self.dry_matter / self.wet_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def fat_percentage(self) -> float:
        """Fat concentration of the dry matter content (percent)."""
        return self.fat_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def ndf_percentage(self) -> float:
        """Neutral Detergent Fiber (NDF) concentration of the dry matter content (percent)."""
        return self.ndf_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def forage_ndf_percentage(self) -> float:
        """NDF concentration of the dry matter content supplied by forages (percent)."""
        return self.forage_ndf_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def potassium_percentage(self) -> float:
        """Potassium concentration of the dry matter content (percent)."""
        return self.potassium_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @property
    def starch_percentage(self) -> float:
        """Starch concentration of the dry matter content (percent)."""
        return self.starch_supply / self.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

    @classmethod
    def make_empty_nutrition_supply(cls) -> "NutritionSupply":
        """Manufactures an empty NutritionSupply object."""
        return NutritionSupply(
            metabolizable_energy=0.0,
            maintenance_energy=0.0,
            lactation_energy=0.0,
            growth_energy=0.0,
            metabolizable_protein=0.0,
            calcium=0.0,
            phosphorus=0.0,
            dry_matter=0.0,
            wet_matter=0.0,
            ndf_supply=0.0,
            fat_supply=0.0,
            crude_protein=0.0,
            adf_supply=0.0,
            digestible_energy_supply=0.0,
            tdn_supply=0.0,
            lignin_supply=0.0,
            ash_supply=0.0,
            potassium_supply=0.0,
            starch_supply=0.0,
            byproduct_supply=0.0,
            forage_ndf_supply=0.0,
        )


@dataclass
class NutritionEvaluationResults:
    """
    Results of evaluating whether a ration supplied the required energy and nutrients.

    Attributes
    ----------
    total_energy : float | None
        Surplus or deficit of total energy in a ration (Mcal). Necessary to know for cows, not heifers because it
        accounts for some energy demands that are not relevant to all heifers (for example, lactation for growing
        heifers).
    maintenance_energy : float
        Surplus or deficit of energy in a ration for maintenance (Mcal).
    lactation_energy : float | None
        Surplus or deficit of lactation in a ration (Mcal). This value is None when evaluating nutrition requirements of
        heifers, because they are never lactating.
    growth_energy : float
        Surplus or deficit of energy in a ration for growth (Mcal).
    metabolizable_protein : float
        Amount of metabolizable protein by which a ration was outside the acceptable bounds (g). If protein is within
        acceptable bounds, this value will be 0.0.
    calcium : float
        Surplus or deficit of calcium in a ration (g).
    phosphorus : float
        Surplus or deficit of phosphorus in a ration (g).
    dry_matter : float
        Amount of dry matter by which a ration was outside the acceptable bounds (kg). If dry matter is within
        acceptable bounds, this value will be 0.0.
    ndf_percent : float
        Surplus or deficit of neutral detergent fiber (NDF) percentage in a ration. If NDF percentage is within
        acceptable bounds, this value will be 0.0.
    forage_ndf_percent : float
        Surplus or deficit of neutral detergent fiber (NDF) percentage supplied by forages in a ration.
    fat_percent : float
        Surplus or deficit of fat percentage in a ration. If fat percentage is within acceptable bounds, this value will
        be 0.0.
    is_valid_heifer_ration : bool
        True if evaluated nutrient supply meets requirements for heifers, else false.
    is_valid_cow_ration : bool
        True if evaluated nutrient supply meets requirements for cows, else false.

    """

    total_energy: float | None
    maintenance_energy: float
    lactation_energy: float | None
    growth_energy: float
    metabolizable_protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    ndf_percent: float
    forage_ndf_percent: float
    fat_percent: float

    UNITS = {
        "total_energy_difference": MeasurementUnits.MEGACALORIES,
        "maintenance_energy_difference": MeasurementUnits.MEGACALORIES,
        "lactation_energy_difference": MeasurementUnits.MEGACALORIES,
        "growth_energy_difference": MeasurementUnits.MEGACALORIES,
        "metabolizable_protein_difference": MeasurementUnits.GRAMS,
        "calcium_difference": MeasurementUnits.GRAMS,
        "phosphorus_difference": MeasurementUnits.GRAMS,
        "dry_matter_difference": MeasurementUnits.KILOGRAMS,
        "ndf_percent_difference": MeasurementUnits.PERCENT,
        "forage_ndf_percent_difference": MeasurementUnits.PERCENT,
        "fat_percent_difference": MeasurementUnits.PERCENT,
    }

    REPORT_UNITS = {
        "is_valid_heifer_ration": MeasurementUnits.UNITLESS,
        "is_valid_cow_ration": MeasurementUnits.UNITLESS,
        "total_energy_acceptable": MeasurementUnits.UNITLESS,
        "maintenance_energy_acceptable": MeasurementUnits.UNITLESS,
        "lactation_energy_acceptable": MeasurementUnits.UNITLESS,
        "growth_energy_acceptable": MeasurementUnits.UNITLESS,
        "metabolizable_protein_acceptable": MeasurementUnits.UNITLESS,
        "calcium_acceptable": MeasurementUnits.UNITLESS,
        "phosphorus_acceptable": MeasurementUnits.UNITLESS,
        "dry_matter_acceptable": MeasurementUnits.UNITLESS,
        "ndf_percent_acceptable": MeasurementUnits.UNITLESS,
        "forage_ndf_percent_acceptable": MeasurementUnits.UNITLESS,
        "fat_percent_acceptable": MeasurementUnits.UNITLESS,
    }

    @property
    def _are_clamped_values_acceptable(self) -> bool:
        """Checks that values which must be in a certain range are in that range."""
        clamped_values = [self.metabolizable_protein, self.ndf_percent, self.fat_percent, self.dry_matter]
        return all([value == 0.0 for value in clamped_values])

    @property
    def is_valid_heifer_ration(self) -> bool:
        """True if evaluated supply meets requirements for heifers, else false."""
        non_negative_fields = {
            self.maintenance_energy,
            self.growth_energy,
            self.calcium,
            self.phosphorus,
            self.forage_ndf_percent,
        }
        valid_non_negative_fields = all([field >= 0.0 for field in non_negative_fields])

        return valid_non_negative_fields and self._are_clamped_values_acceptable

    @property
    def is_valid_cow_ration(self) -> bool:
        """True if evaluated supply meets requirements for cows, else false."""
        if self.total_energy is None or self.lactation_energy is None:
            return False

        valid_non_negative_fields = all([field >= 0.0 for field in {self.total_energy, self.lactation_energy}])

        return valid_non_negative_fields and self._are_clamped_values_acceptable and self.is_valid_heifer_ration

    @property
    def report(self) -> dict[str, bool | None]:
        """Returns a dictionary with the evaluation results."""
        return {
            "is_valid_heifer_ration": self.is_valid_heifer_ration,
            "is_valid_cow_ration": self.is_valid_cow_ration,
            "total_energy_acceptable": None if self.total_energy is None else self.total_energy >= 0.0,
            "maintenance_energy_acceptable": self.maintenance_energy >= 0.0,
            "lactation_energy_acceptable": None if self.total_energy is None else self.total_energy >= 0.0,
            "growth_energy_acceptable": self.growth_energy >= 0.0,
            "metabolizable_protein_acceptable": self.metabolizable_protein == 0.0,
            "calcium_acceptable": self.calcium >= 0.0,
            "phosphorus_acceptable": self.phosphorus >= 0.0,
            "dry_matter_acceptable": self.dry_matter == 0.0,
            "ndf_percent_acceptable": self.ndf_percent >= 0.0,
            "forage_ndf_percent_acceptable": self.forage_ndf_percent >= 0.0,
            "fat_percent_acceptable": self.fat_percent == 0.0,
        }

    def __add__(self, other: "NutritionEvaluationResults") -> "NutritionEvaluationResults":
        """Add two NutritionEvaluationResults objects together."""
        total_energy = self.total_energy if self.total_energy is not None else 0.0
        other_total_energy = other.total_energy if other.total_energy is not None else 0.0

        lactation = self.lactation_energy if self.lactation_energy is not None else 0.0
        other_lactation = other.lactation_energy if other.lactation_energy is not None else 0.0

        return NutritionEvaluationResults(
            total_energy=total_energy + other_total_energy,
            maintenance_energy=self.maintenance_energy + other.maintenance_energy,
            lactation_energy=lactation + other_lactation,
            growth_energy=self.growth_energy + other.growth_energy,
            metabolizable_protein=self.metabolizable_protein + other.metabolizable_protein,
            calcium=self.calcium + other.calcium,
            phosphorus=self.phosphorus + other.phosphorus,
            dry_matter=self.dry_matter + other.dry_matter,
            ndf_percent=self.ndf_percent + other.ndf_percent,
            forage_ndf_percent=self.forage_ndf_percent + other.forage_ndf_percent,
            fat_percent=self.fat_percent + other.fat_percent,
        )

    def __truediv__(self, divisor: float | int) -> "NutritionEvaluationResults":
        """Divide all NutritionEvaluationResults values by a scalar."""
        if divisor == 0.0:
            raise ZeroDivisionError("Cannot divide NutritionEvaluationResults by zero.")
        total_energy = self.total_energy if self.total_energy is not None else 0.0
        lactation = self.lactation_energy if self.lactation_energy is not None else 0.0

        return NutritionEvaluationResults(
            total_energy=total_energy / divisor,
            maintenance_energy=self.maintenance_energy / divisor,
            lactation_energy=lactation / divisor,
            growth_energy=self.growth_energy / divisor,
            metabolizable_protein=self.metabolizable_protein / divisor,
            calcium=self.calcium / divisor,
            phosphorus=self.phosphorus / divisor,
            dry_matter=self.dry_matter / divisor,
            ndf_percent=self.ndf_percent / divisor,
            forage_ndf_percent=self.forage_ndf_percent / divisor,
            fat_percent=self.fat_percent / divisor,
        )

    @classmethod
    def make_empty_evaluation_results(cls) -> "NutritionEvaluationResults":
        """Manufactures an empty NutritionEvaluationResults object."""
        return NutritionEvaluationResults(
            total_energy=0.0,
            maintenance_energy=0.0,
            lactation_energy=0.0,
            growth_energy=0.0,
            metabolizable_protein=0.0,
            calcium=0.0,
            phosphorus=0.0,
            dry_matter=0.0,
            ndf_percent=0.0,
            forage_ndf_percent=0.0,
            fat_percent=0.0,
        )
