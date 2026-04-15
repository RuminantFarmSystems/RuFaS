from unittest.mock import call, MagicMock

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
from RUFAS.output_manager import OutputManager


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


def test_calculate_ebv_and_ranking_index(genetics: Genetics, mocker: MockerFixture) -> None:
    """Unit test for calculate_ebv_and_ranking_index()"""
    mock_calculate_ebv_values = mocker.patch.object(genetics, "_calculate_ebv_values", return_value=(5.0, 10.0))
    mock_calculate_ranking_index = mocker.patch.object(genetics, "_calculate_ranking_index", return_value=2.89)

    genetics.calculate_ebv_and_ranking_index(
        animal_type=AnimalType.LAC_COW,
        group_specific_TBV_fat_mean=1.0,
        group_specific_TBV_protein_mean=2.0,
        parity=2,
    )

    mock_calculate_ebv_values.assert_called_once_with(
        animal_type=AnimalType.LAC_COW,
        group_specific_TBV_fat_mean=1.0,
        group_specific_TBV_protein_mean=2.0,
        parity=2,
    )
    mock_calculate_ranking_index.assert_called_once_with()
    assert genetics.EBV_fat == 5.0
    assert genetics.EBV_protein == 10.0
    assert genetics.ranking_index == 2.89


def test_to_dict(genetics: Genetics) -> None:
    """Unit test for to_dict()"""
    genetics.TBV_fat = 1.1
    genetics.TBV_protein = 2.2
    genetics.E_permanent_fat = 3.3
    genetics.E_permanent_protein = 4.4
    genetics.E_temporary_fat = 5.5
    genetics.E_temporary_protein = 6.6
    genetics.phenotype_fat = 7.7
    genetics.phenotype_protein = 8.8
    genetics.EBV_fat = 9.9
    genetics.EBV_protein = 10.0
    genetics.ranking_index = 11.11

    result = genetics.to_dict()

    assert result == {
        "TBV_fat": 1.1,
        "TBV_protein": 2.2,
        "E_permanent_fat": 3.3,
        "E_permanent_protein": 4.4,
        "E_temporary_fat": 5.5,
        "E_temporary_protein": 6.6,
        "phenotype_fat": 7.7,
        "phenotype_protein": 8.8,
        "EBV_fat": 9.9,
        "EBV_protein": 10.0,
        "ranking_index": 11.11,
    }


def test_calculate_average_genetic_values_empty_list() -> None:
    """calculate_average_genetic_values returns None for all keys when list is empty."""
    result = Genetics.calculate_average_genetic_values([])
    assert all(v is None for v in result.values())
    assert set(result.keys()) == {
        "TBV_fat", "TBV_protein",
        "E_permanent_fat", "E_permanent_protein",
        "E_temporary_fat", "E_temporary_protein",
        "phenotype_fat", "phenotype_protein",
        "EBV_fat", "EBV_protein",
        "ranking_index",
    }


def test_calculate_average_genetic_values_nonempty(genetics: Genetics) -> None:
    """calculate_average_genetic_values returns mean of each attribute."""
    g1 = MagicMock(spec=Genetics)
    g1.TBV_fat, g1.TBV_protein = 10.0, 20.0
    g1.E_permanent_fat, g1.E_permanent_protein = 1.0, 2.0
    g1.E_temporary_fat, g1.E_temporary_protein = 3.0, 4.0
    g1.phenotype_fat, g1.phenotype_protein = 5.0, 6.0
    g1.EBV_fat, g1.EBV_protein = 7.0, 8.0
    g1.ranking_index = 9.0

    g2 = MagicMock(spec=Genetics)
    g2.TBV_fat, g2.TBV_protein = 20.0, 40.0
    g2.E_permanent_fat, g2.E_permanent_protein = 3.0, 6.0
    g2.E_temporary_fat, g2.E_temporary_protein = 7.0, 8.0
    g2.phenotype_fat, g2.phenotype_protein = 9.0, 10.0
    g2.EBV_fat, g2.EBV_protein = 11.0, 12.0
    g2.ranking_index = 13.0

    result = Genetics.calculate_average_genetic_values([g1, g2])

    assert result["TBV_fat"] == pytest.approx(15.0)
    assert result["TBV_protein"] == pytest.approx(30.0)
    assert result["E_permanent_fat"] == pytest.approx(2.0)
    assert result["E_permanent_protein"] == pytest.approx(4.0)
    assert result["E_temporary_fat"] == pytest.approx(5.0)
    assert result["E_temporary_protein"] == pytest.approx(6.0)
    assert result["phenotype_fat"] == pytest.approx(7.0)
    assert result["phenotype_protein"] == pytest.approx(8.0)
    assert result["EBV_fat"] == pytest.approx(9.0)
    assert result["EBV_protein"] == pytest.approx(10.0)
    assert result["ranking_index"] == pytest.approx(11.0)


def test_calculate_average_tbv_empty_list() -> None:
    """calculate_average_tbv returns (0.0, 0.0) for empty list."""
    fat, protein = Genetics.calculate_average_tbv([])
    assert fat == 0.0
    assert protein == 0.0


def test_calculate_average_tbv_nonempty() -> None:
    """calculate_average_tbv returns mean TBV_fat and TBV_protein."""
    g1 = MagicMock(spec=Genetics)
    g1.TBV_fat, g1.TBV_protein = 10.0, 20.0
    g2 = MagicMock(spec=Genetics)
    g2.TBV_fat, g2.TBV_protein = 30.0, 60.0

    fat, protein = Genetics.calculate_average_tbv([g1, g2])

    assert fat == pytest.approx(20.0)
    assert protein == pytest.approx(40.0)


def test_calculate_newborn_calf_tbv_values_too_early(genetics: Genetics, mocker: MockerFixture) -> None:
    """Out-of-range early birth date falls back to earliest semen date with warning."""
    AnimalConfig.top_listing_semen["estimated_fat"] = {"2010-01": 50.0, "2020-01": 80.0}
    AnimalConfig.top_listing_semen["estimated_protein"] = {"2010-01": 25.0, "2020-01": 40.0}
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager")
    mock_generate = mocker.patch.object(Utility, "generate_bivariate_random_numbers", return_value=(1.0, 2.0))
    Genetics.set_top_semen_too_early_warning_raised(False)

    genetics._calculate_newborn_calf_tbv_values(10.0, 20.0, "2005-06")

    # Fallback to earliest date "2010-01"
    expected_mean_fat = (50.0 + 10.0) / 2
    expected_mean_protein = (25.0 + 20.0) / 2
    mock_generate.assert_called_once_with(
        expected_mean_fat, expected_mean_protein, pytest.approx(18.243354954612926), pytest.approx(9.475230867899738), TBV_CORRELATION
    )
    mock_om.return_value.add_warning.assert_called_once()


def test_calculate_newborn_calf_tbv_values_too_late(genetics: Genetics, mocker: MockerFixture) -> None:
    """Out-of-range late birth date falls back to latest semen date with warning."""
    AnimalConfig.top_listing_semen["estimated_fat"] = {"2010-01": 50.0, "2020-01": 80.0}
    AnimalConfig.top_listing_semen["estimated_protein"] = {"2010-01": 25.0, "2020-01": 40.0}
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager")
    mock_generate = mocker.patch.object(Utility, "generate_bivariate_random_numbers", return_value=(1.0, 2.0))
    Genetics.set_birthdate_too_recent_warning_raised(False)

    genetics._calculate_newborn_calf_tbv_values(10.0, 20.0, "2025-03")

    # Fallback to latest date "2020-01"
    expected_mean_fat = (80.0 + 10.0) / 2
    expected_mean_protein = (40.0 + 20.0) / 2
    mock_generate.assert_called_once_with(
        expected_mean_fat, expected_mean_protein, pytest.approx(18.243354954612926), pytest.approx(9.475230867899738), TBV_CORRELATION
    )
    mock_om.return_value.add_warning.assert_called_once()


def test_calculate_phenotype_values_too_early(genetics: Genetics, mocker: MockerFixture) -> None:
    """Birth year before phenotype data range falls back to earliest year with warning."""
    AnimalConfig.average_phenotype["fat_kg"] = {2010: 300.0, 2020: 500.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2010: 200.0, 2020: 400.0}
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager")
    genetics.TBV_fat = 0.0
    genetics.TBV_protein = 0.0
    genetics.E_permanent_fat = 0.0
    genetics.E_permanent_protein = 0.0
    genetics.E_temporary_fat = 0.0
    genetics.E_temporary_protein = 0.0
    Genetics.set_phenotype_too_early_warning_raised(False)

    fat, protein = genetics._calculate_phenotype_values(birth_year=2000)

    assert fat == pytest.approx(300.0)
    assert protein == pytest.approx(200.0)
    mock_om.return_value.add_warning.assert_called_once()


def test_calculate_phenotype_values_too_late(genetics: Genetics, mocker: MockerFixture) -> None:
    """Birth year after phenotype data range falls back to latest year with warning."""
    AnimalConfig.average_phenotype["fat_kg"] = {2010: 300.0, 2020: 500.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2010: 200.0, 2020: 400.0}
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager")
    genetics.TBV_fat = 0.0
    genetics.TBV_protein = 0.0
    genetics.E_permanent_fat = 0.0
    genetics.E_permanent_protein = 0.0
    genetics.E_temporary_fat = 0.0
    genetics.E_temporary_protein = 0.0
    Genetics.set_phenotype_too_recent_warning_raised(False)

    fat, protein = genetics._calculate_phenotype_values(birth_year=2030)

    assert fat == pytest.approx(500.0)
    assert protein == pytest.approx(400.0)
    mock_om.return_value.add_warning.assert_called_once()
