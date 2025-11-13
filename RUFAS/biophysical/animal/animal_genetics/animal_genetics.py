import numpy as np

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
FAT_ACCURACY_BY_PARITY = {
    0: 0.75, 1: 0.80, 2: 0.85, 3: 0.90
}
PROTEIN_ACCURACY_BY_PARITY = {
    0: 0.75, 1: 0.80, 2: 0.85, 3: 0.90
}


class Genetics:
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
            assert (animal_type == AnimalType.CALF
                    and dam_tbv_fat is not None
                    and dam_tbv_protein is not None
                    and birth_month is not None)
            self.TBV_fat, self.TBV_protein = self._calculate_newborn_calf_tbv_values(
                dam_tbv_fat, dam_tbv_protein, f"{birth_year}-{birth_month:02d}")
        else:
            self.TBV_fat, self.TBV_protein = self._calculate_tbv_values()
        self.E_permanent_fat, self.E_permanent_protein = self._calculate_ep_values()
        self.E_temporary_fat, self.E_temporary_protein = self._calculate_et_values()
        self.phenotype_fat, self.phenotype_protein = self._calculate_phenotype_values(birth_year=birth_year)
        self.EBV_fat, self.EBV_protein = self._calculate_ebv_values(animal_type=animal_type, parity=parity)
        self.ranking_index = self._calculate_ranking_index()

    def recalculate_values_at_lactation_start(self, birth_year: int, animal_type: AnimalType, parity: int) -> None:
        """Recalculate genetic values at lactation start."""
        self.E_temporary_fat, self.E_temporary_protein = self._calculate_et_values()
        self.phenotype_fat, self.phenotype_protein = self._calculate_phenotype_values(birth_year=birth_year)
        if parity <= 3:
            self.EBV_fat, self.EBV_protein = self._calculate_ebv_values(animal_type=animal_type, parity=parity)
        self.ranking_index = self._calculate_ranking_index()

    def _calculate_tbv_values(self) -> tuple[float, float]:
        """Calculate TBV values for an animal entering the herd."""
        tbv_fat, tbv_protein = Utility.generate_bivariate_random_numbers(
            0.0, 0.0, TBV_FAT_STD, TBV_PROTEIN_STD, TBV_CORRELATION
        )
        return tbv_fat, tbv_protein

    def _calculate_newborn_calf_tbv_values(
            self,
            dam_tbv_fat: float,
            dam_tbv_protein: float,
            birth_year_month: str
    ) -> tuple[float, float]:
        """Calculate TBV values for a newborn calf."""
        tbv_fat_top_semen = AnimalConfig.top_listing_semen["estimated_fat"][birth_year_month]
        tbv_protein_top_semen = AnimalConfig.top_listing_semen["estimated_protein"][birth_year_month]
        std_tbv_fat_national_average, std_tbv_protein_national_average = TBV_FAT_STD, TBV_PROTEIN_STD

        mean_tbv_fat = (tbv_fat_top_semen + dam_tbv_fat) / 2
        mean_tbv_protein = (tbv_protein_top_semen + dam_tbv_protein) / 2

        std_tbv_fat = np.sqrt(std_tbv_fat_national_average ** 2 / 2)
        std_tbv_protein = np.sqrt(std_tbv_protein_national_average ** 2 / 2)

        tbv_fat, tbv_protein = Utility.generate_bivariate_random_numbers(
            mean_tbv_fat, mean_tbv_protein, std_tbv_fat, std_tbv_protein, TBV_CORRELATION
        )

        return tbv_fat, tbv_protein

    def _calculate_ep_values(self) -> tuple[float, float]:
        """Calculate E_permanent values."""
        ep_fat, ep_protein = Utility.generate_bivariate_random_numbers(
            0.0, 0.0, E_PERMANENT_FAT_STD, E_PERMANENT_PROTEIN_STD, E_PERMANENT_CORRELATION
        )
        return ep_fat, ep_protein

    def _calculate_et_values(self) -> tuple[float, float]:
        """Calculate E_temporary values."""
        et_fat, et_protein = Utility.generate_bivariate_random_numbers(
            0.0, 0.0, E_TEMPORARY_FAT_STD, E_TEMPORARY_PROTEIN_STD, E_TEMPORARY_CORRELATION
        )
        return et_fat, et_protein

    def _calculate_phenotype_values(self, birth_year: int) -> tuple[float, float]:
        """Calculate phenotype values."""
        mean_fat = AnimalConfig.average_phenotype["fat_kg"][birth_year]
        mean_protein = AnimalConfig.average_phenotype["protein_kg"][birth_year]
        phenotype_fat = mean_fat + self.TBV_fat + self.E_permanent_fat + self.E_temporary_fat
        phenotype_protein = mean_protein + self.TBV_protein + self.E_permanent_protein + self.E_temporary_protein
        return phenotype_fat, phenotype_protein

    def _calculate_ebv_values(self, animal_type: AnimalType, parity: int | None) -> tuple[float, float]:
        """Calculate EBV values."""
        parity_index = min(parity, 3) if animal_type.is_cow else 0
        fat_accuracy, protein_accuracy = FAT_ACCURACY_BY_PARITY[parity_index], PROTEIN_ACCURACY_BY_PARITY[parity_index]

        mean_ebv_fat = self.TBV_fat * (fat_accuracy ** 2)
        mean_ebv_protein = self.TBV_protein * (protein_accuracy ** 2)

        std_ebv_fat = np.sqrt((1 - fat_accuracy ** 2) * (fat_accuracy ** 2) * TBV_FAT_STD)
        std_ebv_protein = np.sqrt((1 - protein_accuracy ** 2) * (protein_accuracy ** 2) * TBV_PROTEIN_STD)

        noise_ebv_fat = np.random.normal(0.0, std_ebv_fat)
        noise_ebv_protein = np.random.normal(0.0, std_ebv_protein)

        ebv_fat = mean_ebv_fat + noise_ebv_fat
        ebv_protein = mean_ebv_protein + noise_ebv_protein
        return ebv_fat, ebv_protein

    def _calculate_ranking_index(self) -> float:
        """Calculate ranking index."""
        return 0.318 * self.EBV_fat + 0.13 * self.EBV_protein
