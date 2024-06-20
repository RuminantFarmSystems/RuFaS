import pytest

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.ration.amino_acid import AminoAcidCalculator, AMINO_ACID_COMPOSITION, \
    ESSENTIAL_AMINO_ACIDS, ESSENTIAL_AMINO_ACID_TARGET_EFFICIENCIES


@pytest.mark.parametrize(
    "amino_acid, NPscurf",
    [
        ("arginine", 1.2),
        ("histidine", 1.2),
        ("isoleucine", 1.2),
        ("leucine", 1.2),
        ("lysine", 1.2),
        ("methionine", 1.2),
        ("phenylalanine", 1.2),
        ("threonine", 1.2),
        ("thryptophan", 1.2),
        ("valine", 1.2)
    ]
)
def test_calculate_scurf(amino_acid: str, NPscurf: float) -> None:
    amino_acid_calculator = AminoAcidCalculator()

    expected_result = NPscurf * AMINO_ACID_COMPOSITION[amino_acid]["scurf"] / 100
    actual_result = amino_acid_calculator._calculate_scurf(amino_acid, NPscurf)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "amino_acid, body_weight",
    [
        ("arginine", 256.7),
        ("histidine", 256.7),
        ("isoleucine", 256.7),
        ("leucine", 256.7),
        ("lysine", 256.7),
        ("methionine", 256.7),
        ("phenylalanine", 256.7),
        ("threonine", 256.7),
        ("thryptophan", 256.7),
        ("valine", 256.7)
    ]
)
def test_calculate_endogenous_urinary_excretion(amino_acid: str, body_weight: float) -> None:
    amino_acid_calculator = AminoAcidCalculator()

    expected_result = 0.010 * 6.25 * body_weight * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100
    actual_result = amino_acid_calculator._calculate_endogenous_urinary_excretion(amino_acid, body_weight)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "amino_acid, NPGrowth",
    [
        ("arginine", 1.2),
        ("histidine", 1.2),
        ("isoleucine", 1.2),
        ("leucine", 1.2),
        ("lysine", 1.2),
        ("methionine", 1.2),
        ("phenylalanine", 1.2),
        ("threonine", 1.2),
        ("thryptophan", 1.2),
        ("valine", 1.2)
    ]
)
def test_calculate_growth(amino_acid: str, NPGrowth: float) -> None:
    amino_acid_calculator = AminoAcidCalculator()

    expected_result = NPGrowth * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100
    actual_result = amino_acid_calculator._calculate_growth(amino_acid, NPGrowth)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "amino_acid, NPGest",
    [
        ("arginine", 1.2),
        ("histidine", 1.2),
        ("isoleucine", 1.2),
        ("leucine", 1.2),
        ("lysine", 1.2),
        ("methionine", 1.2),
        ("phenylalanine", 1.2),
        ("threonine", 1.2),
        ("thryptophan", 1.2),
        ("valine", 1.2)
    ]
)
def test_calculate_pregnancy(amino_acid: str, NPGest: float) -> None:
    amino_acid_calculator = AminoAcidCalculator()

    expected_result = NPGest * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100
    actual_result = amino_acid_calculator._calculate_pregnancy(amino_acid, NPGest)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "amino_acid, NPMilk",
    [
        ("arginine", 1.2),
        ("histidine", 1.2),
        ("isoleucine", 1.2),
        ("leucine", 1.2),
        ("lysine", 1.2),
        ("methionine", 1.2),
        ("phenylalanine", 1.2),
        ("threonine", 1.2),
        ("thryptophan", 1.2),
        ("valine", 1.2)
    ]
)
def test_calculate_lactation(amino_acid: str, NPMilk: float) -> None:
    amino_acid_calculator = AminoAcidCalculator()

    expected_result = NPMilk * AMINO_ACID_COMPOSITION[amino_acid]["milk"] / 100
    actual_result = amino_acid_calculator._calculate_lactation(amino_acid, NPMilk)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "lactating, body_weight, frame_weight_gain, gravid_uterine_weight_gain, dry_matter_intake_estimate,"
    "milk_true_protein, milk_production, NDF_conc",
    [
        (True, 256.7, 100, 30.68, 50.79, 15, 8.8, 80),
        (True, 1256.7, 388.6, 48.1, 89.9, 66, 18.18, 98),
        (False, 256.7, 100, 30.68, 50.79, 15, 8.8, 80),
        (False, 1256.7, 388.6, 48.1, 89.9, 66, 18.18, 98),
    ]
)
def test_calculate_lactation_integration(
        lactating: bool,
        body_weight: float,
        frame_weight_gain: float,
        gravid_uterine_weight_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        NDF_conc: float,
) -> None:
    amino_acid_calculator = AminoAcidCalculator()
    expected_result = {}

    target_efficiency_gest: float = 0.33
    target_efficiency_growth: float = 0.40

    for amino_acid in ESSENTIAL_AMINO_ACIDS:
        net_AA_scurf: float = (
                (0.20 * body_weight ** 0.60 * 0.85) * AMINO_ACID_COMPOSITION[amino_acid]["scurf"] / 100
        )
        net_AA_End_Urine: float = (
                0.010 * 6.25 * body_weight * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100
        )
        net_AA_MFP: float = (
                (
                    (11.62 + 0.134 * NDF_conc) * dry_matter_intake_estimate * 0.73
                ) * AMINO_ACID_COMPOSITION[amino_acid]["metabolic_fecal"] / 100
        )
        net_AA_Growth: float = (
                frame_weight_gain * 0.11 * 0.86
        ) * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100
        net_AA_Gest: float = (
                gravid_uterine_weight_gain * 125
        ) * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100

        if lactating:
            net_AA_Milk: float = (
                    (milk_true_protein / 100) * milk_production * GeneralConstants.KG_TO_GRAMS
            ) * AMINO_ACID_COMPOSITION[amino_acid]["milk"] / 100

            expected_result[amino_acid] = (
                    (
                            net_AA_scurf +
                            net_AA_MFP +
                            net_AA_Growth +
                            net_AA_Milk
                    ) / ESSENTIAL_AMINO_ACID_TARGET_EFFICIENCIES[amino_acid]
                ) + (
                        net_AA_Gest / target_efficiency_gest
                ) + net_AA_End_Urine
        else:
            expected_result[amino_acid] = (
                    (net_AA_scurf + net_AA_MFP) / ESSENTIAL_AMINO_ACID_TARGET_EFFICIENCIES[amino_acid]
                ) + (
                    net_AA_Growth / target_efficiency_growth
                ) + (
                    net_AA_Gest / target_efficiency_gest
                ) + net_AA_End_Urine

    actual_result = amino_acid_calculator.calculate_essential_amino_acid_requirements(
        lactating,
        body_weight,
        frame_weight_gain,
        gravid_uterine_weight_gain,
        dry_matter_intake_estimate,
        milk_true_protein,
        milk_production,
        NDF_conc
    )

    assert actual_result == expected_result
