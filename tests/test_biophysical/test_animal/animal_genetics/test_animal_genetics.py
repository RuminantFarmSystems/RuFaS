from unittest.mock import call, MagicMock

import numpy
import pytest
from RUFAS.util import Utility
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import Genetics
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@pytest.fixture
def genetics(mocker: MockerFixture) -> Genetics:
    AnimalConfig.average_phenotype["fat_kg"] = {2020: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2020: 20.0}
    mocker.patch.object(
        AnimalConfig, "national_average_breeding_value", {"fat_kg": {2020: 0.0}, "protein_kg": {2020: 0.0}}
    )
    genetics = Genetics(animal_type=AnimalType.LAC_COW, birth_year=2020)
    return genetics


@pytest.mark.parametrize(
    "animal_type, birth_year, birth_month, parity, initialize_new_born_calf, dam_tbv_fat, dam_tbv_protein",
    [
        (AnimalType.CALF, 2020, None, False, False, None, None),
        (AnimalType.HEIFER_I, 2020, None, None, False, None, None),
        (AnimalType.HEIFER_II, 2020, None, None, False, None, None),
        (AnimalType.HEIFER_III, 2020, None, 0, False, None, None),
        (AnimalType.LAC_COW, 2020, None, 1, False, None, None),
        (AnimalType.DRY_COW, 2020, None, 5, False, None, None),
        (AnimalType.CALF, 2020, 1, 1, True, 10.0, 20.0),
    ],
)
def test_animal_genetics_init(
    animal_type: AnimalType,
    birth_year: int,
    birth_month: int | None,
    parity: int | None,
    initialize_new_born_calf: bool,
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
        mock_calculate_tbv_values.assert_called_once_with(birth_year=birth_year)
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


@pytest.mark.parametrize(
    "tbv_fat_variance, tbv_protein_variance, tbv_correlation",
    [
        (25.8, 13.4, 0.59),
        (10.0, 5.0, 0.25),
    ],
    ids=["cdcb_national_average", "farm_specific"],
)
def test_calculate_tbv_values(
    tbv_fat_variance: float,
    tbv_protein_variance: float,
    tbv_correlation: float,
    genetics: Genetics,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for _calculate_tbv_values(): the TBV distribution is centered on the national average breeding values
    of the birth year and its spread comes from the AnimalConfig inputs.
    """
    mocker.patch.object(AnimalConfig, "tbv_fat_variance", tbv_fat_variance)
    mocker.patch.object(AnimalConfig, "tbv_protein_variance", tbv_protein_variance)
    mocker.patch.object(AnimalConfig, "tbv_correlation", tbv_correlation)
    mock_get_national_average_breeding_values = mocker.patch.object(
        Genetics, "get_national_average_breeding_values", return_value=(-33.1, -21.3)
    )
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )
    genetics._calculate_tbv_values(birth_year=2016)
    mock_get_national_average_breeding_values.assert_called_once_with(2016)
    mock_generate_bivariate_random_numbers.assert_called_once_with(
        -33.1, -21.3, numpy.sqrt(tbv_fat_variance), numpy.sqrt(tbv_protein_variance), tbv_correlation
    )


@pytest.mark.parametrize(
    "dam_tbv_fat, dam_tbv_protein, birth_year_month, top_listing_semen_fat, top_listing_semen_protein,"
    "expected_mean_tbv_fat, expected_mean_tbv_protein, expected_std_tbv_fat, expected_std_tbv_protein",
    [
        (10.0, 20.0, "2020-01", 13.0, 18.0, 11.5, 19.0, 3.591656999213594, 2.588435821108957),
        (15.0, 25.0, "2021-01", 15.0, 25.0, 15.0, 25.0, 3.591656999213594, 2.588435821108957),
        (20.0, 30.0, "2022-01", 128.0, 64.0, 74.0, 47.0, 3.591656999213594, 2.588435821108957),
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
        AnimalConfig.tbv_correlation,
    )


def test_calculate_newborn_calf_tbv_values_uses_farm_specific_tbv_inputs(
    genetics: Genetics, mocker: MockerFixture
) -> None:
    """The newborn calf TBV spread is half of the user-input TBV variances."""
    AnimalConfig.top_listing_semen["estimated_fat"] = {"2020-01": 13.0}
    AnimalConfig.top_listing_semen["estimated_protein"] = {"2020-01": 18.0}
    mocker.patch.object(AnimalConfig, "tbv_fat_variance", 100.0)
    mocker.patch.object(AnimalConfig, "tbv_protein_variance", 25.0)
    mocker.patch.object(AnimalConfig, "tbv_correlation", 0.25)
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )

    genetics._calculate_newborn_calf_tbv_values(10.0, 20.0, "2020-01")

    mock_generate_bivariate_random_numbers.assert_called_once_with(
        11.5,
        19.0,
        pytest.approx(7.0710678118654755),
        pytest.approx(3.5355339059327378),
        0.25,
    )


def test_calculate_newborn_calf_tbv_values_key_error(genetics: Genetics, mocker: MockerFixture) -> None:
    """Missing in-range semen data logs an error and re-raises the KeyError."""
    AnimalConfig.top_listing_semen["estimated_fat"] = {
        "2010-01": 50.0,
        "2020-01": 80.0,
    }
    AnimalConfig.top_listing_semen["estimated_protein"] = {
        "2010-01": 25.0,
        "2020-01": 40.0,
    }

    mock_add_error = mocker.patch.object(genetics.om, "add_error")
    mock_generate = mocker.patch.object(Utility, "generate_bivariate_random_numbers")

    with pytest.raises(KeyError):
        genetics._calculate_newborn_calf_tbv_values(10.0, 20.0, "2015-06")

    mock_add_error.assert_called_once_with(
        "Newborn calf tbv calculation key error.",
        "'2015-06'",
        {
            "class": genetics.__class__.__name__,
            "function": genetics._calculate_newborn_calf_tbv_values.__name__,
        },
    )
    mock_generate.assert_not_called()


@pytest.mark.parametrize(
    "fat_variance, protein_variance, correlation",
    [
        (38.8, 20.1, 0.95),
        (12.0, 6.0, 0.5),
    ],
    ids=["cdcb_national_average", "farm_specific"],
)
def test_calculate_ep_values(
    fat_variance: float, protein_variance: float, correlation: float, genetics: Genetics, mocker: MockerFixture
) -> None:
    """Unit test for _calculate_ep_values(): the E_permanent distribution comes from the AnimalConfig inputs."""
    mocker.patch.object(AnimalConfig, "permanent_environment_fat_variance", fat_variance)
    mocker.patch.object(AnimalConfig, "permanent_environment_protein_variance", protein_variance)
    mocker.patch.object(AnimalConfig, "permanent_environment_correlation", correlation)
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )
    genetics._calculate_ep_values()
    mock_generate_bivariate_random_numbers.assert_called_once_with(
        0.0, 0.0, numpy.sqrt(fat_variance), numpy.sqrt(protein_variance), correlation
    )


@pytest.mark.parametrize(
    "fat_variance, protein_variance, correlation",
    [
        (64.5, 33.4, 0.78),
        (20.0, 10.0, 0.4),
    ],
    ids=["cdcb_national_average", "farm_specific"],
)
def test_calculate_et_values(
    fat_variance: float, protein_variance: float, correlation: float, genetics: Genetics, mocker: MockerFixture
) -> None:
    """Unit test for _calculate_et_values(): the E_temporary distribution comes from the AnimalConfig inputs."""
    mocker.patch.object(AnimalConfig, "temporary_environment_fat_variance", fat_variance)
    mocker.patch.object(AnimalConfig, "temporary_environment_protein_variance", protein_variance)
    mocker.patch.object(AnimalConfig, "temporary_environment_correlation", correlation)
    mock_generate_bivariate_random_numbers = mocker.patch.object(
        Utility, "generate_bivariate_random_numbers", return_value=(10.0, 20.0)
    )
    genetics._calculate_et_values()
    mock_generate_bivariate_random_numbers.assert_called_once_with(
        0.0, 0.0, numpy.sqrt(fat_variance), numpy.sqrt(protein_variance), correlation
    )


@pytest.mark.parametrize(
    "mean_phenotype_fat, mean_phenotype_protein, birth_year, national_average_fat, national_average_protein,"
    "tbv_fat, tbv_protein, e_p_fat, e_p_protein, e_t_fat, e_t_protein,"
    "expected_phenotype_fat, expected_phenotype_protein",
    [
        (10.0, 20.0, 2023, 0.0, 0.0, 100.0, 200.0, 5.0, 10.0, 3.0, 6.0, 118.0, 236.0),
        (15.0, 25.0, 2022, 20.0, 10.0, 120.0, 240.0, 7.0, 14.0, 4.0, 8.0, 126.0, 277.0),
        (15.0, 25.0, 2016, -33.0, -21.0, -30.0, -25.0, 7.0, 14.0, 4.0, 8.0, 29.0, 43.0),
        (15.0, 25.0, 2016, -33.0, -21.0, -33.0, -21.0, 0.0, 0.0, 0.0, 0.0, 15.0, 25.0),
    ],
    ids=["zero_national_average", "positive_national_average", "negative_national_average", "average_animal"],
)
def test_calculate_phenotype_values(
    mean_phenotype_fat: float,
    mean_phenotype_protein: float,
    birth_year: int,
    national_average_fat: float,
    national_average_protein: float,
    tbv_fat: float,
    tbv_protein: float,
    e_p_fat: float,
    e_p_protein: float,
    e_t_fat: float,
    e_t_protein: float,
    expected_phenotype_fat: float,
    expected_phenotype_protein: float,
    genetics: Genetics,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for _calculate_phenotype_values(): the phenotype is the mean phenotype of the birth year plus the
    TBV deviation from the national average of that birth year plus the environmental effects, so an average animal
    has the mean phenotype.
    """
    genetics.TBV_fat = tbv_fat
    genetics.TBV_protein = tbv_protein
    genetics.E_permanent_fat = e_p_fat
    genetics.E_permanent_protein = e_p_protein
    genetics.E_temporary_fat = e_t_fat
    genetics.E_temporary_protein = e_t_protein

    AnimalConfig.average_phenotype["fat_kg"] = {birth_year: mean_phenotype_fat}
    AnimalConfig.average_phenotype["protein_kg"] = {birth_year: mean_phenotype_protein}
    mocker.patch.object(
        AnimalConfig,
        "national_average_breeding_value",
        {"fat_kg": {birth_year: national_average_fat}, "protein_kg": {birth_year: national_average_protein}},
    )

    phenotype_fat, phenotype_protein = genetics._calculate_phenotype_values(birth_year=birth_year)

    assert phenotype_fat == pytest.approx(expected_phenotype_fat)
    assert phenotype_protein == pytest.approx(expected_phenotype_protein)


@pytest.mark.parametrize(
    "animal_type, parity, tbv_fat, tbv_protein,"
    "expected_std_ebv_fat, expected_std_ebv_protein, expected_ebv_fat, expected_ebv_protein",
    [
        (AnimalType.CALF, None, 10.0, 20.0, 2.1994317447922773, 1.585086748414736, 7.875, 15.65),
        (AnimalType.HEIFER_I, None, 10.0, 20.0, 2.1994317447922773, 1.585086748414736, 7.875, 15.65),
        (AnimalType.HEIFER_II, None, 10.0, 20.0, 2.1994317447922773, 1.585086748414736, 7.875, 15.65),
        (AnimalType.HEIFER_III, None, 10.0, 20.0, 2.1994317447922773, 1.585086748414736, 7.875, 15.65),
        (AnimalType.LAC_COW, 1, 15.0, 25.0, 2.0317480158720467, 1.46424041741785, 12.32, 20.54),
        (
            AnimalType.DRY_COW,
            2,
            15.0,
            25.0,
            1.8136978800230208,
            1.3070960178961606,
            13.015,
            21.68,
        ),
        (AnimalType.LAC_COW, 3, 15.0, 25.0, 1.5238110119040351, 1.0981803130633876, 13.71, 22.82),
        (AnimalType.DRY_COW, 4, 15.0, 25.0, 1.5238110119040351, 1.0981803130633876, 13.71, 22.82),
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


def test_calculate_ebv_values_uses_farm_specific_tbv_inputs(genetics: Genetics, mocker: MockerFixture) -> None:
    """The EBV estimation noise is scaled by the user-input TBV variances."""
    genetics.TBV_fat = 10.0
    genetics.TBV_protein = 20.0
    mocker.patch.object(AnimalConfig, "tbv_fat_variance", 100.0)
    mocker.patch.object(AnimalConfig, "tbv_protein_variance", 50.0)
    mock_np_random_normal = mocker.patch.object(numpy.random, "normal", side_effect=[0.0, 0.0])

    genetics._calculate_ebv_values(
        animal_type=AnimalType.CALF, parity=None, group_specific_TBV_fat_mean=1.1, group_specific_TBV_protein_mean=2.2
    )

    assert mock_np_random_normal.call_args_list == [
        call(0.0, pytest.approx(4.330127018922194)),
        call(0.0, pytest.approx(3.0618621784789726)),
    ]


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


def test_calculate_ranking_index_uses_user_defined_weights(genetics: Genetics, mocker: MockerFixture) -> None:
    """When both user-defined selection index weights are positive, they override the default weights."""
    mocker.patch.object(AnimalConfig, "genetic_selection_index_weights", {"fat": 0.4, "protein": 0.2})
    genetics.EBV_fat = 5.0
    genetics.EBV_protein = 10.0

    ranking_index = genetics._calculate_ranking_index()

    # 0.4 * 5.0 + 0.2 * 10.0 = 4.0 (default 0.318/0.13 weights would give 2.89).
    assert ranking_index == pytest.approx(4.0)


@pytest.mark.parametrize(
    "weights, expected",
    [
        ({"fat": 0.0, "protein": 0.0}, 0.0),  # both zero
        ({"fat": 0.5, "protein": 0.0}, 2.5),  # protein zero
        ({"fat": 0.0, "protein": 0.5}, 5.0),  # fat zero
    ],
)
def test_calculate_ranking_index_accepts_zero_user_weights(
    weights: dict[str, float], expected: float, genetics: Genetics, mocker: MockerFixture
) -> None:
    """Zero-valued user weights are valid and are used instead of the default weighting."""
    mocker.patch.object(AnimalConfig, "genetic_selection_index_weights", weights)
    genetics.EBV_fat = 5.0
    genetics.EBV_protein = 10.0

    ranking_index = genetics._calculate_ranking_index()

    assert ranking_index == pytest.approx(expected)


@pytest.mark.parametrize(
    "weights",
    [
        {},  # no weights provided
        {"fat": -0.5, "protein": -0.5},  # both negative
        {"fat": 0.5, "protein": -0.5},  # protein negative
        {"fat": -0.5, "protein": 0.5},  # fat negative
    ],
)
def test_calculate_ranking_index_falls_back_to_default_weights(
    weights: dict[str, float], genetics: Genetics, mocker: MockerFixture
) -> None:
    """Missing, empty, or negative user weights fall back to the default 0.318/0.13 weighting."""
    mocker.patch.object(AnimalConfig, "genetic_selection_index_weights", weights)
    genetics.EBV_fat = 5.0
    genetics.EBV_protein = 10.0

    ranking_index = genetics._calculate_ranking_index()

    # 0.318 * 5.0 + 0.13 * 10.0 = 2.89
    assert ranking_index == pytest.approx(2.89)


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


def test_dict_representation(genetics: Genetics) -> None:
    """Unit test for dict_representation property"""
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

    result = genetics.dict_representation

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
        "TBV_fat",
        "TBV_protein",
        "E_permanent_fat",
        "E_permanent_protein",
        "E_temporary_fat",
        "E_temporary_protein",
        "phenotype_fat",
        "phenotype_protein",
        "EBV_fat",
        "EBV_protein",
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
    mock_add_warning = mocker.patch.object(genetics.om, "add_warning")
    mock_generate = mocker.patch.object(Utility, "generate_bivariate_random_numbers", return_value=(1.0, 2.0))
    Genetics.set_top_semen_too_early_warning_raised(False)

    genetics._calculate_newborn_calf_tbv_values(10.0, 20.0, "2005-06")

    expected_mean_fat = (50.0 + 10.0) / 2
    expected_mean_protein = (25.0 + 20.0) / 2
    mock_generate.assert_called_once_with(
        expected_mean_fat,
        expected_mean_protein,
        pytest.approx(3.591656999213594),
        pytest.approx(2.588435821108957),
        AnimalConfig.tbv_correlation,
    )
    mock_add_warning.assert_called_once()


def test_calculate_newborn_calf_tbv_values_too_late(genetics: Genetics, mocker: MockerFixture) -> None:
    """Out-of-range late birth date falls back to latest semen date with warning."""
    AnimalConfig.top_listing_semen["estimated_fat"] = {"2010-01": 50.0, "2020-01": 80.0}
    AnimalConfig.top_listing_semen["estimated_protein"] = {"2010-01": 25.0, "2020-01": 40.0}
    mock_add_warning = mocker.patch.object(genetics.om, "add_warning")
    mock_generate = mocker.patch.object(Utility, "generate_bivariate_random_numbers", return_value=(1.0, 2.0))
    Genetics.set_birthdate_too_recent_warning_raised(False)

    genetics._calculate_newborn_calf_tbv_values(10.0, 20.0, "2025-03")

    expected_mean_fat = (80.0 + 10.0) / 2
    expected_mean_protein = (40.0 + 20.0) / 2
    mock_generate.assert_called_once_with(
        expected_mean_fat,
        expected_mean_protein,
        pytest.approx(3.591656999213594),
        pytest.approx(2.588435821108957),
        AnimalConfig.tbv_correlation,
    )
    mock_add_warning.assert_called_once()


def test_calculate_phenotype_values_too_early(genetics: Genetics, mocker: MockerFixture) -> None:
    """Birth year before phenotype data range falls back to earliest year with warning."""
    AnimalConfig.average_phenotype["fat_kg"] = {2010: 300.0, 2020: 500.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2010: 200.0, 2020: 400.0}
    mock_add_warning = mocker.patch.object(genetics.om, "add_warning")
    genetics.TBV_fat = 0.0
    genetics.TBV_protein = 0.0
    genetics.E_permanent_fat = 0.0
    genetics.E_permanent_protein = 0.0
    genetics.E_temporary_fat = 0.0
    genetics.E_temporary_protein = 0.0
    Genetics.set_phenotype_too_early_warning_raised(False)
    mocker.patch.object(Genetics, "get_national_average_breeding_values", return_value=(0.0, 0.0))

    fat, protein = genetics._calculate_phenotype_values(birth_year=2000)

    assert fat == pytest.approx(300.0)
    assert protein == pytest.approx(200.0)
    mock_add_warning.assert_called_once()


def test_calculate_phenotype_values_too_late(genetics: Genetics, mocker: MockerFixture) -> None:
    """Birth year after phenotype data range falls back to latest year with warning."""
    AnimalConfig.average_phenotype["fat_kg"] = {2010: 300.0, 2020: 500.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2010: 200.0, 2020: 400.0}
    mock_add_warning = mocker.patch.object(genetics.om, "add_warning")
    genetics.TBV_fat = 0.0
    genetics.TBV_protein = 0.0
    genetics.E_permanent_fat = 0.0
    genetics.E_permanent_protein = 0.0
    genetics.E_temporary_fat = 0.0
    genetics.E_temporary_protein = 0.0
    Genetics.set_phenotype_too_recent_warning_raised(False)
    mocker.patch.object(Genetics, "get_national_average_breeding_values", return_value=(0.0, 0.0))

    fat, protein = genetics._calculate_phenotype_values(birth_year=2030)

    assert fat == pytest.approx(500.0)
    assert protein == pytest.approx(400.0)
    mock_add_warning.assert_called_once()


def test_calculate_phenotype_values_key_error(genetics: Genetics, mocker: MockerFixture) -> None:
    """Missing in-range phenotype data logs an error and re-raises the KeyError."""
    AnimalConfig.average_phenotype["fat_kg"] = {
        2010: 50.0,
        2020: 80.0,
    }
    AnimalConfig.average_phenotype["protein_kg"] = {
        2010: 25.0,
        2020: 40.0,
    }

    mock_add_error = mocker.patch.object(genetics.om, "add_error")

    with pytest.raises(KeyError):
        genetics._calculate_phenotype_values(2015)

    mock_add_error.assert_called_once_with(
        "Phenotype value calculation key error.",
        "2015",
        {
            "class": genetics.__class__.__name__,
            "function": genetics._calculate_phenotype_values.__name__,
        },
    )


def test_get_national_average_breeding_values(mocker: MockerFixture) -> None:
    """A birth year with an entry returns the national average breeding values of that year."""
    mocker.patch.object(
        AnimalConfig,
        "national_average_breeding_value",
        {"fat_kg": {2016: -33.1, 2020: 0.0}, "protein_kg": {2016: -21.3, 2020: 0.0}},
    )
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager").return_value

    assert Genetics.get_national_average_breeding_values(2016) == (-33.1, -21.3)
    assert Genetics.get_national_average_breeding_values(2020) == (0.0, 0.0)
    mock_om.add_warning.assert_not_called()
    mock_om.add_error.assert_not_called()


def test_get_national_average_breeding_values_too_early(mocker: MockerFixture) -> None:
    """A birth year before the available data uses the earliest year and warns only once."""
    mocker.patch.object(
        AnimalConfig,
        "national_average_breeding_value",
        {"fat_kg": {2010: -60.8, 2020: 0.0}, "protein_kg": {2010: -43.1, 2020: 0.0}},
    )
    mocker.patch.object(Genetics, "national_average_too_early_warning", False)
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager").return_value

    first_result = Genetics.get_national_average_breeding_values(2000)
    second_result = Genetics.get_national_average_breeding_values(2005)

    assert first_result == (-60.8, -43.1)
    assert second_result == (-60.8, -43.1)
    mock_om.add_warning.assert_called_once()
    assert Genetics.national_average_too_early_warning is True


def test_get_national_average_breeding_values_too_late(mocker: MockerFixture) -> None:
    """A birth year after the available data uses the latest year and warns only once."""
    mocker.patch.object(
        AnimalConfig,
        "national_average_breeding_value",
        {"fat_kg": {2010: -60.8, 2020: 0.0}, "protein_kg": {2010: -43.1, 2020: 0.0}},
    )
    mocker.patch.object(Genetics, "national_average_too_recent_warning", False)
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager").return_value

    first_result = Genetics.get_national_average_breeding_values(2025)
    second_result = Genetics.get_national_average_breeding_values(2030)

    assert first_result == (0.0, 0.0)
    assert second_result == (0.0, 0.0)
    mock_om.add_warning.assert_called_once()
    assert Genetics.national_average_too_recent_warning is True


def test_get_national_average_breeding_values_key_error(mocker: MockerFixture) -> None:
    """Missing in-range national average data logs an error and re-raises the KeyError."""
    mocker.patch.object(
        AnimalConfig,
        "national_average_breeding_value",
        {"fat_kg": {2010: -60.8, 2020: 0.0}, "protein_kg": {2010: -43.1, 2020: 0.0}},
    )
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal_genetics.animal_genetics.OutputManager").return_value

    with pytest.raises(KeyError):
        Genetics.get_national_average_breeding_values(2015)

    mock_om.add_error.assert_called_once_with(
        "National average breeding value key error.",
        "2015",
        {
            "class": Genetics.__name__,
            "function": Genetics.get_national_average_breeding_values.__name__,
        },
    )
    mock_om.add_warning.assert_not_called()


@pytest.mark.parametrize("birth_year", [2006, 2016, 2021])
def test_animal_without_simulated_dam_is_centered_on_birth_year_averages(
    birth_year: int, mocker: MockerFixture
) -> None:
    """
    An animal entering the herd without a simulated dam has a mean TBV equal to the national average breeding value
    of its birth year, and an average animal has the mean phenotype of its birth year.
    """
    national_average = {
        "fat_kg": {2006: -71.2, 2016: -33.1, 2021: 9.1},
        "protein_kg": {2006: -50.3, 2016: -21.3, 2021: 5.0},
    }
    mean_phenotype = {
        "fat_kg": {2006: 420.0, 2016: 450.0, 2021: 510.0},
        "protein_kg": {2006: 340.0, 2016: 365.0, 2021: 400.0},
    }
    mocker.patch.object(AnimalConfig, "national_average_breeding_value", national_average)
    mocker.patch.object(AnimalConfig, "average_phenotype", mean_phenotype)
    # Every random draw returns the mean of its distribution, so the values below are the distribution means.
    mocker.patch.object(Utility, "generate_bivariate_random_numbers", side_effect=lambda mu_x, mu_y, *_: (mu_x, mu_y))

    genetics = Genetics(birth_year=birth_year, animal_type=AnimalType.LAC_COW)

    assert genetics.TBV_fat == national_average["fat_kg"][birth_year]
    assert genetics.TBV_protein == national_average["protein_kg"][birth_year]
    assert genetics.phenotype_fat == pytest.approx(mean_phenotype["fat_kg"][birth_year])
    assert genetics.phenotype_protein == pytest.approx(mean_phenotype["protein_kg"][birth_year])


def test_first_generation_gain_is_similar_across_recent_start_years(mocker: MockerFixture) -> None:
    """
    The mean TBV gain of the first home-raised generation over its dams barely depends on the simulation start year.

    The values are taken from ``national_average_BV_HO.csv`` (dams born four years before the start year) and
    ``TopListingSemen_HO.csv`` (January of the start year). With a mean dam TBV of 0 for every start year, the fat
    gains for these three start years would spread over 41.7 kg and the protein gains over 26.3 kg.
    """
    mocker.patch.object(
        AnimalConfig,
        "national_average_breeding_value",
        {
            "fat_kg": {
                2011: -58.059892,
                2015: -39.008990,
                2016: -33.112282,
                2020: 0.0,
                2021: 9.071858,
                2024: 33.112282,
            },
            "protein_kg": {
                2011: -40.369769,
                2015: -26.308389,
                2016: -21.318867,
                2020: 0.0,
                2021: 4.989522,
                2024: 18.143716,
            },
        },
    )
    mocker.patch.object(
        AnimalConfig,
        "top_listing_semen",
        {
            "estimated_fat": {"2015-01": 36.21923076, "2020-01": 77.91369429, "2025-01": 119.60815782},
            "estimated_protein": {"2015-01": 9.23811259, "2020-01": 35.53624150, "2025-01": 61.83437041},
        },
    )
    mocker.patch.object(
        AnimalConfig,
        "average_phenotype",
        {
            "fat_kg": {year: 500.0 for year in (2011, 2015, 2016, 2020, 2021, 2025)},
            "protein_kg": {year: 400.0 for year in (2011, 2015, 2016, 2020, 2021, 2025)},
        },
    )
    # Calves born in 2025 use the national average of 2024, the latest year available. Marking the warning for that
    # as already raised keeps it out of the logs.
    mocker.patch.object(Genetics, "national_average_too_recent_warning", True)
    # Every random draw returns the mean of its distribution, so the gains below are the expected gains.
    mocker.patch.object(Utility, "generate_bivariate_random_numbers", side_effect=lambda mu_x, mu_y, *_: (mu_x, mu_y))

    fat_gains: list[float] = []
    protein_gains: list[float] = []
    for start_year in (2015, 2020, 2025):
        dam = Genetics(birth_year=start_year - 4, animal_type=AnimalType.LAC_COW)
        calf = Genetics(
            birth_year=start_year,
            birth_month=1,
            animal_type=AnimalType.CALF,
            initialize_new_born_calf=True,
            dam_tbv_fat=dam.TBV_fat,
            dam_tbv_protein=dam.TBV_protein,
        )
        fat_gains.append(calf.TBV_fat - dam.TBV_fat)
        protein_gains.append(calf.TBV_protein - dam.TBV_protein)

    assert fat_gains == pytest.approx([47.14, 55.51, 55.27], abs=0.01)
    assert protein_gains == pytest.approx([24.80, 28.43, 28.42], abs=0.01)
    assert max(fat_gains) - min(fat_gains) < 10.0
    assert max(protein_gains) - min(protein_gains) < 5.0
