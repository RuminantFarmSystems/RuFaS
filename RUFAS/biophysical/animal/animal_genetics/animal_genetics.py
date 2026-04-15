import numpy as np

from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.util import Utility

TBV_FAT_STD = 25.8
TBV_PROTEIN_STD = 13.4
TBV_CORRELATION = 0.59
E_PERMANENT_FAT_STD = 38.8
E_PERMANENT_PROTEIN_STD = 20.1
E_PERMANENT_CORRELATION = 0.95
E_TEMPORARY_FAT_STD = 38.8
E_TEMPORARY_PROTEIN_STD = 20.1
E_TEMPORARY_CORRELATION = 0.95
FAT_ACCURACY_BY_PARITY = {0: 0.75, 1: 0.80, 2: 0.85, 3: 0.90}
PROTEIN_ACCURACY_BY_PARITY = {0: 0.75, 1: 0.80, 2: 0.85, 3: 0.90}

UNITS = {
    "TBV_fat": MeasurementUnits.KILOGRAMS,
    "TBV_protein": MeasurementUnits.KILOGRAMS,
    "E_permanent_fat": MeasurementUnits.KILOGRAMS,
    "E_permanent_protein": MeasurementUnits.KILOGRAMS,
    "E_temporary_fat": MeasurementUnits.KILOGRAMS,
    "E_temporary_protein": MeasurementUnits.KILOGRAMS,
    "phenotype_fat": MeasurementUnits.KILOGRAMS,
    "phenotype_protein": MeasurementUnits.KILOGRAMS,
    "EBV_fat": MeasurementUnits.KILOGRAMS,
    "EBV_protein": MeasurementUnits.KILOGRAMS,
    "ranking_index": MeasurementUnits.UNITLESS,
}


class Genetics:
    """
    Genetic attributes of an animal.

    Attributes
    ----------
    TBV_fat : float
        True Breeding Value for fat, (kg).
    TBV_protein : float
        True Breeding Value for protein, (kg).
    E_permanent_fat : float
        Permanent Environment Effect for fat, (kg).
    E_permanent_protein : float
        Permanent Environment Effect for protein, (kg).
    E_temporary_fat : float
        Temporary Environment Effect for fat, (kg).
    E_temporary_protein : float
        Temporary Environment Effect for protein, (kg).
    phenotype_fat : float
        Phenotype for fat, (kg).
    phenotype_protein : float
        Phenotype for protein, (kg).
    EBV_fat : float
        Estimated Breeding Value for fat, (kg).
    EBV_protein : float
        Estimated Breeding Value for protein, (kg).
    ranking_index : float
        Ranking index for animal performance.
    """

    TBV_fat: float
    TBV_protein: float
    E_permanent_fat: float
    E_permanent_protein: float

    E_temporary_fat: float
    E_temporary_protein: float
    phenotype_fat: float
    phenotype_protein: float
    EBV_fat: float
    EBV_protein: float
    ranking_index: float

    top_semen_too_early_warning: bool = False
    top_semen_too_recent_warning: bool = False
    phenotype_too_early_warning: bool = False
    phenotype_too_recent_warning: bool = False

    def __init__(
        self,
        birth_year: int,
        animal_type: AnimalType,
        *,
        parity: int | None = None,
        initialize_new_born_calf: bool = False,
        dam_tbv_fat: float | None = None,
        dam_tbv_protein: float | None = None,
        birth_month: int | None = None,
    ) -> None:
        """Initialize genetic attributes."""
        if initialize_new_born_calf:
            assert (
                animal_type == AnimalType.CALF
                and dam_tbv_fat is not None
                and dam_tbv_protein is not None
                and birth_month is not None
            )
            self.TBV_fat, self.TBV_protein = self._calculate_newborn_calf_tbv_values(
                dam_tbv_fat, dam_tbv_protein, f"{birth_year}-{birth_month:02d}"
            )
        else:
            self.TBV_fat, self.TBV_protein = self._calculate_tbv_values()
        self.E_permanent_fat, self.E_permanent_protein = self._calculate_ep_values()
        self.E_temporary_fat, self.E_temporary_protein = self._calculate_et_values()
        self.phenotype_fat, self.phenotype_protein = self._calculate_phenotype_values(birth_year=birth_year)
        self.EBV_fat, self.EBV_protein = 0.0, 0.0
        self.ranking_index = 0.0

    def calculate_ebv_and_ranking_index(
        self,
        animal_type: AnimalType,
        group_specific_TBV_fat_mean: float,
        group_specific_TBV_protein_mean: float,
        parity: int | None,
    ) -> None:
        """Calculate EBV and ranking index values."""
        self.EBV_fat, self.EBV_protein = self._calculate_ebv_values(
            animal_type=animal_type,
            group_specific_TBV_fat_mean=group_specific_TBV_fat_mean,
            group_specific_TBV_protein_mean=group_specific_TBV_protein_mean,
            parity=parity,
        )
        self.ranking_index = self._calculate_ranking_index()

    def recalculate_values_at_lactation_start(
        self,
        birth_year: int,
        animal_type: AnimalType,
        parity: int,
        group_specific_TBV_fat_mean: float,
        group_specific_TBV_protein_mean: float,
    ) -> None:
        """Recalculate genetic values at lactation start."""
        self.E_temporary_fat, self.E_temporary_protein = self._calculate_et_values()
        self.phenotype_fat, self.phenotype_protein = self._calculate_phenotype_values(birth_year=birth_year)
        if parity <= 3:
            self.EBV_fat, self.EBV_protein = self._calculate_ebv_values(
                animal_type=animal_type,
                parity=parity,
                group_specific_TBV_fat_mean=group_specific_TBV_fat_mean,
                group_specific_TBV_protein_mean=group_specific_TBV_protein_mean,
            )
        self.ranking_index = self._calculate_ranking_index()

    def _calculate_tbv_values(self) -> tuple[float, float]:
        """Calculate TBV values for an animal entering the herd."""
        tbv_fat, tbv_protein = Utility.generate_bivariate_random_numbers(
            0.0, 0.0, TBV_FAT_STD, TBV_PROTEIN_STD, TBV_CORRELATION
        )
        return tbv_fat, tbv_protein

    def _calculate_newborn_calf_tbv_values(
        self, dam_tbv_fat: float, dam_tbv_protein: float, birth_year_month: str
    ) -> tuple[float, float]:
        """Calculate TBV values for a newborn calf."""
        try:
            tbv_fat_top_semen = AnimalConfig.top_listing_semen["estimated_fat"][birth_year_month]
            tbv_protein_top_semen = AnimalConfig.top_listing_semen["estimated_protein"][birth_year_month]
        except KeyError as key_error:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._calculate_newborn_calf_tbv_values.__name__,
            }
            earliest_top_semen_date = min(AnimalConfig.top_listing_semen["estimated_fat"])
            latest_top_semen_date = max(AnimalConfig.top_listing_semen["estimated_fat"])
            if birth_year_month < earliest_top_semen_date:
                tbv_fat_top_semen = AnimalConfig.top_listing_semen["estimated_fat"][earliest_top_semen_date]
                tbv_protein_top_semen = AnimalConfig.top_listing_semen["estimated_protein"][earliest_top_semen_date]
                if not Genetics.top_semen_too_early_warning:
                    om = OutputManager()
                    om.add_warning(
                        "Animal born before the earliest available Top Listing Semen data",
                        f"All animals born before {earliest_top_semen_date} will have use values "
                        f"{tbv_fat_top_semen=} and {tbv_protein_top_semen=} "
                        f"from the earliest available date of {earliest_top_semen_date}.",
                        info_map,
                    )
                    Genetics.set_top_semen_too_early_warning_raised(True)
            elif birth_year_month > latest_top_semen_date:
                tbv_fat_top_semen = AnimalConfig.top_listing_semen["estimated_fat"][latest_top_semen_date]
                tbv_protein_top_semen = AnimalConfig.top_listing_semen["estimated_protein"][latest_top_semen_date]
                if not Genetics.top_semen_too_recent_warning:
                    om = OutputManager()
                    om.add_warning(
                        "Animal born after the latest available Top Listing Semen data",
                        f"All animals born after {latest_top_semen_date} will have use values "
                        f"{tbv_fat_top_semen=} and {tbv_protein_top_semen=} "
                        f"from the earliest available date of {earliest_top_semen_date}.",
                        info_map,
                    )
                    Genetics.set_birthdate_too_recent_warning_raised(True)

            else:
                raise key_error
        std_tbv_fat_national_average, std_tbv_protein_national_average = TBV_FAT_STD, TBV_PROTEIN_STD

        mean_tbv_fat = (tbv_fat_top_semen + dam_tbv_fat) / 2
        mean_tbv_protein = (tbv_protein_top_semen + dam_tbv_protein) / 2

        std_tbv_fat = np.sqrt(std_tbv_fat_national_average**2 / 2)
        std_tbv_protein = np.sqrt(std_tbv_protein_national_average**2 / 2)

        tbv_fat, tbv_protein = Utility.generate_bivariate_random_numbers(
            mean_tbv_fat, mean_tbv_protein, std_tbv_fat, std_tbv_protein, TBV_CORRELATION
        )

        return tbv_fat, tbv_protein

    def _calculate_ep_values(self) -> tuple[float, float]:
        """Calculate Permanent Environment Effect (E_permanent) values."""
        ep_fat, ep_protein = Utility.generate_bivariate_random_numbers(
            0.0, 0.0, E_PERMANENT_FAT_STD, E_PERMANENT_PROTEIN_STD, E_PERMANENT_CORRELATION
        )
        return ep_fat, ep_protein

    def _calculate_et_values(self) -> tuple[float, float]:
        """Calculate Temporary Environment Effect (E_temporary) values."""
        et_fat, et_protein = Utility.generate_bivariate_random_numbers(
            0.0, 0.0, E_TEMPORARY_FAT_STD, E_TEMPORARY_PROTEIN_STD, E_TEMPORARY_CORRELATION
        )
        return et_fat, et_protein

    def _calculate_phenotype_values(self, birth_year: int) -> tuple[float, float]:
        """Calculate phenotype values."""
        try:
            mean_fat = AnimalConfig.average_phenotype["fat_kg"][birth_year]
            mean_protein = AnimalConfig.average_phenotype["protein_kg"][birth_year]
        except KeyError as key_error:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._calculate_newborn_calf_tbv_values.__name__,
            }
            earliest_phenotype_date = min(AnimalConfig.average_phenotype["fat_kg"])
            latest_phenotype_date = max(AnimalConfig.average_phenotype["fat_kg"])
            if birth_year < earliest_phenotype_date:
                mean_fat = AnimalConfig.average_phenotype["fat_kg"][earliest_phenotype_date]
                mean_protein = AnimalConfig.average_phenotype["protein_kg"][earliest_phenotype_date]
                if not Genetics.phenotype_too_early_warning:
                    om = OutputManager()
                    om.add_warning(
                        "Animal born before the earliest available Average Phenotype data",
                        f"All animals born before {earliest_phenotype_date} will have use values {mean_fat=} and "
                        f"{mean_protein=} from the earliest available year of {earliest_phenotype_date}.",
                        info_map,
                    )
                    Genetics.set_phenotype_too_early_warning_raised(True)
            elif birth_year > latest_phenotype_date:
                mean_fat = AnimalConfig.average_phenotype["fat_kg"][latest_phenotype_date]
                mean_protein = AnimalConfig.average_phenotype["protein_kg"][latest_phenotype_date]
                if not Genetics.phenotype_too_recent_warning:
                    om = OutputManager()
                    om.add_warning(
                        "Animal born after the latest available Average Phenotype data",
                        f"All animals born after {latest_phenotype_date} will have use values "
                        f"{mean_fat=} and {mean_protein=} "
                        f"from the earliest available date of {latest_phenotype_date}.",
                        info_map,
                    )
                    Genetics.set_phenotype_too_recent_warning_raised(True)

            else:
                raise key_error
        phenotype_fat = mean_fat + self.TBV_fat + self.E_permanent_fat + self.E_temporary_fat
        phenotype_protein = mean_protein + self.TBV_protein + self.E_permanent_protein + self.E_temporary_protein
        return phenotype_fat, phenotype_protein

    def _calculate_ebv_values(
        self,
        animal_type: AnimalType,
        group_specific_TBV_fat_mean: float,
        group_specific_TBV_protein_mean: float,
        parity: int | None,
    ) -> tuple[float, float]:
        """Calculate EBV values."""
        parity_index = min(parity, 3) if animal_type.is_cow and parity is not None else 0
        fat_accuracy, protein_accuracy = FAT_ACCURACY_BY_PARITY[parity_index], PROTEIN_ACCURACY_BY_PARITY[parity_index]

        mean_ebv_fat = group_specific_TBV_fat_mean + (self.TBV_fat - group_specific_TBV_fat_mean) * (fat_accuracy**2)
        mean_ebv_protein = group_specific_TBV_protein_mean + (self.TBV_protein - group_specific_TBV_protein_mean) * (
            protein_accuracy**2
        )

        std_ebv_fat = np.sqrt((1 - fat_accuracy**2) * (fat_accuracy**2) * TBV_FAT_STD)
        std_ebv_protein = np.sqrt((1 - protein_accuracy**2) * (protein_accuracy**2) * TBV_PROTEIN_STD)

        noise_ebv_fat = np.random.normal(0.0, std_ebv_fat)
        noise_ebv_protein = np.random.normal(0.0, std_ebv_protein)

        ebv_fat = mean_ebv_fat + noise_ebv_fat
        ebv_protein = mean_ebv_protein + noise_ebv_protein
        return ebv_fat, ebv_protein

    def _calculate_ranking_index(self) -> float:
        """Calculate ranking index."""
        return 0.318 * self.EBV_fat + 0.13 * self.EBV_protein

    @staticmethod
    def calculate_average_genetic_values(list_of_genetics: list["Genetics"]) -> dict[str, float | None]:
        """Calculate average genetic values for a list of genetics."""
        if (num_animal := len(list_of_genetics)) <= 0:
            return {
                "TBV_fat": None,
                "TBV_protein": None,
                "E_permanent_fat": None,
                "E_permanent_protein": None,
                "E_temporary_fat": None,
                "E_temporary_protein": None,
                "phenotype_fat": None,
                "phenotype_protein": None,
                "EBV_fat": None,
                "EBV_protein": None,
                "ranking_index": None,
            }
        else:
            return {
                "TBV_fat": sum([genetic.TBV_fat for genetic in list_of_genetics]) / num_animal,
                "TBV_protein": sum([genetic.TBV_protein for genetic in list_of_genetics]) / num_animal,
                "E_permanent_fat": sum([genetic.E_permanent_fat for genetic in list_of_genetics]) / num_animal,
                "E_permanent_protein": sum([genetic.E_permanent_protein for genetic in list_of_genetics]) / num_animal,
                "E_temporary_fat": sum([genetic.E_temporary_fat for genetic in list_of_genetics]) / num_animal,
                "E_temporary_protein": sum([genetic.E_temporary_protein for genetic in list_of_genetics]) / num_animal,
                "phenotype_fat": sum([genetic.phenotype_fat for genetic in list_of_genetics]) / num_animal,
                "phenotype_protein": sum([genetic.phenotype_protein for genetic in list_of_genetics]) / num_animal,
                "EBV_fat": sum([genetic.EBV_fat for genetic in list_of_genetics]) / num_animal,
                "EBV_protein": sum([genetic.EBV_protein for genetic in list_of_genetics]) / num_animal,
                "ranking_index": sum([genetic.ranking_index for genetic in list_of_genetics]) / num_animal,
            }

    @staticmethod
    def calculate_average_tbv(list_of_genetics: list["Genetics"]) -> tuple[float, float]:
        """Calculate average TBV values for a specific group of animals."""
        num_animals = len(list_of_genetics)
        return (
            sum([genetic.TBV_fat for genetic in list_of_genetics]) / num_animals if num_animals > 0 else 0.0,
            sum([genetic.TBV_protein for genetic in list_of_genetics]) / num_animals if num_animals > 0 else 0.0,
        )

    def to_dict(self) -> dict[str, float]:
        """Return dictionary representation of the genetics properties of the animal."""
        return {
            "TBV_fat": self.TBV_fat,
            "TBV_protein": self.TBV_protein,
            "E_permanent_fat": self.E_permanent_fat,
            "E_permanent_protein": self.E_permanent_protein,
            "E_temporary_fat": self.E_temporary_fat,
            "E_temporary_protein": self.E_temporary_protein,
            "phenotype_fat": self.phenotype_fat,
            "phenotype_protein": self.phenotype_protein,
            "EBV_fat": self.EBV_fat,
            "EBV_protein": self.EBV_protein,
            "ranking_index": self.ranking_index,
        }

    @classmethod
    def set_top_semen_too_early_warning_raised(cls, birthdate_too_early_warning_raised: bool) -> None:
        """
        Sets the flag indicating whether a warning has been raised for animals born before
        the earliest available top semen listing data.

        Parameters
        ----------
        birthdate_too_early_warning_raised : bool
            True if the birthdate too early warning for top semen has been raised, False otherwise.
        """
        cls.top_semen_too_early_warning = birthdate_too_early_warning_raised

    @classmethod
    def set_birthdate_too_recent_warning_raised(cls, birthdate_too_recent_warning_raised: bool) -> None:
        """
        Sets the flag indicating whether a warning has been raised for animals born after
        the latest available top semen listing data.

        Parameters
        ----------
        birthdate_too_recent_warning_raised : bool
            True if the birthdate too recent warning for top semen has been raised, False otherwise.
        """
        cls.top_semen_too_recent_warning = birthdate_too_recent_warning_raised

    @classmethod
    def set_phenotype_too_early_warning_raised(cls, birthdate_too_early_warning_raised: bool) -> None:
        """
        Sets the flag indicating whether a warning has been raised for animals born before
        the earliest available average phenotype data.

        Parameters
        ----------
        birthdate_too_early_warning_raised : bool
            True if the birthdate too early warning for phenotype has been raised, False otherwise.
        """
        cls.phenotype_too_early_warning = birthdate_too_early_warning_raised

    @classmethod
    def set_phenotype_too_recent_warning_raised(cls, birthdate_too_recent_warning_raised: bool) -> None:
        """
        Sets the flag indicating whether a warning has been raised for animals born after
        the latest available average phenotype data.

        Parameters
        ----------
        birthdate_too_recent_warning_raised : bool
            True if the birthdate too recent warning for phenotype has been raised, False otherwise.
        """
        cls.phenotype_too_recent_warning = birthdate_too_recent_warning_raised
