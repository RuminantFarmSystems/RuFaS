import pytest
from pytest import approx

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.ration.amino_acid import AminoAcidCalculator, EssentialAminoAcidRequirements


def test_essential_amino_acid_addition() -> None:
    """Tests the addition of two EssentialAminoAcidRequirements instances."""
    req1 = EssentialAminoAcidRequirements(
        histidine=1.0,
        isoleucine=2.0,
        leucine=3.0,
        lysine=4.0,
        methionine=5.0,
        phenylalanine=6.0,
        threonine=7.0,
        thryptophan=8.0,
        valine=9.0,
    )

    req2 = EssentialAminoAcidRequirements(
        histidine=0.5,
        isoleucine=1.5,
        leucine=2.5,
        lysine=3.5,
        methionine=4.5,
        phenylalanine=5.5,
        threonine=6.5,
        thryptophan=7.5,
        valine=8.5,
    )

    expected = EssentialAminoAcidRequirements(
        histidine=1.5,
        isoleucine=3.5,
        leucine=5.5,
        lysine=7.5,
        methionine=9.5,
        phenylalanine=11.5,
        threonine=13.5,
        thryptophan=15.5,
        valine=17.5,
    )

    result: EssentialAminoAcidRequirements = req1 + req2

    assert isinstance(result, EssentialAminoAcidRequirements)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_essential_amino_acid_truediv() -> None:
    """Tests the division of an EssentialAminoAcidRequirements instance by a scalar."""
    req = EssentialAminoAcidRequirements(
        histidine=2.0,
        isoleucine=4.0,
        leucine=6.0,
        lysine=8.0,
        methionine=10.0,
        phenylalanine=12.0,
        threonine=14.0,
        thryptophan=16.0,
        valine=18.0,
    )

    divisor: float = 2.0

    expected = EssentialAminoAcidRequirements(
        histidine=1.0,
        isoleucine=2.0,
        leucine=3.0,
        lysine=4.0,
        methionine=5.0,
        phenylalanine=6.0,
        threonine=7.0,
        thryptophan=8.0,
        valine=9.0,
    )

    result: EssentialAminoAcidRequirements = req / divisor

    assert isinstance(result, EssentialAminoAcidRequirements)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_essential_amino_acid_truediv_zero() -> None:
    """Tests that division by zero raises a ZeroDivisionError."""
    req = EssentialAminoAcidRequirements(
        histidine=1.0,
        isoleucine=2.0,
        leucine=3.0,
        lysine=4.0,
        methionine=5.0,
        phenylalanine=6.0,
        threonine=7.0,
        thryptophan=8.0,
        valine=9.0,
    )

    with pytest.raises(ZeroDivisionError, match="Cannot divide EssentialAminoAcidRequirements by zero."):
        _ = req / 0.0


@pytest.mark.parametrize(
    "amino_acid, NPscurf, expected",
    [
        ("arginine", 1.2, 0.1152),
        ("histidine", 1.2, 0.021),
        ("isoleucine", 1.2, 0.03552),
        ("leucine", 1.2, 0.08315999999999998),
        ("lysine", 1.2, 0.06768),
        ("methionine", 1.2, 0.0168),
        ("phenylalanine", 1.2, 0.04332),
        ("threonine", 1.2, 0.048119999999999996),
        ("thryptophan", 1.2, 0.00876),
        ("valine", 1.2, 0.05592),
    ],
)
def test_calculate_scurf(amino_acid: str, NPscurf: float, expected: float) -> None:
    """
    Unit test for AminoAcidCalculator._calculate_scurf()
    """
    amino_acid_calculator = AminoAcidCalculator()
    actual_result = amino_acid_calculator._calculate_scurf(amino_acid, NPscurf)

    assert actual_result == approx(expected, abs=0.001)


@pytest.mark.parametrize(
    "amino_acid, body_weight, expected",
    [
        ("arginine", 256.7, 1.3155874999999997),
        ("histidine", 256.7, 0.48772999999999994),
        ("isoleucine", 256.7, 0.592014375),
        ("leucine", 256.7, 1.3268181249999997),
        ("lysine", 256.7, 1.26745625),
        ("methionine", 256.7, 0.38023687500000003),
        ("phenylalanine", 256.7, 0.707529375),
        ("threonine", 256.7, 0.7765175),
        ("thryptophan", 256.7, 0.16845937500000002),
        ("valine", 256.7, 0.826253125),
    ],
)
def test_calculate_endogenous_urinary_excretion(amino_acid: str, body_weight: float, expected: float) -> None:
    """
    Unit test for AminoAcidCalculator._calculate_endogenous_urinary_excretion()
    """
    amino_acid_calculator = AminoAcidCalculator()
    actual_result = amino_acid_calculator._calculate_endogenous_urinary_excretion(amino_acid, body_weight)
    assert actual_result == approx(expected, abs=0.001)


@pytest.mark.parametrize(
    "amino_acid, NPGrowth, expected",
    [
        ("arginine", 1.2, 0.09839999999999999),
        ("histidine", 1.2, 0.03648),
        ("isoleucine", 1.2, 0.04428),
        ("leucine", 1.2, 0.09924),
        ("lysine", 1.2, 0.09480000000000001),
        ("methionine", 1.2, 0.02844),
        ("phenylalanine", 1.2, 0.052919999999999995),
        ("threonine", 1.2, 0.05808),
        ("thryptophan", 1.2, 0.0126),
        ("valine", 1.2, 0.06180000000000001),
    ],
)
def test_calculate_growth(amino_acid: str, NPGrowth: float, expected: float) -> None:
    """
    Unit test for AminoAcidCalculator._calculate_growth()
    """
    amino_acid_calculator = AminoAcidCalculator()
    actual_result = amino_acid_calculator._calculate_growth(amino_acid, NPGrowth)
    assert actual_result == approx(expected, abs=0.001)


@pytest.mark.parametrize(
    "amino_acid, NPGest, expected",
    [
        ("arginine", 1.2, 0.09839999999999999),
        ("histidine", 1.2, 0.03648),
        ("isoleucine", 1.2, 0.04428),
        ("leucine", 1.2, 0.09924),
        ("lysine", 1.2, 0.09480000000000001),
        ("methionine", 1.2, 0.02844),
        ("phenylalanine", 1.2, 0.052919999999999995),
        ("threonine", 1.2, 0.05808),
        ("thryptophan", 1.2, 0.0126),
        ("valine", 1.2, 0.06180000000000001),
    ],
)
def test_calculate_pregnancy(amino_acid: str, NPGest: float, expected: float) -> None:
    """
    Unit test for AminoAcidCalculator._calculate_pregnancy()
    """
    amino_acid_calculator = AminoAcidCalculator()
    actual_result = amino_acid_calculator._calculate_pregnancy(amino_acid, NPGest)
    assert actual_result == approx(expected, abs=0.001)


@pytest.mark.parametrize(
    "amino_acid, NPMilk, expected",
    [
        ("arginine", 1.2, 0.04488),
        ("histidine", 1.2, 0.03504),
        ("isoleucine", 1.2, 0.07415999999999999),
        ("leucine", 1.2, 0.12672),
        ("lysine", 1.2, 0.10583999999999999),
        ("methionine", 1.2, 0.036359999999999996),
        ("phenylalanine", 1.2, 0.06312),
        ("threonine", 1.2, 0.055439999999999996),
        ("thryptophan", 1.2, 0.019799999999999998),
        ("valine", 1.2, 0.0828),
    ],
)
def test_calculate_lactation(amino_acid: str, NPMilk: float, expected: float) -> None:
    """
    Unit test for AminoAcidCalculator._calculate_lactation()
    """
    amino_acid_calculator = AminoAcidCalculator()
    actual_result = amino_acid_calculator._calculate_lactation(amino_acid, NPMilk)
    assert actual_result == approx(expected, abs=0.001)


@pytest.mark.parametrize(
    "animal_type, lactating, body_weight, frame_weight_gain, gravid_uterine_weight_gain, dry_matter_intake_estimate,"
    "milk_true_protein, milk_production, NDF_conc, expected",
    [
        (
            AnimalType.DRY_COW,
            True,
            256.7,
            100,
            30.68,
            50.79,
            15,
            8.8,
            80,
            EssentialAminoAcidRequirements(
                histidine=444.75415905775316,
                isoleucine=607.8802372175029,
                leucine=1259.145226809208,
                lysine=1169.9987839467644,
                methionine=350.6195244438681,
                phenylalanine=702.7935242069381,
                threonine=754.7970603482727,
                thryptophan=164.91259507532814,
                valine=801.8208567273932,
            ),
        ),
        (
            AnimalType.LAC_COW,
            True,
            1256.7,
            388.6,
            48.1,
            89.9,
            66,
            18.18,
            98,
            EssentialAminoAcidRequirements(
                histidine=1101.86857774196,
                isoleucine=1845.3482152778374,
                leucine=3458.810162197632,
                lysine=3092.1012637087865,
                methionine=971.62615877822,
                phenylalanine=2005.2365378218012,
                threonine=1942.1550805517568,
                thryptophan=456.70449804253167,
                valine=2218.3784711619164,
            ),
        ),
        (
            AnimalType.DRY_COW,
            False,
            256.7,
            100,
            30.68,
            50.79,
            15,
            8.8,
            80,
            EssentialAminoAcidRequirements(
                histidine=393.6976737244198,
                isoleucine=493.3654940484889,
                leucine=1069.0814352338655,
                lysine=1009.1291617245423,
                methionine=296.0838623205804,
                phenylalanine=587.421179206938,
                threonine=659.9388078482726,
                thryptophan=139.71983867997932,
                valine=679.2993857814473,
            ),
        ),
        (
            AnimalType.LAC_COW,
            False,
            1256.7,
            388.6,
            48.1,
            89.9,
            66,
            18.18,
            98,
            EssentialAminoAcidRequirements(
                histidine=636.0191077366268,
                isoleucine=802.4263120554431,
                leucine=1726.529161286536,
                lysine=1625.4751117532307,
                methionine=474.57840590411047,
                phenylalanine=954.6927251518009,
                threonine=1077.659761336757,
                thryptophan=227.01112110881076,
                valine=1101.746089120024,
            ),
        ),
        (
            AnimalType.CALF,
            True,
            256.7,
            100,
            30.68,
            50.79,
            15,
            8.8,
            80,
            EssentialAminoAcidRequirements(
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
        ),
        (
            AnimalType.HEIFER_I,
            True,
            1256.7,
            388.6,
            48.1,
            89.9,
            66,
            18.18,
            98,
            EssentialAminoAcidRequirements(
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
        ),
        (
            AnimalType.HEIFER_II,
            False,
            256.7,
            100,
            30.68,
            50.79,
            15,
            8.8,
            80,
            EssentialAminoAcidRequirements(
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
        ),
        (
            AnimalType.HEIFER_III,
            False,
            1256.7,
            388.6,
            48.1,
            89.9,
            66,
            18.18,
            98,
            EssentialAminoAcidRequirements(
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
        ),
    ],
)
def test_calculate_lactation_integration(
    animal_type: AnimalType,
    lactating: bool,
    body_weight: float,
    frame_weight_gain: float,
    gravid_uterine_weight_gain: float,
    dry_matter_intake_estimate: float,
    milk_true_protein: float,
    milk_production: float,
    NDF_conc: float,
    expected: EssentialAminoAcidRequirements,
) -> None:
    """
    Unit test for AminoAcidCalculator.calculate_essential_amino_acid_requirements()
    """
    amino_acid_calculator = AminoAcidCalculator()
    actual_result = amino_acid_calculator.calculate_essential_amino_acid_requirements(
        animal_type,
        lactating,
        body_weight,
        frame_weight_gain,
        gravid_uterine_weight_gain,
        dry_matter_intake_estimate,
        milk_true_protein,
        milk_production,
        NDF_conc,
    )

    assert actual_result.lysine == approx(expected.lysine, abs=0.001)
    assert actual_result.methionine == approx(expected.methionine, abs=0.001)
    assert actual_result.phenylalanine == approx(expected.phenylalanine, abs=0.001)
    assert actual_result.threonine == approx(expected.threonine, abs=0.001)
    assert actual_result.thryptophan == approx(expected.thryptophan, abs=0.001)
    assert actual_result.valine == approx(expected.valine, abs=0.001)
    assert actual_result.histidine == approx(expected.histidine, abs=0.001)
    assert actual_result.isoleucine == approx(expected.isoleucine, abs=0.001)
    assert actual_result.leucine == approx(expected.leucine, abs=0.001)

    # for amino_acid in actual_result.keys():
    #     assert actual_result[amino_acid] == approx(expected[amino_acid], abs=0.001)
