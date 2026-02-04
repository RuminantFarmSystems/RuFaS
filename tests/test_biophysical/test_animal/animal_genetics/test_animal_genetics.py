from unittest.mock import call

import numpy
import pytest
from RUFAS.util import Utility
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import (
    Genetics,
    TBV_CORRELATION,
    TBV_FAT_STD,
    TBV_PROTEIN_STD,
    E_PERMANENT_FAT_STD,
    E_PERMANENT_PROTEIN_STD,
    E_PERMANENT_CORRELATION,
    E_TEMPORARY_FAT_STD,
    E_TEMPORARY_PROTEIN_STD,
    E_TEMPORARY_CORRELATION,
)
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@pytest.fixture
def genetics() -> Genetics:
    AnimalConfig.average_phenotype["fat_kg"] = {2020: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2020: 20.0}
    genetics = Genetics(animal_type=AnimalType.LAC_COW, birth_year=2020, parity=3)
    return genetics


@pytest.mark.parametrize(
    "animal_type, birth_year, birth_month, parity, initialize_new_born_calf, dam_tbv_fat, dam_tbv_protein",
    [
        (AnimalType.CALF, 2020, None, False, None, None, None),
        (AnimalType.HEIFER_I, 2020, None, None, None, None, None),
        (AnimalType.HEIFER_II, 2020, None, None, None, None, None),
        (AnimalType.HEIFER_III, 2020, None, 0, None, None, None),
        (AnimalType.LAC_COW, 2020, None, 1, None, None, None),
        (AnimalType.DRY_COW, 2020, None, 5, None, None, None),
        (AnimalType.CALF, 2020, 1, 1, True, 10.0, 20.0),
    ],
)
def test_animal_genetics_init(
    animal_type: AnimalType,
    birth_year: int,
    birth_month: int | None,
    parity: int | None,
    initialize_new_born_calf: bool | None,
    dam_tbv_fat: float | None,
    dam_tbv_protein: float | None,
    mocker: MockerFixture,
) -> None:
    """Unit test for __init__()"""
    mock_calculate_newborn_calf_tbv_values = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_newborn_calf_tbv_values",
        return_value=(10.0, 20.0),
    )
    mock_calculate_tbv_values = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_tbv_values",
        return_value=(10.0, 20.0),
    )
    mock_calculate_ep_values = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_ep_values",
        return_value=(10.0, 20.0),
    )
    mock_calculate_et_values = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_et_values",
        return_value=(10.0, 20.0),
    )
    mock_calculate_phenotype_values = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_phenotype_values",
        return_value=(10.0, 20.0),
    )
    mock_calculate_ebv_values = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_ebv_values",
        return_value=(10.0, 20.0),
    )
    mock_calculate_ranking_index = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.Genetics._calculate_ranking_index",
        return_value=10.0,
    )

    Genetics(
        animal_type=animal_type,
        birth_year=birth_year,
        birth_month=birth_month,
        parity=parity,
        initialize_new_born_calf=initialize_new_born_calf,
        dam_tbv_fat=dam_tbv_fat,
        dam_tbv_protein=dam_tbv_protein,
    )

    if initialize_new_born_calf:
        mock_calculate_newborn_calf_tbv_values.assert_called_once_with(
            dam_tbv_fat, dam_tbv_protein, f"{birth_year}-{birth_month:02d}"
        )
        mock_calculate_tbv_values.assert_not_called()
    else:
        mock_calculate_newborn_calf_tbv_values.assert_not_called()
        mock_calculate_tbv_values.assert_called_once_with()
    mock_calculate_ep_values.assert_called_once_with()
    mock_calculate_et_values.assert_called_once_with()
    mock_calculate_phenotype_values.assert_called_once_with(birth_year=birth_year)
    mock_calculate_ebv_values.assert_not_called()
    mock_calculate_ranking_index.assert_not_called()


@pytest.mark.parametrize(
    "birth_year, animal_type, parity, ebv_recalculate",
    [
        (2020, AnimalType.LAC_COW, 0, True),
        (2020, AnimalType.LAC_COW, 1, True),
        (2020, AnimalType.LAC_COW, 2, True),
        (2020, AnimalType.LAC_COW, 3, True),
        (2020, AnimalType.LAC_COW, 4, False),
        (2020, AnimalType.LAC_COW, 5, False),
    ],
)
def test_recalculate_values_at_lactation_start(
    birth_year: int,
    animal_type: AnimalType,
    parity: int,
    ebv_recalculate: bool,
    genetics: Genetics,
    mocker: MockerFixture,
) -> None:
    """Unit test for recalculate_values_at_lactation_start()"""
    mock_calculate_et_values = mocker.patch.object(genetics, "_calculate_et_values", return_value=(10.0, 20.0))
    mock_calculate_phenotype_values = mocker.patch.object(
        genetics, "_calculate_phenotype_values", return_value=(10.0, 20.0)
    )
    mock_calculate_ebv_values = mocker.patch.object(genetics, "_calculate_ebv_values", return_value=(10.0, 20.0))
    mock_calculate_ranking_index = mocker.patch.object(genetics, "_calculate_ranking_index", return_value=10.0)

    genetics.recalculate_values_at_lactation_start(
        birth_year=birth_year,
        animal_type=animal_type,
        parity=parity,
        group_specific_TBV_fat_mean=1.1,
        group_specific_TBV_protein_mean=2.2,
    )

    mock_calculate_et_values.assert_called_once_with()
    mock_calculate_phenotype_values.assert_called_once_with(birth_year=birth_year)
    if ebv_recalculate:
        mock_calculate_ebv_values.assert_called_once_with(
            animal_type=animal_type, parity=parity, group_specific_TBV_fat_mean=1.1, group_specific_TBV_protein_mean=2.2
        )
    else:
        mock_calculate_ebv_values.assert_not_called()
    mock_calculate_ranking_index.assert_called_once_with()


def test_calculate_tbv_values(genetics: Genetics, mocker: MockerFixture) -> None:
    """Unit test for _calculate_tbv_values()"""
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )
    genetics._calculate_tbv_values()
    mock_generate_bivariate_random_numbers.assert_called_once_with(
        0.0, 0.0, TBV_FAT_STD, TBV_PROTEIN_STD, TBV_CORRELATION
    )


@pytest.mark.parametrize(
    "dam_tbv_fat, dam_tbv_protein, birth_year_month, top_listing_semen_fat, top_listing_semen_protein,"
    "expected_mean_tbv_fat, expected_mean_tbv_protein, expected_std_tbv_fat, expected_std_tbv_protein",
    [
        (10.0, 20.0, "2020-01", 13.0, 18.0, 11.5, 19.0, 18.243354954612926, 9.475230867899738),
        (15.0, 25.0, "2021-01", 15.0, 25.0, 15.0, 25.0, 18.243354954612926, 9.475230867899738),
        (20.0, 30.0, "2022-01", 128.0, 64.0, 74.0, 47.0, 18.243354954612926, 9.475230867899738),
    ],
)
def test_calculate_newborn_calf_tbv_values(
    dam_tbv_fat: float,
    dam_tbv_protein: float,
    birth_year_month: str,
    top_listing_semen_fat: float,
    top_listing_semen_protein: float,
    expected_mean_tbv_fat: float,
    expected_mean_tbv_protein: float,
    expected_std_tbv_fat: float,
    expected_std_tbv_protein: float,
    genetics: Genetics,
    mocker: MockerFixture,
) -> None:
    """Unit test for _calculate_newborn_calf_tbv_values()"""
    AnimalConfig.top_listing_semen["estimated_fat"] = {birth_year_month: top_listing_semen_fat}
    AnimalConfig.top_listing_semen["estimated_protein"] = {birth_year_month: top_listing_semen_protein}
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )

    genetics._calculate_newborn_calf_tbv_values(dam_tbv_fat, dam_tbv_protein, birth_year_month)

    mock_generate_bivariate_random_numbers.assert_called_once_with(
        expected_mean_tbv_fat,
        expected_mean_tbv_protein,
        expected_std_tbv_fat,
        expected_std_tbv_protein,
        TBV_CORRELATION,
    )


def test_calculate_ep_values(genetics: Genetics, mocker: MockerFixture) -> None:
    """Unit test for _calculate_ep_values()"""
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )
    genetics._calculate_ep_values()
    mock_generate_bivariate_random_numbers.assert_called_once_with(
        0.0, 0.0, E_PERMANENT_FAT_STD, E_PERMANENT_PROTEIN_STD, E_PERMANENT_CORRELATION
    )


def test_calculate_et_values(genetics: Genetics, mocker: MockerFixture) -> None:
    """Unit test for _calculate_et_values()"""
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )
    genetics._calculate_et_values()
    mock_generate_bivariate_random_numbers.assert_called_once_with(
        0.0, 0.0, E_TEMPORARY_FAT_STD, E_TEMPORARY_PROTEIN_STD, E_TEMPORARY_CORRELATION
    )


@pytest.mark.parametrize(
    "mean_phenotype_fat, mean_phenotype_protein, birth_year,"
    "tbv_fat, tbv_protein, e_p_fat, e_p_protein, e_t_fat, e_t_protein,"
    "expected_phenotype_fat, expected_phenotype_protein",
    [
        (10.0, 20.0, 2023, 100.0, 200.0, 5.0, 10.0, 3.0, 6.0, 118.0, 236.0),
        (15.0, 25.0, 2022, 120.0, 240.0, 7.0, 14.0, 4.0, 8.0, 146.0, 287.0),
    ],
)
def test_calculate_phenotype_values(
    mean_phenotype_fat: float,
    mean_phenotype_protein: float,
    birth_year: int,
    tbv_fat: float,
    tbv_protein: float,
    e_p_fat: float,
    e_p_protein: float,
    e_t_fat: float,
    e_t_protein: float,
    expected_phenotype_fat: float,
    expected_phenotype_protein: float,
    genetics: Genetics,
) -> None:
    """Unit test for _calculate_phenotype_values()"""
    genetics.TBV_fat = tbv_fat
    genetics.TBV_protein = tbv_protein
    genetics.E_permanent_fat = e_p_fat
    genetics.E_permanent_protein = e_p_protein
    genetics.E_temporary_fat = e_t_fat
    genetics.E_temporary_protein = e_t_protein

    AnimalConfig.average_phenotype["fat_kg"] = {birth_year: mean_phenotype_fat}
    AnimalConfig.average_phenotype["protein_kg"] = {birth_year: mean_phenotype_protein}

    phenotype_fat, phenotype_protein = genetics._calculate_phenotype_values(birth_year=birth_year)

    assert phenotype_fat == pytest.approx(expected_phenotype_fat)
    assert phenotype_protein == pytest.approx(expected_phenotype_protein)


@pytest.mark.parametrize(
    "animal_type, parity, tbv_fat, tbv_protein,"
    "expected_std_ebv_fat, expected_std_ebv_protein, expected_ebv_fat, expected_ebv_protein",
    [
        (AnimalType.CALF, None, 10.0, 20.0, 2.519765614099851, 1.8159450019204877, 6.20625, 12.3125),
        (AnimalType.HEIFER_I, None, 10.0, 20.0, 2.519765614099851, 1.8159450019204877, 6.20625, 12.3125),
        (AnimalType.HEIFER_II, None, 10.0, 20.0, 2.519765614099851, 1.8159450019204877, 6.20625, 12.3125),
        (AnimalType.HEIFER_III, None, 10.0, 20.0, 2.519765614099851, 1.8159450019204877, 6.20625, 12.3125),
        (AnimalType.LAC_COW, 1, 15.0, 25.0, 2.4380976190464563, 1.75708850090142, 10.096, 16.892),
        (
            AnimalType.DRY_COW,
            2,
            15.0,
            25.0,
            2.274365570879053,
            1.6390900676899975,
            11.24275,
            18.773,
        ),
        (AnimalType.LAC_COW, 3, 15.0, 25.0, 1.992641462983243, 1.4360571019287496, 12.459, 20.768),
        (AnimalType.DRY_COW, 4, 15.0, 25.0, 1.992641462983243, 1.4360571019287496, 12.459, 20.768),
    ],
)
def test_calculate_ebv_values(
    animal_type: AnimalType,
    parity: int,
    tbv_fat: float,
    tbv_protein: float,
    expected_std_ebv_fat: float,
    expected_std_ebv_protein: float,
    expected_ebv_fat: float,
    expected_ebv_protein: float,
    genetics: Genetics,
    mocker: MockerFixture,
) -> None:
    """Unit test for _calculate_ebv_values()"""
    genetics.TBV_fat = tbv_fat
    genetics.TBV_protein = tbv_protein
    mock_np_random_normal = mocker.patch.object(numpy.random, "normal", side_effect=[0.1, 0.1])
    ebv_fat, ebv_protein = genetics._calculate_ebv_values(
        animal_type=animal_type, parity=parity, group_specific_TBV_fat_mean=1.1, group_specific_TBV_protein_mean=2.2
    )

    assert mock_np_random_normal.call_args_list == [
        call(0.0, pytest.approx(expected_std_ebv_fat)),
        call(0.0, pytest.approx(expected_std_ebv_protein)),
    ]
    assert ebv_fat == pytest.approx(expected_ebv_fat)
    assert ebv_protein == pytest.approx(expected_ebv_protein)


@pytest.mark.parametrize(
    "ebv_fat, ebv_protein, expected_ranking_index",
    [
        (5.725, 11.35, 3.29605),
        (1.234, 5.678, 1.130552),
    ],
)
def test_calculate_ranking_index(
    ebv_fat: float, ebv_protein: float, expected_ranking_index: float, genetics: Genetics
) -> None:
    """Unit test for _calculate_ranking_index()"""
    genetics.EBV_fat = ebv_fat
    genetics.EBV_protein = ebv_protein
    ranking_index = genetics._calculate_ranking_index()
    assert ranking_index == pytest.approx(expected_ranking_index)
