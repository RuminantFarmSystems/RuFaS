import pytest

from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator


@pytest.mark.parametrize(
    "NDF_concentration,EE_concentration,starch_concentration,methane_mitigation_additive_amount,expected",
    [(2, 3, 4, 5, -42.8749), (2.3, 10.3, 2.4, 4.6, -13.71519)],
)
def test_methane_mitigation_3NOP(
    NDF_concentration: float,
    EE_concentration: float,
    starch_concentration: float,
    methane_mitigation_additive_amount: float,
    expected: float,
) -> None:
    actual = MethaneMitigationCalculator.mitigate_methane(
        NDF_concentration, EE_concentration, starch_concentration, "3-NOP", methane_mitigation_additive_amount
    )
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "NDF_concentration,EE_concentration,starch_concentration,methane_mitigation_additive_amount,expected",
    [(2, 3, 4, 5, 4.247), (2.3, 10.3, 2.4, 4.6, 4.649)],
)
def test_methane_mitigation_monensin(
    NDF_concentration: float,
    EE_concentration: float,
    starch_concentration: float,
    methane_mitigation_additive_amount: float,
    expected: float,
) -> None:
    actual = MethaneMitigationCalculator.mitigate_methane(
        NDF_concentration, EE_concentration, starch_concentration, "Monensin", methane_mitigation_additive_amount
    )
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "NDF_concentration,EE_concentration,starch_concentration,methane_mitigation_additive_amount,expected",
    [(2, 3, 4, 5, 0), (2.3, 10.3, 2.4, 4.6, 0)],
)
def test_methane_mitigation_no_spec(
    NDF_concentration: float,
    EE_concentration: float,
    starch_concentration: float,
    methane_mitigation_additive_amount: float,
    expected: float,
) -> None:
    actual = MethaneMitigationCalculator.mitigate_methane(
        NDF_concentration, EE_concentration, starch_concentration, "other", methane_mitigation_additive_amount
    )
    assert actual == expected
